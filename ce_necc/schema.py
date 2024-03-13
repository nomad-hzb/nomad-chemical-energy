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

from datetime import datetime

from nomad.metainfo import (Section)
from nomad.datamodel.data import EntryData

from baseclasses.chemical_energy import (
    CENECCElectrode,
    PotentiometryGasChromatographyMeasurement,
    NECCExperimentalProperties,
    GasChromatographyOutput,
    PotentiostatOutput,
    ThermocoupleOutput,
    PotentiometryGasChromatographyResults
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

        with archive.m_context.raw_file(archive.metadata.mainfile) as f:
            path = os.path.dirname(f.name)

        if self.data_file:
            gaschromatography_measurements = []

            if self.properties is None:
                # TODO fill properties with meaningful values
                self.properties = NECCExperimentalProperties(membrane_thickness=45)

            if self.potentiometry is None:
                # TODO move methods in helpers file and import it
                # from baseclasses.helper.file_parser.conductivity_parser import read_conductivity
                date_time, time, current, working_electrode_potential = read_potentiostat_data(os.path.join(path, self.data_file))
                self.potentiometry = PotentiostatOutput(datetime=date_time,
                                                        time=time,
                                                        current=current,
                                                        working_electrode_potential=working_electrode_potential)

            if self.thermocouple is None:
                # TODO move methods in helpers file and import it
                date_time, pressure, temperature_cathode, temperature_anode = read_thermocouple_data(os.path.join(path, self.data_file))
                self.thermocouple = ThermocoupleOutput(datetime=date_time,
                                                       pressure=pressure,
                                                       temperature_cathode=temperature_cathode,
                                                       temperature_anode=temperature_anode)

            gas_type, retention_time, area = read_gaschromatography_data(os.path.join(path, self.data_file))
            gaschromatography_measurements.append(GasChromatographyOutput(
                #experiment_name='',
                #datetime='',
                gas_type=gas_type,
                retention_time=retention_time,
                area=area,
                #ppm=''),
            ))

            self.gaschromatographies = gaschromatography_measurements

        super(CE_NECC_PotentiometryGasChromatographyMeasurement, self).normalize(archive, logger)


def read_potentiostat_data(file):
    data = pd.read_excel(file, sheet_name='Raw Data', header=1)

    date_time = pd.to_datetime(data['time/s'])
    # TODO compute real time/s
    time = 0
    current = data['<I>/mA']
    working_electrode_potential = data['Ewe/V']

    return date_time, time, current, working_electrode_potential

def read_thermocouple_data(file):
    data = pd.read_excel(file, sheet_name='Raw Data', header=3)

    data['DateTime'] = pd.to_datetime(data['Time Stamp Local'].astype(str))
    data['DateTime'] = data['Date'] + pd.to_timedelta(data['DateTime'].dt.strftime('%H:%M:%S'))
    date_time = data['DateTime']
    pressure = data['bar(g)']
    temperature_cathode = data['øC  cathode?']
    temperature_anode = data['øC  anode?']

    return date_time, pressure, temperature_cathode, temperature_anode

def read_gaschromatography_data(file):
    data = pd.read_excel(file, sheet_name='Raw Data', header=1)

    #experiment_name
    #datetime
    gas_type = data['Gas type'][0]
    retention_time = data['RT (mins)']
    area = data['area  (pA*min)']
    #ppm

    return gas_type, retention_time, area

def read_results_data(file):
    data = pd.read_excel(file, sheet_name='Results', header=0)

    total_flow_rate = data['Total flow rate (ml/min)']
    total_fe = data['Total FE (%)']

    #gas_results:
    #gas_type
    #current
    #faradaic_efficiency

    return total_flow_rate, total_fe
