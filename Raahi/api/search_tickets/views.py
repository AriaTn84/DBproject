from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ...elasticsearch_utils import get_es_client


@csrf_exempt
def search_tickets(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'This method is not allowed'}, status=405)

    departure_city = request.GET.get('departure_city')
    arrival_city = request.GET.get('arrival_city')
    departure_date = request.GET.get('departure_date')

    if not all([departure_city, arrival_city, departure_date]):
        return JsonResponse({
            'error': 'departure_city, arrival_city, and departure_date are required parameters.'
        }, status=400)

    try:
        es = get_es_client()

        search_query = {
            "query": {
                "bool": {
                    "must": [
                        {"match": {"departure_city": departure_city}},
                        {"match": {"arrival_city": arrival_city}},
                        {"match": {"departure_date": departure_date}}
                    ]
                }
            }
        }

        results = es.search(index='tickets', body=search_query, size=100)
        hits = [hit['_source'] for hit in results['hits']['hits']]

        return JsonResponse({
            'message': 'Search results fetched successfully from Elasticsearch.',
            'source': 'Elasticsearch',
            'data': hits
        }, status=200)

    except Exception as e:
        return JsonResponse({
            'error': 'Could not connect to the search service.',
            'details': str(e)
        }, status=503)
