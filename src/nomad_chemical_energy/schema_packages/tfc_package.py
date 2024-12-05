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

import numpy as np
import pandas as pd
import plotly.graph_objs as go
from baseclasses import SingleLibraryMeasurement
from baseclasses.characterizations import (
    XRDLibrary,
    XRFComposition,
    XRFLayer,
    XRFLibrary,
    XRFSingleLibraryMeasurement,
)
from baseclasses.chemical_energy import Equipment
from baseclasses.helper.utilities import convert_datetime, set_sample_reference
from baseclasses.vapour_based_deposition import MultiTargetSputtering
from nomad.datamodel.data import EntryData
from nomad.datamodel.metainfo.plot import PlotlyFigure, PlotSection
from nomad.metainfo import Datetime, Quantity, SchemaPackage, Section, SubSection

m_package = SchemaPackage()

# %% ####################### Entities


class TFC_Equipment(Equipment, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['users', 'origin', 'elemental_composition', 'components'],
            properties=dict(order=['name', 'lab_id', 'producer', 'location']),
        )
    )


# %% ####################### Deposition


class TFC_Sputtering(MultiTargetSputtering, PlotSection, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'layer',
                'batch',
                'present',
                'positon_in_experimental_plan',
                'end_time',
                'instruments',
                'steps',
                'location',
            ],
            properties=dict(
                order=[
                    'name',
                    'data_file',
                    'datetime',
                    'substrate',
                    'sample_owner',
                    'process_user',
                    'holder',
                    'sample_lab_label',
                ]
            ),
        )
    )

    def make_targets_process_table(self):
        target_names = [target.name for target in self.targets]
        if len(target_names) == 0:
            return None
        value_list = [''] * len(target_names) * 3
        value_list[0] = 'Power (W)'
        value_list[len(target_names)] = 'Bias U (V)'
        value_list[len(target_names) * 2] = 'Bias I (A)'
        color_list = ['white'] * len(target_names) * 3
        color_list[len(target_names) : len(target_names) * 2] = ['lightgrey'] * len(
            target_names
        )
        target_power = [
            process.power.magnitude.tolist() for process in self.process_properties
        ]
        target_bias_u = [
            process.bias_voltage.magnitude.tolist() for process in self.observables
        ]
        target_bias_i = [
            process.bias_current.magnitude.tolist() for process in self.observables
        ]
        cells = [
            power + bias_u + bias_i
            for power, bias_u, bias_i in zip(target_power, target_bias_u, target_bias_i)
        ]
        header_values = ['', 'Targets'] + [
            f'Step {i + 1}' for i in range(len(target_power))
        ]
        fig = go.Figure(
            data=[
                go.Table(
                    header=dict(
                        values=header_values,
                        fill_color='grey',
                        line_color='darkslategray',
                        font=dict(color='white'),
                    ),
                    cells=dict(
                        values=[value_list, target_names * 3, *cells],
                        fill_color=[color_list * len(header_values)],
                        line_color='darkslategray',
                    ),
                )
            ]
        )
        return fig

    def normalize(self, archive, logger):
        if self.data_file:
            with archive.m_context.raw_file(self.data_file, 'rb') as f:
                xls_file = pd.ExcelFile(f)
                information_df = pd.read_excel(
                    xls_file, sheet_name='Information', header=0, index_col=0
                )
                information_values = information_df['Value'].where(
                    pd.notna(information_df['Value']), None
                )
                self.name = (
                    information_values.get('Process')
                    if self.name is None
                    else self.name
                )
                self.datetime = (
                    information_values.get('Date')
                    if self.datetime is None
                    else self.datetime
                )
                self.sample_lab_label = information_values.get('Sample Lab label')
                self.holder = information_values.get('Holder')
                self.substrate = information_values.get('Substrate')
                self.sample_owner = information_values.get('Sample Owner')
                self.process_user = information_values.get('Process user')

                if not self.samples:
                    sample_id = information_values.get('Sample ID (NOMAD)')
                    sample_id = (
                        self.data_file.split('.')[0][:8]
                        if sample_id is None
                        else sample_id
                    )
                    set_sample_reference(
                        archive, self, sample_id, archive.metadata.upload_id
                    )

                if not self.targets:
                    target_df = pd.read_excel(
                        xls_file, sheet_name='Source_Configuration', header=0
                    )
                    from baseclasses.helper.archive_builder.prevac_archive import (
                        get_target_properties,
                    )

                    self.targets = get_target_properties(target_df)
                num_targets = len(self.targets)
                if not self.process_properties:
                    parameters_df = pd.read_excel(
                        xls_file, sheet_name='Parameters', header=1, index_col=0
                    )
                    from baseclasses.helper.archive_builder.prevac_archive import (
                        get_process_properties,
                    )

                    self.process_properties = get_process_properties(
                        parameters_df, num_targets
                    )
                if not self.observables:
                    observables_df = pd.read_excel(
                        xls_file, sheet_name='Observables', header=1, index_col=0
                    )
                    self.description = observables_df.loc['Notes', 'Steps']
                    from baseclasses.helper.archive_builder.prevac_archive import (
                        get_observables,
                    )

                    self.observables = get_observables(observables_df, num_targets)

        fig1 = self.make_targets_process_table()
        if fig1:
            self.figures = [
                PlotlyFigure(
                    label='Table for Target & Process View',
                    figure=fig1.to_plotly_json(),
                ),
            ]

        super().normalize(archive, logger)


# %%######################## Measurements


def load_XRF_txt(input_file):
    head = [next(input_file) for _ in range(3)]
    pos = [0]
    ns = False
    for i, c in enumerate(head[2]):
        if c != ' ':
            ns = True
        if c == ' ' and ns and head[0][i] == ' ':
            pos.append(i)
            ns = False
    pos.append(-1)
    col = []
    c_old = ''
    for i in range(len(pos) - 1):
        c1 = (
            head[0][pos[i] : pos[i + 1]].strip()
            if head[0][pos[i] : pos[i + 1]].strip()
            else c_old
        )
        c2 = head[1][pos[i] : pos[i + 1]].strip()
        col.append((c1, c2))
        c_old = c1
    input_file.seek(0)
    try:
        composition_data = pd.read_csv(
            input_file,
            names=col,
            header=None,
            skiprows=2,
            sep='\s{2,}',
            decimal=',',
            index_col=0,
        )
    except Exception:
        composition_data = pd.read_csv(
            input_file,
            names=col,
            header=None,
            skiprows=2,
            sep='\s{2,}',
            decimal='.',
            index_col=0,
        )

    return composition_data


class TFC_XRFLibrary(XRFLibrary, EntryData, PlotSection):
    m_def = Section(
        label='XRF Measurement Library',
        a_eln=dict(
            hide=['instruments', 'steps', 'results', 'lab_id'],
            properties=dict(
                order=[
                    'name',
                ]
            ),
        ),
    )

    def get_xrf_overview(self, logger):
        overview_df = pd.DataFrame()
        try:
            for single_library in self.measurements:
                x = single_library.get('position_x')
                y = single_library.get('position_y')
                thickness = single_library.get('layer')[1].get('thickness')
                composition = single_library.get('layer')[1].get('composition')
                composition_names = [element.name for element in composition]
                composition_amounts = [element.amount for element in composition]
                if overview_df.empty:
                    overview_df = overview_df.reindex(columns=['x', 'y', 'thickness']+composition_names)
                overview_df.loc[len(overview_df)] = [x, y, thickness] + composition_amounts
        except:
            logger.debug('The XRF Library does not have the expected structure.')
        return overview_df

    def make_library_overview_table(self, overview_df):
        fig = go.Figure(
            data=[
                go.Table(
                    header=dict(
                        values=list(overview_df.columns),
                        fill_color='grey',
                        line_color='darkslategray',
                        font=dict(color='white'),
                    ),
                    cells=dict(
                        values=[overview_df[col] for col in overview_df.columns],
                        line_color='darkslategray',
                    ),
                )
            ]
        )
        return fig

    def normalize(self, archive, logger):
        with archive.m_context.raw_file(archive.metadata.mainfile, 'rt') as f:
            os.path.basename(f.name)
            if not self.samples:
                set_sample_reference(archive, self, self.data_folder.split('_')[0])

        if self.composition_file and self.data_folder:
            file_path = os.path.join(self.data_folder, self.composition_file)

            measurements = []

            from nomad_chemical_energy.schema_packages.file_parser.xrf_spx_parser import (
                read as xrf_read,
            )

            files = [
                os.path.basename(file.path)
                for file in archive.m_context.upload_files.raw_directory_list(
                    self.data_folder
                )
                if file.path.endswith('.spx')
            ]
            files.sort()

            with archive.m_context.raw_file(
                os.path.join(self.data_folder, files[0]), 'rb'
            ) as f:
                _, energy, measurement_rows, positions_array, _, _ = xrf_read([f])

            self.datetime = convert_datetime(
                measurement_rows[0]['DateTime'],
                datetime_format='%Y-%m-%dT%H:%M:%S.%f',
                utc=False,
            )

            # self.datetime = convert_datetime(
            #     measurement_rows[0]["DateTime"], datetime_format="%Y-%m-%dT%H:%M:%S.%f", utc=False)
            self.energy = energy
            with archive.m_context.raw_file(file_path, 'rt') as f:
                composition_data = load_XRF_txt(f)

            material_name = ''
            for i, file in enumerate(files):
                with archive.m_context.raw_file(
                    os.path.join(self.data_folder, file), 'rb'
                ) as f:
                    _, _, _, ar, _, _ = xrf_read([f])

                measurement_row = composition_data.loc[
                    os.path.splitext(os.path.basename(file))[0]
                ]
                layer_data = {}
                for v in measurement_row.items():
                    if v[0][0] not in layer_data:
                        layer_data.update({v[0][0]: {}})
                    if 'Thick' in v[0][1] or 'Dicke' in v[0][1]:
                        layer_data.update({v[0][0]: {'thickness': v[1]}})
                        continue
                    if '%' not in v[0][1]:
                        continue
                    if 'composition' not in layer_data[v[0][0]]:
                        layer_data[v[0][0]].update({'composition': []})
                    if v[0][1] not in material_name:
                        material_name += f'{v[0][0]}:{v[0][1]},'
                    layer_data[v[0][0]]['composition'].append(
                        XRFComposition(amount=float(v[1]), name=v[0][1])
                    )

                layers = []
                for key, layer in layer_data.items():
                    layers.append(
                        XRFLayer(
                            layer=key,
                            composition=layer.get('composition', None),
                            thickness=layer.get('thickness', None),
                        )
                    )

                measurements.append(
                    XRFSingleLibraryMeasurement(
                        data_file=[
                            os.path.basename(os.path.join(self.data_folder, file))
                        ],
                        position_x=ar[0][0],  # positions_array[0, i],
                        position_y=ar[1][0],  # positions_array[1, i],
                        layer=layers,
                        name=f'{round(ar[0][0], 5)},{round(ar[1][0], 5)}',
                    )
                )
            self.measurements = measurements
            self.material_names = material_name
            overview_df = self.get_xrf_overview(logger)
            fig1 = self.make_library_overview_table(overview_df)
            self.figures = [PlotlyFigure(label='XRF Overview',figure=fig1.to_plotly_json()),]

        super().normalize(archive, logger)


def get_value(val):
    try:
        return float(val)
    except Exception:
        return None


def set_single_xrd_measurement_metadata(row):
    entry = XRDMetalJetSingleLibraryMeasurement()
    entry.datetime = convert_datetime(
        f'{row["Date"]} {row["Time"]}', datetime_format='%Y/%m/%d %H:%M:%S', utc=False
    )
    entry.position_x = get_value(row['motors x'])
    entry.position_y = get_value(row['motors y'])
    entry.motors_det_v = get_value(row['motors det_v'])
    entry.motors_det_h = get_value(row['motors det_h'])
    entry.motors_det_rot = get_value(row['motors det_rot'])
    entry.motors_x = get_value(row['motors x'])
    entry.motors_y = get_value(row['motors y'])
    entry.motors_z = get_value(row['motors z'])
    entry.motors_phi = get_value(row['motors phi'])
    entry.motors_chi = get_value(row['motors chi'])
    entry.motors_chi_cor = get_value(row['motors chi_cor'])
    entry.motors_omega = get_value(row['motors omega'])
    entry.motors_zhuber = get_value(row['motors zhuber'])
    entry.motors_xhuber = get_value(row['motors xhuber'])
    entry.motors_sb = get_value(row['motors sb'])
    entry.motors_st = get_value(row['motors st'])
    entry.motors_sl = get_value(row['motors sl'])
    entry.motors_sr = get_value(row['motors sr'])
    entry.motors_sv_delta = get_value(row['motors sv_delta'])
    entry.motors_sv_pos = get_value(row['motors sv_pos'])
    entry.motors_sh_delta = get_value(row['motors sh_delta'])
    entry.motors_sh_pos = get_value(row['motors sh_pos'])
    entry.hexapod_x = get_value(row['hexapod x'])
    entry.hexapod_y = get_value(row['hexapod y'])
    entry.hexapod_z = get_value(row['hexapod z'])
    entry.hexapod_u = get_value(row['hexapod u'])
    entry.hexapod_v = get_value(row['hexapod v'])
    entry.hexapod_w = get_value(row['hexapod w'])
    entry.hexapod_pivot_x = get_value(row['hexapod pivot_x'])
    entry.hexapod_pivot_y = get_value(row['hexapod pivot_y'])
    entry.hexapod_pivot_z = get_value(row['hexapod pivot_z'])
    entry.metaljet_generator_emission_power = get_value(
        row['metaljet generator_emission_power,m']
    )
    entry.metaljet_generator_high_voltage = get_value(
        row['metaljet generator_high_voltage,m']
    )
    entry.metaljet_spotsize_x_um = get_value(row['metaljet spotsize_x_um,m'])
    entry.metaljet_spotsize_y_um = get_value(row['metaljet spotsize_y_um,m'])
    entry.metaljet_spot_position_x_um = get_value(row['metaljet spot_position_x_um,m'])
    entry.metaljet_spot_position_y_um = get_value(row['metaljet spot_position_y_um,m'])
    entry.metaljet_jet_pressure = get_value(row['metaljet jet_pressure,m'])
    entry.metaljet_vacuum_pressure_mbar = get_value(
        row['metaljet vacuum_pressure_mbar,m']
    )
    entry.detector_position_pos = get_value(row['detector_position pos'])
    entry.detector_position_rel_pos = get_value(row['detector_position rel_pos'])
    entry.detector_position_valid = get_value(row['detector_position valid'])
    entry.filter_open = get_value(row['filter_ open'])

    return entry


class XRDMetalJetSingleLibraryMeasurement(SingleLibraryMeasurement):
    m_def = Section(
        label_quantity='name',
        a_plot=[
            {
                'x': 'q_nm_inv',
                'y': 'intensity',
                'layout': {
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False},
                },
                'config': {
                    'scrollZoom': True,
                    'staticPlot': False,
                },
            }
        ],
    )

    datetime = Quantity(type=Datetime)

    motors_det_v = Quantity(type=np.dtype(np.float64))
    motors_det_h = Quantity(type=np.dtype(np.float64))
    motors_det_rot = Quantity(type=np.dtype(np.float64))
    motors_x = Quantity(type=np.dtype(np.float64))
    motors_y = Quantity(type=np.dtype(np.float64))
    motors_z = Quantity(type=np.dtype(np.float64))
    motors_phi = Quantity(type=np.dtype(np.float64))
    motors_chi = Quantity(type=np.dtype(np.float64))
    motors_chi_cor = Quantity(type=np.dtype(np.float64))
    motors_omega = Quantity(type=np.dtype(np.float64))
    motors_zhuber = Quantity(type=np.dtype(np.float64))
    motors_xhuber = Quantity(type=np.dtype(np.float64))
    motors_sb = Quantity(type=np.dtype(np.float64))
    motors_st = Quantity(type=np.dtype(np.float64))
    motors_sl = Quantity(type=np.dtype(np.float64))
    motors_sr = Quantity(type=np.dtype(np.float64))
    motors_sv_delta = Quantity(type=np.dtype(np.float64))
    motors_sv_pos = Quantity(type=np.dtype(np.float64))
    motors_sh_delta = Quantity(type=np.dtype(np.float64))
    motors_sh_pos = Quantity(type=np.dtype(np.float64))
    hexapod_x = Quantity(type=np.dtype(np.float64))
    hexapod_y = Quantity(type=np.dtype(np.float64))
    hexapod_z = Quantity(type=np.dtype(np.float64))
    hexapod_u = Quantity(type=np.dtype(np.float64))
    hexapod_v = Quantity(type=np.dtype(np.float64))
    hexapod_w = Quantity(type=np.dtype(np.float64))
    hexapod_pivot_x = Quantity(type=np.dtype(np.float64))
    hexapod_pivot_y = Quantity(type=np.dtype(np.float64))
    hexapod_pivot_z = Quantity(type=np.dtype(np.float64))
    metaljet_generator_emission_power = Quantity(type=np.dtype(np.float64))
    metaljet_generator_high_voltage = Quantity(type=np.dtype(np.float64))
    metaljet_spotsize_x_um = Quantity(type=np.dtype(np.float64))
    metaljet_spotsize_y_um = Quantity(type=np.dtype(np.float64))
    metaljet_spot_position_x_um = Quantity(type=np.dtype(np.float64))
    metaljet_spot_position_y_um = Quantity(type=np.dtype(np.float64))
    metaljet_jet_pressure = Quantity(type=np.dtype(np.float64))
    metaljet_vacuum_pressure_mbar = Quantity(type=np.dtype(np.float64))
    detector_position_pos = Quantity(type=np.dtype(np.float64))
    detector_position_rel_pos = Quantity(type=np.dtype(np.float64))
    detector_position_valid = Quantity(type=np.dtype(np.float64))
    filter_open = Quantity(type=np.dtype(np.float64))

    q_nm_inv = Quantity(type=np.dtype(np.float64), shape=['*'])
    intensity = Quantity(type=np.dtype(np.float64), shape=['*'])


def load_XRD_txt(file_object):
    for _ in range(2):
        next(file_object)
    date = next(file_object).split(' ')[-1]
    time = next(file_object).split(' ')[-1]

    for _ in range(4):
        next(file_object)
    try:
        df = pd.read_csv(
            file_object,
            header=0,
            sep='\t',
            decimal='.',
        )
    except Exception:
        df = pd.read_csv(
            file_object,
            header=0,
            sep='\t',
            decimal=',',
        )
    for c in df.columns:
        df.rename(columns={c: c.strip()}, inplace=True)
    return df, f'{date.strip()} {time.strip()}'


def xrd_read(file_object):
    for _ in range(23):
        next(file_object)
    try:
        df = pd.read_csv(file_object, sep='    ', decimal='.', header=None, dtype=float)
    except Exception:
        df = pd.read_csv(file_object, sep='    ', decimal=',', header=None, dtype=float)
    return df


class TFC_XRDMetalJetLibrary(XRDLibrary, EntryData):
    m_def = Section(
        label='XRD Measurement Library',
        a_eln=dict(
            hide=['instruments', 'steps', 'results', 'lab_id'],
            properties=dict(
                order=[
                    'name',
                ]
            ),
        ),
        a_plot=[
            {
                'x': 'measurements/:/q_nm_inv',
                'y': 'measurements/:/intensity',
                'layout': {
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False},
                },
                'config': {
                    'scrollZoom': True,
                    'staticPlot': False,
                },
            }
        ],
    )

    data_folder = Quantity(type=str, a_eln=dict(component='StringEditQuantity'))

    data_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'),
    )

    measurements = SubSection(
        section_def=XRDMetalJetSingleLibraryMeasurement, repeats=True
    )

    def normalize(self, archive, logger):
        with archive.m_context.raw_file(archive.metadata.mainfile, 'rt') as f:
            os.path.basename(f.name)
            if not self.samples:
                set_sample_reference(archive, self, self.data_folder.split('_')[0])
        if self.data_file and self.data_folder:
            file_path = os.path.join(self.data_folder, self.data_file)
            measurements = []
            files = [
                os.path.basename(file.path)
                for file in archive.m_context.upload_files.raw_directory_list(
                    self.data_folder
                )
                if file.path.endswith('integrated.dat')
            ]
            files.sort()

            with archive.m_context.raw_file(file_path, 'rt') as f:
                df_md, datetime_file = load_XRD_txt(f)

            self.datetime = convert_datetime(
                datetime_file, datetime_format='%Y/%m/%d %H:%M:%S', utc=False
            )

            material_name = ''
            for i, file in enumerate(files):
                with archive.m_context.raw_file(
                    os.path.join(self.data_folder, file), 'rb'
                ) as f:
                    df_data = xrd_read(f)

                measurement_entry = set_single_xrd_measurement_metadata(
                    df_md.iloc[int(file.split('_')[1]) - 1]
                )
                measurement_entry.q_nm_inv = df_data[0]
                measurement_entry.intensity = df_data[1]
                measurement_entry.data_file = [f'{self.data_folder}/{file}']
                measurement_entry.normalize(archive, logger)
                measurements.append(measurement_entry)

            self.measurements = measurements
            self.material_names = material_name

        super().normalize(archive, logger)


# %%######################## Generic Entries
# %%######################## Analysis
m_package.__init_metainfo__()
