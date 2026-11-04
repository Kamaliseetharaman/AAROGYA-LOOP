
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

HEALTHCARE_PROMPT = """
You are Aarogya AI, a friendly personal healthcare
support assistant.

Your responsibilities:
- Communicate in simple Tamil and English.
- Explain general health information.
- Help users understand medicine reminders.
- Give supportive and easy-to-understand answers.
- Be polite and patient.

Safety:
- Never diagnose diseases.
- Never prescribe or change medication doses.
- Never tell users to stop prescribed medication.
- Never invent patient records or medicine history.
- For medical decisions, recommend consulting a qualified
  healthcare professional.
- For emergencies, advise seeking immediate medical help.
- Clearly explain that you are an AI assistant, not a doctor.
"""

@app.route("/")
def home():
    return jsonify({
        "message": "Aarogya AI is running!"
    })

@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json(silent=True) or {}
        messages = data.get("messages", [])

        if not isinstance(messages, list) or not messages:
            return jsonify({"error": "Message is required"}), 400

        if len(messages) > 20:
            return jsonify({"error": "Conversation is too long"}), 400

        for message in messages:
            if (
                not isinstance(message, dict)
                or message.get("role") not in ["user", "assistant"]
                or not isinstance(message.get("content"), str)
                or not message["content"].strip()
                or len(message["content"]) > 4000
            ):
                return jsonify({"error": "Invalid message"}), 400

        response = client.responses.create(
            model="gpt-5.5",
            instructions=HEALTHCARE_PROMPT,
            input=messages
        )

        return jsonify({
            "reply": response.output_text
        })

    except Exception:
        app.logger.exception("Aarogya AI request failed")
        return jsonify({
            "error": "Aarogya AI is temporarily unavailable."
        }), 500


if __name__ == "__main__":
    app.run(debug=False, port=5000)
