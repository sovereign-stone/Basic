from tld import get_tld


def parse_domain(domain):
    """

    解析顶级域名得到主域名等相关信息

    :param domain: 顶级域名
    :return: 字典 {"tld": {详情}}
    """
    # fix_protocol=True,默认为false，设置成为 true 即可忽略缺少的 scheme(http://，https://，ftp://)
    res = get_tld(domain, fix_protocol=True, as_object=True)
    dom = res.fld
    trd = res.subdomain
    tld = res.tld
    sld = res.domain
    return {"tld": {"domain": dom, "subdomain": domain, "trd": trd, "tld": tld, "sld": sld}}


res = parse_domain("yentoma.cloud")
print(res)
