#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: hao 2019/12/16-15:20
from selenium import webdriver


class SeleniumGetCookies:
    def __init__(self, url):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        self.driver = webdriver.Chrome(executable_path='E:/chromedriver.exe', options=options)
        self.driver.get(url)

    def run(self):
        cookie = [item["name"] + "=" + item["value"] for item in self.driver.get_cookies()]
        cookie_str = ';'.join(item for item in cookie)
        return cookie_str

    def __del__(self):
        self.driver.close()


if __name__ == '__main__':
    s = SeleniumGetCookies('https://www.baidu.com').run()
    print(s)
