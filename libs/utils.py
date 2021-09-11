# Author: P1n93r
# Date  : 2021/09/04
import os
import requests
import time
import csv

from libs.log import logger


def current_time():
    """
    返回当前时间
    """
    return time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())


def url_encode(param):
    """
    url编码请求参数，只编码关键字符
    """
    param = param.replace(':', '%3A')
    param = param.replace('"', '%22')
    param = param.replace(' ', '+')
    return param


def get_content_with_path(path):
    """
    获取某个文件夹下的所有文件的内容，返回一个列表
    """
    files = os.listdir(path)
    res = []
    for current_file in files:
        if not os.path.isdir(current_file):
            f = open(path + "/" + current_file)
            iterator_line = iter(f)
            for line in iterator_line:
                res.append(line.strip())
    return res


def request_with_header(url, headers):
    # 可能需要设置代理才能访问 github
    # proxies = {'http': 'http://localhost:10809', 'https': 'http://localhost:10809'}
    r = requests.get(url, headers=headers, timeout=5)
    return r.json()


def save_csv_file(file, data):
    if not file or not data:
        logger.error("save_csv_file() 's file and data must not None")
    if type(data) != list:
        logger.error("save_csv_file() 's data must be an List, "
                     "such as [{'oneColumn', 'twoColumn'}, {'oneData', 'twoData'}]")
    with open(file, "w", encoding="UTF-8", newline="") as csv_file:
        res_file = csv.writer(csv_file)
        # data的第一行为表头
        headers = data.pop(0)
        res_file.writerow(headers)
        res_tmp = []
        for item in data:
            tmp = []
            for header in headers:
                tmp.append(item[header])
            res_tmp.append(tmp)
        res_file.writerows(res_tmp)
        logger.info("save_csv_file() finished save file: {0}".format(file))
    return file
