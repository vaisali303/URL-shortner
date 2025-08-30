from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3, string, random, webbrowser
from threading import Timer

app = Flask(__name__)
DB = "urls.db"

# ------------------ DATABASE SETUP ------------------
def init_db():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS urls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    long_url TEXT NOT NULL,
                    short_code TEXT NOT NULL UNIQUE)''')
    conn.commit()
    conn.close()

# ------------------ SHORT CODE GENERATOR ------------------
def generate_code(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

# ------------------ HOME PAGE ------------------
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        long_url = request.form["long_url"]

        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute("SELECT short_code FROM urls WHERE long_url=?", (long_url,))
        row = cursor.fetchone()

        if row:
            short_code = row[0]
        else:
            short_code = generate_code()
            cursor.execute("INSERT INTO urls (long_url, short_code) VALUES (?, ?)", (long_url, short_code))
            conn.commit()

        conn.close()
        return render_template("index.html", short_url=request.host_url + short_code)

    return render_template("index.html", short_url=None)

# ------------------ REDIRECT SHORT URL ------------------
@app.route("/<short_code>")
def redirect_to_url(short_code):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT long_url FROM urls WHERE short_code=?", (short_code,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return redirect(row[0])
    return "❌ Invalid short URL!", 404

# ------------------ VIEW ALL URLS ------------------
@app.route("/urls")
def view_urls():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT id, long_url, short_code FROM urls")
    urls = cursor.fetchall()
    conn.close()
    return render_template("urls.html", urls=urls, host=request.host_url)

# ------------------ DELETE URL ------------------
@app.route("/delete/<int:url_id>", methods=["POST"])
def delete_url(url_id):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM urls WHERE id=?", (url_id,))
    conn.commit()
    conn.close()
    return {"status": "success"}

# ------------------ AUTO OPEN BROWSER ------------------
import webbrowser
import threading
from app import app

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")

if __name__ == '__main__':
    threading.Timer(1, open_browser).start()
    app.run(debug=False)


