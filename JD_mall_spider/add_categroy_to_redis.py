"""
1.在项目文件下创建add_category_to_redis.py
2.实现方法 add_category_to_redis:
    1.连接MongoDB
    2.连接Redis
    3.读取MongoDB中分类信息，序列化后，添加到商品爬虫redis_key指定的List
    4.关闭MongoDB
3.在if __name__ == '__main__':中调用add_category_to_redis方法

"""
from pymongo import MongoClient
from redis import StrictRedis
import pickle
from JD_mall_spider.settings import MONGODB_URL,REDIS_URL
from JD_mall_spider.spiders.jd_product import JdProductSpider

def add_category_to_redis():
    #1.连接MongoDB
    mongo = MongoClient(MONGODB_URL)
    #2.连接Redis
    redis = StrictRedis.from_url(REDIS_URL)
    #3.读取MongoDB中分类信息，序列化后，添加到商品爬虫redis_key指定的List
    #获取MongoDB中分类的集合
    collection = mongo['jd']['category']
    #读取分类信息
    cursor = collection.find()
    for category in cursor:
        #序列化字典数据
        data = pickle.dumps(category)
        #添加到商品爬虫redis_key指定的list
        redis.lpush(JdProductSpider.redis_key,data)

    #4.关闭MongoDB
    mongo.close()

if __name__ == '__main__':
    add_category_to_redis()
