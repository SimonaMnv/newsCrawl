from crawling.items import ArticleItem
import scrapy
import json


class NewsbombSpider(scrapy.Spider):
    name = 'newsbomb'
    allowed_domains = ['newsbomb.gr']
    start_urls = ['https://www.newsbomb.gr/ellada/astynomiko-reportaz']

    def parse(self, response):
        article_links = response.css('a.overlay-link ::attr(href)')
        next_page = "https://newsbomb.gr/ellada/astynomiko-reportaz?page=" + str(
            int(response.css("span.nav-number::text").get()) + 1)

        for link in article_links:
            url = 'https://www.newsbomb.gr' + link.get()
            yield scrapy.Request(url=url, callback=self.parse_article)
        # if next_page:
        #     yield scrapy.Request(response.urljoin(next_page), callback=self.parse)

    def parse_article(self, response):
        data = json.loads(response.xpath('//script[@type="application/ld+json"]//text()').extract_first())
        article = ArticleItem()

        article['title'] = data["@graph"][0]["headline"]
        article['date'] = data["@graph"][0]["datePublished"]
        article['body'] = data["@graph"][0]["articleBody"]
        article['tags'] = data["@graph"][0]["keywords"]
        article['author'] = data["@graph"][0]["author"]['name']
        article['link'] = data["@graph"][0]["mainEntityOfPage"]["@id"]
        yield article


# 1. to scrape: go in crawling>crawling: scrapy crawl newsbomb
# 2. to check the html manually before parsing: scrapy shell > fetch(site) > print(response.text)
