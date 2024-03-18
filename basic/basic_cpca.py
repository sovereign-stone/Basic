import cpca


def cpca_get_province(address):
    """

    cpca方法可以输入任意的可迭代类型（如list，pandas的Series类型等），然后将其转换为一个DataFrame

    :param address:
    :return: dict
    """
    dict_province = {}
    try:
        df = cpca.transform(address)
    except Exception as e:
        return e
    if len(df) == 1:
        province = df.loc[0, '省'] if df.loc[0, '省'] else ''
        city = df.loc[0, '市'] if df.loc[0, '市'] else ''
        distinct = df.loc[0, '区'] if df.loc[0, '区'] else ''
        dict_province['province'] = province
        dict_province['city'] = city
        dict_province['distinct'] = distinct
        return dict_province


# addr = ['重庆市武隆县网安支队']
# res = cpca_get_province(addr)
# print(res)
