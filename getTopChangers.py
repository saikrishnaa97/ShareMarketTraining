#!/usr/bin/python

import requests
from html.parser import HTMLParser
import json


class Parser(HTMLParser):
  # method to append the start tag to the list start_tags.
  def handle_starttag(self, tag, attrs):
    global start_tags
    start_tags.append(tag)
    # method to append the end tag to the list end_tags.
  def handle_endtag(self, tag):
    global end_tags
    end_tags.append(tag)
  # method to append the data between the tags to the list all_data.
  def handle_data(self, data):
    global all_data
    all_data.append(data)
  # method to append the comment to the list comments.
  def handle_comment(self, data):
    global comments
    comments.append(data)
start_tags = []
end_tags = []
all_data = []
comments = []

def get_data():
    conn = requests.Session()
    headers = {'Accept': '*/*', 'Accept-Language': 'en-US,en;q=0.9', 'Cache-Control': 'max-age=0', 'Connection': 'keep-alive', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.41', 'Upgrade-Insecure-Requests': '1', 'Sec-Fetch-Site': 'none', 'Sec-Fetch-Dest': 'document', 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-User': '?1', 'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Microsoft Edge";v="110"', 'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Windows"'}
    resp = conn.request('GET','https://www.nseindia.com',headers=headers)
    data = resp.content
    parser = Parser()
    parser.feed(str(data))
    result = ""
    for i in all_data:
      if 'topGainers' in i:
        result = i.split('window.headerData = ')[1]
        result = result.split('\\n      var checkDownloadFile')[0]
    jsonData = json.loads(result)
    return jsonData

def get_top_gainers():
    jsonData = get_data()
    return jsonData['indexDataInfo'][0]['topGainers']

def get_top_losers():
    jsonData = get_data()
    return jsonData['indexDataInfo'][0]['topLosers']
