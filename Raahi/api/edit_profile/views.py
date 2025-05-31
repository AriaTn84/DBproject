import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ...db import get_db_connection
from ...redis_client import get_redis_connection


@csrf_exempt
def update_user_profile(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'This method is not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        if not user_id:
            return JsonResponse({'error': 'user_id is a required field'}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format in request body'}, status=400)

    key_to_column_map = {
        'first_name': 'first_name',
        'last_name': 'last_name',
        'phone': 'phone',
        'date_of_birth': 'dateـofـbirth',
        'city_of_residence': 'city_of_residence'
    }

    update_fields_and_values = {}
    for api_key, value in data.items():
        if api_key in key_to_column_map and value is not None:
            db_column = key_to_column_map[api_key]
            update_fields_and_values[db_column] = value

    if not update_fields_and_values:
        return JsonResponse({'error': 'No valid fields to update were provided'}, status=400)

    connection = None
    try:
        connection = get_db_connection()  #
        if connection is None:
            return JsonResponse({'error': 'Database connection failed'}, status=500)

        cursor = connection.cursor()

        set_clause = ", ".join([f"`{field}` = %s" for field in update_fields_and_values.keys()])
        sql_query = f"UPDATE Users SET {set_clause} WHERE user_id = %s"

        values = list(update_fields_and_values.values())
        values.append(user_id)

        cursor.execute(sql_query, tuple(values))

        if cursor.rowcount == 0:
            return JsonResponse({'error': f'User with user_id {user_id} not found or data is unchanged'}, status=404)

        connection.commit()

    except Exception as e:
        if connection and connection.is_connected():
            connection.rollback()
        return JsonResponse({'error': f'Database error: {str(e)}'}, status=500)
    finally:
        if connection and connection.is_connected():
            if 'cursor' in locals() and cursor:
                cursor.close()
            connection.close()

    redis_client = get_redis_connection()  #
    if redis_client is None:
        return JsonResponse({
            'message': 'Profile updated in DB successfully, but failed to connect to Redis'
        }, status=200)

    try:
        redis_key = f"user:{user_id}"
        redis_update_data = {api_key: value for api_key, value in data.items() if
                             api_key in key_to_column_map and value is not None}
        if redis_update_data:
            redis_client.hset(redis_key, mapping=redis_update_data)
    except Exception as e:
        print(f"Could not update Redis cache for user {user_id}: {e}")

    return JsonResponse({'message': 'User profile updated successfully'}, status=200)