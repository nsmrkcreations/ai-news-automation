# AI News Automation Project Requirements

## 1. Project Overview
A full-stack, production-ready web application for NewSurgeAI.com that automatically fetches, summarizes, and publishes the latest news from free news APIs (e.g., newsAPI.org and more) using AI models from local system using ollama (e.g., Llama). The platform delivers a modern, responsive user experience inspired by leading news sites (BBC, FirstPost, wallstreet, cnbc  etc.) and supports web, tablet, and mobile devices.

## 2. Core Features
### Backend (Python Service) Which should in Local system (personal computer)
- Fetch news articles from open/free news APIs (initially newsAPI.org, and other)
- Summarize articles using AI Ollama(Llama or similar)
- Categorize news (technology, business, science, world, etc.), most of the popular categories
- Mark breaking news (recent/important)
- Deduplicate and filter articles
- Store articles in a structured JSON file for frontend consumption
- Schedule periodic updates (cron/scheduler)
- Log and handle errors robustly
- Support environment variables for API keys and config
- utilise max free limit per day from free news API's
- We have to push summarized news to our frontend application very frequently.

### Frontend (Web Application)
- Modern, responsive UI (web, tablet, mobile)
- Clean layout inspired by BBC, FirstPost, etc.
- Header with logo, navigation, date, and social links
- Breaking news ticker
- Hero/main story and side stories
- Latest news grid with category filters and load more
- Topic sections (technology, business, etc.)
- Article cards with image, title, summary, source, date
- Footer with info, links, and newsletter subscription
- Progressive Web App (PWA) support
- Error handling and fallback images
- Google Adsense integration

## 3. Technical Requirements
- Python 3.10+
- Node.js for frontend tooling (optional)
- HTML5, CSS3 (with variables, grid, flexbox, media queries)
- Vanilla JavaScript (ES6+)
- REST API integration (newsAPI.org)
- AI summarization using ollama(local model)
- Environment variable management
- Logging and monitoring
- GitHub Actions for CI/CD (optional)
- Frontend: Website host in Github
- Backedend: will run in my computer

## 4. Data Model (news.json)
Each article must include:
- `title`: string
- `description`: string
- `url`: string
- `urlToImage`: string (image URL or fallback)
- `publishedAt`: ISO datetime string
- `source`: string
- `category`: string (technology, business, science, world, general)
- `isBreaking`: boolean

## 5. Workflow
1. **Idea & Planning**
   - Define goals, target audience, and feature set
   - Research reference designs and APIs
2. **Backend Development**
   - Implement news fetcher and aggregator
   - Integrate AI summarization
   - Build scheduler and error handling
   - Output validated JSON for frontend
3. **Frontend Development**
   - Design and build responsive UI
   - Implement news rendering, filters, and interactivity
   - Add PWA features and accessibility
4. **Testing & QA**
   - Unit and integration tests for backend
   - UI/UX testing on multiple devices
   - Validate data flow end-to-end
5. **Deployment**
   - Set up CI/CD pipeline
   - Configure environment variables and secrets
   - Deploy to production (GIThub, Local computer (my personal).)
6. **Monitoring & Maintenance**
   - Monitor logs, errors, and API usage
   - Update dependencies and models
   - Add new features and improve UX

## 6. Future Enhancements
- Multi-language support
- Advanced search and filtering
- Push notifications
- Analytics dashboard
- More news sources/APIs
- AI-powered recommendations

---

**This document serves as a blueprint for building, testing, and deploying the AI News Automation platform from idea to production-ready.**
