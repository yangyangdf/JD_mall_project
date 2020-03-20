# -*- coding: utf-8 -*-
import scrapy
from JD_mall_spider.items import Product
import json
from jsonpath import jsonpath
from scrapy_redis.spiders import RedisSpider
import pickle


#修改继承关系，继承RedisSpider
class JdProductSpider(RedisSpider):
    name = 'jd_product'
    allowed_domains = ['jd.com','3.cn']
    # start_urls = ['http://jd.com/']
    # 指定redis_key，用于指定起始URL列表，在Redis数据库中key
    redis_key = 'jd_product:categroy'

    #把重写start_requests,改成make_request_from_data

    # def start_requests(self):
    #     """重写start_request方法，根据分类信息构建列表页的请求"""
    #     category = { "b_category_name" : "家用电器",
    #                  "b_category_url" : "https://jiadian.jd.com",
    #                  "m_category_name" : "洗衣机",
    #                  "m_category_url" : "https://list.jd.com/list.html?cat=737,794,880",
    #                  "s_category_name" : "迷你洗衣机",
    #                  "s_category_url" : "https://list.jd.com/list.html?cat=737,794,880&ev=998_77402&JL=3_%E4%BA%A7%E5%93%81%E7%B1%BB%E5%9E%8B_%E8%BF%B7%E4%BD%A0%E6%B4%97%E8%A1%A3%E6%9C%BA#J_crumbsBar"}
    #
    #     #根据小分类的URL，构建列表页的请求
    #     yield scrapy.Request(category['s_category_url'],callback=self.parse,meta={'category':category})

    def make_request_from_data(self, data):
        """
        根据redis中读取的分类信息的二进制数据，构建请求
        :param data: 分类信息的二进制数据
        :return: 根据小分类URL，构建的请求对象
        """
        #把分类信息的二进制数据转化为字典
        category = pickle.loads(data)

        # 根据小分类的URL，构建列表页的请求
        return scrapy.Request(category['s_category_url'],callback=self.parse,meta={'category':category})

    def parse(self, response):
        category = response.meta['category']
        # print(category)
        #解析列表页，提取商品的skuid
        sku_ids = response.xpath('//div[contains(@class,"j-sku-item")]/@data-sku').extract()
        for sku_id in sku_ids:
            #创建Product,用于保存商品数据
            item = Product()
            #设置商品类别
            item['product_category'] = category
            item['product_sku_id'] = sku_id
            #构建商品基本的信息请求
            product_base_url = 'https://cdnware.m.jd.com/c1/skuDetail/apple/7.3.0/{}.json'.format(sku_id)
            yield scrapy.Request(product_base_url,callback=self.parse_product_base,meta={'item':item})

        #获取下一页的URL
        next_url = response.xpath('//a[@class="pn-next"]/@href').extract_first()
        if next_url:
            #补全url
            next_url = response.urljoin(next_url)
            # print(next_url)
            #构建下一页的请求
            yield scrapy.Request(next_url,callback=self.parse,meta={'category':category})


    def parse_product_base(self,response):
        item = response.meta['item']
        # print(item)
        # print(response.text)
        #把json字符串，转化成字典
        result = json.loads(response.text)
        #提取数据
        #product_name        商品名称
        # product_img_url     商品图片url
        # product_book_info   图书信息，作者，出版社
        # product_option      商品选项
        # product_shop        商品店铺
        item['product_name'] = result['wareInfo']['basicInfo']['name']
        item['product_img_url'] = result['wareInfo']['basicInfo']['wareImage'][0]['small']
        item['product_book_info'] = result['wareInfo']['basicInfo']['bookInfo']
        color_size = jsonpath(result,'$..colorSize')
        if color_size:
            #注意colorsize值是列表，而jsonpath返回列表，color_size是两层列表
            color_size = color_size[0]
            product_option = {}
            for option in color_size:
                title = option['title']
                value = jsonpath(option,'$..text')
                product_option[title] = value

            item['product_option'] = product_option
        shop = jsonpath(result,'$..shop')
        if shop:
            shop = shop[0]
            if shop:
                item['product_shop'] = {
                    "shopId":shop['shopId'],
                    "shop_name":shop['name'],
                    "shop_score":shop['score']
                }
            else:
                item['product_shop'] = {
                    "shop_name": "京东自营",
                }

        item['product_category_id'] = result['wareInfo']['basicInfo']['category']
        #category:需要将';'改成','
        item['product_category_id'] = item['product_category_id'].replace(';',',')
        # print(item)
        #准备出校信息的URL
        ad_url = "https://cd.jd.com/promotion/v2?skuId={}&area=17_1381_50712_50817&cat={}"\
        .format(item['product_sku_id'],item['product_category_id'])
        yield scrapy.Request(ad_url,callback=self.parse_product_ad,meta={'item':item})

    def parse_product_ad(self,response):
        item = response.meta['item']
        # print(item)
        # print(response.text)
        #把数据转化成字典
        result = json.loads(response.text)
        item['product_ad'] = jsonpath(result,'$..ad')[0] if jsonpath(result,'$..ad')[0] else ''
        # print(item)
        comment_url = 'https://club.jd.com/comment/productCommentSummaries.action?referenceIds={}'\
            .format(item['product_sku_id'])

        yield scrapy.Request(comment_url,callback=self.parse_product_comments,meta={'item':item})

    def parse_product_comments(self,response):
        item = response.meta['item']
        result = json.loads(response.text)
        item['product_comments'] = {
            'CommentCount':result['CommentsCount'][0]['CommentCount'],
            'GoodCount':result['CommentsCount'][0]['GoodCount'],
            'PoorCount':result['CommentsCount'][0]['PoorCount'],
            'GoodRate':result['CommentsCount'][0]['GoodRate']
        }
        #构建价格请求
        price_url = 'https://p.3.cn/prices/mgets?skuIds=J_{}'.format(item['product_sku_id'])
        yield scrapy.Request(price_url,callback=self.parse_product_price,meta={'item':item})


    def parse_product_price(self,response):
        item = response.meta['item']
        # print(response.text)
        result = json.loads(response.text)
        item['product_price'] = result[0]['p']
        #把商品数据交给引擎
        yield item
