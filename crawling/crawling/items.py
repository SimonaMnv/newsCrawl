# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy_djangoitem import DjangoItem
from api.models.article_model import ArticleOfInterest


class ArticleItem(DjangoItem):
    django_model = ArticleOfInterest
    title = scrapy.Field()
    date = scrapy.Field()
    body = scrapy.Field()
    tags = scrapy.Field()