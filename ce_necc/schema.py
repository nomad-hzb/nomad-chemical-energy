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

from nomad.metainfo import (Section)
from nomad.datamodel.data import EntryData

from baseclasses.chemical_energy import (
    CENECCElectrode,
    CENECCElectrodeRecipe,
    PotentiometryGasChromatographyMeasurement,
    NECCExperimentalProperties,
    GasChromatographyOutput,
    PotentiostatOutput,
    ThermocoupleOutput,
    PotentiometryGasChromatographyResults
)

# %% ####################### Entities

class CE_NECC_ElectrodeRecipe(CENECCElectrodeRecipe, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=["users", "origin", "chemical_composition_or_formulas", "elemental_composition",
                  "components"],
            properties=dict(
                order=[
                    "name",
                    "lab_id",
                    "recipe_type",
                    "deposition_method",
                    "deposition_temperature",
                    "n2_deposition_pressure",
                    "mass_loading"
                ])),
        label_quantity='sample_id') # TODO what is this?

class CE_NECC_Electrode(CENECCElectrode, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=["chemical_composition_or_formulas", "origin", "elemental_composition", "components"],
            properties=dict(
                order=[
                    "name",
                    "lab_id",
                    "recipe",
                    "remarks"
                ])),
        label_quantity='electrode_id')

# %%####################################### Measurements

class CE_NECC_PotentiometryGasChromatographyMeasurement(PotentiometryGasChromatographyMeasurement, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'location', 'steps', 'samples', 'atmosphere', 'instruments', 'results', 'method'
                ],
            properties=dict(
                order=[
                    'name', 'properties', 'gaschromatographies',
                    'potentiometry', 'thermocouple', 'fe_results'
                    ])),
                a_plot=[{
                    'label': 'Potential-dependent Faradaic efficiencies',
                    'x': 'potentiometry/working_electrode_potential',
                    'y': ['fe_results/gas_results/faradaic_efficiency',
                          'fe_results/total_flow_rate'],
                    'layout': {"showlegend": True,
                               'yaxis': {
                                   "fixedrange": False},
                               'xaxis': {
                                   "fixedrange": False}}},
                    {
                        'label': 'Current–voltage characteristics and electrode temperatures',
                        'x': 'potentiometry/working_electrode_potential',
                        'y': ['fe_results/gas_results/current',
                              'thermocouple/temperature_cathode'],
                        'layout': {"showlegend": True,
                                   'yaxis': {
                                       "fixedrange": False},
                                   'xaxis': {
                                       "fixedrange": False}},
                    }])

    def normalize(self, archive, logger):

        with archive.m_context.raw_file(archive.metadata.mainfile) as f:
            path = os.path.dirname(f.name)

        if self.data_file:
            if self.properties is None:
                from baseclasses.helper.file_parser.necc_excel_parser import read_properties
                experimental_properties_dict = read_properties(os.path.join(path, self.data_file))
                self.properties = NECCExperimentalProperties()
                for attribute_name, value in experimental_properties_dict.items():
                    # TODO setattr should be avoided but I don't know better way when having that many attributes
                    setattr(self.properties, attribute_name, value)

            if self.potentiometry is None:
                from baseclasses.helper.file_parser.necc_excel_parser import read_potentiostat_data
                date_time, time, current, working_electrode_potential = read_potentiostat_data(os.path.join(path, self.data_file))
                self.potentiometry = PotentiostatOutput(datetime=date_time,
                                                        time=time,
                                                        current=current,
                                                        working_electrode_potential=working_electrode_potential)

            if self.thermocouple is None:
                from baseclasses.helper.file_parser.necc_excel_parser import read_thermocouple_data
                date_time, pressure, temperature_cathode, temperature_anode = read_thermocouple_data(os.path.join(path, self.data_file))
                self.thermocouple = ThermocoupleOutput(datetime=date_time,
                                                       pressure=pressure,
                                                       temperature_cathode=temperature_cathode,
                                                       temperature_anode=temperature_anode)

            from baseclasses.helper.file_parser.necc_excel_parser import read_gaschromatography_data
            gaschromatography_measurements = []
            experiment_name, datetimes, gas_types, retention_times, areas, ppms = read_gaschromatography_data(os.path.join(path, self.data_file))
            for index in range(len(gas_types)):
                gaschromatography_measurements.append(GasChromatographyOutput(
                    experiment_name=experiment_name,
                    datetime=datetimes,
                    gas_type=gas_types.iat[index],
                    retention_time=retention_times.iloc[:, index],
                    area=areas.iloc[:, index],
                    ppm=ppms.iloc[:, index]
                ))
            self.gaschromatographies = gaschromatography_measurements

            if self.fe_results is None:
                from baseclasses.helper.file_parser.necc_excel_parser import read_results_data
                total_flow_rate, total_fe, gas_measurements = read_results_data(os.path.join(path, self.data_file))
                self.fe_results = PotentiometryGasChromatographyResults(total_flow_rate=total_flow_rate,
                                                                     gas_results=gas_measurements,
                                                                     total_fe=total_fe)

        super(CE_NECC_PotentiometryGasChromatographyMeasurement, self).normalize(archive, logger)
