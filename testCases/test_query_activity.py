#coding=utf-8
#Author: XHS
#Date:2021/12/14 10:06
#File:test_query_activity.py
from common import assertRes
from common.yamlTools import YamlTools
from common.logger import Logger
from common.methodTools import RequestTools
import allure
import pytest

'''
   脚本功能：使用@pytest.mark.parametrize读取YAML文件实现参数化，查询活动并断言。
   主要场景：
   1.正确的活动ID
   2.错误的活动ID
   3.活动ID为空
   4.活动ID模糊查询
   '''
@allure.severity(allure.severity_level.NORMAL)
@allure.epic("活动中心")
@allure.feature("查询活动列表")
class TestActivityCenter:
    global logger
    logger = Logger()

    @pytest.mark.parametrize("activity_center_info", YamlTools().read_yaml('query_activity.yml'))
    def test_ActivityCenter(self, activity_center_info,read_token): #OK

        token = read_token
        logger.info("开始加载测试数据...")
        url = activity_center_info['request']['url']
        header = activity_center_info['request']['headers']
        header['authorization']=token
        method = activity_center_info['request']['method']
        data = activity_center_info['request']['data']
        logger.info("测试数据加载完成！")
        logger.info("开始发送接口请求...")
        try:
            query_res = RequestTools().send_requests(method=method, url=url, data=data, header=header)
            #logger.info("接口请求发送成功！")
            #logger.info("请求数据:url:{}, headers:{}, method:{},  data:{}".format(url, header, method, data))
            #logger.info(f'查询活动请求响应结果:{query_res}')

            total=query_res['result']['total']   #获取活动总数
            if total==1:
                #等于1,精确查询
                logger.info(f'活动总数：{total}')
                logger.info("查询活动返回活动ID：" + query_res['result']['data'][0]['activityId'])
                actual_code = query_res['errorCode'] #获取返回状态码

                #调用外部函数断言
                assertRes.assertRes().assert_code(actual_code, "00000")  # 断言状态码,预期00000 ，
                assertRes.assertRes().assert_contains_string(query_res, '一切 ok')
                assertRes.assertRes().assert_equal_string(query_res['result']['data'][0]['activityId'],'HD100770')

            elif total > 1:
                # 大于1，模糊查询或活动ID为空

                logger.info(f'活动总数：{total}')
                actual_code = query_res['errorCode']  # 获取返回状态码
                assertRes.assertRes().assert_contains_string(query_res, '一切 ok')  # '一切 ok'
                assertRes.assertRes().assert_code(actual_code, "100000")  # 断言状态码,预期100000

            else:
                logger.info('活动不存在！')

        except Exception as e:
                logger.info(f"断言失败或发生异常! {e}")
                raise

