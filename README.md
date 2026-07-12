# Scraping Task: NetShort Scraper

This project contains a Scrapy spider designed to scrape series information from `netshort.com` using Playwright for handling dynamic content and pagination.
* Scrapy natively enforces a clean separation of concerns. Spiders only handle parsing logic; structural behaviors (like proxy insertion, deduplication, and file generation) are globally managed by Middlewares and Pipelines.
* Hybrid Execution Efficiency: It allows to scrape standard static sections using raw asynchronous HTTP requests for high speed, while selectively triggering headless browser context (scrapy-playwright) exclusively for sections protected by dynamic JavaScript.
* First-Class Extensibility: Adding a new target site in the future requires writing nothing more than a simple, lightweight parsing class. The core routing engine remains completely untouched.

**Extensibility**

Every new target site will inherit from BaseUniversalSpider. They simply define their unique domain limits and CSS selector maps.

**Proxy & Anti-Bot Shielding**

The AntiBotProxyMiddleware automatically hooks into every outgoing network request. It handles user-agent randomization, rotates proxies dynamically from an upstream pool, masks browser configurations via playwright-stealth, and watches for HTTP 403/503 codes to auto-throttle or switch nodes safely.
(Do not forget to set correct proxies!)

## Setup

To set up and run this project, follow these steps:

1.  **Clone the repository (if applicable):**
    ```bash
    # If this is a git repository
    # git clone <your-repo-url>
    # cd scraping_task
    ```

2.  **Create and activate a virtual environment:**
    It's recommended to use a virtual environment to manage project dependencies.
    ```bash
    python -m venv venv
    source venv/bin/activate # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    Install Scrapy, Scrapy-Playwright, and Playwright browser executables.
    ```bash
    pip install scrapy scrapy-playwright
    playwright install chromium # Install the Chromium browser for Playwright
    ```

## Usage

To run the spider, navigate to the project's root directory (`scraping_task`) and execute the Scrapy command:

```bash
scrapy crawl netshort 
```

## Spider Details

### `NetShortSpider`

*   **Name:** `netshort`
*   **Allowed Domains:** `netshort.com`
*   **Start URLs:** `https://netshort.com/drama/all-plots`
*   **Functionality:**
    *   Uses Playwright to navigate the website, handling JavaScript-rendered content.
    *   Extracts series cards from the main catalog page.
    *   Follows links to individual series detail pages to extract more information.
    *   Implements pagination by parsing page numbers from the navigation bar.
    *   Blocks unwanted resource types (images, stylesheets, fonts) using a Playwright hook to improve scraping efficiency.
    *   Extracts structured data (JSON-LD) where available, falling back to CSS/XPath selectors for other details.

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