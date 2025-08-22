import json
from tokenize import TokenError

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.tokens import AccessToken

from ...db import get_db_connection
from ...redis_client import get_redis_connection


@csrf_exempt
def get_user_profile(request):
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
    except (InvalidToken, TokenError) as e:
        return JsonResponse({'error': 'Token is invalid or expired'}, status=401)
    except Exception as e:
        return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)

    redis_client = get_redis_connection()
    if redis_client:
        try:
            cached_user = redis_client.hgetall(f"user:{user_id}")
            if cached_user:
                return JsonResponse({
                    'message': 'User profile fetched from cache successfully',
                    'data': cached_user,
                    'source': 'Redis Cache'
                })
        except Exception as e:
            print(f"Redis error: {e}")

    connection = get_db_connection()
    if connection is None:
        return JsonResponse({'error': 'Database connection failed'}, status=500)

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT u.user_id, u.first_name, u.last_name, u.email, u.phone, u.date_of_birth, u.city_of_residence, w.balance  "
            "FROM Users u JOIN Wallet w ON u.user_id = w.user_id WHERE u.user_id = %s",
            (user_id,))
        user = cursor.fetchone()

        if not user:
            return JsonResponse({'error': 'User not found'}, status=404)

        if redis_client:
            try:
                if user.get('date_of_birth'):
                    user['date_of_birth'] = str(user['date_of_birth'])
                if user.get('balance'):
                    user['balance'] = str(user['balance'])
                redis_client.hset(f"user:{user_id}:balance{user.balance}", mapping=user)
            except Exception as e:
                print(f"Could not write to Redis cache: {e}")

        return JsonResponse({
            'message': 'User profile fetched from database successfully',
            'data': user,
            'source': 'MySQL Database'
        })
    except Exception as e:
        return JsonResponse({'error': f'Database error: {str(e)}'}, status=500)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
