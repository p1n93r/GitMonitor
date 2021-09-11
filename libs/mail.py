# Author: p1n93r
# Date  : 2021/01/24
import os
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import time
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from libs.log import logger

FROM = "P1n93r"
SUBJECT = "GitMonitor-Result-%s" % time.strftime("%Y-%m-%d", time.localtime())


class SMTP:

    def __init__(self, mail_host, mail_port, mail_user, mail_pass):
        self.host = mail_host
        self.port = mail_port
        self.user = mail_user
        self.password = mail_pass
        self.smtp = smtplib.SMTP_SSL(self.host)
        self.smtp.login(self.user, self.password)

    @staticmethod
    def build_mail(msg, to):
        mail = MIMEText(msg, 'html', 'utf-8')
        mail['From'] = Header(FROM)
        mail['To'] = Header(to)
        mail['Subject'] = Header(SUBJECT)
        return mail

    @staticmethod
    def build_mail_with_attachment(msg, to, file_path):
        mail = MIMEMultipart()
        mail['From'] = Header(FROM)
        mail['To'] = Header(to)
        mail['Subject'] = Header(SUBJECT)
        mail.attach(MIMEText(msg, 'html', 'utf-8'))
        # 构造附件
        # 添加附件就是加上一个MIMEBase
        with open(file_path, 'rb') as f:
            # 设置附件的MIME和文件名，这里是png类型:
            mime = MIMEBase('application', 'octet-stream')
            # 加上必要的头信息:
            mime.add_header('Content-Disposition', 'attachment', filename=os.path.split(file_path)[1])
            mime.add_header('Content-ID', '<0>')
            mime.add_header('X-Attachment-Id', '0')
            # 把附件的内容读进来:
            mime.set_payload(f.read())
            # 用Base64编码:
            encoders.encode_base64(mime)
            # 添加到MIMEMultipart:
            mail.attach(mime)
        return mail

    def send(self, msg, tolist):
        for addr in tolist:
            mail = self.build_mail(msg, addr)
            self.smtp.sendmail(self.user, addr, mail.as_string())

    def send_with_attachment(self, msg, tolist, file_path):
        for addr in tolist:
            mail = self.build_mail_with_attachment(msg, addr, file_path)
            self.smtp.sendmail(self.user, addr, mail.as_string())
