import logging
import os
import configparser
import socket

logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.DEBUG)
FILE_DIR = os.path.dirname(os.path.abspath(__file__))


config = configparser.ConfigParser()
config.read(os.path.join(FILE_DIR, 'diy_change_global.cfg'))

HOST_NAME = socket.gethostname()
DEBUG = 'jd-arvin' not in HOST_NAME
if not DEBUG:
    config_name = 'CONFIG'
else:
    config_name = 'DEBUG_CONFIG'

js_exclude_dir_list = []
js_exclude_files_list = []
ROOT_DIR = None

for key in config[config_name]:
    if key == 'js_exclude_dir':
        js_exclude_dir_list = config.get(config_name, key).replace('\n', '').split(',')
    elif key == 'js_exclude_files':
        js_exclude_files_list = config.get(config_name, key).replace('\n', '').split(',')
    elif key == 'root_dir':
        ROOT_DIR = config.get(config_name, key)
    else:
        logging.error("不支持的 key: " + key)

assert ROOT_DIR is not None

def remove_help_author_help(file):
    assert os.path.isfile(file), file
    cmds = []
    cmds.append("sed -i 's/let helpAuthor = true/let helpAuthor = false/g' {}".format(
        file))
    cmds.append("sed -i 's/const helpAuthor = true/const helpAuthor = false/g' {}".format(
        file))

    for cmd in cmds:
        result: bool = os.system(cmd) == 0
        logging.info("{} {} ".format(result, cmd))

def is_need_skip(dir_name, file_name) -> bool:
    __skip_check = False
    if os.path.isdir(os.path.join(dir_name, file_name)):
        __skip_check = True
    elif '.js' not in file_name:
        __skip_check = True
    elif file_name in js_exclude_files_list:
        logging.info("skip {}".format(os.path.join(dir_name, file_name)))
        __skip_check = True
    return __skip_check

if __name__ == '__main__':
    for js_dir in os.listdir(ROOT_DIR):
        if js_dir in js_exclude_dir_list:
            logging.info("skip dir: {}".format(js_dir))
            continue
        check_dir = os.path.join(ROOT_DIR, js_dir)
        for file_name in os.listdir(check_dir):
            absolute_path_file = os.path.join(check_dir, file_name)
            if is_need_skip(check_dir, file_name):
                continue
            remove_help_author_help(absolute_path_file)




