import os
import re
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def count_fillers(text):
    filler_patterns = [
        r'\bum+\b', r'\buh+\b', r'\blike\b',
        r'\byou know\b', r'\bso\b', r'\bbasically\b',
        r'\bkind of\b', r'\bsort of\b', r'\bright\b',
        r'\bliterally\b', r'\bactually\b'
    ]
    filler_count = 0
    for pattern in filler_patterns:
        matches = re.findall(pattern, text.lower())
        filler_count += len(matches)
    return filler_count

def detect_confidence(text):
    confidence_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": f"""You are an expert public speaking coach analyzing confidence levels.

Analyze this speech transcript and rate the speaker's confidence:

Transcript: '{text}'

Look for:
- Weak phrases like "I think maybe", "I'm not sure but", "kind of", "sort of"
- Strong phrases like "I know", "I believe", "clearly", "definitely"
- Hesitation patterns
- Assertiveness of language

Respond in exactly this format:
Confidence Score: X/10
Strength: [one thing that showed confidence]
Weakness: [one thing that showed lack of confidence]
Tip: [one specific tip to sound more confident]"""
        }]
    )
    return confidence_response.choices[0].message.content

def calculate_score(filler_count, wpm, word_count):
    score = 100
    score -= filler_count * 3
    if wpm > 160:
        score -= 10
    if wpm < 100:
        score -= 10
    if word_count < 50:
        score -= 15
    if 120 <= wpm <= 150:
        score += 5
    return max(0, min(100, score))

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
    filler_count = count_fillers(text)
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
            "content": f"""You are an expert public speaking coach for students.

Analyze this speech transcript and provide:
1. Three specific improvement tips
2. One thing they did well
3. A confidence rating out of 10
4. One drill they can practice today

Transcript: '{text}'
Word count: {word_count}
WPM: {wpm}
Filler words detected: {filler_count}

Be encouraging but honest. Keep each tip under 2 sentences."""
        }]
    )

    tips = feedback.choices[0].message.content
    print(f"Feedback: {tips}")

    # Step 5: Confidence detection
    confidence = detect_confidence(text)
    print(f"\nConfidence Analysis:\n{confidence}")

    # Step 6: Calculate score
    score = calculate_score(filler_count, wpm, word_count)
    print(f"Score: {score}")

    return {
        "transcript": text,
        "filler_count": filler_count,
        "wpm": wpm,
        "score": score,
        "feedback": tips,
        "confidence": confidence
    }

def chat_with_coach(transcript, analysis_result, conversation_history, user_message):

    if not conversation_history:
        conversation_history = [{
            "role": "system",
            "content": f"""You are an expert AI public speaking coach.
You just analyzed a student's speech. Here are the results:

Transcript: {transcript}
Score: {analysis_result['score']}/100
Filler words: {analysis_result['filler_count']}
WPM: {analysis_result['wpm']}
Confidence: {analysis_result['confidence']}

Answer their questions about their speech and give
personalized coaching advice. Be encouraging and specific."""
        }]

    conversation_history.append({
        "role": "user",
        "content": user_message
    })

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=conversation_history
    )

    ai_message = response.choices[0].message.content

    conversation_history.append({
        "role": "assistant",
        "content": ai_message
    })

    return ai_message, conversation_history

# ---- TEST EVERYTHING ----

# Test analysis
result = analyze_speech("test.mp3", 60)
print(result)

# Test conversation
print("\n---- AI COACH CONVERSATION ----")
conversation_history = []

questions = [
    "How can I reduce my filler words?",
    "What exercises can I do to speak slower?",
    "How long until I see improvement?"
]

for question in questions:
    print(f"\nYou: {question}")
    response, conversation_history = chat_with_coach(
        result['transcript'],
        result,
        conversation_history,
        question
    )
    print(f"Coach: {response}")