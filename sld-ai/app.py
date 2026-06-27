from flask import Flask, request, jsonify
from analyze import analyze_speech, chat_with_coach
import os

app = Flask(__name__)

@app.route("/analyze", methods=["POST"])
def analyze():
    audio_file = request.files["audio"]
    duration = float(request.form["duration"])
   
    # Save the audio file temporarily
    ext = os.path.splitext(audio_file.filename)[1]
    audio_path = f"/tmp/temp_audio{ext}"
    audio_file.save(audio_path)
   
    # Run the analysis
    result = analyze_speech(audio_path, duration)
   
    # Delete temp file
    os.remove(audio_path)
   
    return jsonify(result)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    
    user_message = data.get("message")
    conversation_history = data.get("history", [])
    analysis_result = data.get("analysis")
    transcript = analysis_result.get("transcript", "")

    response, updated_history = chat_with_coach(
        transcript,
        analysis_result,
        conversation_history,
        user_message
    )

    return jsonify({
        "response": response,
        "history": updated_history
    })

if __name__ == "__main__":
    app.run(debug=True)