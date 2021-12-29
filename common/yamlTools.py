# coding=utf-8
# Date  :  2021/6/7 22:30
# Author: XHS
# File  : yamlTools.py

'''
功能：1.读取YAML文件内容
     2.写入YAML文件内容
     3.删除YAML文件内容
'''
import os
import yaml
class  YamlTools:

    #cur_dir=((os.path.dirname(__file__)))  #当前文件目录
    #par_dir=((os.path.dirname(cur_dir))) #当前文件的上级目录

    # 写入token，token.yml用于存放token
    def write_yaml(self,data):

        with open((os.path.dirname((os.path.dirname(__file__))))+"/testData/token.yml",mode='a',encoding='utf-8') as f:
            yaml.dump(data=data,stream=f,allow_unicode=True)


     #清除token
    def clear_yaml(self):
        with open((os.path.dirname((os.path.dirname(__file__))))+"/testData/token.yml",mode='w',encoding='utf-8') as f:
            f.truncate()


    #读取YAML文件 OK
    def  read_yaml(self,yaml_name):
        with open((os.path.dirname((os.path.dirname(__file__))))+"/testData/"+yaml_name,mode='r',encoding='utf-8') as f:
            value=yaml.load(stream=f,Loader=yaml.FullLoader)
            return value

    #读取环境配置文件environment.yml
    def read_environment_yaml(self):
        with open((os.path.dirname((os.path.dirname(__file__)))) + "/environment.yml", mode='r',encoding='utf-8') as f:
            value = yaml.load(stream=f, Loader=yaml.FullLoader) #OK

            #print(value)
            con_url=value['environment']['url']

            return con_url
    
