# Change Request: Update existing Python News Service

**Purpose:**
This document lists required changes to the existing Python service so it can **fetch latest news directly from websites (not APIs)**, collect media links, keep publisher attribution, summarize using Ollama, produce standardized JSON, and push changes to a Git repository.

---

## Goals / Requirements

1. **Source discovery**: Use RSS feeds where available; fall back to direct site scraping for sites without good RSS.
2. **Respect copyright & attribution**: Store only headline, excerpt/first N paragraphs, media URL (do not copy full article without permission). Always include `source` and `source_url` and ensure clicks redirect to original site.
3. **Collect media**: Capture image/video URL(s) found in the article (don’t re-host unless allowed).
4. **Summarization**: Use local Ollama model via CLI or HTTP endpoint to produce a short summary and extracted metadata (entities, keywords, reading_time).
5. **Output**: Produce one normalized JSON file per run and optionally per category. Follow the JSON schema outlined below.
6. **Git**: Commit and push generated JSON(s) to configured repo branch with deterministic commit messages.
7. **Robustness**: Retry, rate-limiting, robots.txt respect, user-agent string, logging and error handling.
8. **Extensibility**: Easy to add new sources and per-site parsing rules.

---

## Project-level changes (high-level)

- Add new module: `sources/` — contains per-publisher adapters (RSS adapter + HTML adapter pattern).
- Add new module: `scraper/` — generic scraping utilities (requests wrapper, Playwright fallback if needed).
- Add new module: `summarizer/` — wrapper for Ollama calls.
- Add new module: `publisher/` — creates JSON, handles git commit & push.
- Update `config.yaml` — include sources list, concurrency limits, git config, output paths.
- Add tests for adapters and JSON schema.

---

## config.yaml (example)

```yaml
output_dir: ./out
json_filename: news_latest.json
git:
  repo_path: /path/to/repo
  branch: main
  author_name: "News Bot"
  author_email: "news-bot@example.com"
sources:
  - id: moneycontrol
    name: Moneycontrol
    discovery: rss
    rss: https://www.moneycontrol.com/rss/MCtopnews.xml
    max_items: 10
  - id: bloomberg
    name: Bloomberg
    discovery: rss
    rss: https://feeds.bloomberg.com/markets/news.rss
    max_items: 10
  - id: custom_x
    name: X (Twitter)
    discovery: web
    base_url: https://x.com/
    max_items: 20
user_agent: "MyNewsCrawler/1.0 (+https://example.com/contact)"
concurrency: 4
ollama:
  cli: true
  model: "llama3"
  timeout_seconds: 30
```

---

## JSON Schema (output)

```json
{
  "articles": [
    {
      "id": "<source>_<sha1-of-url-or-title>",
      "title": "...",
      "source": "Moneycontrol",
      "source_url": "https://...",
      "published_at": "2025-09-16T09:30:00Z",
      "category": "business",
      "language": "en",
      "media": [
        {"type": "image", "url": "https://..."}
      ],
      "excerpt": "first 2-3 paragraphs or lead",
      "content_snippet": "first 500 chars of article (for preview)",
      "summary": "3-sentence summary from Ollama",
      "keywords": ["ai","economy"],
      "reading_time_minutes": 2,
      "fetched_at": "2025-09-16T10:00:00Z"
    }
  ]
}
```

> **Note:** `source_url` must be present and editors must not replace it—UI will redirect users to `source_url` when clicked.

---

## Implementation Details & Code Examples

### 1) Source adapter pattern
Create a base `SourceAdapter` class with methods:
- `discover()` → yields article URLs (from RSS or site pages)
- `fetch(url)` → returns raw HTML/response
- `parse(html)` → returns normalized dict (title, published_at, media_urls, excerpt)

Each publisher gets a small adapter that overrides `parse` logic. Keep rules minimal and robust.

### 2) Discovery
- Prefer RSS: parse XML, read `<item>` entries.
- If RSS not available, crawl the site's listing or search pages.
- Respect `max_items` per source in config.

### 3) Scraping
- Use `requests` with timeout + retry backoff for simple pages.
- Use `playwright` (headless) for JS-heavy sites (only when necessary).
- Always fetch robots.txt and confirm `User-agent` access before scraping site sections.
- Use a configurable `User-Agent` string.

**requests wrapper example**

```python
# scraper/http.py
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))

def get(url, headers=None, timeout=15):
    headers = headers or {}
    return session.get(url, headers=headers, timeout=timeout)
```

### 4) HTML parsing
- Use `BeautifulSoup` for extracting `<meta property="og:image">`, `<meta name="description">`, and main `<article>` or `<div class="content">` blocks.
- Fall back: gather first N `<p>` tags that are not navigation/ads.

### 5) Media capture
- Prefer `og:image`, `twitter:image` meta tags. If not present, collect largest `<img>` in article.
- Store media as URL(s) only. **Do not** download and re-host unless license permits.

### 6) Ollama summarizer wrapper
- Provide sync and async wrappers depending on your use-case.
- Example using CLI call (subprocess):

```python
# summarizer/ollama_cli.py
import subprocess, shlex, json

def summarize(text, model='llama3', max_tokens=200):
    prompt = f"Summarize in 3 sentences and provide 5 keywords:\n\n{text}"
    proc = subprocess.run([
        'ollama', 'run', model, '--json'
    ], input=prompt.encode(), capture_output=True, timeout=30)
    return proc.stdout.decode().strip()
```

> Option: run Ollama as a local server and use HTTP client rather than subprocess for better concurrency.

### 7) Normalization & deduplication
- Normalize by canonical URL or hash of (source + slug + published_at).
- Keep an in-memory set to avoid duplicates within a run.

### 8) Output & Git push
- Generate `news_latest.json` atomically: write to `news_latest.json.tmp` then move/rename.
- Use `GitPython` to add, commit and push.
- Commit message pattern: `news: update {N} articles {YYYY-MM-DDTHH:MM:SS}`
- Optional: tag the commit with date for easy history.

**git push example**

```python
from git import Repo

def push_json(repo_path, file_path, author_name, author_email, branch='main'):
    repo = Repo(repo_path)
    repo.index.add([file_path])
    repo.index.commit(f"news: update {file_path}", author=repo.config_reader().get_value('user','name', author_name))
    origin = repo.remote(name='origin')
    origin.push(branch)
```

---

## Operational Notes & Legal Considerations

- **Robots.txt**: Respect `robots.txt` and site-specific terms. If a site explicitly forbids scraping, remove it from the sources list.
- **Rate limits**: Honor publisher servers (low concurrency, random delays).
- **Attribution**: Always include `source` and `source_url`. Use only short excerpts and encourage click-through to original.
- **Copyright**: Storing small excerpts and headlines is generally safer than full-article reproduction, but consult legal counsel for production.

---

## Tests
- Unit tests for adapters: ensure `parse()` returns required keys.
- Integration test: run on one or two allowed RSS sources and validate output JSON against schema.
- Add linter and basic CI (GitHub Actions) to run tests and flake8.

---

## Logging & Monitoring
- Add structured logging (JSON logs) with levels.
- Capture metrics: articles fetched per source, failures, average fetch time.
- Configure alerting for repeated failures (e.g., 5 consecutive fetch errors for a source).

---

## Deployment & Scheduling
- Run as cron every X minutes (configurable). For high frequency, stagger sources across runs.
- Consider running on a small VPS or your laptop service; ensure your IP isn't blocked by publishers.

---

## Backwards compatibility & migration
- Keep previous `news.json` schema compatibility: include `legacy` field if keys change.
- Provide a compatibility script to migrate old JSON files to the new schema.

---

## Quick TODO Checklist (for PR)

- [ ] Add `sources/` adapters for Moneycontrol, Bloomberg, CNBC, India Today.
- [ ] Implement `scraper/http.py` with retries and robots.txt check.
- [ ] Implement `summarizer/ollama.py` wrapper (CLI and HTTP options).
- [ ] Implement `publisher/json_writer.py` and `publisher/git_pusher.py`.
- [ ] Update `config.yaml`.
- [ ] Add unit/integration tests.
- [ ] Add README updates and developer notes on legal/copyright.

---

If you want, I can also generate the **pull request description** text (MD) ready to paste into GitHub that summarizes these changes for reviewers.

