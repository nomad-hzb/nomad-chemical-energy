#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 17 13:17:46 2025

@author: a2853
"""

from zahner_analysis.file_import.isw_import import IswImport
from zahner_analysis.file_import.ism_import import IsmImport
import numpy as np
import matplotlib.pyplot as plt
import os
from baseclasses.helper.utilities import convert_datetime


def parse_metadata(filedata):
    lines = filedata.split("\n")

    datetime = lines[4].split(":", 1)[1] + " " + lines[6][:8]
    method = None
    if "cp" in lines[-1].lower():
        method = "cp"
    elif "ca" in lines[-1].lower():
        method = "ca"
    return datetime.strip(), method


def determine_method_isw(t, c, v):
    fit_c = np.polyfit(t, c, 1, full=True)
    fit_v = np.polyfit(t, v, 1, full=True)

    if abs(fit_c[0][0]) < 1e-12 and fit_c[1] < fit_v[1]:
        return "cp"

    if abs(fit_v[0][0]) < 1e-12 and fit_v[1] < fit_c[1]:
        return "ca"

    if fit_c[1] < fit_v[1]:
        return "cp"

    if fit_v[1] < fit_c[1]:
        return "ca"


def get_data_from_isw_file(filedata, filemetadata=None):
    isw_file = IswImport(filedata)
    datetime, method = parse_metadata(filemetadata) if filemetadata else (None, None)

    t = isw_file.getTimeArray()
    c = isw_file.getCurrentArray()
    v = isw_file.getVoltageArray()
    if not method:
        method = determine_method_isw(t, c, v)

    return {
        "datetime": datetime,
        "method": method,
        "time": t,
        "current": c,
        "voltage": v,
    }


def get_data_from_ism_file(filedata):
    ism_file = IsmImport(filedata)

    imp = ism_file.getImpedanceArray()*np.exp(1j*ism_file.getPhaseArray())
    f = ism_file.getFrequencyArray()
    datetime = ism_file.getMeasurementDateTimeArray()
    return ism_file


def set_zahner_data_isw(entry, d):
    entry.current = d["current"]
    entry.time = d["time"]
    entry.voltage = d["voltage"]
    entry.datetime = convert_datetime(d["datetime"], "%b,%d.%Y %H:%M:%S")
