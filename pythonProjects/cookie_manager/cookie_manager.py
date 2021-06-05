import os
import logging
import yaml
from datetime import datetime
import time
from sendNotify import sendNotify
import socket
logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.DEBUG)

FORCE_BROADCAST = False

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
HOST_NAME = socket.gethostname()
if HOST_NAME == 'jd-arvin':
    CK_YAML_FILE = '/jd/config/ck.yaml'
    RESULT_COOKIE_FILE = '/jd/config/cookie.sh'

if HOST_NAME == 'ubuntu157362':
    CK_YAML_FILE = '/home/arvin/ck.yaml'
    RESULT_COOKIE_FILE = os.path.join(os.environ['HOME'], 'cookie.sh')

if HOST_NAME == 'arvin-wang':
    CK_YAML_FILE = '/home/arvin/ck.yaml'
    RESULT_COOKIE_FILE = os.path.join('/home/arvin', 'cookie2.sh')

assert os.path.isfile(CK_YAML_FILE)

logging.info("CK_YAML_FILE {}".format(CK_YAML_FILE))
logging.info('RESULT_COOKIE_FILE {}'.format(RESULT_COOKIE_FILE))
notify = sendNotify()


def get_remaining_of_days(cookie_item: dict) -> int:
    payment_time = datetime.date(cookie_item.get('payment_time'))
    duration_of_day = cookie_item.get('duration_of_day')
    assert payment_time is not None and duration_of_day is not None


def sort_cookie(cookie_item_list):
    n = len(cookie_item_list)
    for i in range(n):
        for j in range(0, n - i - 1):
            if cookie_item_list[j].get('priority') > cookie_item_list[j + 1].get('priority'):
                cookie_item_list[j], cookie_item_list[j + 1] = cookie_item_list[j + 1], cookie_item_list[j]

def send_broadcast(cookie_item: dict, title="这是广播信息"):
    logging.warning('{}'.format(cookie_item))
    if cookie_item.get('pushplus_token') is not None:
        notify.set_push_push_token(cookie_item.get('pushplus_token'))
        result_list = []
        result_list.append('用户名: {}'.format(cookie_item.get('name')))
        result_list.append('微信: {}'.format(cookie_item.get('wechart')))
        result_list.append('优先级: {}'.format(cookie_item.get('priority')))
        try:
            register_time = cookie_item.get('register_time')
            payment_time = cookie_item.get('payment_time')
            duration_of_day = cookie_item.get('duration_of_day')
            result_list.append('注册日期: {}'.format(datetime.strptime(register_time.isoformat(), "%Y-%m-%d")))
            result_list.append('付款日期: {}'.format(datetime.strptime(payment_time.isoformat(), "%Y-%m-%d")))
            result_list.append('购买天数: {} 天'.format(duration_of_day))
            payment_time = datetime.strptime(payment_time.isoformat(), "%Y-%m-%d")
            now = datetime.strptime(time.strftime("%Y-%m-%d", time.localtime()), "%Y-%m-%d")
            pass_days = now - payment_time
            if duration_of_day < 0:
                result_list.append("剩余天数: 永久")
            elif duration_of_day > 0 and pass_days.days < duration_of_day:
                result_list.append("剩余天数: {} 天".format(duration_of_day - pass_days))
            elif duration_of_day > 0 and pass_days.days > duration_of_day:
                result_list.append("超期数量: {} 天".format(pass_days.days - duration_of_day))
            else:
                result_list.append("剩余天数: 计算错误，联系管理员")

        except Exception as e:
            logging.error(e)
        result_list.append("\n\n 如有错误，联系管理员修改")
        notify.pushPlusNotify(title, '\n'.join(result_list))

def out_day(cookie_item: dict, title="用户超期"):
    if cookie_item.get('wechart') is not None:
        logging.warning("微信号 {} 超期".format(cookie_item.get('wechart')))
    else:
        logging.warning("用户名 {} 超期".format(cookie_item.get('name')))
    logging.warning('{}'.format(cookie_item))
    if cookie_item.get('pushplus_token') is not None:
        notify.set_push_push_token(cookie_item.get('pushplus_token'))
        result_list = []
        result_list.append('用户名: {}'.format(cookie_item.get('name')))
        result_list.append('微信: {}'.format(cookie_item.get('wechart')))
        result_list.append('优先级: {}'.format(cookie_item.get('priority')))
        try:
            register_time = cookie_item.get('register_time')
            payment_time = cookie_item.get('payment_time')
            duration_of_day = cookie_item.get('duration_of_day')
            result_list.append('注册日期: {}'.format(datetime.strptime(register_time.isoformat(), "%Y-%m-%d")))
            result_list.append('付款日期: {}'.format(datetime.strptime(payment_time.isoformat(), "%Y-%m-%d")))
            result_list.append('购买天数: {} 天'.format(duration_of_day))
            payment_time = datetime.strptime(payment_time.isoformat(), "%Y-%m-%d")
            now = datetime.strptime(time.strftime("%Y-%m-%d", time.localtime()), "%Y-%m-%d")
            pass_days = now - payment_time
            if duration_of_day < 0:
                result_list.append("剩余天数: 永久")
            elif duration_of_day > 0 and pass_days.days < duration_of_day:
                result_list.append("剩余天数: {} 天".format(duration_of_day - pass_days))
            elif duration_of_day > 0 and pass_days.days > duration_of_day:
                result_list.append("超期数量: {} 天".format(pass_days.days - duration_of_day))
            else:
                result_list.append("剩余天数: 计算错误，联系管理员")

        except Exception as e:
            logging.error(e)
        result_list.append("\n\n 如有错误，联系管理员")
        notify.pushPlusNotify(title, '\n'.join(result_list))


if __name__ == '__main__':
    result_ck_yaml_list = []
    high_priority_ck = []

    sorte_ck_result = []

    with open(CK_YAML_FILE, 'r', encoding="utf-8") as fp:
        yaml_result = yaml.load(fp.read(), Loader=yaml.SafeLoader)
        for cookie_item in yaml_result.get('cookies'):
            try:
                ck = cookie_item.get('cookie')
                duration_of_day = cookie_item.get('duration_of_day')
                register_time = cookie_item.get('register_time')
                payment_time = cookie_item.get('payment_time')
                assert ck is not None
                assert duration_of_day is not None
                payment_time = datetime.strptime(payment_time.isoformat(), "%Y-%m-%d")
                now = datetime.strptime(time.strftime("%Y-%m-%d", time.localtime()), "%Y-%m-%d")
                pass_days = now - payment_time

                if FORCE_BROADCAST:
                    send_broadcast(cookie_item, "个人信息确认")

                if duration_of_day > 0 and pass_days.days > duration_of_day:
                    out_day(cookie_item)
                    continue
                result_ck_yaml_list.append(cookie_item)

            except Exception as e:
                logging.error(e)

    sort_cookie(result_ck_yaml_list)
    with open(RESULT_COOKIE_FILE, 'w') as f:
        count = 1
        for i in result_ck_yaml_list:
            f.write("# {}\n".format(i.get('name')))
            f.write("Cookie{}=\"{}\"\n".format(count, i.get('cookie')))
            count += 1
