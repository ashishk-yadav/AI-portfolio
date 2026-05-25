# pip install newspaper3k lxml_html_clean
"""
An RSS feed (Really Simple Syndication) is a type of web feed that allows users and applications to receive updates
to websites in a standardized, computer-readable format.

Here’s a breakdown of how it works:

Publishers (like blogs, news sites, or podcasts) create an RSS feed — an XML file containing summaries or full content of their latest updates.

Users subscribe to that feed using an RSS reader (such as Feedly, Inoreader, or an email client).

The reader periodically checks the feed and shows new content, so users can stay updated without visiting each site individually.

Example Use Case:
You follow 10 blogs. Instead of visiting each site daily, you subscribe to their RSS feeds in one app. That app aggregates all new posts in one place.

Would you like to see an example of what an RSS feed file looks like?

"""
import newspaper
import feedparser
import openai

import data_info
import certifi
import os
os.environ['SSL_CERT_FILE'] = certifi.where()
from openai import OpenAI
import os

from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") # Replace this with your open ai key "SK-"

openai.api_key = OPENAI_API_KEY

def scrape_news_from_feed(feed_url):
    articles = []
    feed = feedparser.parse(feed_url)
    for entry in feed.entries:
        # create a newspaper article object
        article = newspaper.Article(entry.link)
        # download and parse the article
        article.download()
        article.parse()
        # extract relevant information
        articles.append({
            'title': article.title,
            'author': article.authors,
            'publish_date': article.publish_date,
            'content': article.text
        })
    return articles


feed_url = 'http://feeds.bbci.co.uk/news/rss.xml'
articles = scrape_news_from_feed(feed_url)
print(articles)
# print the extracted articles
for article in articles[0:5]:
    print('Title:', article['title'])
    print('Author:', article['author'])
    print('Publish Date:', article['publish_date'])
    print('Content:', article['content'])

    #Analyze sentiment
    analyze_sentiment_prompt = f"""
    Analyze the sentiment as positive, negative or neutral of this news article. 
     
     News Article: {article['content']}
    
    """
    client = OpenAI(api_key=data_info.open_ai_key)
    response = client.responses.create(
        model="gpt-4o-mini",
        input=analyze_sentiment_prompt,
        temperature=0,
    )

    print(response.output_text)
    # named entity recognition ( Company names )
    # Analyze sentiment
    entity_recognition_prompt = f"""
    Analyze this news article and identify company names. 

     News Article: {article['content']}

    """
    client = OpenAI(api_key=data_info.open_ai_key)
    response = client.responses.create(
        model="gpt-4o-mini",
        input=entity_recognition_prompt,
        temperature=0,
    )
    print(response.output_text)
