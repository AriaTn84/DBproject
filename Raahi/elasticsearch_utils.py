from elasticsearch import Elasticsearch, NotFoundError

ELASTICSEARCH_HOST = "localhost"
ELASTICSEARCH_PORT = 9200
INDEX_NAME = "tickets"


def get_es_client():
    return Elasticsearch(
        [{'host': ELASTICSEARCH_HOST, 'port': ELASTICSEARCH_PORT, 'scheme': 'http'}]
    )


def create_ticket_index():
    es = get_es_client()
    try:
        if not es.indices.exists(index=INDEX_NAME):
            es.indices.create(index=INDEX_NAME)
            print(f"Index '{INDEX_NAME}' created successfully.")
        else:
            print(f"Index '{INDEX_NAME}' already exists.")
    except Exception as e:
        print(f"An error occurred while creating index: {e}")


def index_ticket(ticket_data):
    if not isinstance(ticket_data, dict) or 'ticket_id' not in ticket_data:
        print("Error: ticket_data must be a dictionary with a 'ticket_id'.")
        return

    es = get_es_client()
    ticket_id = ticket_data['ticket_id']

    try:
        es.index(index=INDEX_NAME, id=ticket_id, document=ticket_data)
        print(f"Successfully indexed ticket with ID: {ticket_id}")
    except Exception as e:
        print(f"Error indexing ticket {ticket_id}: {e}")


def delete_ticket_from_index(ticket_id):
    es = get_es_client()
    try:
        es.delete(index=INDEX_NAME, id=ticket_id)
        print(f"Successfully deleted ticket with ID: {ticket_id} from index.")
    except NotFoundError:
        print(f"Ticket with ID: {ticket_id} not found in index. Nothing to delete.")
    except Exception as e:
        print(f"Error deleting ticket {ticket_id}: {e}")