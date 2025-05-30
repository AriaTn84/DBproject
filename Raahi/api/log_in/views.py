import random
import string
import json
from django.http import JsonResponse
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from ...redis_client import get_redis_connection
from ...db import get_db_connection

def generate_otp(length=6):
    return ''.join(random.choices(string.digits, k=length))

@csrf_exempt
def send_otp(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    try:
        data = json.loads(request.body)
        email = data.get('email')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format in request body'}, status=400)

    if not email:
        return JsonResponse({'error': 'Email is required'}, status=400)

    connection = get_db_connection()
    if connection is None:
        return JsonResponse({'error': 'Database connection failed'}, status=500)

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Users WHERE email = %s", (email,))
        user = cursor.fetchone()
        if not user:
            return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    finally:
        cursor.close()
        connection.close()

    redis_client = get_redis_connection()
    if redis_client is None:
        return JsonResponse({'error': 'Redis connection failed'}, status=500)

    otp = generate_otp()
    try:
        redis_client.setex(f"otp:{email}", 300, otp)
        send_mail(
            subject='Your OTP Code',
            message=f'Your OTP code is {otp}. It is valid for 5 minutes.',
            from_email='mobinfallahi0@gmail.com', #
            recipient_list=[email],
            fail_silently=False,
        )
        return JsonResponse({'message': 'OTP sent successfully'})
    except Exception as e:
        print(f"SMTP Error: {str(e)}")
        return JsonResponse({'error': f'Failed to send OTP: {str(e)}'}, status=500)

@csrf_exempt
def verify_otp(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    try:
        data = json.loads(request.body)
        email = data.get('email')
        otp = data.get('otp')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format in request body'}, status=400)

    if not email or not otp:
        return JsonResponse({'error': 'Email and OTP are required'}, status=400)

    redis_client = get_redis_connection()
    if redis_client is None:
        return JsonResponse({'error': 'Redis connection failed'}, status=500)

    try:
        stored_otp = redis_client.get(f"otp:{email}")
        if stored_otp is None:
            return JsonResponse({'error': 'OTP expired or not found'}, status=400)
        if stored_otp == otp:
            redis_client.delete(f"otp:{email}")
            redis_client.sadd("otp_users", email)
            return JsonResponse({'message': 'OTP verified successfully'})
        else:
            return JsonResponse({'error': 'Invalid OTP'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_otp_users(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid request method'}, status=400)

    redis_client = get_redis_connection()
    if redis_client is None:
        return JsonResponse({'error': 'Redis connection failed'}, status=500)

    try:
        otp_users = redis_client.smembers("otp_users")
        otp_users_list = list(otp_users) if otp_users else []
        return JsonResponse({'otp_users': otp_users_list})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
