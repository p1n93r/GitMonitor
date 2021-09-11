# Author: P1n93r
# Version: 1.1.1
# !/usr/bin/python3
# coding=utf-8
from libs.database import DataBase
from libs.log import logger
from libs.utils import url_encode
from libs.setting import GITHUB_API_URL, GITHUB_SEARCH_RESULTS_PATH, GITHUB_SEARCH_URL, DB_HOST, DB_USER, DB_PASS, \
    DB_NAME, DB_CHARSET, DB_PORT
from libs.utils import current_time, save_csv_file
from libs.git_query_thread import GitQueryThread
import uuid
import time


class GitSearch:
    def __init__(self, tokens, keywords, dorkers, prefix_dict):
        if not tokens:
            raise RuntimeError('Github Token must not None')
        # 允许 dorker 或 keywords 为空（但不允许同时为空）, 方便作为非监控性使用
        if not dorkers and not keywords:
            raise RuntimeError('dorkers and keywords both are None')
        # github token[required]
        self.tokens = tokens
        # 待搜索资产关键字
        self.keywords = keywords
        # 傻瓜关键字, 使用内部字典构建，例如 api_key 等傻瓜关键字
        self.dorkers = dorkers
        # 查询前缀, 数据结构 : [{“org”:"apache"},{"user":"p1n93r"}]
        self.prefix_dict = prefix_dict
        # 待请求的url列表
        self.urls = []
        # 请求失败的url列表
        self.error_urls = []
        # 请求结果列表，用于存放数据库或者csv表格中
        self.results = []
        logger.info("called GitSearch#__init__()...")

    def start_search(self):
        """
        开始扫描, 注意, Github 规定每个token最多每分钟请求 30 个请求
        """
        logger.info("Start to create query urls by call GitSearch#create_query_urls()...")
        logger.info("current time is {0}".format(current_time()))
        self.create_query_urls()
        self.start_request()
        return self.save_result()

    def start_request(self):
        # 有多少个token，就开多少个线程进行请求
        # 每个线程最多处理 30 个url

        # 计算循环创建线程的次数
        for_count = (len(self.urls) + len(self.tokens) * 30 - 1) / (len(self.tokens) * 30)
        for _ in range(int(for_count)):
            threads = []
            for token in self.tokens:
                target_urls = []
                for _ in range(29):
                    if not self.urls:
                        break
                    target_urls.append(self.urls.pop())
                if target_urls:
                    thread = GitQueryThread(str(uuid.uuid4()), target_urls, token)
                    threads.append(thread)
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
            for thread in threads:
                res = thread.get_res()
                error_urls = thread.get_error_urls()
                for item in error_urls:
                    self.error_urls.append(item)
                for item in res:
                    self.results.append(item)
                logger.info("thread_id: {0},find len(res)= {1}".format(thread.get_thread_id(), len(res)))
            # 每请求一轮，需要暂停一分钟
            logger.info("one batch has bean finished,start to sleep one minute")
            logger.info("===========still remaining : {0} standard urls===========".format(len(self.urls)))
            time.sleep(65)
            logger.info("Start next batch request......")

        # 如果 error_urls 不为空，还得清空这个列表,防止收集不全
        if self.error_urls:
            logger.info("Clean up the remaining error urls...")
            logger.info(":::::::::::still remaining : {0} error urls:::::::::::".format(len(self.error_urls)))
            for item in self.error_urls:
                self.urls.append(item)
            self.error_urls.clear()
            # 递归调用本函数，直到清空所有请求
            self.start_request()

    def save_result(self):
        # 先将 results 中的 github api替换一下
        for item in self.results:
            tmp = item['url'].replace(GITHUB_API_URL, GITHUB_SEARCH_URL)
            item['url'] = tmp
        # save results to db
        new_res = []
        db = DataBase(host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME, port=DB_PORT, charset=DB_CHARSET)
        for item in self.results:
            logger.info("start save current res url : {0}".format(item))
            judge = db.check_insert('scan_res', item, {"url": item['url'], 'count': item['count']})
            if judge:
                new_res.append(item)
        # save results to csv
        # only save new ones
        self.results = new_res
        res_file = self.save_to_csv()
        return {'res': self.results, 'res_file': res_file}

    def add_query_url(self, query_prefix, prefix_val):
        """
        往urls中添加待搜索url
        """
        # keywords 和 dorkers 都不为空的情况
        if self.keywords and self.dorkers:
            for keyword in self.keywords:
                for dork in self.dorkers:
                    # 如果存在查询前缀, 例如 user: 或者 org:
                    if query_prefix and prefix_val:
                        current_key = "{0}:{1} {2} {3}".format(query_prefix, prefix_val, keyword, dork)
                    else:
                        current_key = "{0} {1}".format(keyword, dork)
                    url = GITHUB_API_URL + url_encode(current_key) + "&type=Code"
                    self.urls.append(url)
        # keywors 不为空, 但是 dokers 为空
        if self.keywords and not self.dorkers:
            for keyword in self.keywords:
                # 如果存在查询前缀, 例如 user: 或者 org:
                if query_prefix and prefix_val:
                    current_key = "{0}:{1} {2}".format(query_prefix, prefix_val, keyword)
                else:
                    current_key = "{0}".format(keyword)
                url = GITHUB_API_URL + url_encode(current_key) + "&type=Code"
                self.urls.append(url)
        # 如果 keywords 为空, 但是 dokers 不为空
        if not self.keywords and self.dorkers:
            for dork in self.dorkers:
                # 如果存在查询前缀, 例如 user: 或者 org:
                if query_prefix and prefix_val:
                    current_key = "{0}:{1} {2}".format(query_prefix, prefix_val, dork)
                else:
                    current_key = "{0}".format(dork)
                url = GITHUB_API_URL + url_encode(current_key) + "&type=Code"
                self.urls.append(url)

    def create_query_urls(self):
        """
        构造待请求的URL
        以下构造url，不考虑 pattern-filter
        :return: 例如 2021-01-26 12:56:01
        """

        # 如果存在搜索前缀
        if self.prefix_dict and type(self.prefix_dict) == list:
            for item in self.prefix_dict:
                (key, val), = item.items()
                self.add_query_url(key, val)
        else:
            # 否则添加最基本的查询url
            self.add_query_url(None, None)
        logger.info("Finished create query urls")

    def save_to_csv(self):
        """
        将结果存入csv表格
        """

        res_file = "{0}/{1}_result.csv".format(GITHUB_SEARCH_RESULTS_PATH, current_time())
        # 再放个表头
        self.results.insert(0, ["url", "count"])
        return save_csv_file(res_file, self.results)
