import time
import sys
from django.core.management.base import BaseCommand
from Raahi.db import get_db_connection
from Raahi.elasticsearch_utils import index_ticket, delete_ticket_from_index
from Raahi.management.commands.sync_tickets_to_es import convert_sql_row_to_dict


def process_sync_queue():
    db = get_db_connection()
    if not db:
        print("Could not connect to the database.")
        return

    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT id, ticket_id, action FROM elasticsearch_sync_queue ORDER BY id ASC LIMIT 100")
        tasks = cursor.fetchall()

        for task in tasks:
            task_id = task['id']
            ticket_id = task['ticket_id']
            action = task['action']

            print(f"Processing task {task_id}: action={action}, ticket_id={ticket_id}")

            if action in ('INSERT', 'UPDATE'):
                query = """
                    SELECT 
                            t.*,
                            dep.city AS departure_city,
                            arr.city AS arrival_city,
                            v.company_name,
                            CASE
                                WHEN a.vehicle_id IS NOT NULL THEN 'Airplane'
                                WHEN tr.vehicle_id IS NOT NULL THEN 'Train'
                                WHEN b.vehicle_id IS NOT NULL THEN 'Bus'
                                ELSE 'Unknown'
                            END AS vehicle_type
                        FROM Ticket t
                        JOIN Location dep ON t.departure_location_id = dep.location_id
                        JOIN Location arr ON t.arrival_location_id = arr.location_id
                        LEFT JOIN Vehicle v ON t.vehicle_id = v.vehicle_id
                        LEFT JOIN Airplane a ON t.vehicle_id = a.vehicle_id
                        LEFT JOIN Train tr ON t.vehicle_id = tr.vehicle_id
                        LEFT JOIN Bus b ON t.vehicle_id = b.vehicle_id
                        WHERE t.ticket_id = %s;
                """
                inner_cursor = db.cursor()
                inner_cursor.execute(query, (ticket_id,))
                columns = [desc[0] for desc in inner_cursor.description]
                ticket_tuple = inner_cursor.fetchone()

                if ticket_tuple:
                    ticket_dict = convert_sql_row_to_dict(ticket_tuple, columns)
                    index_ticket(ticket_dict)
                else:
                    print(f"Warning: Ticket {ticket_id} not found in DB for indexing.")

                inner_cursor.close()

            elif action == 'DELETE':
                delete_ticket_from_index(ticket_id)

            cursor.execute("DELETE FROM elasticsearch_sync_queue WHERE id = %s", (task_id,))
            db.commit()

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cursor.close()
        db.close()


class Command(BaseCommand):
    help = 'Starts the worker to sync database changes to Elasticsearch.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting Elasticsearch sync worker...'))
        while True:
            try:
                process_sync_queue()
                time.sleep(10)
            except KeyboardInterrupt:
                self.stdout.write(self.style.WARNING('Worker stopped by user.'))
                sys.exit(0)
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'Worker crashed with error: {e}. Restarting in 10 seconds...'))
                time.sleep(10)