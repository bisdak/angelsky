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
            "-H 'Connection: keep-alive' "
            "-H 'Pragma: no-cache' "
            "-H 'Cache-Control: no-cache' "
            "-H 'sec-ch-ua: \" Not;A Brand\";v=\"99\", \"Google Chrome\";v=\"91\", \"Chromium\";v=\"91\"' "
            "-H 'Accept: */*' "
            "-H 'X-Requested-With: XMLHttpRequest' "
            "-H 'sec-ch-ua-mobile: ?0' "
            "-H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36' "
            "-H 'Content-Type: application/x-www-form-urlencoded; charset=UTF-8' "
            "-H 'Origin: https://www.lider-mart.ru' "
            "-H 'Sec-Fetch-Site: same-origin' "
            "-H 'Sec-Fetch-Mode: cors' "
            "-H 'Sec-Fetch-Dest: empty' "
           f"-H 'Referer: ${source}' "
            "-H 'Accept-Language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7' "
            "-H 'Cookie: CodeBrowser=3F9708167EB13986C274DA4F26CC6D14; _gid=GA1.2.1523455674.1626008647; _ym_uid=162600864773720386; _ym_d=1626008647; _fbp=fb.1.1626008647643.389622410; _ym_isad=2; _ym_visorc=w; _ga_51FQ6Y1Z7J=GS1.1.1626011558.2.1.1626016725.60; _ga=GA1.2.757362236.1626008647; runid=5013CD59120786E652FBE0B660D5552D; userID=A46C3B54F2C9871CD81DAF7A932499C0' "
           f"--data-raw 'dataEncryptionKey={encryption_key}&productID={product_id}' "
            "--compressed"
        )

        yield scrapy.Request.from_curl(curl_command, callback=self.parse_barcode, 
                                       cb_kwargs=dict(product=p), meta={'dont_redirect': True})