from watchdog.observers import Observer
from watchdog.events import *
import time
import configparser
import logging

from watchdog.events import FileSystemEventHandler

logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.DEBUG)

observer_files_cfg = os.getenv('observer_files_cfg').replace('\n', '').replace(' ', '')
assert os.path.isfile(observer_files_cfg)

config = configparser.ConfigParser()
config.read(observer_files_cfg)

observer_files = []
children_container_paths = []
qinglong_target_path = None
for key in config['CONFIG']:
    if key == 'observer_files':
        for file in config.get('CONFIG', key).replace('\n', '').replace(' ', '').split(';'):
            if os.path.isfile(file):
                observer_files.append(file)
            else:
                logging.error(f"{file} 不存在")
    elif key == 'qinglong_target_path':
        qinglong_target_path = config.get('CONFIG', key).replace('\n', '').replace(' ', '')

    elif key == 'children_container_paths':
        for file in config.get('CONFIG', key).replace('\n', '').replace(' ', '').split(';'):
            if os.path.isfile(file) or os.path.isdir(file):
                children_container_paths.append(file)
            else:
                logging.error(f"{file} 不存在")
    else:
        logging.error("不支持的 key ".format(key))

assert os.path.isfile(qinglong_target_path) or os.path.isdir(qinglong_target_path)


class FileEventHandler(FileSystemEventHandler):
    def __init__(self):
        FileSystemEventHandler.__init__(self)

    def on_moved(self, event):
        if event.is_directory:
            print("directory moved from {0} to {1}".format(event.src_path, event.dest_path))
        else:
            print("file moved from {0} to {1}".format(event.src_path, event.dest_path))

    def on_created(self, event):
        if event.is_directory:
            print("directory created:{0}".format(event.src_path))
        else:
            print("file created:{0}".format(event.src_path))

    def on_deleted(self, event):
        if event.is_directory:
            print("directory deleted:{0}".format(event.src_path))
        else:
            print("file deleted:{0}".format(event.src_path))

    def on_modified(self, event):
        if event.is_directory:
            print("directory modified:{0}".format(event.src_path))
        else:
            print("file modified:{0}".format(event.src_path))
            if 'qinglong' in event.src_path:

                cmd = f'cp -f {event.src_path} {qinglong_target_path}'
                logging.info(f'run {cmd}')
                os.system(cmd)
            else:
                for target_path in children_container_paths:
                    cmd = f'cp -f {event.src_path} {target_path}'
                    logging.info(f'run {cmd}')
                    os.system(cmd)


if __name__ == "__main__":
    observer = Observer()
    event_handler = FileEventHandler()
    for file in observer_files:
        observer.schedule(event_handler, file, True)
    observer.start()
    try:
        while True:
            time.sleep(600)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
