# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import logging
import pymongo 

class MongodbPipline:

    mongourl = "mongodb+srv://amr:amramr@cluster0.iup4q.mongodb.net/IMDB_DB?retryWrites=true&w=majority"
    
    def open_spider(self, spider):
        logging.warning("SPIDER OPENED PIPELINE")
        self.client = pymongo.MongoClient(self.mongourl)
        self.db = self.client['amz_top']
        

    def close_spider(self, spider):
        logging.warning("SPIDER CLOSED PIPELINE")
        self.client.close()


    def process_item(self, item, spider):
        logging.warning("SPIDER itemPIPELINE")
        self.db[spider.settings.get('COLLECTION_NAME')].insert(item)
        return item
