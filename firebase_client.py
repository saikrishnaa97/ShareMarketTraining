#!/usr/bin/python

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from datetime import datetime


cred = credentials.Certificate("/usr/share/httpd/sample/fbSA.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://sharemarkettraining-4ed56-default-rtdb.firebaseio.com/'
})
#ref = db.reference('Trades')
#print(ref.get())


def get_portfolio(userId):
    ref = db.reference('Trades/'+userId)
    return ref.get()

def get_userDetails(userId):
    ref = db.reference('Users/'+userId)
    return ref.get()

def update_portfolio(userId,data):
    user_ref = db.reference('Users/'+userId)
    portfolio_ref = db.reference('Trades/'+userId)
    user_data = user_ref.get()
    portfolio_data = portfolio_ref.get()
    user_data['lastUpdatedTimestamp'] = datetime.now().strftime("%s")
    for k,v in portfolio_data.items():
        portfolio_data[k] = data['portfolio'][k]
    portfolio_ref.update(portfolio_data)
    user_ref.update({"lastUpdatedTimestamp":int(datetime.now().strftime("%s"))})
