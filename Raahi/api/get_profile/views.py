import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ...db import get_db_connection
from ...redis_client import get_redis_connection


@csrf_exempt
def get_user_profile(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'This method is not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        if not user_id:
            return JsonResponse({'error': 'user_id is a required field'}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format in request body'}, status=400)

    redis_client = get_redis_connection()
    if redis_client:
        try:
            # 1. First, check the cache
            cached_user = redis_client.hgetall(f"user:{user_id}")
            if cached_user:
                # Cache Hit: Data found in Redis
                return JsonResponse({
                    'message': 'User profile fetched from cache successfully',
                    'data': cached_user,
                    'source': 'Redis Cache'
                })
        except Exception as e:
            print(f"Redis error: {e}")
            # Continue to fetch from DB if Redis fails

    # 2. Cache Miss or Redis connection failed: Fetch from database
    connection = get_db_connection()
    if connection is None:
        return JsonResponse({'error': 'Database connection failed'}, status=500)

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT user_id, first_name, last_name, email, phone, date_of_birth, city_of_residence FROM Users WHERE user_id = %s",
            (user_id,))
        user = cursor.fetchone()

        if not user:
            return JsonResponse({'error': 'User not found'}, status=404)

        # 3. Populate the cache for next time
        if redis_client:
            try:
                # Convert date object to string if it exists
                if user.get('date_of_birth'):
                    user['date_of_birth'] = str(user['date_of_birth'])

                redis_client.hset(f"user:{user_id}", mapping=user)
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