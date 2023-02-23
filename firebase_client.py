#!/usr/bin/python

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db


cred = credentials.Certificate("/usr/share/httpd/sample/fbSA.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://sharemarkettraining-4ed56-default-rtdb.firebaseio.com/'
})
#ref = db.reference('Trades')
#print(ref.get())


def get_portfolio(userId):
    ref = db.reference('Trades/'+userId)
    return ref.get()
