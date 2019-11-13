#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: hao 2019/11/9-17:40
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from selenium import webdriver
from pymongo import MongoClient


class LianJia:
    def __init__(self, part=None, page=1):
        self.executor = ThreadPoolExecutor(max_workers=2)  # 使用内置线程池, 设置最大线程数

        # 声明Chrome浏览器对象
        self.driver = webdriver.Chrome(r'E:\I want something just like this\spider\webdriver\chromedriver.exe')
        self.driver2 = webdriver.Chrome(r'E:\I want something just like this\spider\webdriver\chromedriver.exe')
        self.driver3 = webdriver.Chrome(r'E:\I want something just like this\spider\webdriver\chromedriver.exe')
        self.part = part  # 代表要爬取的城区
        self.page = page  # 代表你要爬取多少页,这里指的是每个城区爬取多少页，默认为1页

        # 声明数据库对象
        self.client = MongoClient(host="localhost", port=27017)
        self.db = self.client.LianJia
        self.collection = self.db.houseInfo

    @staticmethod   # 因为没有引入类中的变量, 所以建议写成静态方法
    def write_item_to_json(item):
        """写入json文件"""
        # 将item字典转换为json格式, ensure_ascii为否, 表示返回值可以包含非ascii值, 比如汉字
        json_data = json.dumps(item, ensure_ascii=False)
        # a表示每次写入为追加, encoding是为了不让中文乱码
        with open('data.json', 'a', encoding='utf-8') as f:
            # 执行写入, 尾部追加换行符
            f.write(json_data + '\n')
        print(f'>>>[{item["title"]}]写入成功')

    @staticmethod
    def clock(obj):
        """返回当前的时间，与对象组成字典"""
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return {now: obj}

    def write_item_to_mongo(self, item):
        """插入item到数据库"""
        self.collection.insert_one(item)
        print(f'>>>[{item["title"]}]写入成功')

    def house_detail(self, item, url, driver):
        """获取一间房子的详情信息"""
        driver.get(url)  # 访问一间房子的详情页
        # 获取页面上的房子信息
        item['houseURL'] = url
        item['title'] = driver.find_element_by_tag_name('h1').text  # 标题
        price = driver.find_element_by_css_selector('span.total').text  # 价格
        first_price = self.clock(price)  # 第一次的价格
        item['price'] = [first_price]  # 房子的价格与更新日期
        house_info = driver.find_elements_by_css_selector('div.mainInfo')
        item['room'] = house_info[0].text  # 户型
        item['faceTo'] = house_info[1].text  # 朝向
        item['area'] = house_info[2].text  # 面积
        # 小区名
        item['communityName'] = driver.find_element_by_css_selector('div.communityName a.info').text
        # 发布日期
        item['releaseDate'] = driver.find_element_by_xpath('//div[@class="transaction"]/div[2]/ul/li/span[2]').text
        self.write_item_to_json(item)

    def asyn_page(self, item, url_list):
        """异步处理线程， 让两个driver同时访问不同的页面"""
        self.executor.submit(self.house_detail, item=dict(item), url=url_list[0], driver=self.driver2)
        self.executor.submit(self.house_detail, item=dict(item), url=url_list[1], driver=self.driver3)

    def house_list(self, item):
        """获取一个城区中所有房子的详情页链接"""
        for page in range(1, self.page + 1):
            self.driver.get(item['partURL'] + f'pg{page}co32/')  # 访问城区的页面
            # 获取到所有的房子链接
            house_ls = self.driver.find_elements_by_xpath('//ul[@class="sellListContent"]//div[@class="title"]/a')
            # 生成url列表
            house_url_ls = [house.get_attribute("href") for house in house_ls]
            # 循环内的作用， 同时给url_list参数提供两个不同的值
            for i in range(0, len(house_url_ls), 2):
                if i < len(house_url_ls) - 1:
                    self.asyn_page(item=dict(item), url_list=[house_url_ls[i], house_url_ls[i + 1]])
            else:
                print(f'>>[{item["partName"]}]区，第[{page}]页--[Done]')
        else:
            print(f'>[{item["partName"]}]--[Done]')

    def run(self):
        """获取所有城区的页面链接"""
        # 访问二手房网址
        self.driver.get('https://wh.lianjia.com/ershoufang/')
        # 获取所有城区的元素对象
        temp_ls = self.driver.find_elements_by_xpath('//div[@class="position"]/dl[2]/dd/div[1]/div/a')
        if self.part:
            self.get_one_part(temp_ls, self.part)
        else:
            self.get_all_part(temp_ls)
        # 城区名和url组成键值对

    def get_one_part(self, temp_ls, part):
        """获取一个城区的房子"""
        part_dict = {ele.text: ele.get_attribute("href") for ele in temp_ls}
        try:
            # 初始化一个容器, 用来存放房子的信息
            item = {'partName': part, 'partURL': part_dict[part]}
            self.house_list(dict(item))  # 传递深拷贝的item对象
        except KeyError:
            print(f'请指定有效的城区名, 如下：\n{list(part_dict.keys())}')

    def get_all_part(self, temp_ls):
        """获取所有城区的房子"""
        # 城区名 集
        part_name_ls = [ele.text for ele in temp_ls]
        # 城区链接 集
        part_url_ls = [ele.get_attribute("href") for ele in temp_ls]
        item = {}  # 初始化一个容器, 用来存放房子的信息
        for i in range(len(temp_ls)):
            item['partName'] = part_name_ls[i]  # 城区名
            item['partURL'] = part_url_ls[i]  # 城区页面链接
            self.house_list(dict(item))  # 传递深拷贝的item对象

    def __del__(self):
        self.driver.close()  # 关闭浏览器1
        self.driver2.close()  # 关闭浏览器2
        self.driver3.close()  # 关闭浏览器3
        print('>>>>[Well Done]')

if __name__ == '__main__':
    lj = LianJia(part='江岸', page=1)
    lj.run()
