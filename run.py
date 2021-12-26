#coding=utf-8
#Author: XHS
# Date  : 2021/6/9 13:47
# File  : run.py
import os
import pytest
import time
if __name__=="__main__":
    #通过pytest.ini ，将命令写在addopts=-vs
    #pytest.main()
    #pytest.main(['-vs','-n=auto']) #分布式测试  ，根据cpu个数 OK
    #pytest.main(['-vs','-n=2']) #多进程 2个进程   OK
    pytest.main(['--alluredir=./report', '--clean-alluredir'])

    #生成Allure报告
    #os.system('allure generate ./report --clean') #OK
    # #os.system('allure generate ./report ')
   # os.system('allure serve ./report/')  #OK
    #


#
# ''' pytest.main() #验证通过
#     pytest.main(['--alluredir=./report', '--clean-alluredir'])
#    # os.system('allure generate ./report --clean') #OK
#     os.system('allure generate ./report ') #OK
#     os.system('allure serve ./report/')
# '''
#

