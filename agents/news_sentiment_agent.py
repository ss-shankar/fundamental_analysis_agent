import os

import json
import logging
from urllib.error import URLError, HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from datetime import datetime, timedelta, timezone
"""
API's Used: 
search_recent_news : newsapi.org (Obtain recent news articles based on a query)-> Returns a list of news articles
-> Scrape the content of the articles and analyze the sentiment using AWS Bedrock's foundation models.
analyze_sentiment : AWS Bedrock (Analyze the sentiment of a given text)-> Returns the sentiment of the text.
"""

def search_recent_news(query: str, api_key: str) -> list[dict]:
    """
    Search for recent news articles based on a query using the NewsAPI.

    Args:
        query (str): The search query.
        api_key (str): Your NewsAPI API key.

    Returns:
        list[dict]: A list of news articles, each represented as a dictionary.
    """
    params = {
        "q": query,
        "sortBy": "publishedAt",
        "language": "en",
        "apiKey": api_key
    }

    try:
        url = "https://newsapi.org/v2/everything?" + urlencode(params)
        with urlopen(url) as response:
            data = json.loads(response.read().decode("utf-8"))
        article_urls = [article["url"] for article in data.get("articles", [])]
        return article_urls
    except (HTTPError, URLError, json.JSONDecodeError) as e:
        logging.error(f"Error fetching news articles: {e}")
        return []

def scrape_article_content(urls: list[str]) -> str:
    """
    Scrape the content of a news article from its URL.

    Args:
        urls (list[str]): A list of URLs of the news articles.

    Returns:
        str: The content of the news article.
    """ 
    content = []
    for url in urls:    
        try:
            request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urlopen(request) as response:
                article_content = response.read().decode("utf-8", errors="replace")
            # For simplicity, we return the raw HTML content. In a real application, you would parse the HTML to extract the main text.
            content.append(article_content)
        except (HTTPError, URLError) as e:
            logging.error(f"Error scraping article content from {url}: {e}")
            return ""
    
    return "\n".join(content)

def analyze_sentiment(text: str, model_id: str = "amazon.titan-llm") -> dict:
    """
    Analyze the sentiment of a given text using LLMs

    Args:
        text (text): The text to analyze (HTML content of the news articles).
        model_id (str): The ID of the foundation model to use for sentiment analysis.

    Returns:
        dict: A dictionary containing the sentiment analysis results.
    """
    # Initialize the Bedrock client
    import boto3
    client = boto3.client("bedrock", region_name=os.getenv("AWS_REGION", "us-east-1"))

    try:
        response = client.invoke_model(
            modelId=model_id,
            body=json.dumps({"text": text}),
            contentType="application/json"
        )
        result = json.loads(response["body"].read())
        return result
    except Exception as e:
        logging.error(f"Error analyzing sentiment: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    # Example usage
    NEWS_API_KEY = os.getenv("NEWS_API_KEY", "6ce8dd0674ff49c296400574b7a529ccs")
    query = "OpenAI"
    
    # Step 1: Search for recent news articles
    article_urls = search_recent_news(query, "2bq2TqPW1D3d8r1g7Iw928eABymuiOV4")
    if not article_urls:
        logging.info("No articles found.")
    else:
        logging.info(f"Found {len(article_urls)} articles.")

        # Step 2: Scrape the content of the articles
        article_content = scrape_article_content(article_urls)
        if not article_content:
            logging.info("No content scraped from articles.")
        else:
            logging.info("Scraped article content successfully.")

            # Step 3: Analyze the sentiment of the scraped content
            sentiment_result = analyze_sentiment(article_content)
            logging.info(f"Sentiment analysis result: {sentiment_result}")