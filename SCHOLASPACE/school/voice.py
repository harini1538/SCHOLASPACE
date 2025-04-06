from flask import Flask, render_template, request, jsonify, send_from_directory, Blueprint
from groq import Groq
from gtts import gTTS
import uuid
import os

voice_bp = Blueprint('voice', __name__, template_folder='templates')

# Groq API key setup
client = Groq(api_key="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")

# Ensure static/audio/ directory exists
AUDIO_FOLDER = os.path.join('static', 'audio')
os.makedirs(AUDIO_FOLDER, exist_ok=True)

# Route to render teacher bot UI
@voice_bp.route('/teacher_bot')
def teacher_bot_home():
    return render_template('teacher_bot.html')

# Endpoint to handle question and give audio + text reply
@voice_bp.route('/ask_teacher', methods=['POST'])
def ask_teacher():
    user_input = request.json['question']

    # LLM response from GROQ
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": user_input}],
        model="llama3-8b-8192",
    )

    response = chat_completion.choices[0].message.content
    limited_response = ' '.join(response.split()[:50])  # Limit to 50 words

    # Convert to audio
    tts = gTTS(text=limited_response)
    audio_filename = f"audio_{uuid.uuid4()}.mp3"
    audio_path = os.path.join(AUDIO_FOLDER, audio_filename)
    tts.save(audio_path)

    return jsonify({'response': limited_response, 'audio': audio_filename})

@voice_bp.route('/play_audio/<filename>')
def play_audio(filename):
    return send_from_directory(AUDIO_FOLDER, filename)


