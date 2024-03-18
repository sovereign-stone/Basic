import time
import datetime
from loguru import logger
from elasticsearch import Elasticsearch
from elasticsearch import helpers


class ConnectES(object):
    def __init__(self, hosts='127.0.0.1:9200', username='elastic', password='elastic'):
        if username and password:
            self.conn_es = Elasticsearch([hosts], http_auth=(username, password), request_timeout=120)
        else:
            self.conn_es = Elasticsearch([hosts], request_timeout=120)

    def es_body_search(self, index, body):
        result = self.conn_es.search(index=index, body=body, request_timeout=60)
        return result

    def update_es_one_data(self, index, ids, update_dict):
        """

        update es one data: {"doc": {"distinct": ""}}

        :param index: index name
        :param ids: es _id
        :param update_dict: update dict, example: update dict={"doc": {"distinct": ""}}
        :return:
        """
        if ids:
            self.conn_es.update(index=index, id=ids, body=update_dict)
        else:
            self.conn_es.index(index=index, body=update_dict)

    def index_es_one_data(self, index, ids, data):
        if ids:
            self.conn_es.index(index=index, id=ids, body=data, doc_type='_doc')
        else:
            self.conn_es.index(index=index, body=data, doc_type='_doc')

    def get_es_one_data(self, index_name, field, value):
        body = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "term": {
                                field: {
                                    "value": value
                                }
                            }
                        }
                    ]
                }
            }
        }
        result = self.conn_es.search(index=index_name, body=body, request_timeout=30)
        count = result['hits']['total']['value']
        if count > 0:
            for j in result['hits']['hits']:
                ids = j['_id']
                es_data = j['_source']
                return ids, es_data
        else:
            return '', {}

    def bulk_insert_data(self, list_data):
        """
        helpers.bulk insert data to es, 字典里面包括_index, _type, _id, _source
        example:
            one_dict = {}
            one_dict['_index'] = index
            one_dict['_id'] = j['domain']
            one_dict['_type'] = "_doc"
            one_dict['_source'] = j
            es_list.append(one_dict)

        :param list_data: type is list
        :return: insert paste time
        """
        start_time = datetime.datetime.now()
        helpers.bulk(self.conn_es, list_data)
        end_time = datetime.datetime.now()
        paste_time = end_time - start_time
        return paste_time

    def get_data_from_time(self, index, start_time=None, end_time=None, size=10000):
        # 根据时间排序，每次获取10000条数据，快速获取数据,不到达指定的时间不停止
        now_timestamp = int(time.time())
        now_time = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(now_timestamp))
        if not start_time:
            start_time = '2022-01-01T00:00:00'
        if not end_time:
            end_time = now_time

        body = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "range": {
                                "@timestamp": {
                                    "gte": start_time,
                                    "lte": end_time
                                }
                            }
                        }
                    ]
                }
            },
            "sort": [
                {
                    "@timestamp": {
                        "order": "asc"
                    }
                }
            ],
            "_source": ["url", "publish_time", "title", "uuid", "@timestamp"],
            "size": size
        }
        result = self.es_body_search(index=index, body=body)
        count = result['hits']['total']['value']
        data = result['hits']['hits']
        if count <= 1:
            return count
        else:
            max_time = data[-1]['_source']['@timestamp']
            logger.info(f'count: {count}, max time: {max_time}')
            for j in data:
                pass
            # self.get_data_from_time(index_name=index_name, start_time=max_time, end_time=end_time)
        return
