import os
import sys
import django
import time
import mysql.connector

project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if project_path not in sys.path:
    sys.path.append(project_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DBproject.settings')
django.setup()

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from Raahi.db import get_db_connection
from Raahi.redis_client import get_redis_connection


def expire_reservation(reservation_id):
    db_connection = None
    try:
        db_connection = get_db_connection()
        cursor = db_connection.cursor(dictionary=True)

        db_connection.start_transaction()

        cursor.execute(
            "SELECT ticket_id, reservation_status FROM Reservation WHERE reservation_id = %s FOR UPDATE",
            (reservation_id,)
        )
        reservation = cursor.fetchone()

        if reservation and reservation['reservation_status'] == 'Pending':
            ticket_id = reservation['ticket_id']
            print(f"Processing expiration for reservation {reservation_id}...")

            cursor.execute(
                "UPDATE Reservation SET reservation_status = 'Expired' WHERE reservation_id = %s",
                (reservation_id,)
            )

            cursor.execute(
                "UPDATE Ticket SET remaining_capacity = remaining_capacity + 1 WHERE ticket_id = %s",
                (ticket_id,)
            )

            cursor.execute(
                "UPDATE Payment SET payment_status = 'Failed' WHERE reservation_id = %s",
                (reservation_id,)
            )

            db_connection.commit()
            print(f"Success: Reservation {reservation_id} has expired. Status updated and capacity released.")

        elif reservation:
            db_connection.rollback()
            print(
                f"Info: Reservation {reservation_id} was already processed (current status: {reservation['reservation_status']}). No action taken.")

        else:
            db_connection.rollback()
            print(f"Warning: Reservation with ID {reservation_id} not found in the database.")

    except mysql.connector.Error as err:
        print(f"Error: Database error while processing reservation {reservation_id}: {err}")
        if db_connection:
            db_connection.rollback()
    except Exception as e:
        print(f"Error: An unexpected error occurred: {e}")
        if db_connection:
            db_connection.rollback()
    finally:
        if db_connection and db_connection.is_connected():
            cursor.close()
            db_connection.close()


def handle_reminder_trigger(reservation_id):
    db_connection = None
    try:
        db_connection = get_db_connection()
        cursor = db_connection.cursor(dictionary=True)

        query = "SELECT u.email, u.first_name, r.reservation_status FROM Reservation r JOIN Users u ON r.passenger_id = u.user_id WHERE r.reservation_id = %s"
        cursor.execute(query, (reservation_id,))
        user_info = cursor.fetchone()

        if user_info and user_info['reservation_status'] == 'Pending':
            print(f"Info: Sending payment reminder for reservation {reservation_id}...")
            subject = f'Reminding for reservation number {reservation_id}'
            context = {
                'first_name': user_info['first_name'],
                'reservation_id': reservation_id,
            }
            try:
                html_message = render_to_string('payment_reminder_email.html', context)
                plain_message = strip_tags(html_message)
                send_mail(
                    subject=subject,
                    message=plain_message,
                    from_email='raahi.ticket@gmail.com',
                    recipient_list=[user_info['email']],
                    fail_silently=False,
                    html_message=html_message
                )
                print(f"Success: HTML payment reminder sent to {user_info['email']}.")
            except Exception as e:
                print(f"Error: Failed to send email to {user_info['email']}. Reason: {e}")
        else:
            print(f"Info: Reservation {reservation_id} is no longer pending. Reminder not sent.")
    except Exception as e:
        print(f"Error handling reminder for reservation {reservation_id}: {e}")
    finally:
        if db_connection and db_connection.is_connected():
            cursor.close()
            db_connection.close()


def redis_event_listener():
    redis_conn = get_redis_connection()
    pubsub = redis_conn.pubsub()

    pubsub.subscribe('__keyevent@0__:expired')
    print("Info: Worker is ready and listening for Redis key expiration events...")

    for message in pubsub.listen():
        if message['type'] == 'message':
            key = message['data']
            print(f"Info: Expiration event received: {key}")
            if key.startswith('reservation_expiry:'):
                try:
                    reservation_id = int(key.split(':')[1])
                    expire_reservation(reservation_id)
                except (ValueError, IndexError):
                    print(f"Warning: Invalid key format: {key}")
            elif key.startswith('reminder_trigger:'):
                try:
                    res_id = int(key.split(':')[1])
                    handle_reminder_trigger(res_id)
                except (ValueError, IndexError):
                    print(f"Warning: Invalid reminder key format: {key}")
        else:
            print(f"Info: Received non-message type: {message['type']}")


if __name__ == '__main__':
    print("Info: Starting reservation expiration worker...")
    while True:
        try:
            redis_event_listener()
        except redis.exceptions.ConnectionError:
            print("Error: Redis connection lost. Reconnecting in 5 seconds...")
            time.sleep(5)
        except Exception as e:
            print(f"Error: A critical error occurred in the worker: {e}. Restarting in 10 seconds...")
            time.sleep(10)
