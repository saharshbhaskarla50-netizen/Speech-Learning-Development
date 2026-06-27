# Speech and Leadership Development (SLD)

SLD is an AI-powered public speaking coach that records your speech, 
analyzes it in real time, and delivers personalized coaching feedback 
on pacing, filler words, and delivery.

Quality public speaking coaching costs hundreds of dollars per session 
and is inaccessible to most people. SLD makes that feedback free and 
available to anyone.

## How It Works

1. User records a speech session
2. OpenAI Whisper transcribes the audio
3. SLD detects filler words (um, uh, like, you know) and measures WPM
4. GPT-4o mini generates personalized coaching feedback on pacing and delivery
5. Results are displayed on a dashboard so users can track progress over time

## Stack

- Frontend: Next.js
- Backend: Next.js API routes
- AI: OpenAI Whisper + GPT-4o mini
- Database: Supabase
- Hosting: Vercel

## Getting Started

Clone the repo and install dependencies:

git clone https://github.com/[your-repo]
cd sld
npm install

Add a .env file:

OPENAI_API_KEY=your_key
SUPABASE_URL=your_url
SUPABASE_ANON_KEY=your_key

Run locally:

npm run dev

## Team

- CEO: Aaditya Bhagat
- CTO: Saharsh Bhaskarla
- CPO: Sahan Phadnis
- Head of AI: Sparsh Pal
- Lead Web Architect: Darsh Patel
- Head of Marketing: Sahil Mathur
- Head of Data & Analytics: Raghav Rao
- Chief R&D: Sankeerth Malasandram
