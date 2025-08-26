import requests

class LinkedInPublisher:
    def __init__(self, access_token, author_urn):
        self.access_token = access_token
        self.api_url = "https://api.linkedin.com/v2/"
        self.author_urn = author_urn

    def post_article(self, text, article_url):
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "X-Restli-Protocol-Version": "2.0.0",
            "Content-Type": "application/json"
        }
        content = {
            "author": self.author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": f"{text}\nRead more: {article_url}"},
                    "shareMediaCategory": "ARTICLE",
                    "media": [
                        {
                            "status": "READY",
                            "originalUrl": article_url,
                            "title": {"text": text}
                        }
                    ]
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
        }
        response = requests.post(f"{self.api_url}ugcPosts", headers=headers, json=content)
        response.raise_for_status()
        return response.json()
