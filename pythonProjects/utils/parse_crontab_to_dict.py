import os

# 0 0 * * * jtask jd_xtg_help
# 0 1,22 * * * jtask jd_gold_creator
# 0 15-19/1 * * * jtask jd_party_night
# 55,1 21-23/1 * * * jtask jd_party_night
# 0-59/30 * * * * jtask jd_zooCollect
FILE_DIR = os.path.dirname(os.path.abspath(__file__))

class parse_crontab:

    def __init__(self):
        pass

    def begin_parse_file(self, crontabl_list_file, script_dir, split_tag=' '):
        assert os.path.isfile(crontabl_list_file)
        assert os.path.isdir(script_dir)

        with open(crontabl_list_file, 'r') as f:
            for line in f.readlines():
                line = line.replace('\n', '')
                if line.startswith('#') or line == '':
                    continue
                print(line)
                print(line.split(split_tag))

if __name__ == '__main__':
    parse = parse_crontab()
    parse.begin_parse_file(os.path.join(FILE_DIR, 'crontab.list'), FILE_DIR, split_tag='otask')
