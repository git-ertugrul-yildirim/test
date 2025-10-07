from flask import Flask, render_template, request, redirect, g
import sqlite3
import os
from collections import namedtuple

# Constants
# ------------------------------------------------------------

DB_PATH = "app.db"
TEMPLATE_NAME = "index.html"


# Routes: list, add, remove, show, update 
# ------------------------------------------------------------

app = Flask(__name__, static_url_path='/static', static_folder='static')

@app.route("/")
def list():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    columns = [description[0] for description in cursor.description]
    return render_template(TEMPLATE_NAME, columns=columns, rows=rows)


@app.route("/add", methods=["POST"])
def add():
    name = request.form.get("name")
    if name:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name) VALUES (?)", (name,))
        conn.commit()
    return redirect("/")

@app.route('/remove/<id>')
def remove(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (id,))
    conn.commit()
    return redirect("/")

@app.route('/show/<id>')
def show(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (id,))
    user = cursor.fetchone()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    columns = [description[0] for description in cursor.description]
    return render_template(TEMPLATE_NAME, columns=columns, rows=rows, user=user)

@app.route("/update", methods=["POST"])
def update():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET name = ? WHERE id = ?", (request.form.get("name"), request.form.get("id")))
    conn.commit()
    return redirect("/")    


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

# Main
# ------------------------------------------------------------

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', '8080'))
    app.run(host="127.0.0.1", port=port, debug=True)
