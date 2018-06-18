import requester

service_code="AAAA"
confdir="conf/var.conf"


def main(service_code,confdir,orderid):
    value = requester.get_value(service_code,confdir,orderid)
    print(value["response"]["result"])

if __name__ == '__main__':
    with open('conf/orderid.txt') as openorderid:
        for orderid in openorderid:
            main(service_code, confdir, orderid)
    #main(service_code,confdir,orderid)