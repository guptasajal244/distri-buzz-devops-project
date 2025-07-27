# user_service/app.py
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import psycopg2
import time

app = Flask(__name__)
CORS(app)

DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    retries = 5
    for i in range(retries):
        try:
            conn = psycopg2.connect(
                dbname=os.environ['POSTGRES_DB'],
                user=os.environ['POSTGRES_USER'],
                password=os.environ['POSTGRES_PASSWORD'],
                host=os.environ['POSTGRES_HOST'], # 'db' in docker-compose
                port=5432
            )
            return conn
        except psycopg2.OperationalError as e:
            print(f"User Service: DB connection failed ({e}). Retrying in {2**i} seconds...")
            time.sleep(2**i)
    raise Exception("User Service: Could not connect to database after multiple retries.")

@app.route('/health') # Health check endpoint
def health_check():
    try:
        conn = get_db_connection()
        conn.close()
        return jsonify({"status": "User Service is healthy", "db_connected": True}), 200
    except Exception as e:
        return jsonify({"status": "User Service is unhealthy", "error": str(e)}), 500

@app.route('/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, username FROM users ORDER BY created_at DESC;')
    users = [{"id": r[0], "username": r[1]} for r in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify(users)

@app.route('/users/register', methods=['POST'])
def register_user():
    data = request.json
    username = data.get('username')
    password = data.get('password') # In a real app, hash this!
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO users (username, password_hash) VALUES (%s, %s) RETURNING id;', (username, password))
        user_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "User registered", "id": user_id}), 201
    except psycopg2.IntegrityError:
        return jsonify({"error": "Username already exists"}), 409
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
