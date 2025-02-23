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

import os

import plotly.graph_objs as go
from baseclasses import BaseMeasurement
from baseclasses.chemical_energy import (
    Chronoamperometry,
    Chronopotentiometry,
    CyclicVoltammetry,
    ElectrochemicalImpedanceSpectroscopy,
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
from nomad.datamodel.metainfo.plot import PlotlyFigure
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


class CE_NESD_Chronoamperometry(Chronoamperometry, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'metadata_file',
                'lab_id',
                'location',
                'control',
                'charge',
                'charge_density',
                'steps',
                'cycles',
                'instruments',
                'results',
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

    def make_current_plot(self):
        fig = go.Figure(
            data=[
                go.Scatter(
                    name='Current',
                    x=self.time,
                    y=self.current,
                )
            ]
        )
        fig.update_layout(
            title_text='Current over Time',
            xaxis={'fixedrange': False},
            yaxis={'fixedrange': False},
        )
        return fig

    def make_current_density_plot(self):
        fig = go.Figure(
            data=[
                go.Scatter(
                    name='Current',
                    x=self.time,
                    y=self.current_density,
                )
            ]
        )
        fig.update_layout(
            title_text='Current Density over Time',
            xaxis={'fixedrange': False},
            yaxis={'fixedrange': False},
        )
        return fig

    def normalize(self, archive, logger):
        if self.data_file:
            with archive.m_context.raw_file(self.data_file, 'rt') as f:
                if os.path.splitext(self.data_file)[-1] == '.mpr':
                    from baseclasses.helper.archive_builder.biologic_archive import (
                        get_biologic_properties,
                        get_voltammetry_archive,
                    )

                    from nomad_chemical_energy.schema_packages.file_parser.biologic_parser import (
                        get_header_and_data,
                    )

                    metadata, data = get_header_and_data(f)
                    get_voltammetry_archive(data, metadata, self)
                    if not self.properties:
                        # metadata_device_settings = json.loads(data.attrs.get('original_metadata')).get('params', {})
                        # TODO use CA Properties with metadata_device_settings attribute
                        self.properties = get_biologic_properties(metadata)
        fig1 = self.make_current_plot()
        fig2 = self.make_current_density_plot()
        self.figures = [
            PlotlyFigure(label='Current over Time', figure=fig1.to_plotly_json()),
            PlotlyFigure(
                label='Current Density over Time', figure=fig2.to_plotly_json()
            ),
        ]
        super().normalize(archive, logger)


class CE_NESD_Chronopotentiometry(Chronopotentiometry, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'metadata_file',
                'lab_id',
                'location',
                'control',
                'charge',
                'charge_density',
                'steps',
                'cycles',
                'instruments',
                'results',
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

    def make_voltage_plot(self):
        fig = go.Figure(
            data=[
                go.Scatter(
                    name='Voltage',
                    x=self.time,
                    y=self.voltage,
                )
            ]
        )
        fig.update_layout(
            title_text='Voltage over Time',
            xaxis={'fixedrange': False},
            yaxis={'fixedrange': False},
        )
        return fig

    def normalize(self, archive, logger):
        if self.data_file:
            with archive.m_context.raw_file(self.data_file, 'rt') as f:
                if os.path.splitext(self.data_file)[-1] == '.mpr':
                    from baseclasses.helper.archive_builder.biologic_archive import (
                        get_biologic_properties,
                        get_voltammetry_archive,
                    )

                    from nomad_chemical_energy.schema_packages.file_parser.biologic_parser import (
                        get_header_and_data,
                    )

                    metadata, data = get_header_and_data(f)
                    get_voltammetry_archive(data, metadata, self)
                    if not self.properties:
                        self.properties = get_biologic_properties(metadata)
        fig1 = self.make_voltage_plot()
        self.figures = [
            PlotlyFigure(label='Voltage over Time', figure=fig1.to_plotly_json()),
        ]
        super().normalize(archive, logger)


class CE_NESD_ConstantCurrentMode(Chronopotentiometry, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'metadata_file',
                'lab_id',
                'location',
                'control',
                'charge',
                'charge_density',
                'steps',
                'cycles',
                'instruments',
                'results',
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
                if os.path.splitext(self.data_file)[-1] == '.mpr':
                    from baseclasses.helper.archive_builder.biologic_archive import (
                        get_biologic_properties,
                        get_voltammetry_archive,
                    )

                    from nomad_chemical_energy.schema_packages.file_parser.biologic_parser import (
                        get_header_and_data,
                    )

                    metadata, data = get_header_and_data(f)
                    get_voltammetry_archive(data, metadata, self)
                    if not self.properties:
                        self.properties = get_biologic_properties(metadata)
        super().normalize(archive, logger)


class CE_NESD_ConstantVoltageMode(Chronoamperometry, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'metadata_file',
                'lab_id',
                'location',
                'control',
                'charge',
                'charge_density',
                'steps',
                'cycles',
                'instruments',
                'results',
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
                if os.path.splitext(self.data_file)[-1] == '.mpr':
                    from baseclasses.helper.archive_builder.biologic_archive import (
                        get_biologic_properties,
                        get_voltammetry_archive,
                    )

                    from nomad_chemical_energy.schema_packages.file_parser.biologic_parser import (
                        get_header_and_data,
                    )

                    metadata, data = get_header_and_data(f)
                    get_voltammetry_archive(data, metadata, self)
                    if not self.properties:
                        self.properties = get_biologic_properties(metadata)
        super().normalize(archive, logger)


class CE_NESD_CyclicVoltammetry(CyclicVoltammetry, EntryData):
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
        fig = go.Figure()
        for cycle in self.cycles:
            fig.add_traces(
                go.Scatter(
                    name='Current Density',
                    x=cycle.voltage_rhe_compensated,
                    y=cycle.current_density,
                )
            )
        fig.update_layout(
            title_text='Current Density over Voltage RHE',
            showlegend=True,
            xaxis={'fixedrange': False},
        )
        return fig

    def make_current_over_voltage_plot(self):
        fig = go.Figure()
        for cycle in self.cycles:
            fig.add_traces(
                go.Scatter(
                    name='Current',
                    x=cycle.voltage,
                    y=cycle.current,
                )
            )
        fig.update_layout(
            title_text='Current over Voltage',
            showlegend=True,
            xaxis={'fixedrange': False},
        )
        return fig

    def normalize(self, archive, logger):
        if self.data_file:
            with archive.m_context.raw_file(self.data_file, 'rt') as f:
                if os.path.splitext(self.data_file)[-1] == '.mpr':
                    from baseclasses.helper.archive_builder.biologic_archive import (
                        get_biologic_properties,
                        get_voltammetry_archive,
                    )

                    from nomad_chemical_energy.schema_packages.file_parser.biologic_parser import (
                        get_header_and_data,
                    )

                    metadata, data = get_header_and_data(f)
                    get_voltammetry_archive(data, metadata, self, multiple=True)
                    if not self.properties:
                        self.properties = get_biologic_properties(metadata)
        fig1 = self.make_current_density_plot()
        fig2 = self.make_current_over_voltage_plot()
        self.figures = [
            PlotlyFigure(
                label='Current Density over Voltage RHE', figure=fig1.to_plotly_json()
            ),
            PlotlyFigure(label='Current over Voltage', figure=fig2.to_plotly_json()),
        ]
        super().normalize(archive, logger)


class CE_NESD_ElectrolyserPerformanceEvaluation(
    ElectrolyserPerformanceEvaluation, EntryData
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


class CE_NESD_GalvanodynamicElectrochemicalImpedanceSpectroscopy(
    ElectrochemicalImpedanceSpectroscopy, EntryData
):
    m_def = Section(
        a_eln=dict(
            hide=[
                'metadata_file',
                'lab_id',
                'location',
                'steps',
                'instruments',
                'results',
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

    def make_nyquist_plot(self):
        fig = go.Figure(
            data=[
                go.Scatter(
                    name='Nyquist',
                    x=self.z_real,
                    y=self.z_imaginary,
                )
            ]
        )
        fig.update_layout(
            title_text='Nyquist Plot',
            xaxis={'fixedrange': False, 'title': 'Re(Z) (Ω)'},
            yaxis={'fixedrange': False, 'title': '-Im(Z) (Ω)'},
        )
        return fig

    def make_bode_plot(self):
        fig = go.Figure(
            data=[
                go.Scatter(
                    name='|Z|',
                    x=self.frequency,
                    y=self.z_modulus,
                )
            ]
        )
        fig.add_traces(go.Scatter(name='Phase(Z)', x=self.frequency, y=self.z_angle))
        fig.update_layout(
            title_text='Bode Plot',
            showlegend=True,
            xaxis={'fixedrange': False, 'type': 'log'},
            yaxis={'fixedrange': False},
        )
        return fig

    def normalize(self, archive, logger):
        if self.data_file:
            with archive.m_context.raw_file(self.data_file, 'rt') as f:
                if os.path.splitext(self.data_file)[-1] == '.mpr':
                    from baseclasses.helper.archive_builder.biologic_archive import (
                        get_biologic_properties,
                        get_eis_data,
                        get_meta_data,
                    )

                    from nomad_chemical_energy.schema_packages.file_parser.biologic_parser import (
                        get_header_and_data,
                    )

                    metadata, data = get_header_and_data(f)
                    get_eis_data(data, self)
                    get_meta_data(metadata, self)
                    if not self.properties:
                        self.properties = get_biologic_properties(metadata)
        fig1 = self.make_nyquist_plot()
        fig2 = self.make_bode_plot()
        self.figures = [
            PlotlyFigure(label='Nyquist Plot', figure=fig1.to_plotly_json()),
            PlotlyFigure(label='Bode Plot', figure=fig2.to_plotly_json()),
        ]
        super().normalize(archive, logger)


class CE_NESD_LinearSweepVoltammetry(LinearSweepVoltammetry, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'metadata_file',
                'lab_id',
                'location',
                'control',
                'charge',
                'charge_density',
                'steps',
                'cycles',
                'instruments',
                'results',
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

    def make_current_density_plot(self):
        fig = go.Figure(
            data=[
                go.Scatter(
                    name='Current Density',
                    x=self.voltage_rhe_compensated,
                    y=self.current_density,
                )
            ]
        )
        fig.update_layout(
            title_text='Current Density over Voltage RHE',
            showlegend=True,
            xaxis={'fixedrange': False},
            yaxis={'fixedrange': False},
        )
        return fig

    def make_current_over_voltage_plot(self):
        fig = go.Figure(
            data=[
                go.Scatter(
                    name='Current',
                    x=self.voltage,
                    y=self.current,
                )
            ]
        )
        fig.update_layout(
            title_text='Current over Voltage',
            showlegend=True,
            xaxis={'fixedrange': False},
            yaxis={'fixedrange': False},
        )
        return fig

    def normalize(self, archive, logger):
        if self.data_file:
            with archive.m_context.raw_file(self.data_file, 'rt') as f:
                if os.path.splitext(self.data_file)[-1] == '.mpr':
                    from baseclasses.helper.archive_builder.biologic_archive import (
                        get_biologic_properties,
                        get_voltammetry_archive,
                    )

                    from nomad_chemical_energy.schema_packages.file_parser.biologic_parser import (
                        get_header_and_data,
                    )

                    metadata, data = get_header_and_data(f)
                    get_voltammetry_archive(data, metadata, self)
                    if not self.properties:
                        self.properties = get_biologic_properties(metadata)
        fig1 = self.make_current_density_plot()
        fig2 = self.make_current_over_voltage_plot()
        self.figures = [
            PlotlyFigure(
                label='Current Density over Voltage RHE', figure=fig1.to_plotly_json()
            ),
            PlotlyFigure(label='Current over Voltage', figure=fig2.to_plotly_json()),
        ]
        super().normalize(archive, logger)


class CE_NESD_OpenCircuitVoltage(OpenCircuitVoltage, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'metadata_file',
                'lab_id',
                'location',
                'control',
                'charge',
                'charge_density',
                'steps',
                'cycles',
                'instruments',
                'results',
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

    def make_voltage_plot(self):
        fig = go.Figure(
            data=[
                go.Scatter(
                    name='Voltage',
                    x=self.time,
                    y=self.voltage,
                )
            ]
        )
        fig.update_layout(
            title_text='Voltage over Time',
            xaxis={'fixedrange': False},
            yaxis={'fixedrange': False},
        )
        return fig

    def normalize(self, archive, logger):
        if self.data_file:
            with archive.m_context.raw_file(self.data_file, 'rt') as f:
                if os.path.splitext(self.data_file)[-1] == '.mpr':
                    from baseclasses.helper.archive_builder.biologic_archive import (
                        get_biologic_properties,
                        get_voltammetry_archive,
                    )

                    from nomad_chemical_energy.schema_packages.file_parser.biologic_parser import (
                        get_header_and_data,
                    )

                    metadata, data = get_header_and_data(f)
                    get_voltammetry_archive(data, metadata, self)
                    if not self.properties:
                        self.properties = get_biologic_properties(metadata)
        fig1 = self.make_voltage_plot()
        self.figures = [
            PlotlyFigure(label='Voltage over Time', figure=fig1.to_plotly_json()),
        ]
        super().normalize(archive, logger)


class CE_NESD_PotentiodynamicElectrochemicalImpedanceSpectroscopy(
    ElectrochemicalImpedanceSpectroscopy, EntryData
):
    m_def = Section(
        a_eln=dict(
            hide=[
                'metadata_file',
                'lab_id',
                'location',
                'steps',
                'instruments',
                'results',
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

    def make_nyquist_plot(self):
        fig = go.Figure(
            data=[
                go.Scatter(
                    name='Nyquist',
                    x=self.z_real,
                    y=self.z_imaginary,
                )
            ]
        )
        fig.update_layout(
            title_text='Nyquist Plot',
            xaxis={'fixedrange': False, 'title': 'Re(Z) (Ω)'},
            yaxis={'fixedrange': False, 'title': '-Im(Z) (Ω)'},
        )
        return fig

    def make_bode_plot(self):
        fig = go.Figure(
            data=[
                go.Scatter(
                    name='|Z|',
                    x=self.frequency,
                    y=self.z_modulus,
                )
            ]
        )
        fig.add_traces(go.Scatter(name='Phase(Z)', x=self.frequency, y=self.z_angle))
        fig.update_layout(
            title_text='Bode Plot',
            showlegend=True,
            xaxis={'fixedrange': False, 'type': 'log'},
            yaxis={'fixedrange': False},
        )
        return fig

    def normalize(self, archive, logger):
        if self.data_file:
            with archive.m_context.raw_file(self.data_file, 'rt') as f:
                if os.path.splitext(self.data_file)[-1] == '.mpr':
                    from baseclasses.helper.archive_builder.biologic_archive import (
                        get_biologic_properties,
                        get_eis_data,
                        get_meta_data,
                    )

                    from nomad_chemical_energy.schema_packages.file_parser.biologic_parser import (
                        get_header_and_data,
                    )

                    metadata, data = get_header_and_data(f)
                    get_eis_data(data, self)
                    get_meta_data(metadata, self)
                    if not self.properties:
                        self.properties = get_biologic_properties(metadata)
        fig1 = self.make_nyquist_plot()
        fig2 = self.make_bode_plot()
        self.figures = [
            PlotlyFigure(label='Nyquist Plot', figure=fig1.to_plotly_json()),
            PlotlyFigure(label='Bode Plot', figure=fig2.to_plotly_json()),
        ]
        super().normalize(archive, logger)


m_package.__init_metainfo__()
