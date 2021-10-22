import datetime
import sys
import logging
import os
from enum import Enum
from datetime import date
import json
import traceback
from cookie import ws_key_to_pt_key

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
    # ck 和 appkey 没有配置，一律返回None type
    def __init__(self, ck=None, sign_server=None, **kwargs):
        if ck is None:
            self.cookie = kwargs.get('cookie', None)
            if self.cookie is not None:
                self.cookie = str(self.cookie).replace(' ', '').replace('；', '')
        else:
            self.cookie = str(ck).replace(' ', '').replace('；', '')

        self.appkey = kwargs.get('appkey', None)
        if self.appkey is not None:
            self.appkey = str(self.appkey).replace(' ', '').replace('；', '')

        # todo move to global config
        self.sign_server = sign_server

        self.name = kwargs.get('name')
        self.uuid = kwargs.get('uuid', '')
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
        if self.pushplus_token is not None:
            self.pushplus_token = str(self.pushplus_token).strip().replace('\'', '').replace(' ', '')
        if kwargs.get('login_status') is None:
            self.login_status = LoginStatus.NEED_CHECK.value
        else:
            assert LoginStatus.is_valid(kwargs.get('login_status'))
            self.login_status = kwargs.get('login_status')

    def has_config_key(self) -> bool:
        if self.cookie == '' and self.appkey == '':
            return False
        else:
            return True

    def get_name(self):
        attr = str(sys._getframe().f_code.co_name).replace('get_', '')
        return getattr(self, attr)

    def get_uuid(self):
        attr = str(sys._getframe().f_code.co_name).replace('get_', '')
        return getattr(self, attr)

    def get_cookie(self):
        attr = str(sys._getframe().f_code.co_name).replace('get_', '')
        return getattr(self, attr)

    def get_appkey(self):
        attr = str(sys._getframe().f_code.co_name).replace('get_', '')
        return getattr(self, attr)

    def set_cookie(self, value: str):
        value = value.strip().replace(' ', '').replace('\n', '')
        attr = str(sys._getframe().f_code.co_name).replace('set_', '')
        setattr(self, attr, value)

    def set_appkey(self, value: str):
        value = value.strip().replace(' ', '').replace('\n', '')
        attr = str(sys._getframe().f_code.co_name).replace('set_', '')
        setattr(self, attr, value)

    def get_wechart(self):
        attr = str(sys._getframe().f_code.co_name).replace('get_', '')
        return getattr(self, attr)

    def set_wechart(self, value: str):
        value = value.strip().replace(' ', '').replace('\n', '')
        attr = str(sys._getframe().f_code.co_name).replace('set_', '')
        setattr(self, attr, value)

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
        result_pin = None
        if self.get_appkey() is not None:
            for key in str(self.get_appkey()).split(';'):
                key = key.strip().replace(' ', '')
                if 'pin=' in key:
                    result_pin = key.split('pin=')[-1].replace(';', '').replace('"', '').replace('\'', '')
        elif self.get_cookie() is not None:
            for key in str(self.get_cookie()).split(';'):
                key = key.strip().replace(' ', '')
                if 'pt_pin=' in key:
                    result_pin = key.split('pt_pin=')[-1].replace(';', '').replace('"', '').replace('\'',
                                                                                                    '')
        if result_pin is None:
            logging.error("no pt_pin")
            return "no_config_pt_pin"
        return result_pin

    def get_wskey(self):
        if self.get_appkey() is not None:
            return self.get_appkey().split('wskey=')[-1].replace(';', '').replace('"', '').replace('\'', '')
        else:
            return None

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

    def set_uuid(self, value: str):
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
                     'appkey': self.get_appkey(),
                     'pushplus_token': self.get_pushplus_token(),
                     'uuid': self.get_uuid()
                     }
        return result_ck

    def format_ck(self):
        if self.cookie != None and self.cookie != '' and len(str(self.cookie)) > 0:
            ck = self.cookie.strip().replace(' ', '').replace('\n', '')
            if not ck.endswith(';'):
                ck = ck + ';'
            self.cookie = ck
        return self

    def update_ck_from_user(self, new_user):
        if new_user.get_appkey() != None and new_user.get_appkey() != '':
            self.set_appkey(new_user.get_appkey())
        if new_user.get_pushplus_token() != None and new_user.get_pushplus_token() != '':
            self.set_pushplus_token(new_user.get_pushplus_token())
        if new_user.get_cookie() != None and new_user.get_cookie() != '':
            self.set_cookie(new_user.get_cookie())
        if new_user.get_wechart() != None and new_user.get_wechart() != '':
            self.set_wechart(new_user.get_wechart())

    def update_ws_key_to_pt_key(self, delay=True):
        if self.get_appkey() is not None:
            appkey = ws_key_to_pt_key(self.get_pt_pin(), self.get_wskey(), sign_server=self.sign_server,
                                      uuid=self.get_uuid(), delay=delay)
            if appkey is not None:
                self.set_cookie(appkey)
                return True
            else:
                logging.error('ws_key 可能已失效')
                return False


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
    user = UserInfo()
    assert user.get_cookie() is None
    assert user.get_wskey() is None
