#coding=utf-8
# Author: XHS
# Date  : 2021/9/7 17:27
# File  : operateMongoDB.py
from  common.logger import Logger
import pymongo

class OperationMongoDB(object):
    global logger
    logger=Logger()
    def __init__(self,host,port,username,password,authSource,dbname):
        '''建立数据库连接'''
        self.connect_client=pymongo.MongoClient(host=host,
                                 port=port,
                                 username=username,
                                 password=password,
                                 authSource=authSource)
        self.DB = self.connect_client[dbname]#数据库名字
        logger.info('已建立数据库连接！')

        '''查询单条记录'''
    def select_data_one(self,collection_name,columnName,colValue):
        collection=self.DB[collection_name]   #指定集合
        try:
            result = collection.find_one({columnName:colValue})  #查询单条记录
            logger.info(f'数据库查询返回结果:{result}')
            #t.sleep(10)
            return result         #如果没有数据则默认返回None
        except Exception as  e:
            print(e)

        '''删除单条活动记录'''
    def delete_data_one(self,collection_name,columnName,colValue):
        collection = self.DB[collection_name]
        try:
            count=collection.count_documents({columnName:colValue})   #先判断是否有记录
            logger.info(f'数据库记录总数:{count}')
            if count!=0:
                collection.delete_one({columnName: colValue})
                logger.info(f'已删除记录:{colValue}')
            else:
                logger.info(f'数据库不存在该记录:{colValue}')
        except Exception as  e:
            logger.info(e)

        '''关闭连接'''
    def close_connect(self):
        self.connect_client.close()
        logger.info('已断开数据库连接！')





if __name__=="__main__":
    aa=OperationMongoDB(host='',
        )

    aa.select_data_one('activities','activity_id','HD100520')  #HD100520
    aa.delete_data_one('activities', 'activity_id', 'HD100520')  # HD100520
    aa.close_connect()

