import requests, json
from datetime import date, timedelta

url = "https://www.nseindia.com/"
headers = {"user-agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36", "accept-encoding": "gzip, deflate, br","accept-language": "en-GB,en-US;q=0.9,en;q=0.8,la;q=0.7","sec-ch-ua-platform": "Linux", "sec-ch-ua": '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"'}
session = requests.Session()
response = session.get(url,headers=headers)
cookies = dict(response.cookies)

response = session.get(url+"api/equity-stockIndices?index=NIFTY 100",headers=headers,cookies=cookies)
#response = session.get(url+"api/equity-stockIndices?index=NIFTY TOTAL MARKET",headers=headers,cookies=cookies)
data = response.json()

current_date = date.today()
to = current_date.strftime("%d-%m-%Y")
from_ = current_date.replace(day = current_date.day-7).strftime("%d-%m-%Y")
for i in data['data']:
   symbol = i['symbol']
   yearHigh = i['yearHigh']
   todayHigh = i['dayHigh']
   lastPrice = i['lastPrice']
   name = i['symbol']
   if 'meta' in i.keys(): 
      name = i['meta']['companyName']
   if(todayHigh >= yearHigh):
     print("^^^^^^^^^^^^^^^^^^^^^^^^^^^")
     print("vvvvvvvvvvvvvvvvvvvvvvvvvvv")
     print("Name: "+name)
     print("52Wk High:- "+str(yearHigh))
     print("Current High:- "+str(todayHigh))
#     print(symbol+"-"+str(yearHigh)+"-"+str(todayHigh)+"-"+str(lastPrice)+"-"+name)
     weekUrl = f"https://www.nseindia.com/api/historical/cm/equity?symbol={symbol}&series=[%22EQ%22]&from={from_}&to={to}"
     response = session.get(weekUrl,headers=headers, cookies=cookies)
     weekData = response.json()
#     print(response.content)
     for j in weekData['data']:
         print("Date:-"+j['mTIMESTAMP'])
         print("Closing Price:- "+str(j["CH_LAST_TRADED_PRICE"]))
          



