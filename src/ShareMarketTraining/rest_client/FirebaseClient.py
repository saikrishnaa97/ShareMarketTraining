import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import base64, json

class FirebaseClient():
    def __init__(self):
        if not firebase_admin._apps:
            f = open('/opt/ShareMarketTraining/rest_client/fbClientSA.txt')
            dec = f.read()
            f.close()
            f = open('/opt/ShareMarketTraining/rest_client/fbSA.json','a')
            f.write(json.dumps(json.loads(base64.b64decode(dec).decode('utf-8'))))
            f.close()
            cred = credentials.Certificate('/opt/ShareMarketTraining/rest_client/fbSA.json')
            firebase_admin.initialize_app(cred, {'databaseURL': 'https://sharemarkettraining-4ed56-default-rtdb.firebaseio.com/'})
        self.user_ref = db.reference('Users')
        self.trade_ref = db.reference('Trades')

    def getUsers(self):
        return self.user_ref.get()

    # def getUserByName(self, userName):
    #     data = self.ref.get()
    #     response = {}
    #     if data is not None:
    #         for k,v in data.items():
    #             if v['search'] == userName.lower():
    #                 response[k] = v
    #                 break
    #     if response == {}:
    #         response = {"reason" : "Could not find the user"}
    #     return response
