import redis
import time
import sys
import os
import mysql.connector

project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if project_path not in sys.path:
    sys.path.append(project_path)

try:
    from Raahi.db import get_db_connection
    from Raahi.redis_client import get_redis_connection
except ImportError:
    print("Error: Could not find db.py or redis_client.py.")
    print("Please ensure the project structure is correct and the script is run from the correct location.")
    sys.exit(1)


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