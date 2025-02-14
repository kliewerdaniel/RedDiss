import asyncpraw
from typing import Dict, Any
import os
import re
from dotenv import load_dotenv
import asyncio
import json
from pathlib import Path
from fastapi import HTTPException

# Load environment variables
load_dotenv()

class RedditScraper:
    def __init__(self):
        # Check if environment variables are set
        client_id = os.getenv("REDDIT_CLIENT_ID")
        client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        user_agent = os.getenv("REDDIT_USER_AGENT")
        
        if not all([client_id, client_secret, user_agent]):
            missing_vars = [var for var, val in {
                "REDDIT_CLIENT_ID": client_id,
                "REDDIT_CLIENT_SECRET": client_secret,
                "REDDIT_USER_AGENT": user_agent
            }.items() if not val]
            raise HTTPException(
                status_code=500,
                detail=f"Missing required environment variables: {', '.join(missing_vars)}"
            )
            
        print(f"Initializing Reddit client with user agent: {user_agent}")
        self.reddit = asyncpraw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        
    async def extract_post_data(self, url: str) -> Dict[str, Any]:
        """Extract data from a Reddit post URL"""
        try:
            print(f"Attempting to fetch submission from URL: {url}")
            submission = await self.reddit.submission(url=url)
            
            print("Loading submission data...")
            await submission.load()
            print(f"Successfully loaded submission: {submission.title}")
            
            # Get author and subreddit info
            author_name = "[deleted]"
            subreddit_name = ""
            
            try:
                if submission.author:
                    await submission.author.load()
                    author_name = submission.author.name
            except Exception as e:
                print(f"Error loading author: {str(e)}")
                
            try:
                if submission.subreddit:
                    await submission.subreddit.load()
                    subreddit_name = submission.subreddit.display_name
            except Exception as e:
                print(f"Error loading subreddit: {str(e)}")
            
            data = {
                "title": submission.title,
                "selftext": submission.selftext,
                "author": author_name,
                "subreddit": subreddit_name,
                "score": submission.score,
                "comments": []
            }
            
            # Load comments
            try:
                await submission.comments.replace_more(limit=None)
                comments = await submission.comments.list()
                for comment in comments:
                    comment_author = "[deleted]"
                    try:
                        if comment.author:
                            await comment.author.load()
                            comment_author = comment.author.name
                    except Exception as e:
                        print(f"Error loading comment author: {str(e)}")
                    
                    data["comments"].append({
                        "body": comment.body,
                        "author": comment_author,
                        "score": comment.score
                    })
            except Exception as e:
                print(f"Error loading comments: {str(e)}")
                # Continue without comments if they fail to load
            
            # Save raw data for debugging
            Path("data/raw").mkdir(parents=True, exist_ok=True)
            safe_id = re.sub(r'[^a-zA-Z0-9_-]', '_', str(submission.id))
            with open(f"data/raw/{safe_id}.json", "w") as f:
                json.dump(data, f, indent=2)
                
            return data
            
        except asyncpraw.exceptions.InvalidURL:
            print("Error: Invalid Reddit URL provided")
            raise HTTPException(status_code=400, detail="Invalid Reddit URL provided")
        except asyncpraw.exceptions.ClientException as e:
            print(f"Reddit API client error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Reddit API client error: {str(e)}")
        except asyncpraw.exceptions.PRAWException as e:
            print(f"Reddit API error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Reddit API error: {str(e)}")
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    
    async def _pushshift_fallback(self, url: str) -> Dict[str, Any]:
        """Fallback to Pushshift API if Reddit API fails"""
        # TODO: Implement Pushshift fallback
        raise NotImplementedError("Pushshift fallback not implemented yet")

async def scrape_reddit(url: str) -> Dict[str, Any]:
    """Main function to scrape Reddit content"""
    scraper = RedditScraper()
    try:
        return await scraper.extract_post_data(url)
    finally:
        await scraper.reddit.close()
