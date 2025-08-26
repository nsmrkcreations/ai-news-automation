import requests

class MediumPublisher:
    def __init__(self, integration_token):
        self.token = integration_token
        self.api_url = 'https://api.medium.com/v1'

    def get_user_id(self):
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        response = requests.get(f'{self.api_url}/me', headers=headers)
        response.raise_for_status()
        data = response.json()
        return data['data']['id']

    def publish_post(self, title, content, tags=[]):
        user_id = self.get_user_id()
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        post_data = {
            'title': title,
            'contentFormat': 'html',
            'content': content,
            'publishStatus': 'public',
            'tags': tags[:5]
        }
        response = requests.post(f'{self.api_url}/users/{user_id}/posts', headers=headers, json=post_data)
        response.raise_for_status()
        return response.json()
