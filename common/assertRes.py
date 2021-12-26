#coding=utf-8
# Author: XHS
# Date  :2021/11/12 16:31
# File  : assertRes.py
from common.logger import Logger
global logger
import json
logger=Logger()
class assertRes:

    def assert_code(self, actual_code, expected_code):

        """
        功能:验证状态码相等
         actual_code 返回状态码
         expected_code 预期状态码
        """
        try:
            assert actual_code == expected_code
            logger.info("断言成功,状态码正确,预期结果: %s,实际结果: %s." % (expected_code, actual_code))

        except:
            logger.info("断言失败,状态码错误,预期结果: %s,实际结果: %s." % (expected_code, actual_code))
            raise


    def assert_contains_string(self, res_str, expected_str):
        """
        功能：验证响应内容中包含预期字符串
         res_str 请求响应字符串
         expected_str 预期字符串
        """
        try:
            res_str = json.dumps(res_str, ensure_ascii=False)
            assert expected_str in res_str
            logger.info("断言成功,请求响应包含字符串:%s."%expected_str)
        except:
            logger.info("断言失败,请求响应未包含字符串:%s." % expected_str )
            raise

    def assert_equal_string(self,  expected_str,actual_str):
        """
        功能：验证响应内容中的字符串相等
        res_str 请求响应字符串
        expected_str 预期字符串
        """
        try:
            assert expected_str==actual_str
            logger.info("断言成功,字符串相等,预期字符串:%s，实际字符串:%s." %(expected_str ,actual_str))
        except:
            logger.info("断言失败,字符串不相等,预期字符串:%s，实际字符串:%s." %(expected_str ,actual_str))
            raise
