from io import StringIO

import pandas as pd


def getHeader(file_data):
    file_lines = file_data.split('\n')
    header = 0
    date_line_found = False
    date_line = None
    for i, line in enumerate(file_lines):
        if line.startswith('#D') and not date_line_found:
            date_line_found = True
            date_line = line
        if line.startswith('#'):
            continue
        header = i - 1
        break
    return header, date_line.strip()


def get_xas_data(file_obj):
    file_data = file_obj.read()
    header, dateline = getHeader(file_data)
    data = pd.read_csv(StringIO(file_data), header=header, sep='\t')
    return data, dateline
