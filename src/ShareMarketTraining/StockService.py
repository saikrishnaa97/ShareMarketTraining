
import os, json

class StockService():
    
    def __init__(self):
        if not os.path.isfile('/opt/ShareMarketTraining/rest_client/SCRIP.json'):
            self.scrip_ids = {}
            try:
                with open('/opt/ShareMarketTraining/rest_client/SCRIP.TXT') as file:
                    lines = file.read().split('\n')
                    for i in lines:
                        stockData = i.split('|')
                        self.scrip_ids[stockData[2]] = stockData[0]
                file.close()

                with open('/opt/ShareMarketTraining/rest_client/SCRIP.json', 'a+') as file:
                    file.write(str(self.scrip_ids))
                file.close()
            except Exception as e:
                print(e)
        else:
            with open('/opt/ShareMarketTraining/rest_client/SCRIP.json') as file:
                json_data = file.read().replace("'",'"')
                self.scrip_ids = json.loads(json_data)
                print(type(self.scrip_ids))
            file.close()
    
    def nseResponseGenerator(self, nse_data):
        response = {}

        response['name'] = nse_data['info']['companyName']
        response['symbol'] = nse_data['info']['symbol']
        response['price_info'] = nse_data['priceInfo']

        return response
    
    def bseResponseGenerator(self, bse_data):
        response = {}

        response['name'] = bse_data['Cmpname']['FullN']
        response['price_info'] = bse_data['CurrRate']

        return response
