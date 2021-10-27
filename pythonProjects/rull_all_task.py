# coding: utf-8
# only for v4
import logging
import os
import socket

import multiprocessing
import time

logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.DEBUG)

FILE_DIR = os.path.dirname(os.path.abspath(__file__))

HOST_NAME = socket.gethostname()
DEBUG = 'jd-arvin' not in HOST_NAME

str_crontab = os.popen("crontab -l").read()
if DEBUG:
    with open("/home/arvin/crontab.list", 'r') as f:
        str_crontab = f.read()

global_crontab_task = []

count = 0
for line in str_crontab.split('\n'):
    line = line.strip()
    if line == '' or line.startswith('#'):
        continue

    if 'otask' in line:
        print(line.split('otask')[-1])
        global_crontab_task.append("otask {}".format(line.split('otask')[-1]))
        count += 1

logging.info("共计 {} task".format(count))


def func(cmd):
    logging.info("run cmd: " + str(cmd))
    os.system(cmd)
    logging.info("run cmd done: " + str(cmd))


if __name__ == "__main__":
    pool = multiprocessing.Pool(processes=34)
    for i in range(count):
        pool.apply_async(func, (global_crontab_task[i],))  # 维持执行的进程总数为processes，当一个进程执行完毕后会添加新的进程进去

    pool.close()
    pool.join()  # 调用join之前，先调用close函数，否则会出错。执行完close后不会有新的进程加入到pool,join函数等待所有子进程结束

