import os
from UserInfo import UserInfo
import socket
import yaml
import logging

logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.DEBUG)

HOST_NAME = socket.gethostname()
DEBUG = 'jd-arvin' not in HOST_NAME

if os.path.isdir('/jd/config'):
    yamlPath = os.path.join('/jd/config', 'ck.yaml')
else:
    yamlPath = os.getenv('ck_yaml_path')

if DEBUG:
    v4_ck_file = os.getenv('v4_ck_file')

else:
    v4_ck_file = '/jd/config/cookie.sh'

assert os.path.isfile(yamlPath)
assert os.path.isfile(v4_ck_file)


def send_bean_notify(user: UserInfo):
    if DEBUG:
        user.to_string()
    if user.get_pushplus_token() is None:
        logging.error("用户没有配置push 通知 {} {}".format(user.get_nick_name(), user.get_pt_pin()))
        return -1
    logging.info("开始发送通知 to： {} {}".format(user.get_nick_name(), user.get_pt_pin()))
    if DEBUG:
        root_dir = '/home/arvin/code/jd_scripts'
    else:
        root_dir = '/jd/scripts'
    cmd = "cd {};export JD_COOKIE=\"{}\";export PUSH_PLUS_TOKEN={}; node jd_bean_change.js".format(root_dir, user.get_cookie(),
                                                                       user.get_pushplus_token())
    logging.info(cmd)
    os.system(cmd)


def get_pt_pin(ck: str):
    return ck.split('pt_pin=')[-1].replace(';', '').replace('"', '').replace('\'', '')


if __name__ == '__main__':
    user_info_l = []
    yaml_load_result = None
    with open(yamlPath, 'r', encoding='utf-8') as f:
        yaml_load_result = yaml.load(f.read(), Loader=yaml.FullLoader)
        for ck in yaml_load_result.get('cookies'):
            user_info_l.append(UserInfo(**ck))

    if os.path.isfile(v4_ck_file):
        with open(v4_ck_file, 'r', encoding='utf-8') as f:
            for new_ck in f.readlines():
                new_ck = new_ck.replace(' ', '').replace('\n', '').strip()
                if new_ck != '':
                    pt_pin = get_pt_pin(new_ck)
                    for user_info in user_info_l:
                        if user_info.get_pt_pin() == pt_pin:
                            if user_info.get_pushplus_token() is not None:
                                send_bean_notify(user_info)