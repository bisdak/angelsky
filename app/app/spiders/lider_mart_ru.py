import scrapy
from scrapy.http import JsonRequest

from htmllaundry import strip_markup

from app.items import Product

class LiderMartRuSpider(scrapy.Spider):
    name = 'lider-mart.ru'
    allowed_domains = ['lider-mart.ru']

    def start_requests(self):
        url = 'https://www.lider-mart.ru/sitemap.xml'
        yield scrapy.Request(url, callback=self.parse_sitemap)

    def parse_sitemap(self, response):
        response.selector.remove_namespaces()

        for product_url in response.xpath('//url/loc/text()').getall()[:100]:
            yield scrapy.Request(product_url, callback=self.parse_product)

    def parse_description_table(self, response):
        table = {}
        for tr in response.css('.product_description table.description tr'):
            key = tr.css('.description_left div::text').get().strip()
            val = tr.css('.description_right div::text').get()

            if isinstance(val, str):
                table[key] = val.strip()
        return table

    def parse_description_under_tabs(self, response):
        tabs = response.css('.product_description_full .title li::text').getall()

        table = {}
        for idx, tab in enumerate(tabs):
            description = response.css(f'.product_description_full #description_{idx+1}').get()
            table[tab] = strip_markup(description)
        return table

    def parse_product(self, response):
        description = self.parse_description_table(response)
        tabs = self.parse_description_under_tabs(response)

        p = Product()
        p['volume'] = description.get('Объём:', None)
        p['weight'] = description.get('Вес:', None)
        p['product_line'] = description.get('Бренд:', None) or description.get('Производитель:', None)
        p['composition'] = tabs.get('Состав', None)

        p['title'] = response.css('.product_description h1.title::text').get()
        p['price'] = response.css('.product_description [itemprop="price"]::text').get()
        p['currency'] = response.css('meta[itemprop=priceCurrency]::attr(content)').get()

        p['source'] = response.url

        product_id = response.css('#dataEncryptionProductID::attr(value)').get()
        encryption_key = response.css('#dataEncryptionKey::attr(value)').get()

        curl_command = (
            "curl 'https://www.lider-mart.ru/Product/GetDataEncryption/' "
            "-H 'Content-Type: application/x-www-form-urlencoded; charset=UTF-8' "
           f"--data-raw 'dataEncryptionKey={encryption_key}&productID={product_id}' "
        )

        yield scrapy.Request.from_curl(curl_command, callback=self.parse_barcode, 
                                       cb_kwargs=dict(product=p), meta={'dont_redirect': True})

    def parse_barcode(self, response, product):
        json = response.json()

        product['barcode'] = json.get('Barcode', None)
        product['article'] = json.get('Article', None)

        yield product