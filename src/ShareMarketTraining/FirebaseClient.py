import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import KubernetesClient

class FirebaseClient():
    def __init__(self):
        if not firebase_admin._apps:
            KubernetesClient().getFirebaseSA()
            cred = credentials.Certificate('/opt/ShareMarketTraining/rest_client/fbSA.json')
            firebase_admin.initialize_app(cred, {'databaseURL': 'https://sharemarkettraining-4ed56-default-rtdb.firebaseio.com/'})
        self.user_ref = db.reference('Users')
        self.trade_ref = db.reference('Trades')

    def getUsers(self):
        return self.user_ref.get()

    def getTradeByUserId(self, uid):
        return self.trade_ref.get().get(uid)
