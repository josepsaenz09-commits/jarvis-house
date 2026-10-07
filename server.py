import os
from flask import Flask, request, jsonify
from openai import OpenAI
import anthropic

app = Flask(__name__)

openai_client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)

anthropic_client = anthropic.Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY")
)

@app.route("/")
def home():
    return "JARVIS está en línea."

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message", "")

    if not message:
        return jsonify({"error": "No se recibió ningún mensaje"}), 400

    try:
        response = openai_client.responses.create(
            model="gpt-5",
            input=message
        )

        answer = response.output_text

        return jsonify({
            "response": answer
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
