# NetShort Scraper

A reusable web scraping framework built with **Scrapy** and **Playwright** for collecting publicly available series from NetShort.

The project is designed to be extensible to additional websites while incorporating proxy management and anti-bot techniques as core architectural components.

---

## Features

- Scrapy-based crawling framework
- Playwright integration for JavaScript-rendered pages
- Reusable base spider architecture
- JSON-LD extraction where available
- CSV export
- Duplicate filtering
- Configurable proxy support
- Automatic proxy rotation
- User-Agent rotation
- Automatic retries on blocked requests
- Exponential backoff for temporary blocking
- Separation of scraping logic and networking middleware

---

## Project Structure

```
test_scraper/
│
├── spiders/
│   ├── base_spider.py
│   └── netshort.py
│
├── middlewares.py
├── pipelines.py
├── settings.py
└── items.py
```

---

## Technology Choice

This project uses **Scrapy** together with **scrapy-playwright**.

### Why Scrapy?

Scrapy provides:

- asynchronous request scheduling
- efficient crawling
- middleware support
- automatic duplicate filtering
- pipelines
- excellent extensibility

### Why Playwright?

NetShort renders part of its content using JavaScript.

Playwright allows rendering only the pages that require JavaScript while keeping the remainder of the crawl lightweight and efficient.

---

# Architecture

```
Spider
   │
   ▼
Downloader Middleware
   │
   ├── Proxy rotation
   ├── User-Agent rotation
   ├── Retry handling
   ├── Exponential backoff
   └── Anti-bot request preparation
   │
Downloader
   │
Website
```

The spider is responsible only for extracting data.

Networking concerns such as proxy selection, retries, and request preparation are handled by downloader middleware.

---

# Anti-Bot Strategy

The scraper incorporates several techniques to reduce blocking:

- rotating proxies
- rotating User-Agents
- automatic retries
- exponential backoff
- Playwright rendering for JavaScript pages
- configurable request headers

---


# Proxy Support

Proxy management is implemented as a dedicated downloader middleware.

Features include:

- configurable proxy list
- automatic proxy selection
- proxy rotation
- removal of failed proxies
- configurable retry limits

Proxy configuration:

```python
PROXY_LIST = [
    "http://user:password@proxy1:8000",
    "http://user:password@proxy2:8000",
]
```

---

# Retry Strategy

The scraper automatically retries requests when encountering temporary failures.

Retry HTTP status codes:

- 403 Forbidden
- 429 Too Many Requests
- 500 Internal Server Error
- 502 Bad Gateway
- 503 Service Unavailable
- 504 Gateway Timeout

Network exceptions are also retried automatically.

---

# Exponential Backoff

Blocked requests are retried using exponential backoff.

Example:

| Retry | Delay |
|-------:|------:|
| 1 | 1 second |
| 2 | 2 seconds |
| 3 | 4 seconds |
| 4 | 8 seconds |
| 5 | 16 seconds |

This reduces request bursts and helps avoid repeated blocking.

---

# User-Agent Rotation

Each outgoing request receives a randomly selected browser User-Agent.

Supported browsers include:

- Chrome
- Firefox
- Safari
- Edge

This reduces the likelihood of detection by basic anti-bot systems.

---

# Data Extraction

The scraper collects:

- Series title
- Series URL
- Cover image URL
- Description
- Genre 
- Episode count

Not available and not exported: 
- Status (when available)
- Tags / ranking (when available)

The output is exported as a deduplicated CSV file.

---

# Running

Install dependencies

```bash
pip install scrapy scrapy-playwright playwright
```


```bash
playwright install
```


Run the spider

```bash
scrapy crawl netshort
```


---

# Extending to Other Websites

The framework has been designed for reuse.

To add support for another website:

1. Create a new spider inheriting from `BaseUniversalSpider`.
2. Implement the parsing logic.
3. Reuse the existing middleware for:
   - proxy management
   - retries
   - anti-bot handling
   - request preparation

No changes to the middleware are required.

---



## Configuration

The `settings.py` file contains various configurations for Scrapy and Scrapy-Playwright, including:

*   `CONCURRENT_REQUESTS`: Limits concurrent requests.
*   `DOWNLOAD_DELAY`: Sets a delay between requests.
*   `DOWNLOAD_HANDLERS`: Configures Scrapy to use `ScrapyPlaywrightDownloadHandler` for HTTP/HTTPS requests.
*   `PLAYWRIGHT_LAUNCH_OPTIONS`: Configures Playwright browser launch options (e.g., `headless` mode, browser arguments).
*   `PLAYWRIGHT_BROWSER_TYPE`: Specifies the browser type (e.g., `chromium`).
*   `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`: Sets the default navigation timeout for Playwright.
*   `PLAYWRIGHT_MAX_CONTEXTS`, `PLAYWRIGHT_MAX_PAGES_PER_CONTEXT`: Limits Playwright browser contexts and pages.
*   `PLAYWRIGHT_START_URLS_AS_REQUESTS`: Ensures `start_urls` are processed as Playwright requests.
*   `LOG_LEVEL`: Set to `DEBUG` for detailed logging during development.
*   `HTTPCACHE_ENABLED`: Explicitly disabled to ensure all requests go through Playwright.
*   `CSV_FILE_PATH`: Set output CSV file name here