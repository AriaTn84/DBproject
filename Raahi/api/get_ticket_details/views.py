import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ...db import get_db_connection


@csrf_exempt
def get_ticket_details(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'This method is not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        ticket_id = data.get('ticket_id')
        if not ticket_id:
            return JsonResponse({'error': 'Ticket ID is required'}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format in request body'}, status=400)



    connection = get_db_connection()
    if connection is None:
        return JsonResponse({'error': 'Database connection failed'}, status=500)

    try:
        cursor = connection.cursor(dictionary=True)

        query_ticket_main = """
                            SELECT t.ticket_id, 
                                   t.arrival_date, 
                                   t.departure_time, 
                                   t.departure_date, 
                                   t.remaining_capacity, 
                                   t.cost, 
                                   t.vehicle_id, 
                                   v.company_name, 
                                   dep_loc.country AS departure_country, 
                                   dep_loc.state   AS departure_state, 
                                   dep_loc.city    AS departure_city, 
                                   arr_loc.country AS arrival_country, 
                                   arr_loc.state   AS arrival_state, 
                                   arr_loc.city    AS arrival_city
                            FROM Ticket t
                                     JOIN Location dep_loc ON t.departure_location_id = dep_loc.location_id
                                     JOIN Location arr_loc ON t.arrival_location_id = arr_loc.location_id
                                     LEFT JOIN Vehicle v ON t.vehicle_id = v.vehicle_id
                            WHERE t.ticket_id = %s 
                            """
        cursor.execute(query_ticket_main, (ticket_id,))
        ticket_details = cursor.fetchone()

        if not ticket_details:
            return JsonResponse({'error': 'Ticket not found'}, status=404)

        vehicle_specific_details = {}
        if ticket_details['vehicle_id']:
            vehicle_id = ticket_details['vehicle_id']
            cursor.execute("SELECT * FROM Train WHERE vehicle_id = %s", (vehicle_id,))
            train_info = cursor.fetchone()
            if train_info:
                vehicle_specific_details['type'] = 'Train'
                if 'vehicle_id' in train_info:
                    del train_info['vehicle_id']
                vehicle_specific_details['amenities'] = train_info
            else:
                cursor.execute("SELECT * FROM Airplane WHERE vehicle_id = %s", (vehicle_id,))
                airplane_info = cursor.fetchone()
                if airplane_info:
                    vehicle_specific_details['type'] = 'Airplane'
                    if 'vehicle_id' in airplane_info:
                        del airplane_info['vehicle_id']
                    vehicle_specific_details['amenities'] = airplane_info
                else:
                    cursor.execute("SELECT * FROM Bus WHERE vehicle_id = %s", (vehicle_id,))
                    bus_info = cursor.fetchone()
                    if bus_info:
                        vehicle_specific_details['type'] = 'Bus'
                        if 'vehicle_id' in bus_info:
                            del bus_info['vehicle_id']
                        vehicle_specific_details['amenities'] = bus_info
        response_data = {
            "ticket_id": ticket_details["ticket_id"],
            "origin": {
                "country": ticket_details["departure_country"],
                "state": ticket_details["departure_state"],
                "city": ticket_details["departure_city"]
            },
            "destination": {
                "country": ticket_details["arrival_country"],
                "state": ticket_details["arrival_state"],
                "city": ticket_details["arrival_city"]
            },
            "departure_date": str(ticket_details["departure_date"]) if ticket_details["departure_date"] else None,
            "departure_time": str(ticket_details["departure_time"]) if ticket_details["departure_time"] else None,
            "arrival_date": str(ticket_details["arrival_date"]) if ticket_details["arrival_date"] else None,
            "price": float(ticket_details["cost"]) if ticket_details["cost"] is not None else None,
            "remaining_capacity": ticket_details["remaining_capacity"],
            "company_name": ticket_details["company_name"],
            "vehicle_type": vehicle_specific_details if vehicle_specific_details else None
        }

        return JsonResponse({'message': 'Ticket details fetched successfully', 'data': response_data}, status=200)

    except Exception as e:
        return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()