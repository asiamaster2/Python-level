#!/usr/bin/python

from elasticsearch import Elasticsearch
import argparse
import ast
import time
from datetime import date
import requests
import os
import base64
import sys
import json
import mysql.connector
from datetime import datetime
import re
from zabbixconfig import *

# buffer size
buffsize = 2000

# Configuration for ES6
esport = 9200
# For everyday
esindex = 'INDEXNAME-' + date.today().strftime("%Y.%m.%d")
estype = 'log'
es = Elasticsearch(['es01.URL', 'es02.URL', 'es03.URL', 'es04.URL'],
                   port=esport,
                   )


# Write the last time / It queries the data before 5 mins if there is no last time.
def getlasttime():
    if os.path.isfile('lasttime.txt'):
        file = open('lasttime.txt', 'r')
        rs = file.read()
        try:
            rs
        except NameError:
            rs = time.time() - 300
            rs = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.localtime(int(rs)))
            file1 = open('lasttime.txt', 'w')
            file1.write(str(rs))
            file1.close()
        file.close()
    else:
        rs = time.time() - 300
        rs = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.localtime(int(rs)))
        file = open('lasttime.txt', 'w')
        file.write(str(rs))
        file.close()
    return rs


def getValue(lasttimestamp, tablename):
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()

    # query = ("SELECT a.host, b.itemid, b.name, b.key_, c.clock, c.value "
    #         "FROM (Select hostid,host from hosts where host not like 'Template%') a "
    #         "INNER JOIN items b ON a.hostid = b.hostid "
    #         "INNER JOIN history c ON c.itemid = b.itemid and c.clock > %s and c.clock < %s order by clock;")
    query = 'select h.host, i.itemid, i.name, i.key_, date_format(from_unixtime(hs.clock),"%Y-%m-%dT%H:%i:%sZ") to_iso, hs.value from ' + str(
        tablename) + ' hs, items i, hosts h where hs.clock > ' + str(
        lasttimestamp) + ' and i.itemid = hs.itemid and i.hostid = h.hostid;'

    cursor.execute(query)
    a = list()
    s = {}

    for i in cursor:
        s['hostname'] = str(i[0])
        s['itemid'] = str(i[1])
        s['itemkey'] = str(i[3])
        s['time'] = str(i[4])
        s['value'] = i[5]

        if '$' in str(i[2]):
            t = str(i[3]).split(',')
            g = re.findall('\d+', str(i[2]))
            for z in g:
                if '[' in t[int(z) - 1]:
                    t = t[int(z) - 1].split('[')
                    tdevicename = t[int(z)].replace(']', '')
                else:
                    tdevicename = t[int(z) - 1].replace(']', '')
                s['itemname'] = str(i[2]).replace('$' + z, tdevicename)
        else:
            s['itemname'] = str(i[2])

        a.append(json.dumps(s))
    cursor.close()
    cnx.close()
    return a


# Insert the data to ES6
def insertdata(bodydata):
    rs = "no error"
    try:
        es.bulk(index=esindex, doc_type=estype, body='\n'.join(bodydata))
    except OSError:
        print "something wrong"
        exit(1)
    else:
        rs = time.time()
        rs = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.localtime(int(rs)))
        file = open('lasttime.txt', 'w')
        file.write(str(rs))
        file.close()
    return rs


try:
    while (not time.sleep(60)):
        if __name__ == '__main__':
            lasttime = getlasttime()
            lasttime = datetime.strptime(lasttime, "%Y-%m-%dT%H:%M:%SZ")
            lasttimestamp = time.mktime(lasttime.timetuple())
            tablename = ('history', 'history_uint')

            for tt in tablename:

                hostanditem = getValue(lasttimestamp, tt)
                s = list()
                seq = 0
                for i in hostanditem:
                    idx = {"index": {"_type": estype, "_index": esindex}}
                    s.append(json.dumps(idx))
                    s.append(i)
                    seq = seq + 1
                    if seq % buffsize == 0 and seq > 0:
                        # print seq, len(hostanditem)
                        insertdata(s)
                        del (s[:])
                    elif seq >= len(hostanditem):
                        insertdata(s)
                        # print seq, len(hostanditem)
                        del (s[:])
                    else:
                        continue
                print "All data has been sent."
except OSError:
    print("Connection error")
    exit(1)
else:
    print "Nothing"

