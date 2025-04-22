import spacy
import re
from textwrap import wrap
from langdetect import detect
import json

# Load spaCy models for different languages
nlp_models = {
    'en': spacy.load("en_core_web_sm"),
    'de': spacy.load("de_core_news_sm"),
    'fr': spacy.load("fr_core_news_sm")
}

# Read tweets from JSON file
def read_tweets(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

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

# Process any text input for Bluesky posting
def process_text_for_bluesky(text):
    """
    A unified function that processes any text input for Bluesky posting.
    This function handles all text processing operations in one place.
    
    Args:
        text (str): The input text to process
        
    Returns:
        dict: A dictionary containing the processed chunks and metadata
    """
    # Process the text into chunks
    chunks = process_tweet(text)
    
    # Create metadata for the processed text
    result = {
        'original_text': text,
        'chunks': chunks,
        'chunk_count': len(chunks)
    }
    
    return result

# Save chunks to JSON file
def save_chunks_to_json(chunks_data, output_file):
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(chunks_data, f, ensure_ascii=False, indent=4)
        print(f"Saved {len(chunks_data)} chunks to {output_file}")
    except Exception as e:
        print(f"Error saving chunks: {str(e)}")

def process_tweets_file(input_file, output_file):
    try:
        # Read tweets from JSON file
        tweets = read_tweets(input_file)
        
        # Process each tweet
        chunks_data = []
        for tweet in tweets:
            text = tweet['content']
            processed_chunks = process_text_for_bluesky(text)
            
            chunk_data = {
                'tweet_id': tweet['tweet_id'],
                'original_text': processed_chunks['original_text'],
                'chunks': processed_chunks['chunks'],
                'chunk_count': processed_chunks['chunk_count'],
                'timestamp': tweet['timestamp'],
                'media': tweet['media']
            }
            chunks_data.append(chunk_data)
        
        # Save chunks to JSON file
        save_chunks_to_json(chunks_data, output_file)
        print(f"Processed {len(chunks_data)} tweets and saved to {output_file}")
    except Exception as e:
        print(f"Error processing tweets: {str(e)}")

if __name__ == "__main__":
    input_file = "tweets.json"
    output_file = "processed_tweets.json"
    process_tweets_file(input_file, output_file)