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

from nomad.metainfo import (Section)
from nomad.datamodel.data import EntryData

from baseclasses.chemical_energy import (
    CENECCElectrode,
    PotentiometryGasChromatographyMeasurement
)

# %% ####################### Entities

class CE_NECC_Electrode(CENECCElectrode, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=["users", "origin", "elemental_composition",
                  "components", "chemical_composition_or_formulas"],
            properties=dict(
                order=[
                    "name",
                    "lab_id",
                    "recipe_id",
                    "recipe_type",
                    "element",
                    "deposition_method"
                ])),
        label_quantity='sample_id')

# %%####################################### Measurements

class CE_NECC_PotentiometryGasChromatographyMeasurement(PotentiometryGasChromatographyMeasurement, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'location', 'steps', 'samples', 'atmosphere', 'instruments'
                ],
            properties=dict(
                order=[
                    'name', 'properties', 'gaschromatographies',
                    'potentiometry', 'thermocouple', 'results'
                    ])),
                a_plot=[{
                    'label': 'Potential-dependent Faradaic efficiencies',
                    'x': 'potentiometry/working_electrode_potential',
                    'y': ['results/gas_results/faradaic_efficiency',
                          'results/total_flow_rate'],
                    'layout': {"showlegend": True,
                               'yaxis': {
                                   "fixedrange": False},
                               'xaxis': {
                                   "fixedrange": False}}},
                    {
                        'label': 'Current–voltage characteristics and electrode temperatures',
                        'x': 'potentiometry/working_electrode_potential',
                        'y': ['results/gas_results/current',
                              'thermocouple/temperature_cathode'],
                        'layout': {"showlegend": True,
                                   'yaxis': {
                                       "fixedrange": False},
                                   'xaxis': {
                                       "fixedrange": False}},
                    }])

    def normalize(self, archive, logger):
        super(CE_NECC_PotentiometryGasChromatographyMeasurement, self).normalize(archive, logger)

