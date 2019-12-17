#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: hao 2019/11/21-20:00
from datetime import datetime
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


class BossJob:
    def __init__(self):
        # 声明浏览器配置, 这种配置能让js检测不出来,我们是webdriver
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        # 声明第一个浏览器, 传入配置, 用作获取职位链接
        self.chrome = webdriver.Chrome(r'E:\chromedriver.exe', options=options)
        # 声明第二个浏览器, 用作访问职位详情页
        self.chrome2 = webdriver.Chrome(r'E:\chromedriver.exe', options=options)
        # 声明数据库
        self.coll = MongoClient(host="localhost", port=27017).Spider.BossJobs
        # 设置过期时间
        self.coll.create_index([('WriteTime', 1)], expireAfterSeconds=259200)

    def write_item(self, item):
        item['WriteTime'] = datetime.utcnow()
        self.coll.insert_one(item)
        print(f'>>>[{item["Name"]}]写入成功')

    def job_detail(self, url):
        # 打开工作详情页到一个新窗口
        if self.coll.find_one({'URL': url}):
            print('已爬取，跳过: ', url)
            return
        # 获取详情页的数据
        self.chrome2.get(url)
        item = {}
        item['URL'] = self.chrome2.current_url  # 链接
        item['Name'] = self.chrome2.find_element_by_tag_name('h1').text  # 职位职称
        item['Salary'] = self.chrome2.find_element_by_class_name('salary').text  # 薪资
        item['Info'] = self.chrome2.find_element_by_xpath('//div[@class="job-banner"]//p').text  # 城市,工作经验,学历
        tags_ls = self.chrome2.find_elements_by_xpath('//div[@class="info-primary"]//div[@class="job-tags"]/span')
        item['Tags'] = [tag.text for tag in tags_ls]  # 工作标签
        item['Description'] = self.chrome2.find_element_by_xpath(
            '//div[@class="job-sec"]/div[@class="text"]').text  # 职位描述
        item['Company'] = self.chrome2.find_element_by_xpath('//div[@class="company-info"]/a[1]').get_attribute(
            'title').split()[0]  # 公司名称
        item['UpdateTime'] = self.chrome2.find_elements_by_class_name('gray')[0].text[4:]  # 更新时间
        self.write_item(item)

    def run(self, job):
        """运行方法, 获取所有工作的url"""
        self.chrome.get('https://www.zhipin.com')
        # 输入关键字到搜索框
        self.chrome.find_element_by_name("query").send_keys(job)
        # 按下回车以搜索
        ActionChains(self.chrome).key_down(Keys.ENTER).key_up(Keys.ENTER).perform()
        while 1:
            # 抓取所有的职位
            job_ls = self.chrome.find_elements_by_xpath('//div[@class="info-primary"]/h3/a')
            # 迭代出职位详情页链接
            job_url_ls = [job.get_attribute('href') for job in job_ls]
            for url in job_url_ls:
                # 遍历详情链接,传入下一个方法
                self.job_detail(url)

            # 滚动条拖动到浏览器的最下方
            self.chrome.execute_script('window.scrollTo(0,document.body.scrollHeight);')

            # 声明下一页按钮的对象
            next_page = self.chrome.find_element_by_css_selector('a.next')
            if 'disable' in next_page.get_attribute('class'):
                # class中有disable,说明已是尾页,跳出循环
                break
            # 否则继续点击下一页按钮
            next_page.click()

    def __del__(self):
        # 到这里表示循环顺利执行完毕
        self.chrome.close()  # 关闭浏览器1
        self.chrome2.close()  # 关闭浏览器2
        print('>>>>[Well Done]')


if __name__ == '__main__':
    bj = BossJob()
    bj.run('爬虫')
