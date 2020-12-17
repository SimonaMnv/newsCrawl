import scrapy


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
        title = response.css('h1::text').get()
        tags = response.xpath("//meta[@name='keywords']/@content")[0].extract()
        date = response.css('script::text').re(r'datePublished":"(.*?)T')
        body = response.css('script::text').re(r'articleBody":"(.*)')

        yield {
            'Title': title,
            'Date': date,
            'Tags': tags,
            'Body': body
        }

# 1. to scrape: go in crawling>crawling: scrapy crawl newsbomb
# 2. to check the html manually before parsing: scrapy shell > fetch(site) > print(response.text)
