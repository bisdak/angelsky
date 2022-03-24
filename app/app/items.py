import scrapy

class Product(scrapy.Item):
    generated_id = scrapy.Field()
    title = scrapy.Field()
    product_line = scrapy.Field()
    volume = scrapy.Field()
    weight = scrapy.Field()
    price = scrapy.Field()
    article = scrapy.Field()
    barcode = scrapy.Field()
    composition = scrapy.Field()
    photo = scrapy.Field()
    source = scrapy.Field()
    currency = scrapy.Field()
    product_id = scrapy.Field()
    encryption_key = scrapy.Field()
