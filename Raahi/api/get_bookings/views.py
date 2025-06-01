import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ...db import get_db_connection
from datetime import date, timedelta
from decimal import Decimal


def serialize_data(data):
    for row in data:
        for key, value in row.items():
            if isinstance(value, (date, Decimal, timedelta)):
                row[key] = str(value)
    return data


@csrf_exempt
def get_user_bookings(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'This method is not allowed'}, status=405)

    status_filter = request.GET.get('status', None)

    connection = get_db_connection()
    if connection is None:
        return JsonResponse({'error': 'Database connection failed'}, status=500)

    try:
        cursor = connection.cursor(dictionary=True)

        query = """
                SELECT R.reservation_id,
                       R.reservation_status,
                       T.cost,
                       T.departure_date,
                       T.departure_time,
                       T.arrival_date,
                       V.company_name,
                       DepL.city AS departure_city,
                       ArrL.city AS arrival_city
                FROM Reservation AS R
                         JOIN
                     Ticket AS T ON R.ticket_id = T.ticket_id
                         JOIN
                     Vehicle AS V ON T.vehicle_id = V.vehicle_id
                         JOIN
                     Location AS DepL ON T.departure_location_id = DepL.location_id
                         JOIN
                     Location AS ArrL ON T.arrival_location_id = ArrL.location_id
                WHERE R.passenger_id = %s
                  AND R.reservation_status != 'Pending' \
                """


        if status_filter == 'future':
            query += " AND R.reservation_status = 'Confirmed' AND T.departure_date >= CURDATE()"
        elif status_filter == 'cancelled':
            query += " AND R.reservation_status IN ('Cancelled By Passenger', 'Cancelled By Admin')"
        elif status_filter == 'past':
            query += " AND R.reservation_status = 'Confirmed' AND T.departure_date < CURDATE()"

        query += " ORDER BY T.departure_date DESC"

        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            if not user_id:
                return JsonResponse({'error': 'USER ID is required'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format in request body'}, status=400)
        params = [user_id]

        cursor.execute(query, params)
        bookings = cursor.fetchall()

        bookings_list = serialize_data(bookings)

        return JsonResponse({'bookings': bookings_list}, status=200)

    except Exception as e:
        return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
