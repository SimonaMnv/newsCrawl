# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import sqlite3
from api.models.article_model import ArticleOfInterest


class DjangoPipeline(object):
    collection_name = 'scrapy_articles'

    def __init__(self):
        self.con = sqlite3.connect('../../db.sqlite3')  # Change this to your own directory
        self.cur = self.con.cursor()

    def process_item(self, item, spider):
        article = ArticleOfInterest(title=item["title"], date=item["date"], body=item["body"],
                                    tags=item["tags"], author=item["author"], link=item["link"])
        article.save()
        return item

    def close_spider(self, spider):
        try:
            self.con.commit()
        except:
            self.con.rollback()
            raise
        finally:
            self.con.close()
