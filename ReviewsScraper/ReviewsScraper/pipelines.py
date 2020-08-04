# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from scrapy.exporters import CsvItemExporter
from csv import DictWriter


class HotelPipeline:
    @classmethod
    def from_crawler(cls, crawler):
        filename = crawler.settings.get('filename')
        return cls(filename)

    def __init__(self, filename):
        self.names_seen = set()
        self.fileName = filename

    def open_spider(self, spider):
        if spider.name == 'hotels':
            self.hotels_file = open(self.fileName, 'w')
            self.csvWrite = DictWriter(self.hotels_file, fieldnames=['name', 'stars', 'nbr_of_reviews', 'rating_score', 'rating_label', 'reviews_file', 'hotel_link'], delimiter='\t')
            self.csvWrite.writeheader()

    def close_spider(self, spider):
        if spider.name == 'hotels':
            self.hotels_file.close()

    def process_item(self, item, spider):
        if spider.name == 'reviews':
            pass
        else:
            adapter = ItemAdapter(item)
            if adapter['name'] in self.names_seen:
                raise DropItem("Hotel duplicate found: {}".format(adapter['name']))
            else:
                self.names_seen.add(adapter['name'])
                self.csvWrite.writerow(item)
                return item

class ReviewPipeline:
    @classmethod
    def from_crawler(cls, crawler):
        filename = crawler.settings.get('filename')
        return cls(filename)

    def __init__(self, filename):
        self.fileName = filename

    def writtenInArabic(self, itemAdapter):
        arabicPattern = compile(r'[\u0600-\u06FF]*')
        if arabicPattern.search(itemAdapter['positivePart']) == None and arabicPattern.search(itemAdapter['negativePart']) == None:
            return False
        else:
            return True

    def open_spider(self, spider):
        if spider.name == 'reviews':
            self.reviews_file = open(self.fileName, 'w')
            self.csvWrite = DictWriter(self.reviews_file, fieldnames=['username', 'nationality', 'personal_score', 'review_title', 'positive_part', 'negative_part'], delimiter='\t')
            self.csvWrite.writeheader()

    def close_spider(self, spider):
        if spider.name == 'reviews':
            self.reviews_file.close()

    def process_item(self, item, spider):
        if spider.name == 'hotels':
            return item
        else:
            adapter = ItemAdapter(item)
            if self.writtenInArabic(adapter):
                self.csvWrite.writerow(item)
                return item
            else:
                raise DropItem("user {} did not write in Arabic, item is dropped".format(adapter['userName']))
