# NewsSurgeAI - AI-Powered News Automation Platform

## Overview

NewsSurgeAI is an automated news platform that builds a **passive income stream** by:

- **Fetching trending news** using free news aggregation APIs (e.g., NewsAPI.org)  
- **Generating high-quality articles** automatically using AI (LLaMA model)  
- **Publishing content with media** (images included) to a WordPress website via REST API  
- Automating these steps with scheduled runs **without manual intervention**

## Key Features

- **Free News API Integration:** Collect trending news without cost.  
- **AI-Driven Content Creation:** Generate 700–1000 word SEO-optimized articles.  
- **Media Extraction:** Extract images from news articles, embed in generated content.  
- **WordPress Publisher:** Publish articles with images and metadata automatically.  
- **Scheduling:** Run 3 cycles daily at fixed times (9 AM, 2 PM, 7 PM).

---

## Application Components

| Component                | Description                                              | Technologies/Services                 |
|--------------------------|--------------------------------------------------------|---------------------------------------|
| News Aggregator          | Fetches latest trending news from free APIs            | NewsAPI.org (free tier API)           |
| AI Content Generator     | Generates unique articles using topic and keywords      | Meta’s LLaMA model (local/cloud)      |
| Media Extractor & Inserter | Downloads and adds images to articles                 | Python `requests`, HTML parsing       |
| WordPress Publisher      | Publishes with media to WordPress via REST API         | WordPress REST API + JWT Auth         |
| Scheduler                | Runs the content cycle on a fixed automated schedule   | Python `schedule` library             |

---

## Free News APIs Used

- **NewsAPI.org** — Free tier allows 100 requests per day, sources global news.  
- (Optional backup) Other free news APIs can be configured if needed.

---

## Media Handling

- Images are extracted from the original news article metadata (if present).  
- Downloaded and uploaded to WordPress media library or embedded with direct URLs.  
- Articles contain the featured image and inline images as appropriate.

---

## Requirements

### Software

- **Python 3.10+**  
- Required Python libraries (see `requirements.txt`):  
  - `requests`  
  - `transformers` (with support for LLaMA)  
  - `torch`  
  - `schedule`  
  - `python-dotenv`  

### Services

- **GitHub Pages Website**  
  - Static site generator (Jekyll/Hugo)
  - GitHub Actions for automation
  - Custom domain integration
  - Automated build and deploy

### API Keys

- **NewsAPI.org key** (free signup required)  
- **WordPress site URL and JWT token**

---

## How It Works (Flow)

1. **Fetch trending news headlines and article metadata** from NewsAPI.  
2. **Extract keywords and main topics** from retrieved articles.  
3. **Generate a unique AI-authored article** based on topic/keywords using LLaMA.  
4. **Fetch associated images** from original news metadata and prepare media for publishing.  
5. **Publish the article with images** to the WordPress site automatically via REST API.  
6. **Repeat the cycle** three times daily to build fresh SEO content and attract organic traffic.  

---

## Running & Testing Locally

- Prepare Python environment with dependencies  
- Configure `.env` file with API keys and WordPress info  
- Run `orchestrator.py` manually or start scheduled mode  
- Observe console logs for content generation and publishing status  

---

## Benefits

- Fully automated content pipeline with **no manual writing needed**  
- Relies on **free API resources** keeping costs minimal  
- Builds consistent, SEO-optimized content on your owned property (WordPress site)  
- Supports images to enhance article engagement and ad revenue potential  
