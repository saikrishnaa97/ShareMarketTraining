from django.http import HttpResponse
import json
from ShareMarketTraining.rest_client.rest_client import Rest_client
from ShareMarketTraining.FirebaseClient import FirebaseClient

def nse(request):
    resp = Rest_client().get_nse_live()
    return HttpResponse(json.dumps(resp))

def bse(request):
    resp = Rest_client().get_bse_live()
    return HttpResponse(json.dumps(resp))

def fullStatus(request):
    resp = Rest_client().get_full_market_status()
    return HttpResponse(json.dumps(resp))

def stockStatus(request, stockName):
    resp = Rest_client().get_stock_status(stockName)
    return HttpResponse(json.dumps(resp))

def searchByName(request, queryString):
    resp = Rest_client().searchByName(queryString)
    return HttpResponse(json.dumps(resp))

def getUsers(request):
    resp = FirebaseClient().getUsers()
    return HttpResponse(json.dumps(resp))

# def getUserByName(request, userName):
#     resp = FirebaseClient().getUserByName(userName)
#     return HttpResponse(json.dumps(resp))

def reload(request):
    return HttpResponse(json.dumps(Rest_client().reload()))

def getTopChangers(request):
    return HttpResponse(json.dumps(Rest_client().getTopChangers()))
