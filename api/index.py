# -*- coding: UTF-8 -*-
import requests
import re
from http.server import BaseHTTPRequestHandler
import json

def list_split(items, n):
    return [items[i:i + n] for i in range(0, len(items), n)]

def getdata(name):
    try:
        gitpage = requests.get("https://github.com/" + name)
        data = gitpage.text
        # 更新的正则表达式
        datadatereg = re.compile(r'data-date="(.*?)"')
        datadate = datadatereg.findall(data)

        datacount = []
        for date in datadate:
            datacountreg = re.compile(rf'data-date="{date}".*?>(\d+) contributions')
            count = datacountreg.findall(data)
            if count:
                datacount.append(int(count[0]))
            else:
                datacount.append(0)

        contributions = sum(datacount)
        datalist = []
        for index, item in enumerate(datadate):
            itemlist = {"date": item, "count": datacount[index]}
            datalist.append(itemlist)

        datalistsplit = list_split(datalist, 7)
        returndata = {
            "total": contributions,
            "contributions": datalistsplit
        }
        return returndata
    except requests.RequestException as e:
        print(f"Network error: {e}")
        return None
    except Exception as e:
        print(f"Error processing data: {e}")
        return None

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            path = self.path
            user = path.split('?')[1]
            data = getdata(user)
            if data:
                self.send_response(200)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(data).encode('utf-8'))
            else:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b'Error processing data')
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Server error: {e}".encode('utf-8'))

        return
