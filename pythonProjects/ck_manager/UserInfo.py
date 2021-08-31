import datetime
import sys
import logging
import os
from enum import Enum
from datetime import date
import json
import traceback

# 封装UserInfo
# 方便扩展修改维护
import requests


class LoginStatus(Enum):
    # ck 更新过
    NEED_CHECK = 0
    # 上次检查登陆有效
    LAST_LOGINED = 1
    # 上次检查是无效登陆
    INVALID_LOGIN = 2

    @staticmethod
    def is_valid(value):
        for i in LoginStatus.__members__:
            if value == LoginStatus.__getitem__(i).value:
                return True
        return False


class UserInfo:
    def __init__(self, ck=None, **kwargs):
        if ck is None:
            assert kwargs.get('cookie', None) is not None
            self.cookie = kwargs.get('cookie', None)
        else:
            self.cookie = ck
        assert self.cookie is not None
        self.cookie = str(self.cookie).replace(' ', '')
        assert self.cookie != ''
        self.name = kwargs.get('name')
        self.wechart = kwargs.get('wechart')
        self.out_of_time = kwargs.get('out_of_time')
        self.register_time = kwargs.get('register_time')
        if self.register_time is None:
            self.register_time = date.today()
        self.last_login_date = kwargs.get('last_login_date')  # 记录上次查询到登陆成功的日期
        if self.last_login_date is None:
            self.last_login_date = date.today()

        self.priority = kwargs.get('priority')
        if self.priority is None:
            self.priority = 888

        self.vip_level = kwargs.get('vip_level')
        if self.vip_level is None:
            self.vip_level = 888

        self.nick_name = kwargs.get('nick_name')
        self.pushplus_token = kwargs.get('pushplus_token')
        if kwargs.get('login_status') is None:
            self.login_status = LoginStatus.NEED_CHECK.value
        else:
            assert LoginStatus.is_valid(kwargs.get('login_status'))
            self.login_status = kwargs.get('login_status')

    def get_name(self):
        attr = str(sys._getframe().f_code.co_name).replace('get_', '')
        return getattr(self, attr)

    def get_cookie(self):
        attr = str(sys._getframe().f_code.co_name).replace('get_', '')
        return getattr(self, attr)

    def set_cookie(self, value: str):
        value = value.strip().replace(' ', '').replace('\n', '')
        attr = str(sys._getframe().f_code.co_name).replace('set_', '')
        setattr(self, attr, value)

    def get_wechart(self):
        attr = str(sys._getframe().f_code.co_name).replace('get_', '')
        return getattr(self, attr)

    def get_out_of_time(self):
        attr = str(sys._getframe().f_code.co_name).replace('get_', '')
        return getattr(self, attr)

    def get_register_time(self):
        attr = str(sys._getframe().f_code.co_name).replace('get_', '')
        return getattr(self, attr)

    def get_last_login_date(self):
        attr = str(sys._getframe().f_code.co_name).replace('get_', '')
        return getattr(self, attr)

    def get_priority(self):
        attr = str(sys._getframe().f_code.co_name).replace('get_', '')
        return getattr(self, attr)

    def get_vip_level(self):
        attr = str(sys._getframe().f_code.co_name).replace('get_', '')
        return getattr(self, attr)

    def get_pt_pin(self):
        return self.get_cookie().split('pt_pin=')[-1].replace(';', '').replace('"', '').replace('\'', '')

    def to_string(self):
        for attr, value in self.__dict__.items():
            logging.info("{}={}".format(str(attr), str(value)))

    def get_login_status(self):
        attr = str(sys._getframe().f_code.co_name).replace('get_', '')
        return getattr(self, attr)

    def set_login_status(self, value: str):
        assert LoginStatus.is_valid(value)
        attr = str(sys._getframe().f_code.co_name).replace('set_', '')
        setattr(self, attr, value)

    def get_nick_name(self):
        attr = str(sys._getframe().f_code.co_name).replace('get_', '')
        return getattr(self, attr)

    def set_nick_name(self, value: str):
        attr = str(sys._getframe().f_code.co_name).replace('set_', '')
        setattr(self, attr, value)

    def get_pushplus_token(self):
        attr = str(sys._getframe().f_code.co_name).replace('get_', '')
        return getattr(self, attr)

    def set_pushplus_token(self, value: str):
        attr = str(sys._getframe().f_code.co_name).replace('set_', '')
        setattr(self, attr, value)

    def set_priority(self, value: str):
        attr = str(sys._getframe().f_code.co_name).replace('set_', '')
        setattr(self, attr, value)

    def update_last_login_date(self):
        attr = str(sys._getframe().f_code.co_name).replace('update_', '')
        return setattr(self, attr, date.today())

    def is_login(self):
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-cn',
            'Connection': 'keep-alive',
            'Cookie': self.get_cookie(),
            'Referer': "https://home.m.jd.com/myJd/newhome.action",
            'User-Agent': "jdapp;iPhone;10.0.2;14.3;network/wifi;Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
            'Host': 'wq.jd.com',
        }
        response = requests.get(
            'https://wq.jd.com/user_new/info/GetJDUserInfoUnion?orgFlag=JD_PinGou_New&callSource=mainorder',
            headers=headers)
        if response.status_code != 200:
            logging.error("GetJDUserInfoUnion failed, switch to new API me-api.jd.com")
            headers = {
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'zh-cn',
                'Connection': 'keep-alive',
                'Cookie': self.get_cookie(),
                'Referer': "hhttps://home.m.jd.com/myJd/newhome.action?sceneval=2&ufc=&",
                'User-Agent': "jdapp;iPhone;10.0.2;14.3;network/wifi;Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
                'Host': 'me-api.jd.com',
            }
            response = requests.get('https://me-api.jd.com/user_new/info/GetJDUserInfoUnion', headers=headers)
        try:
            response = response.json()
        except json.JSONDecodeError as err:
            logging.error(traceback.format_exc())
            logging.error("decode jason failed: error: {} ck:{} response code:{} response.txt:{}".format(str(err),
                                                                                                         self.get_cookie(),
                                                                                                         response,
                                                                                                         response.text))
            return False
        # print(response)
        if response.get('retcode') == 0 or response.get('retcode') == '0':
            user_name = response['data']['userInfo']['baseInfo']['nickname']
            curPin = response['data']['userInfo']['baseInfo']['curPin']
            logging.info("{} {} 登陆成功".format(self.get_cookie(), user_name))
            logging.info("curPin={}".format(curPin))
            self.set_nick_name(user_name)
            return True
        elif response.get('retcode') == 13 or response.get('retcode') == '13':
            logging.info("{} 登陆失效".format(self.get_cookie()))
            return False
        elif response.get('retcode') == 1001 or response.get('retcode') == '1001':
            logging.info("{} 登陆失效".format(self.get_cookie()))
            return False
        else:
            logging.error("Error: {} {}".format(self.get_cookie(), response))
            return False

    def is_expired(self):
        out_of_date = datetime.datetime.strptime(str(self.get_register_time()), '%Y-%m-%d')
        current_date = datetime.datetime.strptime(str(date.today()), '%Y-%m-%d')
        return {
            "is_expired": (current_date - out_of_date).days < 0,
            "remaining_days": (current_date - out_of_date).days
        }

    def get_last_login_date_expired_days(self) -> int:
        last_login_day = datetime.datetime.strptime(str(self.get_last_login_date()), '%Y-%m-%d')
        current_date = datetime.datetime.strptime(str(date.today()), '%Y-%m-%d')
        return (current_date - last_login_day).days

    def get_user_dict(self):
        result_ck = {'name': self.get_name(),
                     'nick_name': self.get_nick_name(),
                     'priority': self.get_priority(),
                     'vip_level': self.get_vip_level(),
                     'wechart': self.get_wechart(),
                     'out_of_time': self.get_out_of_time(),
                     'register_time': self.get_register_time(),
                     'login_status': self.get_login_status(),
                     'last_login_date': self.get_last_login_date(),
                     'cookie': self.get_cookie(),
                     'pushplus_token': self.get_pushplus_token()
                     }
        return result_ck

    def format_ck(self):
        if self.cookie != None and self.cookie != '' and len(str(self.cookie)) > 0:
            ck = self.cookie.strip().replace(' ', '').replace('\n', '')
            if not ck.endswith(';'):
                ck = ck + ';'
            self.cookie = ck
        return self

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                        level=logging.DEBUG)
    ck = os.getenv('cookie')
    if ck is None:
        ck = 1
    userInfo = UserInfo(ck, name='name', wechart='3', out_of_time=date.today(), priority=1)
    assert userInfo.get_cookie() == str(ck), userInfo.get_cookie()
    assert userInfo.get_name() == 'name', userInfo.get_name()
    assert userInfo.get_wechart() == '3', userInfo.wechart()
    assert userInfo.get_out_of_time() == date.today(), userInfo.out_of_time()
    assert userInfo.get_priority() == 1, userInfo.priority()
    a = datetime.datetime.strptime(str(userInfo.get_register_time()), '%Y-%m-%d')
    b = datetime.datetime.strptime(str(date.today()), '%Y-%m-%d')
    assert (b - a).days == 0
    print(userInfo.is_login())
