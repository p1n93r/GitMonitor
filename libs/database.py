# Author: p1n93r
# Date  : 2021/01/24

import pymysql

from libs.log import logger


class DataBase:
    def __init__(self, host, user, password, database, port=3306, charset='utf8'):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.charset = charset

        self.db = self.connect()
        self.cursor = self.db.cursor()

    def __del__(self):
        self.close()

    def connect(self):
        logger.info("Connecting to the database")
        try:
            db = pymysql.connect(host=self.host,
                                 port=self.port,
                                 user=self.user,
                                 password=self.password,
                                 database=self.database,
                                 charset=self.charset)
            return db
        except Exception as err:
            logger.error(err)

    def close(self):
        try:
            self.cursor.close()
            self.db.close()
        except Exception as err:
            print(err)

    def commit(self):
        self.db.commit()

    def execute(self, sql, params=()):
        try:
            result = self.cursor.execute(sql, tuple(params))
            self.commit()
        except Exception as err:
            logger.error(err)

    def query(self, sql, params=(), row="all"):
        try:
            self.cursor.execute(sql, tuple(params))
            if row == "all":
                ret = self.cursor.fetchall()
            elif row == "one":
                ret = self.cursor.fetchone()
            elif isinstance(row, int):
                ret = self.cursor.fetchmany(row)
            else:
                logger.error("number must be 'one' 'all' or a number")
                ret = ()
            return ret
        except Exception as err:
            logger.error(err)

    def insert(self, table, data):
        try:
            fields = ",".join(["".join(["`", column, "`"]) for column in data.keys()])
            values = ",".join(["%s" for i in range(len(data.keys()))])
            sql = "INSERT INTO `{}` ({}) VALUES ({})".format(table, fields, values)
            params = [data[key] for key in data.keys()]
            self.execute(sql, params)
        except Exception as err:
            logger.error(err)

    def update(self, table, data, condition=dict):
        try:
            fields = []
            for key in data.keys():
                fields.append("`{}` = %s".format(key, data[key]))
            fields2 = []
            for key in condition.keys():
                fields2.append("`{}` = %s".format(key))
            sql = "UPDATE `{}` SET {} WHERE {}".format(table, ",".join(fields), ",".join(fields2))
            params = [data[key] for key in data.keys()] + [condition[key] for key in condition.keys()]
            self.execute(sql, params)
        except Exception as err:
            logger.error(err)

    def find(self, table, condition=dict, columns=["*"], row="all", operator="="):
        try:
            fields = []
            for key in condition.keys():
                fields.append("`{}` {} %s".format(key, operator))
            sql = "SELECT {} FROM `{}` WHERE {}".format(",".join(columns), table, " and ".join(fields))
            params = [condition[key] for key in condition.keys()]
            ret = self.query(sql, params, row)
            return ret
        except Exception as err:
            logger.error(err)

    def count(self, table):
        try:
            sql = "SELECT COUNT(*) FROM `{}`".format(table)
            ret = self.query(sql, row="one")
            return ret
        except Exception as err:
            logger.error(err)

    def delete(self, table, condition=dict):
        try:
            fields = []
            for key in condition.keys():
                fields.append("{} = %s")
            sql = "DELETE FROM `{}` WHERE {}".format(table, " and ".join(fields))
            params = [condition[key] for key in condition.keys()]
            self.execute(sql, params)
        except Exception as err:
            logger.error(err)

    def check_insert(self, table, data, condition):
        """
        检查数据是否存在，存在则pass，不存在则插入
        :param condition: 检查条件
        :param table: str, 数据表
        :param data: dict, 字典格式的数据 (键: 列名, 值: 列值)
        :return: 无返回值
        """
        if self.find(table=table, condition=condition):
            return False
        else:
            self.insert(table=table, data=data)
            return True
