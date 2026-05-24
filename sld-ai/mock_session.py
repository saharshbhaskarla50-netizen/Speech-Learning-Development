import os
import re
import sounddevice as sd
import soundfile as sf
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SCENARIOS = {
    "1": {
        "name": "Job Interview",
        "context": "You are a professional job interviewer at a top tech company. Ask the candidate interview questions one at a time. Start by welcoming them and asking them to introduce themselves.",
        "opener": "Welcome! Thanks for coming in today. To get started, could you tell me a little about yourself and why you're interested in this position?"
    },
    "2": {
        "name": "Investor Pitch",
        "context": "You are a skeptical venture capitalist. The candidate is pitching their startup to you. Ask tough but fair questions. Start by asking them to pitch their idea.",
        "opener": "Alright, you've got 5 minutes. Tell me about your startup — what problem are you solving and why should I care?"
    },
    "3": {
        "name": "Class Presentation",
        "context": "You are a teacher evaluating a student's presentation. Ask follow up questions about their topic. Start by asking them to begin their presentation.",
        "opener": "Okay class, we're ready for your presentation. Go ahead and begin whenever you're ready."
    },
    "4": {
        "name": "Debate Practice",
        "context": "You are a debate opponent. Challenge the user's arguments respectfully but firmly. Start by stating an opening argument they must respond to.",
        "opener": "I'll open the debate: Social media has done more harm than good to our generation. I'd like to hear your response."
    },
    "5": {
        "name": "Public Speech",
        "context": "You are an audience member at a public speaking event. React naturally to what the speaker says and ask questions. Start by welcoming the speaker.",
        "opener": "Welcome to the stage! We're excited to hear from you today. Please go ahead and begin your speech."
    }
}

def record_audio(duration=10, sample_rate=44100):
    print(f"\n🎙️  Recording for {duration} seconds... Speak now!")
    audio_data = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype=np.float32
    )
    sd.wait()
    print("✅ Done recording!")
    
    filename = "response.wav"
    sf.write(filename, audio_data, sample_rate)
    return filename

def transcribe_audio(audio_path):
    with open(audio_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    return transcript.text

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

def get_ai_response(scenario_context, conversation_history, user_message):
    conversation_history.append({
        "role": "user",
        "content": user_message
    })

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "system",
            "content": scenario_context
        }] + conversation_history
    )

    ai_message = response.choices[0].message.content
    conversation_history.append({
        "role": "assistant",
        "content": ai_message
    })

    return ai_message, conversation_history

def get_turn_feedback(text, filler_count, wpm):
    feedback_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": f"""You are a public speaking coach giving quick feedback on one response in a mock session.
            
Transcript: '{text}'
Filler words: {filler_count}
WPM: {wpm}

Give exactly 2 lines of feedback:
1. One thing they did well
2. One quick thing to improve

Keep it very short and encouraging."""
        }]
    )
    return feedback_response.choices[0].message.content

def run_mock_session():
    print("\n" + "="*50)
    print("🎤  SLD MOCK PRACTICE SESSION")
    print("="*50)
    print("\nChoose a scenario:")
    for key, scenario in SCENARIOS.items():
        print(f"  {key}. {scenario['name']}")

    choice = input("\nEnter number (1-5): ").strip()
    if choice not in SCENARIOS:
        print("Invalid choice. Defaulting to Job Interview.")
        choice = "1"

    scenario = SCENARIOS[choice]
    print(f"\n✅ Starting: {scenario['name']}")
    print("\n" + "-"*50)

    # How long each response should be
    record_duration = int(input("How many seconds per response? (recommended: 20-30): ").strip())

    conversation_history = []
    turn = 1
    total_fillers = 0
    total_wpm = []
    total_score = 0

    # AI opens the conversation
    print(f"\n🤖 AI: {scenario['opener']}\n")
    conversation_history.append({
        "role": "assistant",
        "content": scenario['opener']
    })

    while True:
        print(f"\n--- Turn {turn} ---")
        print("Press ENTER when ready to record (or type 'quit' to end session)")
        user_input = input().strip().lower()

        if user_input == "quit":
            break

        # Record user response
        audio_path = record_audio(duration=record_duration)

        # Transcribe
        print("⏳ Transcribing...")
        text = transcribe_audio(audio_path)
        print(f"\n📝 You said: {text}")

        # Analyze response
        filler_count = count_fillers(text)
        word_count = len(text.split())
        wpm = round(word_count / (record_duration / 60))
        
        # Score this turn
        score = 100
        score -= filler_count * 3
        if wpm > 160: score -= 10
        if wpm < 100: score -= 10
        score = max(0, score)

        total_fillers += filler_count
        total_wpm.append(wpm)
        total_score += score

        # Quick feedback
        print("\n💡 Quick Feedback:")
        feedback = get_turn_feedback(text, filler_count, wpm)
        print(feedback)
        print(f"📊 This turn: Fillers: {filler_count} | WPM: {wpm} | Score: {score}/100")

        # AI responds in character
        print("\n⏳ AI is responding...")
        ai_response, conversation_history = get_ai_response(
            scenario['context'],
            conversation_history,
            text
        )
        print(f"\n🤖 AI: {ai_response}")

        turn += 1

        # Ask to continue
        print("\nContinue? (press ENTER) or type 'quit' to see final results")
        cont = input().strip().lower()
        if cont == "quit":
            break

    # Final results
    print("\n" + "="*50)
    print("📊 SESSION COMPLETE — FINAL RESULTS")
    print("="*50)
    print(f"Turns completed: {turn - 1}")
    print(f"Total filler words: {total_fillers}")
    print(f"Average WPM: {round(sum(total_wpm) / len(total_wpm)) if total_wpm else 0}")
    print(f"Average Score: {round(total_score / (turn - 1)) if turn > 1 else 0}/100")

    # Final AI coaching summary
    print("\n⏳ Generating final coaching summary...")
    summary = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": f"""You are a public speaking coach. 
The student just completed a mock {scenario['name']} session with {turn-1} turns.

Stats:
- Total filler words: {total_fillers}
- Average WPM: {round(sum(total_wpm)/len(total_wpm)) if total_wpm else 0}
- Average score: {round(total_score/(turn-1)) if turn > 1 else 0}/100

Give a short encouraging summary with:
1. Overall performance assessment
2. Their biggest strength
3. Their biggest area to improve
4. One specific drill to practice before next session"""
        }]
    )
    print("\n🏆 Coach Summary:")
    print(summary.choices[0].message.content)
    print("\n" + "="*50)

# Run it
run_mock_session()