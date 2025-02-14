import pytest
from agents.sanitizer import clean_text

@pytest.mark.asyncio
async def test_clean_text():
    # Test input data
    test_data = {
        "title": "Test [Post] with http://example.com URLs",
        "selftext": "Some &amp; special characters &lt; here &gt;",
        "author": "test_user",
        "subreddit": "test_sub",
        "comments": [
            {
                "body": "A comment with [markdown](http://test.com)",
                "author": "commenter1",
                "score": 10
            },
            {
                "body": "A downvoted comment!!!!!!",
                "author": "commenter2",
                "score": -5
            }
        ]
    }
    
    # Expected output
    expected_title = "test post with urls"
    expected_main_text = "some special characters here"
    
    # Run the function
    result = await clean_text(test_data)
    
    # Assertions
    assert result["title"] == expected_title
    assert result["main_text"] == expected_main_text
    assert len(result["comments"]) == 1  # Only positive score comments
    assert result["comments"][0]["text"] == "a comment with markdown"
    assert result["author"] == "test_user"
    assert result["subreddit"] == "test_sub"

@pytest.mark.asyncio
async def test_clean_text_empty_input():
    # Test with empty input
    test_data = {
        "title": "",
        "selftext": "",
        "author": "test_user",
        "subreddit": "test_sub",
        "comments": []
    }
    
    result = await clean_text(test_data)
    
    assert result["title"] == ""
    assert result["main_text"] == ""
    assert len(result["comments"]) == 0

@pytest.mark.asyncio
async def test_clean_text_special_characters():
    # Test with various special characters
    test_data = {
        "title": "!@#$%^&*()_+ Test Title",
        "selftext": "Text with\nmultiple\nlines and     spaces",
        "author": "test_user",
        "subreddit": "test_sub",
        "comments": []
    }
    
    result = await clean_text(test_data)
    
    assert result["title"] == "test title"
    assert result["main_text"] == "text with multiple lines and spaces"
