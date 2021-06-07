import configparser
import logging
import os

import yaml

logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.DEBUG)

FILE_DIR = os.path.dirname(os.path.abspath(__file__))

DEBUG = True


class parse_yaml(object):
    def __init__(self):
        pass

    def begin_parse_file(self, source_yaml, script_dir):
        # logging.info("begin_parse_file")
        assert os.path.isfile(source_yaml)
        assert os.path.isdir(script_dir)

        source_yaml_file_name = str(source_yaml).strip().split('/')[-1]
        result_dic = {}

        with open(source_yaml, 'r', encoding="utf-8") as fp:
            result = fp.read()
            yaml_result = yaml.load(result, Loader=yaml.SafeLoader)
            try:
                schedule_name = yaml_result.get('name')

                if yaml_result.get(True).get('schedule') is None:
                    logging.warning("{} 没有schedule".format(source_yaml))
                schedule_time = yaml_result.get(True).get('schedule')[0].get('cron')

                for step in yaml_result.get('jobs').get('build').get('steps'):
                    step = step.get('run')
                    if 'node' in str(step) and '.js' in step:
                        jsname = str(step).replace('\n', '').split('node')[1].strip().split('/')[-1]

                if '.js' not in jsname:
                    raise ValueError('{} 没有找到js文件名称'.format(yaml_result.get('jobs').get('build').get('steps')))

                if jsname != '':
                    result_dic['name'] = schedule_name
                    result_dic['schedule_cron'] = schedule_time
                    result_dic['file_name'] = jsname

                    result_dic['script_dir'] = script_dir
                    result_dic['script_file'] = os.path.join(script_dir, jsname)
                    result_dic['yaml_file_name'] = source_yaml_file_name

            except Exception as e:
                logging.error(source_yaml)
                logging.error(str(e))

            return result_dic

        def begin_parse_file(self, source_yaml, script_dir):
            # logging.info("begin_parse_file")
            assert os.path.isfile(source_yaml)
            assert os.path.isdir(script_dir)

            source_yaml_file_name = str(source_yaml).strip().split('/')[-1]
            result_dic = {}


    def begin_parse_myactions_file(self, source_yaml, script_dir):
        # logging.info("begin_parse_file")
        assert os.path.isfile(source_yaml)
        assert os.path.isdir(script_dir)

        source_yaml_file_name = str(source_yaml).strip().split('/')[-1]
        result_dic = {}

        with open(source_yaml, 'r', encoding="utf-8") as fp:
            result = fp.read()
            yaml_result = yaml.load(result, Loader=yaml.SafeLoader)
            try:
                schedule_name = yaml_result.get('name')

                if yaml_result.get(True).get('schedule') is None:
                    logging.warning("{} 没有schedule".format(source_yaml))
                schedule_time = yaml_result.get(True).get('schedule')[0].get('cron')

                for step in yaml_result.get('jobs').get('build').get('steps'):
                    run_step = step.get('run')
                    if 'node' in str(run_step) and '.js' in run_step:
                        jsname = str(step.get('env').get('SYNCURL')).strip().split('/')[-1]
                        # jsname = str(step).replace('\n', '').split('node')[1]

                if '.js' not in jsname:
                    raise ValueError('{} 没有找到js文件名称'.format(yaml_result.get('jobs').get('build').get('steps')))

                if jsname != '':
                    result_dic['name'] = schedule_name
                    result_dic['schedule_cron'] = schedule_time
                    result_dic['file_name'] = jsname

                    result_dic['script_dir'] = script_dir
                    result_dic['script_file'] = os.path.join(script_dir, jsname)
                    result_dic['yaml_file_name'] = source_yaml_file_name

            except Exception as e:
                logging.error(source_yaml)
                logging.error(str(e))

            return result_dic


