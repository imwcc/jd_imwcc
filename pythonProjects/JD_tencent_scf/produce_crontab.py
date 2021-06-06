import json
import os
import demjson
import socket
import time
import yaml

import logging

logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.DEBUG)

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
print(FILE_DIR)

HOST_NAME = socket.gethostname()
DEBUG = HOST_NAME != 'jd-arvin'


RESULT_FILE_NAME = 'crontab.list'
RESULT_FILE = os.path.join(FILE_DIR, RESULT_FILE_NAME)

exclude_file_list = []

exclude_yaml_file_list = []

if HOST_NAME == 'arvin-wang':
    ROOT_DIR = '/home/arvin/code'

elif HOST_NAME == 'jd-arvin':
    ROOT_DIR = '/jd/own'

elif HOST_NAME == 'ubuntu157362':
    ROOT_DIR = '/home/arvin/code'
else:
    logging.error("请配置jd_tencent_scf目录")
    exit(-1)

if HOST_NAME == 'jd-arvin':
    new_scripts_dir = os.path.join(ROOT_DIR, 'zero205_JD_tencent_scf')
    RESULT_FILE = os.path.join(new_scripts_dir, RESULT_FILE_NAME)
else:
    new_scripts_dir = os.path.join(ROOT_DIR, 'JD_tencent_scf')

parse_from_file = os.path.join(new_scripts_dir, 'jd_task.json')

if not os.path.exists(new_scripts_dir):
    logging.error("找不到配置文件")
    exit(-1)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    result_crontab_list = []
    old_crontab_list = []

    if os.path.isfile(RESULT_FILE):
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        with open(RESULT_FILE, 'r') as f:
            for line in f.readlines():
                line = line.strip().replace('\n', '')
                if line.strip() == '':
                    continue
                elif line.startswith('#'):
                    continue
                elif '.js' not in line and 'jtask' not in line:
                    continue
                old_crontab_list.append(line)

    with open(parse_from_file, 'r') as f:
        s = f.read()
        result = demjson.decode(s)
        for item in result.get("list"):
            file_name = item.get('job').get('target').split('/')[-1].strip()
            if file_name != '':
                if file_name in exclude_file_list:
                    logging.info("{} 在排除列表中".format(file_name))
                    continue

                # is_in_old_crontab_list = False
                # # 判斷是否在 已經jd_scripts 配置中， 若是 退出
                # for jd_scripts_line_item in old_crontab_list:
                #     if str(file_name).split('.js')[0] in str(jd_scripts_line_item):
                #         is_in_old_crontab_list = True
                #         logging.info("{} 已经存在于 {}".format(file_name, jd_scripts_line_item))
                #         break
                # if is_in_old_crontab_list:
                #     continue

                comment = "# {}".format(item.get('name'))
                result_crontab_list.append(comment)
                crontab_item = "{} otask {}".format(item.get('time'), os.path.join(new_scripts_dir, file_name))
                if DEBUG:
                    print(crontab_item)
                result_crontab_list.append(crontab_item)

    logging.info("============================= 分割线 =====================================")
    if len(result_crontab_list) > 0:
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        with open(RESULT_FILE, 'w') as f:
            f.write("# =========== JD-SCRIPT start {}  ==============\n".format(current_time))
            for line in result_crontab_list:
                logging.info(line)
                f.write(line + '\n')
            f.write("# =========== JD-SCRIPT end {} ==============\n\n".format(current_time))
