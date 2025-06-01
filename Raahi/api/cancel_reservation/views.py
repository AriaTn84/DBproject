import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ...db import get_db_connection
from datetime import datetime, time
# need for test:
# from dateutil.relativedelta import relativedelta


@csrf_exempt
def cancel_reservation(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'This method is not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        reservation_id = data.get('reservation_id')
        user_id = data.get('user_id')

        if not reservation_id or not user_id:
            return JsonResponse({'error': 'reservation_id and user_id are required'}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format'}, status=400)

    connection = get_db_connection()
    if connection is None:
        return JsonResponse({'error': 'Database connection failed'}, status=500)

    try:
        cursor = connection.cursor(dictionary=True)

        connection.start_transaction()

        cursor.execute("SELECT * FROM Reservation WHERE reservation_id = %s", (reservation_id,))
        reservation = cursor.fetchone()

        if not reservation:
            connection.rollback()
            return JsonResponse({'error': 'Reservation not found'}, status=404)

        if reservation['passenger_id'] != user_id:
            connection.rollback()
            return JsonResponse({'error': 'You are not authorized to cancel this reservation'}, status=403)

        if reservation['reservation_status'] in ['Cancelled By Passenger', 'Cancelled By Admin']:
            connection.rollback()
            return JsonResponse({'error': 'This reservation has already been cancelled'}, status=400)

        ticket_id = reservation['ticket_id']
        cursor.execute("SELECT departure_date, departure_time FROM Ticket WHERE ticket_id = %s", (ticket_id,))
        ticket = cursor.fetchone()
        start_of_day = datetime.combine(ticket['departure_date'], time.min)
        departure_datetime = start_of_day + ticket['departure_time']

        if departure_datetime < datetime.now():
            connection.rollback()
            return JsonResponse({'error': 'Cannot cancel a reservation for a past trip'}, status=400)

        cursor.execute(
            "UPDATE Reservation SET reservation_status = 'Cancelled By Passenger' WHERE reservation_id = %s",
            (reservation_id,)
        )

        cursor.execute(
            "UPDATE Ticket SET remaining_capacity = remaining_capacity + 1 WHERE ticket_id = %s",
            (ticket_id,)
        )

        connection.commit()

        return JsonResponse({'message': 'Reservation cancelled successfully and refund is being processed.'},
                            status=200)

    except Exception as e:
        if connection.is_connected():
            connection.rollback()
        return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
