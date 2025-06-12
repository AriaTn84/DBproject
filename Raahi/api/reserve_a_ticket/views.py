import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken
from datetime import datetime, timedelta
from Raahi.db import get_db_connection
from Raahi.redis_client import get_redis_connection

RESERVATION_EXPIRY_MINUTES = 10


@csrf_exempt
def create_reservation(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'This method is not allowed'}, status=405)

    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({'error': 'Authorization header is missing or invalid'}, status=401)

    token_str = auth_header.split(' ')[1]
    try:
        token = AccessToken(token_str)
        token.verify()
        user_id_from_token = token['user_id']
    except (InvalidToken, TokenError):
        return JsonResponse({'error': 'Token is invalid or expired'}, status=401)
    except Exception as e:
        return JsonResponse({'error': f'An unexpected error occurred during token validation: {str(e)}'}, status=500)

    try:
        data = json.loads(request.body)
        ticket_id = data.get('ticket_id')
        ticket_id = int(ticket_id)

        if not ticket_id or not isinstance(ticket_id, int):
            return JsonResponse({'error': 'Ticket ID is required and must be an integer.'}, status=400)

        number_of_seats_requested = 1

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON payload.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Error processing request data: {str(e)}'}, status=400)

    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        if connection is None:
            return JsonResponse({'error': 'Database connection failed'}, status=500)

        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT cost, remaining_capacity FROM Ticket WHERE ticket_id = %s FOR UPDATE", (ticket_id,))
        ticket_details = cursor.fetchone()

        if not ticket_details:
            return JsonResponse({'error': 'Ticket not found.'}, status=404)

        remaining_capacity_db = ticket_details['remaining_capacity']
        ticket_cost = ticket_details['cost']

        if remaining_capacity_db < number_of_seats_requested:
            return JsonResponse({'error': 'Not enough capacity available for this ticket.'}, status=409)

        new_remaining_capacity = remaining_capacity_db - number_of_seats_requested

        update_capacity_query = "UPDATE Ticket SET remaining_capacity = %s WHERE ticket_id = %s AND remaining_capacity >= %s"
        cursor.execute(update_capacity_query, (new_remaining_capacity, ticket_id, number_of_seats_requested))

        if cursor.rowcount == 0:
            connection.rollback()
            return JsonResponse(
                {'error': 'Failed to update ticket capacity. Capacity might have been taken by another user.'},
                status=409)

        reservation_time = datetime.now()

        passenger_id = user_id_from_token

        insert_reservation_query = """
                                   INSERT INTO Reservation (ticket_id, passenger_id, reservation_status, reservation_date)
                                   VALUES (%s, %s, %s, %s)
                                   """
        cursor.execute(insert_reservation_query,
                       (ticket_id, passenger_id, 'Pending', reservation_time))

        reservation_id = cursor.lastrowid
        if not reservation_id:
            connection.rollback()
            return JsonResponse({'error': 'Failed to create reservation record; no reservation ID was generated.'},
                                status=500)
        insert_payment_query = """
                               INSERT INTO Payment (reservation_id, user_id, payment_status, amount)
                               VALUES (%s, %s, %s, %s)
                               """
        cursor.execute(insert_payment_query,
                       (reservation_id, passenger_id, 'Pending', ticket_cost))

        if cursor.lastrowid is None:
            connection.rollback()
            return JsonResponse({'error': 'Failed to create payment record.'}, status=500)
        connection.commit()

        try:
            redis_conn = get_redis_connection()

            reminder_trigger_key = f"reminder_trigger:{reservation_id}"
            redis_conn.setex(reminder_trigger_key, int((RESERVATION_EXPIRY_MINUTES * 60)/2), str(ticket_id))

            final_expiry_key = f"reservation_expiry:{reservation_id}"
            redis_conn.setex(final_expiry_key, int(RESERVATION_EXPIRY_MINUTES * 60), str(ticket_id))

            print(f"Set final expiration (10m) and reminder trigger (5m) for reservation {reservation_id}")
        except Exception as e:
            print(f"Could not set reservation key in Redis: {e}")

        payment_due_time = reservation_time + timedelta(minutes=RESERVATION_EXPIRY_MINUTES)
        return JsonResponse({
            'message': 'Ticket successfully reserved. Please complete payment within the time limit.',
            'reservation_id': reservation_id,
            'ticket_id': ticket_id,
            'number_of_tickets': number_of_seats_requested,
            'total_cost': float(ticket_cost),
            'status': 'Pending',
            'reservation_time': reservation_time.isoformat(),
            'payment_due_by': payment_due_time.isoformat()
        }, status=201)
    finally:
        if cursor:
            try:
                cursor.close()
            except Exception as cursor_err:
                print(f"Error closing database cursor: {cursor_err}")
        if connection and connection.is_connected():
            try:
                connection.close()
            except Exception as conn_err:
                print(f"Error closing database connection: {conn_err}")
