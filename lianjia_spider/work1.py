#!/usr/bin/env python
#-*- coding: utf-8 -*-
# author: hao 2019/11/9-17:40
import time

from datetime import datetime
from selenium import webdriver
from pymongo import MongoClient
from concurrent.futures import ThreadPoolExecutor


class LianJia:
    def __init__(self, page):
        self.executor = ThreadPoolExecutor(max_workers=2)  # 直接使用内置线程池, 设置最大线程数

        # 声明Chrome浏览器对象
        self.driver = webdriver.Chrome(r'E:\Download\BaiduYunDownload\chromedriver_win32\chromedriver.exe')
        self.driver2 = webdriver.Chrome(r'E:\Download\BaiduYunDownload\chromedriver_win32\chromedriver.exe')
        self.driver3 = webdriver.Chrome(r'E:\Download\BaiduYunDownload\chromedriver_win32\chromedriver.exe')

        # 声明数据库对象
        self.client = MongoClient(host="localhost", port=27017)
        self.db = self.client.LianJia
        self.coll = self.db.houseInfo
        self.page = page    # 代表你要爬取多少页,这里指的是每个城区爬取多少页

    def write_item(self, item):
        # self.coll.insert_one(item)  # 写入数据库里
        print(f'>[{item["title"]}]写入成功')
        # with open('logs.txt', 'a') as f:
        #     f.write(f'[{item["title"]}]写入成功')

    def handle_price(self, priceStr):
        """返回获取价格的时间"""
        date = {
            datetime.now(): priceStr
        }
        return date

    def house_detail(self, item, driver):
        """获取一间房子的详情信息"""
        driver.get(item['houseURL'])  # 访问一间房子的详情页
        # 获取页面上的房子信息
        item['title'] = driver.find_element_by_tag_name('h1').text    # 标题
        price = driver.find_element_by_css_selector('span.total').text    # 价格
        first_price = self.handle_price(price)  # 第一次的价格
        item['price'] = [first_price]   # 房子的价格, 可增量爬取
        houseInfo = driver.find_elements_by_css_selector('div.mainInfo')
        item['room'] = houseInfo[0].text    # 户型
        item['faceTo'] = houseInfo[1].text   # 朝向
        item['area'] = houseInfo[2].text     # 面积
        # 小区名
        item['communityName'] = driver.find_element_by_css_selector('div.communityName a.info').text
        # 发布日期
        item['releaseDate'] = driver.find_element_by_xpath('//div[@class="transaction"]/div[2]/ul/li/span[2]').text
        self.write_item(item)    # 执行写入

    def house_list(self, item):
        """获取一个城区中所有房子的详情页链接"""
        for page in range(1, self.page+1):
            self.driver.get(item['partURL']+f'pg{page}co32/')  # 访问城区的页面
            # 切换到'最新发布'页面
            # self.driver.find_element_by_link_text('最新发布').click()
            # 获取到所有的房子链接
            house_ls = self.driver.find_elements_by_xpath('//ul[@class="sellListContent"]//div[@class="title"]/a')
            # 定义为tuple, 作为url生成器
            houseURL_ls = (house.get_attribute("href") for house in house_ls)
            # 定义一个生成器， 每次生成一个房子的链接， 传入线程当中执行
            for i in range(len(house_ls)):
                try:
                    # 遍历出每间房子的详情页链接
                    item['houseURL'] = next(houseURL_ls)
                    # self.house_detail(dict(item), i)    # 传递深拷贝的item对象, 以及目前的索引
                    self.executor.submit(self.house_detail, item=dict(item), driver=self.driver2)

                    item['houseURL'] = next(houseURL_ls)
                    self.executor.submit(self.house_detail, item=dict(item), driver=self.driver3)
                except StopIteration:
                    break

            else:
                print(f'>>[{item["partName"]}]第{page}页--[Done]')
        else:
            print(f'>>>[{item["partName"]}]--[Done]')

    def run(self):
        """获取所有城区的页面链接"""
        self.driver.get('https://wh.lianjia.com/ershoufang/')    # 访问二手房网址
        # 获取所有区的元素,包含区名和链接
        time.sleep(2)
        # 获取所有城区的元素对象
        temp_ls = self.driver.find_elements_by_xpath('//div[@class="position"]/dl[2]/dd/div[1]/div/a')
        partName_ls = [ele.text for ele in temp_ls]     # 城区名 集
        partURL_ls = [ele.get_attribute("href") for ele in temp_ls]     # 城区链接 集
        item = {}   # 初始化一个容器, 用来存放房子的信息
        for i in range(len(temp_ls)):
            item['partName'] = partName_ls[i]    # 城区名
            item['partURL'] = partURL_ls[i]    # 城区页面链接
            # self.collections = self.db[]
            self.house_list(dict(item))    # 传递深拷贝的item对象
        else:
            # 到这里表示循环顺利执行完毕
            self.driver.close()     # 关闭浏览器
            print('>>>>[Well Done]')
            exit()      # 退出程序执行


if __name__ == '__main__':
    lj = LianJia(1)
    lj.run()