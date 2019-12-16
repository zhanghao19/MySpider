#!/usr/bin/env python
#-*- coding: utf-8 -*-
# author: hao 2019/12/12-19:13
import json
from datetime import datetime

import requests
from lxml import etree
from pymongo import MongoClient
from selenium import webdriver


class ZhiLianJob:
    def __init__(self):
        # 声明数据库
        self.coll = MongoClient(host="localhost", port=27017).Spider.Jobs
        # 设置过期时间
        self.coll.create_index([('WriteTime', 1)], expireAfterSeconds=259200)
        # 使用selenium获取cookies,方法很慢,但是最有效
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        self.driver = webdriver.Chrome(executable_path='E:/chromedriver.exe', options=options)
        self.driver.get("https://jobs.zhaopin.com")
        cookie = [item["name"] + "=" + item["value"] for item in self.driver.get_cookies()]
        self.cookiestr = ';'.join(item for item in cookie)

    def write_item(self, item):
        item['WriteTime'] = datetime.utcnow()
        self.coll.insert_one(item)
        print(f'>>>[{item["Name"]}]写入成功')

    def job_detail(self, item):
        # 打开工作详情页到一个新窗口
        if self.coll.find_one({'URL': item['URL']}):
            print('已爬取，跳过: ', item['URL'])
            return
        headers = {
            'cookie': self.cookiestr,
        }
        # 获取详情页的数据
        resp = requests.get(url=item['URL'], headers=headers)
        html = etree.HTML(resp.text)
        item['Description'] = html.xpath('//*[@class="describtion__detail-content"]//text()')  # 职位描述
        self.write_item(dict(item))

    def run(self, job_name):
        """运行方法, 获取所有工作的url"""
        # post请求携带的json数据
        payload = {
            'cityId': "736",
            'kt': "3",
            'kw': job_name,
            'pageSize': "100",
        }
        # 访问网址获取响应
        resp = requests.post('https://fe-api.zhaopin.com/c/i/sou', json=payload)
        # json解析出数据形成一个字典,再通过key取出职位列表
        job_list = json.loads(resp.text)['data']['results']
        # 遍历出所有的数据
        item = {}
        for job in job_list:
            if 'jobs.zhaopin.com' in job['positionURL']:
                item['URL'] = job['positionURL']  # 链接
                item['Name'] = job['jobName']  # 职位职称
                item['Salary'] = job['salary']  # 薪资
                item['City'] = job['city']['display']  # 城市
                item['eduLevel'] = job['eduLevel']['name']  # 学历
                item['workingExp'] = job['workingExp']['name']  # 工作经验
                item['Tags'] = job['welfare']  # 职位待遇标签
                item['Company'] = job['company']['name']  # 公司名称
                item['UpdateTime'] = job['updateDate']  # 更新时间
                self.job_detail(dict(item))

    def __del__(self):
        # 到这里表示循环顺利执行完毕
        self.driver.close()
        print('>>>>[Well Done]')


if __name__ == '__main__':
    bj = ZhiLianJob()
    bj.run('python爬虫')
