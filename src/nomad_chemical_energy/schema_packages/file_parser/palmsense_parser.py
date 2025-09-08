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

import json

import numpy as np
from baseclasses.chemical_energy.electrochemical_impedance_spectroscopy import (
    EISCycle,
    EISPropertiesWithData,
)
from baseclasses.chemical_energy.voltammetry import VoltammetryCycle
from nomad.units import ureg


def get_data_from_pssession_file(filedata):
    d = json.loads(filedata[:-1])
    return d


def map_voltammetry_curve_data(entry, dataset):
    if dataset['DataValueType'] == 'PalmSens.Data.VoltageReading':
        entry.voltage = np.array([dv['V'] for dv in dataset['DataValues']]) * ureg(
            dataset['Unit']['Type'].split('.')[-1].lower()
        )
    if dataset['DataValueType'] == 'PalmSens.Data.CurrentReading':
        entry.current = np.array([dv['V'] for dv in dataset['DataValues']]) * ureg(
            dataset['Unit']['Type'].split('.')[-1].lower()
        )
    if dataset['Type'] == 'PalmSens.Data.DataArrayTime':
        entry.time = np.array([dv['V'] for dv in dataset['DataValues']]) * ureg(
            dataset['Unit']['S']
        )
    if dataset['Type'] == 'PalmSens.Data.DataArrayCharge':
        entry.charge = np.array([dv['V'] for dv in dataset['DataValues']]) * ureg(
            dataset['Unit']['Type'].split('.')[-1].lower()
        )


def map_voltammetry_curve(entry, datasets):
    # for dataset in d["Measurements"][0]["DataSet"]["Values"]:
    for dataset in datasets:
        map_voltammetry_curve_data(entry, dataset)


def map_voltammetry_data(entry, data):
    datasets = data['Measurements'][0]['DataSet']['Values']
    multiple_measurements = any(['scan' in s['Description'] for s in datasets])
    if not multiple_measurements:
        map_voltammetry_curve(entry, datasets)
    else:
        cycles_sorted = {}
        time = None
        for dataset in datasets:
            if 'time' in dataset['Description']:
                time = dataset
        for dataset in datasets:
            if 'scan' not in dataset['Description']:
                continue
            if dataset['Description'] not in cycles_sorted:
                cycles_sorted[dataset['Description']] = [time]
            cycles_sorted[dataset['Description']].append(dataset)

        cycles = []
        for dataset in cycles_sorted.values():
            cycle_entry = VoltammetryCycle()
            map_voltammetry_curve(cycle_entry, dataset)
            cycles.append(cycle_entry)
        entry.cycles = cycles


def map_eis_data(entry, data):
    datasets = data['Measurements'][0]['DataSet']['Values']
    eis_cycle = EISCycle()

    for dataset in datasets:
        # if dataset['Type'] == 'PalmSens.Data.DataArrayTime':
        #     eis_cycle.time = np.array([dv['V'] for dv in dataset['DataValues']]) * ureg(
        #         dataset['Unit']['S']
        #     )
        if dataset['Description'] == 'Frequency':
            eis_cycle.frequency = np.array(
                [dv['V'] for dv in dataset['DataValues']]
            ) * ureg(dataset['Unit']['S'])
        if dataset['Description'] == 'ZRe':
            eis_cycle.z_real = np.array(
                [dv['V'] for dv in dataset['DataValues']]
            ) * ureg('ohm')
        if dataset['Description'] == 'ZIm':
            eis_cycle.z_imaginary = np.array(
                [dv['V'] for dv in dataset['DataValues']]
            ) * ureg('ohm')
        if dataset['Description'] == 'Z':
            eis_cycle.z_modulus = np.array(
                [dv['V'] for dv in dataset['DataValues']]
            ) * ureg('ohm')
        if dataset['Description'] == 'Phase':
            eis_cycle.z_angle = np.array(
                [dv['V'] for dv in dataset['DataValues']]
            ) * ureg(dataset['Unit']['S'])

    entry.measurements = [EISPropertiesWithData(data=eis_cycle)]


# def get_encoding(file_obj):
#     return chardet.detect(file_obj.read())['encoding']


# file = "/home/a2853/Downloads/palmense_data/03_IR Drop N2.pssession"


# with open(file, "br") as f:
#     encoding = get_encoding(f)

# with open(file, "r", encoding=encoding) as f:
#     fd = f.read()
#     d = get_data_from_pssession_file(fd)
#     print(d["Measurements"][0]["Title"], d['Measurements'][0]['DataSet']['Values'])
