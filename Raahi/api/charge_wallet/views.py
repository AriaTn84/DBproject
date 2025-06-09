import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from ...db import get_db_connection
from ...redis_client import get_redis_connection


@csrf_exempt
def charge_wallet(request):
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
    except Exception as e:
        return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)

    try:
        data = json.loads(request.body)
        amount = data.get('amount')
        if not isinstance(amount, (int, float)) or amount <= 0:
            return JsonResponse({'error': 'Invalid amount provided. Amount must be a positive number.'}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)

    connection = get_db_connection()
    if connection is None:
        return JsonResponse({'error': 'Database connection failed'}, status=500)

    try:
        cursor = connection.cursor(dictionary=True)
        connection.start_transaction()

        cursor.execute("SELECT balance FROM Wallet WHERE user_id = %s FOR UPDATE", (user_id,))
        wallet = cursor.fetchone()

        if not wallet:
            connection.rollback()
            return JsonResponse({'error': 'Wallet not found for this user'}, status=404)

        cursor.execute("UPDATE Wallet SET balance = balance + %s WHERE user_id = %s", (amount, user_id))

        connection.commit()

        cursor.execute("SELECT balance FROM Wallet WHERE user_id = %s", (user_id,))
        updated_wallet = cursor.fetchone()

        redis_client = get_redis_connection()
        if redis_client:
            try:
                redis_client.delete(f"user:{user_id}")
            except Exception as e:
                print(f"Redis cache invalidation error: {e}")

        return JsonResponse({
            'message': 'Wallet charged successfully',
            'data': {'new_balance': updated_wallet['balance']}
        }, status=200)

    except Exception as e:
        if connection.is_connected():
            connection.rollback()
        return JsonResponse({'error': f'Database error: {str(e)}'}, status=500)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()