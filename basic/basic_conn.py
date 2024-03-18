import redis
import pymysql
import pymongo
import psycopg2
import numpy as np
import pandas as pd
from sqlalchemy import create_engine


class ConnectRedis(object):
    def __init__(self, host='127.0.0.1', db=0, port=6379, password='stone'):
        self.red = redis.StrictRedis(host=host, port=port, db=db, password=password,
                                     decode_responses=True, charset='UTF-8', encoding='UTF-8')

class ConnectMongo(object):
    def __init__(self, db_name, host='127.0.0.1', port='27017', name='stone', password='stone'):
        client = pymongo.MongoClient(f'mongodb://{host}:{port}/')
        self.db_mongo = client[db_name]
        self.db_mongo.authenticate(name, password, mechanism='SCRAM-SHA-1')

    def query_mongo(self, col_name, data_dict=None, skip=0, limit=10, sort_key='_id'):
        # query mongodb
        if data_dict is None:
            data_dict = {}
        col_start = self.db_mongo[col_name]
        data_list = []
        # {'_id': 0} 表示排除 _id 字段
        with col_start.find(data_dict, {'_id': 0}).skip(skip).limit(limit).sort(sort_key, -1) as cursors:
            for j in cursors:
                data_list.append(j)
        return data_list

    def count_query(self, col_name, data_dict=None):
        if data_dict is None:
            data_dict = {}
        col_start = self.db_mongo[col_name]
        count = col_start.count_documents(data_dict)
        return count

    def update_one(self, col_name, query_dict, data_dict):
        # update collection one data, upsert=True: if existed update else insert
        collection = self.db_mongo[col_name]
        info = collection.update_one(query_dict, {'$set': data_dict}, upsert=True)
        return info.acknowledged, info.matched_count

    def update_add_array(self, col_name, query_dict, update_dict):
        # 向mongodb单个文档数组array类型中添加新的数据
        collection = self.db_mongo[col_name]
        info = collection.update_one(query_dict, {"$addToSet": update_dict}, upsert=True)
        return info.acknowledged, info.matched_count

    def mongo_data_copy(self, start_col, copy_col):
        """

        复制一个大的集合数据，mongodb游标默认保持10分钟，如果集合数据很大，那么会报错；使用
        with col_start.find(no_cursor_timeout=True) as cursors 来解决游标超时问题
        如果设置了no_cursor_timeout还报错，那么加上 batch_size=10 ，一次读取少量的几条
        :param start_col: 集合的名称
        :param copy_col: 复制后集合的名称
        :return:
        """
        col_start = self.db_mongo[start_col]
        col_end = self.db_mongo[copy_col]
        with col_start.find(no_cursor_timeout=True, batch_size=10) as cursors:
            for j in cursors:
                del j['_id']
                col_end.insert_one(j)
        return

    def query_common_condition_agge(self, col_name, condition, con_name, limit_con, limit_name, gt_num=1, sort_num=-1):
        # 对mongodb进行管道聚合查询
        collection = self.db_mongo[col_name]
        agge_list = [
            {"$match": {f"{condition}": {'$ne': ''}, f"{limit_con}": {"$regex": f"{limit_name}"}}},
            {"$group": {"_id": {f'{con_name}': f'${condition}'}, "count": {"$sum": 1}}},
            {"$match": {'count': {"$gt": gt_num}}},
            {"$sort": {'count': sort_num}}
        ]
        result = collection.aggregate(agge_list)
        results = []
        for j in result:
            each_tar = {f'{con_name}': j['_id'][f'{con_name}'], 'count': j['count']}
            results.append(each_tar)
        return results


class ConnectPostgres(object):
    def __init__(self, dbname):
        self.conn = psycopg2.connect(database='stone', user='postgres', password='123456',
                                     host='localhost', port='5432')
        self.engine = create_engine(f'postgresql://postgres:123456@localhost:5432/stone')
        self.dbname = dbname

    def get_pg_data(self, query):
        # query: select * from gonganbeian_info where id >2500 and id < 2600;
        self.conn.cursor()
        df = pd.read_sql_query(query, con=self.engine)
        df1 = np.array(df)  # 先使用array()将DataFrame转换一下
        df2 = df1.tolist()  # 再将转换后的数据用tolist()转成列表
        return df2


class ConnectMysql(object):
    db_config = {
        'host': '127.0.0.1',
        'port': 3306,
        'user': 'stone',
        'password': 'stone',
        'database': 'stone'
    }
    def __init__(self, db_config=None):
        if db_config is None:
            self.db_config = {
                'host': '127.0.0.1',
                'port': 3306,
                'user': 'stone',
                'password': 'stone',
                'database': 'stone'
            }

    def query_many_mysql(self, query_list):
        data_list = []
        # 对每个查询建立新的连接，并执行查询
        for query in query_list:
            conn = pymysql.connect(**self.db_config)
            try:
                with conn.cursor() as cursor:
                    cursor.execute(query)
                    result = [row for row in cursor.fetchall()]
            finally:
                conn.close()
            data_list.append(result)
        return data_list
