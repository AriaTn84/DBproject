import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ...db import get_db_connection

@csrf_exempt
def get_all_cities(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'This method is not allowed'}, status=405)

    connection = get_db_connection()
    if connection is None:
        return JsonResponse({'error': 'Database connection failed'}, status=500)

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT DISTINCT city FROM Location ORDER BY city ASC")
        cities_data = cursor.fetchall()

        cities_list = [item['city'] for item in cities_data]

        return JsonResponse({
            'cities': cities_list
        })
    except Exception as e:
        return JsonResponse({'error': f'Database error: {str(e)}'}, status=500)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()