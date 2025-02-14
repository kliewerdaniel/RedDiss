RedDiss: AI-Powered Diss Track Generator

A Streamlit app that crafts diss tracks from Reddit posts using AI-powered text analysis, lyrics generation, and text-to-speech synthesis.

Features
	•	Reddit Integration: Scrapes posts and comments from Reddit for analysis.
	•	Natural Language Processing (NLP): Extracts themes and sentiments from the text.
	•	Lyrics Generation: Uses Llama 3.3 to generate diss track lyrics.
	•	Flow & Punchline Enhancement: Refines lyrics for impactful delivery.
	•	Text-to-Speech (TTS): Converts lyrics into vocal audio using Bark TTS.
	•	Beat Synchronization: Aligns vocals with beats using Librosa.
	•	Audio Mastering: Applies final processing for a polished diss track.

Installation & Setup

1. Clone the Repository

git clone https://github.com/kliewerdaniel/RedDiss.git
cd RedDiss

2. Install Dependencies

pip install -r requirements.txt

3. Set Up Environment Variables

Create a .env file in the root directory and add your Reddit API credentials:

REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=your_user_agent

Usage

1. Run the Streamlit App

streamlit run streamlit_app.py

2. Generate a Diss Track
	•	Enter a Reddit post URL in the input field.
	•	Click “Generate Diss Track” to process the text and create lyrics.
	•	Listen to the AI-generated diss track directly in the app.
