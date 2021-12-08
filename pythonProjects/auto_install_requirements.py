# -*- coding:utf-8 -*-
import configparser
import sys
import os
import socket
import logging
import tempfile

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(os.path.dirname(FILE_DIR)))

HOST_NAME = socket.gethostname()
DEBUG = 'jd-arvin' not in HOST_NAME
logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.DEBUG)

crontab_file = '/jd/config/crontab.list'
work_home = '/jd/scripts'
cache_files = '/jd/auto_install_cache_file.sh'
if DEBUG:
    crontab_file = '/home/arvin/work/jd_v4/config/crontab.list'
    work_home = '/home/arvin/work/jd_v4/scripts'
    cache_files = '/home/arvin/auto_install_cache_file.sh'
if not os.path.isfile(cache_files):
    os.system('touch {}'.format(cache_files))
assert os.path.isfile(crontab_file)
assert os.path.isdir(work_home)
force_dep_list = ["tough-cookie", "got"]
npm_path = "/usr/bin/npm_my"

def TIMEOUT_COMMAND(command, timeout=300):
    """call shell-command and either return its output or kill it
    if it doesn't normally exit within timeout seconds and return None"""
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
            return result, process.returncode
    return process.communicate()[0].decode('utf-8'), process.returncode


installed_list = []
cache_skip_files_list_list = []
with open(cache_files, 'r') as f:
    for key in f.read().split(';'):
        key = key.strip().replace(' ', '').replace('\n','')
        if key == '':
            continue
        cache_skip_files_list_list.append(key)
with open(crontab_file, 'r') as f:
    for line in f.readlines():
        line = line.strip()
        if line.startswith('#'):
            continue
        if 'otask' not in line:
            continue
        absolute_file = None
        for key in line.split('otask')[-1].split(' '):
            if '.js' in key:
                absolute_file = key
                if DEBUG:
                    absolute_file = os.path.join(work_home, str(absolute_file).split('/')[-1])
                break
        if absolute_file is None:
            logging.error("crontab list 配置错误")
            continue

        if not os.path.isfile(absolute_file):
            logging.error("js不存在: {}".format(absolute_file))
            continue
        # absolute_file = '/home/arvin/work/jd_v4/scripts/jd_beauty.js'
        file_name = absolute_file.split('/')[-1]
        if file_name in cache_skip_files_list_list:
            logging.info("file_name {} 在忽律緩存中,忽律檢查".format(file_name))
            continue
        run_scripts_cmd = 'cd {};cp {} {}; node {} 2>&1'.format(work_home, absolute_file, work_home, file_name)
        logging.info("run cmd: {}".format(run_scripts_cmd))
        run_scripts_cmd_output, return_code = TIMEOUT_COMMAND(run_scripts_cmd, 600)
        logging.info("执行返回状态码: {}".format(return_code))
        if return_code == 0:
            logging.info("执行成功，忽律检查依赖包")
            continue
        logging.info(run_scripts_cmd_output)
        for run_cmd_result_line in run_scripts_cmd_output.split('\n'):
            run_cmd_result_line = str(run_cmd_result_line).strip().replace('\n', '')
            logging.info(run_cmd_result_line)
            if 'Error: Cannot find module' in run_cmd_result_line:
                requirement_module = run_cmd_result_line.split('Error: Cannot find module')[-1].replace('\'',
                                                                                                        '').strip()
                logging.info("需要安装: {}".format(requirement_module))
                if '/' in requirement_module:
                    logging.info("依赖本地文件，skip")
                    cache_skip_files_list_list.append(file_name)
                    break
                installed_list.append(requirement_module)
                install_cmd = 'cd {}; {} install --save {} --registry=https://registry.npm.taobao.org 2>&1'.format(npm_path, work_home, requirement_module)
                logging.info("run " + install_cmd)
                install_cmd_result = TIMEOUT_COMMAND(install_cmd, 10*60)
                logging.info(install_cmd_result)



for i in force_dep_list:
    install_cmd = 'cd {}; {} install --save {} --registry=https://registry.npm.taobao.org 2>&1'.format(npm_path,
                                                                                                       work_home,
                                                                                                      i)
    logging.info("run " + install_cmd)
    install_cmd_result = TIMEOUT_COMMAND(install_cmd, 10 * 60)

logging.info("共计安装{}个: {}".format(len(installed_list), ' '.join(installed_list)))
with open(cache_files, 'w') as f:
    f.write(';'.join(cache_skip_files_list_list))
