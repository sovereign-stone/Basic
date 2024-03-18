from phone import Phone


def get_phone_address(num):
    p = Phone()
    res = p.find(num)
    print(res)


get_phone_address(num='18838099656')
