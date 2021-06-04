import socket
import logging
import os
import time

logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.DEBUG)

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
HOST_NAME = socket.gethostname()
DEBUG = HOST_NAME != 'jd-arvin'

exclude_dir = ['test']

if HOST_NAME == 'jd-arvin':
    ROOT_DIR = '/jd/own'
    crontab_imwcc_file = '/jd/own/imwcc_jd_imwcc/imwcc_crontab.list'
else:
    ROOT_DIR = FILE_DIR

if DEBUG:
    old_crontab_list_file = os.path.join(FILE_DIR, 'test/crontab.list')
else:
    old_crontab_list_file = os.path.join('/jd/config/crontab.list')

if __name__ == '__main__':

    old_crontab_list = []
    result_crontab_list = []

    if os.path.isfile(old_crontab_list_file):
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        with open(old_crontab_list_file, 'r') as f:
            for line in f.readlines():
                line = line.strip().replace('\n', '')
                if line.strip() == '':
                    continue
                elif line.startswith('#'):
                    continue
                elif '.js' not in line and 'jtask' not in line:
                    continue
                old_crontab_list.append(line)

    # 1, 统计own 目录 crontab.list
    crontab_file_list = []
    for dir_name in os.listdir(ROOT_DIR):
        # print(dir_name)
        if dir_name in exclude_dir:
            continue
        if os.path.isfile(os.path.join(dir_name, 'crontab.list')):
            crontab_file_list.append(os.path.join(ROOT_DIR, dir_name, 'crontab.list'))
