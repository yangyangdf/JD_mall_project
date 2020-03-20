# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

"""
实现保存分类的Pipeline类
-open_spider方法中，连接MongoDB数据库，获取要操作的集合
-process_item方法中，向MongoDB中插入类到数据
-close_spider 方法中，关闭MongoDB的连接
"""
from pymongo import MongoClient
from JD_mall_spider.spiders.jd_category import MallSpiderSpider
from JD_mall_spider.spiders.jd_product import JdProductSpider
from JD_mall_spider.settings import MONGODB_URL

class CategoryPipeline(object):

    def open_spider(self,spider):
        """当爬虫启动的时候执行"""
        if isinstance(spider,MallSpiderSpider):
            self.client = MongoClient(MONGODB_URL)
            self.collection = self.client['jd']['category']

    def process_item(self, item, spider):
        if isinstance(spider, MallSpiderSpider):
            self.collection.insert(dict(item))

        return item

    def close_spider(self,spider):
        if isinstance(spider, MallSpiderSpider):
            self.client.close()


"""
实现存储商品的Pipeline类
-open_spider方法中，连接MongoDB数据库，获取要操作的集合
-process_item方法中，向MongoDB中插入类到数据
-close_spider 方法中，关闭MongoDB的连接
"""



class JdproductPipeline(object):

    def open_spider(self,spider):
        """当爬虫启动的时候执行"""
        if isinstance(spider,JdProductSpider):
            self.client = MongoClient(MONGODB_URL)
            self.collection = self.client['jd']['product']

    def process_item(self, item, spider):
        if isinstance(spider, JdProductSpider):
            self.collection.insert(dict(item))

        return item

    def close_spider(self,spider):
        if isinstance(spider, JdProductSpider):
            self.client.close()