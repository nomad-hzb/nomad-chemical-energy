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
from baseclasses import BaseMeasurement
from baseclasses.chemical_energy import (
    CENESDSample,
    Chronoamperometry,
    Chronopotentiometry,
    CyclicVoltammetry,
    ElectrochemicalImpedanceSpectroscopyMultiple,
    ElectroChemicalSetup,
    ElectrolyserPerformanceEvaluation,
    ElectrolyserProperties,
    Environment,
    GalvanodynamicSweep,
    LinearSweepVoltammetry,
    NESDElectrode,
    OpenCircuitVoltage,
    ReferenceElectrode,
    SampleIDCENESD,
)
from baseclasses.helper.archive_builder.labview_archive import (
    get_electrolyser_properties,
    get_tdms_archive,
)
from baseclasses.helper.utilities import (
    create_archive,
    get_entry_id_from_file_name,
    get_reference,
)
from nomad.datamodel.data import EntryData
from nomad.datamodel.metainfo.basesections import CompositeSystemReference
from nomad.datamodel.metainfo.plot import PlotlyFigure, PlotSection
from nomad.metainfo import Quantity, SchemaPackage, Section, SubSection

from nomad_chemical_energy.schema_packages.file_parser.electrolyser_tdms_parser import (
    get_info_and_data,
)
from nomad_chemical_energy.schema_packages.file_parser.palmsense_parser import (
    get_data_from_pssession_file,
    map_eis_data,
    map_voltammetry_data,
)
from nomad_chemical_energy.schema_packages.utilities.ce_nesd_oer_analysis import (
    NESD_OERAnalysis,
    NESD_OERCompareReplicates,
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


class CE_NESD_Sample(CENESDSample, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['users', 'elemental_composition', 'chemical_composition_or_formulas'],
            properties=dict(
                order=[
                    'name',
                    'lab_id',
                    'components',
                    'id_of_preparation_protocol',
                ]
            ),
        ),
        label_quantity='sample_id',
    )


class CE_NESD_Electrode(NESDElectrode, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['components', 'elemental_composition'],
        ),
    )


class CE_NESD_ReferenceElectrode(ReferenceElectrode, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['components', 'elemental_composition'],
        ),
    )


class CE_NESD_Electrolyser(ElectrolyserProperties, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['components', 'elemental_composition'],
            properties=dict(
                order=[
                    'name',
                    'cell_name',
                    'lab_id',
                    'datetime',
                ]
            ),
        ),
    )

    def normalize(self, archive, logger):
        super().normalize(archive, logger)


class CE_NESD_Electrolyte(Environment, EntryData):
    m_def = Section(
        a_eln=dict(
            overview=True,
            hide=[
                'name',
                'origin',
                'datetime',
                'lab_id',
                'elemental_composition',
                'components',
            ],
        ),
    )


class CE_NESD_Setup(ElectroChemicalSetup, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'users',
                'elemental_composition',
                'components',
                'substrate',
            ],
            properties=dict(
                order=[
                    'name',
                    'lab_id',
                    'origin',
                    'chemical_composition_or_formulas',
                    'setup',
                    'reference_electrode',
                    'counter_electrode',
                    'equipment',
                ]
            ),
        ),
    )

    # TODO what should ID look like?
    setup_id = SubSection(section_def=SampleIDCENESD)

    environment = SubSection(
        links=['https://w3id.org/nfdi4cat/voc4cat_0007223'],
        section_def=CE_NESD_Electrolyte,
        label='Electrolyte',
    )

    ir_compensation = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(component='NumberEditQuantity'),
        label='iR compensation',
    )

    def normalize(self, archive, logger):
        super().normalize(archive, logger)


# %% ####################### Generic Entries


class CE_NESD_Measurement(BaseMeasurement, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'location', 'steps', 'instruments', 'results'],
            properties=dict(order=['name', 'data_file', 'samples']),
        ),
    )

    data_file = Quantity(
        type=str,
        shape=['*'],
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'),
    )


# %% ####################### Measurements


def find_electrolyser_in_folder(archive, datafile):
    folder = os.path.dirname(datafile)
    tdms_files = []
    for item in archive.m_context.upload_files.raw_directory_list(folder):
        if not item.path.endswith('.tdms'):
            continue
        tdms_files.append(item.path)
    if len(tdms_files) == 1:
        electrolyser_entry_id = get_entry_id_from_file_name(
            tdms_files[0].split('.')[0] + '_electrolyser.archive.json', archive
        )
        return [
            CompositeSystemReference(
                reference=get_reference(
                    archive.metadata.upload_id, electrolyser_entry_id
                )
            )
        ]


def find_setup_in_folder(archive, datafile):
    # this function only finds setups that are created via the NESD metadata excel file (xlsx_setup ending)
    folder = os.path.dirname(datafile)
    setup_files = []
    for item in archive.m_context.upload_files.raw_directory_list(folder):
        if not item.path.endswith('.xlsx_setup.archive.json'):
            continue
        setup_files.append(item.path)
    if len(setup_files) == 1:
        setup_entry_id = get_entry_id_from_file_name(setup_files[0], archive)
        return get_reference(archive.metadata.upload_id, setup_entry_id)


def find_sample_in_folder(archive, datafile):
    # this function only finds samples that are created via the NESD metadata excel file (xlsx_sample ending)
    folder = os.path.dirname(datafile)
    sample_files = []
    for item in archive.m_context.upload_files.raw_directory_list(folder):
        if not item.path.endswith('.xlsx_sample.archive.json'):
            continue
        sample_files.append(item.path)
    if len(sample_files) == 1:
        sample_entry_id = get_entry_id_from_file_name(sample_files[0], archive)
        return [
            CompositeSystemReference(
                reference=get_reference(archive.metadata.upload_id, sample_entry_id)
            )
        ]


def set_sample(archive, entry):
    if not entry.samples:
        entry.samples = find_electrolyser_in_folder(archive, entry.data_file)
        entry.samples.label = 'electrolyser'
    if not entry.samples:
        entry.samples = find_sample_in_folder(archive, entry.data_file)
        if entry.samples is not None:
            entry.samples.label = 'samples'


class CE_NESD_Chronoamperometry(Chronoamperometry, EntryData, PlotSection):
    m_def = Section(
        a_eln=dict(
            hide=[
                'metadata_file',
                'lab_id',
                'location',
                'control',
                'environment',
                'steps',
                'cycles',
                'instruments',
                'results',
            ],
            properties=dict(
                order=[
                    'name',
                    'data_file',
                    'setup',
                    'station',
                    'voltage_shift',
                    'resistance',
                    'samples',
                ],
            ),
        ),
    )
    samples = (
        BaseMeasurement.samples.m_copy()
    )  # needed to link either electrolyser or sample

    def normalize(self, archive, logger):
        if self.data_file:
            if os.path.splitext(self.data_file)[-1] == '.pssession':
                with archive.m_context.raw_file(
                    self.data_file, 'rt', encoding='utf-16'
                ) as f:
                    d = get_data_from_pssession_file(f.read())
                map_voltammetry_data(self, d)
            with archive.m_context.raw_file(self.data_file, 'rb') as f:
                if os.path.splitext(self.data_file)[-1] == '.isw':
                    from nomad_chemical_energy.schema_packages.file_parser.zahner_parser import (
                        get_data_from_isw_file,
                        set_zahner_data_isw,
                    )

                    try:
                        with archive.m_context.raw_file(
                            self.data_file.replace('.isw', '_c.txt'), 'tr'
                        ) as f_m:
                            metadata = f_m.read()
                    except Exception:
                        metadata = None
                    d = get_data_from_isw_file(f.read(), metadata)
                    set_zahner_data_isw(self, d)

                elif os.path.splitext(self.data_file)[-1] == '.mpr':
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
        set_sample(archive, self)
        if not self.setup:
            self.setup = find_setup_in_folder(archive, self.data_file)
        if self.setup and self.voltage_shift == 0:
            if self.setup.get('reference_electrode') is not None:
                self.voltage_shift = self.setup.get('reference_electrode').get(
                    'standard_potential'
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


class CE_NESD_Chronopotentiometry(Chronopotentiometry, EntryData, PlotSection):
    m_def = Section(
        a_eln=dict(
            hide=[
                'metadata_file',
                'lab_id',
                'location',
                'control',
                'charge_density',
                'environment',
                'steps',
                'cycles',
                'instruments',
                'results',
            ],
            properties=dict(
                order=[
                    'name',
                    'data_file',
                    'setup',
                    'station',
                    'voltage_shift',
                    'resistance',
                    'samples',
                ]
            ),
        ),
    )
    samples = (
        BaseMeasurement.samples.m_copy()
    )  # needed to link either electrolyser or sample

    def normalize(self, archive, logger):
        if self.data_file:
            if os.path.splitext(self.data_file)[-1] == '.pssession':
                with archive.m_context.raw_file(
                    self.data_file, 'rt', encoding='utf-16'
                ) as f:
                    d = get_data_from_pssession_file(f.read())
                map_voltammetry_data(self, d)
            with archive.m_context.raw_file(self.data_file, 'rb') as f:
                if os.path.splitext(self.data_file)[-1] == '.isw':
                    from nomad_chemical_energy.schema_packages.file_parser.zahner_parser import (
                        get_data_from_isw_file,
                        set_zahner_data_isw,
                    )

                    try:
                        with archive.m_context.raw_file(
                            self.data_file.replace('.isw', '_c.txt'), 'tr'
                        ) as f_m:
                            metadata = f_m.read()
                    except Exception:
                        metadata = None

                    d = get_data_from_isw_file(f.read(), metadata)
                    set_zahner_data_isw(self, d)

                elif os.path.splitext(self.data_file)[-1] == '.mpr':
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
        set_sample(archive, self)
        if not self.setup:
            self.setup = find_setup_in_folder(archive, self.data_file)
        if self.setup and self.voltage_shift == 0:
            if self.setup.get('reference_electrode') is not None:
                self.voltage_shift = self.setup.get('reference_electrode').get(
                    'standard_potential'
                )
        super().normalize(archive, logger)
        fig1 = make_voltage_plot(self.time, self.voltage)
        self.figures = [
            PlotlyFigure(label='Voltage over Time', figure=json.loads(fig1.to_json())),
        ]


class CE_NESD_ConstantCurrentMode(Chronopotentiometry, EntryData, PlotSection):
    m_def = Section(
        a_eln=dict(
            hide=[
                'metadata_file',
                'lab_id',
                'location',
                'control',
                'charge_density',
                'environment',
                'steps',
                'cycles',
                'instruments',
                'results',
            ],
            properties=dict(
                order=[
                    'name',
                    'data_file',
                    'setup',
                    'station',
                    'voltage_shift',
                    'resistance',
                    'samples',
                ]
            ),
        ),
    )
    samples = (
        BaseMeasurement.samples.m_copy()
    )  # needed to link either electrolyser or sample

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


class CE_NESD_ConstantVoltageMode(Chronoamperometry, EntryData, PlotSection):
    m_def = Section(
        a_eln=dict(
            hide=[
                'metadata_file',
                'lab_id',
                'location',
                'control',
                'charge_density',
                'environment',
                'steps',
                'cycles',
                'instruments',
                'results',
            ],
            properties=dict(
                order=[
                    'name',
                    'data_file',
                    'setup',
                    'station',
                    'voltage_shift',
                    'resistance',
                    'samples',
                ]
            ),
        ),
    )
    samples = (
        BaseMeasurement.samples.m_copy()
    )  # needed to link either electrolyser or sample

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


class CE_NESD_CyclicVoltammetry(CyclicVoltammetry, EntryData, PlotSection):
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
    samples = (
        BaseMeasurement.samples.m_copy()
    )  # needed to link either electrolyser or sample

    def normalize(self, archive, logger):
        if self.data_file:
            if os.path.splitext(self.data_file)[-1] == '.pssession':
                with archive.m_context.raw_file(
                    self.data_file, 'rt', encoding='utf-16'
                ) as f:
                    d = get_data_from_pssession_file(f.read())
                map_voltammetry_data(self, d)
                self.set_calculated_properties()

            if os.path.splitext(self.data_file)[-1] == '.txt':
                from nomad_chemical_energy.schema_packages.file_parser.ch_instruments_txt_parser import (
                    get_data_from_cv_txt_file,
                    set_chi_data_cv,
                )

                with archive.m_context.raw_file(self.data_file, 'r') as f:
                    d = get_data_from_cv_txt_file(f.read())
                set_chi_data_cv(self, d)

            with archive.m_context.raw_file(self.data_file, 'rb') as f:
                if os.path.splitext(self.data_file)[-1] == '.isc':
                    from nomad_chemical_energy.schema_packages.file_parser.zahner_parser import (
                        get_data_from_isc_file,
                        set_zahner_data_isc,
                    )

                    d = get_data_from_isc_file(f.read())
                    set_zahner_data_isc(self, d)
                    self.set_calculated_properties()

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
        set_sample(archive, self)
        if not self.setup:
            self.setup = find_setup_in_folder(archive, self.data_file)
        if self.setup and self.voltage_shift == 0:
            if self.setup.get('reference_electrode') is not None:
                self.voltage_shift = self.setup.get('reference_electrode').get(
                    'standard_potential'
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


class CE_NESD_ElectrolyserPerformanceEvaluation(
    ElectrolyserPerformanceEvaluation, EntryData, PlotSection
):
    m_def = Section(
        a_eln=dict(
            hide=['location', 'steps', 'instruments', 'results', 'lab_id'],
            properties=dict(
                order=[
                    'name',
                    'data_file',
                    'datetime',
                    'laview_user',
                    'description',
                ]
            ),
        ),
    )

    samples = (
        BaseMeasurement.samples.m_copy()
    )  # needed to link either electrolyser or sample
    samples.label = 'electrolyser'

    def normalize(self, archive, logger):
        if self.data_file:
            with archive.m_context.raw_file(self.data_file, 'rb') as f:
                if os.path.splitext(self.data_file)[-1] == '.tdms':
                    metadata, data = get_info_and_data(f)
                    get_tdms_archive(data, self)
                    self.name = metadata.get('name')
                    self.labview_user = metadata.get('User_Name')
                    self.description = metadata.get('Comments')
                    # caution: samples has the "electrolyser properties" label in the GUI
                    if not self.samples:
                        # if filename starts with id this is already used for reference
                        # otherwise create a new CE_NESD_Electrolyser and reference this one
                        file_name = archive.metadata.mainfile.split('.')[0]
                        electrolyser_file_name = (
                            f'{file_name}_electrolyser.archive.json'
                        )
                        electrolyser = get_electrolyser_properties(
                            metadata, CE_NESD_Electrolyser()
                        )
                        create_archive(
                            electrolyser,
                            archive,
                            electrolyser_file_name,
                            overwrite=False,
                        )
                        electrolyser_entry_id = get_entry_id_from_file_name(
                            electrolyser_file_name, archive
                        )
                        self.samples = [
                            CompositeSystemReference(
                                reference=get_reference(
                                    archive.metadata.upload_id, electrolyser_entry_id
                                )
                            )
                        ]

        super().normalize(archive, logger)


class CE_NESD_GEIS(
    ElectrochemicalImpedanceSpectroscopyMultiple, EntryData, PlotSection
):
    m_def = Section(
        a_eln=dict(
            hide=[
                'environment',
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
                    'setup',
                    'station',
                    'samples',
                ]
            ),
        ),
    )

    samples = (
        BaseMeasurement.samples.m_copy()
    )  # needed to link either electrolyser or sample

    def normalize(self, archive, logger):
        if self.data_file:
            with archive.m_context.raw_file(self.data_file, 'rb') as f:
                if os.path.splitext(self.data_file)[-1] == '.ism':
                    from nomad_chemical_energy.schema_packages.file_parser.zahner_parser import (
                        get_data_from_ism_file,
                        set_zahner_data_ism,
                    )

                    d = get_data_from_ism_file(f.read())
                    set_zahner_data_ism(self, d)

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
        set_sample(archive, self)
        if not self.setup:
            self.setup = find_setup_in_folder(archive, self.data_file)
        super().normalize(archive, logger)
        fig1 = make_nyquist_plot(self.measurements)
        fig2 = make_bode_plot(self.measurements)
        self.figures = [
            PlotlyFigure(label='Nyquist Plot', figure=json.loads(fig1.to_json())),
            PlotlyFigure(label='Bode Plot', figure=json.loads(fig2.to_json())),
        ]


class CE_NESD_LinearSweepVoltammetry(LinearSweepVoltammetry, EntryData, PlotSection):
    m_def = Section(
        a_eln=dict(
            hide=[
                'metadata_file',
                'lab_id',
                'location',
                'control',
                'charge_density',
                'environment',
                'steps',
                'cycles',
                'instruments',
                'results',
            ],
            properties=dict(
                order=[
                    'name',
                    'data_file',
                    'setup',
                    'station',
                    'voltage_shift',
                    'resistance',
                    'samples',
                ]
            ),
        ),
    )

    samples = (
        BaseMeasurement.samples.m_copy()
    )  # needed to link either electrolyser or sample

    def normalize(self, archive, logger):
        if self.data_file:
            if os.path.splitext(self.data_file)[-1] == '.pssession':
                with archive.m_context.raw_file(
                    self.data_file, 'rt', encoding='utf-16'
                ) as f:
                    d = get_data_from_pssession_file(f.read())
                map_voltammetry_data(self, d)

            if os.path.splitext(self.data_file)[-1] == '.txt':
                from nomad_chemical_energy.schema_packages.file_parser.ch_instruments_txt_parser import (
                    get_data_from_lsv_txt_file,
                    set_chi_data_lsv,
                )

                with archive.m_context.raw_file(self.data_file, 'r') as f:
                    d = get_data_from_lsv_txt_file(f.read())
                set_chi_data_lsv(self, d)

            with archive.m_context.raw_file(self.data_file, 'rb') as f:
                if os.path.splitext(self.data_file)[-1] == '.isw':
                    from nomad_chemical_energy.schema_packages.file_parser.zahner_parser import (
                        get_data_from_isw_file,
                        set_zahner_data_isw,
                    )

                    try:
                        with archive.m_context.raw_file(
                            self.data_file.replace('.isw', '_c.txt'), 'tr'
                        ) as f_m:
                            metadata = f_m.read()
                    except Exception:
                        metadata = None
                    d = get_data_from_isw_file(f.read(), metadata)
                    set_zahner_data_isw(self, d)

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
        set_sample(archive, self)
        if not self.setup:
            self.setup = find_setup_in_folder(archive, self.data_file)
        if self.setup and self.voltage_shift == 0:
            if self.setup.get('reference_electrode') is not None:
                self.voltage_shift = self.setup.get('reference_electrode').get(
                    'standard_potential'
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


class CE_NESD_GalvanodynamicSweep(GalvanodynamicSweep, EntryData, PlotSection):
    m_def = Section(
        a_eln=dict(
            hide=[
                'metadata_file',
                'lab_id',
                'location',
                'control',
                'charge_density',
                'environment',
                'steps',
                'cycles',
                'instruments',
                'results',
            ],
            properties=dict(
                order=[
                    'name',
                    'data_file',
                    'setup',
                    'station',
                    'voltage_shift',
                    'resistance',
                    'samples',
                ]
            ),
        ),
    )

    samples = (
        BaseMeasurement.samples.m_copy()
    )  # needed to link either electrolyser or sample

    def normalize(self, archive, logger):
        if self.data_file:
            with archive.m_context.raw_file(self.data_file, 'rb') as f:
                if os.path.splitext(self.data_file)[-1] == '.isw':
                    from nomad_chemical_energy.schema_packages.file_parser.zahner_parser import (
                        get_data_from_isw_file,
                        set_zahner_data_isw,
                    )

                    try:
                        with archive.m_context.raw_file(
                            self.data_file.replace('.isw', '_c.txt'), 'tr'
                        ) as f_m:
                            metadata = f_m.read()
                    except Exception:
                        metadata = None

                    d = get_data_from_isw_file(f.read(), metadata)
                    set_zahner_data_isw(self, d)
        set_sample(archive, self)
        if not self.setup:
            self.setup = find_setup_in_folder(archive, self.data_file)
        if self.setup and self.voltage_shift == 0:
            if self.setup.get('reference_electrode') is not None:
                self.voltage_shift = self.setup.get('reference_electrode').get(
                    'standard_potential'
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


class CE_NESD_OpenCircuitVoltage(OpenCircuitVoltage, EntryData, PlotSection):
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
                'steps',
                'cycles',
                'instruments',
                'results',
            ],
            properties=dict(
                order=[
                    'name',
                    'data_file',
                    'setup',
                    'station',
                    'voltage_shift',
                    'resistance',
                    'samples',
                ]
            ),
        ),
    )

    samples = (
        BaseMeasurement.samples.m_copy()
    )  # needed to link either electrolyser or sample

    def normalize(self, archive, logger):
        if self.data_file:
            if os.path.splitext(self.data_file)[-1] == '.pssession':
                with archive.m_context.raw_file(
                    self.data_file, 'rt', encoding='utf-16'
                ) as f:
                    d = get_data_from_pssession_file(f.read())
                map_voltammetry_data(self, d)
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
        set_sample(archive, self)
        if not self.setup:
            self.setup = find_setup_in_folder(archive, self.data_file)
        if self.setup and self.voltage_shift == 0:
            if self.setup.get('reference_electrode') is not None:
                self.voltage_shift = self.setup.get('reference_electrode').get(
                    'standard_potential'
                )
        super().normalize(archive, logger)
        fig1 = make_voltage_plot(self.time, self.voltage)
        self.figures = [
            PlotlyFigure(label='Voltage over Time', figure=json.loads(fig1.to_json())),
        ]


class CE_NESD_PEIS(
    ElectrochemicalImpedanceSpectroscopyMultiple, EntryData, PlotSection
):
    m_def = Section(
        a_eln=dict(
            hide=[
                'environment',
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
                    'setup',
                    'station',
                    'samples',
                ]
            ),
        ),
    )

    samples = (
        BaseMeasurement.samples.m_copy()
    )  # needed to link either electrolyser or sample

    def normalize(self, archive, logger):
        if self.data_file:
            if os.path.splitext(self.data_file)[-1] == '.pssession':
                with archive.m_context.raw_file(
                    self.data_file, 'rt', encoding='utf-16'
                ) as f:
                    d = get_data_from_pssession_file(f.read())
                map_eis_data(self, d)

            if os.path.splitext(self.data_file)[-1] == '.txt':
                from nomad_chemical_energy.schema_packages.file_parser.ch_instruments_txt_parser import (
                    get_data_from_eis_txt_file,
                    set_chi_data_eis,
                )

                with archive.m_context.raw_file(self.data_file, 'r') as f:
                    d = get_data_from_eis_txt_file(f.read())
                set_chi_data_eis(self, d)
            with archive.m_context.raw_file(self.data_file, 'rb') as f:
                if os.path.splitext(self.data_file)[-1] == '.ism':
                    from nomad_chemical_energy.schema_packages.file_parser.zahner_parser import (
                        get_data_from_ism_file,
                        set_zahner_data_ism,
                    )

                    d = get_data_from_ism_file(f.read())
                    set_zahner_data_ism(self, d)
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
        set_sample(archive, self)
        if not self.setup:
            self.setup = find_setup_in_folder(archive, self.data_file)
        super().normalize(archive, logger)
        fig1 = make_nyquist_plot(self.measurements)
        fig2 = make_bode_plot(self.measurements)
        self.figures = [
            PlotlyFigure(label='Nyquist Plot', figure=json.loads(fig1.to_json())),
            PlotlyFigure(label='Bode Plot', figure=json.loads(fig2.to_json())),
        ]
        super().normalize(archive, logger)


# %%####################################### Analysis


class CE_NESD_OERAnalysis(NESD_OERAnalysis, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['location', 'lab_id', 'description', 'method', 'steps'],
            properties=dict(order=['name']),
        )
    )


class CE_NESD_OERCompareReplicates(NESD_OERCompareReplicates, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['location', 'lab_id', 'description', 'method', 'steps'],
            properties=dict(order=['name']),
        )
    )


m_package.__init_metainfo__()
