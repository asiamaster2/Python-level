from elasticsearch import Elasticsearch
import argparse
import ast
import time
from datetime import date
import requests
import os
import base64
import sys

from influxdb import InfluxDBClient
from influxdb.client import InfluxDBClientError
import json
import bz2
sys.path.append('/usr/local/infconf')
from infpass import *

LOCKFILE_LOCATION = "./sciprtisrunning"

# buffer size
buffsize = 5000

# Configuration for influxDB
USER = 'USERID'

DBNAME = 'k8s'
# Needs an ClusterIP or you can set NodePort and use the host IP
host = 'monitoring-influxdb.default.svc'
port = 8086
client = InfluxDBClient(host, port, USER, PASSWORD, DBNAME)

# Configuration for ES6
esport = 9100
esindex = 'INDEX-STAGING-' + date.today().strftime("%Y.%m.%d")
estype = 'log'
# es= Elasticsearch([{'host': eshost, 'port': esport, }])
es = Elasticsearch(['es02.URL', 'es03.URL', 'es04.URL', 'es01.URL'],
                   port=esport,
                   )
nodedata = 'no'


# lock to not run duplicated.
def lockfile():
    try:
        os.open(LOCKFILE_LOCATION, os.O_CREAT | os.O_WRONLY | os.O_EXCL)
        # Maybe even write the script's PID to this file, just in case you need
        # to check whether the program died unexpectedly.
    except OSError:
        # File exists or could not be created. Can check errno if you really
        # need to know, but this may be OS dependent.
        print("Failed to create lockfile. Is another instance already running?")
        exit(1)
    else:
        print "Start to send the metrics to ES6."


# Get the tablename from InfluxDB
def tablenames():
    query = 'SHOW MEASUREMENTS;'
    result = client.query(query, database=DBNAME)
    rs = list(result.get_points(measurement=None, tags=None))
    return rs


# Get the metrics from InfluxDB
def metricsval(tname, ltime):
    # without node data
    if nodedata == 'no':
        nodequery = ' AND ("type" != \'sys_container\' AND "type" != \'node\') order by time asc limit 0'
    else:
        nodequery = ' order by time asc limit 0'
    query = 'SELECT * FROM "' + tname + '" WHERE (time > ' + ltime + ' and time < now() -10s)' + nodequery
    #print query
    result = client.query(query, database=DBNAME)
    rs = list(result.get_points(measurement=None, tags=None))
    return rs


# Get the last time from ES6(the same index)
def getlasttime(tname):
    # Check whether there is a data
    if es.indices.exists(index=esindex):
        tval = es.search(index=esindex, doc_type=estype,
                         body={"query": {"query_string": {"query": "(tablename:\"" + tname + "\")"}}, "_source": "time",
                               "sort": {"time": {"order": "desc"}}}, size=1)
        if tval['hits']['total'] == 0:
            rs = date.today().strftime("%Y-%m-%d") + 'T00:00:00Z'
        else:
            rs = dict(dict(tval['hits']['hits'][0])['_source'])['time']
    else:
        rs = date.today().strftime("%Y-%m-%d") + 'T00:00:00Z'
    return rs


# Insert the metrics data to ES6
def insertdata(bodydata):
    rs = "no error"
    # print esindex, estype, bodyval
    # es.index(index=esindex, doc_type=estype, body=bodyval)
    es.bulk(index=esindex, doc_type=estype, body='\n'.join(bodydata))
    # time.sleep(1000)
    return rs


while (not time.sleep(60)):
    if __name__ == '__main__':
        table_names = tablenames()
        s = list()
        lockfile()
        for i in table_names:
            lasttime = "'" + getlasttime(i['name']) + "'"
            result = metricsval(i['name'], lasttime)
            # print i['name'], lasttime
            seq = 0
            for x in result:
                # Apeend the index name
                idx = {"index": {"_type": estype, "_index": esindex}}
                s.append(json.dumps(idx))
                # Append the table name
                x['tablename'] = i['name']
                s.append(json.dumps(x))
                seq = seq + 1
                if seq % buffsize == 0 and seq > 0:
                    #print i['name'], seq, len(s), len(result)
                    insertdata(s)
                    del (s[:])
                elif seq >= len(result):
                    insertdata(s)
                    #print i['name'], len(s), len(result)
                    del (s[:])
                else:
                    continue

        os.remove(LOCKFILE_LOCATION)
        print "All data has been sent."
