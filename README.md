# AI-Powered Diss Track Generator

An AI system that generates diss tracks from Reddit posts using SmolAgents and various AI models.

## Features

- Reddit post/comment scraping
- NLP preprocessing and theme extraction
- AI-powered lyrics generation using DeepSeek-R1 32B
- Flow and punchline refinement
- Text-to-Speech using Bark TTS
- Beat synchronization with Librosa
- Audio mastering and processing

## Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file with your API keys:
```
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=your_user_agent
```

## Usage

Run the FastAPI server:
```bash
uvicorn main:app --reload
```

Generate a diss track:
```bash
curl "http://localhost:8000/generate_diss?url=https://reddit.com/r/..."
```

## Project Structure

- `agents/`: AI Agents for modular processing
- `data/`: Stores scraped data & generated lyrics
- `models/`: Pre-trained model storage
- `tests/`: Unit tests for each module
- `main.py`: FastAPI server
