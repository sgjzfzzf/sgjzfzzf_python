'''本python脚本用于访问上海交大水源社区论坛并根据不同的模块自动下载有关数据，以json的格式对下载数据进行储存。脚本启动为调用run_spider()函数'''

import re
import requests
import json
import threading
from bs4 import BeautifulSoup


class DevSJTUSpider:
    '''自动爬取上海交大水源社区的爬虫，使用时先初始化，无需传参，然后通过run_spider函数直接调用'''

    def __init__(self):
        '''初始化爬虫，信息包含主页面链接与头文件'''
        self.url_home = "https://dev.bbs.sjtu.edu.cn"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',
            'cookie': '_ga=GA1.3.1925017915.1596813996; _gid=GA1.3.1910873029.1596813996; _t=59c986caa0a2f55170dc85ea70ec3cee; _bypass_cache=true; authentication_data=%7B%22authenticated%22%3Atrue%2C%22awaiting_activation%22%3Afalse%2C%22awaiting_approval%22%3Afalse%2C%22not_allowed_from_ip_address%22%3Afalse%2C%22admin_not_allowed_from_ip_address%22%3Afalse%2C%22destination_url%22%3A%22%2F%22%7D; _forum_session=dWRRd21wMDR4ZFZmaVZhWklzWnd3ZlRmUFIxTnAwUm94OHlUdWNWVStZUFdVSEZZSW9vSHJWWk53cGpBQjJGeGR1NnFUUVBiQnlaVk44NFZReWxjNEIxN3k5WHJHL05EZ2JLYVNjNGtzSDRxbHhvN1I5dEY3UVVhZEJYVmtVNm9tcUlFck9ZVWQ2OTVDOGZMR1Y5WWdQUTJRMGd3L1FYVDhyanFuY2RTWUFUZ2VkQkpRaThhL1JzYlpMRG5pbGRvMTA1L1ZOWGExV0Q2SVlka1VRYzRON2ppdUlRaklHUElGRENJaUN2MXhGOUlZOWNubU9hNWhwTDhCbm1ucFdDOGtaQ1crV095WnBZWm9Sd0plMXAyY0FTSHFIS1lFRnRML09xbjVoODVSNnc9LS1BcFlhRkN5RUdLNnU0NjkyNjF2OUZRPT0%3D--d7880794b7d4620d404f299bd3d5879ace034d6b'}
        self.all_post_content = list()

    def home_page_parse(self):
        '''解析论坛主界面，以获取各个模块的信息，并使得能进行下一步的访问'''
        goal_re_expression = r"<h3>\s*?<a href='([\s\S]+?)'>\s*?<span itemprop='name'>([\s\S]+?)</span>\s*?</a>\s*?</h3>"
        url_home_resp = requests.get(self.url_home, headers=self.headers)
        goal_pages_info = re.findall(goal_re_expression, url_home_resp.text)
        self.home_page_sources = goal_pages_info

    def module_page_parse(self, url_module, module_name):
        '''解析各个模块主页面，获得各篇帖子的主要信息，并使得能进行下一步的访问'''
        request_url_self = self.url_home + url_module + "?page="
        goal_pages_info = list()
        k = 0
        while True:
            k += 1
            request_url = request_url_self
            request_url += str(k)
            module_url_resp = requests.get(request_url, headers=self.headers)
            goal_re_expression = r"'>\s*?<a href='([\s\S]+?)' class='title raw-link raw-topic-link'>\s*?<span>([\s\S]+?)</span>\s*?</a>\s*?<div>"
            goal_next_pages_info = re.findall(goal_re_expression, module_url_resp.text)
            if len(goal_next_pages_info) == 0:
                return (module_name, goal_pages_info)
            for every_info in goal_next_pages_info:
                goal_pages_info.append(every_info)

    def return_all_pages_src(self):
        '''home_page_parse与module_page_parse的连接使用'''
        all_post_pages = list()
        self.home_page_parse()
        for module_page in self.home_page_sources:
            post_page_dict = dict()
            post_page_dict['module_name'], post_page_dict['content'] = self.module_page_parse(module_page[0],
                                                                                              module_page[1])
            all_post_pages.append(post_page_dict)
        self.all_post_pages = all_post_pages

    def return_all_pages_content(self):
        '''对各篇帖子的页面进行解析并抓取关键信息，采用六线程的方式同时运行'''
        threads = list()
        for every_item in self.all_post_pages:
            thread = SpiderThread(self, every_item['module_name'], every_item['content'])
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()

    def page_src_storage(self):
        '''对获得的信息以json的格式进行储存'''
        with open("上海交大水源论坛爬虫爬取消息.json", 'w') as f:
            json.dump(self.all_post_content, f)

    def run_spider(self):
        '''爬虫启动器'''
        print("开始解析主页面......")
        self.return_all_pages_src()
        print("主页面解析完成，开始解析各篇帖子......")
        self.return_all_pages_content()
        print("帖子解析完成，开始存储数据......")
        self.page_src_storage()
        print("运行完成!")


class SpiderThread(threading.Thread):
    '''爬虫的多线程对象'''
    all_post_content = list()
    semaphore = threading.BoundedSemaphore(6)

    def __init__(self, spider, module_name, content):
        '''传入参数为spider本身，模块名与内容'''
        super().__init__()
        self.spider = spider
        self.module_name = module_name
        self.content = content

    def run(self):
        '''SpiderThread对象的线程函数'''
        for (every_url_origin, every_url_name) in self.content:
            SpiderThread.semaphore.acquire()
            print('正在解析"{}"模块,帖子:\t{}'.format(self.module_name, every_url_name))
            k = 0
            post_info = dict()
            while True:
                k += 1
                title_re_expression = r'<a href="/t/topic/\d+?">([\s\S]+?)</a>'
                every_url = every_url_origin + "?page=" + str(k)
                every_url_resp = requests.get(every_url, headers=self.spider.headers)
                every_url_text = every_url_resp.text
                every_url_soup = BeautifulSoup(every_url_text, "html.parser")
                goal_title_tags = every_url_soup.find_all(name="h1", class_="crawler-topic-title")
                if len(goal_title_tags) == 0:
                    break
                goal_title_tag = goal_title_tags[0]
                post_info['title'] = re.findall(title_re_expression, str(goal_title_tag))[0]
                goal_ques_tags = every_url_soup.find_all(name="div", class_='post', itemprop='articleBody')
                if len(goal_ques_tags) == 0:
                    break
                goal_ques_tag = goal_ques_tags[0]
                post_info['ques'] = goal_ques_tag.get_text()
                goal_reply_tags = every_url_soup.find_all(name='div', class_='post', itemprop='articleBody')
                reply_list = list()
                for goal_reply_tag in goal_reply_tags:
                    reply_list.append(goal_reply_tag.get_text())
                post_info['reply'] = reply_list
            self.spider.all_post_content.append(post_info)
            SpiderThread.semaphore.release()
