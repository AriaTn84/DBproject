# DBproject/Raahi/api/edit_profile/views.py

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ...db import get_db_connection
from ...redis_client import get_redis_connection
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


@csrf_exempt
def update_user_profile(request):
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
    except (InvalidToken, TokenError) as e:
        return JsonResponse({'error': 'Token is invalid or expired'}, status=401)
    except Exception as e:
        return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format in request body'}, status=400)

    allowed_fields = ['first_name', 'last_name', 'phone', 'city_of_residence', 'date_of_birth']
    update_fields = {key: value for key, value in data.items() if key in allowed_fields}

    if not update_fields:
        return JsonResponse({'error': 'No valid fields provided to update'}, status=400)

    set_clause = ", ".join([f"{key} = %s" for key in update_fields.keys()])
    sql_query = f"UPDATE Users SET {set_clause} WHERE user_id = %s"
    sql_values = list(update_fields.values()) + [user_id]

    connection = get_db_connection()
    if connection is None:
        return JsonResponse({'error': 'Database connection failed'}, status=500)

    try:
        cursor = connection.cursor()
        cursor.execute(sql_query, tuple(sql_values))

        if cursor.rowcount == 0:
            connection.rollback()
            return JsonResponse({'error': 'User not found or data is unchanged'}, status=404)

        connection.commit()

        redis_client = get_redis_connection()
        if redis_client:
            try:
                redis_client.delete(f"user:{user_id}")
            except Exception as e:
                print(f"Could not delete user cache from Redis: {e}")

        return JsonResponse({'message': 'User profile updated successfully'})
    except Exception as e:
        if connection.is_connected():
            connection.rollback()
        if 'Duplicate entry' in str(e):
            return JsonResponse({'error': 'The provided phone number is already in use.'}, status=409)
        return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
