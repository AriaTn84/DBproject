import json
from tokenize import TokenError

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.tokens import AccessToken

from Raahi.db import get_db_connection
from mysql.connector import Error as MySQLError


def _verify_admin_and_get_id(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None, JsonResponse({'error': 'Authorization header is missing or invalid.'}, status=401)

    token_str = auth_header.split(' ')[1]
    try:
        token = AccessToken(token_str)
        token.verify()
        user_id_from_token = token['user_id']
    except (InvalidToken, TokenError):
        return None, JsonResponse({'error': 'Token is invalid, expired, or malformed.'}, status=401)
    except Exception as e:
        return None, JsonResponse({'error': 'An unexpected error occurred during token validation.'}, status=500)

    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        if connection is None:
            return None, JsonResponse({'error': 'Admin check: Database connection failed.'}, status=500)

        cursor = connection.cursor(dictionary=True)
        query_check_admin = "SELECT user_id FROM Admins WHERE user_id = %s"
        cursor.execute(query_check_admin, (user_id_from_token,))
        admin_record = cursor.fetchone()

        if not admin_record:
            return None, JsonResponse({'error': 'Access Forbidden: User is not an administrator.'}, status=403)

        return user_id_from_token, None

    except MySQLError as e:
        return None, JsonResponse({'error': 'Admin check: Database error.'}, status=500)
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

@csrf_exempt
def list_cancelled_reservations_view(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'This method is not allowed. Please use GET.'}, status=405)

    admin_user_id, error_response = _verify_admin_and_get_id(request)
    if error_response:
        return error_response

    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        if connection is None:
            return JsonResponse({'error': 'Database connection failed.'}, status=500)
        cursor = connection.cursor(dictionary=True)

        query_cancelled = """
                          SELECT reservation_id, passenger_id, ticket_id, reservation_date, reservation_status
                          FROM Reservation
                          WHERE reservation_status = 'Cancelled By Passenger' \
                             OR reservation_status = 'Cancelled By Admin'
                          ORDER BY reservation_date DESC \
                          """
        cursor.execute(query_cancelled)
        cancelled_reservations = cursor.fetchall()

        return JsonResponse({
            'message': 'Cancelled reservations fetched successfully.',
            'admin_id': admin_user_id,
            'data': cancelled_reservations
        }, status=200)

    except MySQLError as db_error:
        return JsonResponse({'error': 'Database error while fetching cancelled reservations.'}, status=500)
    except Exception as e:
        return JsonResponse({'error': 'An unexpected error occurred.'}, status=500)
    finally:
        if cursor: cursor.close()
        if connection and connection.is_connected(): connection.close()


@csrf_exempt
def list_user_reports_view(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'This method is not allowed. Please use GET.'}, status=405)

    admin_user_id, error_response = _verify_admin_and_get_id(request)
    if error_response:
        return error_response

    report_status_filter = request.GET.get('status')

    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        if connection is None:
            return JsonResponse({'error': 'Database connection failed.'}, status=500)
        cursor = connection.cursor(dictionary=True)

        query_reports = "SELECT report_id, ticket_id, passenger_id, admin_id, category, report_description, report_status, admin_response FROM Reports"
        params_reports = []

        if report_status_filter:
            if report_status_filter in ['Open', 'Closed', 'Pending']:
                query_reports += " WHERE report_status = %s"
                params_reports.append(report_status_filter)
            else:
                return JsonResponse({'error': 'Invalid status filter. Allowed: Open, Closed, Pending.'}, status=400)

        query_reports += " ORDER BY report_id DESC"

        cursor.execute(query_reports, tuple(params_reports))
        reports = cursor.fetchall()

        return JsonResponse({
            'message': 'User reports fetched successfully.',
            'admin_id': admin_user_id,
            'data': reports
        }, status=200)

    except MySQLError as db_error:
        return JsonResponse({'error': 'Database error while fetching user reports.'}, status=500)
    except Exception as e:
        return JsonResponse({'error': 'An unexpected error occurred.'}, status=500)
    finally:
        if cursor: cursor.close()
        if connection and connection.is_connected(): connection.close()


@csrf_exempt
def update_user_report_view(request, report_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'This method is not allowed. Please use POST (or PUT).'}, status=405)

    admin_user_id, error_response = _verify_admin_and_get_id(request)
    if error_response:
        return error_response

    try:
        data = json.loads(request.body.decode('utf-8'))
        new_status = data.get('new_status')
        admin_response_text = data.get('admin_response')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format in request body.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'Error processing request body.'}, status=400)

    if new_status is None or admin_response_text is None:
        return JsonResponse({'error': 'new_status and admin_response are required for updating a report.'}, status=400)

    allowed_report_statuses = ['Open', 'Closed', 'Pending']
    if new_status not in allowed_report_statuses:
        return JsonResponse({'error': f'Invalid new_status. Allowed: {", ".join(allowed_report_statuses)}'}, status=400)

    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        if connection is None:
            return JsonResponse({'error': 'Database connection failed.'}, status=500)
        cursor = connection.cursor()

        query_update_report = """
                              UPDATE Reports
                              SET report_status  = %s, \
                                  admin_response = %s, \
                                  admin_id       = %s
                              WHERE report_id = %s \
                              """
        params_update = (new_status, admin_response_text, admin_user_id, report_id)

        cursor.execute(query_update_report, params_update)

        if cursor.rowcount == 0:
            connection.rollback()
            return JsonResponse({'error': f'Report with ID {report_id} not found or no changes made.'}, status=404)

        connection.commit()
        return JsonResponse({
            'message': f'Report ID {report_id} updated successfully by admin {admin_user_id}.',
            'report_id': report_id,
            'updated_status': new_status
        }, status=200)

    except MySQLError as db_error:
        if connection and connection.is_connected(): connection.rollback()
        return JsonResponse({'error': 'Database error while updating report.'}, status=500)
    except Exception as e:
        return JsonResponse({'error': 'An unexpected error occurred.'}, status=500)
    finally:
        if cursor: cursor.close()
        if connection and connection.is_connected(): connection.close()


@csrf_exempt
def confirm_reservation_view(request, reservation_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'This method is not allowed. Please use POST (or PUT).'}, status=405)

    admin_user_id, error_response = _verify_admin_and_get_id(request)
    if error_response:
        return error_response

    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        if connection is None:
            return JsonResponse({'error': 'Database connection failed.'}, status=500)
        cursor = connection.cursor(dictionary=True)

        query_get_reservation = "SELECT reservation_status FROM Reservation WHERE reservation_id = %s"
        cursor.execute(query_get_reservation, (reservation_id,))
        reservation_to_confirm = cursor.fetchone()

        if not reservation_to_confirm:
            return JsonResponse({'error': f'Reservation with ID {reservation_id} not found.'}, status=404)

        current_reservation_status = reservation_to_confirm['reservation_status']

        if current_reservation_status == 'Confirmed':
            return JsonResponse({'message': f'Reservation ID {reservation_id} is already confirmed.'}, status=200)

        confirmable_initial_statuses = ['Pending']
        if current_reservation_status not in confirmable_initial_statuses:
            return JsonResponse({
                                    'error': f'Reservation in status "{current_reservation_status}" cannot be confirmed. Allowed initial statuses: {", ".join(confirmable_initial_statuses)}'},
                                status=400)

        query_payment_status = """
                               SELECT payment_status
                               FROM Payment
                               WHERE reservation_id = %s
                               ORDER BY payment_date DESC
                               LIMIT 1 \
                               """
        cursor.execute(query_payment_status, (reservation_id,))
        payment_info = cursor.fetchone()

        if not payment_info:
            return JsonResponse({'error': 'Payment information not found for this reservation.'}, status=400)  # یا 404

        if payment_info['payment_status'] != 'Completed':
            return JsonResponse({'error': 'You cannot confirm the ticket because the user has not yet paid.'},
                                status=400)

        query_confirm_reservation = "UPDATE Reservation SET reservation_status = 'Confirmed' WHERE reservation_id = %s AND reservation_status = %s"
        cursor.execute(query_confirm_reservation, (reservation_id, current_reservation_status))

        if cursor.rowcount == 0:
            connection.rollback()
            return JsonResponse({
                                    'error': 'Failed to confirm reservation. Status might have changed or reservation not found with the expected status.'},
                                status=409)

        connection.commit()
        return JsonResponse({
            'message': f'Reservation ID {reservation_id} confirmed successfully by admin {admin_user_id}.'
        }, status=200)

    except MySQLError as db_error:
        if connection and connection.is_connected(): connection.rollback()
        return JsonResponse({'error': 'Database error during reservation confirmation.'}, status=500)
    except Exception as e:
        return JsonResponse({'error': 'An unexpected error occurred.'}, status=500)
    finally:
        if cursor: cursor.close()
        if connection and connection.is_connected(): connection.close()

@csrf_exempt
def cancel_reservation_by_admin_view(request, reservation_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'This method is not allowed. Please use POST.'}, status=405)

    admin_user_id, error_response = _verify_admin_and_get_id(request)
    if error_response:
        return error_response

    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        if connection is None:
            return JsonResponse({'error': 'Database connection failed.'}, status=500)
        connection.autocommit = False
        cursor = connection.cursor(dictionary=True)
        query_get_reservation = "SELECT passenger_id, reservation_status FROM Reservation WHERE reservation_id = %s FOR UPDATE"
        cursor.execute(query_get_reservation, (reservation_id,))
        reservation_to_cancel = cursor.fetchone()

        if not reservation_to_cancel:
            return JsonResponse({'error': f'Reservation with ID {reservation_id} not found.'}, status=404)

        passenger_id_of_reservation = reservation_to_cancel['passenger_id']
        current_reservation_status = reservation_to_cancel['reservation_status']

        cancelled_statuses = ['Cancelled By Passenger', 'Cancelled By Admin']
        if current_reservation_status in cancelled_statuses:
            return JsonResponse({'message': f'Reservation ID {reservation_id} is already cancelled.'}, status=200)

        query_payment = """
                        SELECT payment_id, amount, payment_status
                        FROM Payment
                        WHERE reservation_id = %s
                        ORDER BY payment_date DESC
                        LIMIT 1 \
                        FOR \
                        UPDATE \
                        """
        cursor.execute(query_payment, (reservation_id,))
        payment_info = cursor.fetchone()

        refund_amount = 0
        payment_id_to_update = None

        if payment_info and payment_info['payment_status'] == 'Completed':
            refund_amount = payment_info['amount']
            payment_id_to_update = payment_info['payment_id']
        else:
            pass

        new_status = 'Cancelled By Admin'
        query_cancel_reservation = "UPDATE Reservation SET reservation_status = %s WHERE reservation_id = %s"
        cursor.execute(query_cancel_reservation, (new_status, reservation_id))

        if cursor.rowcount == 0:
            connection.rollback()
            return JsonResponse({'error': 'Failed to update reservation status.'}, status=500)
        if payment_id_to_update:
            query_update_payment = "UPDATE Payment SET payment_status = 'Failed' WHERE payment_id = %s"
            cursor.execute(query_update_payment, (payment_id_to_update,))
            if cursor.rowcount == 0:
                connection.rollback()
                return JsonResponse(
                    {'error': f'Failed to update payment status for payment ID {payment_id_to_update}.'}, status=500)
        if refund_amount > 0:
            query_update_wallet = "UPDATE Wallet SET balance = balance + %s WHERE user_id = %s"
            cursor.execute(query_update_wallet, (refund_amount, passenger_id_of_reservation))
            if cursor.rowcount == 0:
                connection.rollback()
                return JsonResponse(
                    {'error': f'Could not find wallet for user ID {passenger_id_of_reservation} to process refund.'},
                    status=404)
        connection.commit()

        return JsonResponse({
            'message': f'Reservation ID {reservation_id} has been successfully cancelled by admin {admin_user_id}.',
            'new_status': new_status,
            'refunded_amount': float(refund_amount)
        }, status=200)

    except MySQLError as db_error:
        if connection:
            connection.rollback()
        return JsonResponse({'error': f'Database error during reservation cancellation: {str(db_error)}'}, status=500)
    except Exception as e:
        if connection:
            connection.rollback()
        return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()





