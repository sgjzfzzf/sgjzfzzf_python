'''
项目名称：YouDaoTranslateSpider，利用在线有道词典功能进行自动化翻译
作者：sgjzfzzf
时间：2020.8.13
'''

# 引入所需库
import requests


# 定义爬虫类，使用时先具象化为具体的对象，再根据所需调用相应的函数
class YouDaoTranslaterSpider:
    '''
    包含四个成员变量，url储存翻译API的url，headers和data储存post方法必需的参数，translate_results储存翻译结果的原始数据
    包含五个成员函数，translate_str对某一字符串进行翻译，translate_document对某一文件内容进行自动化翻译，print_str打印翻译结果，store_str储存翻译结果，return_str对原始数据进行初始化并将其返回，只有在调用过translate_str或translate_document才能调用其他函数
    '''
    url = "http://fanyi.youdao.com/translate?"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36"}
    data = {"from": "AUTO",
            "to": "AUTO",
            "smartresult": "dict",
            "client": "fanyideskweb",
            "doctype": "json",
            "version": 2.1,
            "keyfrom": "fanyi.web",
            "action": "FY_BY_REALTlME"}
    translate_results = list()

    class NoTranslateResults(BaseException):
        '''内置异常类'''
        WarnString = "尚未执行翻译函数，请检查代码"

    def __return_str__(self):
        '''对储存的translate_results进行初始化使其打印后更易读，无需传参，为内置方法，使用者无需调用'''
        try:
            if len(self.translate_results) == 0:
                raise self.NoTranslateResults()
        except self.NoTranslateResults as e:
            print(e.WarnString)
            return
        print_string = ""
        print_string += "原文:\n"
        for translate_paragraph_result in self.translate_results:
            for translate_sentence_result in translate_paragraph_result:
                print_string += translate_sentence_result["src"]
            print_string += '\n'
        print_string += "译文:\n"
        for translate_paragraph_result in self.translate_results:
            for translate_sentence_result in translate_paragraph_result:
                print_string += translate_sentence_result["tgt"]
            print_string += '\n'
        return print_string

    def print_str(self):
        '''打印翻译结果，无需传参'''
        print_string = self.__return_str__()
        print(print_string)

    def store_str(self, save_place):
        '''储存翻译结果，传入参数save_place为str类型，代表翻译文件储存位置'''
        with open(save_place, 'w') as f:
            input_string = self.__return_str__()
            f.write(input_string)

    def translate_str(self, string, flag=False):
        '''对某一字符串进行翻译。传入第一个参数string为str类型，代表所需翻译的字符串；传入第二个参数为bool类型的变量，默认为False，代表完成后是否需要自动打印翻译结果'''
        self.data["i"] = string
        self.url_resp = requests.post(self.url, headers=self.headers, data=self.data)
        translate_results = self.url_resp.json()['translateResult']
        self.translate_results = translate_results
        if (flag):
            self.print_str()
        return translate_results

    def translate_document(self, document, flag=False):
        '''对某一字符串进行翻译。传入第一个参数string为str类型，代表所需翻译的字符串；传入第二个参数为bool类型的变量，默认为False，代表完成后是否需要自动打印翻译结果'''
        with open(document, 'r') as f:
            read_str = f.read()
        return self.translate_str(read_str, flag)
