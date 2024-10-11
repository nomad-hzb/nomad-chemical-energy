import pandas as pd
import numpy as np


def to_float(value):
    try:
        return float(value)
    except:
        return value


def parse_spectrum(f):
    metadata = {}
    while True:
        line = f.readline()

        if "Scan Data" in line:
            break

        if "\t" not in line or len(line.strip().strip("\t").split("\t")) != 2:
            continue

        key,  value = line.split("\t")
        metadata.update({key.strip().strip('"'):  to_float(value.strip().strip('"'))})

    data = pd.read_csv(f, sep="\t", header=0, on_bad_lines="skip")
    data.Time = pd.to_datetime(data.Time, errors="coerce")
    data = data[pd.notnull(data.Time)]
    data[data == "Skipped"] = np.nan
    return metadata, data


# file = "ce-nome/frederik/CE-NOME_FrJo_240815_0001.0 H2O Au000001.txt"
# m, d = parse_spectrum(file)
