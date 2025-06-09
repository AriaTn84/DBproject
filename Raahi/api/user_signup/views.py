import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken
from ...db import get_db_connection

@csrf_exempt
def signup_user(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    try:
        data = json.loads(request.body)
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        phone = data.get('phone')
        password = data.get('password')
        city_of_residence = data.get('city_of_residence')

        if not all([first_name, last_name, email, phone, password]):
            return JsonResponse({'error': 'Missing required fields'}, status=400)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format in request body'}, status=400)

    connection = None
    try:
        connection = get_db_connection()
        if connection is None:
            return JsonResponse({'error': 'Database connection failed'}, status=500)

        cursor = connection.cursor()

        cursor.execute("SELECT user_id FROM Users WHERE email = %s", (email,))
        if cursor.fetchone():
            return JsonResponse({'error': 'User with this email already exists'}, status=400)

        cursor.execute("SELECT user_id FROM Users WHERE phone = %s", (phone,))
        if cursor.fetchone():
            return JsonResponse({'error': 'User with this phone number already exists'}, status=400)

        hashed_password = make_password(password)

        user_insert_query = """
            INSERT INTO Users (first_name, last_name, email, phone, pass, city_of_residence)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        user_data = (first_name, last_name, email, phone, hashed_password, city_of_residence)
        cursor.execute(user_insert_query, user_data)

        new_user_id = cursor.lastrowid

        passenger_insert_query = """
            INSERT INTO Passengers (user_id, account_status)
            VALUES (%s, %s)
        """
        passenger_data = (new_user_id, 'Deactive')
        cursor.execute(passenger_insert_query, passenger_data)

        wallet_insert_query = """
                              INSERT INTO Wallet (user_id, balance)
                              VALUES (%s, %s) 
                              """
        wallet_data = (new_user_id, 0.00)
        cursor.execute(wallet_insert_query, wallet_data)

        connection.commit()

        refresh = RefreshToken()
        refresh['user_id'] = new_user_id
        refresh['email'] = email

        return JsonResponse({
            'message': 'User registered successfully',
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=201)

    except Exception as e:
        if connection and connection.is_connected():
            connection.rollback()
        return JsonResponse({'error': str(e)}, status=500)
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()