import requests
from datetime import datetime, timezone
import re
from typing import List, Dict
import dotenv

dotenv.load_dotenv()



class BlueskyClient:
    def __init__(self, pds_url="https://bsky.social"):
        self.pds_url = pds_url
        self.session = {
            "did": None,
            "accessJwt": None
        }

    def login(self, handle: str, password: str):
        """Authenticate with Bluesky servers"""
        resp = requests.post(
            f"{self.pds_url}/xrpc/com.atproto.server.createSession",
            json={"identifier": handle, "password": password}
        )
        resp.raise_for_status()
        data = resp.json()
        self.session.update({
            "did": data["did"],
            "accessJwt": data["accessJwt"]
        })

    def _create_post(self, text: str, parent_ref: Dict = None, root_ref: Dict = None) -> Dict:
        """Internal method to create a single post"""
        post = {
            "$type": "app.bsky.feed.post",
            "text": text,
            "createdAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        }

        if parent_ref and root_ref:
            post["reply"] = {
                "root": root_ref,
                "parent": parent_ref
            }

        resp = requests.post(
            f"{self.pds_url}/xrpc/com.atproto.repo.createRecord",
            headers={"Authorization": "Bearer " + self.session["accessJwt"]},
            json={
                "repo": self.session["did"],
                "collection": "app.bsky.feed.post",
                "record": post
            }
        )
        resp.raise_for_status()
        return resp.json()

    @staticmethod
    def split_text(text: str, max_len: int = 300) -> List[str]:
        """Split text into chunks respecting word boundaries"""
        chunks = []
        while len(text) > max_len:
            split_at = text.rfind(' ', 0, max_len)
            if split_at <= 0:  # Handle long unbroken strings
                split_at = max_len
            chunks.append(text[:split_at].strip())
            text = text[split_at:].strip()
        chunks.append(text)
        return chunks

    def create_thread(self, text: str) -> List[Dict]:
        """Create a threaded post from long text"""
        chunks = self.split_text(text)
        if not chunks:
            return []

        thread_refs = []
        for idx, chunk in enumerate(chunks):
            if idx == 0:  # Root post
                response = self._create_post(chunk)
                root_ref = {
                    "uri": response["uri"],
                    "cid": response["cid"]
                }
                parent_ref = root_ref
                thread_refs.append(root_ref)
            else:  # Reply post
                response = self._create_post(
                    chunk,
                    parent_ref=parent_ref,
                    root_ref=root_ref
                )
                new_ref = {
                    "uri": response["uri"],
                    "cid": response["cid"]
                }
                parent_ref = new_ref
                thread_refs.append(new_ref)

        return thread_refs

if __name__ == "__main__":
    # Example usage
    client = BlueskyClient(os.getenv("BLUESKY_USERNAME"), os.getenv("BLUESKY_PASSWORD"))
    
    # Replace with your credentials (never commit real credentials!)
    client.login()
    
    long_post = """In an era where social media platforms constantly vie for our attention, Bluesky stands out with its innovative approach to decentralized networking. By implementing the AT Protocol, Bluesky offers users unprecedented control over their data and interactions. Let's explore three key advantages...

    [1] User-Controlled Data Portability: Unlike traditional platforms that lock your data within their ecosystem, Bluesky allows seamless migration of your profile, connections, and content between providers. This means...

    [2] Algorithmic Choice: Bluesky's unique system enables users to select from multiple curation algorithms. Whether you prefer chronological feeds, topic-based sorting, or community-recommended content...

    [3] Interoperable Moderation: The platform's composable moderation system allows users and communities to layer filtering mechanisms. You can combine..."""

    try:
        thread_refs = client.create_thread(long_post)
        print(f"Successfully created thread with {len(thread_refs)} posts")
        print(f"Root post URI: {thread_refs[0]['uri']}")
    except Exception as e:
        print(f"Error creating thread: {str(e)}")