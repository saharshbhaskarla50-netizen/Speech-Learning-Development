import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_speech(audio_file_path, duration_seconds):
    
    # Step 1: Transcribe with Whisper
    with open(audio_file_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    
    text = transcript.text
    print(f"Transcript: {text}")

    # Step 2: Detect filler words
    filler_words = ["um", "uh", "like", "you know", "so", "basically"]
    filler_count = 0
    for word in filler_words:
        count = text.lower().count(word)
        filler_count += count


    
    print(f"Filler words: {filler_count}")

    # Step 3: Calculate WPM
    word_count = len(text.split())
    minutes = duration_seconds / 60
    wpm = round(word_count / minutes)
    print(f"WPM: {wpm}")

    # Step 4: Get GPT feedback
    feedback = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": f"You are a public speaking coach. Analyze this transcript and give 3 short specific tips: '{text}'"
        }]
    )
    
    tips = feedback.choices[0].message.content
    print(f"Feedback: {tips}")

    # Step 5: Calculate score
    score = 100
    score -= filler_count * 3
    if wpm > 160:
        score -= 10
    if wpm < 100:
        score -= 10
    score = max(0, score)
    print(f"Score: {score}")

    return {
        "transcript": text,
        "filler_count": filler_count,
        "wpm": wpm,
        "score": score,
        "feedback": tips
    }

# Test it with a sample audio file
if __name__ == "__main__":
    result = analyze_speech("test.m4a", 60)
    print(result)