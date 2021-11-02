# -*- coding:utf-8 -*-
import configparser
import sys
import os
import socket
import logging
import tempfile
HOST_NAME = socket.gethostname()
DEBUG = 'jd-arvin' not in HOST_NAME
logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.DEBUG)

def TIMEOUT_COMMAND(command, timeout=300):
    """call shell-command and either return its output or kill it
    if it doesn't normally exit within timeout seconds and return None"""
    logging.info("run cmd: " + command)
    import subprocess, datetime, os, time, signal
    cmd = command.split(" ")
    start = datetime.datetime.now()
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    while process.poll() is None:
        time.sleep(0.2)
        now = datetime.datetime.now()
        if (now - start).seconds > timeout:
            logging.error("超時，杀掉: {}".format(command))
            result = process.communicate()[0].decode('utf-8')
            os.kill(process.pid, signal.SIGKILL)
            os.waitpid(-1, os.WNOHANG)
            return result
    return process.communicate()[0].decode('utf-8')


if __name__ == '__main__':
    start_docker = ['/home/arvin/work/jd_v4']
    flask_server_home = '/home/arvin/work/jd_v4/own/imwcc_jd_imwcc/pythonProjects/ck_manager'
    flask_server_name = 'flask_server'

    for i in start_docker:
        print(TIMEOUT_COMMAND('cd {}; docker-compose up -d'.format(i)))

    for line in TIMEOUT_COMMAND('docker container ls').split('\n'):
        if 'CONTAINER ID' in line:
            continue
        line = line.strip()
        key = line.split(' ')[-1]
        if 'jd-' in key:
            logging.info("找到容器: " + line)
        container_id = line.split(' ')[0].strip()
        print(TIMEOUT_COMMAND(' docker container exec -it {} /jd/config/diy.sh 2>&1'.format(container_id), 15 * 60))
        print(TIMEOUT_COMMAND(' docker container exec -it {} /jd/jup.sh 2>&1'.format(container_id), 15 * 60))

    flask_server_start_cmd = 'cd {};python3 flask_server.py'.format(flask_server_home)
    TIMEOUT_COMMAND('screen -dmS {}'.format(flask_server_name))
    TIMEOUT_COMMAND('screen -x -S {} -X screen {}'.format(flask_server_name, flask_server_start_cmd))
