#!/usr/bin/env python
#-*- coding: utf-8 -*-
# author: hao 2019/11/9-17:40
import json

from datetime import datetime
from selenium import webdriver


class LianJia:
    def __init__(self, page):
        # self.executor = ThreadPoolExecutor(max_workers=2)  # 使用内置线程池, 设置最大线程数

        # 声明Chrome浏览器对象
        self.driver = webdriver.Chrome(r'E:\I want something just like this\spider\webdriver\chromedriver.exe')
        self.page = page    # 代表你要爬取多少页,这里指的是每个城区爬取多少页

    def write_item(self, item):
        json_data = json.dumps(item, ensure_ascii=False)
        print(item)
        with open('data.json', 'a', encoding='utf-8') as f:
            f.write(json_data + '\n')
        print(f'>>>[{item["title"]}]写入成功')

    def handle_price(self, priceStr):
        """返回获取价格的时间"""
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        date = {
            now: priceStr
        }
        return date

    def house_detail(self, item, url):
        """获取一间房子的详情信息"""
        self.driver.get(url)  # 访问一间房子的详情页
        # 获取页面上的房子信息
        item['houseURL'] = url
        item['title'] = self.driver.find_element_by_tag_name('h1').text    # 标题
        price = self.driver.find_element_by_css_selector('span.total').text    # 价格
        first_price = self.handle_price(price)  # 第一次的价格
        item['price'] = [first_price]   # 房子的价格, 可增量爬取
        houseInfo = self.driver.find_elements_by_css_selector('div.mainInfo')
        item['room'] = houseInfo[0].text    # 户型
        item['faceTo'] = houseInfo[1].text   # 朝向
        item['area'] = houseInfo[2].text     # 面积
        # 小区名
        item['communityName'] = self.driver.find_element_by_css_selector('div.communityName a.info').text
        # 发布日期
        item['releaseDate'] = self.driver.find_element_by_xpath('//div[@class="transaction"]/div[2]/ul/li/span[2]').text
        self.write_item(item)

    def house_list(self, item):
        """获取一个城区中所有房子的详情页链接"""
        for page in range(1, self.page+1):
            self.driver.get(item['partURL']+f'pg{page}co32/')  # 访问城区的页面
            # 获取到所有的房子链接
            house_ls = self.driver.find_elements_by_xpath('//ul[@class="sellListContent"]//div[@class="title"]/a')
            # 定义为tuple, 作为url生成器
            houseURL_ls = [house.get_attribute("href") for house in house_ls]

            for url in houseURL_ls:
                self.house_detail(item=item, url=url)
            print(f'>>[{item["partName"]}]第{page}页--[Done]')
        else:
            print(f'>[{item["partName"]}]--[Done]')

    def run(self):
        """获取所有城区的页面链接"""
        self.driver.get('https://wh.lianjia.com/ershoufang/')    # 访问二手房网址
        # 获取所有城区的元素对象
        temp_ls = self.driver.find_elements_by_xpath('//div[@class="position"]/dl[2]/dd/div[1]/div/a')
        partName_ls = [ele.text for ele in temp_ls]     # 城区名 集
        partURL_ls = [ele.get_attribute("href") for ele in temp_ls]     # 城区链接 集
        item = {}   # 初始化一个容器, 用来存放房子的信息
        # for i in range(len(temp_ls)):
        for i in range(1, 2):
            item['partName'] = partName_ls[i]    # 城区名
            item['partURL'] = partURL_ls[i]    # 城区页面链接
            self.house_list(dict(item))    # 传递深拷贝的item对象
        else:
            # 到这里表示循环顺利执行完毕
            self.driver.close()     # 关闭浏览器
            print('>>>>[Well Done]')
            exit()      # 退出程序执行


if __name__ == '__main__':
    lj = LianJia(1)
    lj.run()