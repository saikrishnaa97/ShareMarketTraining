#!/usr/bin/python
#print('Content-type: application/json\r\n\r\n') # the mime-type header.
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

nse_url = "https://www.nseindia.com/"
nse1_url = "https://www1.nseindia.com/"
headers = {"user-agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36", "accept-encoding": "gzip,deflate, br","accept-language": "en-GB,en-US;q=0.9,en;q=0.8,la;q=0.7","sec-ch-ua-platform": "Linux", "sec-ch-ua": '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"'}


def get_cookie(cookie_url):
  conn = requests.Session()
  try:
   response = conn.get(cookie_url,headers=headers)
  except Exception as e:
      print(e)
      return e
  cookies = dict(response.cookies)
  conn.close()
  return cookies
#   return {}

def get_stock_status(symbol):
    current_url = nse_url+"api/quote-equity?symbol="+symbol
    cookies = get_cookie(nse_url)
    conn = requests.Session()
    response = conn.get(current_url,headers=headers,cookies=cookies)
    data = response.json()
    result = {}
    result['symbol'] = urllib.parse.unquote(symbol)
    result['name'] = data['info']['companyName']
    result['ltp'] = data['priceInfo']['lastPrice']
    conn.close()
    return result

def get_nse_status():
    current_url = nse1_url+"homepage/Indices1.json"
    cookies = get_cookie(nse_url)
    conn = requests.Session()
    response = conn.get(current_url,headers=headers,cookies=cookies)
    data = response.json()
    result = {}
    #TODO the url to be checked is this "https://www.nseindia.com/api/marketStatus"
    conn.close()
    for i in data['data']:
        if i['name'] == "NIFTY 50":
            result = i
            result.pop('imgFileName')
            return result
    return result

def search_stock(text):
    current_url = nse_url + "api/search/autocomplete?q="+text
    cookies = get_cookie(nse_url)
    conn = requests.Session()
    response = conn.get(current_url,headers=headers,cookies=cookies)
    data = response.json()
    result = {}
    result['data'] = []
    conn.close()
    for i in data['symbols']:
        temp = {}
        temp['symbol'] = i['symbol']
        temp['name'] = i['symbol_info']
        temp['url'] = i['url']
        result['data'].append(temp)
    return result

def get_index_stocks(index):
    current_url = nse_url + "api/equity-stockIndices?index="+index
    cookies = get_cookie(nse_url)
    conn = requests.Session()
    response = conn.get(current_url,headers=headers,cookies=cookies)
    data = response.json()
    result = {}
    result['data'] = []
    conn.close()
    result['index'] = data['name']
    for i in data['data']:
      if 'meta' in i.keys():
        temp = {}
        temp['symbol'] = i['symbol']
        temp['name'] = i['meta']['companyName']
        temp['ltp'] = i['lastPrice']
        temp['52WkHigh'] = i['yearHigh']
        temp['52WkLow'] = i['yearLow']
        temp['dayHigh'] = i['dayHigh']
        temp['dayLow'] = i['dayLow']
        result['data'].append(temp)
    return result

def get_historical_data(symbol,from_,to_):
    current_url = nse_url+"api/historical/cm/equity?symbol="+symbol+"&series=[\"EQ\"]&from="+from_+"&to="+to_
    cookies = get_cookie(nse_url)
    conn = requests.Session()
    response = conn.get(current_url,headers=headers,cookies=cookies)
    data = response.json()
    result = {}
    result['data'] = []
    conn.close()
    result['symbol'] = urllib.parse.unquote(symbol)
    for i in data['data']:
        temp = {}
        temp['date'] = i['mTIMESTAMP']
        temp['dayLow'] = i['CH_TRADE_LOW_PRICE']
        temp['dayHigh'] = i['CH_TRADE_HIGH_PRICE']
        temp['openingPrice'] = i['CH_OPENING_PRICE']
        temp['closingPrice'] = i['CH_CLOSING_PRICE']
        result['data'].append(temp)
    return result

#def get_top_gainers():
#    current_url = nse1_url + "live_market/dynaContent/live_analysis/gainers/niftyGainers1.json"
#    cookies = get_cookie(nse1_url)
#    conn = requests.Session()
#    response = conn.get(current_url,headers=headers,cookies=cookies)
#    data = response.json()
#    result = {}
#    result['data'] = []
#    conn.close()
#    for i in data['data']:
#        temp = {}
#        temp['symbol'] = i['symbol']
#        temp['ltp'] = i['ltp']
#        temp['highPrice'] = i['highPrice']
#        temp['lowPrice'] = i['lowPrice']
#        result['data'].append(temp)
#    return result

#def get_top_losers():
#    current_url = nse1_url + "live_market/dynaContent/live_analysis/losers/niftyLosers1.json"
#    cookies = get_cookie(nse1_url)
#    conn = requests.Session()
#    response = conn.get(current_url,headers=headers,cookies=cookies)
#    data = response.json()
#    result = {}
#    result['data'] = []
#    conn.close()
#    for i in data['data']:
#        temp = {}
#        temp['symbol'] = i['symbol']
#        temp['ltp'] = i['ltp']
#        temp['highPrice'] = i['highPrice']
#        temp['lowPrice'] = i['lowPrice']
#        result['data'].append(temp)
#    return result

def get_nWeek_low(symbol,weeks):
  to_ = str(date.today().strftime("%d-%m-%Y"))
  from_ = str((date.today() - timedelta(days=7*weeks)).strftime("%d-%m-%Y"))
  data = get_historical_data(symbol,from_,to_)
  lowPrice = 99999999
  lowDate = ""
  for i in data['data']:
      date_obj = datetime.strptime(i['date'],"%d-%b-%Y").date()
      if "Friday" == calendar.day_name[date_obj.weekday()]:
          if lowPrice > i['dayLow']:
              lowPrice = i['dayLow']
              lowDate = i['date']
  return json.loads('{"numberOfWeeks":'+str(weeks)+',"type":"Low","price":'+str(lowPrice)+',"symbol":"'+urllib.parse.unquote(symbol)+'","date":"'+lowDate+'"}')


def get_nWeek_high(symbol,weeks):
  to_ = str(date.today().strftime("%d-%m-%Y"))
  from_ = str((date.today() - timedelta(days=7*weeks)).strftime("%d-%m-%Y"))
  data = get_historical_data(symbol,from_,to_)
  highPrice = -1
  highDate = ""
  for i in data['data']:
      date_obj = datetime.strptime(i['date'],"%d-%b-%Y").date()
      if "Friday" == calendar.day_name[date_obj.weekday()]:
          if highPrice < i['dayHigh']:
              highPrice = i['dayHigh']
              highDate = i['date']
  return json.loads('{"numberOfWeeks":'+str(weeks)+',"type":"High","price":'+str(highPrice)+',"symbol":"'+urllib.parse.unquote(symbol)+'","date":"'+highDate+'"}')

def get_portfolio(user_id):
    data = firebase_client.get_portfolio(user_id)
    user_data = firebase_client.get_userDetails(user_id)
    result = {}
    result['portfolio'] = {}
    response = {}
    response['portfolio'] = []
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
            item['symbol'] = i['symbol']
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
#    print(gttValues)
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

#        stopLoss = ThreadWithReturnValue( target= get_nWeek_low,args = (i['symbol'],10,))
#        ltp = ThreadWithReturnValue( target= get_stock_status,args = (i['symbol'],))

        stopLoss = get_nWeek_low(i['symbol'],10)
        ltp = get_stock_status(i['symbol'])

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

request_uri = request_uri.split("nseData")[1].split("?")[0]

if request_uri == "/topGainers":
    print(json.dumps(getTopChangers.get_top_gainers(),indent=1))
elif request_uri == "/topLosers":
    print(json.dumps(getTopChangers.get_top_losers(),indent=1))
elif request_uri == "/stockData":
    if 'symbol' in query_params.keys():
        print(json.dumps(get_stock_status(query_params['symbol'][0]),indent=1))
    else:
        print(json.dumps({"error":"symbol is missing"},indent=1))
elif request_uri == "/niftyData":
    print(json.dumps(get_nse_status(),indent=1))
elif request_uri == "/search":
    if 'symbol' in query_params.keys():
        print(json.dumps(search_stock(query_params['symbol'][0]),indent=1))
    else:
        print(json.dumps({"error":"symbol is missing"},indent=1))
elif request_uri == "/indexData":
    if 'index' in query_params.keys():
        print(json.dumps(get_index_stocks(query_params['index'][0]),indent=1))
    else:
        print(json.dumps({"error":"index is missing"},indent=1))
elif request_uri == "/nWeekLow":
  if 'symbol' in query_params.keys() and 'weeks' in query_params.keys():
    print(json.dumps(get_nWeek_low(query_params['symbol'][0],int(query_params['weeks'][0])),indent=1))
  else:
      print(json.dumps({"error":"symbol and/or weeks are missing"},indent=1))
elif request_uri == "/nWeekHigh":
  if 'symbol' in query_params.keys() and 'weeks' in query_params.keys():
    print(json.dumps(get_nWeek_high(query_params['symbol'][0],int(query_params['weeks'][0])),indent=1))
  else:
      print(json.dumps({"error":"symbol and/or weeks are missing"},indent=1))
elif request_uri == "/historicalData":
    if 'symbol' in query_params.keys() and "from" in query_params.keys() and "to" in query_params.keys():
        print(json.dumps(get_historical_data(query_params['symbol'][0],query_params['from'][0],query_params['to'][0]),indent=1))
    else:
        print(json.dumps({"error":"Either symbol or fromDate or toDate is missing"},indent=1))
elif request_uri == "/portfolio":
    if 'user_id' in query_params.keys():
        print(json.dumps(get_portfolio(query_params['user_id'][0]),indent=1))
    else:
        print(json.dumps({"error":"user_id is missing"},indent=1))

#if 'query' in query_params.keys():
#    q = query_params['query'][0]
#    elif q == "indexData":
#        if 'index' in query_params.keys():
#            print(json.dumps(get_index_stocks(query_params['index'][0]),indent=1))
#        else:
#            print(json.dumps({"error":"index is missing"},indent=1))
#    elif q == "nWeekLow":
#      if 'symbol' in query_params.keys() and 'weeks' in query_params.keys():
#        print(json.dumps(get_nWeek_low(query_params['symbol'][0],int(query_params['weeks'][0])),indent=1))
#      else:
#          print(json.dumps({"error":"symbol and/or weeks are missing"},indent=1))
#    elif q == "nWeekHigh":
#      if 'symbol' in query_params.keys() and 'weeks' in query_params.keys():
#        print(json.dumps(get_nWeek_high(query_params['symbol'][0],int(query_params['weeks'][0])),indent=1))
#      else:
#          print(json.dumps({"error":"symbol and/or weeks are missing"},indent=1))
#    elif q == "historicalData":
#        if 'symbol' in query_params.keys() and "from" in query_params.keys() and "to" in query_params.keys():
#            print(json.dumps(get_historical_data(query_params['symbol'][0],query_params['from'][0],query_params['to'][0]),indent=1))
#        else:
#            print(json.dumps({"error":"Either symbol or fromDate or toDate is missing"},indent=1))
#    elif q == "portfolio":
#        if 'user_id' in query_params.keys():
#            print(json.dumps(get_portfolio(query_params['user_id'][0]),indent=1))
#        else:
#            print(json.dumps({"error":"user_id is missing"},indent=1))
