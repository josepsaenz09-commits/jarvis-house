import os
from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI

app = Flask(__name__)

client = OpenAI(
    api_key=os.environ.get("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>JARVIS</title>
<style>
body {
    background:#050b12;
    color:#00d9ff;
    font-family:Arial,sans-serif;
    text-align:center;
    padding:30px;
}
h1 { font-size:42px; }
#status { color:#00ff88; margin-bottom:30px; }
#chat { max-width:700px; margin:auto; text-align:left; }
.message {
    padding:12px;
    margin:10px 0;
    border-radius:10px;
    background:#101c28;
}
input {
    width:70%;
    padding:14px;
    border-radius:8px;
    border:1px solid #00d9ff;
    background:#08121c;
    color:white;
    font-size:16px;
}
button {
    padding:14px 20px;
    margin-left:5px;
    border:none;
    border-radius:8px;
    background:#00d9ff;
    color:#001018;
    font-weight:bold;
}
</style>
</head>

<body>

<h1>JARVIS</h1>
<div id="status">● JARVIS está en línea</div>

<div id="chat"></div>

<input id="message" placeholder="Habla con Jarvis...">
<button onclick="sendMessage()">Enviar</button>

<script>
async function sendMessage() {
    const input = document.getElementById("message");
    const message = input.value.trim();

    if (!message) return;

    const chat = document.getElementById("chat");

    chat.innerHTML +=
        '<div class="message"><b>Tú:</b> ' +
        message +
        '</div>';

    input.value = "";

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: message
            })
        });

        const data = await response.json();

        chat.innerHTML +=
            '<div class="message"><b>JARVIS:</b> ' +
            (data.response || data.error) +
            '</div>';

    } catch (error) {
        chat.innerHTML +=
            '<div class="message"><b>JARVIS:</b> Error de conexión.</div>';
    }
}
</script>

</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML)


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message", "")

    if not message:
        return jsonify({"error": "No se recibió ningún mensaje"}), 400

    try:
        response = client.responses.create(
            model="openrouter/free",
            input=message
        )

        return jsonify({
            "response": response.output_text
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
