import re
import dns.resolver
import maxminddb
import uuid
import hashlib
import socket
from loguru import logger
from functools import reduce
from tld import get_tld


class BasicUse(object):
    def __init__(self):
        geoip = '/home/geoip/soc-geoip.socdb'
        scene = '/home/geoip/soc-scene.socdb'
        self.geoip_reader = maxminddb.open_database(geoip)
        self.scene_reader = maxminddb.open_database(scene)

    @staticmethod
    def get_uuid():
        # 自动生成唯一id
        unique_id = uuid.uuid4()
        return unique_id

    @staticmethod
    def hashlib_md5(keyword):
        md5 = hashlib.md5()
        md5.update(keyword.encode('utf-8'))  # 注意转码
        res = md5.hexdigest()
        return res

    @staticmethod
    def hash_value(string):
        # 将字符串通过SHA1哈希生成唯一id
        sha1 = hashlib.sha1()
        sha1.update(string.encode('utf-8'))
        res = sha1.hexdigest()
        return res

    @staticmethod
    def remove_duplicate(data_list):
        # 对列表中的字典去重
        function = lambda x, y: x if y in x else x + [y]
        new_list = reduce(function, [[], ] + data_list)
        return new_list

    @staticmethod
    def sorted_list(data):
        sorted_data = sorted(data, key=lambda x: x['key'])
        return sorted_data

    @staticmethod
    def distinct_list_dict_key(data_list, key):
        # 对列表中的字典按照key(特定值)进行去重
        # key 必须在所有的字典中都存在
        new_data = [data_list[0]]
        for tar in data_list:
            k = 0
            for item in new_data:
                if tar[key] != item[key]:
                    k = k + 1
                else:
                    break
                if k == len(new_data):
                    new_data.append(tar)
        return new_data

    @staticmethod
    def replace_text(text, old_word, new_word):
        new_text = text.replace(old_word, new_word)
        return new_text

    def soc_geoip(self, ip):
        geoip_result = self.geoip_reader.get(ip)
        scene_result = self.scene_reader.get(ip)
        geoip = geoip_result if geoip_result else {}
        scene = scene_result.get('scene', '') if scene_result else ''
        geoip['scene'] = scene
        save_result = {'ip': ip, 'geoip': geoip}
        return save_result

    @staticmethod
    def extract_domain(target: str):
        try:
            result = re.findall('(?<=://)[a-zA-Z\.0-9]+(?=\/)', target)[0]
        except:
            subdomain = target.split('//')[-1]
            domain = subdomain.split('/')
            if len(domain) >= 2:
                result = domain[0]
            else:
                result = domain[0]
        return result

    @staticmethod
    def dns_parse(domain):
        try:
            ip_list = []
            # res = dns.resolver.query(domain, 'A')  # 指定查看类型为A记录
            res = dns.resolver.resolve(domain, 'A')
            for i in res.response.answer:  # 通过response.answer方法获取查询回应信息
                for j in i.items:  # 遍历回应信息
                    ip_list.append(j.address)
            return ip_list
        except Exception as e:
            # logger.error(f'dns parse error domain: {domain}, error reason {e}')
            try:
                ip_address = socket.gethostbyname(domain)
                return [ip_address]
            except socket.gaierror:
                return []

    @staticmethod
    def tld_parse(domain):
        try:
            res = get_tld(domain, fix_protocol=True, as_object=True)
            dom = res.fld
            trd = res.subdomain
            tld = res.tld
            sld = res.domain
            return {"tld": {"domain": dom, "subdomain": domain, "trd": trd, "tld": tld, "sld": sld}}
        except Exception as e:
            logger.error(f'tld parse error domain: {domain}, error reason: {e}')
            return {"tld": {}}

    @staticmethod
    def draw_ip(info):
        try:
            rip = re.findall('((?:(?:25[0-5]|2[0-4]\\d|[01]?\\d?\\d)\\.){3}(?:25[0-5]|2[0-4]\\d|[01]?\\d?\\d))', info)
            if len(rip) > 0:
                return rip[0]
            else:
                return ''
        except Exception as e:
            logger.error(f'info draw ip error: {info}, error reason: {e}')
            return ''
