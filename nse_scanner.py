#!/usr/bin/python

import requests, json
from datetime import date, timedelta

def get_scanner_data():
  print('Content-type: application/json\r\n\r\n') # the mime-type header.
  url = "https://www.nseindia.com/"
  headers = {"user-agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36", "accept-encoding": "gzip, deflate, br","accept-language": "en-GB,en-US;q=0.9,en;q=0.8,la;q=0.7","sec-ch-ua-platform": "Linux", "sec-ch-ua": '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"'}
  conn = requests.Session()
  try:
   response = conn.get(url,headers=headers)
  except Exception as e:
      print(e)
      return e

  cookies = dict(response.cookies)
  response = conn.get(url+"api/equity-stockIndices?index=NIFTY 100",headers=headers,cookies=cookies)
  #response = session.get(url+"api/equity-stockIndices?index=NIFTY TOTAL MARKET",headers=headers,cookies=cookies)
  data = response.json()
  result = {}
  result['data'] = []
  current_date = date.today()
  to = current_date.strftime("%d-%m-%Y")
  from_ = (current_date-timedelta(days=7)).strftime("%d-%m-%Y")
  for i in data['data']:
     symbol = i['symbol']
     yearHigh = i['yearHigh']
     todayHigh = i['dayHigh']
     lastPrice = i['lastPrice']
     name = i['symbol']
     if 'meta' in i.keys():
        name = i['meta']['companyName']
     if(todayHigh >= yearHigh):
       a = {}
       a['symbol'] = symbol
       a['52WkHigh'] = yearHigh
       a['curHigh'] = todayHigh
       a['ltp']  = lastPrice
       a['name'] = name
       result['data'].append(a)
  print(json.dumps(result,indent=1))
  return result


get_scanner_data()