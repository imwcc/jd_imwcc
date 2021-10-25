import os.path
import socket
import logging

HOST_NAME = socket.gethostname()

UN_DEFINE = "not found"

default_time_config = "0 3 * * *"

def is_docker_server(host_name=HOST_NAME):
    return host_name == 'jd-arvin'


def get_host_name():
    return HOST_NAME


def get_file_name_from_dict(full_dict):
    return full_dict['file_name']


def get_full_crontab_dic(file: str):
    result = UN_DEFINE
    if not os.path.isfile(file):
        logging.error("file is not found: " + file)
        return result
    env_name = get_env_name(file)
    if env_name == UN_DEFINE:
        logging.error("没有找到 Env Name: " + file)
        return result
    crontab_config = get_crontab_from_file(file)
    if crontab_config == UN_DEFINE:
        logging.warning("crontab_config is not, use defult time confrig for: " + file)
        crontab_config = default_time_config
    file_name = os.path.basename(file)
    script_file = file
    temp_dic = {}
    temp_dic['name'] = env_name
    temp_dic['file_name'] = file_name
    temp_dic['schedule_cron'] = crontab_config
    temp_dic['script_file'] = script_file
    return temp_dic


def get_crontab_from_file(file: str) -> str:
    result = UN_DEFINE
    if not os.path.isfile(file):
        logging.error("file is not found: " + file)
        return result
    with open(file, 'r', encoding="utf-8") as f:
        for line in f.readlines():
            line = line.strip()
            crontab_config = get_crontab_from_line(line)
            if crontab_config is None:
                continue
            else:
                result = crontab_config
                break
    return result


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

    elif '.py' in line and '*' in line:
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


def get_py_name(line: str) -> str:
    result = None
    if '.py' in line:
        for key in line.split(' '):
            if '.py' in key:
                result = key.split('/')[-1]
    return result


def get_env_name_from_str(line: str):
    result = UN_DEFINE
    is_find_Env = False
    line = line.strip()
    if "new Env" in line:
        begin_index = line.find('new Env') + 8
        end_index = -1
        for index, ch in enumerate(line):
            if str(ch) == ')':
                end_index = index
                break
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
                break
        # logging.info(line)
        # logging.info(type(begin_index))
        # logging.info(type(end_index))
        # logging.info(begin_index, end_index)
        result = str(line[begin_index:end_index]).replace("'", "").replace("\"", "")
        # logging.info("名字: {}".format(schedule_name))
        is_find_Env = True

    elif "common.env" in line:
        begin_index = line.find('common.env') + len("common.env") + 1
        end_index = -1
        for index, ch in enumerate(line):
            if str(ch) == ')':
                end_index = index
                break
        # logging.info(line)
        # logging.info(type(begin_index))
        # logging.info(type(end_index))
        # logging.info(begin_index, end_index)
        result = str(line[begin_index:end_index]).replace("'", "").replace("\"", "")
        # logging.info("名字: {}".format(schedule_name))
        is_find_Env = True

    if not is_find_Env:
        line = line.replace(' ', '')
        local_found = line.find('$=Env') >= 0
        if local_found:
            begin_index = line.find('$=Env') + len("$=Env") + 1
            end_index = -1
            for index, ch in enumerate(line):
                if str(ch) == ')':
                    end_index = index
                    break
            # logging.info(line)
            # logging.info(type(begin_index))
            # logging.info(type(end_index))
            # logging.info(begin_index, end_index)
            result = str(line[begin_index:end_index]).replace("'", "").replace("\"", "")
            # logging.info("名字: {}".format(schedule_name))
            is_find_Env = True

    return is_find_Env, result


def get_env_name(file: str) -> str:
    result = UN_DEFINE
    if not os.path.isfile(file):
        logging.error("file is not found: " + file)
        return result
    with open(file, 'r', encoding="utf-8") as f:
        for line in f.readlines():
            line = line.strip()
            is_find_Env, env_result = get_env_name_from_str(line)
            if is_find_Env:
                result = env_result
                break
    return result


# 替换文件中匹配字符串
def replace_file_str(target_file, source: str, target: str):
    assert os.path.isfile(target_file)
    cache_file = []
    count = 0
    with open(target_file, mode='r', encoding='utf-8') as f:
        for line in f.readlines():
            old = line
            line = line.replace(source, target)
            if line != old:
                logging.info("replace: \"{}\" to \"{}\"".format(old, line).replace('\n', ''))
                count += 1
            cache_file.append(line)
    logging.info("replace count: {}".format(count))
    with open(target_file, mode='w', encoding='utf-8') as f:
        f.write(''.join(cache_file))


def replace_file_line(target_file, source: str, target: str):
    assert os.path.isfile(target_file)
    cache_file = []
    count = 0
    with open(target_file, mode='r', encoding='utf-8') as f:
        for line in f.readlines():
            old = line
            if source in line:
                line = target
            if line != old:
                logging.info("replace: \"{}\" to \"{}\"".format(old, line).replace('\n', ''))
                count += 1
            cache_file.append(line)
    logging.info("replace count: {}".format(count))
    with open(target_file, mode='w', encoding='utf-8') as f:
        f.write(''.join(cache_file))
