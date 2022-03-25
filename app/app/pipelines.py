from itemadapter import ItemAdapter

import pymysql


class AppPipeline:
    def __init__(self):
        self.generated_id = 0

    def process_item(self, item, spider):
        self.generated_id += 1

        item['generated_id'] = self.generated_id
        #item['images'] = '\n'.join(item['images'])
        return item
