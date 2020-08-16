'''
项目：SinoUniSpider，新浪官微的爬虫
作者：sgjzfzzf
完成时间：2020.8.16
'''

import requests
import json
import threading


class SpiderThread(threading.Thread):
    '''爬虫的多线程类，用户在使用时无需主动调用'''
    semaphore = threading.Semaphore(10)

    def __init__(self, spider, every_card):
        super().__init__()
        self.spider = spider
        self.every_card = every_card

    def run(self):
        SpiderThread.semaphore.acquire()
        card_info = dict()
        if (not 'mblog' in self.every_card.keys()):
            return
        card_info['scheme'] = self.every_card['scheme']  # 链接
        card_info['id'] = self.every_card['mblog']['id']
        card_info['raw_text'] = self.every_card['mblog']['raw_text']  # 内容
        card_info['reposts_count'] = self.every_card['mblog']['reposts_count']  # 转发数
        card_info['attitudes_count'] = self.every_card['mblog']['attitudes_count']  # 点赞数
        card_info['comments_count'] = self.every_card['mblog']['comments_count']  # 评论数
        card_info['created_at'] = self.every_card['mblog']['created_at']  # 创建时间
        card_info['comment'] = self.spider.comment_parse(card_info['id'])  # 评论抓取
        self.spider.card_infos.append(card_info)
        SpiderThread.semaphore.release()


class SinoSpider:
    '''爬虫类，初始化时传入两个参数，第一个是爬取官微的名称，第二个是用户的唯一表识uid，需要手动进入微博查看'''

    def __init__(self, name, uid):
        '''初始化函数'''
        self.name = name
        self.uid = uid
        self.api_container_home_url = "https://m.weibo.cn/api/container/getIndex?"
        self.api_comments_url = "https://m.weibo.cn/comments/hotflow?"
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36'}
        self.api_container_params = {'uid': '1871729063',
                                     't': '0',
                                     'luicode': '10000011',
                                     'lfid': '100103type=1&q=' + name,
                                     'type': 'uid',
                                     'value': str(uid),
                                     'containerid': str(107603) + str(uid)}
        self.api_comments_params = {"max_id_type": "0"}
        self.card_infos = list()

    def card_parse(self):
        '''对主页面的分析'''
        url = self.api_container_home_url
        for key, value in self.api_container_params.items():
            url = url + key + '=' + value + '&'
        url = url[:-1]
        url_resp = requests.get(url, headers=self.headers, params=self.api_container_params)
        url_resp_json = url_resp.json()
        threads = list()
        for every_card in url_resp_json['data']['cards']:
            thread = SpiderThread(self, every_card)
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
        self.api_container_params['since_id'] = str(
            url_resp_json['data']['cardlistInfo']['since_id'])  # 获取下一页的关键参数since_id

    def comment_parse(self, id):
        '''对每一条微博下评论的解析'''
        comments = list()
        self.api_comments_params['id'] = id
        self.api_comments_params['mid'] = id
        comments_url = self.api_comments_url + 'id=' + str(self.api_comments_params['id']) + '&mid=' + \
                       str(self.api_comments_params[
                               'mid']) + '&max_id_type=' + self.api_comments_params['max_id_type']
        comments_url_resp = requests.get(comments_url, headers=self.headers, params=self.api_comments_params)
        try:
            comments_info = comments_url_resp.json()['data']['data']
        except(KeyError):
            print("id={}页面无评论,尝试抓取评论失败......".format(id))
            return
        for comment_info in comments_info:
            comment = dict()
            comment['created_at'] = comment_info['created_at']
            comment['text'] = comment_info['text']
            comment['user'] = dict()
            comment['user']['name'] = comment_info['user']['screen_name']
            comment['user']['id'] = comment_info['user']['id']
            comment['like_count'] = comment_info['like_count']
            comments.append(comment)
        return comments

    def storage(self):
        with open(self.name + "新浪微博爬取结果.json", 'w') as f:
            json.dump(self.card_infos, f)

    def run_spider(self, page_num=10):
        print("开始解析......")
        for i in range(page_num):
            self.card_parse()
        print("开始存储.....")
        self.storage()
        print("运行完成")
