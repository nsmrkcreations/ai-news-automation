from flask import Flask, send_from_directory
from flask_compress import Compress
import os
from core.logger import setup_logger

logger = setup_logger()

# Initialize Flask app
app = Flask(__name__, static_folder='../public', static_url_path='')
Compress(app)

@app.route('/')
def root():
    return app.send_static_file('index.html')

@app.route('/<path:path>')
def serve_static(path):
    response = app.send_static_file(path)
    # Set cache headers for static files
    if path.endswith(('.css', '.js', '.jpg', '.png', '.ico')):
        response.headers['Cache-Control'] = 'public, max-age=31536000'
    return response

if __name__ == "__main__":
    # Use Gunicorn WSGI server in production
    if os.environ.get('FLASK_ENV') == 'development':
        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        # This branch won't be taken as we'll use gunicorn command line
        from gunicorn.app.base import BaseApplication

        class WebApp(BaseApplication):
            def __init__(self, app, options=None):
                self.options = options or {}
                self.application = app
                super().__init__()

            def load_config(self):
                for key, value in self.options.items():
                    self.cfg.set(key, value)

            def load(self):
                return self.application

        options = {
            'bind': '0.0.0.0:5000',
            'workers': 3,
            'worker_class': 'gthread',
            'threads': 2,
            'timeout': 30,
            'accesslog': 'logs/access.log',
            'errorlog': 'logs/error.log'
        }

        WebApp(app, options).run()
