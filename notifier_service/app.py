# notifier_service/app.py
from flask import Flask, jsonify
import pika
import json
import threading
import time

app = Flask(__name__)

# RabbitMQ connection setup
def connect_to_rabbitmq():
    retries = 5
    for i in range(retries):
        try:
            params = pika.ConnectionParameters(host='rabbitmq', port=5672) # 'rabbitmq' is service name
            connection = pika.BlockingConnection(params)
            channel = connection.channel()
            channel.queue_declare(queue='event_notifications', durable=True)
            return connection, channel
        except pika.exceptions.AMQPConnectionError as e:
            print(f"Notifier Service: RabbitMQ connection failed ({e}). Retrying in {2**i} seconds...")
            time.sleep(2**i)
    raise Exception("Notifier Service: Could not connect to RabbitMQ after multiple retries.")

# Consumer logic
def consume_messages():
    print("Notifier Service: Starting message consumer...")
    while True:
        try:
            connection, channel = connect_to_rabbitmq()
            def callback(ch, method, properties, body):
                try:
                    event_data = json.loads(body.decode())
                    print(f"Notifier Service: [✅] Received event for notification: {event_data.get('name')} (ID: {event_data.get('id')})")
                    # --- Simulate sending notifications to users subscribed to this event ---
                    print(f"--- [🔔] Sending dummy notification for event '{event_data.get('name')}' to subscribed users ---")
                    # In a real app, you'd query users, send emails/SMS/push notifications here.
                    # For now, it's a print statement to show the logic.
                    time.sleep(1) # Simulate work
                    ch.basic_ack(delivery_tag=method.delivery_tag) # Acknowledge message after processing
                except Exception as process_e:
                    print(f"Notifier Service: [❌] Error processing message: {process_e} - Message: {body.decode()}")
                    ch.basic_nack(delivery_tag=method.delivery_tag) # Nack message if processing fails

            channel.basic_consume(queue='event_notifications', on_message_callback=callback)
            print("Notifier Service: Waiting for messages. To exit press CTRL+C")
            channel.start_consuming()

        except pika.exceptions.AMQPConnectionError as e:
            print(f"Notifier Service: RabbitMQ connection lost. Reconnecting... Error: {e}")
            time.sleep(5) # Wait before retrying connection
        except KeyboardInterrupt:
            print("Notifier Service: Stopping consumer.")
            break # Exit loop on Ctrl+C
        except Exception as e:
            print(f"Notifier Service: An unexpected error occurred in consumer: {e}. Restarting consumer...")
            time.sleep(5)

# Start the consumer in a separate thread to not block the Flask app
consumer_thread = threading.Thread(target=consume_messages)
consumer_thread.daemon = True # Allows main program to exit even if this thread is running
consumer_thread.start()

@app.route('/health') # Simple health check endpoint for the Notifier service
def health_check():
    try:
        # Try to connect to RabbitMQ to ensure it's healthy
        conn_mq, channel_mq = connect_to_rabbitmq()
        channel_mq.close()
        conn_mq.close()
        return jsonify({"status": "Notifier Service is healthy", "rabbitmq_connected": True}), 200
    except Exception as e:
        return jsonify({"status": "Notifier Service is unhealthy", "error": str(e)}), 500

if __name__ == '__main__':
    # The Flask app on 5003 will just serve the health check
    app.run(host='0.0.0.0', port=5003)
