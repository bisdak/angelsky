import scrapy

class Product(scrapy.Item):
    name = scrapy.Field()
    product_line = scrapy.Field()
    volume = scrapy.Field()
    weight = scrapy.Field()
    price = scrapy.Field()
    article = scrapy.Field()
    barcode = scrapy.Field()
    composition = scrapy.Field()
    photo = scrapy.Field()
    source = scrapy.Field()
