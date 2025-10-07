from flask import Flask, render_template_string, request, redirect
import sqlite3

app = Flask("test")

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
        <input type="hidden" name="id" id="id" value="{{ user[0] }}">
        <input type="text" name="name" id="name" value="{{ user[1] }}" required>
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
                    <a href="{{ url_for('show', id=row[0]) }}" class="show">Düzenle</a>
                    <a href="{{ url_for('remove', id=row[0]) }}" class="remove">Sil</a>
                </td>
            </tr>
        {% endfor %}
    </tbody>
</table>

</body>
</html>
"""

@app.route("/")
def list():
    conn = sqlite3.connect("test.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    columns = [description[0] for description in cursor.description]
    conn.close()
    return render_template_string(HTML_TEMPLATE, columns=columns, rows=rows)


@app.route("/add", methods=["POST"])
def add():
    name = request.form.get("name")
    if name:
        conn = sqlite3.connect("test.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name) VALUES (?)", (name,))
        conn.commit()
        conn.close()
    return redirect("/")

@app.route("/remove")
def remove(id):
    conn = sqlite3.connect("test.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/show")
def show(id):
    conn = sqlite3.connect("test.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (id,))
    user = cursor.fetchone()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    columns = [description[0] for description in cursor.description]
    conn.close()
    return render_template_string(HTML_TEMPLATE, columns=columns, rows=rows, user=user)

@app.route("/update", methods=["POST"])
def update():
    conn = sqlite3.connect("test.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET name = ? WHERE id = ?", (request.form.get("name"), request.form.get("id")))
    conn.commit()
    conn.close()
    return redirect("/")    

app.add_url_rule('/show/<id>', 'show', show)
app.add_url_rule('/remove/<id>', 'remove', remove)

app.run(host="127.0.0.1", port=8080, debug=True)
