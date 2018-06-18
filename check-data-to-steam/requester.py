import requests
import ConfigParser

def get_value(service_code,confdir,orderid):
    cfg = ConfigParser.ConfigParser()
    cfg.read(confdir)
    params = {'key': cfg.get(service_code,'key'),'appid': cfg.get(service_code,'appid'),'orderid': orderid}
    res = requests.get(cfg.get(service_code,'URL'), params)

    if res.status_code == 200:
        return res.json()
    else:
        res = {'response': {'result': 'ERROR'}}
        return res

