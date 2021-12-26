#coding=utf-8
# Author: XHS
# Date  : 2021/6/9 13:42
# File  : conftest.py
from common.yamlTools import YamlTools
import pytest
import yagmail
from common.logger import Logger
from  common.methodTools import RequestTools
import time
global logger
logger = Logger()

#清除Token
@pytest.fixture(scope="session",autouse=True)
def clear_yaml():
    YamlTools().clear_yaml()


#登录并写入Token
@pytest.fixture(scope="session",autouse=True)
def login_write_token():
    url="https://"
    header={'content-type': "application/json;charset=UTF-8"}
    method='post'
    data={'account':"XXX",
          'password':"YYY"

          }

    result = RequestTools().send_requests(method=method, url=url, data=data, header=header)
    # errorCode等于00000，说明请求成功，存在accesstoken
    if (result['errorCode']) == '00000':
        LastToken = "Bearer " + str(result['result']['accesstoken'])
        YamlTools().write_yaml(data={'access_token': LastToken})
        logger.info("Token保存成功!")
    else:
        logger.info("Token保存失败!")


#读取Token
@pytest.fixture(scope="session",autouse=True)

def read_token():
    global token
    token=YamlTools().read_yaml("token.yml")['access_token']
    logger.info("成功读取Token:{}".format(token))
    return token





#统计测试结果及发送邮件
def pytest_terminal_summary(terminalreporter):
    # print(terminalreporter.stats)
    total = terminalreporter._numcollected
    passed= len([i for i in terminalreporter.stats.get('passed', []) if i.when != 'teardown'])
    failed=len([i for i in terminalreporter.stats.get('failed', []) if i.when != 'teardown'])
    error=len([i for i in terminalreporter.stats.get('error', []) if i.when != 'teardown'])
    skipped=len([i for i in terminalreporter.stats.get('skipped', []) if i.when != 'teardown'])
    #执行通过率
    passing_rate=('%.2f%%' % ((len(terminalreporter.stats.get('passed', [])) / terminalreporter._numcollected * 100) ))
    duration = time.time() - terminalreporter._sessionstarttime #从会话开始计算时间
    spend_time= ('%.2f' %( duration)) #执行用例花费时间

    logger.info(f"用例总数: {terminalreporter._numcollected}")
    logger.info(f"通过用例: {passed}")
    logger.info(f"失败用例: {failed}")
    logger.info(f"错误用例: {error}")
    logger.info(f'执行通过率: {passing_rate}')
    logger.info(f'执行花费时间: {spend_time}')


#
#
#
#     with open("result.txt", "w") as fp:
#         fp.write("####CRM接口用例执行结果###"+"\n")
#         fp.write("用例总数: %s" % total+"\n")
#         fp.write("通过用例: %s" % passed+"\n")
#         fp.write("失败用例: %s" % failed+"\n")
#         fp.write("错误用例: %s" % error+"\n")
#         fp.write("跳过用例: %s" % skipped+"\n")
#         fp.write("执行通过率:%s" %passing_rate + "\n")
#         fp.write("执行花费时间:%.2fs" % duration)
#
    try:

        yag = yagmail.SMTP(user="XXX@163.com", password="XXX", host='smtp.163.com')
        subject='CRM接口测试报告'
        # 邮箱正文
        contents = ['Hi,All', f'<h4>EDCRM接口测试用例执行结果:</h4>  <ul><li>用例总数:{total}个</li> <li>通过用例:{passed}个</li> <li>失败用例:{failed}个</li>'
                         f'<li>跳过用例:{skipped}个</li>'
                          f'<li>执行通过率:{passing_rate}</li> <li>执行花费时间:{spend_time}秒</li>'
                         f'<li>详细报告请查阅: ''<a href="xxx">xxx</a></li></ul>']
        yag.send('XXX@.com', subject, contents)
        yag.close()
        logger.info('邮件发送成功!')
    except Exception as  e:
        logger.info(f'邮件发送失败,异常信息:{e}')


