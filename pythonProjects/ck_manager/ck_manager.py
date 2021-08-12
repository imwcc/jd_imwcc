import socket
import yaml
import os
from UserInfo import UserInfo, LoginStatus
import logging
import configparser
import pushPlusNotify
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED

logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.DEBUG)
FILE_DIR = os.path.dirname(os.path.abspath(__file__))
HOST_NAME = socket.gethostname()

if os.path.isdir('/jd/config') and HOST_NAME != 'jd-arvin':
    logging.info("只需要在一台主机上运行，{}没必要运行".format(HOST_NAME))
    exit(0)

# v4 直接放入config
ck_manager_config = None
if os.path.isdir('/jd/config'):
    # 获取配置文件的路径
    yamlPath = os.path.join('/jd/config', 'ck.yaml')
    ck_manager_config = os.path.join('/jd/config', 'ck_manager.cfg')
else:
    yamlPath = os.getenv('ck_yaml_path')
    ck_manager_config = os.getenv('ck_manager_config')

assert os.path.isfile(ck_manager_config)
assert os.path.isfile(yamlPath)

# 任然检查上次登陆登陆失败且没有更新ck的用户登陆状态
FORCE_LOGIN_CHECK = False
DEBUG = 'jd-arvin' not in HOST_NAME

config = configparser.ConfigParser()
config.read(ck_manager_config)

out_put_ck_files = []
max_support_user_single = 37
# 线程池大小
thread_poll_size = 5
scan_login_url = None
qinglong_ck_file = None
admin_pushplus_token = None
external_ck_file = None

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


def send_notify(user: UserInfo):
    if user.get_pushplus_token() is None:
        logging.warning("用户没有配置通知")
        return 0
    content = '''您的登录已经失效
复制下面连接到浏览器扫码登录:
'''
    content += scan_login_url
    pushPlusNotify.pushPlusNotify(user.get_pushplus_token(), content, title='登陆失效，请重新登陆')


def is_need_skip(user: UserInfo):
    return False


def send_fata_message(e):
    if admin_pushplus_token is None:
        logging.error("没有配置管理员token")
        return -1
    title = "ck管理器加载失败"
    pushPlusNotify.pushPlusNotify(admin_pushplus_token, str(e), title=title)


if __name__ == '__main__':
    try:
        # 1. 导入 yaml
        user_info_l = []
        yaml_load_result = None
        with open(yamlPath, 'r', encoding='utf-8') as f:
            yaml_load_result = yaml.load(f.read(), Loader=yaml.FullLoader)
            for ck in yaml_load_result.get('cookies'):
                user_info_l.append(UserInfo(**ck))

        # 2. 根据优先级排序
        bubbleSort(user_info_l)

        # 3. 更新CK or 添加新用户
        if os.path.isfile(qinglong_ck_file):
            with open(qinglong_ck_file, 'r', encoding='utf-8') as f:
                for new_ck in f.readlines():
                    new_ck = new_ck.replace(' ', '').replace('\n', '').strip()
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
        # 4. 并发刷新登陆状态
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
        if len(out_v4_user_list) < len(out_put_ck_files)*max_support_user_single:
            request_ck_number = len(out_put_ck_files)*max_support_user_single - len(out_v4_user_list)
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
                if len(out_v4_user_list) == len(out_put_ck_files)*max_support_user_single:
                    logging.info("加载外部ck完成")
                    break
            if len(out_v4_user_list) < len(out_put_ck_files)*max_support_user_single:
                logging.info("加载外部ck没有完成, 差 {}个".format(len(out_put_ck_files)*max_support_user_single - len(out_v4_user_list)))
            logging.info("加载外部用户后， {}个有效用户".format(len(out_v4_user_list)))

        for out_v4_ck_file in out_put_ck_files:
            count = 0
            with open(out_v4_ck_file, 'w') as f:
                for user_info in out_v4_user_list:
                    count += 1
                    f.writelines('Cookie{}="{}"\n'.format(count, user_info.get_cookie()))
                    if count == max_support_user_single:
                        break
            logging.info("文件{} 写入{}个".format(out_v4_ck_file, count))
            # 上一轮输出写满的情况,保留前部3个用户到第二容器
            if count == max_support_user_single:
                out_v4_user_list = out_v4_user_list[0:4] + out_v4_user_list[max_support_user_single:]
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
                result_ck = {'cookie': user_info.get_cookie(), 'name': user_info.get_name(),
                             'wechart': user_info.get_wechart(), 'out_of_time': user_info.get_out_of_time(),
                             'register_time': user_info.get_register_time(), 'priority': user_info.get_priority(),
                             'login_status': user_info.get_login_status(),
                             'nick_name': user_info.get_nick_name(),
                             'pushplus_token': user_info.get_pushplus_token()}
                result_ck_list.append(result_ck)
            yaml_load_result['cookies'] = result_ck_list
            yaml.dump(yaml_load_result, w_f, encoding='utf-8', allow_unicode=True)
    except Exception as e:
        logging.error(e)
        send_fata_message(e)
