import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from . import KubernetesClient
from ShareMarketTraining.rest_client.rest_client import Rest_client
import uuid

class FirebaseClient():
    def __init__(self):
        if not firebase_admin._apps:
            KubernetesClient.KubernetesClient().getFirebaseSA()
            cred = credentials.Certificate('/opt/ShareMarketTraining/rest_client/fbSA.json')
            firebase_admin.initialize_app(cred, {'databaseURL': 'https://sharemarkettraining-4ed56-default-rtdb.firebaseio.com/'})
        self.user_ref = db.reference('Users')
        self.trade_ref = db.reference('Trades')
        self.indices_ref = db.reference('Indices')

    def getUsers(self):
        return self.user_ref.get()

    def getTradeByUserId(self, uid):
        response = {}
        trades = self.trade_ref.get().get(uid)
        response['tradedValue'] = 0.00
        response['availableBalance'] = 300000.00
        for i in trades.keys():
            if trades[i]['status'] == "HOLDING":
                stockStatus = Rest_client().get_stock_status(trades[i]['stockSymbol'])
                if trades[i]['exchange'] == "BSE":
                    trades[i]['currentPrice'] = float(stockStatus['BSE']['price_info']['LTP'])
                elif trades[i]['exchange'] == "NSE":
                    trades[i]['currentPrice'] = float(stockStatus['NSE']['price_info']['lastPrice'])
                trades[i]['P/L'] = (trades[i]['currentPrice'] - trades[i]['purchasedAt']) * trades[i]['numOfShares']
                response['tradedValue'] = response['tradedValue'] + (trades[i]['purchasedAt'] * trades[i]['numOfShares'])
            else:
                trades[i]['P/L'] = (trades[i]['soldAt']-trades[i]['purchasedAt'])*trades[i]['numOfShares']
                response['availableBalance'] = response['availableBalance'] + ((trades[i]['soldAt']-trades[i]['purchasedAt'])*trades[i]['numOfShares'])
        response['trades'] = trades
        response['availableBalance'] = response['availableBalance'] - response['tradedValue']
        self.user_ref.child(uid).update({'availableBalance':response['availableBalance']})
        return response

    def updateTrade(self,tradeData):
        try:
            existing = self.trade_ref.child(tradeData['uid'])
            existing.update(tradeData)
            response = {"status":"success"}
        except Exception as e:
            response = {"status":"And Exception occurred "+str(e)}
        return response

    def buyShares(self, tradeData):
        try:
            userId = tradeData['userId']
            tradeData.pop('userId')
            uid = str(uuid.uuid4())
            tradeData['uid'] = uid
            tradeData['soldAt'] = -1
            tradeData["status"] = "HOLDING"
            stockStatus = Rest_client().get_stock_status(tradeData["stockSymbol"])
            if trades[i]['exchange'] == "BSE":
                tradeData['purchasedAt'] = float(stockStatus['BSE']['price_info']['LTP'])
            elif trades[i]['exchange'] == "NSE":
                tradeData['purchasedAt'] = float(stockStatus['NSE']['price_info']['lastPrice'])
            userData = self.user_ref.child(userId).get()
            totalAmount = tradeData['purchasedAt']*tradeData['numOfShares']
            if float(userData['availableBalance']) < float(totalAmount):
                response = {"error":"Not enough balance available to buy shares"}
                return response
            else:
                userData['availableBalance'] = float(userData['availableBalance'] - totalAmount)
                self.user_ref.child(userId).update(userData)
            self.trade_ref.child(userId).child(uid).update(tradeData)
            response = tradeData
            response["status"]="Successfully bought"
        except Exception as e:
            response = {"status": "Exception occurred " + str(e)}
        return response

    def sellShares(self, tradeData):
        try:
            userId = tradeData['userId']
            tradeData.pop('userId')
            tradeData["status"] = "SOLD"
            stockStatus = Rest_client().get_stock_status(tradeData["stockSymbol"])
            curTrade = self.trade_ref.child(userId).child(tradeData['uid']).get()
            if curTrade['status'] == "SOLD":
                response = {"error": "These shares are already sold"}
                return response
            if curTrade['numOfShares'] > tradeData['numOfShares']:
                curTrade['numOfShares'] = curTrade['numOfShares'] - tradeData['numOfShares']
                self.trade_ref.child(userId).child(tradeData['uid']).update(curTrade)
                tradeData['uid'] = str(uuid.uuid4())
                tradeData['purchasedAt'] = curTrade['purchasedAt']
            elif curTrade['numOfShares'] < tradeData['numOfShares']:
                response = {"error": "Only "+str(curTrade['numOfShares'])+" shares left to sell"}
                return response
            if trades[i]['exchange'] == "BSE":
                tradeData['soldAt'] = float(stockStatus['BSE']['price_info']['LTP'])
            elif trades[i]['exchange'] == "NSE":
                tradeData['soldAt'] = float(stockStatus['NSE']['price_info']['lastPrice'])
            self.trade_ref.child(userId).child(tradeData['uid']).update(tradeData)
            userData = self.user_ref.child(userId).get()
            totalAmount = tradeData['soldAt'] * tradeData['numOfShares']
            userData['availableBalance'] = float(userData['availableBalance'] + totalAmount)
            self.user_ref.child(userId).update(userData)
            response = tradeData
            response["status"]="Successfully sold"
        except Exception as e:
            response = {"status": "Exception occurred " + str(e)}
        return response

    def updateIndices(self):
        liveIndices = Rest_client().get_full_market_status()
        bse = liveIndices['BSE']['ltp']
        nse = liveIndices['NSE']['lastPrice']
        try:
            self.indices_ref.update({'NIFTY 50':nse, "SENSEX":bse})
            response = {"status":"Success"}
        except Exception as e:
            response = {"status": "Exception occurred " + str(e)}
        return response