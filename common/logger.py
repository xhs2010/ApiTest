#coding=utf-8
# Author: XHS
# Date  : 2021/5/13 11:29
# File  : logger.py

import logging, time
import os

log_path = (os.path.dirname((os.path.dirname(__file__)))+'/logs')
if not os.path.exists(log_path):os.mkdir(log_path)   #不存在，则创建logs

class Logger(object):
    def __init__(self):
        # 命名
        self.logname = os.path.join(log_path, '%s.log' % time.strftime('%Y%m%d%H%M', time.localtime(time.time())))

        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        # 格式
        self.formatter = logging.Formatter('[%(asctime)s] - %(filename)s] - %(levelname)s: %(message)s')

    def __console(self, level, message):
        # FileHandler 写入文件
        #fh = logging.FileHandler(self.logname, 'a')  # 追加模式  python2
        fh = logging.FileHandler(self.logname, 'a', encoding='utf-8')  # 追加模式，python3
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(self.formatter)
        self.logger.addHandler(fh)

        # StreamHandler,控制台输出
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(self.formatter)
        self.logger.addHandler(ch)

        if level == 'info':
            self.logger.info(message)
        elif level == 'debug':
            self.logger.debug(message)
        elif level == 'warning':
            self.logger.warning(message)
        elif level == 'error':
            self.logger.error(message)
        #
        self.logger.removeHandler(ch)  #
        self.logger.removeHandler(fh)  #

        fh.close()

    def debug(self, message):
        self.__console('debug', message)

    def info(self, message):
        self.__console('info', message)

    def warning(self, message):
        self.__console('warning', message)

    def error(self, message):
        self.__console('error', message)


# if __name__ == "__main__":
#    log = Logger()
#    log.info("-------")
#    log.warning("aaa")



