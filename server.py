import sqlite3
from flask import Flask, request, send_from_directory, render_template
from datetime import datetime
import pytz

# http://localhost:5000/53949?id=791518137

app = Flask(__name__)

IMAGES_FOLDER = "images"

DB_NAME = "id_data.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tracking_data (
                user_id TEXT,
                track_id TEXT,
                timestamp INTEGER
            )
        ''')
        conn.commit()

init_db()

@app.route('/<user_id>', methods=['GET'])
def track_user(user_id):
    track_id = request.args.get('id')

    if not track_id:
        return "Missing 'id' parameter", 400

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO tracking_data (user_id, track_id, timestamp)
            VALUES (?, ?, ?)
        ''', (user_id, track_id, int(datetime.now().timestamp())))
        conn.commit()

    try:
        return send_from_directory(IMAGES_FOLDER, "pixel.png")
    except Exception as e:
        return f"Error serving image: {e}", 500

@app.route('/<user_id>/showmee', methods=['GET'])
def show_user_data(user_id):
    # Connect to the database
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(''' 
            SELECT track_id, timestamp FROM tracking_data
            WHERE user_id = ?
        ''', (user_id,))
        rows = cursor.fetchall()

    kolkata_tz = pytz.timezone('Asia/Kolkata')
    
    id_map = {}
    for track_id, timestamp in rows:
        dt = datetime.fromtimestamp(timestamp, tz=pytz.utc)
        kolkata_time = dt.astimezone(kolkata_tz)
        human_time = kolkata_time.strftime('%Y-%m-%d %H:%M:%S')

        if track_id not in id_map:
            id_map[track_id] = []
        id_map[track_id].append(human_time)

    return render_template('show_me.html', user_id=user_id, id_map=id_map)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6565, debug=True)