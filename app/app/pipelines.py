# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class AppPipeline:
    def __init__(self):
        self.generated_id = 0

    def process_item(self, item, spider):
        self.generated_id += 1

        item['generated_id'] = self.generated_id
        #item['images'] = '\n'.join(item['images'])
        return item
