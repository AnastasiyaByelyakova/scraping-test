import random
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message


class AntiBotProxyMiddleware(RetryMiddleware):
    """
    Centralized middleware layer handling dynamic proxy rotation, 
    user-agent spoofing, and automatic bot fallback strategies.
    """
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ]

    # Placeholder proxy pool - in production, tie this to your proxy provider API (e.g., BrightData, Oxylabs)
    PROXY_POOL = [ ]

    def process_request(self, request, spider):
        # 1. Rotate User-Agents for raw HTTP calls
        request.headers['User-Agent'] = random.choice(self.USER_AGENTS)

        # 2. Inject Rotating Proxies into the request context
        if self.PROXY_POOL:
            proxy = random.choice(self.PROXY_POOL)
            request.meta['proxy'] = proxy

        # 3. For pages requiring Javascript/Cloudflare execution, apply Playwright arguments
        if request.meta.get('playwright'):
            request.meta['playwright_context_kwargs'] = {
                "ignore_https_errors": True,
                "proxy": {"server": proxy} if self.PROXY_POOL else None,
            }

    def process_response(self, request, response, spider):
        # Intercept Cloudflare challenge signals or blocks
        if response.status in [403, 503, 429]:
            spider.logger.warning(f"Status fallback triggered for code: {response.status}.Rotating node...")
            reason = response_status_message(response.status)
            return self._retry(request, reason, spider) or response
        return response