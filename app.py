from flask import Flask, request, jsonify
from analyze import analyze_speech, chat_with_coach
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/analyze", methods=["POST"])
def analyze():
    audio_file = request.files["audio"]
    duration = float(request.form["duration"])
   
    # Save the audio file temporarily
    ext = os.path.splitext(audio_file.filename)[1] or ".webm"
    audio_path = f"temp_audio{ext}"
    audio_file.save(audio_path)
   
    # Run the analysis
    result = analyze_speech(audio_path, duration)
   
    # Delete temp file
    os.remove(audio_path)
   
    return jsonify(result)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data["message"]
    history = data.get("history", [])
    analysis = data["analysis"]

    response, updated_history = chat_with_coach(
        analysis["transcript"],
        analysis,
        history,
        message
    )

    return jsonify({"response": response, "history": updated_history})

if __name__ == "__main__":
    app.run(debug=True)
