#!/usr/bin/python3
# coding=utf-8
# Author: p1n93r
# Date  : 2021/09/03

from libs.log import logger
from libs.mail import SMTP
from libs.setting import MAIL_RECEIVERS, GITHUB_SEARCH_DORKS_FILE_PATH, GITHUB_TOKEN_FILE_PATJ, \
    GITHUB_SEARCH_TARGETS_FILE_PATH, MAIL_HOST, MAIL_USER, MAIL_PASS, MAIL_PORT
from libs.git_dorker import GitSearch
from libs.utils import get_content_with_path

if __name__ == '__main__':
    # 获取 dokers
    dorkers = get_content_with_path(GITHUB_SEARCH_DORKS_FILE_PATH)

    # 获取 github tokens
    tokens = get_content_with_path(GITHUB_TOKEN_FILE_PATJ)

    # 获取 targets 作为keywords
    targets = get_content_with_path(GITHUB_SEARCH_TARGETS_FILE_PATH)

    try:
        git_search = GitSearch(tokens=tokens, keywords=targets, dorkers=dorkers, prefix_dict=None)
        res = git_search.start_search()
        if res['res']:
            # 发个邮件提醒下
            logger.info("ready to send email tips, res_file: {0}".format(res['res_file']))
            msg = "本次监控，共发现 <span style=\"color:red\">{0}</span> 个新增结果，请查收~".format(len(res['res']))
            smtp = SMTP(mail_host=MAIL_HOST, mail_user=MAIL_USER, mail_pass=MAIL_PASS, mail_port=MAIL_PORT)
            smtp.send_with_attachment(msg, MAIL_RECEIVERS, res['res_file'])
    except Exception as e:
        logger.error("GitSearch has an error : {0}".format(e))
