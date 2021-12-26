#coding=utf-8
# Author: XHS
# Date  : 2021/8/5 18:07
# File  : extractString.py
from common.logger import Logger
import jmespath

global logger
logger=Logger()

def extract_res(expression, response):
    try:
        extract = jmespath.search(expression, response)
        logger.info(f"响应报文提取结果：{extract}")
        return extract
    except Exception as e:
        logger.info(f"响应报文提取异常：{e}")
        return None