#!/usr/bin/env python
#-*- coding: utf-8 -*-
# author: hao 2019/7/22-20:49
import json
import os
import random
import re
import time
import jieba
import requests
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import collections
import wordcloud


COMMENTS_FILE_PATH = 'comments.txt'
IMAGE_SOURCE = 'durex.jpg'
FONT_PATH = 'C:/Windows/Fonts/simhei.ttf'


def get_comments(page=0):
    """
    发送productPageComments请求,从响应中获取评论文本,并写入文件
    :param page: 第几页
    """
    headers = {'referer': 'https://item.jd.com/1668311.html', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0;WOW64) '
                                                                            'AppleWebKit/537.36 (KHTML, like Gecko) '
                                                                            'Chrome/69.0.3497.100 Safari/537.36'}
    url = 'https://sclub.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98vv15496&productId' \
          '=1668311&score=0&sortType=5&page={}&pageSize=10&isShadowSku=0&rid=0&fold=1'.format(page)
    print(url)
    resp = requests.get(url=url, headers=headers)   # 获取响应
    resp_str = resp.text[27:-2]     # 获取响应文本, 切片的目的是去掉头部和尾部的冗余字符
    resp_json = json.loads(resp_str)    # 将文本转为json
    with open(COMMENTS_FILE_PATH, 'a+') as file:
        for comment in resp_json['comments']:
            file.write(comment['content'] + '\n')


def get_more_pages(num):
    """
    实现分页爬取
    :param num: 目标页码
    """
    if os.path.exists(COMMENTS_FILE_PATH):
        os.remove(COMMENTS_FILE_PATH)
    for i in range(num):
        get_comments(i)
        time.sleep(random.random() * 5)


def cut_word():
    """
    从评论中截取词, 剔除无效的词
    :return:截取好的词
    """
    with open(COMMENTS_FILE_PATH) as file:
        comments = file.read()
    chars = re.compile(u'\n|\t|,|\.|，|！|\?|。|～|？|、')
    word_re = re.sub(chars, '', comments)
    word_list = jieba.lcut(word_re, cut_all=True)
    remove_words = ['', u'的', u'和', u'是', u'我', u'很', u'中', u'在', u'了', u'有', u'不']
    word_list_ok = [s for s in word_list if s not in remove_words]
    words = ' '.join(word_list_ok)
    return words
    # return word_list_ok


def create_words_cloud():
    """
    生成词云图
    :return:
    """
    img_shape = np.array(Image.open(IMAGE_SOURCE))
    word_cloud = wordcloud.WordCloud(background_color='white', max_words=2000, mask=img_shape,
                                     scale=4, max_font_size=50, random_state=42, font_path=FONT_PATH)
    word_cloud.generate(cut_word())

    plt.imshow(word_cloud, interpolation='bilinear')
    plt.axis('off')
    plt.figure()
    plt.show()


def make_words_cloud():
    # 词频统计
    word_counts = collections.Counter(cut_word())  # 对分词做词频统计
    word_counts_top10 = word_counts.most_common(10)  # 获取前10最高频的词
    # print(word_counts_top10)  # 输出检查

    # 词频展示
    mask = np.array(Image.open(IMAGE_SOURCE))  # 定义词频背景
    wc = wordcloud.WordCloud(
        font_path=FONT_PATH,  # 设置字体格式
        mask=mask,  # 设置背景图
        max_words=200,  # 最多显示词数
        max_font_size=100  # 字体最大值
    )

    wc.generate_from_frequencies(word_counts)  # 从字典生成词云
    image_colors = wordcloud.ImageColorGenerator(mask)  # 从背景图建立颜色方案
    wc.recolor(color_func=image_colors)  # 将词云颜色设置为背景图方案
    plt.imshow(wc)  # 显示词云
    plt.axis('off')  # 关闭坐标轴
    plt.show()  # 显示图像


if __name__ == '__main__':
    # get_more_pages(50)
    # print(cut_word())
    create_words_cloud()
    # make_words_cloud()