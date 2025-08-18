import datetime
import decimal
from django.core.management.base import BaseCommand
from Raahi.db import get_db_connection
from Raahi.elasticsearch_utils import index_ticket


def convert_sql_row_to_dict(sql_row, columns):
    if sql_row is None:
        return None

    ticket_dict = dict(zip(columns, sql_row))

    for key, value in ticket_dict.items():
        if isinstance(value, datetime.date):
            ticket_dict[key] = value.isoformat()
        elif isinstance(value, datetime.timedelta):
            total_seconds = int(value.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            ticket_dict[key] = f'{hours:02}:{minutes:02}:{seconds:02}'
        elif isinstance(value, decimal.Decimal):
            ticket_dict[key] = float(value)

    return ticket_dict


class Command(BaseCommand):
    help = 'Fetches all tickets from the SQL database and indexes them in Elasticsearch.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE('Starting to sync tickets to Elasticsearch...'))

        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()

            query = """
                        SELECT 
                            t.*,
                            dep.city AS departure_city,
                            arr.city AS arrival_city,
                            v.company_name
                        FROM Ticket t
                        JOIN Location dep ON t.departure_location_id = dep.location_id
                        JOIN Location arr ON t.arrival_location_id = arr.location_id
                        LEFT JOIN Vehicle v ON t.vehicle_id = v.vehicle_id;
            """

            cursor.execute(query)

            columns = [desc[0] for desc in cursor.description]
            all_tickets = cursor.fetchall()

            count = 0
            self.stdout.write(f'Found {len(all_tickets)} tickets to index.')

            for ticket_tuple in all_tickets:
                ticket_dict = convert_sql_row_to_dict(ticket_tuple, columns)
                if ticket_dict:
                    index_ticket(ticket_dict)
                    count += 1

            self.stdout.write(self.style.SUCCESS(f'Successfully synced {count} tickets.'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {str(e)}'))

        finally:
            if db and db.is_connected():
                cursor.close()
                db.close()
