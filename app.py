from flask import Flask, request, jsonify
from analyze import analyze_speech
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/analyze", methods=["POST"])
def analyze():
    audio_file = request.files["audio"]
    duration = float(request.form["duration"])
   
    # Save the audio file temporarily
    ext = os.path.splitext(audio_file.filename)[1]
    audio_path = f"temp_audio{ext}"
    audio_file.save(audio_path)
   
    # Run the analysis
    result = analyze_speech(audio_path, duration)
   
    # Delete temp file
    os.remove(audio_path)
   
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
