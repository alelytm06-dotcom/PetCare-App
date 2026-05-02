from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

mascotas = []

# Página principal
@app.route("/")
def home():
    return send_from_directory("", "index.html")

# Crear mascota
@app.route("/mascotas", methods=["POST"])
def agregar_mascota():
    data = request.json

    if "nombre" not in data or "edad" not in data:
        return {"error": "Datos incompletos"}, 400

    data["vacunas"] = []
    mascotas.append(data)

    return {"mensaje": "Mascota creada"}

# Ver mascotas
@app.route("/mascotas", methods=["GET"])
def ver_mascotas():
    return jsonify(mascotas)

# Agregar vacuna
@app.route("/vacunas", methods=["POST"])
def agregar_vacuna():
    data = request.json

    nombre_mascota = data["nombre"]
    vacuna = data["vacuna"]

    for m in mascotas:
        if m["nombre"] == nombre_mascota:
            fecha_hoy = datetime.now()
            proxima = fecha_hoy + timedelta(days=30)

            nueva_vacuna = {
                "vacuna": vacuna,
                "fecha": fecha_hoy.strftime("%Y-%m-%d"),
                "proxima": proxima.strftime("%Y-%m-%d")
            }

            m["vacunas"].append(nueva_vacuna)
            return {"mensaje": "Vacuna agregada"}

    return {"error": "Mascota no encontrada"}, 404

# Recordatorios
@app.route("/recordatorios", methods=["GET"])
def recordatorios():
    hoy = datetime.now()
    alertas = []

    for m in mascotas:
        for v in m["vacunas"]:
            fecha_proxima = datetime.strptime(v["proxima"], "%Y-%m-%d")

            if fecha_proxima <= hoy:
                alertas.append({
                    "mascota": m["nombre"],
                    "vacuna": v["vacuna"],
                    "estado": "URGENTE"
                })

    return jsonify(alertas)

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)