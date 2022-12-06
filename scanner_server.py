#!/opt/rh/rh-python36/root/usr/bin/python


import ssl
import sys
import asyncio
import json
import logging
from quart import Quart,request,Response,session
from queue import Queue
import argparse
import time
import nse_scanner

app_with_storage = Quart("Store")
app_no_storage = Quart("No_Store")
MAXSIZE = 500
q = asyncio.Queue(maxsize=MAXSIZE)
response_q = asyncio.PriorityQueue(maxsize=MAXSIZE)
response_config = []

@app_with_storage.route('/scanner',methods=['GET'])
async def get_scanner():
    data = nse_scanner.get_scanner_data()
    resp = Response(json.dumps(data),status=200)
    return resp

  
if __name__ == '__main__':
    #Disabling HTTPS as it is not supported yet"
    ssl_context = ssl.create_default_context(
        ssl.Purpose.CLIENT_AUTH,
    )
    ssl_context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
    ssl_context.set_ciphers('ECDHE+AESGCM')
    #ssl_context.load_cert_chain(
    #    certfile='/src/domain.crt', keyfile='/src/domain.key',
    #)
    ssl_context.set_alpn_protocols(['h2'])
    #app.run(host='127.0.0.1', port=80, ssl=ssl_context)
#    start_http_server(8000)
#     if 'IPV6_SUPPORT' in os.environ.keys():
#         hostName='::'
#     else:
#         hostName='0.0.0.0'
    if len(sys.argv) > 1:
        if sys.argv[1] == 'store':
            app_with_storage.run(host='0.0.0.0', port=8080)
            sys.exit(1)
    app_no_storage.run(host='0.0.0.0', port=8080)
