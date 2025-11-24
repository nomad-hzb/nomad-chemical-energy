# MIT License

# Copyright (c) 2019

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import locale
import re
from io import StringIO

import pandas as pd
from pandas.api.types import is_numeric_dtype


def _read_curve_data(fid, curve_length) -> tuple:
    """helper function to process an EXPLAIN Table
    Args:
        fid (int): a file handle pointer to the table position in the
        data files
    Returns:
        keys (list): column identifier (e.g. Vf)
        units (list): column unit type (e.g. V)
        curve (DataFrame): Table data saved as a pandas Dataframe
    """
    pos = 0
    curve = fid.readline().strip() + '\n'  # grab header data
    if len(curve) <= 1 or 'CURVE' in curve:
        return [], [], pd.DataFrame()

    units = fid.readline().strip().split('\t')
    cur_line = fid.readline().strip()
    line_count = 0
    while not re.search(r'(CURVE|EXPERIMENTABORTED)', cur_line):
        line_count += 1
        curve += cur_line + '\n'
        if curve_length is not None and curve_length == line_count:
            break
        pos = fid.tell()
        cur_line = fid.readline().strip()
        if fid.tell() == pos:
            break
    if 'CURVE' in cur_line:
        fid.seek(pos)  # jump back to CURVE line
    try:
        curve = pd.read_csv(StringIO(curve), delimiter='\t', header=0, index_col=0)
    except Exception:
        curve = pd.read_csv(
            StringIO(curve), delimiter='\t', header=0, index_col=0, decimal=','
        )

    keys = curve.columns.values.tolist()
    units = units[1:]

    return keys, units, curve


def get_number(value_str):
    if ',' in value_str:
        return get_number(value_str.replace(',', '.'))
    try:
        return locale.atof(value_str)
    except Exception:
        return value_str


def get_curve(f, _header, _curve_units, curve_length=None):
    curve_keys, curve_units, curve = _read_curve_data(f, curve_length)
    dict(CV=dict(Vf='V vs. Ref.', Im='A'))
    if curve.empty:
        return None

    for key in curve_keys:
        nonnumeric_keys = [
            'Over',
        ]
        if key in nonnumeric_keys:
            continue
        elif key == 'Pt':
            if not is_numeric_dtype(curve.index):
                curve.index = curve.index.map(int)
        elif not is_numeric_dtype(curve[key]):
            try:
                curve[key] = curve[key].map(locale.atof)
            except Exception:
                curve[key] = curve[key].apply(lambda x: x.replace(',', '.'))
                curve[key] = curve[key].map(locale.atof)

    return curve


def check_is_number(key, input_string):
    if key in [
        'NICK',
        'PSTATSERIALNO',
        'PSTATSECTION',
        'SAMPLEID',
        'ENVIRONMENTID',
        'ECSETUPID',
        'DCCALDATE',
        'ACCALDATE',
    ]:
        return input_string
    try:
        return float(input_string)
    except Exception:
        return input_string


def get_header_and_data(f):
    _header = dict()
    _curve_units = dict()
    _curves = {}

    pos = 0
    f.readline().split('\t')  # consumes first line ('EXPLAIN')
    while True:
        if f.tell() == pos:
            break
        pos = f.tell()
        cur_line = f.readline().strip().split('\t')
        if len(cur_line[0]) == 0:
            pass

        if len(cur_line) > 1:
            if 'CURVE' in cur_line[0] and len(cur_line) > 2:
                table_length = get_number(cur_line[2])
                _curves[cur_line[0]] = [
                    get_curve(f, _header, _curve_units, table_length)
                ]
            elif 'CURVE' in cur_line[0]:
                curve_method = ''.join(x for x in cur_line[0] if not x.isdigit())
                curves = []
                while True:
                    curve_start_pos = f.tell()
                    cur_line = f.readline().strip().split('\t')
                    if 'CURVE' in cur_line[0]:
                        if curve_method != ''.join(
                            x for x in cur_line[0] if not x.isdigit()
                        ):
                            # new curve method should not be appended
                            f.seek(curve_start_pos)
                            break
                    else:
                        # if we consumed header of curve table we should jump back
                        f.seek(curve_start_pos)
                    curve = get_curve(f, _header, _curve_units)
                    if curve is None:
                        break
                    curves.append(curve)
                _curves[curve_method] = curves
            if len(cur_line) < 2:
                break
            # data format: key, type, value
            if cur_line[0].strip() in ['METHOD']:
                _header[cur_line[0]] = cur_line[1]
            if cur_line[1].strip() in ['LABEL', 'PSTAT']:
                _header[cur_line[0]] = (
                    check_is_number(cur_line[0], cur_line[2])
                    if len(cur_line) > 2
                    else ''
                )
                if cur_line[0] in ['TITLE'] and len(cur_line) > 3:
                    _header['SAMPLE_ID'] = cur_line[3]
            elif cur_line[1] in ['POTEN'] and len(cur_line) == 5:
                tmp_value = get_number(cur_line[2])
                _header[cur_line[0]] = (tmp_value, cur_line[3] == 'T')

            elif cur_line[1] in ['QUANT', 'IQUANT', 'POTEN']:
                # locale-friendly alternative to float
                _header[cur_line[0]] = get_number(cur_line[2])
            elif cur_line[1] in ['IQUANT', 'SELECTOR']:
                _header[cur_line[0]] = int(cur_line[2])
            elif cur_line[1] in ['TOGGLE']:
                _header[cur_line[0]] = cur_line[2] == 'T'
            elif cur_line[1] in ['ONEPARAM']:
                tmp_value = get_number(cur_line[3])
                _header[cur_line[0]] = (tmp_value, cur_line[2] == 'T')
            elif cur_line[1] == 'TWOPARAM':
                tmp_start = get_number(cur_line[3])
                tmp_finish = get_number(cur_line[4])
                _header[cur_line[0]] = {
                    'enable': cur_line[2] == 'T',
                    # locale-friendly alternative to float
                    'start': tmp_start,
                    # locale-friendly alternative to float
                    'finish': tmp_finish,
                }
            elif cur_line[0] == 'TAG':
                _header['TAG'] = cur_line[1]
            elif cur_line[0] == 'NOTES':
                n_notes = int(cur_line[2])
                note = ''
                for _ in range(n_notes):
                    note += f.readline().strip() + '\n'
                _header[cur_line[0]] = note

    f.tell()

    return _header, _curves
