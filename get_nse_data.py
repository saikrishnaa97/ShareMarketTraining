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

def get_top_gainers():
    current_url = nse1_url + "live_market/dynaContent/live_analysis/gainers/niftyGainers1.json"
    cookies = get_cookie(nse1_url)
    conn = requests.Session()
    response = conn.get(current_url,headers=headers,cookies=cookies)
    data = response.json()
    result = {}
    result['data'] = []
    conn.close()
    for i in data['data']:
        temp = {}
        temp['symbol'] = i['symbol']
        temp['ltp'] = i['ltp']
        temp['highPrice'] = i['highPrice']
        temp['lowPrice'] = i['lowPrice']
        result['data'].append(temp)
    return result

def get_top_losers():
    current_url = nse1_url + "live_market/dynaContent/live_analysis/losers/niftyLosers1.json"
    cookies = get_cookie(nse1_url)
    conn = requests.Session()
    response = conn.get(current_url,headers=headers,cookies=cookies)
    data = response.json()
    result = {}
    result['data'] = []
    conn.close()
    for i in data['data']:
        temp = {}
        temp['symbol'] = i['symbol']
        temp['ltp'] = i['ltp']
        temp['highPrice'] = i['highPrice']
        temp['lowPrice'] = i['lowPrice']
        result['data'].append(temp)
    return result

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
  return '{"numberOfWeeks":'+str(weeks)+',"type":"High","price":'+str(highPrice)+',"symbol":"'+urllib.parse.unquote(symbol)+'","date":"'+highDate+'"}'

def get_portfolio(user_id):
    data = firebase_client.get_portfolio(user_id)
    result = {}
    result['portfolio'] = []
    stocksList = []
    for k,i in data.items():
        item = {}
        item['symbol'] = i['stockSymbol']
        item['avgCost'] = i['purchasedAt']
        item['uid'] = i['uid']
        stocksList.append(item)
    gttValues = {}
    numOfThreads = math.ceil(len(stocksList)/4)
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
#    print(gttValues)
    for k,i in data.items():
        trade = {}
        trade['symbol'] = i['stockSymbol']
        trade['ltp'] = gttValues[i['uid']]['ltp']
        trade['stopLoss'] = gttValues[i['uid']]['stopLoss']
        trade['target'] = gttValues[i['uid']]['target']
        trade['numOfShares'] = i['numOfShares']
        trade['avgCost'] = i['purchasedAt']
        trade['uid'] = i['uid']
        result['portfolio'].append(trade)
    return(result)

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
        result[i['uid']]['stopLoss'] = get_nWeek_low(i['symbol'],10)['price']
        result[i['uid']]['target'] = i['avgCost'] * 1.6
        result[i['uid']]['ltp'] = get_stock_status(i['symbol'])['ltp']
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
if 'query' in query_params.keys():
    q = query_params['query'][0]
    if q == "topGainers":
        print(getTopChangers.get_top_gainers())
    elif q == "topLosers":
        print(getTopChangers.get_top_losers())
    elif q == "stockData":
        if 'symbol' in query_params.keys():
            print(get_stock_status(query_params['symbol'][0]))
        else:
            print('{"error":"symbol is missing"}')
    elif q == "niftyData":
        print(get_nse_status())
    elif q == "search":
        if 'symbol' in query_params.keys():
            print(search_stock(query_params['symbol'][0]))
        else:
            print('{"error":"symbol is missing"}')
    elif q == "indexData":
        if 'index' in query_params.keys():
            print(get_index_stocks(query_params['index'][0]))
        else:
            print('{"error":"index is missing"}')
    elif q == "nWeekLow":
      if 'symbol' in query_params.keys() and 'weeks' in query_params.keys():
        print(get_nWeek_low(query_params['symbol'][0],int(query_params['weeks'][0])))
      else:
          print('{"error":"symbol and/or weeks are missing"}')
    elif q == "nWeekHigh":
      if 'symbol' in query_params.keys() and 'weeks' in query_params.keys():
        print(get_nWeek_high(query_params['symbol'][0],int(query_params['weeks'][0])))
      else:
          print('{"error":"symbol and/or weeks are missing"}')
    elif q == "historicalData":
        if 'symbol' in query_params.keys() and "from" in query_params.keys() and "to" in query_params.keys():
            print(get_historical_data(query_params['symbol'][0],query_params['from'][0],query_params['to'][0]))
        else:
            print('{"error":"Either symbol or fromDate or toDate is missing"}')
    elif q == "portfolio":
        if 'user_id' in query_params.keys():
            print(get_portfolio(query_params['user_id'][0]))
        else:
            print('{"error":"user_id is missing"}')
