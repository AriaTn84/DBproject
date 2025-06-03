import json
from tokenize import TokenError

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.tokens import AccessToken

from Raahi.db import get_db_connection
from mysql.connector import Error as MySQLError


@csrf_exempt
def report_ticket_issue_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'This method is not allowed. Please use POST.'},
                            status=405)

    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({'error': 'Authorization header is missing or invalid.'}, status=401)

    token_str = auth_header.split(' ')[1]
    try:
        token = AccessToken(token_str)
        token.verify()

        current_user_id = token['user_id']
    except InvalidToken:
        return JsonResponse({'error': 'Token is invalid or expired.'}, status=401)
    except TokenError:
        return JsonResponse({'error': 'Token is malformed.'}, status=401)
    except Exception as e:
        return JsonResponse({'error': f'An unexpected error occurred during token validation: {str(e)}'}, status=500)

    try:
        data = json.loads(request.body.decode('utf-8'))
        reservation_id_str = data.get('reservation_id')
        category = data.get('category')
        report_description = data.get('description')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format in request body.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Error processing request body: {str(e)}'}, status=400)

    if not all([reservation_id_str, category, report_description]):
        return JsonResponse(
            {'error': 'Reservation ID, category, and description are required fields.'},
            status=400
        )

    try:
        reservation_id = int(reservation_id_str)
    except ValueError:
        return JsonResponse(
            {'error': 'Reservation ID must be an integer.'},
            status=400
        )

    if not isinstance(category, str) or not category.strip() or len(category) > 100:
        return JsonResponse(
            {'error': 'Category must be a non-empty string and at most 100 characters.'},
            status=400
        )

    if not isinstance(report_description, str) or len(report_description.strip()) < 10:
        return JsonResponse(
            {'error': 'Description must be a non-empty string and at least 10 characters long.'},
            status=400
        )

    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        if connection is None:
            return JsonResponse({'error': 'Database connection failed.'}, status=500)

        cursor = connection.cursor(dictionary=True)

        query_check_reservation = """
                                  SELECT passenger_id, ticket_id
                                  FROM Reservation
                                  WHERE reservation_id = %s \
                                  """
        cursor.execute(query_check_reservation, (reservation_id,))
        reservation_details = cursor.fetchone()

        if not reservation_details:
            return JsonResponse(
                {'error': f'Reservation with ID {reservation_id} not found.'},
                status=404
            )

        if reservation_details['passenger_id'] != current_user_id:
            return JsonResponse(
                {'error': 'You are not authorized to report an issue for this reservation.'},
                status=403
            )

        ticket_id_from_reservation = reservation_details['ticket_id']

        query_insert_report = """
                              INSERT INTO Reports (ticket_id, passenger_id, admin_id, category, report_description, \
                                                   report_status)
                              VALUES (%s, %s, NULL, %s, %s, %s) \
                              """
        params_insert = (
            ticket_id_from_reservation,
            current_user_id,
            category,
            report_description,
            'Open'
        )
        cursor.execute(query_insert_report, params_insert)
        connection.commit()

        new_report_id = cursor.lastrowid

        return JsonResponse({
            'message': 'Ticket issue reported successfully.',
            'report_id': new_report_id
        }, status=201)

    except MySQLError as db_error:
        if connection and connection.is_connected():
            try:
                connection.rollback()
            except MySQLError as rb_error:
                pass
        return JsonResponse({'error': f'Database error: {str(db_error)}'}, status=500)
    except Exception as e:
        return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()