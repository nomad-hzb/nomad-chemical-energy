#!/usr/bin/env python3
"""
Created on Thu Jul 17 13:17:46 2025

@author: a2853
"""

import io

import numpy as np
import pandas as pd
import scipy as sc
from baseclasses.chemical_energy import (
    CVProperties,
    EISPropertiesWithData,
    LSVProperties,
    VoltammetryCycleWithPlot,
)
from baseclasses.chemical_energy.electrochemical_impedance_spectroscopy import EISCycle
from baseclasses.helper.utilities import convert_datetime
from nomad.units import ureg


def try_convert_datetime(string_date):
    formats = ['%B %d, %Y   %H:%M:%S%b. %d, %Y   %H:%M:%S']
    for f in formats:
        try:
            return convert_datetime(string_date, f)
        except Exception:
            continue


def parse_chi_txt_file(filedata):
    lines = filedata.splitlines()

    metadata = {
        'datetime': lines[0].strip(),
        'method': lines[1].strip(),
        'instrument_model': lines[4].split(':', 1)[1].strip(),
    }

    for i, line in enumerate(lines):
        if '=' in line:
            key, value = line.split('=', 1)
            metadata[key.strip()] = value.strip()
        if 'Freq/Hz' in line or 'Potential/V' in line:
            break
    data = [lines[i]]
    data.extend(lines[i + 2 :])
    df = pd.read_csv(io.StringIO('\n'.join(data)), sep=None, engine='python')
    df.rename(columns=lambda x: x.strip(), inplace=True)
    return metadata, df


def get_data_from_lsv_txt_file(filedata):
    metadata, data = parse_chi_txt_file(filedata)
    scan_rate = float(metadata['Scan Rate (V/s)'])
    sample_rate = float(metadata['Sample Interval (V)'])
    voltage = data['Potential/V']
    return {
        'station': metadata['instrument_model'],
        'datetime': metadata['datetime'],
        'method': metadata['method'],
        'time': np.linspace(
            0, (len(voltage) - 1) * sample_rate / scan_rate, len(voltage)
        ),
        'current': data['Current/A'],
        'voltage': voltage,
        'scan_rate': scan_rate * ureg('V/s'),
        'p_start': float(metadata['Init E (V)']) * ureg('V'),
        'p_end': float(metadata['Final E (V)']) * ureg('V'),
        'step_size': float(metadata['Sample Interval (V)']) * ureg('V'),
    }


def get_data_from_eis_txt_file(filedata):
    metadata, data = parse_chi_txt_file(filedata)

    return {
        'station': metadata['instrument_model'],
        'datetime': metadata['datetime'],
        'method': metadata['method'],
        'frequency': data['Freq/Hz'],
        'Z_phase': data['Phase/deg'],
        'Z_mod': data['Z/ohm'],
        'Z_real': data["Z'/ohm"],
        'Z_imag': data['Z"/ohm'],
    }


def get_data_from_cv_txt_file(filedata):
    metadata, data = parse_chi_txt_file(filedata)
    return {
        'station': metadata['instrument_model'],
        'datetime': metadata['datetime'],
        'method': metadata['method'],
        'current': data['Current/A'],
        'voltage': data['Potential/V'] * ureg('V'),
        'p_lower': float(metadata['Low E (V)']) * ureg('V'),
        'p_upper': float(metadata['High E (V)']) * ureg('V'),
        'p_start': float(metadata['Init E (V)']) * ureg('V'),
        'scan_rate': float(metadata['Scan Rate (V/s)']) * ureg('V/s'),
    }


def set_chi_data_lsv(entry, d):
    entry.current = d['current']
    entry.station = d['station']
    entry.time = d['time']
    entry.voltage = d['voltage']
    entry.properties = LSVProperties(
        scan_rate=d['scan_rate'],
        step_size=d['step_size'],
        initial_potential=d['p_start'],
        final_potential=d['p_end'],
    )
    if d['datetime']:
        entry.datetime = try_convert_datetime(d['datetime'])


def set_chi_data_cv(entry, d):
    entry.station = d['station']
    if d['datetime']:
        entry.datetime = try_convert_datetime(d['datetime'])
    cycle_indices = (
        [0]
        + list(
            sc.signal.argrelextrema(
                np.abs(np.array(d['voltage']) * ureg('V') - d['p_start']), np.less
            )[0]
        )
        + [None]
    )
    cycles = []
    for i in range(len(cycle_indices) - 1):
        cycles.append(
            VoltammetryCycleWithPlot(
                name=f'Cycle {i}',
                current=d['current'][cycle_indices[i] : cycle_indices[i + 1]].tolist(),
                voltage=d['voltage'][cycle_indices[i] : cycle_indices[i + 1]].tolist(),
            )
        )

    entry.cycles = cycles
    entry.properties = CVProperties(
        initial_potential=d['p_start'],
        limit_potential_1=d['p_upper'],
        limit_potential_2=d['p_lower'],
        scan_rate=d['scan_rate'],
    )


def set_chi_data_eis(entry, d):
    entry.station = d['station']
    entry.measurements = [
        EISPropertiesWithData(
            data=EISCycle(
                frequency=d['frequency'].tolist(),
                z_real=d['Z_real'].tolist(),
                z_imaginary=d['Z_imag'].tolist(),
                z_modulus=d['Z_mod'].tolist(),
                z_angle=d['Z_phase'].tolist(),
            )
        )
    ]
    if d['datetime']:
        entry.datetime = try_convert_datetime(d['datetime'])
