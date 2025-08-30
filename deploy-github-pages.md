# GitHub Pages Deployment Guide

## 1. Create GitHub Repository
```bash
# Initialize git if not already done
git init
git add .
git commit -m "Initial commit - AI News Automation"

# Create repository on GitHub and push
git remote add origin https://github.com/YOUR_USERNAME/ai-news-automation.git
git branch -M main
git push -u origin main
```

## 2. Enable GitHub Pages
1. Go to your repository on GitHub
2. Click **Settings** tab
3. Scroll to **Pages** section
4. Under **Source**, select **GitHub Actions**
5. The workflow will automatically deploy from `public/` directory

## 3. Repository Structure for Pages
```
ai-news-automation/
├── .github/workflows/deploy.yml  ✓ (configured)
├── public/                       ✓ (frontend files)
│   ├── index.html               ✓
│   ├── css/                     ✓
│   ├── js/                      ✓
│   └── data/news.json           ✓
├── src/                         (backend - not deployed)
└── .env                         (local only)
```

## 4. Your Site Will Be Available At:
`https://YOUR_USERNAME.github.io/ai-news-automation/`

## 5. Automatic Updates
- Push to `main` branch triggers automatic deployment
- Frontend updates in ~2-3 minutes
- Backend runs locally and updates `public/data/news.json`
