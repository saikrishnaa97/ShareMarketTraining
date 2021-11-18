import json, requests
import datetime
from ShareMarketTraining.StockService import StockService
import html_to_json as h2j
import os
import threading

class Rest_client():

    def __init__(self):
        self.stockStatusService = StockService()

        self.headers = {'Accept': '*/*', 'Accept-Language': 'en-US,en;q=0.5',
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36 Edg/95.0.1020.40',
                            'X-Requested-With': 'XMLHttpRequest', 'cache-control' : 'max-age=0'}
        self.nse_index_url = "https://www1.nseindia.com/homepage/Indices1.json"
        self.bse_index_url = "https://api.bseindia.com/RealTimeBseIndiaAPI/api/GetSensexData/w"

        self.bse_scrip_url = "https://api.bseindia.com/Msource/1D/getQouteSearch.aspx?Type=EQ&flag=nw&text="
        self.nse_stock_url = "https://www.nseindia.com/api/quote-equity?symbol="
        #self.nse_stock_url = "https://www1.nseindia.com/live_market/dynaContent/live_watch/get_quote/getPEDetails.jsp?symbol="
        self.bse_stock_url = "https://api.bseindia.com/BseIndiaAPI/api/getScripHeaderData/w?Debtflag=&seriesid=&scripcode="
        self.top_gainers_url = "https://api.bseindia.com/BseIndiaAPI/api/HoTurnover/w?flag=G"
        self.top_losers_url = "https://api.bseindia.com/BseIndiaAPI/api/HoTurnover/w?flag=L"
        self.NIFTY_INDEX_NAME = "NIFTY 50"
        self.topChanges = {}

    def get_nse_live(self):
        self.headers['Host'] = 'www1.nseindia.com'
        response = requests.get(self.nse_index_url, headers=self.headers, timeout=5)
        if response.status_code == 200:
            for i in json.loads(response.content)['data']:
                if i['name'] == self.NIFTY_INDEX_NAME:
                    response_data = i
                    response_data.pop('imgFileName')
        else:
            response_data = {"reason": "Could not fetch nse_data"}
        return response_data

    def get_bse_live(self):
        self.headers['Host'] = 'api.bseindia.com'
        response = requests.get(self.bse_index_url, timeout=5, headers=self.headers)
        if response.status_code == 200:
            response_data = json.loads(response.content)[0]
        else:
            response_data = {"reason": "Could not fetch bse_data"}
        return response_data

    def get_full_market_status(self):
        nse_resp = self.get_nse_live()
        bse_resp = self.get_bse_live()
        response = {"NSE NIFTY 50" : str(nse_resp['lastPrice']), "BSE SENSEX" : str(bse_resp['ltp'])}
        return response

    def get_nse_stock_status(self,stockName):
        self.headers['Host'] = 'www.nseindia.com'
        cookie = self.get_nse_cookie(stockName)
        url = self.nse_stock_url+stockName
        response = requests.get(url, timeout=5, headers=self.headers, cookies= cookie)
        if response.status_code == 200:
            response_data = json.loads(response.content)
        else:
            response_data = {"reason": "Could not fetch nse_data"}
            print(response.content)
        return response_data

    def get_bse_stock_status(self,stockName):
        self.headers['Host'] = 'api.bseindia.com'
        try:
            scrip_id = self.stockStatusService.scrip_ids[str(stockName)]
        except Exception as e:
            response_data = {"reason": "invalid stock name "+str(e)}
            return response_data
        response = requests.get(self.bse_stock_url+scrip_id, timeout=5, headers=self.headers)
        if response.status_code == 200:
            resp_data = response.content
            response_data = json.loads(resp_data)
        else:
            response_data = {"reason": "Could not fetch bse_data"}
        return response_data


    def get_stock_status(self,stockName):
        nse_stock_data = self.get_nse_stock_status(stockName)
        bse_stock_data = self.get_bse_stock_status(stockName)

        if "data" not in nse_stock_data.keys():
            nse_response = self.stockStatusService.nseResponseGenerator(nse_stock_data)
        else:
            nse_response = nse_stock_data

        if "reason" not in bse_stock_data.keys():
            bse_response = self.stockStatusService.bseResponseGenerator(bse_stock_data)
            bse_response['symbol'] = stockName
        else:
            bse_response = bse_stock_data

        response = {"NSE" : nse_response, "BSE": bse_response, "Symbol" : stockName}
        return response

    def get_nse_cookie(self,stockName):
        self.headers['Host'] = 'www.nseindia.com'
        self.headers['Accept'] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
        url = "https://www.nseindia.com"
        date_cookie = (datetime.datetime.now() + + datetime.timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")
        cookie = {
            "RT": "Value=z=1&dm=nseindia.com&si=cc7f1048-5a4e-4714-8bf7-2a7019d0fec7&ss=kvb2kwrk&sl=1&tt=26w&bcn=%2F%2F684d0d40.akstat.io%2F&ld=4dw&ul=bxq; domain=.nseindia.com; path=/; Expires=" + date_cookie + ";"}
        s = requests.Session()
        response = s.get(url, timeout=5, headers=self.headers, cookies=cookie)
        return response.cookies

    def reload(self):
        try:
            os.system("sh /opt/ShareMarketTraining/rest_client/reload.sh")
            return {"status":"Success"}
        except Exception as e:
            return {"reason":str(e)}
    
    def searchByName(self,queryString):
        self.headers['Host'] = 'api.bseindia.com'
        response = requests.get(self.bse_scrip_url+queryString, timeout=5, headers=self.headers)
        response_data = {}
        if response.status_code == 200:
            json_data = h2j.convert(response.content)
            response_data['results'] = []
            for i in json_data['li']:
               if "_value" in i['a'][0].keys() and not i['a'][0]['_value'] == "No Match Found":
                   response_item = {}
                   response_item['name'] = (i['a'][0]['_attributes']['id'].split('/')[-4]).upper().replace('-',' ')
                   response_item['symbol'] = (i['a'][0]['_attributes']['id'].split('/')[-3]).upper()
                   response_item['scrip_id'] = i['a'][0]['_attributes']['id'].split('/')[-2]
                   response_data['results'].append(response_item)
               elif "strong" in i['a'][0].keys():
                   response_item = {}
                   response_item['name'] = (i['a'][0]['_attributes']['id'].split('/')[-4]).upper().replace('-',' ')
                   response_item['symbol'] = (i['a'][0]['_attributes']['id'].split('/')[-3]).upper()
                   response_item['scrip_id'] = i['a'][0]['_attributes']['id'].split('/')[-2]
                   response_data['results'].append(response_item)
               else:
                response_data = {"reason": "No matching share found"}
                return response_data
        else:
            response_data = {"reason": "Could not fetch bse_data"}
        return response_data
    
    def getTopGainers(self):
        self.headers['Host'] = 'api.bseindia.com'
        response = requests.get(self.top_gainers_url, timeout=5, headers=self.headers)
        response_data = []
        if response.status_code == 200:
            json_data = h2j.convert(response.content)
            for i in json_data["Table"]:
                temp = {}
                temp["symbol"] = i["ScripName"]
                temp["ltp"] = i["Ltradert"]
                temp["Name"] = i["LONGNAME"]
                temp["scripId"] = i["scrip_cd"]
                temp["changeValue"] = i["change_val"]
                temp["changePercent"] = i["change_percent"]
                response_data.append(temp)
        else:
            response_data = {"reason": "Could not fetch top gainers"}
        self.top_changes["gainers"] = response_data
    
     def getTopLosers(self):
        self.headers['Host'] = 'api.bseindia.com'
        response = requests.get(self.top_losers_url, timeout=5, headers=self.headers)
        response_data = []
        if response.status_code == 200:
            json_data = h2j.convert(response.content)
            for i in json_data["Table"]:
                temp = {}
                temp["symbol"] = i["ScripName"]
                temp["ltp"] = i["Ltradert"]
                temp["Name"] = i["LONGNAME"]
                temp["scripId"] = i["scrip_cd"]
                temp["changeValue"] = i["change_val"]
                temp["changePercent"] = i["change_percent"]
                response_data.append(temp)
        else:
            response_data = {"reason": "Could not fetch top losers"}
        self.top_changes["losers"] = response_data
    
    def getTopChangers(self):
        t1 = threading.Thread(target=getTopLosers)
        t2 = threading.Thread(target=getTopGainers)
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        return self.top_changes
        
        
        
