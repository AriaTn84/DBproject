import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ...db import get_db_connection
from ...redis_client import get_redis_connection
from datetime import date, timedelta
from decimal import Decimal


def serialize_data(data):
    for row in data:
        for key, value in row.items():
            if isinstance(value, (date, Decimal, timedelta)):
                row[key] = str(value)
    return data


@csrf_exempt
def search_tickets(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'This method is not allowed'}, status=405)

    departure_city = request.GET.get('departure_city')
    arrival_city = request.GET.get('arrival_city')
    departure_date = request.GET.get('departure_date')
    vehicle_type = request.GET.get('vehicle_type')

    min_cost = request.GET.get('min_cost')
    max_cost = request.GET.get('max_cost')
    company_name = request.GET.get('company_name')
    departure_time = request.GET.get('departure_time')
    travel_class = request.GET.get('travel_class')

    if not all([departure_city, arrival_city, departure_date]):
        return JsonResponse({'error': 'departure_city, arrival_city, and departure_date are required parameters.'},
                            status=400)

    redis_client = get_redis_connection()
    cache_key = (f"search:{departure_city}:{arrival_city}:{departure_date}:{vehicle_type or 'any'}"
                 f":{min_cost or ''}:{max_cost or ''}:{company_name or ''}:{departure_time or ''}:{travel_class or ''}")

    if redis_client:
        try:
            cached_results = redis_client.get(cache_key)
            if cached_results:
                return JsonResponse({
                    'message': 'Search results fetched from cache.',
                    'source': 'Redis Cache',
                    'data': json.loads(cached_results)
                }, status=200)
        except Exception as e:
            print(f"Redis cache read error: {e}")

    connection = get_db_connection()
    if connection is None:
        return JsonResponse({'error': 'Database connection failed'}, status=500)

    try:
        cursor = connection.cursor(dictionary=True)

        params = [departure_city, arrival_city, departure_date]

        query = """
            SELECT
                T.ticket_id,
                T.departure_date,
                T.departure_time,
                T.arrival_date,
                T.cost,
                T.remaining_capacity,
                V.company_name,
                origin.city AS departure_city,
                destination.city AS arrival_city,
                CASE
                    WHEN A.vehicle_id IS NOT NULL THEN 'Airplane'
                    WHEN TR.vehicle_id IS NOT NULL THEN 'Train'
                    WHEN B.vehicle_id IS NOT NULL THEN 'Bus'
                    ELSE 'Unknown'
                END AS vehicle_type,
                A.airplane_class,
                TR.star as train_star
            FROM
                Ticket AS T
            JOIN
                Location AS origin ON T.departure_location_id = origin.location_id
            JOIN
                Location AS destination ON T.arrival_location_id = destination.location_id
            JOIN
                Vehicle AS V ON T.vehicle_id = V.vehicle_id
            LEFT JOIN
                Airplane AS A ON T.vehicle_id = A.vehicle_id
            LEFT JOIN
                Train AS TR ON T.vehicle_id = TR.vehicle_id
            LEFT JOIN
                Bus AS B ON T.vehicle_id = B.vehicle_id
            WHERE
                origin.city = %s
                AND destination.city = %s
                AND T.departure_date = %s
        """

        if vehicle_type == 'Airplane':
            query += " AND A.vehicle_id IS NOT NULL"
        elif vehicle_type == 'Train':
            query += " AND TR.vehicle_id IS NOT NULL"
        elif vehicle_type == 'Bus':
            query += " AND B.vehicle_id IS NOT NULL"

        if min_cost:
            query += " AND T.cost >= %s"
            params.append(min_cost)

        if max_cost:
            query += " AND T.cost <= %s"
            params.append(max_cost)

        if company_name:
            query += " AND V.company_name = %s"
            params.append(company_name)

        if departure_time:
            query += " AND T.departure_time = %s"
            params.append(departure_time)

        if travel_class:
            if vehicle_type == 'Airplane':
                query += " AND A.airplane_class = %s"
                params.append(travel_class)
            elif vehicle_type == 'Train':
                query += " AND TR.star = %s"
                params.append(travel_class)
            elif vehicle_type == 'Bus':
                query += " AND B.vehicle_class = %s"
                params.append(travel_class)

        cursor.execute(query, tuple(params))
        tickets = cursor.fetchall()

        serialized_tickets = serialize_data(tickets)

        if redis_client:
            try:
                redis_client.setex(cache_key, 900, json.dumps(serialized_tickets))
            except Exception as e:
                print(f"Redis cache write error: {e}")

        return JsonResponse({
            'message': 'Search results fetched from database.',
            'source': 'MySQL Database',
            'data': serialized_tickets
        }, status=200)

    except Exception as e:
        return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()