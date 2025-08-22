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
    vehicle_type = request.GET.get('vehicle_type')
    min_cost = request.GET.get('min_cost')
    max_cost = request.GET.get('max_cost')
    company_name = request.GET.get('company_name')
    departure_time = request.GET.get('departure_time')
    arrival_time = request.GET.get('arrival_time')
    travel_class = request.GET.get('travel_class')

    if not all([departure_city, arrival_city, departure_date]):
        return JsonResponse({
            'error': 'departure_city, arrival_city, and departure_date are required parameters.'
        }, status=400)

    try:
        es = get_es_client()

        must_clauses = [
            {"match": {"departure_city": departure_city}},
            {"match": {"arrival_city": arrival_city}},
            {"match": {"departure_date": departure_date}},
        ]

        filter_clauses = []

        if vehicle_type:
            must_clauses.append({"match": {"vehicle_type": vehicle_type}})

        if company_name:
            must_clauses.append({"match": {"company_name": company_name}})

        if travel_class:
            must_clauses.append({"match": {"travel_class": travel_class}})

        if departure_time:
            filter_clauses.append({"range": {"departure_time": {"gte": departure_time}}})

        if arrival_time:
            filter_clauses.append({"range": {"arrival_time": {"lte": arrival_time}}})

        if min_cost or max_cost:
            cost_range = {}
            if min_cost:
                cost_range["gte"] = float(min_cost)
            if max_cost:
                cost_range["lte"] = float(max_cost)
            filter_clauses.append({"range": {"cost": cost_range}})

        search_query = {
            "query": {
                "bool": {
                    "must": must_clauses,
                    "filter": filter_clauses
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
