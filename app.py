from flask import Flask, render_template_string, request, redirect, g
import sqlite3
import os
from collections import namedtuple

# Constants
# ------------------------------------------------------------

DB_PATH = "app.db"
HTML_TEMPLATE = """

<!doctype html>

<html lang="tr">
<head>
    <meta charset="utf-8">
    <title>Kullanıcı Listesi</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 2rem; }
        table { border-collapse: collapse; width: 100%; margin-top: 1rem; }
        th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
        th { background-color: #f5f5f5; }
        form { margin-bottom: 1rem; }
        input[type="text"] { padding: 6px; width: 200px; }
        input[type="submit"] { padding: 6px 12px; cursor: pointer; }
    </style>
</head>
<body>
    <h2>Kullanıcılar</h2>


{% if not user %}
    <form action="/add" method="post">
        <label for="name">Kullanıcı:</label>
        <input type="text" name="name" id="name" required>
        <input type="submit" value="Ekle">
    </form>
{% else %}    
    <form action="/update" method="post">
        <label for="name">Kullanıcı:</label>
        <input type="hidden" name="id" id="id" value="{{ user.id }}">
        <input type="text" name="name" id="name" value="{{ user.name }}" required>
        <input type="submit" value="Düzenle">
    </form>    
{% endif %}

<table>
    <thead>
        <tr>
            {% for col in columns %}
                <th>{{ col }}</th>
            {% endfor %}
            <th>İşlem</th>
        </tr>
    </thead>
    <tbody>
        {% for row in rows %}
            <tr>
                {% for value in row %}
                    <td>{{ value }}</td>
                {% endfor %}
                <td>
                    <a href="{{ url_for('show', id=row.id) }}" class="show">Düzenle</a>
                    <a href="{{ url_for('remove', id=row.id) }}" class="remove">Sil</a>
                </td>
            </tr>
        {% endfor %}
    </tbody>
</table>

</body>
</html>
"""

# Routes: list, add, remove, show, update 
# ------------------------------------------------------------

app = Flask("test")

@app.route("/")
def list():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    columns = [description[0] for description in cursor.description]
    return render_template_string(HTML_TEMPLATE, columns=columns, rows=rows)


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
    return render_template_string(HTML_TEMPLATE, columns=columns, rows=rows, user=user)

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
