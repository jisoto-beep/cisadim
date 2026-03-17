from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime
import random

app = Flask(__name__)
CORS(app)

# ── DATABASE SETUP ──────────────────────────────────────────
# This creates the cisadim.db file automatically if it doesn't exist
DB_PATH = "cisadim.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS quejas (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            referencia  TEXT,
            fecha_envio TEXT,

            -- Section 1: Client data
            nombre      TEXT,
            cargo       TEXT,
            empresa     TEXT,
            correo      TEXT,
            telefono    TEXT,

            -- Section 2: Work description
            fecha_trabajo   TEXT,
            codigo_servicio TEXT,
            tipo_servicio   TEXT,
            instrumento     TEXT,

            -- Section 3: Complaint info
            fecha_queja TEXT,
            naturaleza  TEXT,
            descripcion TEXT,
            evidencia   TEXT,

            -- Section 4: Requested action
            accion      TEXT,
            accion_otra TEXT
        )
    ''')
    conn.commit()
    conn.close()

# ── SERVE THE WEBPAGE ────────────────────────────────────────
@app.route('/')
def index():
    return send_from_directory('.', 'cisadim.html')

# ── RECEIVE THE FORM ─────────────────────────────────────────
@app.route('/enviar', methods=['POST'])
def enviar():
    data = request.json

    # Generate a reference number like QR-2025-4823
    ref = f"QR-{datetime.now().year}-{random.randint(1000, 9999)}"
    fecha_envio = datetime.now().strftime("%d/%m/%Y %H:%M")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO quejas (
            referencia, fecha_envio,
            nombre, cargo, empresa, correo, telefono,
            fecha_trabajo, codigo_servicio, tipo_servicio, instrumento,
            fecha_queja, naturaleza, descripcion, evidencia,
            accion, accion_otra
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        ref, fecha_envio,
        data.get('nombre'), data.get('cargo'), data.get('empresa'),
        data.get('correo'), data.get('telefono'),
        data.get('fechaTrabajo'), data.get('codigoServicio'),
        data.get('tipoServicio'), data.get('instrumento'),
        data.get('fechaQueja'), data.get('naturaleza'),
        data.get('descripcion'), data.get('evidencia'),
        data.get('accion'), data.get('accionOtra')
    ))
    conn.commit()
    conn.close()

    print(f"✓ Nueva queja recibida: {ref} de {data.get('nombre')} ({data.get('correo')})")

    return jsonify({ "ok": True, "referencia": ref })

# ── ADMIN PAGE — see all complaints ─────────────────────────
@app.route('/admin')
def admin():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM quejas ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()

    # Build a simple HTML table
    html = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
    <meta charset="UTF-8">
    <title>Admin – Quejas CISADIM</title>
    <style>
        body { font-family: sans-serif; padding: 2rem; background: #f7f5f1; }
        h1 { color: #0d1f3c; margin-bottom: 1rem; }
        .count { color: #6b6560; margin-bottom: 1.5rem; font-size: 0.9rem; }
        table { width: 100%; border-collapse: collapse; background: white; border-radius: 6px; overflow: hidden; box-shadow: 0 2px 12px rgba(0,0,0,0.07); }
        th { background: #0d1f3c; color: white; padding: 0.75rem 1rem; text-align: left; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; }
        td { padding: 0.75rem 1rem; border-bottom: 1px solid #eee; font-size: 0.88rem; vertical-align: top; }
        tr:last-child td { border-bottom: none; }
        tr:hover td { background: #fafafa; }
        .ref { color: #c8973a; font-weight: 600; }
        .empty { text-align: center; padding: 3rem; color: #6b6560; }
    </style>
    </head>
    <body>
    <h1>🗂 Panel de Quejas — CISADIM</h1>
    """

    if not rows:
        html += '<p class="empty">No hay quejas registradas aún.</p>'
    else:
        html += f'<p class="count">Total: {len(rows)} queja(s) recibida(s)</p>'
        html += """
        <table>
        <tr>
            <th>Referencia</th>
            <th>Fecha Envío</th>
            <th>Nombre</th>
            <th>Correo</th>
            <th>Naturaleza</th>
            <th>Descripción</th>
            <th>Acción Solicitada</th>
        </tr>
        """
        for row in rows:
            html += f"""
            <tr>
                <td class="ref">{row['referencia']}</td>
                <td>{row['fecha_envio']}</td>
                <td>{row['nombre']}<br><small style="color:#999">{row['cargo']} — {row['empresa'] or '—'}</small></td>
                <td>{row['correo']}<br><small style="color:#999">{row['telefono']}</small></td>
                <td>{row['naturaleza']}</td>
                <td style="max-width:300px">{row['descripcion']}</td>
                <td>{row['accion']}</td>
            </tr>
            """
        html += "</table>"

    html += "</body></html>"
    return html

# ── START ────────────────────────────────────────────────────
if __name__ == '__main__':
    init_db()
    print("─────────────────────────────────────")
    print("  CISADIM backend running!")
    print("  Webpage  → http://localhost:5000")
    print("  Admin    → http://localhost:5000/admin")
    print("─────────────────────────────────────")
    app.run(debug=True)
