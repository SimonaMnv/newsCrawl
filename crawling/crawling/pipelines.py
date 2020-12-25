from bson.objectid import ObjectId
from api.models.article_model import ArticleOfInterest
import re
import hashlib


class DjangoPipeline(object):
    collection_name = 'scrapy_articles'

    def process_item(self, item, spider):
        body = item["body"]
        junkyard = ["Ειδήσεις από την Ελλάδα", "Διαβάστε ΕΔΩ περισσότερα", "Πηγή", "Διαβάστε επίσης"]
        recycled_body = [[re.search("(?:(?!" + junk + ").)*", body).group() for junk in junkyard]]

        hashed_id = hashlib.md5(item["link"].encode()).hexdigest()

        article = ArticleOfInterest(_id=ObjectId(hashed_id[:24]), title=item["title"], date=item["date"],
                                    body=min(recycled_body[0], key=len), tags=item["tags"], author=item["author"],
                                    link=item["link"])
        article.save()
        return item
