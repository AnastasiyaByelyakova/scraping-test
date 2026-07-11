# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class SeriesItem(scrapy.Item):
    title = scrapy.Field()
    series_url = scrapy.Field()
    cover_image_url = scrapy.Field()
    description = scrapy.Field()
    genre = scrapy.Field()
    episodes_count = scrapy.Field()
    status = scrapy.Field()
    tags = scrapy.Field()