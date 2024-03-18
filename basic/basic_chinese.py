"""
中文字符的编码范围是：
\u4e00 - \u9fff
只要编码在此范围就可判断为中文字符
"""


def is_chinese(string):
    """
    检查整个字符串是否包含中文
    :param string: 需要检查的字符串
    :return: bool
    """
    for ch in string:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True

    return False


ret1 = is_chinese("刘亦菲")
print(ret1)
ret2 = is_chinese("123")
print(ret2)
