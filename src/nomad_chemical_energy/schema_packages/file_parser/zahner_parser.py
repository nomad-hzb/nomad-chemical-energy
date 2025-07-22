#!/usr/bin/env python3
"""
Created on Thu Jul 17 13:17:46 2025

@author: a2853
"""

import numpy as np
from baseclasses.chemical_energy.cyclicvoltammetry import CVProperties
from baseclasses.chemical_energy.electrochemical_impedance_spectroscopy import (
    EISCycle,
    EISPropertiesWithData,
)
from baseclasses.chemical_energy.voltammetry import (
    VoltammetryCycleWithPlot,
)
from baseclasses.helper.utilities import convert_datetime
from zahner_analysis.file_import.isc_import import IscImport
from zahner_analysis.file_import.ism_import import IsmImport
from zahner_analysis.file_import.isw_import import IswImport


def parse_metadata(filedata):
    lines = filedata.split('\n')

    datetime = lines[4].split(':', 1)[1] + ' ' + lines[6][:8]
    method = None
    if '-cp-' in lines[-1].lower():
        method = 'cp'
    elif '-ca-' in lines[-1].lower():
        method = 'ca'
    return datetime.strip(), method


def determine_method_isw(t, c, v):
    fit_c = np.polyfit(t, c, 1, full=True)
    fit_v = np.polyfit(t, v, 1, full=True)

    if abs(fit_c[0][0]) < 1e-12 and fit_c[1] < fit_v[1]:
        return 'cp'

    if abs(fit_v[0][0]) < 1e-12 and fit_v[1] < fit_c[1]:
        return 'ca'

    if fit_c[1] < fit_v[1]:
        return 'gds'

    if fit_v[1] < fit_c[1]:
        return 'lsv'


def get_data_from_isw_file(filedata, filemetadata=None):
    isw_file = IswImport(filedata)
    datetime, method = parse_metadata(filemetadata) if filemetadata else (None, None)

    t = isw_file.getTimeArray()
    c = isw_file.getCurrentArray()
    v = isw_file.getVoltageArray()
    if not method:
        method = determine_method_isw(t, c, v)

    return {
        'datetime': datetime,
        'method': method,
        'time': t,
        'current': c * 1000,
        'voltage': v,
    }


def determine_method_ism(c, v):
    t = np.arange(len(c))
    fit_c = np.polyfit(t, c, 0, full=True)
    fit_v = np.polyfit(t, v, 0, full=True)

    if fit_c[1] < fit_v[1]:
        return 'geis'

    if fit_v[1] < fit_c[1]:
        return 'peis'


def get_data_from_ism_file(filedata):
    ism_file = IsmImport(filedata)
    phase = ism_file.getPhaseArray()
    imp_mod = ism_file.getImpedanceArray()

    imp = imp_mod * np.exp(1j * phase)
    freq = ism_file.getFrequencyArray()
    datetime = ism_file.getMeasurementDateTimeArray()
    current = ism_file.getTrack('Current/A')
    voltage = ism_file.getTrack('Voltage/V')
    method = determine_method_ism(current, voltage)
    time = (
        ism_file.getMeasurementDateTimeArray()
        - ism_file.getMeasurementDateTimeArray()[-1]
    )
    return {
        'time': np.array([t.total_seconds() for t in time]),
        'datetime': datetime[0],
        'method': method,
        'frequency': freq,
        'Z_phase': phase,
        'Z_mod': imp_mod,
        'Z_real': np.real(imp),
        'Z_imag': np.imag(imp),
    }


def get_data_from_isc_file(filedata):
    isc_file = IscImport(filedata)

    return {
        'datetime': isc_file.getMeasurementStartDateTime(),
        'time': isc_file.getTimeArray(),
        'voltage': isc_file.getVoltageArray(),
        'current': isc_file.getCurrentArray() * 1000,
        'p_lower': isc_file.Plower,
        'p_upper': isc_file.Pupper,
        'p_start': isc_file.Pstart,
        'p_end': isc_file.Pend,
    }


def set_zahner_data_isw(entry, d):
    entry.current = d['current']
    entry.time = d['time']
    entry.voltage = d['voltage']
    entry.datetime = convert_datetime(d['datetime'], '%b,%d.%Y %H:%M:%S')


def set_zahner_data_isc(entry, d):
    entry.datetime = d['datetime']
    entry.cycles = [
        VoltammetryCycleWithPlot(
            time=d['time'].tolist(),
            current=d['current'].tolist(),
            voltage=d['voltage'].tolist(),
        )
    ]
    entry.properties = CVProperties(
        initial_potential=d['p_start'],
        final_potential=d['p_end'],
        limit_potential_1=d['p_upper'],
        limit_potential_2=d['p_lower'],
    )


def set_zahner_data_ism(entry, d):
    entry.measurements = [
        EISPropertiesWithData(
            data=EISCycle(
                time=d['time'].tolist(),
                frequency=d['frequency'].tolist(),
                z_real=d['Z_real'].tolist(),
                z_imaginary=d['Z_imag'].tolist(),
                z_modulus=d['Z_mod'].tolist(),
                z_angle=d['Z_phase'].tolist(),
            )
        )
    ]
    entry.datetime = d['datetime']
