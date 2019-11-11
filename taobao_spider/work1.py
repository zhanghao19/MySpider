#!/usr/bin/env python
#-*- coding: utf-8 -*-
# author: hao 2019/11/6-22:59
import time

from selenium import webdriver
from pymongo import MongoClient

from taobao_spider.account import USERNAME, PASSWORD


class TaoBao:
    def __init__(self):
        # 声明浏览器对象
        self.driver = webdriver.Chrome(r'E:\Download\BaiduYunDownload\chromedriver_win32\chromedriver.exe')
        # 声明数据库对象
        self.client = MongoClient(host="localhost", port=27017)
        self.db = self.client.TaoBao
        self.coll = self.db.iPhone

    def get_elements(self, itemName, number):
        self.driver.get('https://login.taobao.com/member/login.jhtml')    # 访问网站
        try:
            self.driver.find_element_by_id('J_Quick2Static').click()    # 点击切换密码登录
        except Exception as e:
            print(e)
        finally:
            # 由于selenium登录淘宝账户会被检测, 导致无法验证, 因此我们选择使用微博登录
            self.driver.find_element_by_class_name('weibo-login').click()    # 点击微博登录
        time.sleep(2)
        # 输入微博的用户名密码
        self.driver.find_element_by_name('username').send_keys(USERNAME)
        self.driver.find_element_by_name('password').send_keys(PASSWORD)
        self.driver.find_element_by_class_name('W_btn_g').click()    # 点击登录按钮
        time.sleep(2)
        self.driver.find_element_by_id('q').send_keys(itemName)    # 输入关键字到搜索框
        self.driver.find_element_by_class_name('search-button').click()    # 点击搜索按钮
        item = {}   # 存放商品的容器
        item_number = 1
        while 1:
            ele_list = self.driver.find_elements_by_class_name('J_MouserOnverReq')   # 获取页面上所有的商品的div元素
            for ele in ele_list:
                if item_number > number:
                    self.driver.close()
                    exit()
                # 遍历每个商品元素, 并获取数据
                item['url'] = ele.find_element_by_class_name('J_ItemPicA').get_attribute('href')    # 商品链接
                item['title'] = ele.find_element_by_class_name('J_ItemPic').get_attribute('alt')    # 商品标题
                item['price'] = ele.find_element_by_tag_name('strong').text    # 商品价格
                item['sales'] = ele.find_element_by_class_name('deal-cnt').text or '未知'  # 销售量,包含空值
                item['shopname'] = ele.find_element_by_class_name('shopname').text  # 商铺名location
                item['location'] = ele.find_element_by_class_name('location').text or '未知产地'  # 产地,包含空值
                print(self.coll.insert_one(dict(item)))
                print(f'[{item_number}]--{item["title"]}')
                item_number += 1
            self.driver.find_elements_by_class_name('icon-btn-next-2')[0].click()
            time.sleep(2)
            print(self.coll.find())


if __name__ == '__main__':
    tb = TaoBao()
    tb.get_elements('iPhone', 100)
