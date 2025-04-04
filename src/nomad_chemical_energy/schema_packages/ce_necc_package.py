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

import pandas as pd
import plotly.graph_objects as go
from baseclasses.chemical_energy import (
    CENECCElectrode,
    CENECCElectrodeRecipe,
    GasChromatographyMeasurement,
    NECCExperimentalProperties,
    PotentiometryGasChromatographyMeasurement,
    ThermocoupleMeasurement,
)
from nomad.datamodel.data import EntryData
from nomad.datamodel.metainfo.plot import PlotlyFigure, PlotSection
from nomad.metainfo import SchemaPackage, Section

m_package = SchemaPackage()

# %% ####################### Entities


class CE_NECC_ElectrodeRecipe(CENECCElectrodeRecipe, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'users',
                'origin',
                'chemical_composition_or_formulas',
                'elemental_composition',
                'components',
            ],
            properties=dict(
                order=[
                    'name',
                    'lab_id',
                    'recipe_type',
                    'deposition_method',
                    'deposition_temperature',
                    'n2_deposition_pressure',
                    'mass_loading',
                ]
            ),
        ),
        label_quantity='sample_id',
    )


class CE_NECC_Electrode(CENECCElectrode, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'chemical_composition_or_formulas',
                'origin',
                'elemental_composition',
                'components',
                'name',
                'datetime',
            ],
            properties=dict(order=['lab_id', 'recipe', 'remarks']),
        ),
        label_quantity='electrode_id',
    )


# %%####################################### Measurements


class CE_NECC_EC_GC(PotentiometryGasChromatographyMeasurement, PlotSection, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'location',
                'steps',
                'samples',
                'atmosphere',
                'instruments',
                'results',
                'method',
            ],
            properties=dict(
                order=[
                    'name',
                    'lab_id',
                    'properties',
                    'gaschromatographies',
                    'potentiometry',
                    'thermocouple',
                    'fe_results',
                ]
            ),
        )
    )

    def make_fe_figure(self, date_strings):
        fig = go.Figure(
            data=[
                go.Bar(
                    name='Total FE in %',
                    x=date_strings,
                    y=abs(self.fe_results.total_fe),
                )
            ]
        )
        for gas in self.fe_results.gas_results:
            date_strings = [date.strftime('%Y-%m-%d %H:%M:%S') for date in gas.datetime]
            fig.add_traces(
                go.Bar(
                    name=gas.gas_type, x=date_strings, y=abs(gas.faradaic_efficiency)
                )
            )
        fig.update_layout(barmode='group', showlegend=True, xaxis={'fixedrange': False})
        fig.update_layout(title_text='Time-Dependent Faradaic Efficiencies')
        return fig

    def make_thermocouple_figure(self, date_strings, merged_df):
        fig = go.Figure(
            data=[
                go.Scatter(
                    name='Temperature Cathode',
                    x=date_strings,
                    y=merged_df['temp_cathode'],
                )
            ]
        )
        fig.add_traces(
            go.Scatter(
                name='Temperature Anode', x=date_strings, y=merged_df['temp_anode']
            )
        )
        fig.add_traces(
            go.Scatter(
                name='Total Flow Rate',
                x=date_strings,
                y=self.fe_results.total_flow_rate,
                yaxis='y2',
                line=dict(color='green'),
            )
        )
        fig.update_layout(
            yaxis=dict(
                title=f'Temperature [{self.thermocouple.temperature_cathode[0].units}]'
            ),
            yaxis2=dict(
                title=f'Total Flow Rate [{self.fe_results.total_flow_rate[0].units}]',
                anchor='x',
                overlaying='y',
                side='right',
                titlefont=dict(color='green'),
                tickfont=dict(color='green'),
            ),
        )
        fig.update_layout(
            title_text='Temperatures and Flow Rate over Time',
            showlegend=True,
            xaxis={'fixedrange': False},
        )
        return fig

    def make_current_voltage_figure(self, date_strings):
        fig = go.Figure(
            data=[
                go.Scatter(
                    name='Current',
                    x=date_strings,
                    y=self.fe_results.cell_current,
                    line=dict(color='blue'),
                )
            ]
        )
        fig.add_traces(
            go.Scatter(
                name='Voltage',
                x=date_strings,
                y=self.fe_results.cell_voltage,
                yaxis='y2',
                line=dict(color='red'),
            )
        )
        fig.update_layout(
            yaxis=dict(
                title=f'Current [{self.fe_results.cell_current[0].units}]',
                titlefont=dict(color='blue'),
                tickfont=dict(color='blue'),
            ),
            yaxis2=dict(
                title=f'Voltage [{self.fe_results.cell_voltage[0].units}]',
                anchor='x',
                overlaying='y',
                side='right',
                titlefont=dict(color='red'),
                tickfont=dict(color='red'),
            ),
        )
        fig.update_layout(
            title_text='Current and Voltage over Time',
            showlegend=True,
            xaxis={'fixedrange': False},
        )
        return fig

    def get_cleaned_df(self, data, column_list):
        string_col_names = [col for col in data.columns if isinstance(col, str)]
        existing_columns = [
            col
            for col in string_col_names
            if any(col.startswith(prefix) for prefix in column_list)
        ]
        cleaned_df = data.loc[:, existing_columns]
        cleaned_df.dropna(axis=0, how='all', inplace=True)
        return cleaned_df

    def normalize(self, archive, logger):
        if self.data_file:
            with archive.m_context.raw_file(self.data_file, 'rb') as f:
                xls_file = pd.ExcelFile(f)

                if self.properties is None:
                    from nomad_chemical_energy.schema_packages.file_parser.necc_excel_parser import (
                        read_properties,
                    )

                    experimental_properties_dict = read_properties(xls_file)
                    self.properties = NECCExperimentalProperties()
                    for attribute_name, value in experimental_properties_dict.items():
                        setattr(self.properties, attribute_name, value)

                if (
                    not self.thermocouple
                    or not self.gaschromatographies
                    or not self.potentiometry
                ):
                    gc_columns = [
                        'Experiment name',
                        'Date',
                        'Time ',
                        'Gas type',
                        'RT',
                        'area',
                        'ppm value',
                    ]
                    pot_columns = [
                        'time/s',
                        'I/mA',
                        '<I/mA>',
                        '<I>/mA',
                        'Ewe/V',
                        '<Ewe/V>',
                        '<Ewe>/V',
                        'Ece/V',
                        '<Ece/V>',
                        '<Ece>/V',
                        'Ewe-Ece/V',
                        '<Ewe-Ece/V>',
                        '<Ewe-Ece>/V',
                        'dQ/C',
                    ]
                    thermo_columns = [
                        'Date',
                        'Time Stamp Local',
                        'bar(g)',
                        'øC  cathode',
                        'øC  anode',
                    ]
                    if len(xls_file.sheet_names) == 4:
                        data = pd.read_excel(xls_file, sheet_name='Raw Data', header=1)
                        results_data = pd.read_excel(
                            xls_file, sheet_name='Results', header=0
                        )

                        gc_data = self.get_cleaned_df(data, gc_columns)
                        pot_data = self.get_cleaned_df(data, pot_columns)
                        data.columns = data.iloc[
                            1
                        ]  # thermo column names are in second row
                        thermo_data = self.get_cleaned_df(data[2:], thermo_columns)
                    else:
                        pot_data = pd.read_excel(xls_file, sheet_name='Pot Data')
                        thermo_data = pd.read_excel(xls_file, sheet_name='Thermo Data')
                        fid_data = pd.read_excel(xls_file, sheet_name='FID Data')
                        tcd_data = pd.read_excel(xls_file, sheet_name='TCD Data')
                        results_data = pd.read_excel(
                            xls_file, sheet_name='GC Calc', header=0
                        )

                        pot_data = self.get_cleaned_df(pot_data, pot_columns)
                        thermo_data = self.get_cleaned_df(thermo_data, thermo_columns)
                        fid_data = self.get_cleaned_df(fid_data, gc_columns)
                        tcd_data = self.get_cleaned_df(tcd_data, gc_columns)
                        gc_data = pd.merge(
                            fid_data, tcd_data, on=['Date', 'Time '], how='inner'
                        )

                    pH_start, pH_end = None, None
                    if 'pH' in results_data.columns:
                        pH_start = results_data['pH'].iloc[0]
                        pH_end = results_data['pH'].iloc[1]
                    results_data.dropna(
                        axis=0,
                        how='any',
                        inplace=True,
                        subset=[
                            'Current(mA)',
                            'Total flow rate (ml/min)',
                            'Total FE (%)',
                        ],
                    )

                    from nomad_chemical_energy.schema_packages.file_parser.necc_excel_parser import (
                        read_gaschromatography_data,
                    )

                    gaschromatography_measurements = []
                    (
                        instrument_file_names,
                        datetimes,
                        gas_types,
                        retention_times,
                        areas,
                        ppms,
                    ) = read_gaschromatography_data(gc_data)
                    if datetimes.size > 0:
                        start_time = datetimes.iat[0]
                        end_time = datetimes.iat[-1]
                    for gas_index in range(len(gas_types)):
                        file_index = 0 if gas_index < 4 else 1
                        gas_type = gas_types.iat[gas_index]
                        if gas_type in {'CO', 'CH4', 'C2H4', 'C2H6', 'H2', 'N2'}:
                            gaschromatography_measurements.append(
                                GasChromatographyMeasurement(
                                    instrument_file_name=instrument_file_names.iloc[
                                        :, file_index
                                    ],
                                    datetime=datetimes.to_list(),
                                    gas_type=gas_type,
                                    retention_time=retention_times.iloc[:, gas_index],
                                    area=areas.iloc[:, gas_index],
                                    ppm=ppms.iloc[:, gas_index],
                                )
                            )
                    self.gaschromatographies = gaschromatography_measurements

                    from nomad_chemical_energy.schema_packages.file_parser.necc_excel_parser import (
                        read_potentiostat_data,
                    )

                    self.potentiometry = read_potentiostat_data(pot_data)
                    if start_time is None or end_time is None:
                        start_time = datetimes[0]
                        end_time = datetimes[-1]
                    from nomad_chemical_energy.schema_packages.file_parser.necc_excel_parser import (
                        read_thermocouple_data,
                    )

                    try:
                        datetimes, pressure, temperature_cathode, temperature_anode = (
                            read_thermocouple_data(thermo_data, start_time, end_time)
                        )
                        self.thermocouple = ThermocoupleMeasurement(
                            datetime=datetimes.to_list(),
                            pressure=pressure,
                            temperature_cathode=temperature_cathode,
                            temperature_anode=temperature_anode,
                        )
                    except Exception as e:
                        logger.info(e)
                        self.thermocouple = ThermocoupleMeasurement()

                if self.fe_results is None:
                    from nomad_chemical_energy.schema_packages.file_parser.necc_excel_parser import (
                        read_results_data,
                    )

                    self.fe_results = read_results_data(results_data, pH_start, pH_end)

        self.properties.normalize(archive, logger)
        self.thermocouple.normalize(archive, logger)
        self.fe_results.normalize(archive, logger)
        super().normalize(archive, logger)

        date_strings = [
            date.strftime('%Y-%m-%d %H:%M:%S') for date in self.fe_results.datetime
        ]

        fig1 = self.make_fe_figure(date_strings)
        fig2 = self.make_current_voltage_figure(date_strings)
        self.figures = [
            PlotlyFigure(
                label='Faradaic Efficiencies Figure', figure=fig1.to_plotly_json()
            ),
            PlotlyFigure(
                label='Current and Voltage Figure', figure=fig2.to_plotly_json()
            ),
        ]
        if self.thermocouple.datetime is not None:
            thermocouple_df = pd.DataFrame(
                {
                    'datetime': self.thermocouple.datetime,
                    'temp_cathode': self.thermocouple.temperature_cathode,
                    'temp_anode': self.thermocouple.temperature_anode,
                    'pressure': self.thermocouple.pressure,
                }
            )
            results_df = pd.DataFrame(
                {
                    'datetime': self.fe_results.datetime,
                    'total_flow_rate': self.fe_results.total_flow_rate,
                }
            )
            merged_df = pd.merge_asof(results_df, thermocouple_df, on='datetime')
            fig3 = self.make_thermocouple_figure(date_strings, merged_df)
            self.figures.append(
                PlotlyFigure(
                    label='Temperatures and Flow Rate Figure',
                    figure=fig3.to_plotly_json(),
                )
            )


m_package.__init_metainfo__()
