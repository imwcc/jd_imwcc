import datetime
import socket
import sys

import yaml
import os
from UserInfo import UserInfo, LoginStatus
import logging
import configparser
import pushPlusNotify
import traceback
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
import json
import argparse

logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.DEBUG)
FILE_DIR = os.path.dirname(os.path.abspath(__file__))
HOST_NAME = socket.gethostname()

if os.path.isdir('/jd/config') and HOST_NAME != 'jd-arvin' and HOST_NAME != 'jd-arvin-all':
    logging.info("只需要在一台主机上运行，{}没必要运行".format(HOST_NAME))
    exit(0)

# v4 直接放入config
ck_manager_config = None
ck_out_of_login_yaml = None
if os.path.isdir('/jd/config'):
    # 获取配置文件的路径
    yamlPath = os.path.join('/jd/config', 'ck.yaml')
    ck_manager_config = os.path.join('/jd/config', 'ck_manager.cfg')
    ck_out_of_login_yaml = os.path.join('/jd/config', 'ck_out_of_login.yaml')
else:
    yamlPath = os.getenv('ck_yaml_path')
    ck_manager_config = os.getenv('ck_manager_config')
    ck_out_of_login_yaml = os.path.join(FILE_DIR, 'ck_out_of_login.yaml')
if not os.path.isfile(ck_out_of_login_yaml):
    os.system(f'touch {ck_out_of_login_yaml}')
assert os.path.isfile(ck_manager_config)
assert os.path.isfile(yamlPath)

# 任然检查上次登陆登陆失败且没有更新ck的用户登陆状态
FORCE_LOGIN_CHECK = False
DEBUG = 'jd-arvin' not in HOST_NAME
disable_user_notify = False

config = configparser.ConfigParser()
config.read(ck_manager_config)

out_put_ck_files = []
max_support_user_single = 37
# 线程池大小
thread_poll_size = 5
# 连续超过五天没有登陆,则删除该用户所有信息
invalid_user_maximum_keep_days = 6
scan_login_url = None
qinglong_ck_file = None
admin_pushplus_token = None
external_ck_file = None
flask_server_yaml = None
assistant_acount = None
if not DEBUG:
    config_name = 'CONFIG'
else:
    config_name = 'DEBUG_CONFIG'

for key in config[config_name]:
    if key == 'out_put_ck_files':
        for i in config.get(config_name, key).replace('\n', '').replace(' ', '').split(';'):
            if i.strip() != '':
                out_put_ck_files.append(i)
    elif key == 'max_support_user_single':
        try:
            max_support_user_single = int(config.get(config_name, key).replace(' ', ''))
        except Exception as e:
            logging.error(e)
            max_support_user_single = 37
    elif key == 'scan_login_url':
        scan_login_url = config.get(config_name, key).replace('\n', '').replace(' ', '')
    elif key == 'qinglong_ck_file':
        qinglong_ck_file = config.get(config_name, key).replace('\n', '').replace(' ', '')

    elif key == 'invalid_user_maximum_keep_days ':
        invalid_user_maximum_keep_days = config.get(config_name, key).replace('\n', '').replace(' ', '')

    elif key == 'admin_pushplus_token':
        admin_pushplus_token = config.get(config_name, key).replace('\n', '').replace(' ', '')

    elif key == 'force_login_check':
        FORCE_LOGIN_CHECK = config.get(config_name, key).replace('\n', '').replace(' ', '').lower() == 'true'

    elif key == 'external_ck_file':
        external_ck_file = config.get(config_name, key).replace('\n', '').replace(' ', '')

    elif key == 'thread_poll_size':
        try:
            thread_poll_size = int(config.get(config_name, key).replace(' ', ''))
        except Exception as e:
            logging.error(e)
            thread_poll_size = 5
    elif key == 'flask_server_yaml':
        flask_server_yaml = config.get(config_name, key).replace('\n', '').replace(' ', '')
    elif key == 'assistant_acount':
        assistant_acount = config.get(config_name, key).replace('\n', '').replace(' ', '')
    else:
        logging.error("不支持的 key: " + key)

assert scan_login_url is not None
for file in out_put_ck_files:
    logging.info("输出文件: " + file)
    assert os.path.isfile(file)

if not os.path.isfile(qinglong_ck_file):
    logging.error("qinglong_ck_file {}不存在，将无法更新CK!".format(qinglong_ck_file))


def bubbleSort(arr: list):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if (arr[j]).get_priority() > (arr[j + 1]).get_priority():
                arr[j], arr[j + 1] = arr[j + 1], arr[j]


def get_pt_pin(ck: str):
    return ck.split('pt_pin=')[-1].replace(';', '').replace('"', '').replace('\'', '')


# def send_notify(user: UserInfo):
#     if DEBUG:
#         return False
#     if disable_user_notify:
#         logging.info("disable_user_notify")
#         return False
#     if user.get_pushplus_token() is None:
#         logging.warning("用户没有配置通知")
#         return 0
#     content = '''您的登录已经失效
# 复制下面连接到浏览器扫码登录:
# '''
#     content += scan_login_url
#     pushPlusNotify.pushPlusNotify(user.get_pushplus_token(), content, title='登陆失效，请重新登陆')


def send_notify(user: UserInfo, title='登陆失效，请重新登陆', content="您的登录已经失效\n复制下面连接到浏览器扫码登录:\n"):
    if DEBUG:
        logging.info("send_notify title: {}\nmessage:{}".format(title, content))
    if disable_user_notify:
        logging.info("disable_user_notify")
        return False
    if user.get_pushplus_token() is None:
        logging.warning("用户没有配置通知")
        return 0
    content += '\n' + scan_login_url
    pushPlusNotify.pushPlusNotify(user.get_pushplus_token(), content, title)


def is_need_skip(user: UserInfo):
    return False


def send_admin_message(title: str, message: str):
    if disable_user_notify:
        logging.info("send_admin_message skip just for disable_user_notify");
        logging.info("title: {}\nmessage:{}".format(title, message))
        return
    if admin_pushplus_token is None:
        logging.error("没有配置管理员token")
        return -1
    pushPlusNotify.pushPlusNotify(admin_pushplus_token, str(message), title=title)


def send_fata_message(e):
    if DEBUG:
        logging.info("debug skip");
        return
    if admin_pushplus_token is None:
        logging.error("没有配置管理员token")
        return -1
    title = "ck管理器加载失败"
    pushPlusNotify.pushPlusNotify(admin_pushplus_token, str(e), title=title)


def format_qinglong_22_ck(ck: str):
    result = ''
    if 'pt_key' in ck and 'pt_pin' in ck:
        pt_key = None
        pt_pin = None
        for i in ck.split(';'):
            i = i.strip().replace(' ', '').replace('\n', '')
            if i.startswith('pt_key'):
                pt_key = i
            elif i.startswith('pt_pin'):
                pt_pin = i
        if pt_key is None or pt_pin is None:
            logging.error("pt_key or pt_pin not int ck str")
        else:
            result = f'{pt_key};{pt_pin};'
    else:
        logging.error("pt_key or pt_pin not int ck str")
    return result


def main(args):
    global disable_user_notify
    global flask_server_yaml
    global DEBUG
    global assistant_acount
    is_update_ck: bool = False
    parser = argparse.ArgumentParser()
    parser.add_argument("--update_appkey", action="store_true",
                        help="app_key to web cookie")
    parser.add_argument("--debug", action="store_true",
                        help="didn't send plush notify to user")

    parser.add_argument("--send_admin_message",
                        help="send admin message to all user, parameter is file or str")

    parser.add_argument("-v", "--verbose", action="store_true",
                        help="enable global debug swich")
    args = parser.parse_args()

    if args.update_appkey:
        is_update_ck = True
    if args.debug:
        logging.info("disable_user_notify")
        disable_user_notify = True
        DEBUG = True
    if args.verbose:
        logging.info("enable debug switch")
        DEBUG = True

    gValid_user_acount_number = 0
    try:
        # 1. 导入 yaml
        user_info_l = []
        yaml_load_result = None
        with open(yamlPath, 'r', encoding='utf-8') as f:
            yaml_load_result = yaml.load(f.read(), Loader=yaml.FullLoader)
            signServer = yaml_load_result.get('sign_server', None)
            if signServer is None:
                send_admin_message("sign error", "signserver 没有配置")
            for ck in yaml_load_result.get('cookies'):
                user = UserInfo(sign_server=signServer, **ck).format_ck()
                if not user.has_config_key():
                    logging.error("无效的用户: {}".format(user.get_user_dict()))
                    continue
                user_info_l.append(user)

        # 1.1 仅发送管理员消息
        if args.send_admin_message:
            logging.info("发送管理员消息")
            send_message_content = str(args.send_admin_message)
            if os.path.isfile(str(args.send_admin_message)):
                with open(args.send_admin_message, 'r', encoding='utf-8') as f:
                    send_message_content = f.read()
            for user in user_info_l:
                send_notify(user, "管理员消息", send_message_content)
            logging.info("发送管理员消息发送结束")
            exit(0)

        # 3. 更新CK or 添加新用户 from qinglong 关闭
        if os.path.isfile(qinglong_ck_file) and False:
            with open(qinglong_ck_file, 'r', encoding='utf-8') as f:
                for new_ck in f.readlines():
                    new_ck = new_ck.replace(' ', '').replace('\n', '').strip()
                    new_ck = format_qinglong_22_ck(new_ck)
                    if new_ck != '':
                        pt_pin = get_pt_pin(new_ck)
                        is_new_ck = True
                        for user_info in user_info_l:
                            if user_info.get_pt_pin() == pt_pin:
                                is_new_ck = False
                                if user_info.get_cookie() == new_ck:
                                    logging.info("pt_pin={} 不需要更新".format(pt_pin))
                                else:
                                    logging.info("{} 更新ck: {}".format(pt_pin, new_ck))
                                    user_info.set_cookie(new_ck)
                                    user_info.set_login_status(LoginStatus.NEED_CHECK.value)
                        if is_new_ck:
                            new_user = UserInfo(new_ck)
                            logging.info("添加新用户 {}".format(new_user))
                            new_user.to_string()
                            user_info_l.append(new_user)
                    else:
                        logging.error("cat null qinglong ck: {}".format(new_ck))

        # 3.1 更新flask server
        if os.path.isfile(flask_server_yaml):
            temp_user_info_l = []
            with open(flask_server_yaml, 'r', encoding='utf-8') as f:
                flask_server_yaml = yaml.load(f.read(), Loader=yaml.FullLoader)
                signServer = flask_server_yaml.get('sign_server', None)
                if signServer is None:
                    send_admin_message("sign error", "signserver 没有配置")
                for ck in flask_server_yaml.get('cookies'):
                    user = UserInfo(sign_server=signServer, **ck).format_ck()
                    if not user.has_config_key():
                        continue
                    temp_user_info_l.append(user)

            for new_user in temp_user_info_l:
                is_new_user_from_flask = True
                for user in user_info_l:
                    if new_user.get_pt_pin() == user.get_pt_pin():
                        is_new_user_from_flask = False
                        logging.info("flask server 更新CK: old:" + str(user.get_user_dict()))
                        logging.info("flask server 更新CK: new:" + str(new_user.get_user_dict()))
                        user.update_ck_from_user(new_user, update_cookie=(
                                    user.get_login_status() == LoginStatus.INVALID_LOGIN.value))
                if is_new_user_from_flask:
                    logging.info("add new user from flask: " + str(new_user.get_user_dict()))
                    user_info_l.append(new_user)
        else:
            logging.error("flask yaml 不存在")

        # 3.2 根据优先级排序
        bubbleSort(user_info_l)

        # 4.0 update app key
        logging.info("begin update_ws_key_to_pt_key")
        for user_info in user_info_l:
            if not is_update_ck:
                logging.info("is_update_ck false, skip update ck")
                break
            if user_info.get_appkey() is not None:
                if not user_info.update_ws_key_to_pt_key():
                    logging.error("{} app key to pt_key 更新失败".format(user_info.get_pt_pin()))
                    send_notify(user_info, title='app key已失效,请联系管理员', content=''''请联系管理员配置\n''')
                else:
                    logging.info("{} app key to pt_key 更新成功".format(user_info.get_pt_pin()))
                    user_info.set_login_status(LoginStatus.NEED_CHECK.value)
        logging.info("done update_ws_key_to_pt_key")

        # 4.1 更新只有app key的ck
        for user_info in user_info_l:
            if user_info.get_appkey() is not None and user_info.get_cookie() is None:
                logging.info("用户需要 update_ws_key_to_pt_key: {}".format(user.get_pt_pin()))
                if user_info.update_ws_key_to_pt_key():
                    logging.info("{} app key to pt_key 2 更新成功".format(user_info.get_pt_pin()))
                else:
                    logging.info("{} app key to pt_key 2 更新失败".format(user_info.get_pt_pin()))

        # 4.2 并发刷新登陆状态
        logging.info("检查登陆状态开始, 线程池数量: {}".format(thread_poll_size))
        executor = ThreadPoolExecutor(max_workers=thread_poll_size)
        for user_info in user_info_l:
            logging.info("开始检查 nickName={} pt_pin={}".format(user_info.get_nick_name(), user_info.get_pt_pin()))
            if not FORCE_LOGIN_CHECK and user_info.get_login_status() == LoginStatus.INVALID_LOGIN.value:
                logging.info(
                    "nickName={} pt_pin={}登陆已经失效，忽略检查".format(user_info.get_nick_name(), user_info.get_pt_pin()))
                continue

            def check_login(user: UserInfo):
                if user.is_login():
                    logging.info("nickName={} pt_pin={}登陆成功".format(user.get_nick_name(), user.get_pt_pin()))
                    user.set_login_status(LoginStatus.LAST_LOGINED.value)
                    user.update_last_login_date()
                elif user.get_appkey() is not None:
                    user.update_ws_key_to_pt_key()
                    if user.is_login():
                        user.set_login_status(LoginStatus.LAST_LOGINED.value)
                        user.update_last_login_date()
                    else:
                        logging.warning("更新wskey依然失效登陆失效： {} {}".format(user.get_nick_name(), user.get_pt_pin()))
                        send_notify(user, content="更新wskey依然失效登陆失效.\n请联系管理员解决")
                        user.set_login_status(LoginStatus.INVALID_LOGIN.value)
                else:
                    logging.warning("用户登陆失效： {} {}".format(user.get_nick_name(), user.get_pt_pin()))
                    send_notify(user)
                    user.set_login_status(LoginStatus.INVALID_LOGIN.value)

            all_task = [executor.submit(check_login, user_info)]
        wait(all_task, return_when=ALL_COMPLETED, timeout=600)
        executor.shutdown()
        logging.info("检查登陆状态完成")

        # 5. 写入 v4
        out_v4_user_list = []
        for user_info in user_info_l:
            if user_info.get_login_status() == LoginStatus.LAST_LOGINED.value:
                if not is_need_skip(user_info):
                    out_v4_user_list.append(user_info)
                else:
                    logging.info("忽略用户: " + user_info.get_pt_pin())
        logging.info("{}个有效用户".format(len(out_v4_user_list)))
        # 用户不足的时候，help from friends
        if len(out_v4_user_list) < len(out_put_ck_files) * max_support_user_single:
            request_ck_number = len(out_put_ck_files) * max_support_user_single - len(out_v4_user_list)
            logging.info("用户不足，还需要加载{}个".format(request_ck_number))
            # 1 从文本加载后需要倒叙
            external_ck_list = []
            if external_ck_file is not None and os.path.isfile(external_ck_file):
                with open(external_ck_file, 'r') as f:
                    for ck in f.readlines():
                        ck = ck.replace(' ', '').replace('\n', '').replace('"', '')
                        if ck == '':
                            continue
                        if 'pt_pin' not in ck or 'pt_key' not in ck:
                            logging.error(f'不是有效的ck {ck}')
                            continue
                        external_ck_list.append(ck)
            external_ck_list.reverse()
            # 2. 加载进 out_v4_ck_file
            for ck in external_ck_list:
                user = UserInfo(ck=ck)
                if user.is_login():
                    is_new = True
                    for user_info in out_v4_user_list:
                        if user_info.get_pt_pin() == user.get_pt_pin():
                            is_new = False
                            break
                    if is_new:
                        out_v4_user_list.append(user)
                if len(out_v4_user_list) == len(out_put_ck_files) * max_support_user_single:
                    logging.info("加载外部ck{}个完成".format(request_ck_number))
                    break
            if len(out_v4_user_list) < len(out_put_ck_files) * max_support_user_single:
                logging.info(
                    "加载外部ck没有完成, 差 {}个".format(len(out_put_ck_files) * max_support_user_single - len(out_v4_user_list)))
            logging.info("加载外部用户后， {}个有效用户".format(len(out_v4_user_list)))

        for out_v4_ck_file in out_put_ck_files:
            count = 0
            assistant_users = []
            with open(out_v4_ck_file, 'w') as f:
                for user_info in out_v4_user_list:
                    count += 1
                    gValid_user_acount_number += 1
                    f.writelines('Cookie{}="{}"\n'.format(count, user_info.get_cookie()))
                    if user_info.get_pt_pin() == assistant_acount:
                        logging.info("添加 assistant account: " + str(user_info.get_pt_pin()))
                        assistant_users.append(user_info)
                    if count == max_support_user_single:
                        break
            logging.info("文件{} 写入{}个".format(out_v4_ck_file, count))
            # 上一轮输出写满的情况,保留前部3个用户到第二容器
            if count == max_support_user_single:
                assistant_users.append(out_v4_user_list[0])
                logging.info("高管: " + ' '.join(assistant_acount))
                out_v4_user_list = assistant_users + out_v4_user_list[max_support_user_single:]
            else:
                logging.info("写入 v4 完成")
                break

        # 6. 格式化优先级
        for index in range(len(user_info_l)):
            user_info_l[index].set_priority(index + 1)

        with open(yamlPath, 'w', encoding='utf-8') as w_f:
            # 覆盖原先的配置文件
            result_ck_list = []
            for user_info in user_info_l:
                if user_info.get_last_login_date_expired_days() > invalid_user_maximum_keep_days:
                    logging.info("用户超期")
                    logging.info(user_info.to_string())
                    continue
                result_ck = user_info.get_user_dict()
                result_ck_list.append(result_ck)
            yaml_load_result['cookies'] = result_ck_list
            yaml_load_result['valid_user_account'] = gValid_user_acount_number
            yaml.dump(yaml_load_result, w_f, encoding='utf-8', allow_unicode=True, default_flow_style=False,
                      sort_keys=False)

        yaml_out_of_login_result = None
        with open(ck_out_of_login_yaml, 'r') as w_f:
            yaml_out_of_login_result = yaml.load(w_f.read(), Loader=yaml.FullLoader)
            if yaml_out_of_login_result is None:
                logging.error("yaml_out_of_login_result is None")
                yaml_out_of_login_result = {'cookies': []}

        with open(ck_out_of_login_yaml, 'a+') as w_f:
            nick_name_list = []
            for ck in yaml_out_of_login_result.get('cookies'):
                nick_name_list.append(ck.get('nick_name'))
            result_ck_list = []
            for user_info in user_info_l:
                if user_info.get_last_login_date_expired_days() > invalid_user_maximum_keep_days and \
                        user_info.get_nick_name() not in nick_name_list:
                    result_ck = user_info.get_user_dict()
                    result_ck_list.append(result_ck)
                    logging.info("移除用户: " + str(result_ck))
                    send_admin_message(title="管理员消息", message="用超过{}天未登陆,已移除\n用户信息:{}".
                                       format(invalid_user_maximum_keep_days,
                                              str(json.dumps(result_ck, indent=1, sort_keys=True, default=str))))
            if yaml_out_of_login_result.get('cookies') is None:
                yaml_out_of_login_result['cookies'] = result_ck_list
            else:
                yaml_out_of_login_result['cookies'] = yaml_out_of_login_result.get('cookies') + result_ck_list
            yaml.dump(yaml_out_of_login_result, w_f, encoding='utf-8', allow_unicode=True, default_flow_style=False,
                      sort_keys=False)
    except Exception as e:
        logging.error(e)
        msg = traceback.format_exc()
        e = "Host: {}\n{}\n{}".format(HOST_NAME, msg, str(e))
        logging.error(e)
        send_fata_message(e)


if __name__ == "__main__":
    main(sys.argv)
