import asyncio
import json
from twscrape import API, gather
from twscrape.logger import set_log_level
import dotenv
import os
import json
from datetime import datetime
import httpx

dotenv.load_dotenv()

async def download_file(client: httpx.AsyncClient, url: str, outdir: str):
    filename = url.split("/")[-1].split("?")[0]
    outpath = os.path.join(outdir, filename)

    async with client.stream("GET", url) as resp:
        with open(outpath, "wb") as f:
            async for chunk in resp.aiter_bytes():
                f.write(chunk)

async def download_tweet_media(api: API, tweet_id: int, outdir: str):
    os.makedirs(outdir, exist_ok=True)
    all_photos = []
    all_videos = []

    tweet = await api.tweet_details(tweet_id)
    if hasattr(tweet, "media") and tweet.media:
        for media in tweet.media.photos:
            all_photos.append(media.url)
        for video in tweet.media.videos:
            variant = sorted(video.variants, key=lambda x: x.bitrate)[-1]
            all_videos.append(variant.url)

    async with httpx.AsyncClient() as client:
        await asyncio.gather(
            *[download_file(client, url, outdir) for url in all_photos],
            *[download_file(client, url, outdir) for url in all_videos],
        )

async def scrape():
    api = API()

    # Only username and password are required in manual mode
    TWITTER_USERNAME = os.getenv("TWITTER_USERNAME")
    TWITTER_PASSWORD = os.getenv("TWITTER_PASSWORD")

    # Add account in manual mode (will prompt for email code if needed)
    await api.pool.add_account(
        username=TWITTER_USERNAME,
        password=TWITTER_PASSWORD,
        email="",  # Leave empty for manual mode
        email_password="",  # Leave empty for manual mode
    )
    
    await api.pool.login_all()

    # Get twitter profile info
    twitter_profile = await api.user_by_login("rumeliobserver")
    
    # Get 5 latest tweets from from the twitter profile
    tweets = await gather(api.user_tweets(twitter_profile.id, limit=5))

    # Create a directory for media downloads
    media_dir = "downloaded_media"
    os.makedirs(media_dir, exist_ok=True)

    
    # Print the tweets and download media
    for tweet in tweets:
        print(f"Tweet ID: {tweet.id}")
        print(f"Content: {tweet.rawContent}")
        print(f"Posted at: {tweet.date}")

        if hasattr(tweet,  "media") and tweet.media:
            print("\nMedia in this tweet:")
            print(f"Media Extracted: {tweet.media}")
            # Download media for this tweet
            await download_tweet_media(api, tweet.id, media_dir)
            
        print("-" * 50)

        formatted_tweets = []
        for tweet in tweets:
            tweet_data = {
                "tweet_id": str(tweet.id),
                "content": tweet.rawContent,
                "timestamp": tweet.date.isoformat(),
                "media": {
                    "photos": [photo.url.split("/")[-1].split("?")[0] for photo in tweet.media.photos] if hasattr(tweet.media, "photos") else [],
                    "videos": [video.variants[0].url.split("/")[-1].split("?")[0] if video.variants else "" for video in tweet.media.videos] if hasattr(tweet.media, "videos") else [],
                    "animated": [anim.variants[0].url.split("/")[-1].split("?")[0] if anim.variants else "" for anim in tweet.media.animated] if hasattr(tweet.media, "animated") else []
                }
            }
            formatted_tweets.append(tweet_data)
        
        # Save to JSON file
        with open('tweets.json', 'w', encoding='utf-8') as f:
            json.dump(formatted_tweets, f, ensure_ascii=False, indent=2)
        
        print(f"Saved {len(formatted_tweets)} tweets to tweets.json")

