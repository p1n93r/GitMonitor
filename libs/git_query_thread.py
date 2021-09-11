#!/usr/bin/python3
# coding=utf-8
# Author: p1n93r
# Date  : 2021/09/03

from threading import Thread

from time import sleep

from libs.log import logger
from libs.utils import request_with_header


class GitQueryThread(Thread):
    """
    每个线程代表一个 Github Token，最多可以每分钟请求 30 次
    """

    def __init__(self, thread_id, urls, token):
        Thread.__init__(self)
        self.thread_id = thread_id
        self.urls = urls
        self.token = token
        self.result = []
        self.error_urls = []
        logger.info("{0} thread has initialized, current target urls length : {1}".format(thread_id, len(urls)))

    def run(self):
        for item in self.urls:
            headers = {"Authorization": "token {0}".format(self.token)}
            try:
                res_json = request_with_header(item, headers=headers)
                # logger.info("request : {0}, returns {1}".format(item,res_json))
                if 'documentation_url' in res_json:
                    self.error_urls.append(item)
                    logger.error("thread_id : {0},request {1} occurred an error[documentation_url] : {2}".format(self.thread_id, item, res_json['documentation_url']))
                elif res_json['total_count'] != 0:
                    self.result.append({"url": item, "count": res_json['total_count']})
            except Exception as e:
                self.error_urls.append(item)
                logger.error("thread_id : {0},request {1} occurred an error : {2}".format(self.thread_id, item, e))

    def get_res(self):
        return self.result

    def get_thread_id(self):
        return self.thread_id

    def get_error_urls(self):
        return self.error_urls
