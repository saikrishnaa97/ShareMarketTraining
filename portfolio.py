#!/usr/bin/python
import urllib.parse
import requests
import cgi
from datetime import datetime, timedelta, date
import calendar
import firebase_client
import urllib.parse
import getTopChangers
import json
from threading import Thread
import math
from datetime import datetime
from datetime import time
import pytz

def get_portfolio(user_id):
    data = firebase_client.get_portfolio(user_id)
    user_data = firebase_client.get_userDetails(user_id)
    result = {}
    result['portfolio'] = {}
    response = {}
    response['portfolio'] = []
    response['total_value'] = 0
    response['total_cost'] = 0
    stocksList = []
    isUpdateEligible = False
    IND_TZ = pytz.timezone("Asia/Kolkata")
    opentime = time(9,30,0)
    closetime = time(15,30,0)
    curDate = datetime.now(IND_TZ)
    if curDate.weekday() > 0 and curDate.weekday() < 6:
        if curDate.time() > opentime and curDate.time() < closetime:
            isUpdateEligible = True

    if  isUpdateEligible and int(datetime.now().strftime("%s")) - int(user_data['lastUpdatedTimestamp']) > 10:
        isUpdateEligible = True
        for k,i in data.items():
          if i['status'] == "HOLDING":
            item = {}
            item['symbol'] = urllib.parse.unquote(i['symbol'])
            item['avgCost'] = i['avgCost']
            item['uid'] = i['uid']
            stocksList.append(item)
        gttValues = {}
        numOfThreads = math.ceil(len(stocksList)/2)
        stocksPerThread = math.ceil(len(stocksList)/numOfThreads)
        i=0
        threads = []
        while i < numOfThreads:
            lastIndex = min((i+1)*stocksPerThread,len(stocksList))
            t = ThreadWithReturnValue( target= get_gtt_values,args = (stocksList[i*stocksPerThread:lastIndex],))
            threads.append(t)
            t.start()
            gttValues = { **gttValues , **t.join()}
            i = i + 1
    else:
        isUpdateEligible = False
        gttValues = {}
        for k,i in data.items():
            item = {}
            item['ltp'] = i['ltp']
            item['stopLoss'] = i['stopLoss']
            item['target'] = i['target']
            gttValues[i['uid']] = item
    for k,i in data.items():
        trade = {}
        trade['symbol'] = i['symbol']
        if i['status'] == "HOLDING":
           trade['ltp'] = gttValues[i['uid']]['ltp']
           trade['stopLoss'] = gttValues[i['uid']]['stopLoss']
           trade['target'] = gttValues[i['uid']]['target']
        else:
            trade['ltp'] = i['ltp']
            trade['stopLoss'] = i['stopLoss']
            trade['target'] = i['target']
        trade['numOfShares'] = i['numOfShares']
        trade['avgCost'] = i['avgCost']
        trade['uid'] = i['uid']
        trade['status'] = i['status']
        result['portfolio'][i['uid']] = trade
        response['portfolio'].append(trade)
        response['total_value'] += trade['numOfShares'] * trade['ltp']
        response['total_cost'] += trade['numOfShares'] * trade['avgCost']
    response['total_profit'] = float("{:.2f}".format(response['total_value'] - response['total_cost']))
    if isUpdateEligible:
        firebase_client.update_portfolio(user_id,result)
    return(response)

class ThreadWithReturnValue(Thread):

    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args,
                                                **self._kwargs)
    def join(self, *args):
        Thread.join(self, *args)
        return self._return

def get_gtt_values(stocksList):
    result = {}
    for i in stocksList:
        result[i['uid']] = {}
        stopLoss = get_nWeek_low(i['symbol'],10)
        ltp = get_stock_status(urllib.parse.quote_plus(i['symbol']))
        result[i['uid']]['stopLoss'] = stopLoss['price']
        result[i['uid']]['target'] = round(i['avgCost'] * 1.6,2)
        result[i['uid']]['ltp'] = ltp['ltp']
    return result

args = cgi.parse()
query_params = {}
for k,v in args.items():
    k = urllib.parse.quote(k)
    query_params[k] = []
    if type(v) is list:
        for j in v:
            j = urllib.parse.quote(j)
            query_params[k].append(j)
print('Content-type: application/json\r\n\r\n') # the mime-type header.
import sys
old= sys.stdout
environ = open("/tmp/file","w")
sys.stdout = environ
cgi.print_environ()
environ.flush()
sys.stdout = old
environ.close()
envData = open("/tmp/file","r")
environ = envData.read()
envData.close()
request_uri = "nseData/hello?"
for i in environ.split('\n'):
    if 'REQUEST_URI ' in i:
        request_uri = i.split("<DT> REQUEST_URI <DD> ")[1]
request_uri = request_uri.split("portfolio")[1].split("?")[0]
if request_uri == "/holdings":
    if 'user_id' in query_params.keys():
        print(json.dumps(get_portfolio(query_params['user_id'][0]),indent=1))
    else:
        print(json.dumps({"error":"user_id is missing"},indent=1))
