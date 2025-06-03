import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ...db import get_db_connection
from datetime import datetime, time, timedelta
from decimal import Decimal
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


@csrf_exempt
def cancel_reservation(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'This method is not allowed'}, status=405)

    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({'error': 'Authorization header is missing or invalid'}, status=401)

    try:
        token_str = auth_header.split(' ')[1]
        token = AccessToken(token_str)
        token.verify()
        user_id = token['user_id']
    except (InvalidToken, TokenError):
        return JsonResponse({'error': 'Token is invalid or expired'}, status=401)
    except Exception as e:
        return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)

    try:
        data = json.loads(request.body)
        reservation_id = data.get('reservation_id')
        if not reservation_id:
            return JsonResponse({'error': 'reservation_id is required'}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format in request body'}, status=400)

    connection = get_db_connection()
    if connection is None:
        return JsonResponse({'error': 'Database connection failed'}, status=500)

    try:
        cursor = connection.cursor(dictionary=True)
        connection.start_transaction()

        cursor.execute("""
            SELECT R.*, T.departure_date, T.departure_time, T.cost
            FROM Reservation R
            JOIN Ticket T ON R.ticket_id = T.ticket_id
            WHERE R.reservation_id = %s
        """, (reservation_id,))
        reservation = cursor.fetchone()

        if not reservation:
            connection.rollback()
            return JsonResponse({'error': 'Reservation not found'}, status=404)

        if reservation['passenger_id'] != user_id:
            connection.rollback()
            return JsonResponse({'error': 'You are not authorized to cancel this reservation'}, status=403)

        if reservation['reservation_status'] in ['Cancelled By Passenger', 'Cancelled By Admin']:
            connection.rollback()
            return JsonResponse({'error': 'This reservation has already been cancelled'}, status=400)

        departure_datetime = datetime.combine(reservation['departure_date'], datetime.min.time()) + reservation['departure_time']

        if departure_datetime < datetime.now():
            connection.rollback()
            return JsonResponse({'error': 'Cannot cancel a reservation for a past trip'}, status=400)

        time_remaining = departure_datetime - datetime.now()
        ticket_cost = reservation['cost']
        refund_percentage = 0.0

        if time_remaining < timedelta(hours=12):
            refund_percentage = 0.50
        elif time_remaining <= timedelta(days=1):
            refund_percentage = 0.70
        elif time_remaining <= timedelta(days=7):
            refund_percentage = 0.80
        else:
            refund_percentage = 0.90

        refund_amount = ticket_cost * Decimal(str(refund_percentage))

        cursor.execute(
            "UPDATE Reservation SET reservation_status = 'Cancelled By Passenger' WHERE reservation_id = %s",
            (reservation_id,)
        )

        cursor.execute(
            "UPDATE Ticket SET remaining_capacity = remaining_capacity + 1 WHERE ticket_id = %s",
            (reservation['ticket_id'],)
        )

        cursor.execute("SELECT wallet_id FROM Wallet WHERE user_id = %s", (user_id,))
        wallet = cursor.fetchone()
        if not wallet:
            cursor.execute("INSERT INTO Wallet (user_id, balance) VALUES (%s, %s)", (user_id, refund_amount))
        else:
            cursor.execute("UPDATE Wallet SET balance = balance + %s WHERE user_id = %s", (refund_amount, user_id))

        connection.commit()

        return JsonResponse({
            'message': 'Reservation cancelled successfully.',
            'refund_processed': True,
            'amount_refunded_to_wallet': f"{refund_amount:.2f}"
        }, status=200)

    except Exception as e:
        if connection.is_connected():
            connection.rollback()
        return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()