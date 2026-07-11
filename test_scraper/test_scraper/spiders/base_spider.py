import scrapy

class BaseUniversalSpider(scrapy.Spider):
    """
    Every future spider will inherit from this base.
    It forces standardization across all target targets.
    """
    name = "base_universal"
    allowed_domains = []
    start_urls = []

    def __init__(self, *args, **kwargs):
        super(BaseUniversalSpider, self).__init__(*args, **kwargs)
        if not self.name or self.name == "base_universal":
            raise ValueError("Every distinct crawler must override the 'name' attribute.")