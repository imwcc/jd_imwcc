import os
import sys
import logging
import configparser

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(os.path.dirname(FILE_DIR)))
# sys.path.append("..")
# from utils import sendNotify

logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.DEBUG)
logging.info(FILE_DIR)

class ConfigurationManager(object):

    def __init__(self, cfg_file):
        if not os.path.isfile(cfg_file):
            logging.error(cfg_file + "不存在")
            return -1

        config = configparser.ConfigParser()
        config.read(os.path.join(cfg_file))
        self.__config = config
        self.__CONFIG_KEY = 'CONFIG'
        self.__EXCLUDE_KEY = 'EXCLUDE'

    def set_debug(self, debug: bool):
        if debug:
            self.__CONFIG_KEY = 'DEBUG_CONFIG'

    def get_config_host_name(self) -> str:
        key = str(sys._getframe().f_code.co_name).replace('get_config_', '')
        return self.__config.get(self.__CONFIG_KEY, key).replace('\n', '')

    def get_config_script_name(self) -> str:
        key = str(sys._getframe().f_code.co_name).replace('get_config_', '')
        return self.__config.get(self.__CONFIG_KEY, key).replace('\n', '')

    def get_config_root_dir(self) -> str:
        key = str(sys._getframe().f_code.co_name).replace('get_config_', '')
        return self.__config.get(self.__CONFIG_KEY, key).replace('\n', '')

    # 检查js 是否包含 cron
    def get_config_check_cron_is_in_js(self) -> bool:
        key = str(sys._getframe().f_code.co_name).replace('get_config_', '')
        return self.__config.get(self.__CONFIG_KEY, key).lower() == 'true'

    def get_exclude_js_exclude_files(self) -> list:
        key = str(sys._getframe().f_code.co_name).replace('get_exclude_', '')
        values = self.__config.get(self.__EXCLUDE_KEY, key).replace('\n', '').replace(' ', '')
        if ';' in values:
            return values.split(';')
        return values.split(',')

    def get_exclude_js_white_files(self) -> list:
        key = str(sys._getframe().f_code.co_name).replace('get_exclude_', '')
        values = self.__config.get(self.__EXCLUDE_KEY, key).replace('\n', '').replace(' ', '')
        if ';' in values:
            return values.split(';')
        return values.split(',')

    def get_exclude_yaml_exclude_files(self) -> list:
        key = str(sys._getframe().f_code.co_name).replace('get_exclude_', '')
        values = self.__config.get(self.__EXCLUDE_KEY, key).replace('\n', '').replace(' ', '')
        if ';' in values:
            return values.split(';')
        return values.split(',')


if __name__ == '__main__':
    cfg_file = os.path.join(FILE_DIR, 'configuration_template.cfg')
    configurationManager = ConfigurationManager(cfg_file)
    print(configurationManager.get_config_host_name())
    assert configurationManager.get_config_host_name() == 'host_name', configurationManager.get_config_host_name()
    print(configurationManager.get_config_script_name())
    assert configurationManager.get_config_script_name() == 'script_name', configurationManager.get_config_host_name()
    print(configurationManager.get_config_root_dir())
    assert configurationManager.get_config_root_dir() == 'root_dir', configurationManager.get_config_host_name()
    print(configurationManager.get_config_check_cron_is_in_js())
    assert type(configurationManager.get_config_check_cron_is_in_js()) == bool
    print(configurationManager.get_exclude_js_exclude_files())
    assert len(configurationManager.get_exclude_js_exclude_files()) > 0
    print(configurationManager.get_exclude_js_white_files())
    assert len(configurationManager.get_exclude_js_white_files()) > 0
    print(configurationManager.get_exclude_yaml_exclude_files())
    assert configurationManager.get_exclude_yaml_exclude_files()

    configurationManager.set_debug(True)
    print(configurationManager.get_config_host_name())
    assert 'debug' in configurationManager.get_config_host_name(), configurationManager.get_config_host_name()
    assert 'debug' in configurationManager.get_config_host_name(), configurationManager.get_config_host_name()
    print(configurationManager.get_config_script_name())
    assert 'debug' in configurationManager.get_config_script_name(), configurationManager.get_config_host_name()
    print(configurationManager.get_config_root_dir())
    assert 'debug' in configurationManager.get_config_root_dir(), configurationManager.get_config_host_name()

