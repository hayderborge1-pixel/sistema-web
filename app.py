from flask import Flask, render_template_string, request
import requests
import sqlite3

app = Flask(__name__)

# =====================================
# TELEGRAM
# =====================================

TOKEN = "8455169869:AAGblAeDhz58yK2kFUicH2fNxahEzxxhzPo"
CHAT_ID = "7736448244"

# =====================================
# BASE DE DATOS
# =====================================

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

# =====================================
# HTML PRINCIPAL
# =====================================

HTML = """

<!DOCTYPE html>
<html>

<head>

<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>Soporte Técnico</title>

<style>

body{
    background:#1e1e1e;
    color:white;
    font-family:Arial;
    text-align:center;
    padding:40px;
}

.container{
    max-width:500px;
    margin:auto;
    background:#2b2b2b;
    padding:30px;
    border-radius:10px;
}

input, select, textarea{
    width:90%;
    padding:12px;
    margin:10px;
    border:none;
    border-radius:5px;
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
    border-radius:5px;
    font-size:16px;
    cursor:pointer;
}

button:hover{
    background:#005fa3;
}

.ticket{
    background:#111827;
    padding:25px;
    border-radius:10px;
    margin-top:20px;
}

.orden{
    color:#00BFFF;
    font-size:40px;
    font-weight:bold;
}

.estado{
    color:orange;
    font-size:28px;
    font-weight:bold;
}

a{
    color:#00BFFF;
    text-decoration:none;
    font-size:18px;
}

</style>

</head>

<body>

<div class="container">

{% if enviado == False %}

<h1>Sistema Inteligente de Soporte Técnico</h1>

<form method="POST">

<input
type="text"
name="nombre"
placeholder="Nombre del cliente"
required
>

<input
type="text"
name="telefono"
placeholder="Número de teléfono"
required
>

<select name="problema" required>

<option value="">Seleccione una falla</option>

<option>No enciende</option>
<option>Pantalla azul</option>
<option>Muy lenta</option>
<option>Se apaga sola</option>
<option>Sin internet</option>
<option>No hay sonido</option>
<option>Error de sistema</option>
<option>Virus</option>
<option>Otro</option>

</select>

<textarea
name="comentario"
placeholder="Describa el problema"
required
></textarea>

<button type="submit">
Solicitar Soporte Técnico
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
Consultar Estado de Reparación
</a>

</div>

</body>
</html>

"""

# =====================================
# HTML CONSULTA
# =====================================

CONSULTA_HTML = """

<!DOCTYPE html>
<html>

<head>

<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>Consultar Estado</title>

<style>

body{
    background:#1e1e1e;
    color:white;
    font-family:Arial;
    text-align:center;
    padding:40px;
}

.container{
    max-width:500px;
    margin:auto;
    background:#2b2b2b;
    padding:30px;
    border-radius:10px;
}

input{
    width:90%;
    padding:12px;
    margin:10px;
    border:none;
    border-radius:5px;
}

button{
    background:#0078D7;
    color:white;
    border:none;
    padding:15px;
    width:95%;
    border-radius:5px;
    cursor:pointer;
}

.ticket{
    background:#111827;
    padding:20px;
    border-radius:10px;
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

# =====================================
# PAGINA PRINCIPAL
# =====================================

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

        # =====================================
        # LINK DIRECTO PARA CAMBIAR ESTADO
        # =====================================

        link_revision = f"https://sistema-web-90xi.onrender.com/actualizar?ticket={ticket_id}&estado=EN_REVISION"

        link_reparando = f"https://sistema-web-90xi.onrender.com/actualizar?ticket={ticket_id}&estado=REPARANDO"

        link_listo = f"https://sistema-web-90xi.onrender.com/actualizar?ticket={ticket_id}&estado=LISTO"

        link_entregado = f"https://sistema-web-90xi.onrender.com/actualizar?ticket={ticket_id}&estado=ENTREGADO"

        texto = f"""
🔥 NUEVA FALLA REPORTADA

📄 ORDEN:
#{orden}

📌 ESTADO:
{estado}

👤 CLIENTE:
{nombre}

📞 TELÉFONO:
{telefono}

💻 FALLA:
{problema}

📝 COMENTARIO:
{comentario}

====================

CAMBIAR ESTADO:

EN REVISION:
{link_revision}

REPARANDO:
{link_reparando}

LISTO:
{link_listo}

ENTREGADO:
{link_entregado}
"""

        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

        data = {
            "chat_id": CHAT_ID,
            "text": texto
        }

        requests.post(url, data=data)

        mensaje = f"""

        <h2 style='color:#00ff88;'>
        ✅ REPORTE ENVIADO
        </h2>

        <hr>

        <h3>
        Número de Orden
        </h3>

        <div class='orden'>
        #{orden}
        </div>

        <br>

        <h3>
        Estado de Reparación
        </h3>

        <div class='estado'>
        {estado}
        </div>

        <br>

        <p>
        Use este número para consultar el estado.
        </p>

        """

    return render_template_string(
        HTML,
        mensaje=mensaje,
        enviado=enviado
    )

# =====================================
# CONSULTAR ESTADO
# =====================================

@app.route("/consulta", methods=["GET", "POST"])
def consulta():

    resultado = ""

    if request.method == "POST":

        orden = request.form["orden"]

        ticket_id = int(orden)

        conn = sqlite3.connect("soporte.db")

        cursor = conn.cursor()

        cursor.execute("""

        SELECT * FROM tickets
        WHERE id = ?

        """, (ticket_id,))

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
            ❌ Orden no encontrada
            </h2>

            </div>

            """

    return render_template_string(
        CONSULTA_HTML,
        resultado=resultado
    )

# =====================================
# CAMBIAR ESTADO
# =====================================

@app.route("/actualizar")
def actualizar():

    ticket = request.args.get("ticket")
    estado = request.args.get("estado")

    conn = sqlite3.connect("soporte.db")

    cursor = conn.cursor()

    cursor.execute("""

    UPDATE tickets
    SET estado = ?
    WHERE id = ?

    """, (estado, ticket))

    conn.commit()
    conn.close()

    return f"""

    <h1>
    ✅ Orden {int(ticket):04d} actualizada a {estado}
    </h1>

    <br><br>

    <a href="/consulta">
    Consultar Estado
    </a>

    """

# =====================================
# INICIAR
# =====================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)