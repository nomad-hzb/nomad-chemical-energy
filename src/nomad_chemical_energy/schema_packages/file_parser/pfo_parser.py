from io import StringIO

import pandas as pd


def get_pfo_measurement_csv(file_obj):
    file_data = file_obj.read()
    lookup = '"Date [mm/dd/yyyy]";'
    for num, line in enumerate(file_data.split("\n")):
        if lookup in line:
            break
    data = pd.read_csv(StringIO(file_data), sep=";",
                       header=num, skip_blank_lines=False)
    return data


def get_pfo_measurement_xlsx(file_obj):
    dfs = pd.read_excel(file_obj, sheet_name=None)
    for key, df in dfs.items():
        if 'Oxygen Concentration' in df.columns:
            return df
