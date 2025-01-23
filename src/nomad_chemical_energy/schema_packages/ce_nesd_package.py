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
import pandas as pd

from nomad.datamodel.metainfo.plot import PlotSection, PlotlyFigure
import plotly.graph_objs as go

from nomad.datamodel.data import EntryData

from nomad.metainfo import (
    Package,
    Quantity,
    Section, SubSection, SchemaPackage)

from baseclasses import BaseMeasurement

from baseclasses.chemical_energy import (
    CENOMESample, ElectroChemicalSetup, Environment, SampleIDCENOME,
    Chronoamperometry,
    Chronopotentiometry,
    CyclicVoltammetry,
    ElectrochemicalImpedanceSpectroscopy,
    ElectrolyserPerformanceEvaluation,
    LinearSweepVoltammetry,
    OpenCircuitVoltage,
)

m_package = SchemaPackage()


# %% ####################### Entities

# TODO decide whether to reuse nome sample, environment, setup
class CE_NESD_Sample(CENOMESample, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['users', 'components', 'elemental_composition', 'id_of_preparation_protocol'],
            properties=dict(
                order=[
                    'name',
                    'lab_id',
                    'chemical_composition_or_formulas',
                    ])),
        label_quantity='sample_id')


class CE_NESD_ElectroChemicalSetup(ElectroChemicalSetup, EntryData):
    m_def = Section(
        a_eln=dict(hide=['users', 'components', 'elemental_composition', 'origin', 'substrate'],
                   properties=dict(
                       order=[
                           'name',
                           'lab_id',
                           'chemical_composition_or_formulas',
                           'setup',
                           'reference_electrode',
                           'counter_electrode',
                           'equipment'
                       ])),
    )

    setup_id = SubSection(section_def=SampleIDCENOME)


class CE_NESD_Environment(Environment, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['users', 'components', 'elemental_composition', 'origin', 'substrate'],
            properties=dict(
                editable=dict(
                    exclude=['chemical_composition_or_formulas']),
                order=[
                    'name',
                    'lab_id',
                    'chemical_composition_or_formulas',
                    'ph_value',
                    'solvent'])))

    environment_id = SubSection(section_def=SampleIDCENOME)


# %% ####################### Generic Entries


class CE_NESD_Measurement(BaseMeasurement, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'location', 'steps', 'instruments', 'results'
                ],
            properties=dict(
                order=[
                    'name', 'data_file', 'samples'
                ])),
    )

    data_file = Quantity(
        type=str,
        shape=['*'],
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))


# %% ####################### Measurements


class CE_NESD_Chronoamperometry(Chronoamperometry, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'metadata_file', 'lab_id', 'location',
                'control', 'charge', 'charge_density',
                'steps', 'cycles', 'instruments', 'results',
                ],
            properties=dict(
                order=[
                    'name',
                    'data_file',
                    'environment', 'setup', 'samples',
                    'station', 'voltage_shift', 'resistance'
                ])),
    )

    def make_current_plot(self):
        fig = go.Figure(data=[go.Scatter(name='Current', x=self.time, y=self.current,)])
        fig.update_layout(title_text='Current over Time',
                          xaxis={'fixedrange': False},
                          yaxis={'fixedrange': False})
        return fig

    def make_current_density_plot(self):
        fig = go.Figure(data=[go.Scatter(name='Current', x=self.time, y=self.current_density,)])
        fig.update_layout(title_text='Current Density over Time',
                          xaxis={'fixedrange': False},
                          yaxis={'fixedrange': False})
        return fig

    def normalize(self, archive, logger):
        if self.data_file:
            with archive.m_context.raw_file(self.data_file, "rt") as f:
                if os.path.splitext(self.data_file)[-1] == ".mpr":
                    from nomad_chemical_energy.schema_packages.file_parser.biologic_parser import get_header_and_data
                    from baseclasses.helper.archive_builder.biologic_archive import get_biologic_properties, \
                        get_voltammetry_archive
                    metadata, data = get_header_and_data(f)
                    get_voltammetry_archive(data, metadata, self)
                    if not self.properties:
                        self.properties = get_biologic_properties(metadata)
        fig1 = self.make_current_plot()
        fig2 = self.make_current_density_plot()
        self.figures = [PlotlyFigure(label='Current over Time', figure=fig1.to_plotly_json()),
                        PlotlyFigure(label='Current Density over Time', figure=fig2.to_plotly_json())]
        super(CE_NESD_Chronoamperometry, self).normalize(archive, logger)


class CE_NESD_Chronopotentiometry(Chronopotentiometry, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'metadata_file', 'lab_id', 'location',
                'control', 'charge', 'charge_density',
                'steps', 'cycles', 'instruments', 'results',
                ],
            properties=dict(
                order=[
                    'name', 'data_file',
                    'environment', 'setup', 'samples',
                    'station', 'voltage_shift', 'resistance'
                ])),
    )

    def make_voltage_plot(self):
        fig = go.Figure(data=[go.Scatter(name='Voltage', x=self.time, y=self.voltage,)])
        fig.update_layout(title_text='Voltage over Time',
                          xaxis={'fixedrange': False},
                          yaxis={'fixedrange': False})
        return fig

    def normalize(self, archive, logger):
        if self.data_file:
            with archive.m_context.raw_file(self.data_file, "rt") as f:
                if os.path.splitext(self.data_file)[-1] == ".mpr":
                    from nomad_chemical_energy.schema_packages.file_parser.biologic_parser import get_header_and_data
                    from baseclasses.helper.archive_builder.biologic_archive import get_biologic_properties, \
                        get_voltammetry_archive
                    metadata, data = get_header_and_data(f)
                    get_voltammetry_archive(data, metadata, self)
                    if not self.properties:
                        self.properties = get_biologic_properties(metadata)
        fig1 = self.make_voltage_plot()
        self.figures = [PlotlyFigure(label='Voltage over Time', figure=fig1.to_plotly_json()),]
        super(CE_NESD_Chronopotentiometry, self).normalize(archive, logger)


class CE_NESD_ConstantCurrentMode(Chronopotentiometry, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'metadata_file', 'lab_id', 'location',
                'control', 'charge', 'charge_density',
                'steps', 'cycles', 'instruments', 'results',
                ],
            properties=dict(
                order=[
                    'name', 'data_file',
                    'environment', 'setup', 'samples',
                    'station', 'voltage_shift', 'resistance'
                ])),
    )

    def normalize(self, archive, logger):
        if self.data_file:
            with archive.m_context.raw_file(self.data_file, "rt") as f:
                if os.path.splitext(self.data_file)[-1] == ".mpr":
                    from nomad_chemical_energy.schema_packages.file_parser.biologic_parser import get_header_and_data
                    from baseclasses.helper.archive_builder.biologic_archive import get_biologic_properties, \
                        get_voltammetry_archive
                    metadata, data = get_header_and_data(f)
                    get_voltammetry_archive(data, metadata, self)
                    if not self.properties:
                        self.properties = get_biologic_properties(metadata)
        super(CE_NESD_ConstantCurrentMode, self).normalize(archive, logger)



class CE_NESD_ConstantVoltageMode(Chronoamperometry, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'metadata_file', 'lab_id', 'location',
                'control', 'charge', 'charge_density',
                'steps', 'cycles', 'instruments', 'results',
                ],
            properties=dict(
                order=[
                    'name', 'data_file',
                    'environment', 'setup', 'samples',
                    'station', 'voltage_shift', 'resistance'
                ])),
    )

    def normalize(self, archive, logger):
        if self.data_file:
            with archive.m_context.raw_file(self.data_file, "rt") as f:
                if os.path.splitext(self.data_file)[-1] == ".mpr":
                    from nomad_chemical_energy.schema_packages.file_parser.biologic_parser import get_header_and_data
                    from baseclasses.helper.archive_builder.biologic_archive import get_biologic_properties, \
                        get_voltammetry_archive
                    metadata, data = get_header_and_data(f)
                    get_voltammetry_archive(data, metadata, self)
                    if not self.properties:
                        self.properties = get_biologic_properties(metadata)
        super(CE_NESD_ConstantVoltageMode, self).normalize(archive, logger)


class CE_NESD_CyclicVoltammetry(CyclicVoltammetry, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'users', 'location', 'end_time', 'steps',
                'instruments', 'results', 'lab_id',
                'voltage', 'current', 'current_density', 'voltage_rhe_uncompensated',
                'voltage_rhe_compensated', 'voltage_ref_compensated',
                'time', 'charge_density', 'control', 'charge',
                'metadata_file'
                ],
            properties=dict(
                order=[
                    'name',
                    'data_file',])),
    )

    def make_current_density_plot(self):
        fig = go.Figure()
        for cycle in self.cycles:
            fig.add_traces(go.Scatter(name='Current Density', x=cycle.voltage_rhe_compensated, y=cycle.current_density,))
        fig.update_layout(title_text='Current Density over Voltage RHE', showlegend=True, xaxis={'fixedrange': False})
        return fig

    def make_current_over_voltage_plot(self):
        fig = go.Figure()
        for cycle in self.cycles:
            fig.add_traces(go.Scatter(name='Current', x=cycle.voltage, y=cycle.current,))
        fig.update_layout(title_text='Current over Voltage', showlegend=True, xaxis={'fixedrange': False})
        return fig

    def normalize(self, archive, logger):
        if self.data_file:
            with archive.m_context.raw_file(self.data_file, "rt") as f:
                if os.path.splitext(self.data_file)[-1] == ".mpr":
                    from nomad_chemical_energy.schema_packages.file_parser.biologic_parser import get_header_and_data
                    from baseclasses.helper.archive_builder.biologic_archive import get_biologic_properties, \
                        get_voltammetry_archive
                    metadata, data = get_header_and_data(f)
                    get_voltammetry_archive(data, metadata, self, multiple=True)
                    if not self.properties:
                        self.properties = get_biologic_properties(metadata)
        fig1 = self.make_current_density_plot()
        fig2 = self.make_current_over_voltage_plot()
        self.figures = [PlotlyFigure(label='Current Density over Voltage RHE', figure=fig1.to_plotly_json()),
                        PlotlyFigure(label='Current over Voltage', figure=fig2.to_plotly_json())]
        super(CE_NESD_CyclicVoltammetry, self).normalize(archive, logger)


class CE_NESD_ElectrolyserPerformanceEvaluation(ElectrolyserPerformanceEvaluation, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'location', 'steps', 'instruments', 'results'
                ],
            properties=dict(
                order=[
                    'name',
                    'data_file',])),
    )

    def normalize(self, archive, logger):
        if self.data_file:
            with archive.m_context.raw_file(self.data_file) as f:
                # TODO difference to tdms_index files
                if os.path.splitext(self.data_file)[-1] == ".tdms":
                    from nomad_chemical_energy.schema_packages.file_parser.electrolyser_tdms_parser import get_info_and_data
                    from baseclasses.helper.archive_builder.labview_archive import get_electrolyser_properties, get_tdms_archive
                    metadata, data = get_info_and_data(f)
                    get_tdms_archive(data, self)

                    get_electrolyser_properties(metadata)
        super(CE_NESD_ElectrolyserPerformanceEvaluation, self).normalize(archive, logger)


class CE_NESD_GalvanodynamicElectrochemicalImpedanceSpectroscopy(ElectrochemicalImpedanceSpectroscopy, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'metadata_file', 'lab_id', 'location',
                'steps', 'instruments', 'results'

                ],
            properties=dict(
                order=[
                    'name', 'data_file',
                    'environment', 'setup', 'samples',
                    'station'
                ])),
    )

    def make_nyquist_plot(self):
        fig = go.Figure(data=[go.Scatter(name='Nyquist', x=self.z_real, y=self.z_imaginary,)])
        fig.update_layout(title_text='Nyquist Plot',
                          xaxis={'fixedrange': False, 'title': 'Re(Z) (Ω)'},
                          yaxis={'fixedrange': False, 'title': '-Im(Z) (Ω)'})
        return fig

    def make_bode_plot(self):
        fig = go.Figure(data=[go.Scatter(name='|Z|', x=self.frequency, y=self.z_modulus,)])
        fig.add_traces(go.Scatter(name='Phase(Z)', x=self.frequency, y=self.z_angle))
        fig.update_layout(title_text='Bode Plot',
                          showlegend=True,
                          xaxis={'fixedrange': False, 'type': 'log'},
                          yaxis={'fixedrange': False})
        return fig

    def normalize(self, archive, logger):
        if self.data_file:
            with archive.m_context.raw_file(self.data_file, "rt") as f:
                if os.path.splitext(self.data_file)[-1] == ".mpr":
                    from nomad_chemical_energy.schema_packages.file_parser.biologic_parser import get_header_and_data
                    from baseclasses.helper.archive_builder.biologic_archive import get_biologic_properties, \
                        get_eis_data, get_meta_data
                    metadata, data = get_header_and_data(f)
                    get_eis_data(data, self)
                    get_meta_data(metadata, self)
                    if not self.properties:
                        self.properties = get_biologic_properties(metadata)
        fig1 = self.make_nyquist_plot()
        fig2 = self.make_bode_plot()
        self.figures = [PlotlyFigure(label='Nyquist Plot', figure=fig1.to_plotly_json()),
                        PlotlyFigure(label='Bode Plot', figure=fig2.to_plotly_json())]
        super(CE_NESD_GalvanodynamicElectrochemicalImpedanceSpectroscopy, self).normalize(archive, logger)


class CE_NESD_LinearSweepVoltammetry(LinearSweepVoltammetry, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'metadata_file', 'lab_id', 'location',
                'control', 'charge', 'charge_density',
                'steps', 'cycles', 'instruments', 'results'
                ],
            properties=dict(
                order=[
                    'name', 'data_file',
                    'environment', 'setup', 'samples',
                    'station', 'voltage_shift', 'resistance'
                ])),
    )

    def make_current_density_plot(self):
        fig = go.Figure(data=[go.Scatter(name='Current Density', x=self.voltage_rhe_compensated, y=self.current_density,)])
        fig.update_layout(title_text='Current Density over Voltage RHE',
                          showlegend=True,
                          xaxis={'fixedrange': False},
                          yaxis={'fixedrange': False})
        return fig

    def make_current_over_voltage_plot(self):
        fig = go.Figure(data=[go.Scatter(name='Current', x=self.voltage, y=self.current,)])
        fig.update_layout(title_text='Current over Voltage',
                          showlegend=True,
                          xaxis={'fixedrange': False},
                          yaxis={'fixedrange': False})
        return fig

    def normalize(self, archive, logger):
        if self.data_file:
            with archive.m_context.raw_file(self.data_file, "rt") as f:
                if os.path.splitext(self.data_file)[-1] == ".mpr":
                    from nomad_chemical_energy.schema_packages.file_parser.biologic_parser import get_header_and_data
                    from baseclasses.helper.archive_builder.biologic_archive import get_biologic_properties, \
                        get_voltammetry_archive
                    metadata, data = get_header_and_data(f)
                    get_voltammetry_archive(data, metadata, self)
                    if not self.properties:
                        self.properties = get_biologic_properties(metadata)
        fig1 = self.make_current_density_plot()
        fig2 = self.make_current_over_voltage_plot()
        self.figures = [PlotlyFigure(label='Current Density over Voltage RHE', figure=fig1.to_plotly_json()),
                        PlotlyFigure(label='Current over Voltage', figure=fig2.to_plotly_json())]
        super(CE_NESD_LinearSweepVoltammetry, self).normalize(archive, logger)


class CE_NESD_OpenCircuitVoltage(OpenCircuitVoltage, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'metadata_file', 'lab_id', 'location',
                'control', 'charge', 'charge_density',
                'steps', 'cycles', 'instruments', 'results'
                ],
            properties=dict(
                order=[
                    'name', 'data_file',
                    'environment', 'setup', 'samples',
                    'station', 'voltage_shift', 'resistance'
                ])),
    )

    def make_voltage_plot(self):
        fig = go.Figure(data=[go.Scatter(name='Voltage', x=self.time, y=self.voltage,)])
        fig.update_layout(title_text='Voltage over Time',
                          xaxis={'fixedrange': False},
                          yaxis={'fixedrange': False})
        return fig

    def normalize(self, archive, logger):
        if self.data_file:
            with archive.m_context.raw_file(self.data_file, "rt") as f:
                if os.path.splitext(self.data_file)[-1] == ".mpr":
                    from nomad_chemical_energy.schema_packages.file_parser.biologic_parser import get_header_and_data
                    from baseclasses.helper.archive_builder.biologic_archive import get_biologic_properties, \
                        get_voltammetry_archive
                    metadata, data = get_header_and_data(f)
                    get_voltammetry_archive(data, metadata, self)
                    if not self.properties:
                        self.properties = get_biologic_properties(metadata)
        fig1 = self.make_voltage_plot()
        self.figures = [PlotlyFigure(label='Voltage over Time', figure=fig1.to_plotly_json()),]
        super(CE_NESD_OpenCircuitVoltage, self).normalize(archive, logger)


class CE_NESD_PotentiodynamicElectrochemicalImpedanceSpectroscopy(ElectrochemicalImpedanceSpectroscopy, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'metadata_file', 'lab_id', 'location',
                'steps', 'instruments', 'results'
            ],
            properties=dict(
                order=[
                    'name', 'data_file',
                    'environment', 'setup', 'samples',
                    'station'
                ])),
    )

    def make_nyquist_plot(self):
        fig = go.Figure(data=[go.Scatter(name='Nyquist', x=self.z_real, y=self.z_imaginary,)])
        fig.update_layout(title_text='Nyquist Plot',
                          xaxis={'fixedrange': False, 'title': 'Re(Z) (Ω)'},
                          yaxis={'fixedrange': False, 'title': '-Im(Z) (Ω)'})
        return fig

    def make_bode_plot(self):
        fig = go.Figure(data=[go.Scatter(name='|Z|', x=self.frequency, y=self.z_modulus,)])
        fig.add_traces(go.Scatter(name='Phase(Z)', x=self.frequency, y=self.z_angle))
        fig.update_layout(title_text='Bode Plot',
                          showlegend=True,
                          xaxis={'fixedrange': False, 'type': 'log'},
                          yaxis={'fixedrange': False})
        return fig

    def normalize(self, archive, logger):
        if self.data_file:
            with archive.m_context.raw_file(self.data_file, "rt") as f:
                if os.path.splitext(self.data_file)[-1] == ".mpr":
                    from nomad_chemical_energy.schema_packages.file_parser.biologic_parser import get_header_and_data
                    from baseclasses.helper.archive_builder.biologic_archive import get_biologic_properties, \
                        get_eis_data, get_meta_data
                    metadata, data = get_header_and_data(f)
                    get_eis_data(data, self)
                    get_meta_data(metadata, self)
                    if not self.properties:
                        self.properties = get_biologic_properties(metadata)
        fig1 = self.make_nyquist_plot()
        fig2 = self.make_bode_plot()
        self.figures = [PlotlyFigure(label='Nyquist Plot', figure=fig1.to_plotly_json()),
                        PlotlyFigure(label='Bode Plot', figure=fig2.to_plotly_json())]
        super(CE_NESD_PotentiodynamicElectrochemicalImpedanceSpectroscopy, self).normalize(archive, logger)


m_package.__init_metainfo__()
