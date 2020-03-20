# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JdMallSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass



class Category(scrapy.Item):
    """
    类别数据模型类：用于存储类别信息（Category）- 字段
    b_category_name: 大分类名称
    b_category_url: 大分类URL
    m_category_name: 中分类名称
    m_category_url: 中分类URL
    s_category_name: 小分类名称
    s_category_url: 小分类URL
    """
    b_category_name = scrapy.Field()
    b_category_url = scrapy.Field()
    m_category_name = scrapy.Field()
    m_category_url = scrapy.Field()
    s_category_name = scrapy.Field()
    s_category_url = scrapy.Field()


class Product(scrapy.Item):
    """
    商品数据模型类：用于存储商品信息（Product）
    product_category    商品类别
    product_sku_id      商品id
    product_name        商品名称
    product_img_url     商品图片url
    product_book_info   图书信息，作者，出版社
    product_option      商品选项
    product_shop        商品店铺
    product_comments    商品评论数量
    product_ad          商品促销
    product_price       商品价格
    """

    product_category = scrapy.Field()
    product_category_id = scrapy.Field()
    product_sku_id = scrapy.Field()
    product_name = scrapy.Field()
    product_img_url = scrapy.Field()
    product_book_info = scrapy.Field()
    product_option = scrapy.Field()
    product_shop = scrapy.Field()
    product_comments = scrapy.Field()
    product_ad = scrapy.Field()
    product_price = scrapy.Field()







