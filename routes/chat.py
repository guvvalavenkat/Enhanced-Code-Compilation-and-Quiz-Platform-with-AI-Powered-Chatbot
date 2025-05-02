
from flask import Blueprint, request, jsonify, render_template
import requests
import re

chat = Blueprint('chat', __name__)
GEMINI_API_KEY = "AIzaSyC5Xf81pJlSNx2_IoHXR5U34HUEvqssfzs"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

@chat.route('/chat', methods=['GET'])
def chat_page():
    return render_template('chat.html')

@chat.route('/chat', methods=['POST'])
def ai_chat():
    user_msg = request.json.get('message')

    # Refined condition to apply MCQ formatting only on explicit quiz-type requests
    if any(x in user_msg.lower() for x in ["mcq", "multiple choice", "quiz", "4 options", "objective"]):
        user_msg = (
            f"Generate {user_msg}. "
            "Return each question and its 4 options (a–d) clearly and separately, in plain text format. "
            "Add a newline between each line for readability."
        )

    try:
        response = requests.post(
            GEMINI_API_URL,
            json={
                "contents": [
                    {
                        "parts": [{"text": user_msg}]
                    }
                ]
            }
        )
        data = response.json()

        if "candidates" in data and data["candidates"]:
            reply = data["candidates"][0]["content"]["parts"][0]["text"]
            formatted_reply = re.sub(r"(\d+\.\s)", r"\n\1", reply)
            formatted_reply = re.sub(r"([a-dA-D]\.)", r"\n\1", formatted_reply)
            formatted_reply = formatted_reply.strip()
        else:
            formatted_reply = "⚠️ Gemini returned no valid content. Raw response: " + str(data)

        return jsonify({"reply": formatted_reply})
    except Exception as e:
        return jsonify({"reply": "Error: " + str(e)})
