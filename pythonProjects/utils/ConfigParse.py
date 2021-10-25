# 解析单个脚本库配置信息
import os
import configparser
import socket
import sys

class ConfigParse:
    support_config_names = ['EXCLUDE', 'CONFIG']

    CONFIG_EXCLUDE_NAME = support_config_names[0]

    def __init__(self, file, debug=False):
        assert os.path.isfile(file)
        self.config = configparser.ConfigParser()
        self.config.read(file)
        self.debug = debug

        if self.debug:
            self.config_attr = "DEBUG_{}".format(ConfigParse.support_config_names[1])
            self.config_exclude_attr = "{}".format(ConfigParse.support_config_names[0])
        else:
            self.config_attr = ConfigParse.support_config_names[1]
            self.config_exclude_attr = ConfigParse.support_config_names[0]

    def get_config_host_name(self):
        attr = str(sys._getframe().f_code.co_name).replace('get_config_', '')
        return self.config.get(self.config_attr, attr).replace('\n', '').replace(' ', '')

    def get_config_script_name(self):
        attr = str(sys._getframe().f_code.co_name).replace('get_config_', '')
        return self.config.get(self.config_attr, attr).replace('\n', '').replace(' ', '')

    def get_config_root_dir(self):
        attr = str(sys._getframe().f_code.co_name).replace('get_config_', '')
        return self.config.get(self.config_attr, attr).replace('\n', '').replace(' ', '')

    def get_exclude_js_exclude_files(self):
        attr = str(sys._getframe().f_code.co_name).replace('get_exclude_', '')
        return self.config.get(self.config_exclude_attr, attr).replace('\n', '').replace(' ', '').split(',')

    def get_exclude_js_white_files(self):
        attr = str(sys._getframe().f_code.co_name).replace('get_exclude_', '')
        return self.config.get(self.config_exclude_attr, attr).replace('\n', '').replace(' ', '').split(',')

    def get_exclude_yaml_exclude_files(self):
        attr = str(sys._getframe().f_code.co_name).replace('get_exclude_', '')
        return self.config.get(self.config_exclude_attr, attr).replace('\n', '').replace(' ', '').split(',')


if __name__ == '__main__':
    FILE_DIR = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(os.path.join(os.path.dirname(FILE_DIR)))
    HOST_NAME = socket.gethostname()
    DEBUG = 'jd-arvin' not in HOST_NAME


    configParser = ConfigParse(os.path.join(FILE_DIR, 'test', 'sample_exclude.cfg'))

    expect_list = ['1.js', '2.js', '3.js']
    actual_list = configParser.get_exclude_js_exclude_files()

    assert len(expect_list) == len(actual_list)
    for i in actual_list:
        assert i in expect_list

    expect_list = ['4.js', '5.js', '7.js']
    actual_list = configParser.get_exclude_js_white_files()

    assert len(expect_list) == len(actual_list)
    for i in actual_list:
        assert i in expect_list

    expect_list = ['9.yaml', '10.yaml']
    actual_list = configParser.get_exclude_yaml_exclude_files()
    assert len(expect_list) == len(actual_list)
    for i in actual_list:
        assert i in expect_list

    assert configParser.get_config_host_name() == 'config_host_name'
    assert configParser.get_config_script_name() == 'config_script_name'
    assert configParser.get_config_root_dir() == 'config_ROOT_DIR'

    configParser = ConfigParse(os.path.join(FILE_DIR, 'test', 'sample_exclude.cfg'), debug=True)
    assert configParser.get_config_host_name() == 'debug_HOST_NAME'
    assert configParser.get_config_script_name() == 'debug_script_name'
    assert configParser.get_config_root_dir() == 'debug_ROOT_DIR'
