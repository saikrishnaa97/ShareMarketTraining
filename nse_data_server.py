from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import json
import cgi
import get_nse_data as g

class Server(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_HEAD(self):
        self._set_headers()

    # GET sends back a Hello world message
    def do_GET(self):
        self._set_headers()
        result = {}
        query_params = {}
        temp = self.path.split("?")
        request_uri = temp[0]
        if len(temp) > 1:
            query_strings = temp[1].split("&")
            for i in query_strings:
                a = i.split("=")
                query_params[a[0]] = a[1]
        print(query_params)

        if request_uri == "/topGainers":
            result = g.getTopChangers.get_top_gainers()
        elif request_uri == "/topLosers":
            result = g.getTopChangers.get_top_losers()
        elif request_uri == "/stockData":
            if 'symbol' in query_params.keys():
                result = g.get_stock_status(query_params['symbol'][0])
            else:
                result = {"error":"symbol is missing"}
        elif request_uri == "/niftyData":
            result = g.get_nse_status()
        elif request_uri == "/search":
            if 'symbol' in query_params.keys():
                result = g.search_stock(query_params['symbol'][0])
            else:
                result = {"error":"symbol is missing"}
        elif request_uri == "/indexData":
            if 'index' in query_params.keys():
                result = g.get_index_stocks(query_params['index'][0])
            else:
                result = {"error":"index is missing"}
        elif request_uri == "/nWeekLow":
          if 'symbol' in query_params.keys() and 'weeks' in query_params.keys():
            result = g.get_nWeek_low(query_params['symbol'][0],int(query_params['weeks'][0]))
          else:
              result = {"error":"symbol and/or weeks are missing"}
        elif request_uri == "/nWeekHigh":
          if 'symbol' in query_params.keys() and 'weeks' in query_params.keys():
            result = g.get_nWeek_high(query_params['symbol'][0],int(query_params['weeks'][0]))
          else:
              result = {"error":"symbol and/or weeks are missing"}
        elif request_uri == "/historicalData":
            if 'symbol' in query_params.keys() and "from" in query_params.keys() and "to" in query_params.keys():
                result = g.get_historical_data(query_params['symbol'][0],query_params['from'][0],query_params['to'][0])
            else:
                result = {"error":"Either symbol or fromDate or toDate is missing"}
        elif request_uri == "/portfolio":
            if 'user_id' in query_params.keys():
                result = g.get_portfolio(query_params['user_id'][0])
            else:
                result = {"error":"user_id is missing"}

        self.wfile.write(bytes(json.dumps(result),'utf-8'))

    # POST echoes the message adding a JSON field
    def do_POST(self):
        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))

        # refuse to receive non-json content
        if ctype != 'application/json':
            self.send_response(400)
            self.end_headers()
            return

        # read the message and convert it into a python dictionary
        length = int(self.headers.getheader('content-length'))
        message = json.loads(self.rfile.read(length))

        # add a property to the object, just to mess with data
        message['received'] = 'ok'

        # send the message back
        self._set_headers()
        self.wfile.write(json.dumps(message))

def run(server_class=HTTPServer, handler_class=Server, port=8008):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)

    print ('Starting httpd on port %d...'+ str(port))
    httpd.serve_forever()

if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
