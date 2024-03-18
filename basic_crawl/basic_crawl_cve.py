import random
import time
import requests
import json
import re
from retrying import retry
from lxml import html
from basic.server.ua_pool import ua
from basic.other_server.proxy_list import get_soc_ip
from loguru import logger

logger.add(
    sink='./logs/basic_crawl_cve.log',
    level='ERROR',
    format='{time:YYYY-MM-DD HH:mm:ss} | {level} - {file} - {line} - {message}',
    rotation='00:00',
    retention='2 days'
)


class CrawlCVE(object):
    def __init__(self):
        self.nvd_base_url = 'https://nvd.nist.gov/vuln/detail/'
        self.ghb_base_url = 'https://raw.githubusercontent.com/CVEProject/cvelist/master/'

    def make_github_url(self, cve_id):
        # 从cve_id中组合出github中cve详情的url
        cve_number = cve_id.split('-')[-1]
        cve_year = cve_id.split('-')[-2]
        if len(cve_number) == 7:
            base_cve_id = cve_number[:4] + 'xxx'
        elif len(cve_number) == 6:
            base_cve_id = cve_number[:3] + 'xxx'
        elif len(cve_number) == 5:
            base_cve_id = cve_number[:2] + 'xxx'
        else:
            base_cve_id = cve_number[:1] + 'xxx'
        github_url = self.ghb_base_url + cve_year + '/' + base_cve_id + '/' + cve_id + '.json'
        return github_url

    @retry(stop_max_attempt_number=5, wait_fixed=3000)
    def download_github_json(self, cve_id):
        headers = {"User-Agent": random.choice(ua)}
        proxy = get_soc_ip()
        url = self.make_github_url(cve_id=cve_id)
        logger.info(f'github: {url}')
        resp = requests.get(url, headers=headers, proxies=proxy, timeout=30)
        status_code = resp.status_code
        resp_content = resp.content.decode('utf-8')
        if status_code == 200:
            if resp_content:
                return resp_content
            else:
                return 'status error'
        else:
            return 'status error'

    @staticmethod
    def date_format_change(str_date):
        # 改变nvd中时间格式
        try:
            if str_date == '':
                return '2000-01-01'
            else:
                time_array = time.strptime(str_date, "%m/%d/%Y")
                end_time = time.strftime("%Y-%m-%d", time_array)
                return end_time
        except Exception as e:
            return '2000-01-01'

    @retry(stop_max_attempt_number=5, wait_fixed=3000)
    def get_nvd_detail(self, cve_id):
        patch_list = []
        logger.info(f'nvd: {cve_id}')
        headers = {"User-Agent": random.choice(ua)}
        proxy = get_soc_ip()
        resp = requests.get(self.nvd_base_url + cve_id, headers=headers, proxies=proxy, timeout=30).content.decode('utf-8')
        selector = html.fromstring(resp)
        # page_title = selector.xpath('//*[@id="ErrorPanel"]/h2/text()')

        try:
            modified_info = selector.xpath('//p[@data-testid="vuln-warning-banner-content"]/text()')[0]
        except Exception as e:
            modified_info = ''
        cvss3_base_score = selector.xpath('//*[data-testid="vuln-cvss3-panel"]/div[1]/div[2]/span/span/a/text()')
        cvss2_base_score = selector.xpath('//*[data-testid="vuln-cvss2-panel"]/div[1]/div[2]/span/span/a/text()')
        resource = selector.xpath('//*[@data-testid="vuln-hyperlinks-table"]//a/text()')
        if len(resource) > 0:
            for num in range(len(resource)):
                try:
                    is_tag = selector.xpath(
                        f'//*[@data-testid="vuln-hyperlinks-resType-{num}"]//span[@class="badge"]/text()')
                    if len(is_tag) > 0:
                        tag = []
                        for each in is_tag:
                            tag.append(each)
                    else:
                        tag = 'None'
                    ref_url = resource[num]
                    patch_list.append({'ref_url': ref_url, 'tag': tag})
                except Exception as e:
                    tag = 'None'
                    ref_url = resource[num]
                    patch_list.append({'ref_url': ref_url, 'tag': tag})
        else:
            ref_url = ''
            tag = 'None'
            patch_list.append({'ref_url': ref_url, 'tag': tag})
        cwe_tag = selector.xpath('//*[@data-testid="vuln-CWEs-link-0"]/a/text()')
        if len(cwe_tag) > 0:
            if cwe_tag[0].strip():
                cwe_id = selector.xpath('//*[@data-testid="vuln-CWEs-link-0"]/a/text()')[0]
                cwe_source = selector.xpath('//*[@data-testid="vuln-cwes-assigner-0-0"]//span/text()')[0].strip()
                cwe_name = re.findall('data-testid="vuln-CWEs-link-0">(.*?)</td>', resp)[0]
            else:
                cwe_id = 'None'
                cwe_source = 'None'
                cwe_name = 'None'
        else:
            cwe_id = 'None'
            cwe_source = 'None'
            cwe_name = 'None'

        publish_time = selector.xpath('//*[@class="bs-callout bs-callout-info"]/span[1]/text()')
        last_modified = selector.xpath('//*[@class="bs-callout bs-callout-info"]/span[2]/text()')
        source = selector.xpath('//*[@class="bs-callout bs-callout-info"]/span[3]/text()')
        pub_time = self.date_format_change(publish_time[0] if len(publish_time) > 0 else '')
        la_mod = self.date_format_change(last_modified[0] if len(last_modified) > 0 else '')
        sou = source[0] if len(source) > 0 else 'MITRE'

        nvd_parm_dict = {
            'cve_id': cve_id,
            'publish_time': pub_time,
            'last_modified': la_mod,
            'source': sou,
            'modified_note': {'english': modified_info},
            'severity': {'cvss3_base_score': cvss3_base_score, 'cvss2_base_score': cvss2_base_score},
            'weakness_enumeration': {'cwe_id': cwe_id, 'cwe_name': cwe_name, 'cwe_source': cwe_source},
            'ref': patch_list
        }
        return nvd_parm_dict

    def get_cve_one(self, cve_id):
        # 返回cve详情或者cve的id
        ghb_detail = self.download_github_json(cve_id=cve_id)
        if ghb_detail == 'status error':
            return cve_id
        else:
            try:
                nvd_detail = self.get_nvd_detail(cve_id=cve_id)
            except Exception as e:
                nvd_detail = {
                    'cve_id': cve_id,
                    'publish_time': '2000-01-01',
                    'last_modified': '2000-01-01',
                    'source': 'MITRE',
                    'modified_note': {'english': ''},
                    'severity': {'cvss3_base_score': [], 'cvss2_base_score': []},
                    'weakness_enumeration': {'cwe_id': "None", 'cwe_name': "None", 'cwe_source': "None"},
                    'ref': [{'ref_url': '', 'tag': 'None'}]
                }
            ghb_dict = json.loads(ghb_detail)
            cve_detail = dict(ghb_dict, **nvd_detail)
            return cve_detail
