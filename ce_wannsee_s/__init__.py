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

# from nomad.units import ureg
from nomad.metainfo import (
    Package,
    Section)
from nomad.datamodel.data import EntryData


from baseclasses.characterizations import (
    XRD, XRDData
)

from baseclasses.chemical_energy import (
    CyclicVoltammetry,
    OpenCircuitVoltage,
    ElectrochemicalImpedanceSpectroscopy,
)

from baseclasses.characterizations.electron_microscopy import (
    SEM_Microscope_Merlin
)

m_package2 = Package(name='ce-wannsee')


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
        a_eln=dict(hide=['lab_id',
                         'users',
                         "location",
                         'end_time',  'steps', 'instruments', 'results', "detector_data_folder", "external_sample_url"],
                   properties=dict(
                       order=[
                           "name",
                           "detector_data",
                           "samples", "solution"])))


# %%
class Wannsee_D8_XRD_Bruker(XRD, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                "location",
                'end_time',  'steps', 'instruments', 'results',  'steps', 'instruments', 'results',
                "metadata_file",
                "shifted_data",
                "identifier"],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "samples", "solution"])),
        a_plot=[
            {
                'x': [
                    'measurements/:/angle',
                    'shifted_data/:/angle'],
                'y': [
                    'measurements/:/intensity',
                    'shifted_data/:/intensity'],
                'layout': {
                    'yaxis': {
                        "fixedrange": False,
                        "title": "Counts"},
                    'xaxis': {
                        "fixedrange": False}}},
        ])

    def normalize(self, archive, logger):
        self.identifier = "HZB_WANNSEE"
        super(Wannsee_D8_XRD_Bruker, self).normalize(archive, logger)


class Wannsee_XRD_XY(XRD, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                "location",
                'end_time',  'steps', 'instruments', 'results',  'steps', 'instruments', 'results',
                "metadata_file",
                "shifted_data",
                "identifier"],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "samples", "solution"])),
        a_plot=[
            {
                'x': [
                    'data/angle'],
                'y': [
                    'data/intensity'],
                'layout': {
                    'yaxis': {
                        "fixedrange": False,
                        "title": "Counts"},
                    'xaxis': {
                        "fixedrange": False}}},
        ])

    def normalize(self, archive, logger):

        if self.data_file:
            with archive.m_context.raw_file(self.data_file) as f:

                if os.path.splitext(self.data_file)[-1] == ".xy" and self.data is None:
                    import pandas as pd
                    data = pd.read_csv(f.name, sep="\t", header=None)
                    print(data)
                    self.data = XRDData(angle=data[0], intensity=data[1])
        super(Wannsee_XRD_XY, self).normalize(archive, logger)


class Wannsee_B307_CyclicVoltammetry_ECLab(CyclicVoltammetry, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'solution',
                'users',
                "location",
                'end_time',  'steps', 'instruments', 'results',
                "metadata_file", "station",  "voltage", "current",
                "current_density", "charge_density", "control", "charge",
                "time", "voltage_rhe_uncompensated",
                "voltage_ref_compensated", "voltage_rhe_compensated"],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "environment",
                    "setup",
                    "samples"])),
        a_plot=[
            {
                'x': 'cycles/:/voltage',
                'y': 'cycles/:/current',
                'layout': {
                    "showlegend": True,
                    'yaxis': {
                        "fixedrange": False},
                    'xaxis': {
                        "fixedrange": False}},
            }, {
                'label': 'Current Density over Voltage RHE',
                'x': 'cycles/:/voltage_rhe_compensated',
                'y': 'cycles/:/current_density',
                'layout': {
                    "showlegend": True,
                    'yaxis': {
                        "fixedrange": False},
                    'xaxis': {
                        "fixedrange": False}},
            }])

    def normalize(self, archive, logger):
        if self.data_file:
            with archive.m_context.raw_file(self.data_file) as f:

                if os.path.splitext(self.data_file)[-1] == ".mpt":
                    from baseclasses.helper.file_parser.mps_file_parser import read_mpt_file
                    from baseclasses.helper.archive_builder.mpt_get_archive import get_voltammetry_data, get_cv_properties

                    metadata, data, technique = read_mpt_file(f.name)
                    get_voltammetry_data(data, self)

                    if "Cyclic" in technique and self.properties is None:
                        self.properties = get_cv_properties(metadata)
        super(Wannsee_B307_CyclicVoltammetry_ECLab,
              self).normalize(archive, logger)


class Wannsee_B307_CyclicVoltammetry_CorrWare(CyclicVoltammetry, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'solution',
                'users',
                "location",
                'end_time',  'steps', 'instruments', 'results',
                "metadata_file", "station",  "voltage", "current",
                "current_density", "charge_density", "control", "charge",
                "time", "voltage_rhe_uncompensated",
                "voltage_ref_compensated", "voltage_rhe_compensated"],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "environment",
                    "setup",
                    "samples"])),
        a_plot=[
            {
                'x': 'cycles/:/voltage',
                'y': 'cycles/:/current_density',
                'layout': {
                    "showlegend": True,
                    'yaxis': {
                        "fixedrange": False},
                    'xaxis': {
                        "fixedrange": False}},
            }, {
                'label': 'Current Density over Voltage RHE',
                'x': 'cycles/:/voltage_rhe_compensated',
                'y': 'cycles/:/current_density',
                'layout': {
                    "showlegend": True,
                    'yaxis': {
                        "fixedrange": False},
                    'xaxis': {
                        "fixedrange": False}},
            },])

    def normalize(self, archive, logger):
        if self.data_file:
            with archive.m_context.raw_file(self.data_file) as f:
                if os.path.splitext(self.data_file)[-1] == ".cor":
                    from baseclasses.helper.file_parser.corr_ware_parser import get_header_data_corrware
                    from baseclasses.helper.archive_builder.corr_ware_archive import \
                        (get_core_ware_archive_properties, get_core_ware_archive)

                    metadata, data, technique = get_header_data_corrware(
                        filename=f.name)
                    get_core_ware_archive(self, metadata, data)
                    if "Cyclic" in technique and self.properties is None:
                        self.properties = get_core_ware_archive_properties(
                            metadata)

        super(Wannsee_B307_CyclicVoltammetry_CorrWare,
              self).normalize(archive, logger)


class Wannsee_B307_ElectrochemicalImpedanceSpectroscopy_ECLab(
        ElectrochemicalImpedanceSpectroscopy, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'solution',
                'users', "location", 'end_time',  'steps', 'instruments', 'results', "metadata_file", "station"],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "environment",
                    "setup",
                    "samples"
                ])),
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

                if os.path.splitext(self.data_file)[-1] == ".mpt":
                    from baseclasses.helper.file_parser.mps_file_parser import read_mpt_file
                    from baseclasses.helper.archive_builder.mpt_get_archive import get_eis_data, get_meta_data, get_eis_properties

                    metadata, data, technique = read_mpt_file(
                        filename=f.name)
                    get_eis_data(data, self)
                    get_meta_data(metadata, self)

                    if "Potentio" in technique and self.properties is None:
                        self.properties = get_eis_properties(metadata)

        super(
            Wannsee_B307_ElectrochemicalImpedanceSpectroscopy_ECLab,
            self).normalize(
            archive,
            logger)


class Wannsee_B307_OpenCircuitVoltage_ECLab(OpenCircuitVoltage, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'solution',
                'users', "location", 'end_time',  'steps', 'instruments', 'results', "metadata_file", "station"],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "environment",
                    "setup",
                    "samples",
                ])),
        a_plot=[
            {
                'label': 'Voltage',
                'x': 'time',
                'y': 'voltage',
                'layout': {
                    'yaxis': {
                        "fixedrange": False},
                    'xaxis': {
                        "fixedrange": False}},
            }])

    def normalize(self, archive, logger):
        if self.data_file:
            with archive.m_context.raw_file(self.data_file) as f:

                if os.path.splitext(self.data_file)[-1] == ".mpt":
                    from baseclasses.helper.file_parser.mps_file_parser import read_mpt_file
                    from baseclasses.helper.archive_builder.mpt_get_archive import get_voltammetry_data, get_ocv_properties

                    metadata, data, technique = read_mpt_file(f.name)
                    get_voltammetry_data(data, self)

                    if "Open Circuit Voltage" in technique and self.properties is None:
                        self.properties = get_ocv_properties(metadata)
        super(Wannsee_B307_OpenCircuitVoltage_ECLab,
              self).normalize(archive, logger)
