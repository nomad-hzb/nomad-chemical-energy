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

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from baseclasses import BaseMeasurement
from baseclasses.chemical_energy import (
    CENECCElectrode,
    CENECCElectrodeRecipe,
    Chronoamperometry,
    Chronopotentiometry,
    CyclicVoltammetry,
    ElectrochemicalImpedanceSpectroscopyMultiple,
    LinearSweepVoltammetry,
    OpenCircuitVoltage,
    PotentiometryGasChromatographyMeasurement,
    ThermocoupleMeasurement,
)
from nomad.datamodel.data import EntryData
from nomad.datamodel.metainfo.plot import PlotlyFigure, PlotSection
from nomad.metainfo import Quantity, SchemaPackage, Section

from nomad_chemical_energy.schema_packages.file_parser.necc_excel_parser import (
    extract_properties,
    read_gaschromatography_data,
    read_ph_data,
    read_potentiostat_data,
    read_results_data,
    read_thermocouple_data,
    set_catalyst_details,
)
from nomad_chemical_energy.schema_packages.utilities.potentiostat_plots import (
    make_bode_plot,
    make_current_density_over_voltage_rhe_cv_plot,
    make_current_density_over_voltage_rhe_plot,
    make_current_density_plot,
    make_current_over_voltage_cv_plot,
    make_current_over_voltage_plot,
    make_current_plot,
    make_nyquist_plot,
    make_voltage_plot,
)

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


# %% ####################### Generic Entries


class CE_NECC_Measurement(BaseMeasurement, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'location', 'steps', 'instruments', 'results'],
            properties=dict(order=['name', 'data_file', 'samples']),
        ),
    )

    data_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'),
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

    def make_total_fe_figure(self):
        def add_stacked_component(figure, label, x_list, y_list):
            if len(y_list) == 0:
                return
            figure.add_trace(
                go.Bar(
                    name=label,
                    x=x_list,
                    y=y_list,
                    text=[round(fe_value, 1) for fe_value in y_list],
                    textposition='inside',
                    hoverinfo='y+name',
                )
            )

        fig = go.Figure()
        fe_dict = {}
        for hplc_obj in self.hplc:
            timestamp = getattr(hplc_obj, 'datetime', 'Total FE') or 'Total FE'
            injection_type = (
                getattr(hplc_obj, 'injection_type', 'unclassified') or 'unclassified'
            )

            for liquid in getattr(hplc_obj, 'liquid_fe', []):
                compound = getattr(liquid, 'compound', None)
                fe = getattr(liquid, 'faradaic_efficiency', 0)
                if compound is not None:
                    compound_dict = fe_dict.get(f'{compound} {injection_type}', {})
                    timestamp_group = compound_dict.get(timestamp, [])
                    timestamp_group.append(fe.to('percent').magnitude)
                    fe_dict.setdefault(f'{compound} {injection_type}', {})[
                        timestamp
                    ] = timestamp_group

        for compound, fe_time_dict in fe_dict.items():
            mean_fe = [np.mean(fe_list) for fe_list in fe_time_dict.values()]
            add_stacked_component(fig, compound, list(fe_time_dict.keys()), mean_fe)

        for gas in self.fe_results.gas_results:
            compound = getattr(gas, 'gas_type', None)
            fe = getattr(gas, 'faradaic_efficiency', 0)
            add_stacked_component(
                fig, compound, ['Total FE'], [np.mean(abs(fe.to('percent').magnitude))]
            )
        fig.update_layout(
            barmode='stack',
            xaxis_title='',
            yaxis_title='Faradaic Efficiency [%]',
            title='Total Faradaic Efficiency',
            showlegend=True,
            hovermode='x unified',
            dragmode='pan',
            xaxis={'fixedrange': False, 'type': 'category'},
            yaxis={'fixedrange': False},
        )
        return fig

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
            fig.add_trace(
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
        fig.add_trace(
            go.Scatter(
                name='Temperature Anode', x=date_strings, y=merged_df['temp_anode']
            )
        )
        fig.add_trace(
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
        fig = go.Figure()
        date_strings = [
            date.strftime('%Y-%m-%d %H:%M:%S') for date in self.potentiometry.datetime
        ]
        if self.potentiometry.current is not None:
            fig.add_trace(
                go.Scatter(
                    name='Current',
                    x=date_strings,
                    y=self.potentiometry.current,
                    line=dict(color='red'),
                )
            )
            fig.update_layout(
                yaxis=dict(
                    title=f'Current [{self.potentiometry.current[0].units:~P}]',
                    titlefont=dict(color='red'),
                    tickfont=dict(color='red'),
                ),
            )
        if self.potentiometry.working_electrode_potential is not None:
            fig.add_trace(
                go.Scatter(
                    name='Working electrode potential',
                    x=date_strings,
                    y=self.potentiometry.working_electrode_potential,
                    yaxis='y2',
                    line=dict(color='blue'),
                )
            )
        if self.potentiometry.counter_electrode_potential is not None:
            fig.add_trace(
                go.Scatter(
                    name='Counter electrode potential',
                    x=date_strings,
                    y=self.potentiometry.counter_electrode_potential,
                    yaxis='y2',
                    line=dict(color='dodgerblue'),
                )
            )
        if (
            self.potentiometry.working_electrode_potential is not None
            or self.potentiometry.counter_electrode_potential is not None
        ):
            fig.update_layout(
                yaxis2=dict(
                    title=f'Voltage [{self.potentiometry.working_electrode_potential[0].units:~P}]',
                    anchor='x',
                    overlaying='y',
                    side='right',
                    titlefont=dict(color='blue'),
                    tickfont=dict(color='blue'),
                ),
            )
        if self.ph.ph_value is not None:
            ph_date_strings = [
                date.strftime('%Y-%m-%d %H:%M:%S') for date in self.ph.datetime
            ]
            fig.add_trace(
                go.Scatter(
                    name='pH',
                    x=ph_date_strings,
                    y=self.ph.ph_value,
                    yaxis='y3',
                    line=dict(color='green'),
                )
            )
        elif self.fe_results.pH_start and self.fe_results.pH_end:
            fig.add_trace(
                go.Scatter(
                    name='pH',
                    x=[self.fe_results.datetime[0], self.fe_results.datetime[-1]],
                    y=[self.fe_results.pH_start, self.fe_results.pH_end],
                    yaxis='y3',
                    line=dict(color='green'),
                )
            )
        if self.ph.ph_value is not None or self.fe_results.pH_start:
            fig.update_layout(
                yaxis3=dict(
                    title='pH',
                    anchor='free',
                    overlaying='y',
                    side='right',
                    position=1,
                    titlefont=dict(color='green'),
                    tickfont=dict(color='green'),
                ),
            )
        fig.update_layout(
            title_text='Current, Voltage, and pH over Time',
            showlegend=True,
            hovermode='x unified',
            xaxis={'fixedrange': False, 'domain': [0, 0.85]},
        )
        return fig

    def make_overview_fig(self):
        fig = go.Figure()
        fig.update_layout(
            showlegend=True,
            hovermode='x unified',
            xaxis={'fixedrange': False, 'domain': [0.15, 0.85]},
            title_text='EC GC Overview',
        )
        date_strings = [
            date.strftime('%Y-%m-%d %H:%M:%S') for date in self.fe_results.datetime
        ]
        if self.fe_results.cell_voltage is not None:
            fig.add_trace(
                go.Scatter(
                    name='Voltage',
                    x=date_strings,
                    y=self.fe_results.cell_voltage,
                    line=dict(color='blue'),
                )
            )
            fig.update_layout(
                yaxis=dict(
                    title=f'Voltage [{self.fe_results.cell_voltage[0].units:~P}]',
                    titlefont=dict(color='blue'),
                    tickfont=dict(color='blue'),
                ),
            )
        if self.fe_results.cell_current is not None:
            fig.add_trace(
                go.Scatter(
                    name='Current',
                    x=date_strings,
                    y=self.fe_results.cell_current,
                    yaxis='y2',
                    line=dict(color='red'),
                )
            )
            fig.update_layout(
                yaxis2=dict(
                    title=f'Current [{self.fe_results.cell_current[0].units:~P}]',
                    anchor='free',
                    overlaying='y',
                    side='left',
                    position=0,
                    titlefont=dict(color='red'),
                    tickfont=dict(color='red'),
                ),
            )
        if self.fe_results.gas_results is not None:
            for gas in self.fe_results.gas_results:
                fig.add_trace(
                    go.Scatter(
                        name=gas.gas_type,
                        x=date_strings,
                        y=abs(gas.faradaic_efficiency),
                        yaxis='y3',
                    )
                )
            fig.update_layout(
                yaxis3=dict(
                    title='FE [%]',
                    anchor='x',
                    overlaying='y',
                    side='right',
                    titlefont=dict(color='black'),
                    tickfont=dict(color='black'),
                ),
            )
        if self.ph.ph_value is not None:
            ph_date_strings = [
                date.strftime('%Y-%m-%d %H:%M:%S') for date in self.ph.datetime
            ]
            fig.add_trace(
                go.Scatter(
                    name='pH',
                    x=ph_date_strings,
                    y=self.ph.ph_value,
                    yaxis='y4',
                    line=dict(color='green'),
                )
            )
            fig.update_layout(
                yaxis4=dict(
                    title='pH',
                    anchor='free',
                    overlaying='y',
                    side='right',
                    position=1.0,
                    titlefont=dict(color='green'),
                    tickfont=dict(color='green'),
                ),
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
                    self.properties = extract_properties(xls_file)

                if self.properties.cathode is None or self.properties.anode is None:
                    set_catalyst_details(archive, xls_file)

                if not self.ph and len(xls_file.sheet_names) < 7:
                    data = pd.read_excel(xls_file, sheet_name='Raw Data', header=1)
                    ph_data = self.get_cleaned_df(data, ['Date', 'pH Time', 'pH'])
                    ph_start_time = None
                    if data.columns.get_loc('pH') + 1 < len(data.columns):
                        potential_start_time = data.columns[
                            data.columns.get_loc('pH') + 1
                        ]
                        if (
                            potential_start_time
                            and str(potential_start_time)[-1].isdigit()
                        ):
                            ph_start_time = str(potential_start_time)

                    self.ph = read_ph_data(ph_data, ph_start_time)

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
                    if len(xls_file.sheet_names) < 7:
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

                    self.gaschromatographies, start_time, end_time = (
                        read_gaschromatography_data(gc_data)
                    )
                    self.potentiometry = read_potentiostat_data(pot_data)

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
        fig3 = self.make_overview_fig()
        self.figures = [
            PlotlyFigure(
                label='Faradaic Efficiencies Figure', figure=fig1.to_plotly_json()
            ),
            PlotlyFigure(
                label='Current and Voltage Figure', figure=fig2.to_plotly_json()
            ),
            PlotlyFigure(label='EC GC Overview Figure', figure=fig3.to_plotly_json()),
        ]
        if self.hplc:
            fig3 = self.make_total_fe_figure()
            self.figures.append(
                PlotlyFigure(label='Total FE Figure', figure=fig3.to_plotly_json()),
            )
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


# %% ####################### Potentiostat Measurements


class CE_NECC_Chronoamperometry(Chronoamperometry, EntryData, PlotSection):
    m_def = Section(
        a_eln=dict(
            hide=[
                'metadata_file',
                'lab_id',
                'location',
                'control',
                'environment',
                'setup',
                'steps',
                'cycles',
                'instruments',
                'results',
            ],
            properties=dict(
                order=[
                    'name',
                    'data_file',
                    'samples',
                    'station',
                    'voltage_shift',
                    'resistance',
                ],
            ),
        ),
    )

    def normalize(self, archive, logger):
        if self.data_file:
            with archive.m_context.raw_file(self.data_file, 'rb') as f:
                if os.path.splitext(self.data_file)[-1] == '.mpr':
                    from baseclasses.helper.archive_builder.biologic_archive import (
                        get_biologic_properties,
                        get_ca_properties,
                        get_voltammetry_archive,
                    )

                    from nomad_chemical_energy.schema_packages.file_parser.biologic_parser import (
                        get_header_and_data,
                    )

                    metadata, data = get_header_and_data(f)
                    get_voltammetry_archive(data, metadata, self)
                    if not self.setup_parameters:
                        self.setup_parameters = get_biologic_properties(
                            metadata.get('settings', {})
                        )
                    if not self.properties:
                        self.properties = get_ca_properties(metadata.get('params', {}))
                        self.properties.sample_area = self.setup_parameters.get(
                            'sample_area'
                        )
        super().normalize(archive, logger)
        fig1 = make_current_plot(self.current, self.time)
        fig2 = make_current_density_plot(self.current_density, self.time)
        self.figures = [
            PlotlyFigure(label='Current over Time', figure=json.loads(fig1.to_json())),
            PlotlyFigure(
                label='Current Density over Time', figure=json.loads(fig2.to_json())
            ),
        ]


class CE_NECC_Chronopotentiometry(Chronopotentiometry, EntryData, PlotSection):
    m_def = Section(
        a_eln=dict(
            hide=[
                'metadata_file',
                'lab_id',
                'location',
                'control',
                'charge_density',
                'environment',
                'setup',
                'steps',
                'cycles',
                'instruments',
                'results',
            ],
            properties=dict(
                order=[
                    'name',
                    'data_file',
                    'samples',
                    'station',
                    'voltage_shift',
                    'resistance',
                ]
            ),
        ),
    )

    def normalize(self, archive, logger):
        if self.data_file:
            with archive.m_context.raw_file(self.data_file, 'rb') as f:
                if os.path.splitext(self.data_file)[-1] == '.mpr':
                    from baseclasses.helper.archive_builder.biologic_archive import (
                        get_biologic_properties,
                        get_cp_properties,
                        get_voltammetry_archive,
                    )

                    from nomad_chemical_energy.schema_packages.file_parser.biologic_parser import (
                        get_header_and_data,
                    )

                    metadata, data = get_header_and_data(f)
                    get_voltammetry_archive(data, metadata, self)
                    if not self.setup_parameters:
                        self.setup_parameters = get_biologic_properties(
                            metadata.get('settings', {})
                        )
                    if not self.properties:
                        self.properties = get_cp_properties(metadata.get('params', {}))
                        self.properties.sample_area = self.setup_parameters.get(
                            'sample_area'
                        )
        super().normalize(archive, logger)
        fig1 = make_voltage_plot(self.time, self.voltage)
        self.figures = [
            PlotlyFigure(label='Voltage over Time', figure=json.loads(fig1.to_json())),
        ]


class CE_NECC_ConstantCurrentMode(Chronopotentiometry, EntryData, PlotSection):
    m_def = Section(
        a_eln=dict(
            hide=[
                'metadata_file',
                'lab_id',
                'location',
                'control',
                'charge_density',
                'environment',
                'setup',
                'steps',
                'cycles',
                'instruments',
                'results',
            ],
            properties=dict(
                order=[
                    'name',
                    'data_file',
                    'samples',
                    'station',
                    'voltage_shift',
                    'resistance',
                ]
            ),
        ),
    )

    def normalize(self, archive, logger):
        self.method = 'Constant Current'
        if self.data_file:
            with archive.m_context.raw_file(self.data_file, 'rb') as f:
                if os.path.splitext(self.data_file)[-1] == '.mpr':
                    from baseclasses.helper.archive_builder.biologic_archive import (
                        get_biologic_properties,
                        get_const_properties,
                        get_voltammetry_archive,
                    )

                    from nomad_chemical_energy.schema_packages.file_parser.biologic_parser import (
                        get_header_and_data,
                    )

                    metadata, data = get_header_and_data(f)
                    get_voltammetry_archive(data, metadata, self)
                    if not self.setup_parameters:
                        self.setup_parameters = get_biologic_properties(
                            metadata.get('settings', {})
                        )
                    if not self.properties:
                        self.properties = get_const_properties(
                            metadata.get('params', {}), constC=True
                        )
                        self.properties.sample_area = self.setup_parameters.get(
                            'sample_area'
                        )
        super().normalize(archive, logger)


class CE_NECC_ConstantVoltageMode(Chronoamperometry, EntryData, PlotSection):
    m_def = Section(
        a_eln=dict(
            hide=[
                'metadata_file',
                'lab_id',
                'location',
                'control',
                'charge_density',
                'environment',
                'setup',
                'steps',
                'cycles',
                'instruments',
                'results',
            ],
            properties=dict(
                order=[
                    'name',
                    'data_file',
                    'samples',
                    'station',
                    'voltage_shift',
                    'resistance',
                ]
            ),
        ),
    )

    def normalize(self, archive, logger):
        self.method = 'Constant Voltage'
        if self.data_file:
            with archive.m_context.raw_file(self.data_file, 'rb') as f:
                if os.path.splitext(self.data_file)[-1] == '.mpr':
                    from baseclasses.helper.archive_builder.biologic_archive import (
                        get_biologic_properties,
                        get_const_properties,
                        get_voltammetry_archive,
                    )

                    from nomad_chemical_energy.schema_packages.file_parser.biologic_parser import (
                        get_header_and_data,
                    )

                    metadata, data = get_header_and_data(f)
                    get_voltammetry_archive(data, metadata, self)
                    if not self.setup_parameters:
                        self.setup_parameters = get_biologic_properties(
                            metadata.get('settings', {})
                        )
                    if not self.properties:
                        self.properties = get_const_properties(
                            metadata.get('params', {}), constC=False
                        )
                        self.properties.sample_area = self.setup_parameters.get(
                            'sample_area'
                        )
        super().normalize(archive, logger)


class CE_NECC_CyclicVoltammetry(CyclicVoltammetry, EntryData, PlotSection):
    m_def = Section(
        a_eln=dict(
            hide=[
                'users',
                'location',
                'end_time',
                'steps',
                'instruments',
                'results',
                'lab_id',
                'voltage',
                'current',
                'current_density',
                'voltage_rhe_uncompensated',
                'voltage_rhe_compensated',
                'voltage_ref_compensated',
                'time',
                'charge_density',
                'control',
                'charge',
                'metadata_file',
            ],
            properties=dict(
                order=[
                    'name',
                    'data_file',
                ]
            ),
        ),
    )

    def normalize(self, archive, logger):
        if self.data_file:
            with archive.m_context.raw_file(self.data_file, 'rb') as f:
                if os.path.splitext(self.data_file)[-1] == '.mpr':
                    from baseclasses.helper.archive_builder.biologic_archive import (
                        get_biologic_properties,
                        get_cv_properties,
                        get_voltammetry_archive,
                    )

                    from nomad_chemical_energy.schema_packages.file_parser.biologic_parser import (
                        get_header_and_data,
                    )

                    metadata, data = get_header_and_data(f)
                    get_voltammetry_archive(data, metadata, self, multiple=True)
                    if not self.setup_parameters:
                        self.setup_parameters = get_biologic_properties(
                            metadata.get('settings', {})
                        )
                    if not self.properties:
                        self.properties = get_cv_properties(metadata.get('params', {}))
                        self.properties.sample_area = self.setup_parameters.get(
                            'sample_area'
                        )
        super().normalize(archive, logger)
        fig1 = make_current_density_over_voltage_rhe_cv_plot(self.cycles)
        fig2 = make_current_over_voltage_cv_plot(self.cycles)
        self.figures = [
            PlotlyFigure(
                label='Current Density over Voltage RHE',
                figure=json.loads(fig1.to_json()),
            ),
            PlotlyFigure(
                label='Current over Voltage', figure=json.loads(fig2.to_json())
            ),
        ]


class CE_NECC_GEIS(
    ElectrochemicalImpedanceSpectroscopyMultiple, EntryData, PlotSection
):
    m_def = Section(
        a_eln=dict(
            hide=[
                'environment',
                'setup',
                'metadata_file',
                'lab_id',
                'location',
                'steps',
                'instruments',
                'results',
                'pretreatment',
                'properties',
            ],
            properties=dict(
                order=[
                    'name',
                    'data_file',
                    'samples',
                    'station',
                ]
            ),
        ),
    )

    def normalize(self, archive, logger):
        if self.data_file:
            with archive.m_context.raw_file(self.data_file, 'rb') as f:
                if os.path.splitext(self.data_file)[-1] == '.mpr':
                    from baseclasses.helper.archive_builder.biologic_archive import (
                        get_biologic_properties,
                        get_eis_data,
                        get_eis_properties,
                        get_meta_data,
                        get_start_time,
                    )

                    from nomad_chemical_energy.schema_packages.file_parser.biologic_parser import (
                        get_header_and_data,
                    )

                    metadata, data = get_header_and_data(f)
                    get_meta_data(metadata.get('settings', {}), self)
                    ole_timestamp = metadata.get('log', {}).get('ole_timestamp', 0)
                    start_time_offset = data.get('time', np.array([0]))[0].item()
                    self.datetime = get_start_time(ole_timestamp, start_time_offset)
                    if not self.setup_parameters:
                        self.setup_parameters = get_biologic_properties(
                            metadata.get('settings', {})
                        )
                    if not self.measurements:
                        self.measurements = get_eis_properties(
                            metadata.get('params', {})
                        )
                        get_eis_data(data, self.measurements)
                    for cycle in self.measurements:
                        cycle.sample_area = self.setup_parameters.get('sample_area')
        super().normalize(archive, logger)
        fig1 = make_nyquist_plot(self.measurements)
        fig2 = make_bode_plot(self.measurements)
        self.figures = [
            PlotlyFigure(label='Nyquist Plot', figure=json.loads(fig1.to_json())),
            PlotlyFigure(label='Bode Plot', figure=json.loads(fig2.to_json())),
        ]


class CE_NECC_LinearSweepVoltammetry(LinearSweepVoltammetry, EntryData, PlotSection):
    m_def = Section(
        a_eln=dict(
            hide=[
                'metadata_file',
                'lab_id',
                'location',
                'control',
                'charge_density',
                'environment',
                'setup',
                'steps',
                'cycles',
                'instruments',
                'results',
            ],
            properties=dict(
                order=[
                    'name',
                    'data_file',
                    'samples',
                    'station',
                    'voltage_shift',
                    'resistance',
                ]
            ),
        ),
    )

    def normalize(self, archive, logger):
        if self.data_file:
            with archive.m_context.raw_file(self.data_file, 'rb') as f:
                if os.path.splitext(self.data_file)[-1] == '.mpr':
                    from baseclasses.helper.archive_builder.biologic_archive import (
                        get_biologic_properties,
                        get_lsv_properties,
                        get_voltammetry_archive,
                    )

                    from nomad_chemical_energy.schema_packages.file_parser.biologic_parser import (
                        get_header_and_data,
                    )

                    metadata, data = get_header_and_data(f)
                    get_voltammetry_archive(data, metadata, self)
                    if not self.setup_parameters:
                        self.setup_parameters = get_biologic_properties(
                            metadata.get('settings', {})
                        )
                    if not self.properties:
                        self.properties = get_lsv_properties(metadata.get('params', {}))
                        self.properties.sample_area = self.setup_parameters.get(
                            'sample_area'
                        )
        super().normalize(archive, logger)
        fig1 = make_current_density_over_voltage_rhe_plot(
            self.current_density, self.voltage_rhe_compensated
        )
        fig2 = make_current_over_voltage_plot(self.current, self.voltage)
        self.figures = [
            PlotlyFigure(
                label='Current Density over Voltage RHE',
                figure=json.loads(fig1.to_json()),
            ),
            PlotlyFigure(
                label='Current over Voltage', figure=json.loads(fig2.to_json())
            ),
        ]


class CE_NECC_OpenCircuitVoltage(OpenCircuitVoltage, EntryData, PlotSection):
    m_def = Section(
        a_eln=dict(
            hide=[
                'metadata_file',
                'lab_id',
                'location',
                'control',
                'charge',
                'charge_density',
                'environment',
                'setup',
                'steps',
                'cycles',
                'instruments',
                'results',
            ],
            properties=dict(
                order=[
                    'name',
                    'data_file',
                    'samples',
                    'station',
                    'voltage_shift',
                    'resistance',
                ]
            ),
        ),
    )

    def normalize(self, archive, logger):
        if self.data_file:
            with archive.m_context.raw_file(self.data_file, 'rb') as f:
                if os.path.splitext(self.data_file)[-1] == '.mpr':
                    from baseclasses.helper.archive_builder.biologic_archive import (
                        get_biologic_properties,
                        get_ocv_properties,
                        get_voltammetry_archive,
                    )

                    from nomad_chemical_energy.schema_packages.file_parser.biologic_parser import (
                        get_header_and_data,
                    )

                    metadata, data = get_header_and_data(f)
                    get_voltammetry_archive(data, metadata, self)
                    if not self.setup_parameters:
                        self.setup_parameters = get_biologic_properties(
                            metadata.get('settings', {})
                        )
                    if not self.properties:
                        self.properties = get_ocv_properties(metadata.get('params', {}))
                        self.properties.sample_area = self.setup_parameters.get(
                            'sample_area'
                        )
        super().normalize(archive, logger)
        fig1 = make_voltage_plot(self.time, self.voltage)
        self.figures = [
            PlotlyFigure(label='Voltage over Time', figure=json.loads(fig1.to_json())),
        ]


class CE_NECC_PEIS(
    ElectrochemicalImpedanceSpectroscopyMultiple, EntryData, PlotSection
):
    m_def = Section(
        a_eln=dict(
            hide=[
                'environment',
                'setup',
                'metadata_file',
                'lab_id',
                'location',
                'steps',
                'instruments',
                'results',
                'pretreatment',
                'properties',
            ],
            properties=dict(
                order=[
                    'name',
                    'data_file',
                    'samples',
                    'station',
                ]
            ),
        ),
    )

    def normalize(self, archive, logger):
        if self.data_file:
            with archive.m_context.raw_file(self.data_file, 'rb') as f:
                if os.path.splitext(self.data_file)[-1] == '.mpr':
                    from baseclasses.helper.archive_builder.biologic_archive import (
                        get_biologic_properties,
                        get_eis_data,
                        get_eis_properties,
                        get_meta_data,
                        get_start_time,
                    )

                    from nomad_chemical_energy.schema_packages.file_parser.biologic_parser import (
                        get_header_and_data,
                    )

                    metadata, data = get_header_and_data(f)
                    get_meta_data(metadata.get('settings', {}), self)
                    ole_timestamp = metadata.get('log', {}).get('ole_timestamp', 0)
                    start_time_offset = data.get('time', np.array([0]))[0].item()
                    self.datetime = get_start_time(ole_timestamp, start_time_offset)
                    if not self.setup_parameters:
                        self.setup_parameters = get_biologic_properties(
                            metadata.get('settings', {})
                        )
                    if not self.measurements:
                        self.measurements = get_eis_properties(
                            metadata.get('params', {})
                        )
                        get_eis_data(data, self.measurements)
                    for cycle in self.measurements:
                        cycle.sample_area = self.setup_parameters.get('sample_area')
        super().normalize(archive, logger)
        fig1 = make_nyquist_plot(self.measurements)
        fig2 = make_bode_plot(self.measurements)
        self.figures = [
            PlotlyFigure(label='Nyquist Plot', figure=json.loads(fig1.to_json())),
            PlotlyFigure(label='Bode Plot', figure=json.loads(fig2.to_json())),
        ]
        super().normalize(archive, logger)


m_package.__init_metainfo__()
