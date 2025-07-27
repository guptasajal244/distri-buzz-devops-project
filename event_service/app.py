# event_service/app.py
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import psycopg2
import pika
import json
import time

app = Flask(__name__)
CORS(app) # Enable CORS for frontend interaction

# Database connection setup
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    # Retry logic for DB connection to account for DB startup time
    retries = 5
    for i in range(retries):
        try:
            conn = psycopg2.connect(DATABASE_URL)
            return conn
        except psycopg2.OperationalError as e:
            print(f"Event Service: DB connection failed ({e}). Retrying in {2**i} seconds...")
            time.sleep(2**i)
    raise Exception("Event Service: Could not connect to database after multiple retries.")

# RabbitMQ connection setup
def get_rabbitmq_channel():
    retries = 5
    for i in range(retries):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq')) # 'rabbitmq' is the service name
            channel = connection.channel()
            channel.queue_declare(queue='event_notifications', durable=True)
            return connection, channel
        except pika.exceptions.AMQPConnectionError as e:
            print(f"Event Service: RabbitMQ connection failed ({e}). Retrying in {2**i} seconds...")
            time.sleep(2**i)
    raise Exception("Event Service: Could not connect to RabbitMQ after multiple retries.")

# Health check for Event Service
@app.route('/health')
def health_check():
    try:
        conn = get_db_connection()
        conn.close()
        # Also try to connect to RabbitMQ to ensure it's healthy
        conn_mq, channel_mq = get_rabbitmq_channel()
        channel_mq.close()
        conn_mq.close()
        return jsonify({"status": "Event Service is healthy", "db_connected": True, "rabbitmq_connected": True}), 200
    except Exception as e:
        return jsonify({"status": "Event Service is unhealthy", "error": str(e)}), 500

@app.route('/events', methods=['GET'])
def get_events():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, name, description, event_date FROM events ORDER BY event_date DESC;')
    events = cur.fetchall()
    cur.close()
    conn.close()
    events_list = []
    for event in events:
        events_list.append({
            "id": event[0], "name": event[1], "description": event[2], "event_date": event[3].isoformat()
        })
    return jsonify(events_list)

@app.route('/events', methods=['POST'])
def create_event():
    data = request.json
    name = data.get('name')
    description = data.get('description')
    event_date_str = data.get('event_date')

    if not name or not event_date_str:
        return jsonify({"error": "Event name and date are required"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO events (name, description, event_date) VALUES (%s, %s, %s) RETURNING id;',
                    (name, description, event_date_str)) # event_date_str should be parseable by PG
        event_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        # Publish event to RabbitMQ
        event_data_for_queue = {
            "id": event_id,
            "name": name,
            "description": description,
            "event_date": event_date_str
        }
        try:
            conn_mq, channel_mq = get_rabbitmq_channel()
            channel_mq.basic_publish(
                exchange='',
                routing_key='event_notifications',
                body=json.dumps(event_data_for_queue),
                properties=pika.BasicProperties(
                    delivery_mode=2, # make message persistent
                )
            )
            channel_mq.close()
            conn_mq.close()
            print(f"Event Service: Published event {event_id} to queue.")
        except Exception as mq_e:
            print(f"Event Service: Failed to publish event to RabbitMQ: {mq_e}")
            # Log this, but don't necessarily fail the API call if DB save succeeded

        return jsonify({"message": "Event created and notification queued", "id": event_id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
