#
# Copyright The NOMAD Authors.
#
# This file is part of NOMAD. See https://nomad-lab.eu for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import numpy as np
import os
import pandas as pd

from nomad.datamodel.metainfo.plot import PlotSection, PlotlyFigure
import plotly.graph_objs as go

# from nomad.units import ureg
from nomad.metainfo import (
    Package,
    Quantity,
    Section, SubSection, SchemaPackage)
from nomad.datamodel.data import EntryData

from nomad.datamodel.metainfo.eln import Substance
from nomad.datamodel.metainfo.basesections import PubChemPureSubstanceSection
from baseclasses import (
    BaseProcess, BaseMeasurement
)

from baseclasses.design1 import Design
from baseclasses.documentation_tool import DocumentationTool

from baseclasses.characterizations import (
    XASFluorescence, XASTransmission
)

from baseclasses.voila import (
    VoilaNotebook
)

from baseclasses.solar_energy import UVvisMeasurement

from baseclasses.chemical_energy import (
    CENOMESample, SampleIDCENOME, Electrode, Electrolyte, ElectroChemicalCell, SubstrateProperties, Equipment,
    CatalystSynthesis,
    ElectroChemicalSetup, Environment, Purging, SubstanceWithConcentration,
    get_next_project_sample_number,
    CyclicVoltammetry, VoltammetryCycleWithPlot,
    Chronoamperometry,
    Chronopotentiometry,
    Chronocoulometry,
    OpenCircuitVoltage,
    ElectrochemicalImpedanceSpectroscopy,
    # PreparationProtocol,
    GalvanodynamicSweep,
    PhaseFluorometryOxygen,
    PumpRateMeasurement,
    LinearSweepVoltammetry,
    UVvisDataConcentration
)

from baseclasses.data_transformations import UVvisConcentrationDetection

from baseclasses.helper.utilities import create_archive, rewrite_json, find_sample_by_id
from datetime import datetime

m_package = SchemaPackage()


class DLR_ElectrochemicalImpedanceSpectroscopy(
        ElectrochemicalImpedanceSpectroscopy, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'solution',
                'users', "location", 'end_time', 'steps', 'instruments', 'results', "metadata_file"],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "environment",
                    "setup",
                    "samples",
                    "station"])),
        a_plot=[
            {
                'label': 'Nyquist Plot',
                'x': 'z_real',
                'y': 'z_imaginary',
                'layout': {
                    'yaxis': {
                        "fixedrange": False, "title": "-Im(Z) (Ω)"},
                    'xaxis': {
                        "fixedrange": False, "title": "Re(Z) (Ω)"}}
            },
            {
                'label': 'Bode Plot',
                'x': ['frequency', 'frequency'],
                'y': ['./z_modulus', './z_angle'],
                'layout': {
                    "showlegend": True,
                    'yaxis': {
                        "fixedrange": False},
                    'xaxis': {
                        "fixedrange": False, 'type': 'log'}},
            }
        ]
    )

    def normalize(self, archive, logger):
        if self.data_file:
            with archive.m_context.raw_file(self.data_file) as f:
                if os.path.splitext(self.data_file)[-1] == ".txt":
                    data = pd.read_csv(f.name, sep="\t", skiprows=1, header=0)
                    data.columns = ["Index", "Freq", "Zreal", "Zimag", "Zmod", "Zphz", "Time"]
                    data.Zimag *= -1
                    data.Zphz *= -1
                    from baseclasses.helper.archive_builder.gamry_archive import get_eis_data
                    get_eis_data(data, self)

        super(DLR_ElectrochemicalImpedanceSpectroscopy,
              self).normalize(archive, logger)


class DLR_CyclicVoltammetry(CyclicVoltammetry, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'solution',
                'users', "location", 'end_time', 'steps', 'instruments', 'results', "metadata_file", "voltage",
                "current", "current_density", "voltage_rhe_uncompensated", "time",
                "voltage_rhe_compensated", "voltage_ref_compensated", "charge_density", "control", "charge"],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "environment",
                    "setup",
                    "samples",
                    "station", "voltage_shift", "resistance"])),
        a_plot=[{
            'label': 'Current Density over Voltage RHE',
            'x': 'cycles/:/voltage_rhe_compensated',
            'y': 'cycles/:/current_density',
            'layout': {
                "showlegend": True,
                'yaxis': {
                    "fixedrange": False},
                'xaxis': {
                    "fixedrange": False}},
        },
            {
                'label': 'Current over Voltage',
                'x': 'cycles/:/voltage',
                'y': 'cycles/:/current',
                'layout': {
                    "showlegend": True,
                    'yaxis': {
                        "fixedrange": False},
                    'xaxis': {
                        "fixedrange": False}},
        }]
    )

    def normalize(self, archive, logger):
        if self.data_file:
            with archive.m_context.raw_file(self.data_file) as f:
                if os.path.splitext(self.data_file)[-1] == ".txt":
                    data = pd.read_csv(f.name, sep="\t", skiprows=1, header=0)
                    data.columns = ["Vf", "T", "Im", "Scan", "Index"]
                    unique_names = data.Scan.unique()
                    data_list = []
                    for key in unique_names:
                        data_list.append(data[:][data.Scan == key])

                    from baseclasses.helper.archive_builder.gamry_archive import get_voltammetry_data
                    self.cycles = []
                    for curve in data_list:
                        cycle = VoltammetryCycleWithPlot()
                        get_voltammetry_data(curve, cycle)
                        self.cycles.append(cycle)

        super(DLR_CyclicVoltammetry, self).normalize(archive, logger)


class DLR_Chronopotentiometry(Chronopotentiometry, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'solution', 'users', "location", 'end_time', 'steps', 'instruments', 'results',
                "metadata_file", "charge_density", "control", "cycles"],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "environment",
                    "setup",
                    "samples",
                    "station", "voltage_shift", "resistance"])), a_plot=[
            {
                'label': 'Voltage', 'x': 'time', 'y': 'voltage', 'layout': {
                    'yaxis': {
                        "fixedrange": False}, 'xaxis': {
                        "fixedrange": False}}, "config": {
                    "scrollZoom": True, 'staticPlot': False, }},
        ])

    def normalize(self, archive, logger):
        if self.data_file:
            with archive.m_context.raw_file(self.data_file) as f:
                if os.path.splitext(self.data_file)[-1] == ".txt":
                    data = pd.read_csv(f.name, sep="\t", skiprows=1, header=0)
                    data.columns = ["Tabs", "Vf", "T", "Index"]

                    from baseclasses.helper.archive_builder.gamry_archive import get_voltammetry_data
                    get_voltammetry_data(data, self)

        super(DLR_Chronopotentiometry, self).normalize(archive, logger)


m_package.__init_metainfo__()
