#!/usr/bin/python
import urllib2
import json
import argparse
import time
import logging
import zabbixlib

def authenticate(url, username, password):
    values = {'jsonrpc': '2.0',
              'method': 'user.login',
              'params': {
                  'user': username,
                  'password': password
              },
              'id': '0'
              }

    data = json.dumps(values)
    req = urllib2.Request(url, data, {'Content-Type': 'application/json-rpc'})
    response = urllib2.urlopen(req, data)
    output = json.loads(response.read())

    try:
        message = output['result']
    except:
        message = output['error']['data']
        print message
        quit()

    return output['result']


def screenCreate(url, auth, screen_name, graphids, columns):
    # print graphids
    if len(graphids) % columns == 0:
        vsize = len(graphids) / columns
    else:
        vsize = (len(graphids) / columns) + 1

    values = {"jsonrpc": "2.0",
              "method": "screen.create",
              "params": [{
                  "name": screen_name,
                  "hsize": columns,
                  "vsize": vsize,
                  "screenitems": []
              }],
              "auth": auth,
              "id": 2
              }

    for i in graphids:
        values['params'][0]['screenitems'].append(i)

    data = json.dumps(values)
    req = urllib2.Request(url, data, {'Content-Type': 'application/json-rpc'})
    response = urllib2.urlopen(req, data)
    host_get = response.read()

    output = json.loads(host_get)

    try:
        message = output['result']
    except:
        message = output['error']['data']

    print json.dumps(message)


def main():
    logging.basicConfig(filename='zabbix-screen.log', level=logging.INFO)
    logging.info('Started')
    url = 'http://URL/zabbix/api_jsonrpc.php'

    parser = argparse.ArgumentParser(description='Create Zabbix screen from all of a host Items or Graphs.')
    parser.add_argument('screentype', metavar='A', type=str,
                        help='Set the type as "graph" or "host". This script will create screen per this value.')
    parser.add_argument('hostname', metavar='H', type=str,
                        help='Zabbix Host to create screen from')
    parser.add_argument('screenname', metavar='N', type=str,
                        help='Screen name in Zabbix.  Put quotes around it if you want space in the name.')
    parser.add_argument('username', metavar='V', type=str,
                        help='zabbix username')
    parser.add_argument('password', metavar='W', type=str,
                        help='zabbix password')
    parser.add_argument('-c', dest='columns', type=int, default=3,
                        help='number of columns in the screen (default: 3)')

    args = parser.parse_args()
    screentype = args.screentype
    hostname = args.hostname
    username = args.username
    password = args.password
    screen_name = args.screenname
    columns = args.columns

    auth = authenticate(url, username, password)
    graphids = zabbixlib.getGraph(screentype, hostname, url, auth, columns)

    print "Screen name: " + screen_name
    print "Total number of graphs: " + str(len(graphids))

    screenCreate(url, auth, screen_name, graphids, columns)

    logging.info('Finished')

if __name__ == '__main__':
    main()
