import csv
import os
from scrapy.exceptions import DropItem
from scrapy import signals
from .items import SeriesItem


class DeduplicationPipeline:

    def __init__(self, csv_file_path):
        self.seen_urls = set()
        self.csv_file_path = csv_file_path

        # Load seen URLs from CSV if it exists
        if os.path.exists(self.csv_file_path):
            with open(self.csv_file_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader, None) # Skip header row
                if header:
                    # Assuming 'title' is the first column, which is used for deduplication
                    # Adjust index if 'title' is not the first column in your CSV
                    title_column_index = list(SeriesItem.fields.keys()).index('title') if 'title' in SeriesItem.fields else 0
                    for row in reader:
                        if len(row) > title_column_index:
                            self.seen_urls.add(row[title_column_index])
            print(f"Loaded {len(self.seen_urls)} URLs from {self.csv_file_path} for deduplication.")

    @classmethod
    def from_crawler(cls, crawler):
        csv_file_path = crawler.settings.get('CSV_FILE_PATH', 'scraped_results.csv')
        return cls(csv_file_path)

    def process_item(self, item, spider):
        url = item.get('url')
        if url in self.seen_urls:
            raise DropItem(f"Duplicate signature detected and blocked: {url}")

        self.seen_urls.add(url)
        return item


class CleanAndFormattingPipeline:
    def process_item(self, item, spider):
        # Standardizes all fields, stripping whitespace or enforcing defaults
        for field in item.fields:
            item.setdefault(field, "N/A")
            if isinstance(item[field], str):
                item[field] = item[field].strip()

        return item


class CsvExportPipeline:
    def __init__(self, csv_file_path):
        self.file = None
        self.writer = None
        self.file_path = csv_file_path

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls(crawler.settings.get('CSV_FILE_PATH', 'scraped_results.csv'))
        crawler.signals.connect(pipeline.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signal=signals.spider_closed)
        return pipeline

    def spider_opened(self, spider):
        # Check if file exists to determine if header needs to be written
        self.file = open(self.file_path, 'a+', newline='', encoding='utf-8')
        self.writer = csv.writer(self.file)

        # Write header only if the file is empty
        if os.stat(self.file_path).st_size == 0:
            # Get field names from the SeriesItem definition
            self.writer.writerow(SeriesItem.fields.keys())

    def spider_closed(self, spider):
        if self.file:
            self.file.close()

    def process_item(self, item, spider):
        if self.writer:
            self.writer.writerow(item.values())
        return item