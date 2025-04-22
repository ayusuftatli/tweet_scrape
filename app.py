from flask import Flask, render_template, request, jsonify
import os
import dotenv
import asyncio
import tweet_scraper
import text_seperator

dotenv.load_dotenv()

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    try:
        
        asyncio.run(tweet_scraper.scrape())
        return jsonify({"message": "Scraping completed successfully!", "data": "Check tweets.json for results"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/process_tweet', methods=['POST'])
def process_tweet():
    try:
        data = request.get_json()
        tweet_text = data.get('tweet_text')
        if not tweet_text:
            return jsonify({"error": "Tweet text is required"}), 400
            
        processed_result = text_seperator.process_text_for_bluesky(tweet_text)
        return jsonify(processed_result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)