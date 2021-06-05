import utils.utils as util
import os
import logging
import yaml
from datetime import datetime
import time
from sendNotify import sendNotify

logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.DEBUG)

FILE_DIR = os.path.dirname(os.path.abspath(__file__))

if util.is_docker_server():
    CK_YAML_FILE = '/jd/config/ck.yaml'
    RESULT_COOKIE_FILE = '/jd/config/cookie.sh'

if util.get_host_name() == 'ubuntu157362':
    CK_YAML_FILE = '/home/arvin/ck.yaml'
    RESULT_COOKIE_FILE = os.path.join(os.environ['HOME'], 'cookie.sh')

if util.get_host_name() == 'arvin-wang':
    CK_YAML_FILE = '/home/arvin/work/jd_v4/config/ck.yaml'
    RESULT_COOKIE_FILE = os.path.join('/home/arvin/work/jd_v4/config', 'cookie.sh')

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


def out_day(cookie_item: dict):
    if cookie_item.get('wechart') is not None:
        logging.warning("微信号 {} 超期".format(cookie_item.get('wechart')))
    else:
        logging.warning("用户名 {} 超期".format(cookie_item.get('name')))
    logging.warning('{}'.format(cookie_item))
    if cookie_item.get('pushplus_token') is not None:
        notify.set_push_push_token(cookie_item.get('pushplus_token'))
        notify.pushPlusNotify('asdfasfsdfsaf', 'afasdfsfsfsdfsdf')


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
