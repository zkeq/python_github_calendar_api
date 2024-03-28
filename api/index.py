# -*- coding: UTF-8 -*-
import requests
import re
from http.server import BaseHTTPRequestHandler, HTTPServer
import json


def list_split(items, n):
    return [items[i:i + n] for i in range(0, len(items), n)]


def getdata(name):
    try:
        gitpage = requests.get("https://github.com/" + name)
        if gitpage.status_code != 200:
            print(f"Failed to get data: {gitpage.status_code} {gitpage.reason} {gitpage.url}")
            return None

        data = gitpage.text
        datadatereg = re.compile(r'data-date="(.*?)"')
        datadate = datadatereg.findall(data)

        datacount = []
        for date in datadate:
            # 匹配 'tool-tip' 标签来提取贡献次数
            datacountreg = re.compile(rf'data-date="{date}"[\s\S]*?<tool-tip.*?>(\d+ contributions|No contributions)')
            count_match = datacountreg.findall(data)
            if count_match:
                # 处理 'No contributions' 的情况
                if 'No contributions' in count_match[0]:
                    datacount.append(0)
                else:
                    # 提取具体的贡献次数
                    num_contributions = re.findall(r'(\d+)', count_match[0])
                    datacount.append(int(num_contributions[0]) if num_contributions else 0)
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
            data = getdata(user[:-1])
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

#
# # 设置服务器的端口号
# port = 8080
#
# # 创建并启动服务器
# httpd = HTTPServer(('localhost', port), handler)
# print(f"Server running on port {port}...")
# httpd.serve_forever()
