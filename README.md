# AI News Automation

Automated AI-powered news content creation and multi-platform publishing system.

## Features

- Fetch trending news automatically
- Generate SEO-optimized articles with LLaMA
- Publish articles to WordPress automatically
- Cross-post snippets to Medium, LinkedIn, and other social platforms

## Setup

1. Clone repo  
2. Copy `.env.template` to `.env` and fill in your API keys and tokens  
3. Build and run with Docker-compose  
4. Push updates to GitHub to auto-deploy via GitHub Actions  

## Environment Variables

- `NEWS_API_KEY`: NewsAPI.org API key  
- `WORDPRESS_URL`: Your WordPress site URL  
- `WORDPRESS_TOKEN`: JWT token for WordPress REST API  
- `MEDIUM_TOKEN`: Medium integration token  
- `LINKEDIN_TOKEN`: LinkedIn OAuth token  
- `LINKEDIN_AUTHOR_URN`: Your LinkedIn user URN  

## License

MIT
