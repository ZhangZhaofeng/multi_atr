
import time

from pathlib import Path


def print_and_write(a_string, filename = './autotrading_log'):
    print(a_string)

    time_str = time.strftime('%Y-%m-%d %H:%M:%S')
    log_file = Path(filename)
    if log_file.is_file():
        with open(filename, 'a') as lf:
            lf.write('%s @ %s \n' % (a_string, time_str))
    else:
        with open(filename, 'w') as lf:
            lf.write('%s @ %s \n' % (a_string, time_str))


