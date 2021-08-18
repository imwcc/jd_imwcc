import os.path
import socket
import logging

HOST_NAME = socket.gethostname()


def is_docker_server(host_name=HOST_NAME):
    return host_name == 'jd-arvin'


def get_host_name():
    return HOST_NAME


def get_crontab_from_line(line: str) -> str:
    crontab_config = None
    is_find_schedule_cron = False
    if '.js' in line and '*' in line:
        line = line.strip()
        is_good = False
        count = 0
        index_begin = -1
        for index, ch in enumerate(line):
            if (str(ch).isdigit() or str(ch) == '*') and index_begin < 0:
                is_good = True
                count += 1
                index_begin = index
                continue
            if is_good:
                if str(ch).isdigit() or str(ch) == '*' or str(ch) == ',' or str(ch) == ' ' or str(ch) == '/' \
                        or str(ch) == '-':
                    count += 1
                    continue
                else:
                    if count >= 5:
                        # logging.info('=====start =====')
                        # logging.info(line[index_begin:index])
                        # logging.info('=====end =====')
                        is_find_schedule_cron = True
                        crontab_config = str(line[index_begin:index]).strip()
                    else:
                        pass
                        # logging.info('=====错误 begin=====')
                        # logging.info(count)
                        # logging.info(index_begin)
                        # logging.info(index)
                        # logging.info(line)
                        # logging.info('====错误 end======')
                    break
    return crontab_config


def get_js_name(line: str) -> str:
    result = None
    if '.js' in line:
        for key in line.split(' '):
            if '.js' in key:
                result = key.split('/')[-1]
    return result


def get_env_name(file: str) -> str:
    result = 'not found'
    if not os.path.isfile(file):
        logging.error("file is not found: " + file)
        return result
    with open(file, 'r', encoding="utf-8") as f:
        for line in f.readlines():
            line = line.strip()

            if "new Env" in line:
                begin_index = line.find('new Env') + 8
                end_index = -1
                for index, ch in enumerate(line):
                    if str(ch) == ')':
                        end_index = index
                # logging.info(line)
                # logging.info(type(begin_index))
                # logging.info(type(end_index))
                # logging.info(begin_index, end_index)
                result = str(line[begin_index:end_index]).replace("'", "").replace("\"", "")
                # logging.info("名字: {}".format(schedule_name))
                is_find_Env = True
            elif "new API" in line:
                begin_index = line.find('new API') + 8
                end_index = -1
                for index, ch in enumerate(line):
                    if str(ch) == ')':
                        end_index = index
                # logging.info(line)
                # logging.info(type(begin_index))
                # logging.info(type(end_index))
                # logging.info(begin_index, end_index)
                result = str(line[begin_index:end_index]).replace("'", "").replace("\"", "")
                # logging.info("名字: {}".format(schedule_name))
                is_find_Env = True
    return result
