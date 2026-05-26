from flask import Flask, render_template_string, request
import requests

app = Flask(__name__)

TOKEN = "8455169869:AAGblAeDhz58yK2kFUicH2fNxahEzxxhzPo"
CHAT_ID = "7736448244"

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

</style>

</head>

<body>

<div class="container">

<h1>Sistema Inteligente de Soporte Técnico</h1>

<form method="POST" enctype="multipart/form-data">

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
Solicitar Soporte Técnico
</button>

</form>

<h2>{{ mensaje }}</h2>

</div>

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
        comentario = request.form["comentario"]

        archivo = request.files["archivo"]

        texto = f"""
🔥 NUEVA FALLA REPORTADA

👤 Nombre:
{nombre}

📞 Teléfono:
{telefono}

💻 Problema:
{problema}

📝 Comentario:
{comentario}

📡 Un técnico se contactará contigo.
"""

        # MENSAJE TELEGRAM

        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

        data = {
            "chat_id": CHAT_ID,
            "text": texto
        }

        requests.post(url, data=data)

        # ENVIAR ARCHIVO

        if archivo.filename != "":

            url_archivo = f"https://api.telegram.org/bot{TOKEN}/sendDocument"

            files = {
                "document": (
                    archivo.filename,
                    archivo.stream,
                    archivo.mimetype
                )
            }

            data_archivo = {
                "chat_id": CHAT_ID
            }

            requests.post(
                url_archivo,
                data=data_archivo,
                files=files
            )

        mensaje = "✅ Un técnico se contactará contigo."

    return render_template_string(
        HTML,
        mensaje=mensaje
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)