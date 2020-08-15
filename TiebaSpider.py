'''
项目名称：TiebaSpider，一个对于百度论坛的简易爬虫类
作者：sgjzfzzf
完成时间：2020.8.16
菜鸡创作望大佬们多多指教
第二版预计添加多线程实现多篇帖子同时爬取，等有时间再努力完成！
'''

import re
import requests
import json
from bs4 import BeautifulSoup


class TiebaSpider:
    '''百度贴吧爬虫类，使用时先初始化爬虫对象并传入str类型的关键词，然后通过run_spider函数进行启动'''

    def __init__(self, keyword):
        '''初始化传入参数为str类型的关键词，为爬取贴吧的贴吧名(不含"吧"字)'''
        self.keyword = keyword
        self.home_url = "https://tieba.baidu.com/"
        self.tieba_url = "https://tieba.baidu.com/f?kw=" + keyword + "&ie=utf-8"
        self.post_url_infos = list()
        self.post_contents = list()

    def page_parse(self, page_nums=10):
        '''主页面的解析，传入参数为int类型，代表想要翻取的页数，默认为10'''
        for page_num in range(page_nums):
            page_url = self.tieba_url + "&pn=" + str(50 * page_num)
            page_url_resp = requests.get(page_url)
            page_url_soup = BeautifulSoup(page_url_resp.text, "html.parser")
            post_url_infos = page_url_soup.find_all(name="a", attrs={"rel": "noreferrer", "target": "_blank",
                                                                     "class": "j_th_tit"})
            for post_url_info in post_url_infos:
                post_url_info_dict = dict()
                post_url_info_dict['href'] = post_url_info['href']  # 帖子链接
                post_url_info_dict['title'] = post_url_info['title']  # 帖子链接
                self.post_url_infos.append(post_url_info_dict)

    def post_parse(self, post_url_info):
        '''各个帖子页面的解析，参数无需手动传入'''
        every_post_contents = dict()
        every_post_contents['title'] = post_url_info['title']
        every_post_contents['content'] = list()
        post_url = self.home_url + post_url_info['href']
        post_url_resp = requests.get(post_url)
        post_url_soup = BeautifulSoup(post_url_resp.text, "html.parser")
        page_num_tag = post_url_soup.find_all(name='li', attrs={'class': 'l_reply_num'})[0]
        page_num = int(list(page_num_tag.children)[2].text)
        for pn in range(1, page_num + 1):
            page_post_url = post_url + "?pn=" + str(pn)
            page_post_url_resp = requests.get(page_post_url)
            times = re.findall(r'\d{4}-\d{2}-\d{2}\s*?\d{2}:\d{2}', page_post_url_resp.text)  # 发帖时间
            post_soup = BeautifulSoup(page_post_url_resp.text, "html.parser")
            names = post_soup.find_all(name='a', attrs={"class": "p_author_name j_user_card"})  # 发帖人昵称
            texts = post_soup.find_all(name="div", attrs={"class": "d_post_content j_d_post_content clearfix"})  # 发帖内容
            for time, name, text in zip(times, names, texts):
                every_post_contents['content'].append(
                    {"times": time, "name": name.text, "text": text.text.strip(' ')})
        self.post_contents.append(every_post_contents)

    def storage(self):
        '''以json的格式实现对爬取数据的储存'''
        with open(self.keyword + "百度贴吧爬取结果.json", 'w') as f:
            json.dump(self.post_contents, f)

    def run_spider(self):
        '''启动器'''
        self.page_parse()
        for post_url_info in self.post_url_infos:
            self.post_parse(post_url_info)
        self.storage()

