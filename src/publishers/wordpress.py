import requests

class WordPressPublisher:
    def __init__(self, wp_url, token):
        self.wp_url = wp_url.rstrip('/')
        self.token = token

    def post_article(self, title, content, excerpt=None, tags=[]):
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        data = {
            'title': title,
            'content': content,
            'status': 'publish',
            'tags': tags
        }
        if excerpt:
            data['excerpt'] = excerpt

        response = requests.post(f'{self.wp_url}/wp-json/wp/v2/posts', headers=headers, json=data)
        response.raise_for_status()
        return response.json()
