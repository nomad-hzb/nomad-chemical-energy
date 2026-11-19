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

import json
import os

import pandas as pd
from baseclasses.chemical_energy import (
    Chronopotentiometry,
    CyclicVoltammetry,
    ElectrochemicalImpedanceSpectroscopy,
    VoltammetryCycleWithPlot,
)
from nomad.datamodel.data import EntryData
from nomad.datamodel.metainfo.plot import PlotlyFigure, PlotSection

# from nomad.units import ureg
from nomad.metainfo import SchemaPackage, Section

from nomad_chemical_energy.schema_packages.utilities.plotly_figure_helpers import (
    make_bode_plot,
    make_current_density_over_voltage_rhe_cv_plot,
    make_current_over_voltage_cv_plot,
    make_nyquist_plot,
    make_voltage_plot,
)

m_package = SchemaPackage()


class DLR_ElectrochemicalImpedanceSpectroscopy(
    ElectrochemicalImpedanceSpectroscopy,
    EntryData,
    PlotSection,
):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'solution',
                'users',
                'location',
                'end_time',
                'steps',
                'instruments',
                'results',
                'metadata_file',
            ],
            properties=dict(
                order=[
                    'name',
                    'data_file',
                    'environment',
                    'setup',
                    'samples',
                    'station',
                ]
            ),
        ),
    )

    def normalize(self, archive, logger):
        if self.data_file:
            with archive.m_context.raw_file(self.data_file, 'rt') as f:
                if os.path.splitext(self.data_file)[-1] == '.txt':
                    data = pd.read_csv(f, sep='\t', skiprows=1, header=0)
                    data.columns = [
                        'Index',
                        'Freq',
                        'Zreal',
                        'Zimag',
                        'Zmod',
                        'Zphz',
                        'Time',
                    ]
                    data.Zimag *= -1
                    data.Zphz *= -1
                    from baseclasses.helper.archive_builder.gamry_archive import (
                        get_eis_data,
                    )

                    get_eis_data(data, self)

        super().normalize(archive, logger)
        fig1 = make_nyquist_plot(z_real=self.z_real, z_imaginary=self.z_imaginary)
        fig2 = make_bode_plot(
            frequency=self.frequency, z_modulus=self.z_modulus, z_angle=self.z_angle
        )
        self.figures = [
            PlotlyFigure(label='Nyquist Plot', figure=json.loads(fig1.to_json())),
            PlotlyFigure(label='Bode Plot', figure=json.loads(fig2.to_json())),
        ]


class DLR_CyclicVoltammetry(CyclicVoltammetry, EntryData, PlotSection):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'solution',
                'users',
                'location',
                'end_time',
                'steps',
                'instruments',
                'results',
                'metadata_file',
                'voltage',
                'current',
                'current_density',
                'voltage_rhe_uncompensated',
                'time',
                'voltage_rhe_compensated',
                'voltage_ref_compensated',
                'charge_density',
                'control',
                'charge',
            ],
            properties=dict(
                order=[
                    'name',
                    'data_file',
                    'environment',
                    'setup',
                    'samples',
                    'station',
                    'voltage_shift',
                    'resistance',
                ]
            ),
        ),
    )

    def normalize(self, archive, logger):
        if self.data_file:
            with archive.m_context.raw_file(self.data_file, 'rt') as f:
                if os.path.splitext(self.data_file)[-1] == '.txt':
                    data = pd.read_csv(f, sep='\t', skiprows=1, header=0)
                    data.columns = ['Vf', 'T', 'Im', 'Scan', 'Index']
                    unique_names = data.Scan.unique()
                    data_list = []
                    for key in unique_names:
                        data_list.append(data[:][data.Scan == key])

                    from baseclasses.helper.archive_builder.gamry_archive import (
                        get_voltammetry_data,
                    )

                    self.cycles = []
                    for curve in data_list:
                        cycle = VoltammetryCycleWithPlot()
                        get_voltammetry_data(curve, cycle)
                        self.cycles.append(cycle)

        super().normalize(archive, logger)
        fig1 = make_current_density_over_voltage_rhe_cv_plot(self.cycles)
        fig2 = make_current_over_voltage_cv_plot(self.cycles)
        self.figures = [
            PlotlyFigure(
                label='Current Density over Voltage RHE',
                figure=json.loads(fig1.to_json()),
            ),
            PlotlyFigure(
                label='Current over Voltage',
                figure=json.loads(fig2.to_json()),
            ),
        ]


class DLR_Chronopotentiometry(Chronopotentiometry, EntryData, PlotSection):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'solution',
                'users',
                'location',
                'end_time',
                'steps',
                'instruments',
                'results',
                'metadata_file',
                'charge_density',
                'control',
                'cycles',
            ],
            properties=dict(
                order=[
                    'name',
                    'data_file',
                    'environment',
                    'setup',
                    'samples',
                    'station',
                    'voltage_shift',
                    'resistance',
                ]
            ),
        ),
    )

    def normalize(self, archive, logger):
        if self.data_file:
            with archive.m_context.raw_file(self.data_file, 'rt') as f:
                if os.path.splitext(self.data_file)[-1] == '.txt':
                    data = pd.read_csv(f, sep='\t', skiprows=1, header=0)
                    data.columns = ['Tabs', 'Vf', 'T', 'Index']

                    from baseclasses.helper.archive_builder.gamry_archive import (
                        get_voltammetry_data,
                    )

                    get_voltammetry_data(data, self)

        super().normalize(archive, logger)
        fig1 = make_voltage_plot(self.time, self.voltage)
        self.figures = [
            PlotlyFigure(label='Voltage over Time', figure=json.loads(fig1.to_json())),
        ]


m_package.__init_metainfo__()
