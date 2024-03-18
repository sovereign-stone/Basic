import time
import datetime


class BasicTime(object):
    def __init__(self):
        self.now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.now_date = datetime.datetime.now().strftime('%Y-%m-%d')

    @staticmethod
    def trans_format(time_string, from_format, to_format='%Y-%m-%d %H:%M:%S'):
        time_struct = time.strptime(time_string, from_format)
        times = time.strftime(to_format, time_struct)
        return times

    @staticmethod
    def date_add_hours(str_date, num=8, date_format="%Y-%m-%d %H:%M:%S"):
        # 给当前时间加上8小时
        tmp = datetime.datetime.strptime(str_date, date_format)
        eta = (tmp + datetime.timedelta(hours=num)).strftime(date_format)
        return eta

    @staticmethod
    def date_format_change(date, before_format, after_format="%Y-%m-%d"):
        """

        转换日期时间的格式
        例   10/16/2015  -> 2015-10-16
        time1 = '10/16/2015'
        timeArray = time.strptime(time1, "%m/%d/%Y")
        otherStyleTime = time.strftime("%Y-%m-%d", timeArray)
        print(otherStyleTime)

        :param date: 要转换的时间
        :param before_format: 转换之前的时间格式
        :param after_format: 转换之后的时间格式， 默认为2021-01-01(%Y-%m-%d)
        :return: 转换了格式之后的时间
        """
        time_array = time.strptime(date, before_format)
        end_time = time.strftime(after_format, time_array)
        return end_time

    @staticmethod
    def get_before_date(number=1, fmt="%Y-%m-%d"):
        # num=0为今天,num=1为昨天,num=2为前天,num=n为不含今天的前n天时间
        today = datetime.datetime.now()
        offset = datetime.timedelta(days=number)
        res_date = (today - offset).strftime(fmt)
        return res_date

    @staticmethod
    def get_after_date(number=1, fmt="%Y-%m-%d"):
        # num=0为今天,num=1为明天,num=2为后天,num=n为不含今天的后n天时间
        today = datetime.datetime.now()
        offset = datetime.timedelta(days=number)
        res_date = (today + offset).strftime(fmt)
        return res_date

    @staticmethod
    def datetime_to_int(str_time, fmt="%Y-%m-%d"):
        # 将字符串时间转换为时间戳
        time_obj = datetime.datetime.strptime(str_time, fmt)
        int_time = int(time_obj.timestamp())
        return int_time