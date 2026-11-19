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

from baseclasses.characterizations import XRD, XRDData
from baseclasses.characterizations.electron_microscopy import SEM_Microscope_Merlin
from baseclasses.chemical_energy import (
    CyclicVoltammetry,
    ElectrochemicalImpedanceSpectroscopy,
    OpenCircuitVoltage,
)
from nomad.datamodel.data import EntryData
from nomad.datamodel.metainfo.plot import PlotlyFigure, PlotSection

# from nomad.units import ureg
from nomad.metainfo import SchemaPackage, Section

from nomad_chemical_energy.schema_packages.utilities.plotly_figure_helpers import (
    make_bode_plot,
    make_current_density_over_voltage_cv_plot,
    make_current_density_over_voltage_rhe_cv_plot,
    make_current_over_voltage_cv_plot,
    make_nyquist_plot,
    make_voltage_plot,
    make_xrd_data_plot,
    make_xrd_measurements_plot,
)

m_package = SchemaPackage()


# %% ####################### Entities

# %% Microscopy

# class Wannsee_EM_M013_TEM_Imaging_lambda750(TEM_lambda750k, EntryData):
#     m_def = Section(
#         a_eln=dict(hide=['lab_id', 'author', 'user']))


# class Wannsee_EM_M013_TEM_Imaging_GatamUS1000(TEM_Gatam_US1000, EntryData):
#     m_def = Section(
#         a_eln=dict(hide=['lab_id', 'author', 'user']))


# class Wannsee_EM_M013_TEM_Scanning_HAADE(TEM_HAADE, EntryData):
#     m_def = Section(
#         a_eln=dict(hide=['lab_id', 'author', 'user']))


# class Wannsee_EM_M013_TEM_Scanning_EDX(TEM_EDX, EntryData):
#     m_def = Section(
#         a_eln=dict(hide=['lab_id', 'author', 'user']))


# class Wannsee_EM_M013_TEM_Session(TEM_Session, EntryData):
#     m_def = Section(
#         a_eln=dict(hide=['lab_id', 'author', 'user']))


# class Wannsee_EM_M013_TEM_Configuration(TEMMicroscopeConfiguration, EntryData):
#     m_def = Section(
#         a_eln=dict(hide=['lab_id', 'author', 'user']))


class Wannsee_EM_M001_SEM_Merlin(SEM_Microscope_Merlin, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time',
                'steps',
                'instruments',
                'results',
                'detector_data_folder',
                'external_sample_url',
            ],
            properties=dict(order=['name', 'detector_data', 'samples', 'solution']),
        )
    )


# %%
class Wannsee_D8_XRD_Bruker(XRD, EntryData, PlotSection):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time',
                'steps',
                'instruments',
                'results',
                'steps',
                'instruments',
                'results',
                'metadata_file',
                'shifted_data',
                'identifier',
            ],
            properties=dict(order=['name', 'data_file', 'samples', 'solution']),
        ),
    )

    def normalize(self, archive, logger):
        self.identifier = 'HZB_WANNSEE'
        super().normalize(archive, logger)
        fig1 = make_xrd_measurements_plot(self.measurements, self.shifted_data)
        self.figures = [
            PlotlyFigure(label='XRD', figure=json.loads(fig1.to_json())),
        ]


class Wannsee_XRD_XY(XRD, EntryData, PlotSection):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time',
                'steps',
                'instruments',
                'results',
                'steps',
                'instruments',
                'results',
                'metadata_file',
                'shifted_data',
                'identifier',
            ],
            properties=dict(order=['name', 'data_file', 'samples', 'solution']),
        ),
    )

    def normalize(self, archive, logger):
        if self.data_file:
            with archive.m_context.raw_file(self.data_file, 'rt') as f:
                if os.path.splitext(self.data_file)[-1] == '.xy' and self.data is None:
                    import pandas as pd

                    if 'Id' in f.readline():
                        skiprows = 1
                        data = pd.read_csv(
                            f, sep=' |\t', header=None, skiprows=skiprows
                        )
                    else:
                        skiprows = 0
                        data = pd.read_csv(
                            f, sep=' |\t', header=None, skiprows=skiprows
                        )
                    print(data)
                    self.data = XRDData(angle=data[0], intensity=data[1])
        super().normalize(archive, logger)
        fig1 = make_xrd_data_plot(self.data)
        self.figures = [
            PlotlyFigure(label='XRD', figure=json.loads(fig1.to_json())),
        ]


class Wannsee_B307_CyclicVoltammetry_ECLab(CyclicVoltammetry, EntryData, PlotSection):
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
                'station',
                'voltage',
                'current',
                'current_density',
                'charge_density',
                'control',
                'charge',
                'time',
                'voltage_rhe_uncompensated',
                'voltage_ref_compensated',
                'voltage_rhe_compensated',
            ],
            properties=dict(
                order=['name', 'data_file', 'environment', 'setup', 'samples']
            ),
        ),
    )

    def normalize(self, archive, logger):
        super().normalize(archive, logger)
        fig1 = make_current_over_voltage_cv_plot(self.cycles)
        fig2 = make_current_density_over_voltage_rhe_cv_plot(self.cycles)
        self.figures = [
            PlotlyFigure(
                label='Current over Voltage',
                figure=json.loads(fig1.to_json()),
            ),
            PlotlyFigure(
                label='Current Density over Voltage RHE',
                figure=json.loads(fig2.to_json()),
            ),
        ]

    # def normalize(self, archive, logger):
    #     if self.data_file:
    #         with archive.m_context.raw_file(self.data_file, "rt") as f:

    #             if os.path.splitext(self.data_file)[-1] == ".mpt":
    #                 from nomad_chemical_energy.schema_packages.file_parser.mps_file_parser import read_mpt_file
    #                 from baseclasses.helper.archive_builder.mpt_get_archive import get_voltammetry_data, get_cv_properties

    #                 metadata, data, technique = read_mpt_file(f)
    #                 get_voltammetry_data(data, self)

    #                 if "Cyclic" in technique and self.properties is None:
    #                     self.properties = get_cv_properties(metadata)
    #     super(Wannsee_B307_CyclicVoltammetry_ECLab,
    #           self).normalize(archive, logger)


class Wannsee_B307_CyclicVoltammetry_CorrWare(
    CyclicVoltammetry,
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
                'station',
                'voltage',
                'current',
                'current_density',
                'charge_density',
                'control',
                'charge',
                'time',
                'voltage_rhe_uncompensated',
                'voltage_ref_compensated',
                'voltage_rhe_compensated',
            ],
            properties=dict(
                order=['name', 'data_file', 'environment', 'setup', 'samples']
            ),
        ),
    )

    def normalize(self, archive, logger):
        super().normalize(archive, logger)
        fig1 = make_current_density_over_voltage_cv_plot(self.cycles)
        fig2 = make_current_density_over_voltage_rhe_cv_plot(self.cycles)
        self.figures = [
            PlotlyFigure(
                label='Current Density over Voltage',
                figure=json.loads(fig1.to_json()),
            ),
            PlotlyFigure(
                label='Current Density over Voltage RHE',
                figure=json.loads(fig2.to_json()),
            ),
        ]

    # def normalize(self, archive, logger):
    #     if self.data_file:
    #         with archive.m_context.raw_file(self.data_file, "rt") as f:
    #             if os.path.splitext(self.data_file)[-1] == ".cor":
    #                 from nomad_chemical_energy.schema_packages.file_parser.corr_ware_parser import get_header_data_corrware
    #                 from baseclasses.helper.archive_builder.corr_ware_archive import \
    #                     (get_core_ware_archive_properties, get_core_ware_archive)

    #                 metadata, data, technique = get_header_data_corrware(f)
    #                 get_core_ware_archive(self, metadata, data)
    #                 if "Cyclic" in technique and self.properties is None:
    #                     self.properties = get_core_ware_archive_properties(
    #                         metadata)

    #     super(Wannsee_B307_CyclicVoltammetry_CorrWare,
    #           self).normalize(archive, logger)


class Wannsee_B307_ElectrochemicalImpedanceSpectroscopy_ECLab(
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
                'station',
            ],
            properties=dict(
                order=['name', 'data_file', 'environment', 'setup', 'samples']
            ),
        ),
    )

    def normalize(self, archive, logger):
        super().normalize(archive, logger)
        fig1 = make_nyquist_plot(z_real=self.z_real, z_imaginary=self.z_imaginary)
        fig2 = make_bode_plot(
            frequency=self.frequency, z_modulus=self.z_modulus, z_angle=self.z_angle
        )
        self.figures = [
            PlotlyFigure(label='Nyquist Plot', figure=json.loads(fig1.to_json())),
            PlotlyFigure(label='Bode Plot', figure=json.loads(fig2.to_json())),
        ]

    # def normalize(self, archive, logger):
    #     if self.data_file:
    #         with archive.m_context.raw_file(self.data_file, "rt") as f:

    #             if os.path.splitext(self.data_file)[-1] == ".mpt":
    #                 from nomad_chemical_energy.schema_packages.file_parser.mps_file_parser import read_mpt_file
    #                 from baseclasses.helper.archive_builder.mpt_get_archive import get_eis_data, get_meta_data, get_eis_properties

    #                 metadata, data, technique = read_mpt_file(f)
    #                 get_eis_data(data, self)
    #                 get_meta_data(metadata, self)

    #                 if "Potentio" in technique and self.properties is None:
    #                     self.properties = get_eis_properties(metadata)

    #     super(
    #         Wannsee_B307_ElectrochemicalImpedanceSpectroscopy_ECLab,
    #         self).normalize(
    #         archive,
    #         logger)


class Wannsee_B307_OpenCircuitVoltage_ECLab(OpenCircuitVoltage, EntryData, PlotSection):
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
                'station',
            ],
            properties=dict(
                order=[
                    'name',
                    'data_file',
                    'environment',
                    'setup',
                    'samples',
                ]
            ),
        ),
    )

    def normalize(self, archive, logger):
        super().normalize(archive, logger)
        fig1 = make_voltage_plot(self.time, self.voltage)
        self.figures = [
            PlotlyFigure(label='Voltage over Time', figure=json.loads(fig1.to_json())),
        ]

    # def normalize(self, archive, logger):
    #     if self.data_file:
    #         with archive.m_context.raw_file(self.data_file, "rt") as f:

    #             if os.path.splitext(self.data_file)[-1] == ".mpt":
    #                 from nomad_chemical_energy.schema_packages.file_parser.mps_file_parser import read_mpt_file
    #                 from baseclasses.helper.archive_builder.mpt_get_archive import get_voltammetry_data, get_ocv_properties

    #                 metadata, data, technique = read_mpt_file(f)
    #                 get_voltammetry_data(data, self)

    #                 if "Open Circuit Voltage" in technique and self.properties is None:
    #                     self.properties = get_ocv_properties(metadata)
    #     super(Wannsee_B307_OpenCircuitVoltage_ECLab,
    #           self).normalize(archive, logger)


m_package.__init_metainfo__()
