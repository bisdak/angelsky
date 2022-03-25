from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from app.spiders.lider_mart_ru import LiderMartRuSpider
#from app.spiders.krasota3_ru import Krasota3RuSpider

process = CrawlerProcess(get_project_settings())
process.crawl(LiderMartRuSpider)
#process.crawl(Krasota3RuSpider)
process.start()