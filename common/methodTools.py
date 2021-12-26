#coding=utf-8
# Author: XHS
# Date  : 2021/5/11 18:54
# File  : methodTools.py

import requests
import json

class RequestTools(object):
    '''
    功能：封装requests各种方法
    '''
    # get方法封装

    def get_method(self,url,data=None,header=None):

        if header is not None:
           res = requests.get(url,params=data,headers=header)
        else:
           res = requests.get(url,params=data)
        return res.json()

    # post方法封装

    def post_method(self, url, data=None, header=None):
        global res
        if header is not None:
            res = requests.post(url, json=data, headers=header)

        else:
             res = requests.post(url, json=data)
        if str(res) == "":
            return res.json()

        else:
            return res.text

    # put方法封装
    def put_method(self,url,data=None,header=None):
         if header is not None:
            res = requests.put(url,json=data,headers=header)
         else:
            res = requests.delete(url, json=data)
         return res.json()

   # delete方法封装

    def delete_method(self, url, data=None, header=None):
         if header is not None:
            res = requests.delete(url, json=data, headers=header)
         else:
            res = requests.delete(url, json=data)
         return res.json()

# 调用主方法

    def send_requests(self,method,url,data=None,header=None):
          if method == 'get' or method == 'GET':
             res = self.get_method(url,data,header)
          elif method == 'post' or method =='POST':
             res = self.post_method(url,data,header)
          elif method == 'put' or method == 'PUT':
             res = self.post_method(url,data,header)
          elif method == 'delete' or method == 'DELETE':
             res = self.post_method(url,data,header)
          else:
             res = "请求方式有误！"


          res = json.loads(res)
          return res
