#coding=utf-8
#Author: XHS
#Date: 2021/8/11 16:43
#File: test_activity_operation_flow.py
import requests
from common import assertRes
from common.methodTools import RequestTools
import allure
import pytest
from common.operateMongoDB  import *
from common.extractString import extract_res
import random

global logger
logger=Logger()

'''数据库初始化'''
global db
db = OperationMongoDB('host', 'port', 'username',
                             'password', 'authSource',
                             'dbname')


''' case_teardown终结函数：清理测试环境 '''
@pytest.fixture()
def case_teardown(request):
    def teardown():
        logger.info('开始清理测试环境...')
        db.delete_data_one('activities', 'activity_id', IDW)
        db.close_connect()
    request.addfinalizer(teardown)


''' 模块：活动中心
    功能：活动相关接口业务流程验证。包括：
    1.新增活动接口、添加规则接口，审核活动接口，查询活动接口。'''

@allure.feature("活动中心业务流程用例")
@allure.severity(allure.severity_level.NORMAL)
class TestIntegrationActivity:
    a_name=random.randint(1000,9999)  #生成随机整数
    global activity_name
    activity_name='activity_name'+str(a_name)

    '''新增活动接口'''
    @pytest.mark.run(order=1)
    @allure.title("新增")
    @allure.step("步骤1:新增活动")
    def test_create_activity(self,read_token):
        logger.info("开始执行创建活动用例...")
        url = "https://" #
        global headers
        headers = {'content-type': 'application/json;charset=UTF-8', 'Connection': 'close'}
        global token
        token=read_token
        headers['authorization'] = token
        method = 'POST'
        data = {

            "name": activity_name,
            "startTime": "2021-10-12T07:30:20.000Z",   #开始时间必须大于当前时间，否则不能审核通过，只能审核拒绝
            "endTime": "2026-08-12T07:30:20.000Z",
            "description": activity_name,
        }

        # 发送请求
        global  c_res
        c_res = RequestTools().send_requests(method=method, url=url, data=data, header=headers)
        logger.info('创建活动请求发送成功！')


         #提取id，内部id
        global expression_id,expression_IDW
        expression_id = 'result.id'
        expression_IDW = 'result.activity_id'
        global id
        id = extract_res(expression_id, c_res)

        #IDW，活动ID,如HD100510'
        global IDW
        IDW = extract_res(expression_IDW, c_res)
        logger.info(f'活动的外部ID：{IDW}')


        '''查询数据库，断言活动ID是否与请求返回的活动ID一致'''
        db_result=db.select_data_one('activities', 'activity_id', IDW)
        #print(db_result)
        try:
            #IDW='HXX'
            assert IDW == db_result['activity_id'], '断言失败，数据库不存在该记录!'  # 如不相等，则提示
            logger.info('断言成功!')
            db.close_connect()
        except Exception as e:
            logger.info(f'断言异常消息:{e}')
            db.close_connect()  #关闭


    '''查询活动接口'''
    @pytest.mark.run(order=2)
    @allure.title("查询活动")
    def test_query_activity(self):
        logger.info("开始执行查询活动用例...")
        method="POST"
        data={"activityId":IDW,

                  "download": "false",
                  "limit": 10,
                  "page": 1,
                  "utcOffset": 8}

        url='https://'
        query_res = RequestTools().send_requests(method=method, url=url, data=data, header=headers)  #请求响应结果
        logger.info(f'查询活动请求响应结果:{query_res}')
        print("查询活动返回的活动ID："+query_res['result']['data'][0]['activityId'])

        # '''直接使用assert断言'''
        # # assert query_res['errorCode'] == "00000"
        # # assert query_res['result']['data'][0]['activityId']==IDW
        # # print('查询成功，与新增的活动ID一致！')

        '''调用外部断言函数断言'''
        actual_code = query_res['errorCode']      #获取响应状态码
        assertRes.assertRes().assert_code(actual_code, "00000")    # 断言状态码，预期状态码"00000"
        assertRes.assertRes().assert_contains_string(query_res, '一切 ok')  # 断言请求响应信息包含字符串
        assertRes.assertRes().assert_equal_string(query_res['result']['data'][0]['activityId'],IDW)# 断言请求响应信息的字符串完全相等


    '''添加活动规则-有规则'''
    @allure.title("添加达标规则")
    @allure.step("步骤2:添加规则")
    @pytest.mark.run(order=3)
    def test_add_rules(self):
        logger.info("开始执行添加活动规则用例...")
        url='https://'+str(id)
        data = {'hasRule': 1,     #达标条件：有
                'rules': [

                {
                    'conditions': {'regTime': {'from': '2021-08-20T16:00:00.000Z', 'to': '2021-08-21T15:59:59.000Z'},
                                   'submitTime': {'from': "2021-10-12T07:30:20.000Z", 'to': "2026-08-12T07:30:20.000Z"}},
                    'coupons': ['KQ100242'],
                    'distributeRules': [{'field': "USER_TRIGGER", 'condition': "EQ", 'value': 1},
                                        {'field': "COUPON_COUNT", 'condition': "EQ", 'value': 10000},
                                        {'field': "DAY_COUPON_COUNT", 'condition': "EQ", 'value': 500}
                                        ],
                    'hasDistribute': True,   # 派发条件：有
                    'target': {}
                        }
                ]
                }

        # 发送请求
        add_res = requests.put(url=url, json=data, headers=headers)
        logger.info(f'添加活动规则响应结果:{add_res}')
        expression_code = "errorCode"
        code = extract_res(expression_code, add_res)
        logger.info(f'添加活动规则响应状态码：{code}')


    '''审核活动通过 OK '''

    @pytest.mark.run(order=4)
    @allure.title("审核通过")
    @allure.step("步骤3:审核活动-通过")
    def test_approval_activity(self,case_teardown): #清理
        logger.info("开始执行审核活动用例...")

        data = {'activityAuditStatus': 'approval',
                'ids': [str(id),]}
        url = 'https://'
        approval_res = requests.patch(url=url, json=data, headers=headers)
        print(approval_res)
        # 获取errorCode
        expression_code = "errorCode"
        code = extract_res(expression_code, approval_res)
        print(f'审核通过响应状态码：{code}')


    # @pytest.mark.run(order=4)
    # @allure.title("审核拒绝")
    # @allure.step("步骤3:审核活动-拒绝")
    # def test_approval_activity(self):
    #     # token = read_token
    #     # headers = {'content-type': 'application/json;charset=UTF-8',
    #     #            'authorization': token}
    #     data = {'activityAuditStatus': 'reject',
    #             'ids': [str(id),]}
    #     url = 'https://'
    #     res = requests.patch(url=url, json=data, headers=headers)
    #     print(res)
    #     # 获取errorCode
    #     expression_code = "errorCode"
    #     code = extract_res(expression_code, res)
    #     print(f'审核通过响应状态码是：{code}')



