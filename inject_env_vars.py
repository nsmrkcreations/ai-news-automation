import os
import re

INDEX_PATH = 'public/index.html'

adsense_id = os.getenv('ADSENSE_ID', 'ca-pub-XXXXXXXXXXXX')
analytics_id = os.getenv('ANALYTICS_ID', 'G-XXXXXXX')

with open(INDEX_PATH, 'r', encoding='utf-8') as f:
    html = f.read()

# Replace window.ENV_ANALYTICS_ID and window.ENV_ADSENSE_ID
html = re.sub(r"window\.ENV_ANALYTICS_ID\s*=\s*['\"]G-XXXXXXX['\"]", f"window.ENV_ANALYTICS_ID = '{analytics_id}'", html)
html = re.sub(r"window\.ENV_ADSENSE_ID\s*=\s*['\"]ca-pub-XXXXXXXXXXXX['\"]", f"window.ENV_ADSENSE_ID = '{adsense_id}'", html)

with open(INDEX_PATH, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Injected AdSense and Analytics IDs into {INDEX_PATH}")
