from scrapy.settings.default_settings import LOG_LEVEL

BOT_NAME = "test_scraper"
SPIDER_MODULES = ["test_scraper.spiders"]
NEWSPIDER_MODULE = "test_scraper.spiders"

# Politeness and Anti-Fingerprinting Concurrency Rules
CONCURRENT_REQUESTS = 15
DOWNLOAD_DELAY = 1.5  # Strategic adaptive crawl delay
RANDOMIZE_DOWNLOAD_DELAY = True

# Activating System Infrastructure Modules
DOWNLOADER_MIDDLEWARES = {
    'test_scraper.middlewares.AntiBotProxyMiddleware': 100,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
}

ITEM_PIPELINES = {
    'test_scraper.pipelines.DeduplicationPipeline': 100,
    'test_scraper.pipelines.CleanAndFormattingPipeline': 200,
    'test_scraper.pipelines.CsvExportPipeline': 300, # Added CsvExportPipeline
}

# Enabling Pluggable Headless Endpoints for Cloudflare Mitigation
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}
DOWNLOAD_HANDLERS_BASE = {} # Explicitly disable default HTTP/HTTPS handlers
HTTPCACHE_ENABLED = False # Explicitly disable HTTP cache

PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": True,
    "args": ["--disable-blink-features=AutomationControlled", "--no-sandbox"], # Added --no-sandbox
}
PLAYWRIGHT_BROWSER_TYPE = "chromium" # Added global Playwright browser type
PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT = 1800000000 # Reverted to 180 seconds
PLAYWRIGHT_PROCESS_REQUEST_HEADERS = None # Added to potentially resolve header processing issues
PLAYWRIGHT_MAX_CONTEXTS = 1 # Limit to one browser context
PLAYWRIGHT_MAX_PAGES_PER_CONTEXT = 8 # Limit to one page per context
PLAYWRIGHT_START_URLS_AS_REQUESTS = True # Re-added to ensure start_urls use Playwright
LOG_LEVEL = "DEBUG" 

# Custom settings
CSV_FILE_PATH = 'scraped_results.csv' # Define the output CSV file name here
MAX_PROXY_RETRIES = 3
PROXY_LIST = ['154.219.125.230:3128']
USE_PROXIES = False