import os
import time
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
    RETRY_STATUSES = {403, 429, 500, 502, 503, 504}


    def __init__(self, settings):
        super().__init__(settings)

        self.max_retries = settings.getint("MAX_PROXY_RETRIES", 3)
        self.proxies = settings.getlist("PROXY_LIST")
        self.dead_proxies = set()


    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def get_proxy(self):

        available = [
            proxy
            for proxy in self.proxies
            if proxy not in self.dead_proxies
        ]

        if not available:
            raise ValueError("No healthy proxies remaining.")

        return random.choice(available)

    def get_user_agent(self):
        return random.choice(self.USER_AGENTS)

    def process_request(self, request, spider):

        if "proxy" not in request.meta:
            request.meta["proxy"] = self.get_proxy()

        request.headers["User-Agent"] = self.get_user_agent()

        request.headers.setdefault(
            "Accept",
            "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        )

        request.headers.setdefault(
            "Accept-Language",
            "en-US,en;q=0.9",
        )

        return None

    def process_response(self, request, response, spider):

        if response.status not in self.RETRY_STATUSES:
            return response

        retries = request.meta.get("proxy_retry", 0)

        if retries >= self.max_retries:

            spider.logger.error(
                "Maximum retries reached for %s",
                request.url,
            )

            return response

        bad_proxy = request.meta.get("proxy")

        if bad_proxy:
            self.dead_proxies.add(bad_proxy)

        delay = 2 ** retries

        spider.logger.warning(
            "Blocked (%s). Retry %d after %d sec.",
            response.status,
            retries + 1,
            delay,
        )

        time.sleep(delay)

        new_request = request.copy()

        new_request.dont_filter = True

        new_request.meta["proxy_retry"] = retries + 1

        new_request.meta.pop("proxy", None)

        new_request.headers["User-Agent"] = self.get_user_agent()

        return new_request

    def process_exception(self, request, exception, spider):

        retries = request.meta.get("proxy_retry", 0)

        if retries >= self.max_retries:
            return None

        bad_proxy = request.meta.get("proxy")

        if bad_proxy:
            self.dead_proxies.add(bad_proxy)

        delay = 2 ** retries

        spider.logger.warning(
            "Network error (%s). Retry %d after %d sec.",
            exception,
            retries + 1,
            delay,
        )

        time.sleep(delay)

        new_request = request.copy()

        new_request.dont_filter = True

        new_request.meta["proxy_retry"] = retries + 1

        new_request.meta.pop("proxy", None)

        new_request.headers["User-Agent"] = self.get_user_agent()

        return new_request