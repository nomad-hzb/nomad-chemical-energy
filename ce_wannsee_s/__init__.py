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

# from nomad.units import ureg
from nomad.metainfo import (
    Package,
    Section)
from nomad.datamodel.data import EntryData


from baseclasses.characterizations import (
    XRD
)

from baseclasses.chemical_energy import (
    CyclicVoltammetry,
    OpenCircuitVoltage,
    ElectrochemicalImpedanceSpectroscopy,
)

m_package2 = Package(name='ce-wannsee')


# %% ####################### Entities
class Wannsee_D8_XRD_Bruker(XRD, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                "location",
                "end_time",
                "metadata_file",
                "shifted_data",
                "identifier"],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "samples"])),
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


class Wannsee_B307_CyclicVoltammetry_ECLab(CyclicVoltammetry, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'solution',
                'users',
                "location",
                "end_time",
                "metadata_file", "station"],
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
                'x': 'cycles/:/voltage_rhe',
                'y': 'cycles/:/current_density',
                'layout': {
                    "showlegend": True,
                    'yaxis': {
                        "fixedrange": False},
                    'xaxis': {
                        "fixedrange": False}},
            }])


class Wannsee_B307_CyclicVoltammetry_CorrWare(CyclicVoltammetry, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'solution',
                'users',
                "location",
                "end_time",
                "metadata_file", "station"],
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
                'x': 'cycles/:/voltage_rhe',
                'y': 'cycles/:/current_density',
                'layout': {
                    "showlegend": True,
                    'yaxis': {
                        "fixedrange": False},
                    'xaxis': {
                        "fixedrange": False}},
            },])


class Wannsee_B307_ElectrochemicalImpedanceSpectroscopy_ECLab(
        ElectrochemicalImpedanceSpectroscopy, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'solution',
                'users', "location", "end_time", "metadata_file", "station"],
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


class Wannsee_B307_OpenCircuitVoltage_ECLab(OpenCircuitVoltage, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'solution',
                'users', "location", "end_time", "metadata_file", "station"],
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
