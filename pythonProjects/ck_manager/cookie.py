#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2021/7/30 4:59 下午
# @File    : cookie.py
# @Project : jd_scripts
# @Desc    :
import json
import logging
import os
import time
from urllib.parse import urlencode

import requests
import urllib3
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.DEBUG)
delay_times = 3


def ws_key_to_pt_key(pt_pin, ws_key, sign_server, uuid='xxxxxxxxx-xxxxxxxxx', delay=True):
    """
    ws_key换pt_key
    :return:
    """
    cookies = {
        'pin': pt_pin,
        'wskey': ws_key,
    }
    headers = {
        'user-agent': 'okhttp/3.12.1;jdmall;android;version/10.1.2;build/89743;screen/1080x2293;os/11;network/wifi;',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    }
    body = 'method=url&functionId=genToken&uuid={}'.format(
        uuid) + '&client=android&clientVersion=10.1.1&body={"action":"to",' \
                '"to":"https://home.m.jd.com/userinfom/QueryUserInfoM"}'
    if delay:
        logging.info("sleep delay {}s".format(delay_times))
        time.sleep(delay_times)
    response = requests.post(sign_server, headers=headers, verify=False, data=body)
    if response.status_code == 200:
        url = str(response.text).strip()
        logging.info("body = " + url)
        for i in range(15):
            response = requests.post(url, headers=headers, cookies=cookies, verify=False)
            data = json.loads(response.text)
            logging.info("str data " + str(data))
            if data.get('code') != '0':
                return None
            token = data.get('tokenKey')
            logging.info("tokenkey: " + str(token))
            if token == "xxx" or token == '' or len(token) < 8:
                logging.error("token 错误")
                time.sleep(1)
                continue
            else:
                logging.info("token 获取成功")
                break
        url = data.get('url')
        session = requests.session()
        params = {
            'tokenKey': token,
            'to': 'https://plogin.m.jd.com/jd-mlogin/static/html/appjmp_blank.html'
        }
        url += '?' + urlencode(params)
        session.get(url, allow_redirects=True)
        for k, v in session.cookies.items():
            if k == 'pt_key':
                if str(v).startswith("fake_"):
                    logging.error("fake wskey")
                    return None
                return 'pt_key={};pt_pin={};'.format(v, pt_pin)
        return None
    else:
        logging.error("catch sign response error: " + response.text)
        return None


def sync_check_cookie(cookies):
    """
    检测cookies是否过期
    :param cookies:
    :return:
    """
    try:
        url = 'https://api.m.jd.com/client.action?functionId=newUserInfo&clientVersion=10.0.9&client=android&openudid' \
              '=a27b83d3d1dba1cc&uuid=a27b83d3d1dba1cc&aid=a27b83d3d1dba1cc&area=19_1601_36953_50397&st' \
              '={}&sign=447ffd52c08f0c8cca47ebce71579283&sv=&body='.format(int(time.time() * 1000))

        headers = {
            'user-agent': 'okhttp/3.12.1;jdmall;android;version/10.0.9;build/89099;screen/1080x2293;os/11;network/wifi;'
        }
        response = requests.post(url=url, headers=headers, cookies=cookies, verify=False)
        data = response.json()
        if data['code'] != '0':
            return False
        else:
            return True
    except Exception as e:
        print(e.args)
        return False


if __name__ == '__main__':
    sign_server = os.getenv('server')
    wskey_pin = os.getenv('wskey')
    pt_pin = ''
    ws_key = ''
    for i in str(wskey_pin).split(';'):
        i = i.strip().replace(' ', '')
        if "pin=" in i:
            pt_pin = i.split('pin=')[-1]
        elif "wskey=" in i:
            ws_key = i.split('wskey=')[-1]
        else:
            logging.error("无法识别: " + i)
    logging.info("pt_pin={};wskey={}".format(pt_pin, ws_key))
    assert pt_pin != ''
    assert wskey_pin != ''
    result = ws_key_to_pt_key(pt_pin, ws_key, sign_server)
    print(result)
