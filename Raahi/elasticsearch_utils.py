from elasticsearch import Elasticsearch


def get_es_client():
    return Elasticsearch([{'host': 'localhost', 'port': 9200, 'scheme': 'http'}])

def create_ticket_index():
    es = get_es_client()
    index_name = 'tickets'
    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name)
        print(f"Index '{index_name}' created successfully.")
    else:
        print(f"Index '{index_name}' already exists.")

def index_ticket(ticket_data):
    es = get_es_client()
    es.index(index='tickets', id=ticket_data['ticket_id'], document=ticket_data)