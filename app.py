from flask import Flask, render_template_string, request, redirect, session
import requests
import sqlite3
import telebot
import threading
import os
import time
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)

# =========================================
# CONFIGURACIÓN SEGURA
# =========================================

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "Hayder2026_Soporte_Privado"
)

TOKEN = os.environ.get( "8455169869:AAGblAeDhz58yK2kFUicH2fNxahEzxxhzPo")
CHAT_ID = os.environ.get("7736448244")

bot = telebot.TeleBot("8455169869:AAGblAeDhz58yK2kFUicH2fNxahEzxxhzPo")
# =========================================
# LOGIN ADMIN
# =========================================

ADMIN_USER = os.environ.get("ADMIN_USER", "admin")
ADMIN_PASS = os.environ.get("ADMIN_PASS", "1234")

# =========================================
# CARPETA ARCHIVOS
# =========================================

UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# =========================================
# HORARIOS DISPONIBLES
# =========================================

HORARIOS = [
    "09:00",
    "10:00",
    "11:00",
    "12:00",
    "13:00",
    "14:00",
    "15:00"
]

# =========================================
# BASE DE DATOS
# =========================================

def crear_db():

    conn = sqlite3.connect("soporte.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tickets (

        id INTEGER PRIMARY KEY AUTOINCREMENT,
        empresa TEXT,
        sucursal TEXT,
        nombre TEXT,
        telefono TEXT,
        problema TEXT,
        comentario TEXT,
        estado TEXT,
        fecha_visita TEXT,
        hora_visita TEXT,
        archivo TEXT

    )
    """)

    conn.commit()
    conn.close()

crear_db()

# =========================================
# HTML PRINCIPAL
# =========================================

HTML = """

<!DOCTYPE html>
<html>
<head>

<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>Soporte Técnico</title>

<style>

body{
    background:#111827;
    color:white;
    font-family:Arial;
    text-align:center;
    padding:40px;
}

.container{
    max-width:550px;
    margin:auto;
    background:#1f2937;
    padding:30px;
    border-radius:15px;
}

input, select, textarea{
    width:90%;
    padding:14px;
    margin:10px;
    border:none;
    border-radius:8px;
    font-size:16px;
}

textarea{
    height:120px;
    resize:none;
}

button{
    background:#0078D7;
    color:white;
    border:none;
    padding:15px;
    width:95%;
    border-radius:8px;
    font-size:16px;
    cursor:pointer;
}

.ticket{
    background:#0f172a;
    padding:25px;
    border-radius:15px;
}

.estado{
    color:#00BFFF;
    font-size:30px;
    font-weight:bold;
}

.orden{
    color:#00ff88;
    font-size:40px;
    font-weight:bold;
}

a{
    color:#00BFFF;
    text-decoration:none;
}

.error{
    color:red;
    font-weight:bold;
}

</style>

</head>

<body>

<div class="container">

{% if not enviado %}

<h1>Soporte Técnico</h1>

<form method="POST" enctype="multipart/form-data">

<input type="text" name="empresa" placeholder="Nombre de la empresa" required>

<input type="text" name="sucursal" placeholder="Sucursal" required>

<input type="text" name="nombre" placeholder="Nombre del cliente" required>

<input
type="text"
name="telefono"
placeholder="Teléfono"
maxlength="8"
oninput="this.value=this.value.replace(/[^0-9]/g,'')"
required
>

<select name="problema" required>

<option value="">Seleccione una falla</option>

<option>No enciende</option>
<option>Pantalla azul</option>
<option>Muy lenta</option>
<option>Sin internet</option>
<option>Virus</option>
<option>Otro</option>

</select>

<textarea
name="comentario"
placeholder="Describa el problema"
required
></textarea>

<h3>Agendar Visita</h3>

<input type="date" name="fecha_visita" required>

<select name="hora_visita" required>

<option value="">Seleccione horario</option>

{% for h in horarios %}
<option value="{{ h }}">{{ h }}</option>
{% endfor %}

</select>

<input type="file" name="archivo">

<br><br>

<button type="submit">
Enviar Reporte
</button>

</form>

{% endif %}

{% if mensaje %}

<div class="ticket">

{{ mensaje|safe }}

</div>

{% endif %}

<br><br>

<a href="/consulta">Consultar Estado</a>

<br><br>

<a href="/login">Panel Técnico</a>

</div>

</body>
</html>

"""

# =========================================
# LOGIN HTML
# =========================================

LOGIN_HTML = """

<!DOCTYPE html>
<html>
<head>

<title>Login</title>

<style>

body{
    background:#111827;
    color:white;
    font-family:Arial;
    text-align:center;
    padding:40px;
}

.container{
    max-width:400px;
    margin:auto;
    background:#1f2937;
    padding:30px;
    border-radius:15px;
}

input{
    width:90%;
    padding:14px;
    margin:10px;
    border:none;
    border-radius:8px;
}

button{
    background:#0078D7;
    color:white;
    border:none;
    padding:15px;
    width:95%;
    border-radius:8px;
}

</style>

</head>

<body>

<div class="container">

<h1>Login Técnico</h1>

<form method="POST">

<input type="text" name="usuario" placeholder="Usuario" required>

<input type="password" name="password" placeholder="Contraseña" required>

<button type="submit">Ingresar</button>

</form>

<p style="color:red;">{{ error }}</p>

</div>

</body>
</html>

"""

# =========================================
# PANEL ADMIN
# =========================================

PANEL_HTML = """

<!DOCTYPE html>
<html>
<head>

<title>Panel Técnico</title>

<style>

body{
    background:#111827;
    color:white;
    font-family:Arial;
    padding:20px;
}

.ticket{
    background:#1f2937;
    padding:20px;
    margin-bottom:20px;
    border-radius:15px;
}

select,input{
    padding:10px;
    border-radius:8px;
    margin:5px;
}

button{
    background:#0078D7;
    color:white;
    border:none;
    padding:10px;
    border-radius:8px;
}

</style>

</head>

<body>

<h1>Panel Técnico</h1>

<a href="/logout" style="color:red;">Cerrar sesión</a>

<br><br>

{% for t in tickets %}

<div class="ticket">

<h2>Orden #{{ '%04d' % t[0] }}</h2>

<p><b>Empresa:</b> {{ t[1] }}</p>
<p><b>Sucursal:</b> {{ t[2] }}</p>
<p><b>Cliente:</b> {{ t[3] }}</p>
<p><b>Teléfono:</b> {{ t[4] }}</p>
<p><b>Problema:</b> {{ t[5] }}</p>
<p><b>Comentario:</b> {{ t[6] }}</p>
<p><b>Estado:</b> {{ t[7] }}</p>
<p><b>Fecha visita:</b> {{ t[8] }}</p>
<p><b>Hora visita:</b> {{ t[9] }}</p>

{% if t[10] %}
<p><b>Archivo:</b> {{ t[10] }}</p>
{% endif %}

<form method="POST" action="/actualizar">

<input type="hidden" name="id" value="{{ t[0] }}">

<select name="estado">

<option>PENDIENTE</option>
<option>EN_REVISION</option>
<option>REPARANDO</option>
<option>LISTO</option>
<option>ENTREGADO</option>

</select>

<button type="submit">
Actualizar
</button>

</form>

</div>

{% endfor %}

</body>
</html>

"""

# =========================================
# CONSULTA HTML
# =========================================

CONSULTA_HTML = """

<!DOCTYPE html>
<html>
<head>

<title>Consulta</title>

<style>

body{
    background:#111827;
    color:white;
    font-family:Arial;
    text-align:center;
    padding:40px;
}

.container{
    max-width:500px;
    margin:auto;
    background:#1f2937;
    padding:30px;
    border-radius:15px;
}

input{
    width:90%;
    padding:14px;
    margin:10px;
    border:none;
    border-radius:8px;
}

button{
    background:#0078D7;
    color:white;
    border:none;
    padding:15px;
    width:95%;
    border-radius:8px;
}

.ticket{
    background:#0f172a;
    padding:25px;
    border-radius:15px;
    margin-top:20px;
}

</style>

</head>

<body>

<div class="container">

<h1>Consultar Estado</h1>

<form method="POST">

<input
type="number"
name="orden"
placeholder="Ingrese número de orden"
required
>

<button type="submit">
Consultar
</button>

</form>

{{ resultado|safe }}

</div>

</body>
</html>

"""

# =========================================
# LOGIN
# =========================================

@app.route("/login", methods=["GET", "POST"])
def login():

    error = ""

    if request.method == "POST":

        usuario = request.form["usuario"]
        password = request.form["password"]

        if usuario == ADMIN_USER and password == ADMIN_PASS:

            session["admin"] = True
            return redirect("/panel")

        else:

            error = "Datos incorrectos"

    return render_template_string(LOGIN_HTML, error=error)

# =========================================
# PANEL
# =========================================

@app.route("/panel")
def panel():

    if not session.get("admin"):
        return redirect("/login")

    conn = sqlite3.connect("soporte.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tickets ORDER BY id DESC")

    tickets = cursor.fetchall()

    conn.close()

    return render_template_string(PANEL_HTML, tickets=tickets)

# =========================================
# ACTUALIZAR ESTADO
# =========================================

@app.route("/actualizar", methods=["POST"])
def actualizar():

    if not session.get("admin"):
        return redirect("/login")

    ticket_id = request.form["id"]
    estado = request.form["estado"]

    conn = sqlite3.connect("soporte.db")
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE tickets SET estado=? WHERE id=?",
        (estado, ticket_id)
    )

    conn.commit()
    conn.close()

    return redirect("/panel")

# =========================================
# LOGOUT
# =========================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")

# =========================================
# BOT TELEGRAM
# =========================================

@bot.message_handler(commands=['estado'])
def cambiar_estado(message):

    try:

        datos = message.text.split()

        if len(datos) < 3:

            bot.reply_to(
                message,
                "Use:\n/estado 1 REPARANDO"
            )
            return

        ticket = int(datos[1])
        estado = datos[2]

        conn = sqlite3.connect("soporte.db")
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE tickets SET estado=? WHERE id=?",
            (estado, ticket)
        )

        conn.commit()
        conn.close()

        bot.reply_to(
            message,
            f"✅ Orden {ticket} actualizada"
        )

    except Exception as e:

        bot.reply_to(
            message,
            f"ERROR: {str(e)}"
        )

# =========================================
# PAGINA PRINCIPAL
# =========================================

@app.route("/", methods=["GET", "POST"])
def inicio():

    mensaje = ""
    enviado = False

    if request.method == "POST":

        try:

            empresa = request.form["empresa"].strip()
            sucursal = request.form["sucursal"].strip()
            nombre = request.form["nombre"].strip()
            telefono = request.form["telefono"].strip()
            problema = request.form["problema"].strip()
            comentario = request.form["comentario"].strip()
            fecha_visita = request.form["fecha_visita"]
            hora_visita = request.form["hora_visita"]

            # VALIDAR TELÉFONO
            if len(telefono) != 8:

                mensaje = """
                <div class='error'>
                El teléfono debe tener 8 números
                </div>
                """

                return render_template_string(
                    HTML,
                    mensaje=mensaje,
                    enviado=False,
                    horarios=HORARIOS
                )

            # VALIDAR LUNES A VIERNES
            fecha_obj = datetime.strptime(
                fecha_visita,
                "%Y-%m-%d"
            )

            if fecha_obj.weekday() >= 5:

                mensaje = """
                <div class='error'>
                Solo se permiten citas de lunes a viernes
                </div>
                """

                return render_template_string(
                    HTML,
                    mensaje=mensaje,
                    enviado=False,
                    horarios=HORARIOS
                )

            # GUARDAR ARCHIVO
            archivo_nombre = ""

            archivo = request.files.get("archivo")

            if archivo and archivo.filename != "":

                nombre_seguro = secure_filename(
                    archivo.filename
                )

                archivo_nombre = (
                    f"{int(time.time())}_{nombre_seguro}"
                )

                ruta = os.path.join(
                    UPLOAD_FOLDER,
                    archivo_nombre
                )

                archivo.save(ruta)

            conn = sqlite3.connect("soporte.db")
            cursor = conn.cursor()

            # VALIDAR CITA DUPLICADA
            cursor.execute("""

            SELECT * FROM tickets
            WHERE fecha_visita=?
            AND hora_visita=?

            """, (
                fecha_visita,
                hora_visita
            ))

            cita = cursor.fetchone()

            if cita:

                conn.close()

                mensaje = """
                <div class='error'>
                Ese horario ya está ocupado
                </div>
                """

                return render_template_string(
                    HTML,
                    mensaje=mensaje,
                    enviado=False,
                    horarios=HORARIOS
                )

            estado = "PENDIENTE"

            cursor.execute("""

            INSERT INTO tickets
            (
                empresa,
                sucursal,
                nombre,
                telefono,
                problema,
                comentario,
                estado,
                fecha_visita,
                hora_visita,
                archivo
            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

            """, (
                empresa,
                sucursal,
                nombre,
                telefono,
                problema,
                comentario,
                estado,
                fecha_visita,
                hora_visita,
                archivo_nombre
            ))

            conn.commit()

            ticket_id = cursor.lastrowid

            conn.close()

            orden = f"{ticket_id:04d}"

            texto = f"""
🔥 NUEVA CITA

📄 ORDEN #{orden}

🏢 Empresa: {empresa}
🏬 Sucursal: {sucursal}

👤 Cliente: {nombre}
📞 {telefono}

💻 Problema: {problema}

📅 Fecha: {fecha_visita}
⏰ Hora: {hora_visita}

📝 {comentario}

📌 Estado: {estado}
"""

            try:

                requests.post(
                    f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                    data={
                        "chat_id": CHAT_ID,
                        "text": texto
                    },
                    timeout=10
                )

            except:
                pass

            mensaje = f"""

            <h2>
            ✅ CITA AGENDADA
            </h2>

            <hr>

            <h3>Número de Orden</h3>

            <div class='orden'>
            #{orden}
            </div>

            <br>

            <h3>Fecha</h3>

            <div class='estado'>
            {fecha_visita}
            </div>

            <br>

            <h3>Hora</h3>

            <div class='estado'>
            {hora_visita}
            </div>

            <br>

            <h3>Estado</h3>

            <div class='estado'>
            {estado}
            </div>

            """

            enviado = True

        except Exception as e:

            mensaje = f"""
            <div class='error'>
            ERROR:
            <br><br>
            {str(e)}
            </div>
            """

    return render_template_string(
        HTML,
        mensaje=mensaje,
        enviado=enviado,
        horarios=HORARIOS
    )

# =========================================
# CONSULTAR ESTADO
# =========================================

@app.route("/consulta", methods=["GET", "POST"])
def consulta():

    resultado = ""

    if request.method == "POST":

        orden = request.form["orden"]

        conn = sqlite3.connect("soporte.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM tickets WHERE id=?",
            (orden,)
        )

        ticket = cursor.fetchone()

        conn.close()

        if ticket:

            resultado = f"""

            <div class='ticket'>

            <h2>
            Orden #{int(ticket[0]):04d}
            </h2>

            <h1 style='color:#00BFFF;'>
            {ticket[7]}
            </h1>

            <p>
            Fecha visita: {ticket[8]}
            </p>

            <p>
            Hora visita: {ticket[9]}
            </p>

            </div>

            """

        else:

            resultado = """

            <div class='ticket'>

            <h2 style='color:red;'>
            Orden no encontrada
            </h2>

            </div>

            """

    return render_template_string(
        CONSULTA_HTML,
        resultado=resultado
    )

# =========================================
# INICIAR BOT
# =========================================

def iniciar_bot():

    while True:

        try:
            bot.infinity_polling(skip_pending=True)

        except Exception as e:

            print("ERROR BOT:", e)

            time.sleep(5)

threading.Thread(
    target=iniciar_bot,
    daemon=True
).start()

# =========================================
# INICIAR APP
# =========================================

if __name__ == "__main__":

    port = int(
        os.environ.get("PORT", 5000)
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )