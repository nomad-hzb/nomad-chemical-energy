from io import StringIO

import pandas as pd


def getHeader(file_data):
    file_lines = file_data.split('\n')
    header = 0
    date_line_found = False
    date_line = None
    for i, line in enumerate(file_lines):
        if not date_line_found and (line.startswith('#D') or line.startswith('# start_time:')):
            date_line_found = True
            date_line = line
        if line.startswith('#'):
            continue
        header = i - 1
        break
    return header, date_line.strip()


def get_xas_data(file_obj, header=None, dateline=None):
    file_data = file_obj.read()
    if header is None:
        header, dateline = getHeader(file_data)
        lines = file_data.splitlines()
        if header:
            lines[header] = lines[header].lstrip("# ").rstrip()
        data = pd.read_csv(StringIO("\n".join(lines)), header=header, sep=r'\s+', engine='python')
        multi_channel_cols = ['fluo', 'ICR', 'OCR', 'TLT', 'LT', 'RT']
        data.rename(columns={col: f"{col}.0" for col in multi_channel_cols if col in data.columns}, inplace=True)
    else:
        file_data = file_data.replace('\t\n', '\n')
        data = pd.read_csv(StringIO(file_data), names=header, sep='\t')
    return data, dateline
