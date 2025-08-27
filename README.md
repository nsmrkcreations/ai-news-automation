# NewsSurgeAI Platform

Advanced AI-powered news aggregation and static site generator at [NewsSurgeAI.com](https://nsmrkcreations.github.io/ai-news-automation)

## Core Features

- Real-time news aggregation from multiple categories
- Automatic content updates every 3 hours
- SEO-optimized static site generation
- Social sharing integration
- Mobile-responsive design
- AdSense integration

## Setup

1. Clone repo  
2. Copy `.env.template` to `.env` and fill in your API key  
3. Install Python dependencies: `pip install -r requirements.txt`  
4. Run locally: `python -m http.server 8000 --directory public`
5. Push updates to GitHub to auto-deploy via GitHub Actions

## Development

- The site is built as a static HTML/CSS/JS site
- News data is fetched using NewsAPI
- Updates run automatically via GitHub Actions
- Deploys to GitHub Pages

## Environment Variables

- `NEWS_API_KEY`: NewsAPI.org API key (required for news updates)

## License

MIT
