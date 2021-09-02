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

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def ws_key_to_pt_key(pt_pin, ws_key, sign_server, uuid=''):
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
    response = requests.post('http://jd.zack.xin/sign.php', headers=headers, verify=False, data=body)
    if response.status_code == 200:
        url = str(response.text).strip()
        logging.info("body = " + url)
        response = requests.post(url, headers=headers, cookies=cookies, verify=False)
        data = json.loads(response.text)
        if data.get('code') != '0':
            return None
        token = data.get('tokenKey')
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
    pt_pin = os.getenv('pt_pin')
    ws_key = os.getenv('wskey')
    result = ws_key_to_pt_key(pt_pin, ws_key)
    print(result)
