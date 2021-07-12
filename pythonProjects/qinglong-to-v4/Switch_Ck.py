import os

FILE_DIR = os.path.dirname(os.path.abspath(__file__))

if __name__ == '__main__':
    result = []
    with open(os.path.join(FILE_DIR, 'source.txt'), 'r') as f:
        count = 1
        for line in f.readlines():
            line = line.strip().replace('\n', '')
            out = "Cookie{}=\"{}\"".format(count,line)
            count += 1
            result.append(out)
            # print(line)
    with open(os.path.join(FILE_DIR, 'cookie.sh'), 'w') as f:
        for line in result:
            f.writelines(line+'\n')
