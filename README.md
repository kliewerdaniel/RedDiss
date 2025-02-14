RedDiss

An AI-powered system that crafts diss tracks from Reddit posts by leveraging SmolAgents and various AI models.

Features
	•	Reddit Integration: Seamlessly scrapes posts and comments from Reddit for analysis.
	•	Natural Language Processing (NLP): Processes text to extract themes and sentiments.
	•	Lyrics Generation: Utilizes the DeepSeek-R1 32B model to generate compelling diss track lyrics.
	•	Flow and Punchline Enhancement: Refines lyrics to ensure impactful delivery.
	•	Text-to-Speech Conversion: Employs Bark TTS to transform text lyrics into vocal audio.
	•	Beat Synchronization: Aligns vocals with beats using Librosa for a cohesive track.
	•	Audio Mastering: Finalizes the track with professional audio processing techniques.

Setup
	1.	Clone the Repository:

git clone https://github.com/kliewerdaniel/RedDiss.git
cd RedDiss


	2.	Install Dependencies:

pip install -r requirements.txt


	3.	Configure Environment Variables:
	•	Create a .env file in the root directory with the following content:

REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=your_user_agent


	•	Replace your_client_id, your_client_secret, and your_user_agent with your actual Reddit API credentials.

Usage
	1.	Start the FastAPI Server:

uvicorn main:app --reload


	2.	Generate a Diss Track:
	•	Send a GET request to the server with the Reddit post URL:

curl "http://localhost:8001/generate_diss?url=https://reddit.com/r/..."


	•	Replace https://reddit.com/r/... with the specific Reddit post URL you want to use.

Project Structure
	•	agents/: Contains AI agents responsible for different processing tasks.
	•	data/: Stores scraped Reddit data and generated lyrics.
	•	models/: Houses pre-trained models utilized in the project.
	•	tests/: Includes unit tests for various modules to ensure code reliability.
	•	main.py: The entry point for the FastAPI server handling API requests.

Workflow Overview
	1.	Data Collection:
	•	The system scrapes the specified Reddit post to gather content for analysis.
	2.	Text Analysis:
	•	NLP techniques are applied to extract themes, sentiments, and key phrases from the Reddit content.
	3.	Lyrics Generation:
	•	Based on the analysis, the DeepSeek-R1 32B model generates diss track lyrics tailored to the extracted themes.
	4.	Lyrics Refinement:
	•	The generated lyrics undergo refinement to enhance flow, coherence, and the impact of punchlines.
	5.	Audio Synthesis:
	•	The refined lyrics are converted into speech using Bark TTS.
	•	Vocals are synchronized with selected beats using Librosa to produce the final diss track.

