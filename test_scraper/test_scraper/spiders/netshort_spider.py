from pip._internal.req import req_install

from ..items import SeriesItem
from .base_spider import BaseUniversalSpider
import scrapy
import json
from scrapy.utils.defer import deferred_from_coro
from scrapy_playwright.handler import ScrapyPlaywrightDownloadHandler # Import the handler

class NetShortSpider(BaseUniversalSpider):
    name = "netshort"
    allowed_domains = ["netshort.com"]
    start_urls = ["https://netshort.com/drama/all-plots"]

    def start_requests(self): # Made start_requests async

        for url in self.start_urls:
            request = scrapy.Request(
                url,
                callback=self.parse,
                meta={
                    "playwright": False,
                },
                priority=100
            )
            yield request

    def parse(self, response):
        # Extract series cards dynamically from the directory catalog
        series_cards = response.css('div.drama-item-card, a[href*="/episode"]')

        for card in series_cards:
            relative_url = card.css('a::attr(href)').get()
            if relative_url:
                detail_url = response.urljoin(relative_url)
                yield scrapy.Request(
                    detail_url,
                    callback=self.parse_details,
                    meta={
                        "playwright": False,
                    }
                )
        nav = [i.get() for i in response.xpath('//nav/div/span/text()')]
        if nav:
            if nav[0].isdigit() and nav[-1].isdigit():
                if int(nav[0]) <= int(nav[-1]):
                    next_page = "https://netshort.com/drama/all-plots/page/" + str(int(nav[0]) + 1)
                    yield scrapy.Request(
                        next_page,
                        callback=self.parse,
                        meta={
                            "playwright": False,
                        }
                    )
                else:
                    self.logger.info("No more pages to scrape.")
                    return
            else:
                self.logger.warning("Pagination numbers are not valid integers.")
                return
        else:
            self.logger.warning("No pagination found, stopping.")
            return


    def parse_details(self, response):
        item = SeriesItem()
        # 1. Extract JSON-LD
        json_ld_script = response.css('script[type="application/ld+json"]::text').get()
        if not json_ld_script:
            self.logger.warning(f"No JSON-LD found on {response.url}")
                
        if json_ld_script:
            try:
                data = json.loads(json_ld_script)
                series_data = None
                if '@graph' in data:
                    for obj in data['@graph']:
                        if obj.get('@type') == 'TVSeries':
                            series_data = obj
                else: # Handle cases where it might not be an @graph, but a single object
                    if data.get('@type') == 'TVSeries':
                        series_data = data
                # Prioritize episode data if available, otherwise use series data
                if series_data:
                    item['title'] = series_data.get('name')
                    item['series_url'] = series_data.get('url') or response.url
                    item['cover_image_url'] = series_data.get('image') or series_data.get('thumbnailUrl')
                    item['description'] = " ".join([i.get() for i in response.xpath('//h2/following-sibling::div/div/text()')])
                    genre_data = series_data.get('genre')
                    if isinstance(genre_data, str):
                        item['genre'] = [genre_data]
                    elif isinstance(genre_data, list):
                        item['genre'] = genre_data
                    else:
                        item['genre'] = [] # Default to empty list if not found or unexpected type

                    item['episodes_count'] = series_data.get('numberOfEpisodes')

            except json.JSONDecodeError:
                self.logger.warning(f"Could not decode JSON-LD from {response.url}")
        else:
            self.logger.warning(f"No JSON-LD script found on {response.url}")
        yield item