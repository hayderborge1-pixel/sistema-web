from flask import Flask, render_template_string, request
import requests
import sqlite3
import telebot
import threading

app = Flask(__name__)

# =========================================
# TELEGRAM
# =========================================

TOKEN = "8455169869:AAGblAeDhz58yK2kFUicH2fNxahEzxxhzPo"
CHAT_ID = "7736448244"

bot = telebot.TeleBot(TOKEN)

# =========================================
# BASE DE DATOS
# =========================================

def crear_db():

    conn = sqlite3.connect("soporte.db")

    cursor = conn.cursor()

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS tickets (

        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        telefono TEXT,
        problema TEXT,
        comentario TEXT,
        estado TEXT

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
    max-width:500px;
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

</style>

</head>

<body>

<div class="container">

{% if not enviado %}

<h1>Soporte Técnico</h1>

<form method="POST" enctype="multipart/form-data">

<input
type="text"
name="nombre"
placeholder="Nombre"
required
>

<input
type="text"
name="telefono"
placeholder="Teléfono"
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

<a href="/consulta">
Consultar Estado
</a>

</div>

</body>
</html>

"""

# =========================================
# HTML CONSULTA
# =========================================

CONSULTA_HTML = """

<!DOCTYPE html>
<html>

<head>

<meta name="viewport" content="width=device-width, initial-scale=1.0">

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
# BOT TELEGRAM
# =========================================

@bot.message_handler(commands=['estado'])
def cambiar_estado(message):

    try:

        datos = message.text.split()

        ticket = datos[1]
        estado = datos[2]

        conn = sqlite3.connect("soporte.db")

        cursor = conn.cursor()

        cursor.execute("""

        UPDATE tickets
        SET estado=?
        WHERE id=?

        """, (estado, ticket))

        conn.commit()
        conn.close()

        bot.reply_to(
            message,
            f"✅ Orden {ticket} actualizada a {estado}"
        )

    except:

        bot.reply_to(
            message,
            "Use:\n/estado 1 REPARANDO"
        )

# =========================================
# PAGINA PRINCIPAL
# =========================================

@app.route("/", methods=["GET", "POST"])
def inicio():

    mensaje = ""
    enviado = False

    if request.method == "POST":

        enviado = True

        nombre = request.form["nombre"]
        telefono = request.form["telefono"]
        problema = request.form["problema"]
        comentario = request.form["comentario"]

        archivo = request.files.get("archivo")

        estado = "PENDIENTE"

        conn = sqlite3.connect("soporte.db")

        cursor = conn.cursor()

        cursor.execute("""

        INSERT INTO tickets
        (nombre, telefono, problema, comentario, estado)

        VALUES (?, ?, ?, ?, ?)

        """, (nombre, telefono, problema, comentario, estado))

        conn.commit()

        ticket_id = cursor.lastrowid

        conn.close()

        orden = f"{ticket_id:04d}"

        texto = f"""
🔥 NUEVA FALLA

📄 ORDEN #{orden}

👤 {nombre}

📞 {telefono}

💻 {problema}

📝 {comentario}

CAMBIAR ESTADO:

/estado {ticket_id} EN_REVISION

/estado {ticket_id} REPARANDO

/estado {ticket_id} LISTO

/estado {ticket_id} ENTREGADO
"""

        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data={
                "chat_id": CHAT_ID,
                "text": texto
            }
        )

        # ENVIAR ARCHIVO

        if archivo and archivo.filename != "":

            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendDocument",
                data={"chat_id": CHAT_ID},
                files={
                    "document": (
                        archivo.filename,
                        archivo.stream,
                        archivo.mimetype
                    )
                }
            )

        mensaje = f"""

        <h2>
        ✅ REPORTE ENVIADO
        </h2>

        <hr>

        <h3>Número de Orden</h3>

        <div class='orden'>
        #{orden}
        </div>

        <br>

        <h3>Estado</h3>

        <div class='estado'>
        {estado}
        </div>

        """

    return render_template_string(
        HTML,
        mensaje=mensaje,
        enviado=enviado
    )

# =========================================
# CONSULTAR
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

            {ticket[5]}

            </h1>

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
    bot.infinity_polling()

threading.Thread(target=iniciar_bot).start()

# =========================================
# INICIAR WEB
# =========================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)