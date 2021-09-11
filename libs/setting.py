# Author: p1n93r
# Date  : 2021/01/24
import os

# PROJECT PATH
PRO_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

# DB Setting
DB_HOST = "xx.xx.xx.xx"
DB_USER = "root"
DB_PASS = "xxx"
DB_NAME = "git_monitor"
DB_PORT = 10121
DB_CHARSET = "utf8"


# Email Setting
MAIL_RECEIVERS = ["xxxx@gmail.com", "xxxx@qq.com", ]
MAIL_HOST = "smtp.qq.com"
MAIL_PORT = 465
MAIL_USER = "xxxx@qq.com"
MAIL_PASS = "xxxxxxx"


# Github API Setting
GITHUB_API_URL = 'https://api.github.com/search/code?q='
GITHUB_SEARCH_URL = 'https://github.com/search?q='
# Github dorker file path
GITHUB_SEARCH_DORKS_FILE_PATH = os.path.join(PRO_PATH, "dict")
# Github token file path
GITHUB_TOKEN_FILE_PATJ = os.path.join(PRO_PATH, "config")
# Aimed Targets
GITHUB_SEARCH_TARGETS_FILE_PATH = os.path.join(PRO_PATH, "targets")
# Results Path
GITHUB_SEARCH_RESULTS_PATH = os.path.join(PRO_PATH, "results")


