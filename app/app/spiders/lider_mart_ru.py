import scrapy
from scrapy.http import JsonRequest

from htmllaundry import strip_markup

from app.items import Product

class LiderMartRuSpider(scrapy.Spider):
    name = 'lider-mart.ru'
    allowed_domains = ['lider-mart.ru']

    def start_requests(self):
        category_ids = [1106, 2481]
        sesderma_group_id = 5667

        for category_id in category_ids:
            yield self.ajax_query_show_more_products(category_id=category_id, group_id=sesderma_group_id, page=0)

    def ajax_query_show_more_products(self, category_id, group_id, page):
        url = 'https://www.lider-mart.ru/Category/GetProducts/'

        headers = {
            "Host": "www.lider-mart.ru",
            "Connection": "keep-alive",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": "https://www.lider-mart.ru",
            "Referer": "https://www.lider-mart.ru/category/641",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
        }

        body = f"page={page}&orderName=NameAscending&groupName=NotGroup&filterGroupID={group_id}&filterMinPrice=&filterMaxPrice=&filterMinVolume=&filterMaxVolume=&categoryID={category_id}"

        return scrapy.Request(
            url=url,
            method='POST',
            dont_filter=False,
            headers=headers,
            body=body,
            meta={'dont_redirect': True},
            cb_kwargs={'page': page, 'group_id': group_id, 'category_id': category_id},
            callback=self.parse_show_more_product_response
        )


    def parse_show_more_product_response(self, response, category_id, group_id, page):
        json_response = response.json()

        if 'ProductsAndSliderLineByGroup' in json_response:
            yield self.ajax_query_show_more_products(category_id, group_id, page+1)

            for product_group in json_response['ProductsAndSliderLineByGroup']:
                group = product_group.get('ProductsAndSliderLine', {})
                for product in group.get('Products', []):
                    try:
                        product_id = product['ProductId']
                        product_url = f'https://www.lider-mart.ru/product/{product_id}'

                        yield scrapy.Request(product_url, callback=self.parse_product)
                    except KeyError:
                        continue


    def parse_sitemap(self, response):
        response.selector.remove_namespaces()

        for product_url in response.xpath('//url/loc/text()').getall()[:3]:
            yield scrapy.Request(product_url, callback=self.parse_product)

    def parse_description_table(self, response):
        table = {}
        for tr in response.css('.product_description table.description tr'):
            key = strip_markup(tr.css('.description_left').get())
            val = strip_markup(tr.css('.description_right').get())

            if isinstance(val, str):
                table[key] = val.strip()
        return table

    def parse_text_under_tabs(self, response):
        tabs = response.css('.product_description_full .title li::text').getall()

        table = {}
        for idx, tab in enumerate(tabs):
            description = response.css(f'.product_description_full #description_{idx+1}').get()
            table[tab] = strip_markup(description)
        return table

    def parse_product(self, response):
        try:
            description = self.parse_description_table(response)
        except:
            description = {}
        
        try:
            tabs = self.parse_text_under_tabs(response)
        except:
            tabs = {}

        p = Product()
        p['volume'] = description.get('Объём:', None)
        p['weight'] = description.get('Вес:', None)
        p['product_line'] = response.css('.patch .patch_el a::text')[-1].get()
        p['composition'] = tabs.get('Состав', None)

        p['title'] = response.css('.product_description h1.title::text').get()
        p['price'] = response.css('.product_description [itemprop="price"]::text').get()
        p['currency'] = response.css('meta[itemprop=priceCurrency]::attr(content)').get()

        p['source'] = response.url
        p['images'] = set(response.css('.product_image a[rel="picture"]::attr(href)').getall())

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
        json_response = response.json()

        product['barcode'] = json_response.get('BarCode', None)
        product['article'] = json_response.get('Article', None)

        yield product