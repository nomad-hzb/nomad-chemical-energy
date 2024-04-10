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

from nomad.metainfo import Section, Quantity
from nomad.datamodel.data import EntryData
from nomad.datamodel.metainfo.plot import PlotSection, PlotlyFigure
import plotly.graph_objects as go

from baseclasses.chemical_energy import (
    CENECCElectrode,
    CENECCElectrodeRecipe,
    PotentiometryGasChromatographyMeasurement,
    NECCExperimentalProperties,
    GasChromatographyMeasurement,
    PotentiostatMeasurement,
    ThermocoupleMeasurement,
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

class CE_NECC_EC_GC(PotentiometryGasChromatographyMeasurement, PlotSection, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'location', 'steps', 'samples', 'atmosphere', 'instruments', 'results', 'method'
                ],
            properties=dict(
                order=[
                    'name', 'properties', 'gaschromatographies',
                    'potentiometry', 'thermocouple', 'fe_results'
                    ])))

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
                self.potentiometry = PotentiostatMeasurement(datetime=date_time,
                                                        time=time,
                                                        current=current,
                                                        working_electrode_potential=working_electrode_potential)

            if self.thermocouple is None:
                from baseclasses.helper.file_parser.necc_excel_parser import read_thermocouple_data
                date_time, pressure, temperature_cathode, temperature_anode = read_thermocouple_data(os.path.join(path, self.data_file))
                self.thermocouple = ThermocoupleMeasurement(datetime=date_time,
                                                       pressure=pressure,
                                                       temperature_cathode=temperature_cathode,
                                                       temperature_anode=temperature_anode)

            from baseclasses.helper.file_parser.necc_excel_parser import read_gaschromatography_data
            gaschromatography_measurements = []
            instrument_file_names, datetimes, gas_types, retention_times, areas, ppms = read_gaschromatography_data(os.path.join(path, self.data_file))
            for gas_index in range(len(gas_types)):
                file_index = 0 if gas_index < 4 else 1
                gas_type = gas_types.iat[gas_index]
                if gas_type in {'CO', 'CH4', 'C2H4', 'C2H6', 'H2', 'N2'}:
                    gaschromatography_measurements.append(GasChromatographyMeasurement(
                        instrument_file_name=instrument_file_names.iloc[:, file_index],
                        datetime=datetimes,
                        gas_type=gas_type,
                        retention_time=retention_times.iloc[:, gas_index],
                        area=areas.iloc[:, gas_index],
                        ppm=ppms.iloc[:, gas_index]
                    ))
            self.gaschromatographies = gaschromatography_measurements

            if self.fe_results is None:
                from baseclasses.helper.file_parser.necc_excel_parser import read_results_data
                total_flow_rate, total_fe, cell_current, cell_voltage, gas_measurements = read_results_data(os.path.join(path, self.data_file))
                self.fe_results = PotentiometryGasChromatographyResults(total_flow_rate=total_flow_rate,
                                                                        cell_current=cell_current,
                                                                        cell_voltage=cell_voltage,
                                                                        gas_results=gas_measurements,
                                                                        total_fe=total_fe)

        super(CE_NECC_EC_GC, self).normalize(archive, logger)


        # TODO set x axis
        x_potential_data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
        #x_potential_data = self.fe_results.cell_voltage

        gaschromatography_df = pd.DataFrame({'datetime': self.gaschromatographies[0].datetime,
                                             'ppm': self.gaschromatographies[0].ppm})
        gaschromatography_df['datetime'] += pd.Timedelta(seconds=1) #needed for same mapping as in excel sheet

        #potentiometry_df = pd.DataFrame({'datetime': self.potentiometry.datetime,
        #                                 'potential': self.potentiometry.working_electrode_potential,
        #                                 'current': self.potentiometry.current})
        #thermocouple_df = pd.DataFrame({'datetime': self.thermocouple.datetime,
        #                                'temp_cathode': self.thermocouple.temperature_cathode,
        #                                'temp_anode': self.thermocouple.temperature_anode,
        #                                'pressure': self.thermocouple.pressure})
        #merged_df = pd.merge_asof(gaschromatography_df, potentiometry_df, on='datetime')

        # TODO merged_df für plots nutzen?

        fig = go.Figure(data=[go.Bar(name='Total FE in %', x=x_potential_data, y=abs(self.fe_results.total_fe))])
        for gas in self.fe_results.gas_results:
            fig.add_traces(go.Bar(name=gas.gas_type, x=x_potential_data, y=abs(gas.faradaic_efficiency)))
        fig.update_layout(barmode='group', showlegend=True)
        fig.update_layout(title_text='Potential-Dependent Faradaic Efficiencies')
        # the next line is necessary for yvalues that are 0 if float xvalues are used
        #fig.update_traces(marker_line_color='blue', marker_line_width=2)
        self.figures = [PlotlyFigure(label='figure 1', figure=fig.to_plotly_json())]
