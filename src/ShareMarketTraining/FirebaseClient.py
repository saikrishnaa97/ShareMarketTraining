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

    def getUsers(self):
        return self.user_ref.get()

    def getTradeByUserId(self, uid):
        return self.trade_ref.get().get(uid)

    def updateTrade(self,tradeData):
        try:
            existing = self.trade_ref.child(tradeData['uid'])
            existing.update(tradeData)
            response = {"status":"success"}
        except Exception as e:
            response = {"status":"And Exception occured "+str(e)}
        return response

    def buyShares(self, tradeData,userId):
        try:
            uid = str(uuid.uuid4())
            tradeData['uid'] = uid
            tradeData['soldAt'] = -1
            tradeData["status"] = "HOLDING"
            stockStatus = Rest_client().get_stock_status(tradeData["stockSymbol"])
            if float(stockStatus['NSE']['price_info']['lastPrice']) > float(stockStatus['BSE']['price_info']['LTP']):
                tradeData['purchasedAt'] = float(stockStatus['BSE']['price_info']['LTP'])
            else:
                tradeData['purchasedAt'] = float(stockStatus['NSE']['price_info']['lastPrice'])
            self.trade_ref.child(userId).push({uid:tradeData})
        except Exception as e:
            response = {"status": "And Exception occured " + str(e)}
        return response


