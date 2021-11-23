from django.http import HttpResponse
import json
from ShareMarketTraining.rest_client.rest_client import Rest_client
from ShareMarketTraining.FirebaseClient import FirebaseClient
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

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

def getTrades(request, uid):
    return HttpResponse(json.dumps(FirebaseClient().getTradeByUserId(uid)))

def reload(request):
    return HttpResponse(json.dumps(Rest_client().reload()))

def getTopChangers(request):
    return HttpResponse(json.dumps(Rest_client().getTopChangers()))

@csrf_exempt
@require_http_methods(["POST"])
def buyShares(request):
    resp = HttpResponse(FirebaseClient().buyShares(json.loads(request.read())))
    return resp

@csrf_exempt
@require_http_methods(["POST"])
def sellShares(request):
    resp = HttpResponse(FirebaseClient().sellShares(json.loads(request.read())))
    return resp