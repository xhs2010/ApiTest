#coding=utf-8
#Author:XHS
#Date:2022/1/9 10:35
#File:test_record_flow.py
import requests
from common import assertRes
import allure
import pytest
from common.yamlTools import YamlTools
from common.operateMySQL import  OperationMySQL
from common.operateMongoDB  import *
from common.extractString import extract_res
import random
from common.methodTools import RequestTools
import time

#用例执行完成，删除指定电话的活动记录
global phone
phone='13515000000'
@pytest.fixture()
def teardown(request):
    def del_activity():
        try:
            logger.info('用例执行完成，开始清理CRM测试数据...')
            db.delete_data_many('table', 'phone', phone)
            db.close_connect()
        except Exception as  e:
            logger.info(f'删除失败！{e}')
            db.close_connect()
            raise
    request.addfinalizer(del_activity)

#用例执行前，清除指定用户活动记录
@pytest.fixture()
def clear_someone_record():
    try:
        logger.info('执行用例前，删除CRM活动记录...')
        db.delete_data_many('table', 'phone', phone)
        db.close_connect()
        #删除中台数据
        my_eddid=''
        sql_delete_coupon = f"delete from XX  where=\'{my_eddid}\'"
        sql_delete_subscribe = f"delete from xx  where  xx=\'{my_eddid}\'"
        sql_delete_subscribe_new = f"delete from XX  where XX=\'{my_eddid}\'"
        #logger.info(f'拼接sql:{sql_delete}')
        global myl_db
        myl_db = OperationMySQL()
        myl_db.MySQL_delete_data_one(sql_delete_coupon)
        myl_db.MySQL_delete_data_one(sql_delete_subscribe)
        myl_db.MySQL_delete_data_one(sql_delete_subscribe_new)
    except Exception as  e:
        logger.info(f'删除失败！{e}')
        db.close_connect()
        raise

class TestActivityRecord:
    global local_date,effectStartTime,convertDeadline
    local_date = time.strftime('%Y-%m-%d', time.localtime())
    effectStartTime = local_date + "T01:19:19.294+00:00"
    convertDeadline = local_date + 'T15:50:50.999+00:00'
    global logger, con_url,phone
    phone='13515000000'      
    con_url = YamlTools().read_environment_yaml()  # 读取environment配置文件的域名端口号
    logger.info(f'environment文件之con_url:{con_url}')
    #数据库初始化
    global db
    db = OperationMongoDB(' ', 3717, ' ',
                          ' ', ' ',
                          ' ')
    ''' 模块：活动记录
        功能：验证活动记录模块业务主流程的相关接口。包括：1.新增、编辑、查询、审核拒绝、审核成功        2.批量操作
    '''

    ############################# QuoteCard-添加-删除 ####################
    #使用客户编号添加QuoteCard
    @pytest.mark.run(order=1)
    @allure.title("添加QuoteCard-客户编号")
    def test_add_record_accountNumber(self,read_token,clear_someone_record):
        global  quote_phone_a, quote_accountNumber_a, quote_remark_a, quote_activityId_a, quote_ruleId_a, quote_couponId_a
        quote_accountNumber_a = '501092'  # 客户编号
        quote_remark_a = 'test'  # 备注
        quote_activityId_a = 'HD100786'  # 活动ID
        quote_ruleId_a = 'GZ100088'  # 规则ID
        quote_couponId_a = 'KQ100002'  # 卡券ID
        logger.info("开始执行添加活动记录用例...")
        url = con_url+"url"
        global headers
        headers = {'content-type': 'application/json;charset=UTF-8', 'Connection': 'close'}
        global token
        token = read_token
        headers['authorization'] = token
        method = 'POST'
        data={
                "activityId": quote_activityId_a,
                "ruleId":quote_ruleId_a,
                "accountNumbers": [quote_accountNumber_a],  #可添加多个客户编号
                "couponId": quote_couponId_a,
                "remark": quote_remark_a
                }
        # 发送请求

        global quote_add_res_a,quote_id_a
        quote_add_res_a = RequestTools().send_requests(method=method, url=url, data=data, header=headers)
        quote_id_a=quote_add_res_a['result']['id']
        logger.info('添加QuoteCard请求发送成功！')
        logger.info('添加QuoteCard响应结果res：{}'.format(quote_add_res_a))
        logger.info(f'添加QuoteCard返回id:{quote_id_a}')
        #调用外部断言函数断言
        try:
            actual_code = quote_add_res_a['errorCode']  # 获取响应状态码
            assertRes.assertRes().assert_code(actual_code, "00000")  # 断言状态码，预期状态码"00000"

            assertRes.assertRes().assert_equal_string(quote_add_res_a['result']['activity_id'],
                                                      quote_activityId_a)  # 断言活动ID
            assertRes.assertRes().assert_equal_string(quote_add_res_a['result']['account_number'],
                                                      quote_accountNumber_a)  # 断言请求响应信息的字符串完全相等
            assertRes.assertRes().assert_equal_string(quote_add_res_a['result']['audit_status'],'notAudit') #待审核
            logger.info('使用客户编号添加QuoteCard，断言成功!')
        except Exception as e:
            logger.info(f'使用客户编号添加QuoteCard，断言失败!{e}')
            raise

    #删除QuoteCard
    @pytest.mark.run(order=2)
    @allure.title('删除QuoteCard活动记录-客户编号')
    def test_record_del_accountNumber(self,read_token):
        logger.info("开始执行删除活动记录用例...")
        url = con_url + "url/"+str(quote_id_a)
        global headers
        headers = {'content-type': 'application/json;charset=UTF-8', 'Connection': 'close'}
        global token
        token = read_token
        headers['authorization'] = token
       # 发送请求
        global quote_del_res_a
        quote_del_res_a=requests.delete(url=url,headers=headers)
        del_res_a=quote_del_res_a.json()
        logger.info('删除QuoteCard活动记录请求发送成功！')
        logger.info('删除QuoteCard活动记录响应结果res：{}'.format(quote_del_res_a))

        #调用外部断言函数断言
        try:
            actual_code_a = del_res_a['errorCode']  # 获取响应状态码
            assertRes.assertRes().assert_code(actual_code_a, "00000")  # 断言状态码，预期状态码"00000"
            logger.info('删除QuoteCard活动记录，断言成功!')
        except Exception as e:
            logger.info(f'删除QuoteCard活动记录，断言失败!{e}')
            raise


    ##################### QuoteCard-添加-审核通过-同步卡券-兑换申请中-已兑换 ##################
    # #手机号码添加活动记录OK
    @pytest.mark.run(order=3)
    @allure.title("添加QuoteCard-手机号码")
    def test_add_quote_record_phone_p(self, read_token,clear_someone_record):
        global quote_phone_p, quote_accountNumber_p, quote_remark_p, quote_activityId_p, quote_ruleId_p, quote_couponId_p
        quote_accountNumber_p = '501092'  # 客户编号
        quote_remark_p = 'test'  # 备注
        quote_activityId_p = 'HD100786'  # 活动ID
        quote_ruleId_p = 'GZ100088'  # 规则ID
        quote_couponId_p = 'KQ100002'  # 卡券ID
        logger.info("开始执行添加QuoteCard活动记录用例...")
        url = con_url + "url"
        global headers
        headers = {'content-type': 'application/json;charset=UTF-8', 'Connection': 'close'}
        global token
        token = read_token
        headers['authorization'] = token
        method = 'POST'
        data = {
            "activityId": quote_activityId_p,
            "ruleId": quote_ruleId_p,
            "phones": [phone],  # 可添加多个客户编号
            "couponId": quote_couponId_p,
            "remark": quote_remark_p
        }
        # 发送请求

        global quote_add_res_p, quote_id_p
        quote_add_res_p = RequestTools().send_requests(method=method, url=url, data=data, header=headers)
        quote_id_p = quote_add_res_p['result']['id']
        logger.info('添加QuoteCard请求发送成功！')
        logger.info('添加QuoteCard响应结果res：{}'.format(quote_add_res_p))
        logger.info(f'添加QuoteCard返回id:{quote_id_p}')
        # 调用外部断言函数断言
        try:
            actual_code = quote_add_res_p['errorCode']  # 获取响应状态码
            assertRes.assertRes().assert_code(actual_code, "00000")  # 断言状态码，预期状态码"00000"

            assertRes.assertRes().assert_equal_string(quote_add_res_p['result']['activity_id'],
                                                      quote_activityId_p)  # 断言活动ID
            assertRes.assertRes().assert_equal_string(quote_add_res_p['result']['phone'],
                                                      phone)  # 断言请求响应信息的字符串完全相等
            assertRes.assertRes().assert_equal_string(quote_add_res_p['result']['audit_status'], 'notAudit')  # 待审核
            logger.info('使用手机号码添加QuoteCard，断言成功!')
        except Exception as e:
            logger.info(f'使用手机号码添加QuoteCard，断言失败!{e}')
            raise

    #审核QuoteCard活动记录-通过OK
    @pytest.mark.run(order=4)
    @allure.title("QuoteCard-活动记录审核通过")
    def test_quote_record_approval_p(self, read_token):
        logger.info("开始执行审核QuoteCard活动记录用例...")
        url = con_url + 'url/audit'
        global headers
        headers = {'content-type': 'application/json;charset=UTF-8', 'Connection': 'close'}
        global token
        token = read_token
        headers['authorization'] = token
        method = 'POST'
        data = {
            'ids': [quote_id_p],
            'type': 'quote',
            'auditStatus': 'approval'
                }

        # 发送请求
        quote_approval_res_p = RequestTools().send_requests(method=method, url=url, data=data, header=headers)
        logger.info('审核QuoteCard活动记录，请求发送成功！')
        logger.info('审核QuoteCard活动记录响应结果res：{}'.format(quote_approval_res_p))

        # 调用外部断言函数断言
        try:
            actual_code = quote_approval_res_p['errorCode']  # 获取响应状态码
            assertRes.assertRes().assert_code(actual_code, "00000")  # 断言状态码，预期状态码"00000"
            assert  quote_approval_res_p['result']==True
            time.sleep(1)

            #查询CRM数据库审核状态
            se_res_p = db.select_data_one('table', 'phone', phone)
            status = se_res_p['audit_status']
            logger.info(f'查询数据库审核状态为:{status}')
            assert status == 'approval'
            logger.info('审核QuoteCard活动记录-通过，断言成功!')

            global _id_quote_p,record_id_quote_p,coupon_id_quote_p,coupon_name_quote_p,coupon_type_quote_p ,idp_user_id_quote_p
            record_id_quote_p=se_res_p['record_id'] #原record_id
            coupon_id_quote_p=se_res_p['coupon_id']  #卡券ID
            coupon_name_quote_p=se_res_p['coupon_name'] #卡券名称
            idp_user_id_quote_p=se_res_p['idp_user_id'] #对应账户中心eddid_id
            logger.info(f'卡券ID:{coupon_id_quote_p}')
            logger.info(f'卡券名称:{coupon_name_quote_p}')
            logger.info(f'eddid:{idp_user_id_quote_p}')
        except Exception as e:
            logger.info(f'审核QuoteCard活动记录-通过，断言失败!{e}')
            raise

    #调用账户中心接口手动同步QuoteCard,修改CRM同步状态OK
    @pytest.mark.run(order=5)
    @allure.title('调用账户中心接口手动同步QuoteCard')
    def test_quote_Sync_accountCenter_p(self):
        accountCenter_url = 'url
        global headers
        headers = {'content-type': 'application/json'}
        logger.info("开始发送CRMQuoteCard同步请求...")
        data = {
            "list": [
                {
                    'convertDeadline': convertDeadline,
                    'convertTime': None,
                    'convertWay': 'MANUAL',  # 兑换方式 ，手动
                    'couponDescription': 'test',
                    'couponId': coupon_id_quote_p,  # "KQ100002",coupon_id
                    'couponInstruction': 'test',
                    'couponName': coupon_name_quote_p,  # 
                    "couponType": 'QUOTE',  # "QUOTE" 卡券类型
                    "deductionCode": None,
                    "discountCode": None,
                    "eddid": idp_user_id_quote_p,
                    "effectStartTime":  effectStartTime,
                    "financingCode": None,
                    "freeCommissionType": None,
                    "freeCommissionTypeTime": None,
                    "freeCommissionTypeTimeUnit": None,
                    "iconList": [],
                    "orderId": str(record_id_quote_p),  #
                    "quoteComboCode": "111111",  # 行情套餐ID
                    "status": "NOTCONVERT",  # 未兑换
                    "welfareCode": None,
                    "welfareCurrency": None,
                    "welfareType": None,
                    "welfareValue": None
                }
            ]
        }

        # 发送请求
        import json
        data=json.dumps(data)
        global approval_res
        approval_res=requests.post(url=accountCenter_url,data=data,headers=headers)
        approval_res=approval_res.json()
        logger.info('同步QuoteCard活动记录，请求发送成功！')
        logger.info('同步QuoteCard活动记录响应结果res：{}'.format(approval_res))

        #断言响应结果
        assert approval_res['code']==200
        assert approval_res['data']==None
        logger.info('CRM同步卡券至账户中心,断言成功！')
        time.sleep(2)
        # 查询账户中心同步数据
        try:
            # 查询数据库断言是否成功同步至账户中心
            sql_query = f"SELECT *From XX  a  where a.xx=\'{record_id_quote_p}\'"
            logger.info(f'拼接sql:{sql_query}')
            global myl_db
            myl_db = OperationMySQL()
            om = myl_db.MySQL_select_data_one(sql_query)
            logger.info(f'CRM向账户中心同步卡券结果：{om}')
            assert om==True
            logger.info('CRM同步卡券至账户中心，断言成功！')

            db.update_data_is_synced('table',record_id_quote_p)
            logger.info('成功更新CRM同步状态！')
        except Exception as  e:
            logger.info(f'CRM同步卡券至账户中心，断言失败！')
            raise e


    #CRM批量操作QuoteCard-兑换申请中
    @pytest.mark.run(order=6)
    @allure.title('批量操作QuoteCard-兑换申请中')
    def test_converting_quoteCard_p(self,read_token):
        url = con_url + 'url'
        global headers
        headers = {'content-type': 'application/json;charset=UTF-8', 'Connection': 'close'}
        global token
        token = read_token
        headers['authorization'] = token
        data={
            "convertStatus": "converting",
                "ids": [quote_id_p],
                "type": "quote"
            }

        global convert_res
        convert_res =requests.patch( url=url, json=data, headers=headers)
        convert_res = convert_res.json()
        logger.info(f'兑换申请中响应结果:{convert_res}')
        #time.sleep(1)
        try:
            actual_code = convert_res['errorCode']  # 获取响应状态码
            assertRes.assertRes().assert_code(actual_code, "00000")  # 断言状态码，预期状态码"00000"
            assert convert_res['result']["nModified"]==1
            global phone
            time.sleep(1)
            # 查询数据库审核状态
            se_res = db.select_data_one('table', 'phone', phone)
            status = se_res['convert_status']
            logger.info(f'查询数据库审核状态为:{status}')
            assert status == 'converting'
            logger.info('批量操作QuoteCard-兑换申请中-通过，断言成功!')
        except Exception as e:
            logger.info(f'批量操作QuoteCard-兑换申请中，断言失败!{e}')
            raise


    # 批量操作QuoteCard--已兑换
    @pytest.mark.run(order=7)
    @allure.title('批量操作QuoteCard-已兑换')
    def test_convert_quoteCard_p(self,read_token,teardown):
        #success
        url = con_url + 'url'
        global headers
        headers = {'content-type': 'application/json;charset=UTF-8', 'Connection': 'close'}
        global quote_id_p
        global token
        token = read_token
        headers['authorization'] = token
        convert_date = time.strftime('%Y-%m-%d', time.localtime())+"T15:59:58.000Z"
        data = {
            "convertStatus": "success",
            "convertTime": convert_date,
            "ids": [quote_id_p],
            "type": "quote"
        }
        logger.info(f'兑换时间：{convert_date}')
        global convert_res
        convert_res = requests.patch(url=url, json=data, headers=headers)
        convert_res = convert_res.json()
        logger.info(f'已兑换响应结果:{convert_res}')

        #time.sleep(1)

        #断言
        try:
            actual_code = convert_res['errorCode']  # 获取响应状态码
            assertRes.assertRes().assert_code(actual_code, "00000")  # 断言状态码，预期状态码"00000"
            assert convert_res['result']["nModified"] == 1
            #time.sleep(1)
            # 查询CRM数据库审核状态
            se_res = db.select_data_one('table', 'phone', phone)
            status = se_res['convert_status']
            logger.info(f'查询数据库审核状态为:{status}')
            assert status == 'success'
            logger.info('批量操作QuoteCard-已兑换-通过，断言成功!')
        except Exception as e:
            logger.info(f'批量操作QuoteCard-已兑换，断言失败!{e}')
            raise

        #删除账户中心数据
        try:
            sql_delete = f"delete from  XX  where xx=\'{record_id_quote_p}\'"
            logger.info(f'拼接sql:{sql_delete}')
            om = myl_db.MySQL_delete_data_one(sql_delete)
            logger.info(f'删除账户中心QuoteCard结果：{om}')
            assert om == True
            logger.info('删除账户中心QuoteCard，断言成功！')
        except Exception as e:
            logger.info(f'删除账户中心QuoteCard，断言失败!{e}')
            raise


# ########################################## QuoteCard 兑换失败  OK ##################################
   # #手机号码添加活动记录OK
    @pytest.mark.run(order=8)
    @allure.title("添加QuoteCard-手机号码")
    def test_add_quote_record_phone_f(self, read_token,clear_someone_record):
        global quote_phone_f, quote_accountNumber_f, quote_remark_f, quote_activityId_f, quote_ruleId_f, quote_couponId_f
        quote_accountNumber_f = '501092'  # 客户编号
        quote_remark_f = 'test'  # 备注
        quote_activityId_f = 'HD100786'  # 活动ID
        quote_ruleId_f = 'GZ100088'  # 规则ID
        quote_couponId_f = 'KQ100002'  # 卡券ID
        logger.info("开始执行添加QuoteCard活动记录用例...")
        url = con_url + "url"
        global headers
        headers = {'content-type': 'application/json;charset=UTF-8', 'Connection': 'close'}
        global token
        token = read_token
        headers['authorization'] = token
        method = 'POST'
        data = {
            "activityId": quote_activityId_f,
            "ruleId": quote_ruleId_f,
            "phones": [phone],  # 可添加多个客户编号
            "couponId": quote_couponId_f,
            "remark": quote_remark_f
        }
        # 发送请求

        global quote_add_res_f, quote_id_f
        quote_add_res_f = RequestTools().send_requests(method=method, url=url, data=data, header=headers)
        quote_id_f = quote_add_res_f['result']['id']
        logger.info('添加QuoteCard请求发送成功！')
        logger.info('添加QuoteCard响应结果res：{}'.format(quote_add_res_f))
        logger.info(f'添加QuoteCard返回id:{quote_id_f}')
        # 调用外部断言函数断言
        try:
            actual_code = quote_add_res_f['errorCode']  # 获取响应状态码
            assertRes.assertRes().assert_code(actual_code, "00000")  # 断言状态码，预期状态码"00000"

            assertRes.assertRes().assert_equal_string(quote_add_res_f['result']['activity_id'],
                                                      quote_activityId_f)  # 断言活动ID
            assertRes.assertRes().assert_equal_string(quote_add_res_f['result']['phone'],
                                                      phone)  # 断言请求响应信息的字符串完全相等
            assertRes.assertRes().assert_equal_string(quote_add_res_f['result']['audit_status'], 'notAudit')  # 待审核
            logger.info('使用手机号码添加QuoteCard，断言成功!')
        except Exception as e:
            logger.info(f'使用手机号码添加QuoteCard，断言失败!{e}')
            raise

    #审核QuoteCard活动记录-通过OK
    @pytest.mark.run(order=9)
    @allure.title("QuoteCard-活动记录审核通过")
    def test_quote_record_approval_f(self, read_token):
        logger.info("开始执行审核QuoteCard活动记录用例...")
        url = con_url + 'url/audit'
        global headers
        headers = {'content-type': 'application/json;charset=UTF-8', 'Connection': 'close'}
        global token
        token = read_token
        headers['authorization'] = token
        method = 'POST'
        data = {
            'ids': [quote_id_f],
            'type': 'quote',
            'auditStatus': 'approval'
                }

        # 发送请求
        quote_approval_res_f = RequestTools().send_requests(method=method, url=url, data=data, header=headers)
        logger.info('审核QuoteCard活动记录，请求发送成功！')
        logger.info('审核QuoteCard活动记录响应结果res：{}'.format(quote_approval_res_f))

        # 调用外部断言函数断言
        try:
            actual_code = quote_approval_res_f['errorCode']  # 获取响应状态码
            assertRes.assertRes().assert_code(actual_code, "00000")  # 断言状态码，预期状态码"00000"
            assert  quote_approval_res_f['result']==True
            time.sleep(1)

            #查询CRM数据库审核状态
            se_res_f = db.select_data_one('table', 'phone', phone)
            status = se_res_f['audit_status']
            logger.info(f'查询数据库审核状态为:{status}')
            assert status == 'approval'
            logger.info('审核QuoteCard活动记录-通过，断言成功!')

            global _id_quote_f,record_id_quote_f,coupon_id_quote_f,coupon_name_quote_f,coupon_type_quote_f ,idp_user_id_quote_f
            record_id_quote_f=se_res_f['record_id'] #原record_id
            coupon_id_quote_f=se_res_f['coupon_id']  #卡券ID
            coupon_name_quote_f=se_res_f['coupon_name'] #卡券名称
            idp_user_id_quote_f=se_res_f['idp_user_id'] #对应账户中心eddid_id
            logger.info(f'卡券ID:{coupon_id_quote_f}')
            logger.info(f'卡券名称:{coupon_name_quote_f}')
            logger.info(f'eddid:{idp_user_id_quote_f}')
        except Exception as e:
            logger.info(f'审核QuoteCard活动记录-通过，断言失败!{e}')
            raise

    #调用账户中心接口手动同步QuoteCard,修改CRM同步状态OK
    @pytest.mark.run(order=10)
    @allure.title('调用账户中心接口手动同步QuoteCard')
    def test_quote_Sync_accountCenter_f(self):
        accountCenter_url = 'url
        global headers
        headers = {'content-type': 'application/json'}
        logger.info("开始发送CRMQuoteCard同步请求...")
        data = {
            "list": [
                {
                    'convertDeadline': convertDeadline,
                    'convertTime': None,
                    'convertWay': 'MANUAL',  # 兑换方式 ，手动
                    'couponDescription': 'test',
                    'couponId': coupon_id_quote_f,  # "KQ100002",coupon_id
                    'couponInstruction': 'test',
                    'couponName': coupon_name_quote_f,  # 
                    "couponType": 'QUOTE',  # "QUOTE" 卡券类型
                    "deductionCode": None,
                    "discountCode": None,
                    "eddid": idp_user_id_quote_f,
                    "effectStartTime":  effectStartTime,
                    "financingCode": None,
                    "freeCommissionType": None,
                    "freeCommissionTypeTime": None,
                    "freeCommissionTypeTimeUnit": None,
                    "iconList": [],
                    "orderId": str(record_id_quote_f),  #
                    "quoteComboCode": "111111",  # 行情套餐ID
                    "status": "NOTCONVERT",  # 未兑换
                    "welfareCode": None,
                    "welfareCurrency": None,
                    "welfareType": None,
                    "welfareValue": None
                }
            ]
        }



        # 发送请求
        import json
        data=json.dumps(data)
        global approval_res
        approval_res=requests.post(url=accountCenter_url,data=data,headers=headers)
        approval_res=approval_res.json()
        logger.info('同步QuoteCard活动记录，请求发送成功！')
        logger.info('同步QuoteCard活动记录响应结果res：{}'.format(approval_res))

        #断言响应结果
        assert approval_res['code']==200
        assert approval_res['data']==None
        logger.info('CRM同步卡券至账户中心,断言成功！')
        time.sleep(2)
        # 查询账户中心同步数据
        try:
            # 查询数据库断言是否成功同步至账户中心
            sql_query = f"SELECT *From XX  a  where a.xx=\'{record_id_quote_f}\'"
            logger.info(f'拼接sql:{sql_query}')
            global myl_db
            myl_db = OperationMySQL()
            om = myl_db.MySQL_select_data_one(sql_query)
            logger.info(f'CRM向账户中心同步卡券结果：{om}')
            assert om==True
            logger.info('CRM同步卡券至账户中心，断言成功！')

            db.update_data_is_synced('table',record_id_quote_f)
            logger.info('成功更新CRM同步状态！')
        except Exception as  e:
            logger.info(f'CRM同步卡券至账户中心，断言失败！')
            raise e


    #CRM批量操作QuoteCard-兑换申请中
    @pytest.mark.run(order=11)
    @allure.title('批量操作QuoteCard-兑换申请中')
    def test_converting_quoteCard_f(self,read_token):
        url = con_url + 'url'
        global headers
        headers = {'content-type': 'application/json;charset=UTF-8', 'Connection': 'close'}
        global token
        token = read_token
        headers['authorization'] = token
        data={
            "convertStatus": "converting",
                "ids": [quote_id_f],
                "type": "quote"
            }

        global convert_res
        convert_res =requests.patch( url=url, json=data, headers=headers)
        convert_res = convert_res.json()
        logger.info(f'兑换申请中响应结果:{convert_res}')
        #time.sleep(1)
        try:
            actual_code = convert_res['errorCode']  # 获取响应状态码
            assertRes.assertRes().assert_code(actual_code, "00000")  # 断言状态码，预期状态码"00000"
            assert convert_res['result']["nModified"]==1
            global phone
            time.sleep(1)
            # 查询数据库审核状态
            se_res = db.select_data_one('table', 'phone', phone)
            status = se_res['convert_status']
            logger.info(f'查询数据库审核状态为:{status}')
            assert status == 'converting'
            logger.info('批量操作QuoteCard-兑换申请中-通过，断言成功!')
        except Exception as e:
            logger.info(f'批量操作QuoteCard-兑换申请中，断言失败!{e}')
            raise


    # CRM批量操作QuoteCard-兑换失败
    @pytest.mark.run(order=12)
    @allure.title('批量操作QuoteCard-兑换失败')
    def test_failed_quoteCard_f(self, read_token,teardown):
        url = con_url + 'url'
        global headers
        headers = {'content-type': 'application/json;charset=UTF-8', 'Connection': 'close'}
        global token
        token = read_token
        headers['authorization'] = token
        data = {
            "convertStatus": "failed",
            "ids": [quote_id_f],
            "type": "quote"
        }

        convert_res = requests.patch(url=url, json=data, headers=headers)
        convert_res = convert_res.json()
        logger.info(f'兑换失败响应结果:{convert_res}')
        # time.sleep(1)
        try:
            actual_code = convert_res['errorCode']  # 获取响应状态码
            assertRes.assertRes().assert_code(actual_code, "00000")  # 断言状态码，预期状态码"00000"
            assert convert_res['result']["nModified"] == 1
            time.sleep(1)
            # 查询数据库审核状态
            se_res = db.select_data_one('table', 'phone',phone)
            status = se_res['convert_status']
            logger.info(f'查询数据库审核状态为:{status}')
            assert status == 'failed'
            logger.info('批量操作QuoteCard-兑换失败，断言成功!')
        except Exception as e:
            logger.info(f'批量操作QuoteCard-兑换失败，断言失败!{e}')
            raise

        #删除账户中心数据
        try:
            sql_delete = f"delete from  XX  where xx=\'{record_id_quote_f}\'"
            logger.info(f'拼接sql:{sql_delete}')
            om = myl_db.MySQL_delete_data_one(sql_delete)
            logger.info(f'删除账户中心QuoteCard结果：{om}')
            assert om == True
            logger.info('删除账户中心QuoteCard，断言成功！')

        except Exception as e:
            logger.info(f'删除账户中心QuoteCard，断言失败!{e}')
            raise

# ########################### QuoteCard-审核拒绝-编辑-审核通过#############################
    # 手机号码添加活动记录
    @pytest.mark.run(order=13)
    @allure.title("添加QuoteCard-手机号码")
    def test_add_quote_record_phone_r(self, read_token, clear_someone_record):
        global quote_phone, quote_accountNumber, quote_remark, quote_activityId, quote_ruleId, quote_couponId
        quote_phone='13515000000'
        quote_accountNumber = '501092'  # 客户编号
        quote_remark = 'test'  # 备注
        quote_activityId = 'HD100786'  # 活动ID
        quote_ruleId = 'GZ100088'  # 规则ID
        quote_couponId = 'KQ100002'  # 卡券ID
        logger.info("开始执行添加QuoteCard活动记录用例...")
        url = con_url + "url"
        global headers
        headers = {'content-type': 'application/json;charset=UTF-8', 'Connection': 'close'}
        global token
        token = read_token
        headers['authorization'] = token
        method = 'POST'
        data = {
                "activityId": quote_activityId,
                "ruleId": quote_ruleId,
                "phones": [quote_phone],
                "couponId": quote_couponId,
                "remark": quote_remark
            }
        # 发送请求

        global  quote_id
        add_res = RequestTools().send_requests(method=method, url=url, data=data, header=headers)
        quote_id = add_res['result']['id']
        logger.info('添加QuoteCard请求发送成功！')
        logger.info('添加QuoteCard响应结果res：{}'.format(add_res))
        logger.info(f'添加QuoteCard返回id:{quote_id}')
        # 调用外部断言函数断言
        try:
            actual_code = add_res['errorCode']  # 获取响应状态码
            assertRes.assertRes().assert_code(actual_code, "00000")  # 断言状态码，预期状态码"00000"

            assertRes.assertRes().assert_equal_string(add_res['result']['activity_id'],
                                                          quote_activityId)  # 断言活动ID
            assertRes.assertRes().assert_equal_string(add_res['result']['phone'],
                                                          phone)  # 断言请求响应信息的字符串完全相等
            assertRes.assertRes().assert_equal_string(add_res['result']['audit_status'], 'notAudit')  # 待审核
            logger.info('使用手机号码添加QuoteCard，断言成功!')
        except Exception as e:
            logger.info(f'使用手机号码添加QuoteCard，断言失败!{e}')
            raise

    # 审核QuoteCard活动记录-拒绝
    @pytest.mark.run(order=14)
    @allure.title("QuoteCard-活动记录审核拒绝")
    def test_quote_record_reject_r(self, read_token):
        logger.info("开始执行审核QuoteCard活动记录用例...")
        url = con_url + "url/audit"
        global headers
        headers = {'content-type': 'application/json;charset=UTF-8', 'Connection': 'close'}
        global token
        token = read_token
        headers['authorization'] = token
        method = 'POST'
        data = {
                "ids": [quote_id],
                "type": "quote",
                "auditStatus": "reject"
            }

        # 发送请求
        approval_res = RequestTools().send_requests(method=method, url=url, data=data, header=headers)
        logger.info('审核QuoteCard活动记录，请求发送成功！')
        logger.info('审核QuoteCard活动记录响应结果res：{}'.format(approval_res))

        # 调用外部断言函数断言
        try:
            actual_code = approval_res['errorCode']  # 获取响应状态码
            assertRes.assertRes().assert_code(actual_code, "00000")  # 断言状态码，预期状态码"00000"
            assert approval_res['result'] == True
            time.sleep(1)
            # 查询数据库审核状态
            se_res = db.select_data_one('table', 'phone', phone)
            status = se_res['audit_status']
            logger.info(f'查询数据库审核状态为:{status}')
            assert status == 'reject'
            logger.info('审核QuoteCard活动记录-拒绝，断言成功!')
        except Exception as e:
            logger.info(f'审核QuoteCard活动记录-拒绝，断言失败!{e}')
            raise



    # 编辑QuoteCard活动记录
    @pytest.mark.run(order=15)
    @allure.title("编辑QuoteCard活动记录")
    def test_quote_record_edit_r(self, read_token):
        global quote_id
        logger.info("开始执行编辑QuoteCard活动记录用例...")
        url = con_url +'url/'+str(quote_id)
        global headers
        headers = {'content-type': 'application/json;charset=UTF-8', 'Connection': 'close'}
        global token
        token = read_token
        headers['authorization'] = token
        data ={
        "accountNumber": quote_accountNumber,
        "activityId": quote_activityId,
        "ruleId": quote_ruleId,
        "phones": [quote_phone],
        "couponId": quote_couponId,
        "remark": quote_remark
}
        # 发送请求
        edit_res = requests.patch(url=url, json=data, headers=headers)
        edit_res=edit_res.json()
        logger.info('编辑QuoteCard活动记录，请求发送成功！')
        logger.info('编辑QuoteCard活动记录响应结果res：{}'.format(edit_res))
        # logger.info(f'审核QuoteCard活动记录返回id:{id}')
        # 调用外部断言函数断言
        try:
            assert edit_res['errorCode']=='00000'
            time.sleep(1)
            # 查询数据库审核状态
            se_res = db.select_data_one('table', 'phone', quote_phone)
            assert se_res['remark']=='test'
            status = se_res['audit_status']
            logger.info(f'查询数据库审核状态为:{status}')
            assert status == 'notAudit'
            logger.info('编辑QuoteCard活动记录，断言成功!')
        except Exception as e:
            logger.info(f'编辑QuoteCard活动记录，断言失败!{e}')
            raise

    #编辑后审核QuoteCard活动记录-通过
    @pytest.mark.run(order=16)
    @allure.title("QuoteCard-活动记录编辑后审核通过")
    def test_quote_record_edit_approval_r(self, read_token,teardown):
        logger.info("开始执行审核QuoteCard活动记录用例...")
        url = con_url + 'url/audit'
        global headers
        headers = {'content-type': 'application/json;charset=UTF-8', 'Connection': 'close'}
        global token
        token = read_token
        headers['authorization'] = token
        method = 'POST'
        data = {
                'ids': [quote_id],
                'type': 'quote',
                 'auditStatus': 'approval'
                    }

        # 发送请求
        approval_res = RequestTools().send_requests(method=method, url=url, data=data, header=headers)
        logger.info('审核QuoteCard活动记录，请求发送成功！')
        logger.info('审核QuoteCard活动记录响应结果res：{}'.format(approval_res))

        # 调用外部断言函数断言
        try:
            actual_code = approval_res['errorCode']  # 获取响应状态码
            assertRes.assertRes().assert_code(actual_code, "00000")  # 断言状态码，预期状态码"00000"
            assert  approval_res['result']==True
            time.sleep(1)
            #查询数据库审核状态
            se_res = db.select_data_one('table', 'phone', quote_phone)
            status = se_res['audit_status']
            logger.info(f'查询数据库审核状态为:{status}')
            assert status == 'approval'
            logger.info('编辑后审核QuoteCard活动记录-通过，断言成功!')
        except Exception as e:
            logger.info(f'编辑后审核QuoteCard活动记录-通过，断言失败!{e}')
            raise




#############################  免佣卡-审核-兑换申请中-已兑换-已过期###############################

    ## 手机号码添加免佣卡活动记录  OK
    @pytest.mark.run(order=17)
    @allure.title("添加免佣卡-手机号码")
    def test_add_freeCommissionCard_record_phone_p(self, read_token, clear_someone_record):

        global logger, con_url, free_phone, free_accountNumber, free_remark, free_activityId, free_ruleId, free_couponId
        free_phone = '13515000000'  # 手机号码    #审核通过approval
        free_accountNumber = '501092'  # 客户编号
        free_remark = 'test'  # 备注
        free_activityId = 'HD100786'  # 活动ID
        free_ruleId = 'GZ100088'  # 规则ID
        free_couponId = 'KQ100407'  # 卡券ID 港股-PRO210101

        logger.info("开始执行添加免佣卡活动记录用例...")
        url = con_url + "url"
        global headers
        headers = {'content-type': 'application/json;charset=UTF-8', 'Connection': 'close'}
        global token
        token = read_token
        headers['authorization'] = token
        method = 'POST'
        data = {
            "activityId": free_activityId,
            "ruleId": free_ruleId,
            "phones": [free_phone],  # 可添加多个客户编号
            "couponId": free_couponId,
            "remark": free_remark
        }

        ##发送请求
        global  free_id_p
        add_res_free = RequestTools().send_requests(method=method, url=url, data=data, header=headers)
        free_id_p = add_res_free['result']['id']
        logger.info('添加免佣卡请求发送成功！')
        logger.info('添加免佣卡响应结果res：{}'.format(add_res_free))
        logger.info(f'添加免佣卡返回id:{free_id_p}')
        # 调用外部断言函数断言
        try:
            actual_code = add_res_free['errorCode']  # 获取响应状态码
            assertRes.assertRes().assert_code(actual_code, "00000")  # 断言状态码，预期状态码"00000"

            assertRes.assertRes().assert_equal_string(add_res_free['result']['activity_id'],
                                                      free_activityId)  # 断言活动ID
            assertRes.assertRes().assert_equal_string(add_res_free['result']['phone'],
                                                      phone)  # 断言请求响应信息的字符串完全相等
            assertRes.assertRes().assert_equal_string(add_res_free['result']['audit_status'], 'notAudit')  # 待审核
            logger.info('使用手机号码添加免佣卡，断言成功!')
        except Exception as e:
            logger.info(f'使用手机号码添加免佣卡，断言失败!{e}')
            raise


    # 审核免佣卡活动记录-通过   OK
    @pytest.mark.run(order=18)
    @allure.title("免佣卡-活动记录审核通过")
    def test_freeCommissionCard_record_approval_p(self, read_token):
        logger.info("开始执行审核免佣卡活动记录用例...")
        url = con_url + "url/audit"
        global headers
        headers = {'content-type': 'application/json;charset=UTF-8', 'Connection': 'close'}
        global token
        token = read_token
        headers['authorization'] = token
        method = 'POST'

        data = {
            "ids": [free_id_p],
            "type": "freeCommission",
            "auditStatus": "approval"
        }

        ## 发送请求
        free_approval_res = RequestTools().send_requests(method=method, url=url, data=data, header=headers)
        logger.info('审核免佣卡活动记录，请求发送成功！')
        logger.info('审核免佣卡活动记录响应结果res：{}'.format(free_approval_res))
        # logger.info(f'审核免佣卡活动记录返回id:{id}')

        # 调用外部断言函数断言
        try:
            actual_code = free_approval_res['errorCode']  # 获取响应状态码
            assertRes.assertRes().assert_code(actual_code, "00000")  # 断言状态码，预期状态码"00000"
            assert free_approval_res['result'] == True
            time.sleep(1)
            # 查询数据库审核状态
            se_res = db.select_data_one('table', 'phone', free_phone)
            status = se_res['audit_status']
            logger.info(f'查询数据库审核状态为:{status}')
            assert status == 'approval'
            logger.info('审核免佣卡活动记录-通过，断言成功!')

            global _id_free, record_id_free, coupon_id_free, coupon_name_free, coupon_type_free, idp_user_id_free

            _id_free = se_res['_id']
            record_id_free = se_res['record_id']  # 原record_id
            coupon_id_free = se_res['coupon_id']  # 卡券ID
            coupon_name_free = se_res['coupon_name']  # 卡券名称
            coupon_type_free = se_res['coupon_type']  # 卡券类型
            idp_user_id_free = se_res['idp_user_id']  # 对应账户中心eddid_id

            logger.info(f'活动记录_id:{_id_free}')
            logger.info(f'卡券ID:{coupon_id_free}')
            logger.info(f'卡券名称:{coupon_name_free}')
            logger.info(f'卡券类型:{coupon_type_free}')
            logger.info(f'eddid:{idp_user_id_free}')
        except Exception as e:
            logger.info(f'审核免佣卡活动记录-通过，断言失败!{e}')
            raise



    # 调用账户中心接口手动同步免佣卡,修改CRM同步状态OK
    @pytest.mark.run(order=19)
    @allure.title('调用账户中心接口手动同步免佣卡')
    def test_freeCommissionCard_Sync_accountCenter_p(self):
        accountCenter_url = 'url
        global headers
        headers = {'content-type': 'application/json'}
        logger.info("开始发送CRM免佣卡同步请求...")
        data = {
            "list": [
                {
                    'convertDeadline': convertDeadline,  #
                    'convertTime': None,
                    'convertWay': 'MANUAL',  # 兑换方式 ，手动
                    'couponDescription': 'test',
                    'couponId': free_couponId,  #
                    'couponInstruction': 'test',
                    'couponName': '港股-PRO210101',  #
                    "couponType": 'FREE_COMMISSION',  #
                    "deductionCode": None,
                    "discountCode": None,
                    "eddid": idp_user_id_free,
                    "effectStartTime":effectStartTime ,
                    "financingCode": None,
                    "freeCommissionType": 'HK_STOCK',
                    "freeCommissionTypeTime": 30,
                    "freeCommissionTypeTimeUnit": 'DAY',
                    "iconList": [],
                    "orderId": str(record_id_free),  #
                    "quoteComboCode": None,  #
                    "status": "NOTCONVERT",  # 未兑换
                    "welfareCode": None,
                    "welfareCurrency": None,
                    "welfareType": None,
                    "welfareValue": None
                }
            ]
        }

        # 发送请求
        import json
        data = json.dumps(data)
        free_approval_res = requests.post(url=accountCenter_url, data=data, headers=headers)
        free_approval_res = free_approval_res.json()
        logger.info('同步免佣卡活动记录，请求发送成功！')
        logger.info('同步免佣卡活动记录响应结果res：{}'.format(free_approval_res))

        # 断言响应结果
        assert free_approval_res['code'] == 200
        assert free_approval_res['data'] == None
        logger.info('CRM同步卡券至账户中心,断言成功！')
        time.sleep(2)
        # 查询账户中心同步数据
        try:
            # 查询中台数据库断言是否成功同步至账户中心
            sql_query = f"SELECT *From XX  a  where a.xx=\'{record_id_free}\'"
            logger.info(f'拼接sql:{sql_query}')
            om = myl_db.MySQL_select_data_one(sql_query)
            assert om == True
            logger.info('CRM同步免佣卡至账户中心，断言成功！')


            db.update_data_is_synced('table', record_id_free)
            logger.info('成功更新CRM同步状态！')

            time.sleep(2)
        except Exception as  e:
            logger.info(f'CRM同步免佣卡至账户中心，断言失败！')
            raise e

    # APP 申请兑换免佣卡-兑换申请中
    @pytest.mark.run(order=20)
    @allure.title('APP申请兑换免佣卡-兑换申请中')
    def test_app_converting_freeCommissionCard_p(self):
        #APP申请兑换免佣卡
        accountCenter_url = 'url'
        global headers
        headers1 = {'Content-Type': 'application/json',"Accept-Language":"zh-CN"}
        
        headers1['authorization'] = free_token
        logger.info("APP申请兑换免佣卡...")
        data = {
                    "orderId": record_id_free
              }

        # 发送请求
        import json
        data = json.dumps(data)
        free_approval_res = requests.post(url=accountCenter_url, data=data, headers=headers1)
        free_approval_res = free_approval_res.json()
        logger.info('APP申请兑换免佣卡，请求发送成功！')
        logger.info('APP申请兑换免佣卡，响应结果res：{}'.format(free_approval_res))

        # 断言响应结果
        assert free_approval_res['code'] == 200
        assert free_approval_res['data'] == None
        time.sleep(2)
        # 数据库断言
        try:
            # 查询中台数据库
            sql_query = f"SELECT *From XX  a  where a.xx=\'{record_id_free}\'"
            logger.info(f'拼接sql:{sql_query}')
            myl_db.MySQL_select_data_one(sql_query)
            om = myl_db.MySQL_select_data_one(sql_query)
            assert om == True
            logger.info('APP申请兑换免佣卡断言成功，查询中台兑换状态为兑换申请中。')

            # 检查CRM数据库兑换状态是否正确
            f_con_status = db.select_data_one('table', 'record_id', record_id_free)
            assert f_con_status['convert_status'] == 'converting'
            logger.info('APP申请兑换免佣卡断言成功，查询CRM兑换状态为兑换申请中。')
        except Exception as  e:
            logger.info(f'CRM同步卡券至账户中心，断言失败！')
            raise e

    # 批量操作免佣卡--已兑换
    @pytest.mark.run(order=21)
    @allure.title('批量操作免佣卡-已兑换')
    def test_convert_success_freeCommissionCard_p(self,read_token):
        url = con_url +'url'
        global headers
        headers = {'content-type': 'application/json;charset=UTF-8', 'Connection': 'close'}
        global token
        token = read_token
        headers['authorization'] = token
        convert_date = time.strftime('%Y-%m-%d', time.localtime())+"T15:59:58.000Z"
        free_records_res = db.select_data_one('free_commission_records', 'phone',free_phone )
        free_records_id=free_records_res['_id']
        logger.info(f'free_records_id:{free_records_id}')
        data ={
            "convertStatus": "success",
            "convertTime": convert_date,
            "ids": [str(free_records_id)]

        }
        free_convert_res = requests.patch(url=url, json=data, headers=headers)
        free_convert_res = free_convert_res.json()
        logger.info(f'已兑换响应结果:{free_convert_res}')

        #断言
        try:
            actual_code = free_convert_res['errorCode']  # 获取响应状态码
            assertRes.assertRes().assert_code(actual_code, "00000")  # 断言状态码，预期状态码"00000"
            assert free_convert_res['result'] ==True
            time.sleep(1)

            # 查询CRM数据库兑换状态
            se_res = db.select_data_one('table', 'phone', free_phone)
            status = se_res['convert_status']
            logger.info(f'查询CRM数据库兑换状态为:{status}')
            assert status == 'success'
            logger.info('批量操作免佣卡-已兑换-通过，断言成功!')

            #查询中台数据库兑换状态
        except Exception as e:
            logger.info(f'批量操作免佣卡-已兑换，断言失败!{e}')
            raise


    # 批量操作免佣卡--已到期
    @pytest.mark.run(order=22)
    @allure.title('批量操作免佣卡-已到期')
    def test_convert_expired_freeCommissionCard_p(self, read_token,teardown):
        url = con_url + 'url'
        global headers
        headers = {'content-type': 'application/json;charset=UTF-8', 'Connection': 'close'}
        global token
        token = read_token
        headers['authorization'] = token
        global free_records_id

        #查询CRM免佣记录
        free_records_res = db.select_data_one('free_commission_records', 'phone', free_phone)
        free_records_id = free_records_res['_id']  #免佣id
        logger.info(f'free_records_id:{free_records_id}')
        data = {
            "convertStatus": "expired",
            "ids": [str(free_records_id)] #

        }
        free_convert_res = requests.patch(url=url, json=data, headers=headers)
        free_convert_res = free_convert_res.json()
        logger.info(f'已兑换响应结果:{free_convert_res}')

        # 断言
        try:
            actual_code = free_convert_res['errorCode']  # 获取响应状态码
            assertRes.assertRes().assert_code(actual_code, "00000")  # 断言状态码，预期状态码"00000"
            assert free_convert_res['result'] == True
            time.sleep(1)

            # 查询CRM数据库兑换状态
            se_res = db.select_data_one('table', 'phone', free_phone)
            status = se_res['convert_status']
            logger.info(f'查询CRM数据库兑换状态为:{status}')
            assert status == 'expired'
            logger.info('批量操作免佣卡-已到期-通过，断言成功!')

            #查询中台数据库兑换状态
        except Exception as e:
            logger.info(f'批量操作免佣卡-已到期，断言失败!{e}')
            raise

        # 删除账户中心和CRM免佣卡记录
        try:
            sql_delete = f"delete from  XX  where xx=\'{record_id_free}\'"

            logger.info(f'拼接sql:{sql_delete}')
            om = myl_db.MySQL_delete_data_one(sql_delete)
            assert om == True
            logger.info('成功删除账户中心免佣卡记录！')
            try:
                db.delete_data_many('free_commission_records', 'phone', phone)
                logger.info('已成功删除CRM免佣卡记录！')
            except Exception as e:
                logger.info(f'删除CRM免佣卡记录，失败!{e}')
                raise
        except Exception as e:
            logger.info(f'删除账户中心免佣卡记录，失败!{e}')
            raise





    ##################### 免佣卡-兑换失败 OK ############################


    # # 手机号码添加免佣卡活动记录  OK
    @pytest.mark.run(order=23)
    @allure.title("添加免佣卡-手机号码")
    def test_add_freeCommissionCard_record_phone_f(self, read_token, clear_someone_record):

        global logger, con_url, free_phone, free_accountNumber, free_remark, free_activityId, free_ruleId, free_couponId
        free_phone = '13515000000'  # 手机号码    #审核通过approval
        free_accountNumber = '501092'  # 客户编号
        free_remark = 'test'  # 备注
        free_activityId = 'HD100786'  # 活动ID
        free_ruleId = 'GZ100088'  # 规则ID
        free_couponId = 'KQ100407'  # 卡券ID 港股-PRO210101

        logger.info("开始执行添加免佣卡活动记录用例...")
        url = con_url + "url"
        global headers
        headers = {'content-type': 'application/json;charset=UTF-8', 'Connection': 'close'}
        global token
        token = read_token
        headers['authorization'] = token
        method = 'POST'
        data = {
            "activityId": free_activityId,
            "ruleId": free_ruleId,
            "phones": [free_phone],  # 可添加多个客户编号
            "couponId": free_couponId,
            "remark": free_remark
        }
        # 发送请求
        global free_id_f
        add_res = RequestTools().send_requests(method=method, url=url, data=data, header=headers)
        free_id_f = add_res['result']['id']  #活动id
        logger.info('添加免佣卡请求发送成功！')
        logger.info('添加免佣卡响应结果res：{}'.format(add_res))
        logger.info(f'添加免佣卡返回id:{free_id_f}')
        # 调用外部断言函数断言
        try:
            actual_code = add_res['errorCode']  # 获取响应状态码
            assertRes.assertRes().assert_code(actual_code, "00000")  # 断言状态码，预期状态码"00000"

            assertRes.assertRes().assert_equal_string(add_res['result']['activity_id'],
                                                      free_activityId)  # 断言活动ID
            assertRes.assertRes().assert_equal_string(add_res['result']['phone'],
                                                      phone)  # 断言请求响应信息的字符串完全相等
            assertRes.assertRes().assert_equal_string(add_res['result']['audit_status'], 'notAudit')  # 待审核
            logger.info('使用手机号码添加免佣卡，断言成功!')
        except Exception as e:
            logger.info(f'使用手机号码添加免佣卡，断言失败!{e}')
            raise


    # 审核免佣卡活动记录-通过   OK
    @pytest.mark.run(order=24)
    @allure.title("免佣卡-活动记录审核通过")
    def test_freeCommissionCard_record_approval_f(self, read_token):
        logger.info("开始执行审核免佣卡活动记录用例...")
        url = con_url + "url/audit"
        global headers
        headers = {'content-type': 'application/json;charset=UTF-8', 'Connection': 'close'}
        global token
        token = read_token
        headers['authorization'] = token
        method = 'POST'

        data = {
            "ids": [free_id_f],
            "type": "freeCommission",
            "auditStatus": "approval"
        }
        # 发送请求
        free_approval_res = RequestTools().send_requests(method=method, url=url, data=data, header=headers)
        logger.info('审核免佣卡活动记录，请求发送成功！')
        logger.info('审核免佣卡活动记录响应结果res：{}'.format(free_approval_res))
        # logger.info(f'审核免佣卡活动记录返回id:{id}')

        # 调用外部断言函数断言
        try:
            actual_code = free_approval_res['errorCode']  # 获取响应状态码
            assertRes.assertRes().assert_code(actual_code, "00000")  # 断言状态码，预期状态码"00000"
            assert free_approval_res['result'] == True
            time.sleep(1)
            # 查询数据库审核状态
            se_res = db.select_data_one('table', 'phone', free_phone)
            status = se_res['audit_status']
            logger.info(f'查询数据库审核状态为:{status}')
            assert status == 'approval'
            logger.info('审核免佣卡活动记录-通过，断言成功!')

            global _id_free, record_id_free, coupon_id_free, coupon_name_free, coupon_type_free, idp_user_id_free

            _id_free = se_res['_id']
            record_id_free = se_res['record_id']  # 原record_id
            coupon_id_free = se_res['coupon_id']  # 卡券ID
            coupon_name_free = se_res['coupon_name']  # 卡券名称
            coupon_type_free = se_res['coupon_type']  # 卡券类型
            idp_user_id_free = se_res['idp_user_id']  # 对应账户中心eddid_id

            logger.info(f'活动记录_id:{_id_free}')
            logger.info(f'卡券ID:{coupon_id_free}')
            logger.info(f'卡券名称:{coupon_name_free}')
            logger.info(f'卡券类型:{coupon_type_free}')
            logger.info(f'eddid:{idp_user_id_free}')
        except Exception as e:
            logger.info(f'审核免佣卡活动记录-通过，断言失败!{e}')
            raise



       # 调用账户中心接口手动同步免佣卡,修改CRM同步状态OK
    @pytest.mark.run(order=25)
    @allure.title('调用账户中心接口手动同步免佣卡')
    def test_freeCommissionCard_Sync_accountCenter_f(self):
        accountCenter_url = 'url
        global headers
        headers = {'content-type': 'application/json'}
        logger.info("开始发送CRM免佣卡同步请求...")
        data = {
            "list": [
                {
                    'convertDeadline': convertDeadline,  #
                    'convertTime': None,
                    'convertWay': 'MANUAL',  # 兑换方式 ，手动
                    'couponDescription': 'test',
                    'couponId': free_couponId,  #
                    'couponInstruction': 'test',
                    'couponName': '港股-PRO210101',  #
                    "couponType": 'FREE_COMMISSION',  #
                    "deductionCode": None,
                    "discountCode": None,
                    "eddid": idp_user_id_free,
                    "effectStartTime":effectStartTime,
                    "financingCode": None,
                    "freeCommissionType": 'HK_STOCK',
                    "freeCommissionTypeTime": 30,
                    "freeCommissionTypeTimeUnit": 'DAY',
                    "iconList": [],
                    "orderId": str(record_id_free),  #
                    "quoteComboCode": None,  #
                    "status": "NOTCONVERT",  # 未兑换
                    "welfareCode": None,
                    "welfareCurrency": None,
                    "welfareType": None,
                    "welfareValue": None
                }
            ]
        }

    # 发送请求
        import json
        data = json.dumps(data)

        free_approval_res = requests.post(url=accountCenter_url, data=data, headers=headers)
        free_approval_res = free_approval_res.json()
        logger.info('同步免佣卡活动记录，请求发送成功！')
        logger.info('同步免佣卡活动记录响应结果res：{}'.format(free_approval_res))

        # 断言响应结果
        assert free_approval_res['code'] == 200
        assert free_approval_res['data'] == None
        logger.info('CRM同步卡券至账户中心,断言成功！')
        time.sleep(2)
        # 查询账户中心同步数据
        try:
            # 查询中台数据库断言是否成功同步至账户中心
            sql_query = f"SELECT *From XX  a  where a.xx=\'{record_id_free}\'"
            logger.info(f'拼接sql:{sql_query}')
            om = myl_db.MySQL_select_data_one(sql_query)
           # logger.info(f'CRM向账户中心同步卡券结果：{om}')
            assert om == True
            logger.info('CRM同步免佣卡至账户中心，断言成功！')


            db.update_data_is_synced('table', record_id_free)
            logger.info('成功更新CRM同步状态！')

            time.sleep(2)
        except Exception as  e:
            logger.info(f'CRM同步免佣卡至账户中心，断言失败！')
            raise e


    # APP 申请兑换免佣卡-兑换申请中
    @pytest.mark.run(order=26)
    @allure.title('APP申请兑换免佣卡-兑换申请中')
    def test_app_converting_freeCommissionCard_f(self):
        #APP申请兑换免佣卡
        accountCenter_url = 'url'
       # global headers
        headers1 = {'Content-Type': 'application/json',"Accept-Language":"zh-CN"}
        #free_token
        
        headers1['authorization'] = free_token
        logger.info("APP申请兑换免佣卡...")
        data = {
                    "orderId": record_id_free
              }

        # 发送请求
        import json
        data = json.dumps(data)
        free_approval_res = requests.post(url=accountCenter_url, data=data, headers=headers1)
        free_approval_res = free_approval_res.json()
        logger.info('APP申请兑换免佣卡，请求发送成功！')
        logger.info('APP申请兑换免佣卡，响应结果res：{}'.format(free_approval_res))

        # 断言响应结果
        assert free_approval_res['code'] == 200
        assert free_approval_res['data'] == None
        time.sleep(2)
        # 数据库断言
        try:
            # 查询中台数据库
            sql_query = f"SELECT *From XX  a  where a.xx=\'{record_id_free}\'"
            logger.info(f'拼接sql:{sql_query}')
            myl_db.MySQL_select_data_one_new(sql_query)

            om = myl_db.MySQL_select_data_one(sql_query)
            #logger.info(f'APP申请兑换免佣卡，查询中台数据库结果：{om}')
            assert om == True
            logger.info('APP申请兑换免佣卡断言成功，查询中台兑换状态为兑换申请中。')

            # 检查CRM数据库兑换状态是否正确
            f_con_status = db.select_data_one('table', 'record_id', record_id_free)
            assert f_con_status['convert_status'] == 'converting'
            logger.info('APP申请兑换免佣卡断言成功，查询CRM兑换状态为兑换申请中。')
        except Exception as  e:
            logger.info(f'CRM同步卡券至账户中心，断言失败！')
            raise e



    # 批量操作免佣卡--兑换失败
    @pytest.mark.run(order=27)
    @allure.title('批量操作免佣卡-兑换失败')
    def test_convert_failed_freeCommissionCard_f(self,read_token,teardown):

        url = con_url +'url'
        #logger.info(f'免佣卡兑换失败请求url:{url}')
        global headers
        headers = {'content-type': 'application/json;charset=UTF-8', 'Connection': 'close'}
        global token
        token = read_token
        headers['authorization'] = token
        convert_date = time.strftime('%Y-%m-%d', time.localtime())+"T15:59:58.000Z"
        global free_records_id
        #查询数据库免佣记录
        free_records_res = db.select_data_one('free_commission_records', 'phone',free_phone )
        free_records_id=free_records_res['_id']
        logger.info(f'free_records_id:{free_records_id}')
        data ={
            "convertStatus": "failed",
            "convertTime": convert_date,
            "ids": [str(free_records_id)]

        }
        free_convert_res = requests.patch(url=url, json=data, headers=headers)
        free_convert_res = free_convert_res.json()
        logger.info(f'兑换失败响应结果:{free_convert_res}')

        ##断言
        try:
            actual_code = free_convert_res['errorCode']  # 获取响应状态码
            assertRes.assertRes().assert_code(actual_code, "00000")  # 断言状态码，预期状态码"00000"
            assert free_convert_res['result'] ==True
            time.sleep(1)
            # 查询CRM数据库兑换状态
            se_res = db.select_data_one('table', 'phone', free_phone)
            status = se_res['convert_status']
            logger.info(f'查询CRM数据库兑换状态为:{status}')
            assert status == 'failed'
            logger.info('批量操作免佣卡-兑换失败-通过，断言成功!')

            #查询中台数据库兑换状态

        except Exception as e:
            logger.info(f'批量操作免佣卡-兑换失败，断言失败!{e}')
            raise

        #删除账户中心和CRM免佣卡记录
        try:
            sql_delete = f"delete from  XX  where xx=\'{record_id_free}\'"
            logger.info(f'拼接sql:{sql_delete}')
            om = myl_db.MySQL_delete_data_one(sql_delete)
            assert om == True
            logger.info('成功删除账户中心免佣卡记录！')
            try:
                db.delete_data_many('free_commission_records', 'phone', free_phone)
                logger.info('已成功删除CRM免佣卡记录！')
            except Exception as e:
                logger.info(f'删除CRM免佣卡记录，失败!{e}')
                raise
        except Exception as e:
            logger.info(f'删除账户中心免佣卡记录，失败!{e}')
            raise


########  添加免佣卡-审核拒绝-编辑-审核通过 OK ###############
    ##手机号码添加免佣卡活动记录
    @pytest.mark.run(order=28)
    @allure.title("添加免佣卡-手机号码")
    def test_add_freeCommission_record_phone_r(self, read_token, clear_someone_record):

        global logger, con_url, free_phone, free_accountNumber, free_remark, free_activityId, free_ruleId, free_couponId
        free_phone = '13515000000'  # 手机号码    #审核通过approval
        free_accountNumber = '501092'  # 客户编号
        free_remark = 'test'  # 备注
        free_activityId = 'HD100786'  # 活动ID
        free_ruleId = 'GZ100088'  # 规则ID
        free_couponId = 'KQ100407'  # 卡券ID 港股-PRO210101

        logger.info("开始执行添加免佣卡活动记录用例...")
        url = con_url + "url"
        global headers
        headers = {'content-type': 'application/json;charset=UTF-8', 'Connection': 'close'}
        global token
        token = read_token
        headers['authorization'] = token
        method = 'POST'
        data = {
            "activityId": free_activityId,
            "ruleId": free_ruleId,
            "phones": [free_phone],  # 可添加多个客户编号
            "couponId": free_couponId,
            "remark": free_remark
        }
        # 发送请求

        global free_id_r
        add_res = RequestTools().send_requests(method=method, url=url, data=data, header=headers)
        free_id_r = add_res['result']['id']
        logger.info('添加免佣卡请求发送成功！')
        logger.info('添加免佣卡响应结果res：{}'.format(add_res))
        logger.info(f'添加免佣卡返回id:{free_id_r}')
        # 调用外部断言函数断言
        try:
            actual_code = add_res['errorCode']  # 获取响应状态码
            assertRes.assertRes().assert_code(actual_code, "00000")  # 断言状态码，预期状态码"00000"

            assertRes.assertRes().assert_equal_string(add_res['result']['activity_id'],
                                                      free_activityId)  # 断言活动ID
            assertRes.assertRes().assert_equal_string(add_res['result']['phone'],
                                                      phone)  # 断言请求响应信息的字符串完全相等
            assertRes.assertRes().assert_equal_string(add_res['result']['audit_status'], 'notAudit')  # 待审核
            logger.info('使用手机号码添加免佣卡，断言成功!')
        except Exception as e:
            logger.info(f'使用手机号码添加免佣卡，断言失败!{e}')
            raise

        # 审核QuoteCard活动记录-拒绝

    @pytest.mark.run(order=29)
    @allure.title("免佣卡-活动记录审核拒绝")
    def test_freeCommission_record_reject_r(self, read_token):
        logger.info("开始执行审核免佣卡活动记录用例...")
        url = con_url + "url/audit"
        global headers
        headers = {'content-type': 'application/json;charset=UTF-8', 'Connection': 'close'}
        global token
        token = read_token
        headers['authorization'] = token
        method = 'POST'
        global free_id_r
        data = {
            "ids": [free_id_r],
            "type": "freeCommission",
            "auditStatus": "reject"
        }
        # 发送请求
        approval_res = RequestTools().send_requests(method=method, url=url, data=data, header=headers)
        logger.info('审核免佣卡活动记录，请求发送成功！')
        logger.info('审核免佣卡活动记录响应结果res：{}'.format(approval_res))
        # logger.info(f'审核免佣卡活动记录返回id:{id}')
        # 调用外部断言函数断言
        try:
            actual_code = approval_res['errorCode']  # 获取响应状态码
            assertRes.assertRes().assert_code(actual_code, "00000")  # 断言状态码，预期状态码"00000"
            assert approval_res['result'] == True
            time.sleep(1)
            # 查询数据库审核状态
            se_res = db.select_data_one('table', 'phone', free_phone)
            status = se_res['audit_status']
            logger.info(f'查询数据库审核状态为:{status}')
            assert status == 'reject'
            logger.info('审核免佣卡活动记录-拒绝，断言成功!')
        except Exception as e:
            logger.info(f'审核免佣卡活动记录-拒绝，断言失败!{e}')
            raise

    # 编辑免佣卡活动记录
    @pytest.mark.run(order=30)
    @allure.title("编辑免佣卡活动记录")
    def test_freeCommission_record_edit_r(self, read_token):
        global free_id_r
        logger.info("开始执行编辑免佣卡活动记录用例...")
        url = con_url + 'url/' + free_id_r
        global headers
        headers = {'content-type': 'application/json;charset=UTF-8', 'Connection': 'close'}
        global token
        token = read_token
        headers['authorization'] = token

        data = {
            "activityId": "HD100786",
            "ruleId": "GZ100088",
            "accountNumber": "501092",
            "couponId": "KQ100405",  # 修改卡券ID  美股US4PRO1
            "remark": "test-freeCommission"  # 修改备注
        }
        # 发送请求

        global edit_res
        edit_res = requests.patch(url=url, json=data, headers=headers)
        edit_res = edit_res.json()
        logger.info('编辑免佣卡活动记录，请求发送成功！')
        logger.info('编辑免佣卡活动记录响应结果res：{}'.format(edit_res))
        # logger.info(f'审核免佣卡活动记录返回id:{id}')
        # 调用外部断言函数断言
        try:
            assert edit_res['errorCode'] == '00000'
            time.sleep(1)
            # 查询数据库审核状态
            se_res = db.select_data_one('table', 'phone', free_phone)
            assert se_res['remark'] == 'test-freeCommission'
            status = se_res['audit_status']
            logger.info(f'查询数据库审核状态为:{status}')
            assert status == 'notAudit'
            logger.info('编辑免佣卡活动记录，断言成功!')
        except Exception as e:
            logger.info(f'编辑免佣卡活动记录，断言失败!{e}')
            raise

    ##编辑后审核免佣卡活动记录-通过
    @pytest.mark.run(order=31)
    @allure.title("免佣卡-活动记录编辑后审核通过")
    def test_freeCommission_record_edit_approval_r(self, read_token,teardown):
        logger.info("开始执行审核免佣卡活动记录用例...")
        url = con_url + 'url/audit'
        global headers
        headers = {'content-type': 'application/json;charset=UTF-8', 'Connection': 'close'}
        global token
        token = read_token
        headers['authorization'] = token
        method = 'POST'
        global free_id_r
        data = {
            'ids': [free_id_r],
            'type': 'freeCommission',
            'auditStatus': 'approval'
        }
        # 发送请求
        approval_res = RequestTools().send_requests(method=method, url=url, data=data, header=headers)
        logger.info('审核免佣卡活动记录，请求发送成功！')
        logger.info('审核免佣卡活动记录响应结果res：{}'.format(approval_res))

        # 调用外部断言函数断言
        try:
            actual_code = approval_res['errorCode']  # 获取响应状态码
            assertRes.assertRes().assert_code(actual_code, "00000")  # 断言状态码，预期状态码"00000"
            assert approval_res['result'] == True
            time.sleep(1)
            # 查询数据库审核状态
            se_res = db.select_data_one('table', 'phone', free_phone)
            status = se_res['audit_status']
            logger.info(f'查询数据库审核状态为:{status}')
            assert status == 'approval'
            logger.info('编辑后审核免佣卡活动记录-通过，断言成功!')
        except Exception as e:
            logger.info(f'编辑后审核免佣卡活动记录-通过，断言失败!{e}')
            raise



##############################  JDCard-新增-审核通过  ###############################

    # 手机号码添加JDCard活动记录  OK
    @pytest.mark.run(order=32)
    @allure.title("添加JDCard-手机号码")
    def test_add_JDCard_record_phone_p(self, read_token, clear_someone_record):
        global logger, con_url, JD_phone_p, JD_accountNumber_p, JD_remark_p, JD_activityId_p, JD_ruleId_p, JD_couponId_p
        JD_phone_p = '13515000000'  # 手机号码    #审核通过approval
        JD_accountNumber_p = '501092'  # 客户编号
        JD_remark_p = 'test'  # 备注
        JD_activityId_p = 'HD100786'  # 活动ID
        JD_ruleId_p = 'GZ100088'  # 规则ID
        JD_couponId_p = 'KQ100414'  # 卡券ID 港股-PRO210101
        logger.info("开始执行添加JDCard活动记录用例...")
        url = con_url + "url"
        global headers
        headers = {'content-type': 'application/json;charset=UTF-8', 'Connection': 'close'}
        global token
        token = read_token
        headers['authorization'] = token
        method = 'POST'
        data = {
            "activityId": JD_activityId_p,
            "ruleId": JD_ruleId_p,
            "phones": [JD_phone_p],  # 可添加多个客户编号
            "couponId": JD_couponId_p,
            "remark": JD_remark_p
        }
        # 发送请求
        global add_res_JD_p, JD_id_p
        add_res_JD_p = RequestTools().send_requests(method=method, url=url, data=data, header=headers)
        JD_id_p = add_res_JD_p['result']['id']
        logger.info('添加JDCard请求发送成功！')
        logger.info('添加JDCard响应结果res：{}'.format(add_res_JD_p))
        logger.info(f'添加JDCard返回id:{JD_id_p}')
        # 调用外部断言函数断言
        try:
            actual_code = add_res_JD_p['errorCode']  # 获取响应状态码
            assertRes.assertRes().assert_code(actual_code, "00000")  # 断言状态码，预期状态码"00000"

            assertRes.assertRes().assert_equal_string(add_res_JD_p['result']['activity_id'],
                                                      JD_activityId_p)  # 断言活动ID
            assertRes.assertRes().assert_equal_string(add_res_JD_p['result']['phone'],
                                                      phone)  # 断言请求响应信息的字符串完全相等
            assertRes.assertRes().assert_equal_string(add_res_JD_p['result']['audit_status'], 'notAudit')  # 待审核
            logger.info('使用手机号码添加JDCard，断言成功!')
        except Exception as e:
            logger.info(f'使用手机号码添加JDCard，断言失败!{e}')
            raise

    # 审核JDCard活动记录-通过   OK
    @pytest.mark.run(order=33)
    @allure.title("JDCard-活动记录审核通过")
    def test_JDCard_record_approval_p(self, read_token):
        logger.info("开始执行审核JDCard活动记录用例...")
        url = con_url + "url/audit"
        global headers
        headers = {'content-type': 'application/json;charset=UTF-8', 'Connection': 'close'}
        global token
        token = read_token
        headers['authorization'] = token
        method = 'POST'
        data = {
            "ids": [JD_id_p],
            "type": "welfare",
            "auditStatus": "approval"
        }

        ##发送请求
        global JD_approval_res_p
        JD_approval_res_p = RequestTools().send_requests(method=method, url=url, data=data, header=headers)
        logger.info('审核JDCard活动记录，请求发送成功！')
        logger.info('审核JDCard活动记录响应结果res：{}'.format(JD_approval_res_p))

        # 调用外部断言函数断言
        try:
            actual_code = JD_approval_res_p['errorCode']  # 获取响应状态码
            assertRes.assertRes().assert_code(actual_code, "00000")  # 断言状态码，预期状态码"00000"
            assert JD_approval_res_p['result'] == True
            time.sleep(1)
            # 查询数据库审核状态
            se_res = db.select_data_one('table', 'phone', JD_phone_p)
            status = se_res['audit_status']
            logger.info(f'查询数据库审核状态为:{status}')
            assert status == 'approval'
            logger.info('审核JDCard活动记录-通过，断言成功!')

            global _id_JD_p, record_id_JD_p, coupon_id_JD_p, coupon_name_JD_p, coupon_type_JD_p, idp_user_id_JD_p

            _id_JD_p = se_res['_id']
            record_id_JD_p = se_res['record_id']  # 原record_id
            coupon_id_JD_p = se_res['coupon_id']  # 卡券ID
            coupon_name_JD_p = se_res['coupon_name']  # 卡券名称
            coupon_type_JD_p = se_res['coupon_type']  # 卡券类型
            idp_user_id_JD_p = se_res['idp_user_id']  # 对应账户中心eddid_id

            logger.info(f'活动记录_id:{_id_JD_p}')
            logger.info(f'卡券ID:{coupon_id_JD_p}')
            logger.info(f'卡券名称:{coupon_name_JD_p}')
            logger.info(f'卡券类型:{coupon_type_JD_p}')
            logger.info(f'eddid:{idp_user_id_JD_p}')
        except Exception as e:
            logger.info(f'审核JDCard活动记录-通过，断言失败!{e}')
            raise


############################### JDCard 拒绝  编辑  通过########################-------
    # 手机号码添加JDCard活动记录
    @pytest.mark.run(order=34)
    @allure.title("添加JDCard-手机号码")
    def test_add_JD_record_phone_f(self, read_token, clear_someone_record):

        global jd_phone_f, jd_accountNumber_f, jd_remark_f, jd_activityId_f, jd_ruleId_f, jd_couponId_f
        jd_phone_f = '13515000000'  # 手机号码    #审核通过approval
        jd_accountNumber_f = '501092'  # 客户编号
        jd_remark_f = 'test'  # 备注
        jd_activityId_f = 'HD100786'  # 活动ID
        jd_ruleId_f = 'GZ100088'  # 规则ID
        jd_couponId_f = 'KQ100414'  # 卡券ID JDCard200-即时

        logger.info("开始执行添加JDCard活动记录用例...")
        url = con_url + "url"
        global headers
        headers = {'content-type': 'application/json;charset=UTF-8', 'Connection': 'close'}
        global token
        token = read_token
        headers['authorization'] = token
        method = 'POST'
        data = {
            "activityId": jd_activityId_f,
            "ruleId": jd_ruleId_f,
            "phones": [jd_phone_f],  # 可添加多个客户编号
            "couponId": jd_couponId_f,
            "remark": jd_remark_f
        }

        ## 发送请求
        global jd_id_f,add_res_JD_f
        add_res_JD_f = RequestTools().send_requests(method=method, url=url, data=data, header=headers)
        logger.info('添加JDCard响应结果res：{}'.format(add_res_JD_f))
        jd_id_f = add_res_JD_f['result']['id']
        logger.info('添加JDCard请求发送成功！')
        logger.info('添加JDCard响应结果res：{}'.format(add_res_JD_f))
        logger.info(f'添加JDCard返回id:{jd_id_f}')
        # 调用外部断言函数断言
        try:
            actual_code = add_res_f['errorCode']  # 获取响应状态码
            assertRes.assertRes().assert_code(actual_code, "00000")  # 断言状态码，预期状态码"00000"

            assertRes.assertRes().assert_equal_string(add_res_JD_f['result']['activity_id'],
                                                      jd_activityId_f)  # 断言活动ID
            assertRes.assertRes().assert_equal_string(add_res_JD_f['result']['phone'],
                                                      phone)  # 断言请求响应信息的字符串完全相等
            assertRes.assertRes().assert_equal_string(add_res_JD_f['result']['audit_status'], 'notAudit')  # 待审核
            logger.info('使用手机号码添加JDCard，断言成功!')
        except Exception as e:
            logger.info(f'使用手机号码添加JDCard，断言失败!{e}')
            raise

    # 审核JDCard活动记录-拒绝
    @pytest.mark.run(order=35)
    @allure.title("JDCard-活动记录审核拒绝")
    def test_JD_record_reject_f(self, read_token):
        logger.info("开始执行审核JDCard活动记录用例...")
        url = con_url + "url/audit"
        global headers
        headers = {'content-type': 'application/json;charset=UTF-8', 'Connection': 'close'}
        global token
        token = read_token
        headers['authorization'] = token
        method = 'POST'
        global jd_id_f
        data = {
            "ids": [jd_id_f],
            "type": "welfare",
            "auditStatus": "reject"
        }
        # 发送请求
        approval_res_f = RequestTools().send_requests(method=method, url=url, data=data, header=headers)
        logger.info('审核JDCard活动记录，请求发送成功！')
        logger.info('审核JDCard活动记录响应结果res：{}'.format(approval_res_f))
        # logger.info(f'审核JDCard活动记录返回id:{id}')
        # 调用外部断言函数断言
        try:
            actual_code = approval_res_f['errorCode']  # 获取响应状态码
            assertRes.assertRes().assert_code(actual_code, "00000")  # 断言状态码，预期状态码"00000"
            assert approval_res_f['result'] == True
            time.sleep(1)
            # 查询数据库审核状态
            se_res = db.select_data_one('table', 'phone', jd_phone_f)
            status = se_res['audit_status']
            logger.info(f'查询数据库审核状态为:{status}')
            assert status == 'reject'
            logger.info('审核JDCard活动记录-拒绝，断言成功!')
        except Exception as e:
            logger.info(f'审核JDCard活动记录-拒绝，断言失败!{e}')
            raise

    # # 编辑JDCard活动记录
    # @pytest.mark.run(order=36)
    # @allure.title("编辑JDCard活动记录")
    # def test_JD_record_edit_f(self, read_token):
    #     global jd_id_f
    #     logger.info("开始执行编辑JDCard活动记录用例...")
    #     url = con_url +'url/'+jd_id_f
    #     global headers
    #     headers = {'content-type': 'application/json;charset=UTF-8', 'Connection': 'close'}
    #     global token
    #     token = read_token
    #     headers['authorization'] = token
    #
    #     data = {
    #         "activityId": jd_activityId_f,
    #         "ruleId":  jd_ruleId_f,
    #         "accountNumber": "501092",
    #         "couponId": "KQ100277",  # 修改卡券ID 200元JDCard
    #         "remark": "test-JD"  # 修改备注
    #     }
    #     # 发送请求
    #     edit_res_f = requests.patch(url=url, json=data, headers=headers)
    #     edit_res_f = edit_res_f.json()
    #     logger.info('编辑JDCard活动记录，请求发送成功！')
    #     logger.info('编辑JDCard活动记录响应结果res：{}'.format(edit_res_f))
    #     # logger.info(f'审核JDCard活动记录返回id:{id}')
    #     # 调用外部断言函数断言
    #     try:
    #         assert edit_res_f['errorCode'] == '00000'
    #         time.sleep(1)
    #         # 查询数据库审核状态
    #         se_res = db.select_data_one('table', 'phone', jd_phone_f)
    #         assert se_res['remark'] == 'test-JD'
    #         status = se_res['audit_status']
    #         logger.info(f'查询数据库审核状态为:{status}')
    #         assert status == 'notAudit'
    #         logger.info('编辑JDCard活动记录，断言成功!')
    #     except Exception as e:
    #         logger.info(f'编辑JDCard活动记录，断言失败!{e}')
    #         raise
    #
    # # 编辑后审核JDCard活动记录-通过
    # @pytest.mark.run(order=37)
    # @allure.title("JDCard-活动记录编辑后审核通过")
    # def test_JD_record_edit_approval_f(self, read_token,teardown):
    #     logger.info("开始执行审核JDCard活动记录用例...")
    #     url = con_url +'url/audit'
    #     global headers
    #     headers = {'content-type': 'application/json;charset=UTF-8', 'Connection': 'close'}
    #     global token
    #     token = read_token
    #     headers['authorization'] = token
    #     method = 'POST'
    #     global jd_id_f
    #     data = {
    #         'ids': [jd_id_f],
    #         'type': 'welfare',
    #         'auditStatus': 'approval'
    #     }
    #     # 发送请求
    #     approval_res_f = RequestTools().send_requests(method=method, url=url, data=data, header=headers)
    #     logger.info('审核JDCard活动记录，请求发送成功！')
    #     logger.info('审核JDCard活动记录响应结果res：{}'.format(approval_res_f))
    #
    #     # 调用外部断言函数断言
    #     try:
    #         actual_code = approval_res_f['errorCode']  # 获取响应状态码
    #         assertRes.assertRes().assert_code(actual_code, "00000")  # 断言状态码，预期状态码"00000"
    #         assert approval_res_f['result'] == True
    #         time.sleep(1)
    #         # 查询数据库审核状态
    #         se_res = db.select_data_one('table', 'phone', jd_phone_f)
    #         status = se_res['audit_status']
    #         logger.info(f'查询数据库审核状态为:{status}')
    #         assert status == 'approval'
    #         logger.info('编辑后审核JDCard活动记录-通过，断言成功!')
    #     except Exception as e:
    #         logger.info(f'编辑后审核JDCard活动记录-通过，断言失败!{e}')
    #         raise


############################ StockCard-审核通过 ######################################

    # 手机号码添加StockCard活动记录
    @pytest.mark.run(order=38)
    @allure.title("添加StockCard-手机号码")
    def test_add_stock_record_phone_p(self, read_token, clear_someone_record):
        global  stock_phone_p, stock_accountNumber_p, stock_remark_p, stock_activityId_p, stock_ruleId_p, stock_couponId_p
        stock_phone_p = '13515000000'  # 手机号码    #审核通过approval
        stock_accountNumber_p = '501092'  # 客户编号
        stock_remark_p = 'test'  # 备注
        stock_activityId_p = 'HD100786'  # 活动ID
        stock_ruleId_p = 'GZ100088'  # 规则ID
        stock_couponId_p = 'KQ100233'  # 卡券ID StockCardall

        logger.info("开始执行添加StockCard活动记录用例...")
        url = con_url + "url"
        global headers
        headers = {'content-type': 'application/json;charset=UTF-8', 'Connection': 'close'}
        global token
        token = read_token
        headers['authorization'] = token
        method = 'POST'
        data = {
            "activityId": stock_activityId_p,
            "ruleId": stock_ruleId_p,
            "phones": [stock_phone_p],  # 可添加多个客户编号
            "couponId": stock_couponId_p,
            "remark": stock_remark_p
        }
        # 发送请求

        global add_res_p, stock_id_p
        add_res_p = RequestTools().send_requests(method=method, url=url, data=data, header=headers)
        stock_id_p = add_res_p['result']['id']
        logger.info('添加StockCard请求发送成功！')
        logger.info('添加StockCard响应结果res：{}'.format(add_res_p))
        logger.info(f'添加StockCard返回id:{stock_id_p}')
        # 调用外部断言函数断言
        try:
            actual_code = add_res_p['errorCode']  # 获取响应状态码
            assertRes.assertRes().assert_code(actual_code, "00000")  # 断言状态码，预期状态码"00000"

            assertRes.assertRes().assert_equal_string(add_res_p['result']['activity_id'],
                                                      stock_activityId_p)  # 断言活动ID
            assertRes.assertRes().assert_equal_string(add_res_p['result']['phone'],
                                                      phone)  # 断言请求响应信息的字符串完全相等
            assertRes.assertRes().assert_equal_string(add_res_p['result']['audit_status'], 'notAudit')  # 待审核
            logger.info('使用手机号码添加StockCard，断言成功!')
        except Exception as e:
            logger.info(f'使用手机号码添加StockCard，断言失败!{e}')
            raise

    # 审核StockCard活动记录-通过
    @pytest.mark.run(order=39)
    @allure.title("StockCard-活动记录审核通过")
    def test_stock_record_approval(self, read_token,teardown):
        logger.info("开始执行审核StockCard活动记录用例...")
        url = con_url + "url/audit"
        global headers
        headers = {'content-type': 'application/json;charset=UTF-8', 'Connection': 'close'}
        global token
        token = read_token
        headers['authorization'] = token
        method = 'POST'
        global stock_id_p
        data = {
            "ids": [stock_id_p],
            "type": "welfare",
            "auditStatus": "approval"
        }

        # 发送请求
        global approval_res_p
        approval_res_p = RequestTools().send_requests(method=method, url=url, data=data, header=headers)
        logger.info('审核StockCard活动记录，请求发送成功！')
        logger.info('审核StockCard活动记录响应结果res：{}'.format(approval_res_p))

        # 调用外部断言函数断言
        try:
            actual_code = approval_res_p['errorCode']  # 获取响应状态码
            assertRes.assertRes().assert_code(actual_code, "00000")  # 断言状态码，预期状态码"00000"
            assert approval_res_p['result'] == True
            global stock_phone_p
            time.sleep(1)
            # 查询数据库审核状态
            se_res = db.select_data_one('table', 'phone', stock_phone_p)
            status = se_res['audit_status']
            logger.info(f'查询数据库审核状态为:{status}')
            assert status == 'approval'
            logger.info('审核StockCard活动记录-通过，断言成功!')
        except Exception as e:
            logger.info(f'审核StockCard活动记录-通过，断言失败!{e}')
            raise

    ##############StockCard-拒绝-编辑-审核通过#####################
    @pytest.mark.run(order=40)
    @allure.title("添加StockCard-手机号码")
    def test_add_stock_record_phone_f(self, read_token, clear_someone_record):

        global stock_phone_f, stock_accountNumber_f, stock_remark_f, stock_activityId_f, stock_ruleId_f, stock_couponId_f
        stock_phone_f = '13515000000'  # 手机号码    #审核通过approval
        stock_accountNumber_f = '501092'  # 客户编号
        stock_remark_f = 'test'  # 备注
        stock_activityId_f = 'HD100786'  # 活动ID
        stock_ruleId_f = 'GZ100088'  # 规则ID
        stock_couponId_f = 'KQ100414'  # 卡券ID StockCard200-即时

        logger.info("开始执行添加StockCard活动记录用例...")
        url = con_url + "url"
        global headers
        headers = {'content-type': 'application/json;charset=UTF-8', 'Connection': 'close'}
        global token
        token = read_token
        headers['authorization'] = token
        method = 'POST'
        data = {
            "activityId": stock_activityId_f,
            "ruleId": stock_ruleId_f,
            "phones": [stock_phone_f],  # 可添加多个客户编号
            "couponId": stock_couponId_f,
            "remark": stock_remark_f
        }

        # 发送请求
        global add_res_f, stock_id_f
        add_res_f = RequestTools().send_requests(method=method, url=url, data=data, header=headers)
        stock_id_f = add_res_f['result']['id']
        logger.info('添加StockCard请求发送成功！')
        logger.info('添加StockCard响应结果res：{}'.format(add_res_f))
        logger.info(f'添加StockCard返回id:{stock_id_f}')
        # 调用外部断言函数断言
        try:
            actual_code = add_res_f['errorCode']  # 获取响应状态码
            assertRes.assertRes().assert_code(actual_code, "00000")  # 断言状态码，预期状态码"00000"

            assertRes.assertRes().assert_equal_string(add_res_f['result']['activity_id'],
                                                      stock_activityId_f)  # 断言活动ID
            assertRes.assertRes().assert_equal_string(add_res_f['result']['phone'],
                                                      phone)  # 断言请求响应信息的字符串完全相等
            assertRes.assertRes().assert_equal_string(add_res_f['result']['audit_status'], 'notAudit')  # 待审核
            logger.info('使用手机号码添加StockCard，断言成功!')
        except Exception as e:
            logger.info(f'使用手机号码添加StockCard，断言失败!{e}')
            raise

    # 审核StockCard活动记录-拒绝
    @pytest.mark.run(order=41)
    @allure.title("StockCard-活动记录审核拒绝")
    def test_stock_record_reject_f(self, read_token):
        logger.info("开始执行审核StockCard活动记录用例...")
        url = con_url + "url/audit"
        global headers
        headers = {'content-type': 'application/json;charset=UTF-8', 'Connection': 'close'}
        global token
        token = read_token
        headers['authorization'] = token
        method = 'POST'
        global stock_id_f
        data = {
            "ids": [stock_id_f],
            "type": "welfare",
            "auditStatus": "reject"
        }
        # 发送请求

        global approval_res_f
        approval_res_f = RequestTools().send_requests(method=method, url=url, data=data, header=headers)
        logger.info('审核StockCard活动记录，请求发送成功！')
        logger.info('审核StockCard活动记录响应结果res：{}'.format(approval_res_f))
        # 调用外部断言函数断言
        try:
            actual_code = approval_res_f['errorCode']  # 获取响应状态码
            assertRes.assertRes().assert_code(actual_code, "00000")  # 断言状态码，预期状态码"00000"
            assert approval_res_f['result'] == True
            global stock_phone_f
            time.sleep(1)
            # 查询数据库审核状态
            se_res = db.select_data_one('table', 'phone', stock_phone_f)
            status = se_res['audit_status']
            logger.info(f'查询数据库审核状态为:{status}')
            assert status == 'reject'
            logger.info('审核StockCard活动记录-拒绝，断言成功!')
        except Exception as e:
            logger.info(f'审核StockCard活动记录-拒绝，断言失败!{e}')
            raise

    # 编辑StockCard活动记录
    @pytest.mark.run(order=42)
    @allure.title("编辑StockCard活动记录")
    def test_stock_record_edit_f(self, read_token):
        global stock_id_f
        logger.info("开始执行编辑StockCard活动记录用例...")
        url = con_url + 'url/' + stock_id_f
        global headers
        headers = {'content-type': 'application/json;charset=UTF-8', 'Connection': 'close'}
        global token
        token = read_token
        headers['authorization'] = token

        data = {
            "activityId": "HD100786",
            "ruleId": "GZ100088",
            "accountNumber": "501092",
            "couponId": "KQ100397",  # 修改卡券ID 2股福特汽车StockCard
            "remark": "test-stock"  # 修改备注
        }

        # 发送请求
        edit_res_f = requests.patch(url=url, json=data, headers=headers)
        edit_res_f = edit_res_f.json()
        logger.info('编辑StockCard活动记录，请求发送成功！')
        logger.info('编辑StockCard活动记录响应结果res：{}'.format(edit_res_f))
        # logger.info(f'审核StockCard活动记录返回id:{id}')
        # 调用外部断言函数断言
        try:
            assert edit_res_f['errorCode'] == '00000'
            global stock_phone
            time.sleep(1)
            # 查询数据库审核状态
            se_res = db.select_data_one('table', 'phone', stock_phone_f)
            assert se_res['remark'] == 'test-stock'
            status = se_res['audit_status']
            logger.info(f'查询数据库审核状态为:{status}')
            assert status == 'notAudit'
            logger.info('编辑StockCard活动记录，断言成功!')
        except Exception as e:
            logger.info(f'编辑StockCard活动记录，断言失败!{e}')
            raise

    # 编辑后审核StockCard活动记录-通过
    @pytest.mark.run(order=43)
    @allure.title("StockCard-活动记录编辑后审核通过")
    def test_stock_record_edit_approval_f(self, read_token,teardown):
        logger.info("开始执行审核StockCard活动记录用例...")
        url = con_url + 'url/audit'
        global headers
        headers = {'content-type': 'application/json;charset=UTF-8', 'Connection': 'close'}
        global token
        token = read_token
        headers['authorization'] = token
        method = 'POST'
        global stock_id_f
        data = {
            'ids': [stock_id_f],
            'type': 'welfare',
            'auditStatus': 'approval'
        }

        # 发送请求
        approval_res_f = RequestTools().send_requests(method=method, url=url, data=data, header=headers)
        logger.info('审核StockCard活动记录，请求发送成功！')
        logger.info('审核StockCard活动记录响应结果res：{}'.format(approval_res_f))

        # 调用外部断言函数断言
        try:
            actual_code = approval_res_f['errorCode']  # 获取响应状态码
            assertRes.assertRes().assert_code(actual_code, "00000")  # 断言状态码，预期状态码"00000"
            assert approval_res_f['result'] == True
            global stock_phone_f
            time.sleep(1)
            # 查询数据库审核状态
            se_res = db.select_data_one('table', 'phone', stock_phone_f)
            status = se_res['audit_status']
            logger.info(f'查询数据库审核状态为:{status}')
            assert status == 'approval'
            logger.info('编辑后审核StockCard活动记录-通过，断言成功!')
        except Exception as e:
            logger.info(f'编辑后审核StockCard活动记录-通过，断言失败!{e}')
            raise




######################################## DeductionCard-审核通过 ######################################

 # 手机号码添加DeductionCard活动记录
    @pytest.mark.run(order=44)
    @allure.title("添加DeductionCard-手机号码")
    def test_add_deduction_record_phone_p(self, read_token, clear_someone_record):
        global  deduction_phone_p, deduction_accountNumber_p, deduction_remark_p, deduction_activityId_p, deduction_ruleId_p, deduction_couponId_p
        deduction_phone_p = '13515000000'  # 手机号码    #审核通过approval
        deduction_accountNumber_p = '501092'  # 客户编号
        deduction_remark_p = 'test'  # 备注
        deduction_activityId_p = 'HD100786'  # 活动ID
        deduction_ruleId_p = 'GZ100088'  # 规则ID
        deduction_couponId_p = 'KQ100367'  # 卡券ID 1085手续费券-1
        logger.info("开始执行添加DeductionCard活动记录用例...")
        url = con_url + "url"
        global headers
        headers = {'content-type': 'application/json;charset=UTF-8', 'Connection': 'close'}
        global token
        token = read_token
        headers['authorization'] = token
        method = 'POST'
        data = {
            "activityId": deduction_activityId_p,
            "ruleId": deduction_ruleId_p,
            "phones": [deduction_phone_p],  # 可添加多个客户编号
            "couponId": deduction_couponId_p,
            "remark": deduction_remark_p
        }

        # 发送请求
        global  deduction_id_p
        add_res_p = RequestTools().send_requests(method=method, url=url, data=data, header=headers)
        deduction_id_p = add_res_p['result']['id']
        logger.info('添加DeductionCard请求发送成功！')
        logger.info('添加DeductionCard响应结果res：{}'.format(add_res_p))
        logger.info(f'添加DeductionCard返回id:{deduction_id_p}')
        # 调用外部断言函数断言
        try:
            actual_code = add_res_p['errorCode']  # 获取响应状态码
            assertRes.assertRes().assert_code(actual_code, "00000")  # 断言状态码，预期状态码"00000"

            assertRes.assertRes().assert_equal_string(add_res_p['result']['activity_id'],
                                                      deduction_activityId_p)  # 断言活动ID
            assertRes.assertRes().assert_equal_string(add_res_p['result']['phone'],
                                                      phone)  # 断言请求响应信息的字符串完全相等
            assertRes.assertRes().assert_equal_string(add_res_p['result']['audit_status'], 'notAudit')  # 待审核
            logger.info('使用手机号码添加DeductionCard，断言成功!')
        except Exception as e:
            logger.info(f'使用手机号码添加DeductionCard，断言失败!{e}')
            raise

    # 审核DeductionCard活动记录-通过
    @pytest.mark.run(order=45)
    @allure.title("DeductionCard-活动记录审核通过")
    def test_deduction_record_approval_p(self, read_token,teardown):
        logger.info("开始执行审核DeductionCard活动记录用例...")
        url = con_url + "url/audit"
        global headers
        headers = {'content-type': 'application/json;charset=UTF-8', 'Connection': 'close'}
        global token
        token = read_token
        headers['authorization'] = token
        method = 'POST'
        global deduction_id_p
        data = {
            "ids": [deduction_id_p],
            "type": "deduction",
            "auditStatus": "approval"
        }

        # 发送请求
        approval_res_p = RequestTools().send_requests(method=method, url=url, data=data, header=headers)
        logger.info('审核DeductionCard活动记录，请求发送成功！')
        logger.info('审核DeductionCard活动记录响应结果res：{}'.format(approval_res_p))

        # 调用外部断言函数断言
        try:
            actual_code = approval_res_p['errorCode']  # 获取响应状态码
            assertRes.assertRes().assert_code(actual_code, "00000")  # 断言状态码，预期状态码"00000"
            assert approval_res_p['result'] == True
            global deduction_phone_p
            time.sleep(1)
            # 查询数据库审核状态
            se_res = db.select_data_one('table', 'phone', deduction_phone_p)
            status = se_res['audit_status']
            logger.info(f'查询数据库审核状态为:{status}')
            assert status == 'approval'
            logger.info('审核DeductionCard活动记录-通过，断言成功!')
        except Exception as e:
            logger.info(f'审核DeductionCard活动记录-通过，断言失败!{e}')
            raise


###############################DeductionCard-拒绝-编辑-通过####################
    # 手机号码添加DeductionCard活动记录
    @pytest.mark.run(order=46)
    @allure.title("添加DeductionCard-手机号码")
    def test_add_deduction_record_phone_f(self, read_token, clear_someone_record):

        global deduction_phone_f, deduction_accountNumber_f, deduction_remark_f, deduction_activityId_f, deduction_ruleId_f, deduction_couponId_f
        deduction_phone_f = '13515000000'  # 手机号码    #审核通过approval
        deduction_accountNumber_f = '501092'  # 客户编号
        deduction_remark_f = 'test'  # 备注
        deduction_activityId_f = 'HD100786'  # 活动ID
        deduction_ruleId_f = 'GZ100088'  # 规则ID
        deduction_couponId_f = 'KQ100367'  # 卡券ID 1085手续费券-1

        logger.info("开始执行添加DeductionCard活动记录用例...")
        url = con_url + "url"
        global headers
        headers = {'content-type': 'application/json;charset=UTF-8', 'Connection': 'close'}
        global token
        token = read_token
        headers['authorization'] = token
        method = 'POST'
        data = {
            "activityId": deduction_activityId_f,
            "ruleId": deduction_ruleId_f,
            "phones": [deduction_phone_f],  # 可添加多个客户编号
            "couponId": deduction_couponId_f,
            "remark": deduction_remark_f
        }
        # 发送请求
        global add_res_f, deduction_id_f
        add_res_f = RequestTools().send_requests(method=method, url=url, data=data, header=headers)
        deduction_id_f = add_res_f['result']['id']
        logger.info('添加DeductionCard请求发送成功！')
        logger.info('添加DeductionCard响应结果res：{}'.format(add_res_f))
        logger.info(f'添加DeductionCard返回id:{deduction_id_f}')
        # 调用外部断言函数断言
        try:
            actual_code = add_res_f['errorCode']  # 获取响应状态码
            assertRes.assertRes().assert_code(actual_code, "00000")  # 断言状态码，预期状态码"00000"

            assertRes.assertRes().assert_equal_string(add_res_f['result']['activity_id'],
                                                      deduction_activityId_f)  # 断言活动ID
            assertRes.assertRes().assert_equal_string(add_res_f['result']['phone'],
                                                      phone)  # 断言请求响应信息的字符串完全相等
            assertRes.assertRes().assert_equal_string(add_res_f['result']['audit_status'], 'notAudit')  # 待审核
            logger.info('使用手机号码添加DeductionCard，断言成功!')
        except Exception as e:
            logger.info(f'使用手机号码添加DeductionCard，断言失败!{e}')
            raise

    # 审核DeductionCard活动记录-拒绝
    @pytest.mark.run(order=47)
    @allure.title("DeductionCard-活动记录审核拒绝")
    def test_deduction_record_reject_f(self, read_token):
        logger.info("开始执行审核DeductionCard活动记录用例...")
        url = con_url + "url/audit"
        global headers
        headers = {'content-type': 'application/json;charset=UTF-8', 'Connection': 'close'}
        global token
        token = read_token
        headers['authorization'] = token
        method = 'POST'
        global deduction_id_f
        data = {
            "ids": [deduction_id_f],
            "type": "deduction",
            "auditStatus": "reject"
        }
        # 发送请求
        global approval_res_f
        approval_res_f = RequestTools().send_requests(method=method, url=url, data=data, header=headers)
        logger.info('审核DeductionCard活动记录，请求发送成功！')
        logger.info('审核DeductionCard活动记录响应结果res：{}'.format(approval_res_f))
        # 调用外部断言函数断言
        try:
            actual_code = approval_res_f['errorCode']  # 获取响应状态码
            assertRes.assertRes().assert_code(actual_code, "00000")  # 断言状态码，预期状态码"00000"
            assert approval_res_f['result'] == True
            global deduction_phone_f
            time.sleep(1)
            # 查询数据库审核状态
            se_res = db.select_data_one('table', 'phone', deduction_phone_f)
            status = se_res['audit_status']
            logger.info(f'查询数据库审核状态为:{status}')
            assert status == 'reject'
            logger.info('审核DeductionCard活动记录-拒绝，断言成功!')
        except Exception as e:
            logger.info(f'审核DeductionCard活动记录-拒绝，断言失败!{e}')
            raise

    # 编辑DeductionCard活动记录
    @pytest.mark.run(order=48)
    @allure.title("编辑DeductionCard活动记录")
    def test_deduction_record_edit_f(self, read_token):
        global deduction_id_f
        logger.info("开始执行编辑DeductionCard活动记录用例...")
        url = con_url + 'url/' + deduction_id_f
        global headers
        headers = {'content-type': 'application/json;charset=UTF-8', 'Connection': 'close'}
        global token
        token = read_token
        headers['authorization'] = token

        data = {
            "activityId": "HD100786",
            "ruleId": "GZ100088",
            "accountNumber": "501092",
            "couponId": "KQ100385",  # 修改卡券ID 30DeductionCard排序4天
            "remark": "test-deduction"  # 修改备注
        }
        # 发送请求
        edit_res_f = requests.patch(url=url, json=data, headers=headers)
        edit_res_f = edit_res_f.json()
        logger.info('编辑DeductionCard活动记录，请求发送成功！')
        logger.info('编辑DeductionCard活动记录响应结果res：{}'.format(edit_res_f))
        # logger.info(f'审核DeductionCard活动记录返回id:{id}')
        # 调用外部断言函数断言
        try:
            assert edit_res_f['errorCode'] == '00000'
            global deduction_phone_f
            time.sleep(1)
            # 查询数据库审核状态
            se_res = db.select_data_one('table', 'phone', deduction_phone_f)
            assert se_res['remark'] == 'test-deduction'
            status = se_res['audit_status']
            logger.info(f'查询数据库审核状态为:{status}')
            assert status == 'notAudit'
            logger.info('编辑DeductionCard活动记录，断言成功!')
        except Exception as e:
            logger.info(f'编辑DeductionCard活动记录，断言失败!{e}')
            raise

    # 编辑后审核DeductionCard活动记录-通过
    @pytest.mark.run(order=49)
    @allure.title("DeductionCard-活动记录编辑后审核通过")
    def test_deduction_record_edit_approval(self, read_token,teardown):
        logger.info("开始执行审核DeductionCard活动记录用例...")
        url = con_url + 'url/audit'
        global headers
        headers = {'content-type': 'application/json;charset=UTF-8', 'Connection': 'close'}
        global token
        token = read_token
        headers['authorization'] = token
        method = 'POST'
        global deduction_id_f
        data = {
            'ids': [deduction_id_f],
            'type': 'deduction',
            'auditStatus': 'approval'
        }
        # 发送请求
        global approval_res_f
        approval_res_f = RequestTools().send_requests(method=method, url=url, data=data, header=headers)
        logger.info('审核DeductionCard活动记录，请求发送成功！')
        logger.info('审核DeductionCard活动记录响应结果res：{}'.format(approval_res_f))

        # 调用外部断言函数断言
        try:
            actual_code = approval_res_f['errorCode']  # 获取响应状态码
            assertRes.assertRes().assert_code(actual_code, "00000")  # 断言状态码，预期状态码"00000"
            assert approval_res_f['result'] == True
            global deduction_phone_f
            time.sleep(1)
            # 查询数据库审核状态
            se_res = db.select_data_one('table', 'phone', deduction_phone_f)
            status = se_res['audit_status']
            logger.info(f'查询数据库审核状态为:{status}')
            assert status == 'approval'
            logger.info('编辑后审核DeductionCard活动记录-通过，断言成功!')
        except Exception as e:
            logger.info(f'编辑后审核DeductionCard活动记录-通过，断言失败!{e}')
            raise


############################################## DiscountCard-审核通过 ############################################
# 手机号码添加DiscountCard活动记录
    @pytest.mark.run(order=50)
    @allure.title("添加DiscountCard-手机号码")
    def test_add_discount_record_phone_p(self, read_token, clear_someone_record):
        global  discount_phone_p, discount_accountNumber_p, discount_remark_p, discount_activityId_p, discount_ruleId_p, discount_couponId_p
        discount_phone_p = '13515000000'  # 手机号码    #审核通过approval
        discount_accountNumber_p = '501092'  # 客户编号
        discount_remark_p = 'test'  # 备注
        discount_activityId_p = 'HD100786'  # 活动ID
        discount_ruleId_p = 'GZ100088'  # 规则ID
        discount_couponId_p = 'KQ100377'  # 卡券ID 1093利息券-1

        logger.info("开始执行添加DiscountCard活动记录用例...")
        url = con_url + "url"
        global headers
        headers = {'content-type': 'application/json;charset=UTF-8', 'Connection': 'close'}
        global token
        token = read_token
        headers['authorization'] = token
        method = 'POST'
        data = {
            "activityId": discount_activityId_p,
            "ruleId": discount_ruleId_p,
            "phones": [discount_phone_p],  # 可添加多个客户编号
            "couponId": discount_couponId_p,
            "remark": discount_remark_p
        }
        # 发送请求
        global add_res_p, discount_id_p
        add_res_p = RequestTools().send_requests(method=method, url=url, data=data, header=headers)
        discount_id_p = add_res_p['result']['id']
        logger.info('添加DiscountCard请求发送成功！')
        logger.info('添加DiscountCard响应结果res：{}'.format(add_res_p))
        logger.info(f'添加DiscountCard返回id:{discount_id_p}')
        # 调用外部断言函数断言
        try:
            actual_code = add_res_p['errorCode']  # 获取响应状态码
            assertRes.assertRes().assert_code(actual_code, "00000")  # 断言状态码，预期状态码"00000"

            assertRes.assertRes().assert_equal_string(add_res_p['result']['activity_id'],
                                                      discount_activityId_p)  # 断言活动ID
            assertRes.assertRes().assert_equal_string(add_res_p['result']['phone'],
                                                      phone)  # 断言请求响应信息的字符串完全相等
            assertRes.assertRes().assert_equal_string(add_res_p['result']['audit_status'], 'notAudit')  # 待审核
            logger.info('使用手机号码添加DiscountCard，断言成功!')
        except Exception as e:
            logger.info(f'使用手机号码添加DiscountCard，断言失败!{e}')
            raise

    # 审核DiscountCard活动记录-通过
    @pytest.mark.run(order=51)
    @allure.title("DiscountCard-活动记录审核通过")
    def test_discount_record_approval_p(self, read_token,teardown):
        logger.info("开始执行审核DiscountCard活动记录用例...")
        url = con_url + "url/audit"
        global headers
        headers = {'content-type': 'application/json;charset=UTF-8', 'Connection': 'close'}
        global token
        token = read_token
        headers['authorization'] = token
        method = 'POST'
        global discount_id_p
        data = {
            "ids": [discount_id_p],
            "type": "discount",
            "auditStatus": "approval"
        }
        # 发送请求
        global approval_res_p
        approval_res_p = RequestTools().send_requests(method=method, url=url, data=data, header=headers)
        logger.info('审核DiscountCard活动记录，请求发送成功！')
        logger.info('审核DiscountCard活动记录响应结果res：{}'.format(approval_res_p))
        # 调用外部断言函数断言
        try:
            actual_code = approval_res_p['errorCode']  # 获取响应状态码
            assertRes.assertRes().assert_code(actual_code, "00000")  # 断言状态码，预期状态码"00000"
            assert approval_res_p['result'] == True
            global discount_phone_p
            time.sleep(1)
            # 查询数据库审核状态
            se_res = db.select_data_one('table', 'phone', discount_phone_p)
            status = se_res['audit_status']
            logger.info(f'查询数据库审核状态为:{status}')
            assert status == 'approval'
            logger.info('审核DiscountCard活动记录-通过，断言成功!')
        except Exception as e:
            logger.info(f'审核DiscountCard活动记录-通过，断言失败!{e}')
            raise



########################################### DiscountCard-拒绝-编辑-通过##########################
    # 手机号码添加DiscountCard活动记录
    @pytest.mark.run(order=52)
    @allure.title("添加DiscountCard-手机号码")
    def test_add_discount_record_phone_r(self, read_token, clear_someone_record):

        global discount_phone_r, discount_accountNumber_r, discount_remark_r, discount_activityId_r, discount_ruleId_r, discount_couponId_r
        discount_phone_r = '13515000000'  # 手机号码    #审核通过approval
        discount_accountNumber_r = '501092'  # 客户编号
        discount_remark_r = 'test'  # 备注
        discount_activityId_r = 'HD100786'  # 活动ID
        discount_ruleId_r = 'GZ100088'  # 规则ID
        discount_couponId_r = 'KQ100377'  # 卡券ID 1093利息券-1

        logger.info("开始执行添加DiscountCard活动记录用例...")
        url = con_url + "url"
        global headers
        headers = {'content-type': 'application/json;charset=UTF-8', 'Connection': 'close'}
        global token
        token = read_token
        headers['authorization'] = token
        method = 'POST'
        data = {
            "activityId": discount_activityId_r,
            "ruleId": discount_ruleId_r,
            "phones": [discount_phone_r],  # 可添加多个客户编号
            "couponId": discount_couponId_r,
            "remark": discount_remark_r
        }
        # 发送请求
        global  discount_id_r
        add_res_r = RequestTools().send_requests(method=method, url=url, data=data, header=headers)
        discount_id_r = add_res_r['result']['id']
        logger.info('添加DiscountCard请求发送成功！')
        logger.info('添加DiscountCard响应结果res：{}'.format(add_res_r))
        logger.info(f'添加DiscountCard返回id:{discount_id_r}')
        # 调用外部断言函数断言
        try:
            actual_code = add_res_r['errorCode']  # 获取响应状态码
            assertRes.assertRes().assert_code(actual_code, "00000")  # 断言状态码，预期状态码"00000"

            assertRes.assertRes().assert_equal_string(add_res_r['result']['activity_id'],
                                                      discount_activityId_r)  # 断言活动ID
            assertRes.assertRes().assert_equal_string(add_res_r['result']['phone'],
                                                      phone)  # 断言请求响应信息的字符串完全相等
            assertRes.assertRes().assert_equal_string(add_res_r['result']['audit_status'], 'notAudit')  # 待审核
            logger.info('使用手机号码添加DiscountCard，断言成功!')
        except Exception as e:
            logger.info(f'使用手机号码添加DiscountCard，断言失败!{e}')
            raise

    # 审核DiscountCard活动记录-拒绝
    @pytest.mark.run(order=53)
    @allure.title("DiscountCard-活动记录审核拒绝")
    def test_discount_record_reject_r(self, read_token):
        logger.info("开始执行审核DiscountCard活动记录用例...")
        url = con_url + "url/audit"
        global headers
        headers = {'content-type': 'application/json;charset=UTF-8', 'Connection': 'close'}
        global token
        token = read_token
        headers['authorization'] = token
        method = 'POST'
        global discount_id_r
        data = {
            "ids": [discount_id_r],
            "type": "discount",
            "auditStatus": "reject"
        }
        # 发送请求
        approval_res_r = RequestTools().send_requests(method=method, url=url, data=data, header=headers)
        logger.info('审核DiscountCard活动记录，请求发送成功！')
        logger.info('审核DiscountCard活动记录响应结果res：{}'.format(approval_res_r))

        # 调用外部断言函数断言
        try:
            actual_code = approval_res_r['errorCode']  # 获取响应状态码
            assertRes.assertRes().assert_code(actual_code, "00000")  # 断言状态码，预期状态码"00000"
            assert approval_res_r['result'] == True
            global discount_phone_r
            time.sleep(1)
            # 查询数据库审核状态
            se_res = db.select_data_one('table', 'phone', discount_phone_r)
            status = se_res['audit_status']
            logger.info(f'查询数据库审核状态为:{status}')
            assert status == 'reject'
            logger.info('审核DiscountCard活动记录-拒绝，断言成功!')
        except Exception as e:
            logger.info(f'审核DiscountCard活动记录-拒绝，断言失败!{e}')
            raise

    # 编辑DiscountCard活动记录
    @pytest.mark.run(order=54)
    @allure.title("编辑DiscountCard活动记录")
    def test_discount_record_edit_r(self, read_token):
        global discount_id_r
        logger.info("开始执行编辑DiscountCard活动记录用例...")
        url = con_url + 'url/' + discount_id_r
        global headers
        headers = {'content-type': 'application/json;charset=UTF-8', 'Connection': 'close'}
        global token
        token = read_token
        headers['authorization'] = token

        data = {
            "activityId": "HD100786",
            "ruleId": "GZ100088",
            "accountNumber": "501092",
            "couponId": "KQ100393",  # 修改卡券ID 1107利息券
            "remark": "test-discount"  # 修改备注
        }
        # 发送请求
        edit_res_r = requests.patch(url=url, json=data, headers=headers)
        edit_res_r = edit_res_r.json()
        logger.info('编辑DiscountCard活动记录，请求发送成功！')
        logger.info('编辑DiscountCard活动记录响应结果res：{}'.format(edit_res_r))
        # 调用外部断言函数断言
        try:
            assert edit_res_r['errorCode'] == '00000'
            global discount_phone_r
            time.sleep(1)
            # 查询数据库审核状态
            se_res = db.select_data_one('table', 'phone', discount_phone_r)
            assert se_res['remark'] == 'test-discount'
            status = se_res['audit_status']
            logger.info(f'查询数据库审核状态为:{status}')
            assert status == 'notAudit'
            logger.info('编辑DiscountCard活动记录，断言成功!')
        except Exception as e:
            logger.info(f'编辑DiscountCard活动记录，断言失败!{e}')
            raise

    # 编辑后审核DiscountCard活动记录-通过
    @pytest.mark.run(order=55)
    @allure.title("DiscountCard-活动记录编辑后审核通过")
    def test_discount_record_edit_approval_r(self, read_token,teardown):
        logger.info("开始执行审核DiscountCard活动记录用例...")
        url = con_url + 'url/audit'
        global headers
        headers = {'content-type': 'application/json;charset=UTF-8', 'Connection': 'close'}
        global token
        token = read_token
        headers['authorization'] = token
        method = 'POST'
        global discount_id_r
        data = {
            'ids': [discount_id_r],
            'type': 'discount',
            'auditStatus': 'approval'
        }
        # 发送请求
        approval_res_r = RequestTools().send_requests(method=method, url=url, data=data, header=headers)
        logger.info('审核DiscountCard活动记录，请求发送成功！')
        logger.info('审核DiscountCard活动记录响应结果res：{}'.format(approval_res_r))

        # 调用外部断言函数断言
        try:
            actual_code = approval_res_r['errorCode']  # 获取响应状态码
            assertRes.assertRes().assert_code(actual_code, "00000")  # 断言状态码，预期状态码"00000"
            assert approval_res_r['result'] == True
            global discount_phone_r
            time.sleep(1)
            # 查询数据库审核状态
            se_res = db.select_data_one('table', 'phone', discount_phone_r)
            status = se_res['audit_status']
            logger.info(f'查询数据库审核状态为:{status}')
            assert status == 'approval'
            logger.info('编辑后审核DiscountCard活动记录-通过，断言成功!')
        except Exception as e:
            logger.info(f'编辑后审核DiscountCard活动记录-通过，断言失败!{e}')
            raise

############################### FinancingCard-审核通过#####################################

    # 手机号码添加FinancingCard活动记录
    @pytest.mark.run(order=56)
    @allure.title("添加FinancingCard-手机号码")
    def test_add_financing_record_phone_p(self, read_token, clear_someone_record):
        global  financing_phone_p, financing_accountNumber_p, financing_remark_p, financing_activityId_p, financing_ruleId_p, financing_couponId_p
        financing_phone_p = '13515000000'  # 手机号码    #审核通过approval
        financing_accountNumber_p = '501092'  # 客户编号
        financing_remark_p = 'test'  # 备注
        financing_activityId_p = 'HD100786'  # 活动ID
        financing_ruleId_p = 'GZ100088'  # 规则ID
        financing_couponId_p = 'KQ100379'  # 卡券ID 1095杠杆券-1

        logger.info("开始执行添加FinancingCard活动记录用例...")
        url = con_url + "url"
        global headers
        headers = {'content-type': 'application/json;charset=UTF-8', 'Connection': 'close'}
        global token
        token = read_token
        headers['authorization'] = token
        method = 'POST'
        data = {
            "activityId": financing_activityId_p,
            "ruleId": financing_ruleId_p,
            "phones": [financing_phone_p],  # 可添加多个客户编号
            "couponId": financing_couponId_p,
            "remark": financing_remark_p
        }
        # 发送请求

        global financing_id_p
        add_res_p = RequestTools().send_requests(method=method, url=url, data=data, header=headers)
        financing_id_p = add_res_p['result']['id']
        logger.info('添加FinancingCard请求发送成功！')
        logger.info('添加FinancingCard响应结果res：{}'.format(add_res_p))
        logger.info(f'添加FinancingCard返回id:{financing_id_p}')
        # 调用外部断言函数断言
        try:
            actual_code = add_res_p['errorCode']  # 获取响应状态码
            assertRes.assertRes().assert_code(actual_code, "00000")  # 断言状态码，预期状态码"00000"
            assertRes.assertRes().assert_equal_string(add_res_p['result']['activity_id'],
                                                      financing_activityId_p)  # 断言活动ID
            assertRes.assertRes().assert_equal_string(add_res_p['result']['phone'],
                                                      phone)  # 断言请求响应信息的字符串完全相等
            assertRes.assertRes().assert_equal_string(add_res_p['result']['audit_status'], 'notAudit')  # 待审核
            logger.info('使用手机号码添加FinancingCard，断言成功!')
        except Exception as e:
            logger.info(f'使用手机号码添加FinancingCard，断言失败!{e}')
            raise

    # 审核FinancingCard活动记录-通过
    @pytest.mark.run(order=57)
    @allure.title("FinancingCard-活动记录审核通过")
    def test_financing_record_approval_p(self, read_token,teardown):
        logger.info("开始执行审核FinancingCard活动记录用例...")
        url = con_url + "url/audit"
        global headers
        headers = {'content-type': 'application/json;charset=UTF-8', 'Connection': 'close'}
        global token
        token = read_token
        headers['authorization'] = token
        method = 'POST'
        global financing_id_p
        data = {
            "ids": [financing_id_p],
            "type": "financing",
            "auditStatus": "approval"
        }
        # 发送请求
        approval_res_p = RequestTools().send_requests(method=method, url=url, data=data, header=headers)
        logger.info('审核FinancingCard活动记录，请求发送成功！')
        logger.info('审核FinancingCard活动记录响应结果res：{}'.format(approval_res_p))
        # 调用外部断言函数断言
        try:
            actual_code = approval_res_p['errorCode']  # 获取响应状态码
            assertRes.assertRes().assert_code(actual_code, "00000")  # 断言状态码，预期状态码"00000"
            assert approval_res_p['result'] == True
            global financing_phone_p
            time.sleep(1)
            # 查询数据库审核状态
            se_res = db.select_data_one('table', 'phone', financing_phone_p)
            status = se_res['audit_status']
            logger.info(f'查询数据库审核状态为:{status}')
            assert status == 'approval'
            logger.info('审核FinancingCard活动记录-通过，断言成功!')
        except Exception as e:
            logger.info(f'审核FinancingCard活动记录-通过，断言失败!{e}')
            raise

    #################################### FinancingCard-拒绝-编辑-通过##############################
    # 手机号码添加FinancingCard活动记录
    @pytest.mark.run(order=58)
    @allure.title("添加FinancingCard-手机号码")
    def test_add_financing_record_phone_r(self, read_token, clear_someone_record):
        global financing_phone_r, financing_accountNumber_r, financing_remark_r, financing_activityId_r, financing_ruleId_r, financing_couponId_r
        financing_phone_r = '13515000000'  # 手机号码    #审核通过approval
        financing_accountNumber_r = '501092'  # 客户编号
        financing_remark_r = 'test'  # 备注
        financing_activityId_r = 'HD100786'  # 活动ID
        financing_ruleId_r = 'GZ100088'  # 规则ID
        financing_couponId_r = 'KQ100379'  # 卡券ID 1095杠杆券-1
        logger.info("开始执行添加FinancingCard活动记录用例...")
        url = con_url + "url"
        global headers
        headers = {'content-type': 'application/json;charset=UTF-8', 'Connection': 'close'}
        global token
        token = read_token
        headers['authorization'] = token
        method = 'POST'
        data = {
            "activityId": financing_activityId_r,
            "ruleId": financing_ruleId_r,
            "phones": [financing_phone_r],  # 可添加多个客户编号
            "couponId": financing_couponId_r,
            "remark": financing_remark_r
        }
        # 发送请求
        global financing_id_r
        add_res_r = RequestTools().send_requests(method=method, url=url, data=data, header=headers)
        financing_id_r = add_res_r['result']['id']
        logger.info('添加FinancingCard请求发送成功！')
        logger.info('添加FinancingCard响应结果res：{}'.format(add_res_r))
        logger.info(f'添加FinancingCard返回id:{financing_id_r}')
        # 调用外部断言函数断言
        try:
            actual_code = add_res_r['errorCode']  # 获取响应状态码
            assertRes.assertRes().assert_code(actual_code, "00000")  # 断言状态码，预期状态码"00000"

            assertRes.assertRes().assert_equal_string(add_res_r['result']['activity_id'],
                                                      financing_activityId_r)  # 断言活动ID
            assertRes.assertRes().assert_equal_string(add_res_r['result']['phone'],
                                                      phone)  # 断言请求响应信息的字符串完全相等
            assertRes.assertRes().assert_equal_string(add_res_r['result']['audit_status'], 'notAudit')  # 待审核
            logger.info('使用手机号码添加FinancingCard，断言成功!')
        except Exception as e:
            logger.info(f'使用手机号码添加FinancingCard，断言失败!{e}')
            raise

    # 审核FinancingCard活动记录-拒绝
    @pytest.mark.run(order=59)
    @allure.title("FinancingCard-活动记录审核拒绝")
    def test_financing_record_reject_r(self, read_token):
        logger.info("开始执行审核FinancingCard活动记录用例...")
        url = con_url + "url/audit"
        global headers
        headers = {'content-type': 'application/json;charset=UTF-8', 'Connection': 'close'}
        global token
        token = read_token
        headers['authorization'] = token
        method = 'POST'
        global financing_id_r
        data = {
            "ids": [financing_id_r],
            "type": "financing",
            "auditStatus": "reject"
        }
        # 发送请求
        approval_res_r = RequestTools().send_requests(method=method, url=url, data=data, header=headers)
        logger.info('审核FinancingCard活动记录，请求发送成功！')
        logger.info('审核FinancingCard活动记录响应结果res：{}'.format(approval_res_r))
        # 调用外部断言函数断言
        try:
            actual_code = approval_res_r['errorCode']  # 获取响应状态码
            assertRes.assertRes().assert_code(actual_code, "00000")  # 断言状态码，预期状态码"00000"
            assert approval_res_r['result'] == True
            global financing_phone_r
            time.sleep(1)
            # 查询数据库审核状态
            se_res = db.select_data_one('table', 'phone', financing_phone_r)
            status = se_res['audit_status']
            logger.info(f'查询数据库审核状态为:{status}')
            assert status == 'reject'
            logger.info('审核FinancingCard活动记录-拒绝，断言成功!')
        except Exception as e:
            logger.info(f'审核FinancingCard活动记录-拒绝，断言失败!{e}')
            raise

    # 编辑FinancingCard活动记录
    @pytest.mark.run(order=60)
    @allure.title("编辑FinancingCard活动记录")
    def test_financing_record_edit_r(self, read_token):
        global financing_id_r
        logger.info("开始执行编辑FinancingCard活动记录用例...")
        url = con_url + 'url/' + financing_id_r
        global headers
        headers = {'content-type': 'application/json;charset=UTF-8', 'Connection': 'close'}
        global token
        token = read_token
        headers['authorization'] = token

        data = {
            "activityId": "HD100786",
            "ruleId": "GZ100088",
            "accountNumber": "501092",
            "couponId": "KQ100387",  # 修改卡券ID 30FinancingCard排序7天
            "remark": "test-financing"  # 修改备注
        }

        # 发送请求
        edit_res_r = requests.patch(url=url, json=data, headers=headers)
        edit_res_r = edit_res_r.json()
        logger.info('编辑FinancingCard活动记录，请求发送成功！')
        logger.info('编辑FinancingCard活动记录响应结果res：{}'.format(edit_res_r))
        # logger.info(f'审核FinancingCard活动记录返回id:{id}')
        # 调用外部断言函数断言
        try:
            assert edit_res_r['errorCode'] == '00000'
            global financing_phone_r
            time.sleep(1)
            # 查询数据库审核状态
            se_res = db.select_data_one('table', 'phone', financing_phone_r)
            assert se_res['remark'] == 'test-financing'
            status = se_res['audit_status']
            logger.info(f'查询数据库审核状态为:{status}')
            assert status == 'notAudit'
            logger.info('编辑FinancingCard活动记录，断言成功!')
        except Exception as e:
            logger.info(f'编辑FinancingCard活动记录，断言失败!{e}')
            raise

    # 编辑后审核FinancingCard活动记录-通过
    @pytest.mark.run(order=61)
    @allure.title("FinancingCard-活动记录编辑后审核通过")
    def test_financing_record_edit_approval_r(self, read_token,teardown):
        logger.info("开始执行审核FinancingCard活动记录用例...")
        url = con_url + 'url/audit'
        global headers
        headers = {'content-type': 'application/json;charset=UTF-8', 'Connection': 'close'}
        global token
        token = read_token
        headers['authorization'] = token
        method = 'POST'
        global financing_id_r
        data = {
            'ids': [financing_id_r],
            'type': 'financing',
            'auditStatus': 'approval'
        }
        # 发送请求
        approval_res_r = RequestTools().send_requests(method=method, url=url, data=data, header=headers)
        logger.info('审核FinancingCard活动记录，请求发送成功！')
        logger.info('审核FinancingCard活动记录响应结果res：{}'.format(approval_res_r))
        # 调用外部断言函数断言
        try:
            actual_code = approval_res_r['errorCode']  # 获取响应状态码
            assertRes.assertRes().assert_code(actual_code, "00000")  # 断言状态码，预期状态码"00000"
            assert approval_res_r['result'] == True
            global financing_phone_r
            time.sleep(1)
            # 查询数据库审核状态
            se_res = db.select_data_one('table', 'phone', financing_phone_r)
            status = se_res['audit_status']
            logger.info(f'查询数据库审核状态为:{status}')
            assert status == 'approval'
            logger.info('编辑后审核FinancingCard活动记录-通过，断言成功!')
        except Exception as e:
            logger.info(f'编辑后审核FinancingCard活动记录-通过，断言失败!{e}')
            raise

