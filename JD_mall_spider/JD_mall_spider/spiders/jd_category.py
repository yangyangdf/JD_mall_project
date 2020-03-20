# -*- coding: utf-8 -*-
import scrapy
import json
import re
from JD_mall_spider.items import Category,Product


class MallSpiderSpider(scrapy.Spider):
    name = 'jd_category'
    allowed_domains = ['3.cn']
    start_urls = ['https://dc.3.cn/category/get?&callback=getCategoryCallbac']

    def parse(self, response):

        content = response.body.decode('gbk')
        data = re.findall(r'getCategoryCallbac\((.*)\)',content)[0]
        result = json.loads(data)

        datas = result['data']
        #遍历数据列表
        for data in datas:
            item = Category()
            b_category = data['s'][0]
            b_category_info = b_category['n']
            # print('大分类:{}'.format(b_category_info))
            item['b_category_name'],item['b_category_url'] = self.get_category_name_url(b_category_info)

            #中分类信息列表
            m_category_s = b_category['s']
            #遍历中分类列表
            for m_category in m_category_s:
                #中分类信息
                m_category_info = m_category['n']
                # print('中分类：{}'.format(m_category_info))
                item['m_category_name'], item['m_category_url'] = self.get_category_name_url(m_category_info)

                #小分类数列表
                s_category_s = m_category['s']
                for s_category in s_category_s:
                    s_category_info = s_category['n']
                    # print('小分类：{}'.format(s_category_info))
                    item['s_category_name'], item['s_category_url'] = self.get_category_name_url(s_category_info)
                    #将数据交给引擎
                    yield item

    def get_category_name_url(self,category_info):
        """
        根据分类的信息提取名称和url
        :param category_info: 分类信息
        :return: 返回名称和url
        """
        category = category_info.split('|')
        #分类Url
        category_url = category[0]
        #分类名称
        category_name = category[1]

        #处理第一种分类URL
        if category_url.count('jd.com') == 1:
            #URL进行补全
            category_url = 'https://'+ category_url
        elif category_url.count('-') == 1:
            #xxxx-xxxx|计算机与互联网
            category_url = 'https://channel.jd.com/{}.html'.format(category_url)
        else:
            #xxxx-xxxx-xxxx
            #把url中的“-”替换成","
            category_url = category_url.replace('-',',')
            #补全url
            category_url = 'https://list.jd.com/list.html?cat={}'.format(category_url)
        #返回类别名称和url
        return category_name,category_url


