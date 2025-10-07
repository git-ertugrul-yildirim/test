from flask import Flask, render_template, request, g, jsonify
import sqlite3
import os
from collections import namedtuple

# Constants
# ------------------------------------------------------------

DB_PATH = "app.db"
TEMPLATE_NAME = "index.html"


# Routes: fetch, get, insert, delete, update
# ------------------------------------------------------------

app = Flask(__name__, static_url_path='/static', static_folder='static')

@app.route("/")
def root():
    return render_template(TEMPLATE_NAME)

@app.route('/users', methods=['GET'])
def users_list():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    return jsonify([get_json_item(r) for r in rows])


@app.route('/users/<int:id>', methods=['GET'])
def users_get(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (id,))
    user = cursor.fetchone()
    if user is None:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(get_json_item(user))


@app.route('/users', methods=['POST'])
def users_create():
    data = request.get_json(silent=True) or {}
    name = data.get('name')
    if not name:
        return jsonify({'error': 'name is required'}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name) VALUES (?)", (name,))
    conn.commit()
    last_id = cursor.lastrowid
    cursor.execute("SELECT * FROM users WHERE id = ?", (last_id,))
    row = cursor.fetchone()
    return jsonify(get_json_item(row)), 201


@app.route('/users/<int:id>', methods=['PUT'])
def users_update(id):
    data = request.get_json(silent=True) or {}
    name = data.get('name')
    if not name:
        return jsonify({'error': 'name is required'}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET name = ? WHERE id = ?", (name, id))
    conn.commit()
    cursor.execute("SELECT * FROM users WHERE id = ?", (id,))
    row = cursor.fetchone()
    if row is None:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(get_json_item(row))


@app.route('/users/<int:id>', methods=['DELETE'])
def users_delete(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (id,))
    conn.commit()
    return ('', 204)

# DB connection handling
# ------------------------------------------------------------

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()    

def get_db_connection():
    if 'db' not in g:
        conn = sqlite3.connect(DB_PATH)
        def namedtuple_factory(cursor, row):
            fields = [col[0] for col in cursor.description]
            Row = namedtuple('Row', fields)
            return Row(*row)
        conn.row_factory = namedtuple_factory
        g.db = conn
    return g.db

def get_json_item(item):
    if item is None:
        return None
    return {k: getattr(item, k) for k in item._fields}

def get_json_list(list):
    return [get_json_item(r) for r in list]

# Main
# ------------------------------------------------------------

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', '8080'))
    app.run(host="127.0.0.1", port=port, debug=True)