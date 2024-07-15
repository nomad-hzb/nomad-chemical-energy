import pandas as pd


def to_float(value):
    try:
        return float(value)
    except:
        return value


def parse_spectrum(file):
    metadata = {}
    with open(file, "r") as f:
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
    return metadata, data[pd.notnull(data.Time)]


# file = "ce-nome/frederik/test double PTFETape 3 100724000001.txt"
# m, d = parse_spectrum(file)
