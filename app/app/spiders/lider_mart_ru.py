import scrapy
from scrapy.http import JsonRequest

from app.items import Product

class LiderMartRuSpider(scrapy.Spider):
    name = 'lider-mart.ru'
    allowed_domains = ['lider-mart.ru']

    def start_requests(self):
        url = 'https://www.lider-mart.ru/sitemap.xml'
        yield scrapy.Request(url, callback=self.parse_sitemap)

    def parse_sitemap(self, response):
        response.selector.remove_namespaces()

        for product_url in response.xpath('//url/loc/text()').getall()[:3]:
            yield scrapy.Request(product_url, callback=self.parse_product)

    def parse_description_table(self, response):
        table = {}
        for tr in table_selector.css('.product_description table.description tr'):
            key = tr.css('.description_left div::text').get().strip()
            val = tr.css('.description_right div::text').get()

            if isinstance(val, str):
                table[key] = val.strip()
        return table

    def parse_barcode(self, response, product):
        product['barcode'] = response.json()['BarCode']

        yield product

    def parse_product(self, response):
        p = Product()

        p['title'] = response.css('.product_description h1.title').get()
        p['price'] = response.css('.product_description [itemprop="price"]::text').get()
        p['currency'] = response.css('meta[itemprop=priceCurrency]::attr(content)').get()

        source = response.url

        product_id = response.css('#dataEncryptionProductID::attr(value)').get()
        encryption_key = response.css('#dataEncryptionKey::attr(value)').get()

        curl_command = (
            "curl 'https://www.lider-mart.ru/Product/GetDataEncryption/' "
            "-H 'Content-Type: application/x-www-form-urlencoded; charset=UTF-8' "
           f"--data-raw 'dataEncryptionKey={encryption_key}&productID={product_id}' "
        )

        yield scrapy.Request.from_curl(curl_command, callback=self.parse_barcode, 
                                       cb_kwargs=dict(product=p), meta={'dont_redirect': True})