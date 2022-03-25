import scrapy
from app.items import Product


class Krasota3RuSpider(scrapy.Spider):
    name = 'krasota3.ru'
    domain = 'https://krasota3.ru/'
    allowed_domains = ['krasota3.ru']
    start_urls = ['https://krasota3.ru/kosmetika-gigi-kupit/']


    def parse(self, response):
        import ipdb; ipdb.set_trace()
        for category_link in response.css('.product a::attr(href)').getall():
            yield scrapy.Request(response.urljoin(category_link), callback=self.parse_category)

        # next_page = response.css('[rel="next"] link::attr(href)').get()
        
        # if next_page:
        #     yield scrapy.Request(next_page, callback=self.parse, dont_filter=True)


    def parse_category(self, response):
        product_links = response.css('.product-name::attr(href)').getall()

        for product_link in product_links:
            yield scrapy.Request(response.urljoin(product_url), callback=self.parse_product)


    def parse_product(self, response):
        p = Product()

        p['article'] = response.css('.acticul span::text').get()
        p['title'] = response.css('h1.heading::text').get()
        p['product_line'] = response.css('.breadcrumb li span[itemprop=name]::text').getall()[-2]

        p['images'] = self.domain + response.css('#image-block .img-responsive::attr(src)').get()

        p['barcode'] = None
        p['composition'] = None
        p['source'] = response.url
        p['currency'] = None

        description_titles = response.css('.text-content h2::text')
        for idx, title in enumerate(description_titles):
            words = title.re('[а-яА-Я]+')
            words = list(map(lambda w: w.lower(), words))

            if 'состав' in words:
                try:
                    p['composition'] = response.css('.text-content p::text').getall()[idx]
                except IndexError:
                    pass

        p['weight'] = None
        for label in response.css('.form-group .flex label'):
            p['price'] = label.css('span::text').get()
            p['volume'] = label.css(':not(span) *::text').getall()[-1].strip()

            import ipdb; ipdb.set_trace()
            yield p
