from flask import Flask, render_template_string, request
import requests

app = Flask(__name__)

TOKEN = "8455169869:AAGblAeDhz58yK2kFUicH2fNxahEzxxhzPo"

CHAT_ID = "7736448244"

HTML = """

<!DOCTYPE html>
<html>

<head>

<title>Soporte Técnico</title>

<style>

body{
    background:#1e1e1e;
    color:white;
    font-family:Arial;
    text-align:center;
    padding:40px;
}

input, select{
    width:300px;
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
    width:320px;
    border-radius:5px;
    font-size:16px;
    cursor:pointer;
}

button:hover{
    background:#005fa3;
}

</style>

</head>

<body>

<h1>Sistema Inteligente de Soporte Técnico</h1>

<form method="POST">

<input type="text" name="nombre" placeholder="Nombre del cliente" required>

<br>

<input type="text" name="telefono" placeholder="Número de teléfono" required>

<br>

<select name="problema">

<option>No enciende</option>
<option>Pantalla azul</option>
<option>Muy lenta</option>
<option>Se apaga sola</option>
<option>Sin internet</option>
<option>No hay sonido</option>

</select>

<br>

<button type="submit">
Solicitar Soporte Técnico
</button>

</form>

<h2>{{ mensaje }}</h2>

</body>
</html>

"""

@app.route("/", methods=["GET", "POST"])

def inicio():

    mensaje = ""

    if request.method == "POST":

        nombre = request.form["nombre"]

        telefono = request.form["telefono"]

        problema = request.form["problema"]

        texto = f"""
NUEVA FALLA REPORTADA

Nombre:
{nombre}

Teléfono:
{telefono}

Problema:
{problema}
"""

        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

        data = {
            "chat_id": CHAT_ID,
            "text": texto
        }

        requests.post(url, data=data)

        mensaje = "✅ Un técnico se contactará contigo."

    return render_template_string(HTML, mensaje=mensaje)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)