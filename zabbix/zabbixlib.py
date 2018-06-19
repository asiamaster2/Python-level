import urllib2
import json
import argparse

def getGraph(screentype, hostname, url, auth, columns):
    selecttype = ['graphid']
    select = 'selectGraphs'

    if screentype == 'host':
        values = {'jsonrpc': '2.0',
                  'method': 'host.get',
                  'params': {
                      select: selecttype,
                      'output': ['hostid', 'host'],
                      'searchByAny': 1,
                      'filter': {
                          'host': hostname
                      }
                  },
                  'auth': auth,
                  'id': '2'
                  }
    elif screentype == 'graph':
        values = {'jsonrpc': '2.0',
                  'method': 'graph.get',
                  'params': {
                      select: selecttype,
                      'output': ['graphid', 'host'],
                      #    'searchByAny': 1,
                      'filter': {
                          'name': hostname,
                          'templateid': '533'
                      }
                  },
                  'auth': auth,
                  'id': '2'
                  }
    else:
        print "You should choose screen type 'host' or 'graph'"
        exit()

    data = json.dumps(values)
    req = urllib2.Request(url, data, {'Content-Type': 'application/json-rpc'})
    response = urllib2.urlopen(req, data)
    host_get = response.read()
    output = json.loads(host_get)

    graphs = []


    if screentype == 'host':
        tgraphs = output['result'][0]['graphs']
        for i in tgraphs:
            if i['templateid'] > '0':
                graphs.append(i['graphid'])
    elif screentype == 'graph':
        tgraphs = output['result']
        for i in tgraphs:
            graphs.append(i['graphid'])
    else:
        print "You should choose screen type 'host' or 'graph'"
        exit()

    graph_list = []
    x = 0
    y = 0

    for graph in graphs:
        graph_list.append({
            "resourcetype": 0,
            "resourceid": graph,
            "width": "500",
            "height": "100",
            "x": str(x),
            "y": str(y),
            "colspan": "1",
            "rowspan": "1",
            "elements": "0",
            "valign": "0",
            "halign": "0",
            "style": "0",
            "url": ""
        })
        x += 1
        if x == columns:
            x = 0
            y += 1

    return graph_list
