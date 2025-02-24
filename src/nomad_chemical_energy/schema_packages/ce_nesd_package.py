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

import numpy as np
import plotly.graph_objs as go
from baseclasses import BaseMeasurement
from baseclasses.chemical_energy import (
    Chronoamperometry,
    Chronopotentiometry,
    CyclicVoltammetry,
    ElectrochemicalImpedanceSpectroscopyMultiple,
    ElectrolyserPerformanceEvaluation,
    ElectrolyserProperties,
    LinearSweepVoltammetry,
    NESDElectrode,
    OpenCircuitVoltage,
)
from baseclasses.helper.archive_builder.labview_archive import (
    get_electrolyser_properties,
    get_tdms_archive,
)
from baseclasses.helper.utilities import (
    create_archive,
    get_entry_id_from_file_name,
    get_reference,
)
from nomad.datamodel.data import EntryData
from nomad.datamodel.metainfo.basesections import CompositeSystemReference
from nomad.datamodel.metainfo.plot import PlotlyFigure, PlotSection
from nomad.metainfo import Quantity, SchemaPackage, Section

from nomad_chemical_energy.schema_packages.file_parser.electrolyser_tdms_parser import (
    get_info_and_data,
)

m_package = SchemaPackage()

# %% ####################### Entities


class CE_NESD_Electrode(NESDElectrode, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['components', 'elemental_composition'],
        ),
    )


class CE_NESD_Electrolyser(ElectrolyserProperties, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['components', 'elemental_composition'],
            properties=dict(
                order=[
                    'name',
                    'cell_name',
                    'lab_id',
                    'datetime',
                ]
            ),
        ),
    )

    def normalize(self, archive, logger):
        super().normalize(archive, logger)


# %% ####################### Generic Entries


class CE_NESD_Electrolyser_Measurement(BaseMeasurement, PlotSection, EntryData):
    samples = BaseMeasurement.samples.m_copy()
    samples.label = 'electrolyser'


class CE_NESD_Measurement(BaseMeasurement, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'location', 'steps', 'instruments', 'results'],
            properties=dict(order=['name', 'data_file', 'samples']),
        ),
    )

    data_file = Quantity(
        type=str,
        shape=['*'],
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'),
    )


# %% ####################### Measurements


class CE_NESD_Chronoamperometry(
    CE_NESD_Electrolyser_Measurement, Chronoamperometry, EntryData
):
    m_def = Section(
        a_eln=dict(
            hide=[
                'metadata_file',
                'lab_id',
                'location',
                'control',
                'environment',
                'setup',
                'steps',
                'cycles',
                'instruments',
                'results',
            ],
            properties=dict(
                order=[
                    'name',
                    'data_file',
                    'samples',
                    'station',
                    'voltage_shift',
                    'resistance',
                ],
            ),
        ),
    )

    def make_current_plot(self):
        if self.current is None:
            return go.Figure().update_layout(
                title_text='Current over Time',
            )
        fig = go.Figure(
            data=[
                go.Scatter(
                    name='Current',
                    x=self.time,
                    y=self.current,
                    mode='lines',
                    hoverinfo='x+y+name',
                )
            ]
        )
        fig.update_layout(
            title_text='Current over Time',
            xaxis={
                'fixedrange': False,
                'title': f'Time ({self.time.units:~P})',
            },
            yaxis={
                'fixedrange': False,
                'title': f'Current ({self.current.units:~P})',
            },
            hovermode='x unified',
        )
        return fig

    def make_current_density_plot(self):
        if self.current_density is None:
            return go.Figure().update_layout(
                title_text='Current Density over Time',
            )
        fig = go.Figure(
            data=[
                go.Scatter(
                    name='Current Density',
                    x=self.time,
                    y=self.current_density,
                    mode='lines',
                    hoverinfo='x+y+name',
                )
            ]
        )
        fig.update_layout(
            title_text='Current Density over Time',
            xaxis={
                'fixedrange': False,
                'title': f'Time ({self.time.units:~P})',
            },
            yaxis={
                'fixedrange': False,
                'title': f'Current Density ({self.current_density.units:~P})',
            },
            hovermode='x unified',
        )
        return fig

    def normalize(self, archive, logger):
        if self.data_file:
            with archive.m_context.raw_file(self.data_file, 'rb') as f:
                if os.path.splitext(self.data_file)[-1] == '.mpr':
                    from baseclasses.helper.archive_builder.biologic_archive import (
                        get_biologic_properties,
                        get_ca_properties,
                        get_voltammetry_archive,
                    )

                    from nomad_chemical_energy.schema_packages.file_parser.biologic_parser import (
                        get_header_and_data,
                    )

                    metadata, data = get_header_and_data(f)
                    get_voltammetry_archive(data, metadata, self)
                    if not self.setup_parameters:
                        self.setup_parameters = get_biologic_properties(
                            metadata.get('settings', {})
                        )
                    if not self.properties:
                        self.properties = get_ca_properties(metadata.get('params', {}))
                        self.properties.sample_area = self.setup_parameters.get(
                            'sample_area'
                        )
        super().normalize(archive, logger)
        fig1 = self.make_current_plot()
        fig2 = self.make_current_density_plot()
        self.figures = [
            PlotlyFigure(label='Current over Time', figure=json.loads(fig1.to_json())),
            PlotlyFigure(
                label='Current Density over Time', figure=json.loads(fig2.to_json())
            ),
        ]


class CE_NESD_Chronopotentiometry(
    CE_NESD_Electrolyser_Measurement, Chronopotentiometry, EntryData
):
    m_def = Section(
        a_eln=dict(
            hide=[
                'metadata_file',
                'lab_id',
                'location',
                'control',
                'charge_density',
                'environment',
                'setup',
                'steps',
                'cycles',
                'instruments',
                'results',
            ],
            properties=dict(
                order=[
                    'name',
                    'data_file',
                    'samples',
                    'station',
                    'voltage_shift',
                    'resistance',
                ]
            ),
        ),
    )

    def make_voltage_plot(self):
        if self.voltage is None:
            return go.Figure().update_layout(
                title_text='Voltage over Time',
            )
        fig = go.Figure(
            data=[
                go.Scatter(
                    name='Voltage',
                    x=self.time,
                    y=self.voltage,
                    mode='lines',
                    hoverinfo='x+y+name',
                )
            ]
        )
        fig.update_layout(
            title_text='Voltage over Time',
            xaxis={
                'fixedrange': False,
                'title': f'Time ({self.time.units:~P})',
            },
            yaxis={
                'fixedrange': False,
                'title': f'Voltage ({self.voltage.units:~P})',
            },
            hovermode='x unified',
        )
        return fig

    def normalize(self, archive, logger):
        if self.data_file:
            with archive.m_context.raw_file(self.data_file, 'rb') as f:
                if os.path.splitext(self.data_file)[-1] == '.mpr':
                    from baseclasses.helper.archive_builder.biologic_archive import (
                        get_biologic_properties,
                        get_cp_properties,
                        get_voltammetry_archive,
                    )

                    from nomad_chemical_energy.schema_packages.file_parser.biologic_parser import (
                        get_header_and_data,
                    )

                    metadata, data = get_header_and_data(f)
                    get_voltammetry_archive(data, metadata, self)
                    if not self.setup_parameters:
                        self.setup_parameters = get_biologic_properties(
                            metadata.get('settings', {})
                        )
                    if not self.properties:
                        self.properties = get_cp_properties(metadata.get('params', {}))
                        self.properties.sample_area = self.setup_parameters.get(
                            'sample_area'
                        )
        super().normalize(archive, logger)
        fig1 = self.make_voltage_plot()
        self.figures = [
            PlotlyFigure(label='Voltage over Time', figure=json.loads(fig1.to_json())),
        ]


class CE_NESD_ConstantCurrentMode(
    CE_NESD_Electrolyser_Measurement, Chronopotentiometry, EntryData
):
    m_def = Section(
        a_eln=dict(
            hide=[
                'metadata_file',
                'lab_id',
                'location',
                'control',
                'charge_density',
                'environment',
                'setup',
                'steps',
                'cycles',
                'instruments',
                'results',
            ],
            properties=dict(
                order=[
                    'name',
                    'data_file',
                    'samples',
                    'station',
                    'voltage_shift',
                    'resistance',
                ]
            ),
        ),
    )

    def normalize(self, archive, logger):
        self.method = 'Constant Current'
        if self.data_file:
            with archive.m_context.raw_file(self.data_file, 'rb') as f:
                if os.path.splitext(self.data_file)[-1] == '.mpr':
                    from baseclasses.helper.archive_builder.biologic_archive import (
                        get_biologic_properties,
                        get_const_properties,
                        get_voltammetry_archive,
                    )

                    from nomad_chemical_energy.schema_packages.file_parser.biologic_parser import (
                        get_header_and_data,
                    )

                    metadata, data = get_header_and_data(f)
                    get_voltammetry_archive(data, metadata, self)
                    if not self.setup_parameters:
                        self.setup_parameters = get_biologic_properties(
                            metadata.get('settings', {})
                        )
                    if not self.properties:
                        self.properties = get_const_properties(
                            metadata.get('params', {}), constC=True
                        )
                        self.properties.sample_area = self.setup_parameters.get(
                            'sample_area'
                        )
        super().normalize(archive, logger)


class CE_NESD_ConstantVoltageMode(
    CE_NESD_Electrolyser_Measurement, Chronoamperometry, EntryData
):
    m_def = Section(
        a_eln=dict(
            hide=[
                'metadata_file',
                'lab_id',
                'location',
                'control',
                'charge_density',
                'environment',
                'setup',
                'steps',
                'cycles',
                'instruments',
                'results',
            ],
            properties=dict(
                order=[
                    'name',
                    'data_file',
                    'samples',
                    'station',
                    'voltage_shift',
                    'resistance',
                ]
            ),
        ),
    )

    def normalize(self, archive, logger):
        self.method = 'Constant Voltage'
        if self.data_file:
            with archive.m_context.raw_file(self.data_file, 'rb') as f:
                if os.path.splitext(self.data_file)[-1] == '.mpr':
                    from baseclasses.helper.archive_builder.biologic_archive import (
                        get_biologic_properties,
                        get_const_properties,
                        get_voltammetry_archive,
                    )

                    from nomad_chemical_energy.schema_packages.file_parser.biologic_parser import (
                        get_header_and_data,
                    )

                    metadata, data = get_header_and_data(f)
                    get_voltammetry_archive(data, metadata, self)
                    if not self.setup_parameters:
                        self.setup_parameters = get_biologic_properties(
                            metadata.get('settings', {})
                        )
                    if not self.properties:
                        self.properties = get_const_properties(
                            metadata.get('params', {}), constC=False
                        )
                        self.properties.sample_area = self.setup_parameters.get(
                            'sample_area'
                        )
        super().normalize(archive, logger)


class CE_NESD_CyclicVoltammetry(
    CE_NESD_Electrolyser_Measurement, CyclicVoltammetry, EntryData
):
    m_def = Section(
        a_eln=dict(
            hide=[
                'users',
                'location',
                'end_time',
                'steps',
                'instruments',
                'results',
                'lab_id',
                'voltage',
                'current',
                'current_density',
                'voltage_rhe_uncompensated',
                'voltage_rhe_compensated',
                'voltage_ref_compensated',
                'time',
                'charge_density',
                'control',
                'charge',
                'metadata_file',
            ],
            properties=dict(
                order=[
                    'name',
                    'data_file',
                ]
            ),
        ),
    )

    def make_current_density_plot(self):
        fig = go.Figure().update_layout(title_text='Current Density over Voltage RHE')
        if not self.cycles or self.cycles is None:
            return fig
        for idx, cycle in enumerate(self.cycles):
            if cycle.voltage_rhe_compensated is None or cycle.current_density is None:
                return fig
            fig.add_traces(
                go.Scatter(
                    name=f'Current Density {idx}',
                    x=cycle.voltage_rhe_compensated,
                    y=cycle.current_density,
                    mode='lines',
                    hoverinfo='x+y+name',
                )
            )
        fig.update_layout(
            showlegend=True,
            xaxis={
                'fixedrange': False,
                'title': f'Voltage RHE compensated ({self.cycles[0].voltage_rhe_compensated.units:~P})',
            },
            yaxis={
                'fixedrange': False,
                'title': f'Current Density ({self.cycles[0].current_density.units:~P})',
            },
            hovermode='x unified',
        )
        return fig

    def make_current_over_voltage_plot(self):
        fig = go.Figure().update_layout(
            title_text='Current over Voltage',
        )
        if not self.cycles or self.cycles is None:
            return fig
        for idx, cycle in enumerate(self.cycles):
            if cycle.voltage is None or cycle.current is None:
                return fig
            fig.add_traces(
                go.Scatter(
                    name=f'Current {idx}',
                    x=cycle.voltage,
                    y=cycle.current,
                    mode='lines',
                    hoverinfo='x+y+name',
                )
            )
        fig.update_layout(
            showlegend=True,
            xaxis={
                'fixedrange': False,
                'title': f'Voltage ({self.cycles[0].voltage.units:~P})',
            },
            yaxis={
                'fixedrange': False,
                'title': f'Current ({self.cycles[0].current.units:~P})',
            },
            hovermode='x unified',
        )
        return fig

    def normalize(self, archive, logger):
        if self.data_file:
            with archive.m_context.raw_file(self.data_file, 'rb') as f:
                if os.path.splitext(self.data_file)[-1] == '.mpr':
                    from baseclasses.helper.archive_builder.biologic_archive import (
                        get_biologic_properties,
                        get_cv_properties,
                        get_voltammetry_archive,
                    )

                    from nomad_chemical_energy.schema_packages.file_parser.biologic_parser import (
                        get_header_and_data,
                    )

                    metadata, data = get_header_and_data(f)
                    get_voltammetry_archive(data, metadata, self, multiple=True)
                    if not self.setup_parameters:
                        self.setup_parameters = get_biologic_properties(
                            metadata.get('settings', {})
                        )
                    if not self.properties:
                        self.properties = get_cv_properties(metadata.get('params', {}))
                        self.properties.sample_area = self.setup_parameters.get(
                            'sample_area'
                        )
        super().normalize(archive, logger)
        fig1 = self.make_current_density_plot()
        fig2 = self.make_current_over_voltage_plot()
        self.figures = [
            PlotlyFigure(
                label='Current Density over Voltage RHE',
                figure=json.loads(fig1.to_json()),
            ),
            PlotlyFigure(
                label='Current over Voltage', figure=json.loads(fig2.to_json())
            ),
        ]


class CE_NESD_ElectrolyserPerformanceEvaluation(
    CE_NESD_Electrolyser_Measurement, ElectrolyserPerformanceEvaluation, EntryData
):
    m_def = Section(
        a_eln=dict(
            hide=['location', 'steps', 'instruments', 'results', 'lab_id'],
            properties=dict(
                order=[
                    'name',
                    'data_file',
                    'datetime',
                    'laview_user',
                    'description',
                ]
            ),
        ),
    )

    def normalize(self, archive, logger):
        if self.data_file:
            with archive.m_context.raw_file(self.data_file, 'rb') as f:
                if os.path.splitext(self.data_file)[-1] == '.tdms':
                    metadata, data = get_info_and_data(f)
                    get_tdms_archive(data, self)
                    self.name = metadata.get('name')
                    self.labview_user = metadata.get('User_Name')
                    self.description = metadata.get('Comments')
                    # caution: samples has the "electrolyser properties" label in the GUI
                    if not self.samples:
                        # if filename starts with id this is already used for reference
                        # otherwise create a new CE_NESD_Electrolyser and reference this one
                        file_name = archive.metadata.mainfile.split('.')[0]
                        electrolyser_file_name = (
                            f'{file_name}_electrolyser.archive.json'
                        )
                        electrolyser = get_electrolyser_properties(
                            metadata, CE_NESD_Electrolyser()
                        )
                        create_archive(
                            electrolyser,
                            archive,
                            electrolyser_file_name,
                            overwrite=False,
                        )
                        electrolyser_entry_id = get_entry_id_from_file_name(
                            electrolyser_file_name, archive
                        )
                        self.samples = [
                            CompositeSystemReference(
                                reference=get_reference(
                                    archive.metadata.upload_id, electrolyser_entry_id
                                )
                            )
                        ]

        super().normalize(archive, logger)


class CE_NESD_GEIS(
    CE_NESD_Electrolyser_Measurement,
    ElectrochemicalImpedanceSpectroscopyMultiple,
    EntryData,
):
    m_def = Section(
        a_eln=dict(
            hide=[
                'environment',
                'setup',
                'metadata_file',
                'lab_id',
                'location',
                'steps',
                'instruments',
                'results',
                'pretreatment',
                'properties',
            ],
            properties=dict(
                order=[
                    'name',
                    'data_file',
                    'samples',
                    'station',
                ]
            ),
        ),
    )

    def make_nyquist_plot(self):
        fig = go.Figure().update_layout(
            title_text='Nyquist Plot',
        )
        if self.measurements is None:
            return fig
        for idx, cycle in enumerate(self.measurements):
            if cycle.data is None:
                return fig
            if cycle.data.z_imaginary is None or cycle.data.z_real is None:
                return fig
            fig.add_traces(
                go.Scatter(
                    name=f'Nyquist {idx}',
                    x=cycle.data.z_real,
                    y=cycle.data.z_imaginary,
                    mode='lines',
                    hoverinfo='x+y+name',
                )
            )
        fig.update_layout(
            title_text='Nyquist Plot',
            xaxis={'fixedrange': False, 'title': 'Re(Z) (Ω)'},
            yaxis={'fixedrange': False, 'title': '-Im(Z) (Ω)'},
            hovermode='closest',
        )
        return fig

    def make_bode_plot(self):
        fig = go.Figure().update_layout(
            title_text='Bode Plot',
        )
        if self.measurements is None:
            return fig
        for idx, cycle in enumerate(self.measurements):
            if cycle.data is None:
                return fig
            if (
                cycle.data.frequency is None
                or cycle.data.z_modulus is None
                or cycle.data.z_angle is None
            ):
                return fig
            fig.add_traces(
                go.Scatter(
                    name=f'|Z| {idx}',
                    x=cycle.data.frequency,
                    y=cycle.data.z_modulus,
                    mode='lines',
                    hoverinfo='x+y+name',
                )
            )
            fig.add_traces(
                go.Scatter(
                    name=f'Phase(Z) {idx}', x=cycle.data.frequency, y=cycle.data.z_angle
                )
            )
        fig.update_layout(
            title_text='Bode Plot',
            showlegend=True,
            xaxis={
                'fixedrange': False,
                'type': 'log',
                'title': f'Frequency ({self.measurements[0].data.frequency.units:~P})',
            },
            yaxis={'fixedrange': False},
            hovermode='closest',
        )
        return fig

    def normalize(self, archive, logger):
        if self.data_file:
            with archive.m_context.raw_file(self.data_file, 'rb') as f:
                if os.path.splitext(self.data_file)[-1] == '.mpr':
                    from baseclasses.helper.archive_builder.biologic_archive import (
                        get_biologic_properties,
                        get_eis_data,
                        get_eis_properties,
                        get_meta_data,
                        get_start_time,
                    )

                    from nomad_chemical_energy.schema_packages.file_parser.biologic_parser import (
                        get_header_and_data,
                    )

                    metadata, data = get_header_and_data(f)
                    get_meta_data(metadata.get('settings', {}), self)
                    ole_timestamp = metadata.get('log', {}).get('ole_timestamp', 0)
                    start_time_offset = data.get('time', np.array([0]))[0].item()
                    self.datetime = get_start_time(ole_timestamp, start_time_offset)
                    if not self.setup_parameters:
                        self.setup_parameters = get_biologic_properties(
                            metadata.get('settings', {})
                        )
                    if not self.measurements:
                        self.measurements = get_eis_properties(
                            metadata.get('params', {})
                        )
                        get_eis_data(data, self.measurements)
                    for cycle in self.measurements:
                        cycle.sample_area = self.setup_parameters.get('sample_area')
        super().normalize(archive, logger)
        fig1 = self.make_nyquist_plot()
        fig2 = self.make_bode_plot()
        self.figures = [
            PlotlyFigure(label='Nyquist Plot', figure=json.loads(fig1.to_json())),
            PlotlyFigure(label='Bode Plot', figure=json.loads(fig2.to_json())),
        ]


class CE_NESD_LinearSweepVoltammetry(
    CE_NESD_Electrolyser_Measurement, LinearSweepVoltammetry, EntryData
):
    m_def = Section(
        a_eln=dict(
            hide=[
                'metadata_file',
                'lab_id',
                'location',
                'control',
                'charge_density',
                'environment',
                'setup',
                'steps',
                'cycles',
                'instruments',
                'results',
            ],
            properties=dict(
                order=[
                    'name',
                    'data_file',
                    'samples',
                    'station',
                    'voltage_shift',
                    'resistance',
                ]
            ),
        ),
    )

    def make_current_density_plot(self):
        if self.current_density is None or self.voltage_rhe_compensated is None:
            return go.Figure().update_layout(
                title_text='Current Density over Voltage RHE',
            )
        fig = go.Figure(
            data=[
                go.Scatter(
                    name='Current Density',
                    x=self.voltage_rhe_compensated,
                    y=self.current_density,
                    mode='lines',
                    hoverinfo='x+y+name',
                )
            ]
        )
        fig.update_layout(
            title_text='Current Density over Voltage RHE',
            showlegend=True,
            xaxis={
                'fixedrange': False,
                'title': f'Voltage RHE compensated ({self.voltage_rhe_compensated.units:~P})',
            },
            yaxis={
                'fixedrange': False,
                'title': f'Current Density ({self.current_density.units:~P})',
            },
            hovermode='x unified',
        )
        return fig

    def make_current_over_voltage_plot(self):
        if self.current is None or self.voltage is None:
            return go.Figure().update_layout(
                title_text='Current over Voltage',
            )
        fig = go.Figure(
            data=[
                go.Scatter(
                    name='Current',
                    x=self.voltage,
                    y=self.current,
                    mode='lines',
                    hoverinfo='x+y+name',
                )
            ]
        )
        fig.update_layout(
            title_text='Current over Voltage',
            showlegend=True,
            xaxis={
                'fixedrange': False,
                'title': f'Voltage ({self.voltage.units:~P})',
            },
            yaxis={
                'fixedrange': False,
                'title': f'Current ({self.current.units:~P})',
            },
            hovermode='x unified',
        )
        return fig

    def normalize(self, archive, logger):
        if self.data_file:
            with archive.m_context.raw_file(self.data_file, 'rb') as f:
                if os.path.splitext(self.data_file)[-1] == '.mpr':
                    from baseclasses.helper.archive_builder.biologic_archive import (
                        get_biologic_properties,
                        get_lsv_properties,
                        get_voltammetry_archive,
                    )

                    from nomad_chemical_energy.schema_packages.file_parser.biologic_parser import (
                        get_header_and_data,
                    )

                    metadata, data = get_header_and_data(f)
                    get_voltammetry_archive(data, metadata, self)
                    if not self.setup_parameters:
                        self.setup_parameters = get_biologic_properties(
                            metadata.get('settings', {})
                        )
                    if not self.properties:
                        self.properties = get_lsv_properties(metadata.get('params', {}))
                        self.properties.sample_area = self.setup_parameters.get(
                            'sample_area'
                        )
        super().normalize(archive, logger)
        fig1 = self.make_current_density_plot()
        fig2 = self.make_current_over_voltage_plot()
        self.figures = [
            PlotlyFigure(
                label='Current Density over Voltage RHE',
                figure=json.loads(fig1.to_json()),
            ),
            PlotlyFigure(
                label='Current over Voltage', figure=json.loads(fig2.to_json())
            ),
        ]


class CE_NESD_OpenCircuitVoltage(
    CE_NESD_Electrolyser_Measurement, OpenCircuitVoltage, EntryData
):
    m_def = Section(
        a_eln=dict(
            hide=[
                'metadata_file',
                'lab_id',
                'location',
                'control',
                'charge',
                'charge_density',
                'environment',
                'setup',
                'steps',
                'cycles',
                'instruments',
                'results',
            ],
            properties=dict(
                order=[
                    'name',
                    'data_file',
                    'samples',
                    'station',
                    'voltage_shift',
                    'resistance',
                ]
            ),
        ),
    )

    def make_voltage_plot(self):
        if self.voltage is None:
            return go.Figure().update_layout(
                title_text='Voltage over Time',
            )
        fig = go.Figure(
            data=[
                go.Scatter(
                    name='Voltage',
                    x=self.time,
                    y=self.voltage,
                    mode='lines',
                    hoverinfo='x+y+name',
                )
            ]
        )
        fig.update_layout(
            title_text='Voltage over Time',
            xaxis={
                'fixedrange': False,
                'title': f'Time ({self.time.units:~P})',
            },
            yaxis={
                'fixedrange': False,
                'title': f'Voltage ({self.voltage.units:~P})',
            },
            hovermode='x unified',
        )
        return fig

    def normalize(self, archive, logger):
        if self.data_file:
            with archive.m_context.raw_file(self.data_file, 'rb') as f:
                if os.path.splitext(self.data_file)[-1] == '.mpr':
                    from baseclasses.helper.archive_builder.biologic_archive import (
                        get_biologic_properties,
                        get_ocv_properties,
                        get_voltammetry_archive,
                    )

                    from nomad_chemical_energy.schema_packages.file_parser.biologic_parser import (
                        get_header_and_data,
                    )

                    metadata, data = get_header_and_data(f)
                    get_voltammetry_archive(data, metadata, self)
                    if not self.setup_parameters:
                        self.setup_parameters = get_biologic_properties(
                            metadata.get('settings', {})
                        )
                    if not self.properties:
                        self.properties = get_ocv_properties(metadata.get('params', {}))
                        self.properties.sample_area = self.setup_parameters.get(
                            'sample_area'
                        )
        super().normalize(archive, logger)
        fig1 = self.make_voltage_plot()
        self.figures = [
            PlotlyFigure(label='Voltage over Time', figure=json.loads(fig1.to_json())),
        ]


class CE_NESD_PEIS(
    CE_NESD_Electrolyser_Measurement,
    ElectrochemicalImpedanceSpectroscopyMultiple,
    EntryData,
):
    m_def = Section(
        a_eln=dict(
            hide=[
                'environment',
                'setup',
                'metadata_file',
                'lab_id',
                'location',
                'steps',
                'instruments',
                'results',
                'pretreatment',
                'properties',
            ],
            properties=dict(
                order=[
                    'name',
                    'data_file',
                    'samples',
                    'station',
                ]
            ),
        ),
    )

    def make_nyquist_plot(self):
        fig = go.Figure().update_layout(
            title_text='Nyquist Plot',
        )
        if self.measurements is None:
            return fig
        for idx, cycle in enumerate(self.measurements):
            if cycle.data is None:
                return fig
            if cycle.data.z_imaginary is None or cycle.data.z_real is None:
                return fig
            fig.add_traces(
                go.Scatter(
                    name=f'Nyquist {idx}',
                    x=cycle.data.z_real,
                    y=cycle.data.z_imaginary,
                    mode='lines',
                    hoverinfo='x+y+name',
                )
            )
        fig.update_layout(
            title_text='Nyquist Plot',
            xaxis={'fixedrange': False, 'title': 'Re(Z) (Ω)'},
            yaxis={'fixedrange': False, 'title': '-Im(Z) (Ω)'},
            hovermode='closest',
        )
        return fig

    def make_bode_plot(self):
        fig = go.Figure().update_layout(
            title_text='Bode Plot',
        )
        if self.measurements is None:
            return fig
        for idx, cycle in enumerate(self.measurements):
            if cycle.data is None:
                return fig
            if (
                cycle.data.frequency is None
                or cycle.data.z_modulus is None
                or cycle.data.z_angle is None
            ):
                return fig
            fig.add_traces(
                go.Scatter(
                    name=f'|Z| {idx}',
                    x=cycle.data.frequency,
                    y=cycle.data.z_modulus,
                    mode='lines',
                    hoverinfo='x+y+name',
                )
            )
            fig.add_traces(
                go.Scatter(
                    name=f'Phase(Z) {idx}', x=cycle.data.frequency, y=cycle.data.z_angle
                )
            )
        fig.update_layout(
            title_text='Bode Plot',
            showlegend=True,
            xaxis={
                'fixedrange': False,
                'type': 'log',
                'title': f'Frequency ({self.measurements[0].data.frequency.units:~P})',
            },
            yaxis={'fixedrange': False},
            hovermode='closest',
        )
        return fig

    def normalize(self, archive, logger):
        if self.data_file:
            with archive.m_context.raw_file(self.data_file, 'rb') as f:
                if os.path.splitext(self.data_file)[-1] == '.mpr':
                    from baseclasses.helper.archive_builder.biologic_archive import (
                        get_biologic_properties,
                        get_eis_data,
                        get_eis_properties,
                        get_meta_data,
                        get_start_time,
                    )

                    from nomad_chemical_energy.schema_packages.file_parser.biologic_parser import (
                        get_header_and_data,
                    )

                    metadata, data = get_header_and_data(f)
                    get_meta_data(metadata.get('settings', {}), self)
                    ole_timestamp = metadata.get('log', {}).get('ole_timestamp', 0)
                    start_time_offset = data.get('time', np.array([0]))[0].item()
                    self.datetime = get_start_time(ole_timestamp, start_time_offset)
                    if not self.setup_parameters:
                        self.setup_parameters = get_biologic_properties(
                            metadata.get('settings', {})
                        )
                    if not self.measurements:
                        self.measurements = get_eis_properties(
                            metadata.get('params', {})
                        )
                        get_eis_data(data, self.measurements)
                    for cycle in self.measurements:
                        cycle.sample_area = self.setup_parameters.get('sample_area')
        super().normalize(archive, logger)
        fig1 = self.make_nyquist_plot()
        fig2 = self.make_bode_plot()
        self.figures = [
            PlotlyFigure(label='Nyquist Plot', figure=json.loads(fig1.to_json())),
            PlotlyFigure(label='Bode Plot', figure=json.loads(fig2.to_json())),
        ]
        super().normalize(archive, logger)


m_package.__init_metainfo__()
