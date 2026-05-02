from flask import Flask, request, jsonify, session, render_template
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__, template_folder="templates")
app.secret_key = "clave_super_secreta"
CORS(app)

# ---------------- DB ----------------
def init_db():
    conn = sqlite3.connect("petcare.db")
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS mascotas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        nombre TEXT,
        edad TEXT,
        raza TEXT
    )""")

    conn.commit()
    conn.close()

init_db()

# ---------------- FRONTEND ----------------
@app.route("/")
def home():
    return render_template("index.html")

# ---------------- REGISTER ----------------
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    conn = sqlite3.connect("petcare.db")
    c = conn.cursor()

    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                  (data["username"], data["password"]))
        conn.commit()
        return {"msg": "usuario creado"}
    except:
        return {"error": "usuario ya existe"}
    finally:
        conn.close()

# ---------------- LOGIN ----------------
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    conn = sqlite3.connect("petcare.db")
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE username=? AND password=?",
              (data["username"], data["password"]))

    user = c.fetchone()
    conn.close()

    if user:
        session["user"] = data["username"]
        return {"msg": "logueado"}

    return {"error": "credenciales inválidas"}

# ---------------- CREAR MASCOTA ----------------
@app.route("/mascotas", methods=["POST"])
def crear():
    if "user" not in session:
        return {"error": "no autorizado"}, 403

    data = request.json
    conn = sqlite3.connect("petcare.db")
    c = conn.cursor()

    c.execute("INSERT INTO mascotas (user, nombre, edad, raza) VALUES (?, ?, ?, ?)",
              (session["user"], data["nombre"], data["edad"], data["raza"]))

    conn.commit()
    conn.close()

    return {"msg": "creado"}

# ---------------- LISTAR ----------------
@app.route("/mascotas", methods=["GET"])
def listar():
    if "user" not in session:
        return {"error": "no autorizado"}, 403

    conn = sqlite3.connect("petcare.db")
    c = conn.cursor()

    c.execute("SELECT * FROM mascotas WHERE user=?",
              (session["user"],))

    data = c.fetchall()
    conn.close()

    return jsonify(data)

# ---------------- EDITAR ----------------
@app.route("/editar", methods=["PUT"])
def editar():
    if "user" not in session:
        return {"error": "no autorizado"}, 403

    data = request.json

    conn = sqlite3.connect("petcare.db")
    c = conn.cursor()

    c.execute("""
        UPDATE mascotas
        SET nombre=?, edad=?, raza=?
        WHERE id=? AND user=?
    """, (data["nombre"], data["edad"], data["raza"], data["id"], session["user"]))

    conn.commit()
    conn.close()

    return {"msg": "actualizado"}

# ---------------- RUN ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
