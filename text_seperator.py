import spacy
import re
from textwrap import wrap
from langdetect import detect


# Load spaCy models for different languages
nlp_models = {
    'en': spacy.load("en_core_web_sm"),
    'de': spacy.load("de_core_news_sm"),
    'fr': spacy.load("fr_core_news_sm")
}

# Split text into sentences using spacy with language detection
def split_into_sentences(text):
    try:
        # Detect the language of the text
        lang = detect(text)
        # Map detected language to available models
        lang_map = {'en': 'en', 'de': 'de', 'fr': 'fr'}
        # Default to English if language not supported
        model_lang = lang_map.get(lang, 'en')
        nlp = nlp_models[model_lang]
        doc = nlp(text)
        return [str(sent) for sent in doc.sents]

    except Exception as e:
        print(f"Error: {e}")
        return []

# Split text into chunks of max length, preserving sentence boundaries
    
def split_into_chunks(text, max_length=300):
    sentences = split_into_sentences(text)
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 1 <= max_length:
            current_chunk += sentence + " "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + " "
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

# Format chunks into a Bluesky thread with markers (e.g., 1/3, 2/3)
def format_thread(chunks):
    formatted_thread = []
    total_posts = len(chunks)
    for i, chunk in enumerate(chunks, start=1):
        formatted_thread.append(f"{i}/{total_posts} {chunk}")
    return formatted_thread

# Process a tweet into Bluesky-compatiable chunks
def process_tweet(tweet):
    
    # Check tweet length
    if len(tweet) <= 300:
        return [tweet]

    # Split into chunks
    chunks = split_into_chunks(tweet)

    # Format into a Bluesky thread
    return format_thread(chunks)

# Example Usage
tweet_text = """
🌟 Exciting news! We're launching a new feature today. This update includes advanced text splitting to preserve context. Stay tuned for details. #TechUpdate 
The tool uses NLP to detect natural breaks, ensuring your message isn't fragmented. Check the blog: https://example.com/blog 
Thanks to our community for feedback! 🙌 Let us know your thoughts. 👇
"""

bluesky_thread = process_tweet(tweet_text)
for post in bluesky_thread:
    print(post)
    print("-" * 50)  # Separator for readability