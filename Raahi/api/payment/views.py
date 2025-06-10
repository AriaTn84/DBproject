import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from ...db import get_db_connection
from ...redis_client import get_redis_connection


@csrf_exempt
def pay_for_ticket(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'This method is not allowed'}, status=405)

    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({'error': 'Authorization header is missing or invalid'}, status=401)

    token_str = auth_header.split(' ')[1]
    try:
        token = AccessToken(token_str)
        token.verify()
        user_id = token['user_id']
    except (InvalidToken, TokenError):
        return JsonResponse({'error': 'Token is invalid or expired'}, status=401)

    try:
        data = json.loads(request.body)
        reservation_id = data.get('reservation_id')
        payment_method = data.get('payment_method')
        if not reservation_id or not payment_method:
            return JsonResponse({'error': 'reservation_id and payment_method are required.'}, status=400)
        if payment_method not in ['Wallet', 'Credit Card', 'PayPal', 'Bank Transfer']:
            return JsonResponse({'error': 'Invalid payment method.'}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON in request body.'}, status=400)

    connection = get_db_connection()
    if connection is None:
        return JsonResponse({'error': 'Database connection failed'}, status=500)

    try:
        cursor = connection.cursor(dictionary=True)
        connection.start_transaction()

        cursor.execute(
            """
            SELECT r.reservation_id, r.ticket_id, p.amount
            FROM Reservation r
                     JOIN Payment p ON r.reservation_id = p.reservation_id
            WHERE r.reservation_id = %s
              AND r.passenger_id = %s
              AND r.reservation_status = 'Pending'
              AND p.payment_status = 'Pending'
                FOR
            UPDATE
            """, (reservation_id, user_id)
        )
        payment_info = cursor.fetchone()

        if not payment_info:
            connection.rollback()
            return JsonResponse({'error': 'Pending reservation for this user not found or already processed.'},
                                status=404)

        amount_to_pay = payment_info['amount']

        if payment_method == 'Wallet':
            cursor.execute("SELECT balance FROM Wallet WHERE user_id = %s FOR UPDATE", (user_id,))
            wallet = cursor.fetchone()
            if not wallet or wallet['balance'] < amount_to_pay:
                connection.rollback()
                return JsonResponse({'error': 'Insufficient wallet balance.'}, status=402)
            cursor.execute("UPDATE Wallet SET balance = balance - %s WHERE user_id = %s", (amount_to_pay, user_id))

        cursor.execute(
            "UPDATE Reservation SET reservation_status = 'Confirmed' WHERE reservation_id = %s",
            (reservation_id,)
        )
        cursor.execute(
            "UPDATE Payment SET payment_status = 'Completed', payment_method = %s, payment_date = NOW() WHERE reservation_id = %s",
            (payment_method, reservation_id)
        )

        connection.commit()

        try:
            redis_conn = get_redis_connection()
            redis_conn.delete(f"reservation_expiry:{reservation_id}")
            redis_conn.delete(f"user:{user_id}")
        except Exception as e:
            print(f"Redis cleanup error: {e}")

        return JsonResponse({'message': 'Payment successful. Your ticket is confirmed.'}, status=200)

    except Exception as e:
        if connection.is_connected():
            connection.rollback()
        return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@csrf_exempt
def get_payment_history(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'This method is not allowed'}, status=405)

    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({'error': 'Authorization header is missing or invalid'}, status=401)

    token_str = auth_header.split(' ')[1]
    try:
        token = AccessToken(token_str)
        token.verify()
        user_id = token['user_id']
    except (InvalidToken, TokenError):
        return JsonResponse({'error': 'Token is invalid or expired'}, status=401)

    connection = get_db_connection()
    if connection is None:
        return JsonResponse({'error': 'Database connection failed'}, status=500)

    try:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT 
                p.payment_id,
                p.reservation_id,
                p.payment_status,
                p.amount,
                p.payment_method,
                p.payment_date,
                t.departure_date,
                l1.city AS departure_city,
                l2.city AS arrival_city,
                v.company_name
            FROM Payment p
            JOIN Reservation r ON p.reservation_id = r.reservation_id
            JOIN Ticket t ON r.ticket_id = t.ticket_id
            JOIN Vehicle v ON t.vehicle_id = v.vehicle_id
            JOIN Location l1 ON t.departure_location_id = l1.location_id
            JOIN Location l2 ON t.arrival_location_id = l2.location_id
            WHERE p.user_id = %s
            ORDER BY p.payment_date DESC
        """
        cursor.execute(query, (user_id,))
        payments = cursor.fetchall()

        for payment in payments:
            if payment.get('amount'):
                payment['amount'] = float(payment['amount'])
            if payment.get('payment_date'):
                payment['payment_date'] = payment['payment_date'].isoformat()
            if payment.get('departure_date'):
                payment['departure_date'] = payment['departure_date'].isoformat()

        return JsonResponse({
            'message': 'Payment history fetched successfully',
            'data': payments
        }, status=200)
    except Exception as e:
        return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()