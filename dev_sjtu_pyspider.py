'''本python脚本用于访问上海交大水源社区论坛并根据不同的模块自动下载有关数据，以json的格式对下载数据进行储存。脚本启动为调用run_spider()函数'''

import re
import requests
import json
from bs4 import BeautifulSoup

url_home = "https://dev.bbs.sjtu.edu.cn"
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',
    'cookie': '_ga=GA1.3.1925017915.1596813996; _gid=GA1.3.1910873029.1596813996; _t=59c986caa0a2f55170dc85ea70ec3cee; _bypass_cache=true; authentication_data=%7B%22authenticated%22%3Atrue%2C%22awaiting_activation%22%3Afalse%2C%22awaiting_approval%22%3Afalse%2C%22not_allowed_from_ip_address%22%3Afalse%2C%22admin_not_allowed_from_ip_address%22%3Afalse%2C%22destination_url%22%3A%22%2F%22%7D; _forum_session=dWRRd21wMDR4ZFZmaVZhWklzWnd3ZlRmUFIxTnAwUm94OHlUdWNWVStZUFdVSEZZSW9vSHJWWk53cGpBQjJGeGR1NnFUUVBiQnlaVk44NFZReWxjNEIxN3k5WHJHL05EZ2JLYVNjNGtzSDRxbHhvN1I5dEY3UVVhZEJYVmtVNm9tcUlFck9ZVWQ2OTVDOGZMR1Y5WWdQUTJRMGd3L1FYVDhyanFuY2RTWUFUZ2VkQkpRaThhL1JzYlpMRG5pbGRvMTA1L1ZOWGExV0Q2SVlka1VRYzRON2ppdUlRaklHUElGRENJaUN2MXhGOUlZOWNubU9hNWhwTDhCbm1ucFdDOGtaQ1crV095WnBZWm9Sd0plMXAyY0FTSHFIS1lFRnRML09xbjVoODVSNnc9LS1BcFlhRkN5RUdLNnU0NjkyNjF2OUZRPT0%3D--d7880794b7d4620d404f299bd3d5879ace034d6b'}


def home_page_parse(url_home):
    '''解析论坛主界面，以获取各个模块的信息，并使得能进行下一步的访问'''
    goal_re_expression = r"<h3>\s*?<a href='([\s\S]+?)'>\s*?<span itemprop='name'>([\s\S]+?)</span>\s*?</a>\s*?</h3>"
    url_home_resp = requests.get(url_home, headers=headers)
    goal_pages_info = re.findall(goal_re_expression, url_home_resp.text)
    return goal_pages_info


def module_page_parse(url_module, module_name):
    '''解析各个模块主页面，获得各篇帖子的主要信息，并使得能进行下一步的访问'''
    request_url_self = url_home + url_module + "?page="
    goal_pages_info = list()
    k = 0
    while True:
        k += 1
        request_url = request_url_self
        request_url += str(k)
        module_url_resp = requests.get(request_url, headers=headers)
        goal_re_expression = r"'>\s*?<a href='([\s\S]+?)' class='title raw-link raw-topic-link'>\s*?<span>([\s\S]+?)</span>\s*?</a>\s*?<div>"
        goal_next_pages_info = re.findall(goal_re_expression, module_url_resp.text)
        if len(goal_next_pages_info) == 0:
            return (module_name, goal_pages_info)
        for every_info in goal_next_pages_info:
            goal_pages_info.append(every_info)


def return_all_pages_src(url_home):
    '''home_page_parse与module_page_parse的连接使用'''
    all_post_pages = list()
    module_pages = home_page_parse(url_home)
    for module_page in module_pages:
        post_page_dict = dict()
        (post_page_dict['module_name'], post_page_dict['content']) = module_page_parse(module_page[0], module_page[1])
        all_post_pages.append(post_page_dict)
    return all_post_pages


def return_all_pages_content(all_post_pages):
    '''对各篇帖子的页面进行解析并抓取关键信息'''
    all_post_content = list()
    for every_item in all_post_pages:
        name = every_item['module_name']
        print('正在解析模块:\t{}'.format(name))
        for (every_url_origin, every_url_name) in every_item['content']:
            print('\t正在解析"{}"模块,帖子:\t{}'.format(name, every_url_name))
            k = 0
            post_info = dict()
            while True:
                k += 1
                title_re_expression = r'<a href="/t/topic/\d+?">([\s\S]+?)</a>'
                every_url = every_url_origin + "?page=" + str(k)
                every_url_resp = requests.get(every_url, headers=headers)
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
                post_info['ques'] = str_init(goal_ques_tag)
                goal_reply_tags = every_url_soup.find_all(name='div', class_='post', itemprop='articleBody')
                reply_list = list()
                for goal_reply_tag in goal_reply_tags:
                    reply_list.append(str_init(goal_reply_tag))
                post_info['reply'] = reply_list
            all_post_content.append(post_info)
    return all_post_content


def str_init(tag):
    '''对页面解析过程中一些html格式字段的处理使得更符合读取习惯'''
    text = tag.get_text()
    for i in range(3):
        text = text.replace('\n\n', '\n')
    text.strip('\n')
    return text


def page_src_storage(all_pages_content):
    '''对获得的信息以json的格式进行储存'''
    with open("上海交大水源论坛爬虫爬取消息.json", 'w') as f:
        json.dump(all_pages_content, f)


def run_spider():
    '''启动器'''
    all_pages_src = return_all_pages_src(url_home)
    all_pages_content = return_all_pages_content(all_pages_src)
    page_src_storage(all_pages_content)
    print("运行完成!")

