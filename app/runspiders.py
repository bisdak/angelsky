from scrapy.crawler import CrawlerProcess
from scrapy.spiderloader import SpiderLoader
from scrapy.utils.project import get_project_settings
from scrapy.utils import project


settings = project.get_project_settings()
spider_loader = SpiderLoader.from_settings(settings)
spiders = [spider_loader.load(name) for name in spider_loader.list()]

process = CrawlerProcess(settings)
for spider in spiders:
    if spider.__name__ == 'Krasota3RuSpider': continue
    process.crawl(spider)
process.start()