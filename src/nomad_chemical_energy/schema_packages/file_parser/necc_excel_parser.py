# MIT License

# Copyright (c) 2019

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import pandas as pd
from baseclasses.chemical_energy import (
    GasFEResults,
    NECCFeedGas,
    NECCPotentiostatMeasurement,
    PotentiometryGasChromatographyResults,
)
from nomad.datamodel.metainfo.basesections import CompositeSystemReference


def _round_not_zero(number):
    rounded_num = round(number, 3)
    if rounded_num == 0:
        return number
    return rounded_num


def _process_potentiostat_column(data, column_names):
    for column_name in column_names:
        if column_name in data.columns:
            return data[column_name].dropna().apply(_round_not_zero)
    return None


def read_potentiostat_data(data):
    measurement = NECCPotentiostatMeasurement()
    data['time/s'] = pd.to_datetime(data['time/s'], errors='coerce')
    data = data.dropna(subset=['time/s'])
    measurement.datetime = data['time/s'].to_list()

    measurement.current = _process_potentiostat_column(
        data, ['I/mA', '<I/mA>', '<I>/mA']
    )
    measurement.working_electrode_potential = _process_potentiostat_column(
        data, ['Ewe/V', '<Ewe/V>', '<Ewe>/V']
    )
    measurement.counter_electrode_potential = _process_potentiostat_column(
        data, ['Ece/V', '<Ece/V>', '<Ece>/V']
    )
    measurement.ewe_ece_difference = _process_potentiostat_column(
        data, ['Ewe-Ece/V', '<Ewe-Ece/V>', '<Ewe-Ece>/V']
    )
    measurement.capacity = _process_potentiostat_column(data, ['dQ/C'])

    return measurement


def read_thermocouple_data(data, start_time, end_time):
    time_grouping = pd.Timedelta(minutes=3)

    data['DateTime'] = pd.to_datetime(data['Time Stamp Local'].astype(str))
    data['Date'] = pd.to_datetime(data['Date'].astype(str))
    data['DateTime'] = data['Date'] + pd.to_timedelta(
        data['DateTime'].dt.strftime('%H:%M:%S')
    )

    data = data[
        (data['DateTime'] > start_time - time_grouping) & (data['DateTime'] <= end_time)
    ]
    data = data[['DateTime', 'bar(g)', 'øC  cathode', 'øC  anode']]
    data = data.resample(
        time_grouping, on='DateTime', origin=start_time, closed='right', label='right'
    ).mean()

    datetimes = data.index
    pressure = data['bar(g)'].apply(_round_not_zero)
    temperature_cathode = data['øC  cathode'].apply(_round_not_zero)
    temperature_anode = data['øC  anode'].apply(_round_not_zero)

    return datetimes, pressure, temperature_cathode, temperature_anode


def read_gaschromatography_data(data):
    instrument_file_names = data.loc[:, data.columns.str.startswith('Experiment name')]
    instrument_file_names.dropna(axis=0, how='all', inplace=True)

    data['DateTime'] = pd.to_datetime(data['Time '].astype(str))
    data['Date'] = pd.to_datetime(data['Date'].astype(str))
    data['DateTime'] = data['Date'] + pd.to_timedelta(
        data['DateTime'].dt.strftime('%H:%M:%S')
    )
    datetimes = data['DateTime'].dropna()

    gas_types = data.loc[0, data.columns.str.startswith('Gas type')]
    retention_times = data.loc[:, data.columns.str.startswith('RT')]
    areas = data.loc[:, data.columns.str.startswith('area')]
    ppms = data.loc[:, data.columns.str.startswith('ppm value')]

    retention_times.dropna(axis=0, how='all', inplace=True)
    areas.dropna(axis=0, how='all', inplace=True)
    ppms.dropna(axis=0, how='all', inplace=True)

    return instrument_file_names, datetimes, gas_types, retention_times, areas, ppms


def read_results_data(data, pH_start=None, ph_end=None):
    results_data = PotentiometryGasChromatographyResults()
    data['DateTime'] = pd.to_datetime(data['Time'].astype(str))
    data['Date'] = pd.to_datetime(data['Date'].astype(str))
    data['DateTime'] = data['Date'] + pd.to_timedelta(
        data['DateTime'].dt.strftime('%H:%M:%S')
    )
    results_data.datetime = data['DateTime'].dropna().to_list()

    results_data.total_flow_rate = data['Total flow rate (ml/min)'].dropna()
    results_data.total_fe = data['Total FE (%)'].dropna()
    results_data.cell_current = data['Current(mA)'].dropna()
    results_data.cell_voltage = data['Cell Voltage'].dropna()

    gas_measurements = []
    current_column_headers = [col for col in data.columns if col.endswith('I (mA)')]

    for col_header in current_column_headers:
        gas_type = col_header.split(' ', 1)[0]
        current = data[col_header].dropna()
        fe = data[' '.join([gas_type, 'FE (%)'])].dropna()
        if (fe <= 0).all():
            fe = abs(fe)
        gas_measurements.append(
            GasFEResults(
                gas_type=gas_type,
                datetime=results_data.datetime,
                current=current,
                faradaic_efficiency=fe,
            )
        )
    results_data.gas_results = gas_measurements

    results_data.pH_start = pH_start
    results_data.pH_end = ph_end

    return results_data


def read_properties(file):
    table_name = (
        'Experimental details' if len(file.sheet_names) == 4 else 'Experimental Details'
    )
    data = pd.read_excel(file, sheet_name=table_name, index_col=0, header=None)

    if len(data.columns) == 0:
        return {}

    experimental_properties_dict = {
        'cell_type': data.loc['Cell type ', 1],
        'has_reference_electrode': data.loc['Reference Electrode (y/n)', 1] == 'y',
        'reference_electrode_type': data.loc['Reference electrode type', 1],
        'cathode_geometric_area': data.loc['Cathode geometric area', 1],
        'membrane_type': data.loc['Membrane type', 1],
        'membrane_name': data.loc['Membrane Name', 1],
        'membrane_thickness': data.loc['Membrane thickness', 1],
        'gasket_thickness': data.loc['Gasket thickness', 1],
        'anolyte_type': data.loc['Anolyte Type', 1],
        'anolyte_concentration': data.loc['Anolyte Conc. (M)', 1],
        'anolyte_flow_rate': data.loc['Anolyte flow rate (ml/min)', 1],
        'anolyte_volume': data.loc['Anolyte Volume (ml)', 1],
        'has_humidifier': data.loc['Humidifier (y/n)', 1] == 'y',
        'humidifier_temperature': 20
        if data.loc['Humidifier Temperature', 1] == 'RT'
        else data.loc['Humidifier Temperature', 1],
        'water_trap_volume': data.loc['Water trap volume', 1],
        'bleedline_flow_rate': data.loc['Bleedline flow rate', 1],
        'nitrogen_start_value': data.loc['Nitrogen start value', 1],
        'remarks': data.loc['Remarks', 1],
        'chronoanalysis_method': data.loc['CP/CA', 1],
    }

    experimental_properties_dict = {
        key: value
        for key, value in experimental_properties_dict.items()
        if not pd.isna(value)
    }

    feed_gases = []
    if not pd.isna(
        data.loc['Feed gas 1', 1] and data.loc['Feed gas flow rate (ml/min)', 1].iat[0]
    ):
        feed_gases.append(
            NECCFeedGas(
                name=data.loc['Feed gas 1', 1],
                flow_rate=data.loc['Feed gas flow rate (ml/min)', 1].iat[0],
            )
        )
    if not pd.isna(
        data.loc['Feed gas 2', 1] and data.loc['Feed gas flow rate (ml/min)', 1].iat[1]
    ):
        feed_gases.append(
            NECCFeedGas(
                name=data.loc['Feed gas 2', 1],
                flow_rate=data.loc['Feed gas flow rate (ml/min)', 1].iat[1],
            )
        )
    experimental_properties_dict.update({'feed_gases': feed_gases})

    if not pd.isna(data.loc['Anode ID', 1]):
        anode = CompositeSystemReference(lab_id=data.loc['Anode ID', 1].strip())
        experimental_properties_dict.update({'anode': anode})

    if not pd.isna(data.loc['Cathode ID', 1]):
        cathode = CompositeSystemReference(lab_id=data.loc['Cathode ID', 1].strip())
        experimental_properties_dict.update({'cathode': cathode})

    return experimental_properties_dict
