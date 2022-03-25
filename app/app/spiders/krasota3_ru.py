import scrapy

class Krasota3RuSpider(scrapy.Spider):
    name = 'krasota3.ru'
    domain = 'https://krasota3.ru/'
    allowed_domains = ['krasota3.ru']
    start_urls = ['https://krasota3.ru/kosmetika-gigi-kupit/']


    def parse(self, response):
        for category_link in response.css('.product a::attr(href)').getall():
            yield scrapy.Request(response.urljoin(category_link), callback=self.parse_category)

        next_page = response.css('.page-item')[-2]
        is_diabled_button = bool(next_page.css('.disabled').get())
        if not is_diabled_button:
            next_page_link = self.domain + next_page.css('a::attr(href)').get()
            yield scrapy.Request(next_page_link, callback=self.parse, dont_filter=True)


    def parse_category(self, response):
        product_links = response.css('.product-name::attr(href)').getall()

        for product_link in product_links:
            yield scrapy.Request(product_url, callback=self.parse_product)


    def parse_product(self, response):
        pass