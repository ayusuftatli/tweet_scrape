from flask import Flask, render_template, request, jsonify
import os
import dotenv
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
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        tweet_count = data.get('tweet_count', 5)
        outdir = data.get('outdir', './downloaded_media')
        
        asyncio.run(tweet_scraper.scrape(username, password, tweet_count, outdir))
        
        return jsonify({"message": "Scraping completed successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/process_tweet', methods=['POST'])
def process_tweet():
    try:
        data = request.get_json()
        tweet_text = data.get('tweet_text')
        bluesky_thread = text_seperator.process_tweet(tweet_text)
        return jsonify({"bluesky_thread": bluesky_thread}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500