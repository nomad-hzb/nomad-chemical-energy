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


# %% ####################### Measurements


class CE_NESD_Chronoamperometry(Chronoamperometry, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[

                ],
            properties=dict(
                order=[
                    'name',
                    'data_file',])),
    )

    def normalize(self, archive, logger):
        super(CE_NESD_Chronoamperometry, self).normalize(archive, logger)


class CE_NESD_Chronopotentiometry(Chronopotentiometry, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[

                ],
            properties=dict(
                order=[
                    'name',
                    'data_file',])),
    )

    def normalize(self, archive, logger):
        super(CE_NESD_Chronopotentiometry, self).normalize(archive, logger)


class CE_NESD_ConstantCurrentMode(Chronopotentiometry, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[

                ],
            properties=dict(
                order=[
                    'name',
                    'data_file',])),
    )

    def normalize(self, archive, logger):
        super(CE_NESD_ConstantCurrentMode, self).normalize(archive, logger)



class CE_NESD_ConstantVoltageMode(Chronoamperometry, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[

                ],
            properties=dict(
                order=[
                    'name',
                    'data_file',])),
    )

    def normalize(self, archive, logger):
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

    def make_current_density_figure(self):
        fig = go.Figure()
        for cycle in self.cycles:
            fig.add_traces(go.Scatter(name='Current Density', x=cycle.voltage_rhe_compensated, y=cycle.current_density,))
        fig.update_layout(title_text='Current Density over Voltage RHE', showlegend=True, xaxis={'fixedrange': False})
        return fig

    def make_current_over_voltage_figure(self):
        fig = go.Figure()
        for cycle in self.cycles:
            fig.add_traces(go.Scatter(name='Current', x=cycle.voltage, y=cycle.current,))
        fig.update_layout(title_text='Current over Voltage', showlegend=True, xaxis={'fixedrange': False})
        return fig

    def normalize(self, archive, logger):
        if self.data_file:
            with archive.m_context.raw_file(self.data_file) as f:
                if os.path.splitext(self.data_file)[-1] == ".mpr":
                    from nomad_chemical_energy.schema_packages.file_parser.biologic_parser import get_header_and_data
                    from baseclasses.helper.archive_builder.biologic_archive import get_biologic_properties, \
                        get_voltammetry_archive
                    metadata, data = get_header_and_data(filename=f.name)
                    get_voltammetry_archive(data, metadata, self, multiple=True)
                    if not self.properties:
                        self.properties = get_biologic_properties(metadata)
        fig1 = self.make_current_density_figure()
        fig2 = self.make_current_over_voltage_figure()
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
                    metadata, data = get_info_and_data(filename=f.name)
                    get_tdms_archive(data, self)

                    get_electrolyser_properties(metadata)
        super(CE_NESD_ElectrolyserPerformanceEvaluation, self).normalize(archive, logger)


class CE_NESD_GalvanodynamicElectrochemicalImpedanceSpectroscopy(ElectrochemicalImpedanceSpectroscopy, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[

                ],
            properties=dict(
                order=[
                    'name',
                    'data_file',])),
    )

    def normalize(self, archive, logger):
        super(CE_NESD_GalvanodynamicElectrochemicalImpedanceSpectroscopy, self).normalize(archive, logger)


class CE_NESD_LinearSweepVoltammetry(LinearSweepVoltammetry, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[

                ],
            properties=dict(
                order=[
                    'name',
                    'data_file',])),
    )

    def normalize(self, archive, logger):
        super(CE_NESD_LinearSweepVoltammetry, self).normalize(archive, logger)


class CE_NESD_OpenCircuitVoltage(OpenCircuitVoltage, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[

                ],
            properties=dict(
                order=[
                    'name',
                    'data_file',])),
    )

    def normalize(self, archive, logger):
        super(CE_NESD_OpenCircuitVoltage, self).normalize(archive, logger)


class CE_NESD_PotentiodynamicElectrochemicalImpedanceSpectroscopy(ElectrochemicalImpedanceSpectroscopy, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[

                ],
            properties=dict(
                order=[
                    'name',
                    'data_file',])),
    )

    def normalize(self, archive, logger):
        super(CE_NESD_PotentiodynamicElectrochemicalImpedanceSpectroscopy, self).normalize(archive, logger)


m_package.__init_metainfo__()
