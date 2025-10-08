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

import datetime

import pandas as pd
from baseclasses.helper.utilities import (
    create_archive,
    get_entry_id_from_file_name,
    get_reference,
    set_sample_reference,
)
from nomad.datamodel import EntryArchive
from nomad.datamodel.data import (
    EntryData,
)
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
)
from nomad.datamodel.metainfo.basesections import (
    Activity,
    Entity,
)
from nomad.metainfo import (
    Quantity,
)
from nomad.parsing import MatchingParser

from nomad_chemical_energy.schema_packages.ce_nesd_package import (
    CE_NESD_GEIS,
    CE_NESD_PEIS,
    CE_NESD_Chronoamperometry,
    CE_NESD_Chronopotentiometry,
    CE_NESD_ConstantCurrentMode,
    CE_NESD_ConstantVoltageMode,
    CE_NESD_CyclicVoltammetry,
    CE_NESD_ElectrolyserPerformanceEvaluation,
    CE_NESD_GalvanodynamicSweep,
    CE_NESD_LinearSweepVoltammetry,
    CE_NESD_Measurement,
    CE_NESD_OERAnalysis,
    CE_NESD_OpenCircuitVoltage,
    CE_NESD_Sample,
    CE_NESD_Setup,
)
from nomad_chemical_energy.schema_packages.file_parser.biologic_parser import (
    get_header_and_data,
)
from nomad_chemical_energy.schema_packages.file_parser.ch_instruments_txt_parser import (
    parse_chi_txt_file,
)
from nomad_chemical_energy.schema_packages.file_parser.nesd_metadata_excel_parser import (
    get_reference_electrode,
    map_sample,
    map_setup,
)
from nomad_chemical_energy.schema_packages.file_parser.palmsense_parser import (
    get_data_from_pssession_file,
)
from nomad_chemical_energy.schema_packages.file_parser.zahner_parser import (
    get_data_from_ism_file,
    get_data_from_isw_file,
)


class ParsedBioLogicFile(EntryData):
    activity = Quantity(
        type=Activity,
        shape=['*'],
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
        ),
    )


class ParsedZahnerFile(EntryData):
    activity = Quantity(
        type=Activity,
        shape=['*'],
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
        ),
    )


class ParsedCHIFile(EntryData):
    activity = Quantity(
        type=Activity,
        shape=['*'],
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
        ),
    )


class ParsedPalmSensFile(EntryData):
    activity = Quantity(
        type=Activity,
        shape=['*'],
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
        ),
    )


class ParsedLabVIEWFile(EntryData):
    activity = Quantity(
        type=Activity,
        shape=['*'],
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
        ),
    )


class ParsedMetadataExcelFile(EntryData):
    entity = Quantity(
        type=Entity,
        shape=['*'],
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
        ),
    )


class CENESDBioLogicParser(MatchingParser):
    def is_mainfile(
        self,
        filename: str,
        mime: str,
        buffer: bytes,
        decoded_buffer: str,
        compression: str = None,
    ):
        is_mainfile_super = super().is_mainfile(
            filename, mime, buffer, decoded_buffer, compression
        )
        if not is_mainfile_super:
            return False
        with open(filename, 'rb') as f:
            metadata, _ = get_header_and_data(f)
        device_number = metadata.get('log', {}).get('device_sn')
        if device_number in ['1581', '1659']:
            return True
        return False

    def parse(self, mainfile: str, archive: EntryArchive, logger):
        if not mainfile.endswith('.mpr'):
            return

        file = mainfile.split('raw/')[-1]
        with archive.m_context.raw_file(file, 'rb') as f:
            metadata, _ = get_header_and_data(f)

        technique = metadata.get('settings', {}).get('technique')
        match technique:
            case 'CA':
                entry = CE_NESD_Chronoamperometry(data_file=file)
            case 'coC':
                entry = CE_NESD_ConstantCurrentMode(data_file=file)
            case 'coV':
                entry = CE_NESD_ConstantVoltageMode(data_file=file)
            case 'CP':
                entry = CE_NESD_Chronopotentiometry(data_file=file)
            case 'CV':
                entry = CE_NESD_CyclicVoltammetry(data_file=file)
            case 'GEIS':
                entry = CE_NESD_GEIS(data_file=file)
            case 'LSV':
                entry = CE_NESD_LinearSweepVoltammetry(data_file=file)
            case 'OCV':
                entry = CE_NESD_OpenCircuitVoltage(data_file=file)
            case 'PEIS':
                entry = CE_NESD_PEIS(data_file=file)
            case _:
                entry = CE_NESD_Measurement(data_file=file)

        electrolyser_id = file.split('/')[-1][:8]
        set_sample_reference(archive, entry, electrolyser_id)
        entry.datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        entry.name = file.split('.')[0]
        file_name = f'{file}.archive.json'
        create_archive(entry, archive, file_name)

        entry_id = get_entry_id_from_file_name(file_name, archive)
        archive.data = ParsedBioLogicFile(
            activity=[get_reference(archive.metadata.upload_id, entry_id)]
        )
        archive.metadata.entry_name = file


class CENESDZahnerParser(MatchingParser):
    def parse(self, mainfile: str, archive: EntryArchive, logger):
        if not mainfile.endswith(('.isw', '.ism', '.isc')):
            return
        file = mainfile.split('raw/')[-1]

        if mainfile.endswith('.isw'):
            with archive.m_context.raw_file(file, 'rb') as f:
                try:
                    with archive.m_context.raw_file(
                        file.replace('.isw', '_c.txt'), 'tr'
                    ) as f_m:
                        metadata = f_m.read()
                except Exception:
                    metadata = None
                d = get_data_from_isw_file(f.read(), metadata)
        if mainfile.endswith('.ism'):
            with archive.m_context.raw_file(file, 'rb') as f:
                d = get_data_from_ism_file(f.read())
        if mainfile.endswith('.isc'):
            d = {'method': 'cv'}

        technique = d.get('method')
        match technique:
            case 'ca':
                entry = CE_NESD_Chronoamperometry(data_file=file)
            case 'cv':
                entry = CE_NESD_CyclicVoltammetry(data_file=file)
            case 'lsv':
                entry = CE_NESD_LinearSweepVoltammetry(data_file=file)
            case 'gds':
                entry = CE_NESD_GalvanodynamicSweep(data_file=file)
            case 'geis':
                entry = CE_NESD_GEIS(data_file=file)
            case 'peis':
                entry = CE_NESD_PEIS(data_file=file)
            case 'cp':
                entry = CE_NESD_Chronopotentiometry(data_file=file)

        electrolyser_id = file.split('/')[-1][:8]
        set_sample_reference(archive, entry, electrolyser_id)
        entry.name = file.split('.')[0]
        file_name = f'{file}.archive.json'
        create_archive(entry, archive, file_name)

        entry_id = get_entry_id_from_file_name(file_name, archive)
        archive.data = ParsedZahnerFile(
            activity=[get_reference(archive.metadata.upload_id, entry_id)]
        )
        archive.metadata.entry_name = file


class CENESDCHIParser(MatchingParser):
    def parse(self, mainfile: str, archive: EntryArchive, logger):
        if not mainfile.endswith('.txt'):
            return
        file = mainfile.split('raw/')[-1]

        with archive.m_context.raw_file(file, 'tr') as f:
            m, _ = parse_chi_txt_file(f.read())

        technique = m.get('method')
        match technique:
            # case 'ca':
            #     entry = CE_NESD_Chronoamperometry(data_file=file)
            case 'Cyclic Voltammetry':
                entry = CE_NESD_CyclicVoltammetry(data_file=file)
            case 'Linear Sweep Voltammetry':
                entry = CE_NESD_LinearSweepVoltammetry(data_file=file)
            # case 'gds':
            #     entry = CE_NESD_GalvanodynamicSweep(data_file=file)
            # case 'geis':
            #     entry = CE_NESD_GEIS(data_file=file)
            case 'A.C. Impedance':
                entry = CE_NESD_PEIS(data_file=file)
            # case 'cp':
            #     entry = CE_NESD_Chronopotentiometry(data_file=file)

        electrolyser_id = file.split('/')[-1][:8]
        set_sample_reference(archive, entry, electrolyser_id)
        entry.name = file.split('.')[0]
        file_name = f'{file}.archive.json'
        create_archive(entry, archive, file_name)

        entry_id = get_entry_id_from_file_name(file_name, archive)
        archive.data = ParsedCHIFile(
            activity=[get_reference(archive.metadata.upload_id, entry_id)]
        )
        archive.metadata.entry_name = file


class CENESDLabviewParser(MatchingParser):
    def parse(self, mainfile: str, archive: EntryArchive, logger):
        file = mainfile.split('raw/')[-1]

        if not file.endswith('.tdms'):
            return

        entry = CE_NESD_ElectrolyserPerformanceEvaluation(data_file=file)
        electrolyser_id = file.split('.')[0][:8]
        set_sample_reference(archive, entry, electrolyser_id)
        entry.datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        entry.name = file.split('.')[0]
        file_name = f'{file}.archive.json'
        create_archive(entry, archive, file_name)

        entry_id = get_entry_id_from_file_name(file_name, archive)
        archive.data = ParsedLabVIEWFile(
            activity=[get_reference(archive.metadata.upload_id, entry_id)]
        )
        archive.metadata.entry_name = file


class CENESDPalmSensParser(MatchingParser):
    def parse(self, mainfile: str, archive: EntryArchive, logger):
        if not mainfile.endswith('.pssession'):
            return
        file = mainfile.split('raw/')[-1]
        with archive.m_context.raw_file(file, 'rt', encoding='utf-16') as f:
            data = get_data_from_pssession_file(f.read())

        if len(data['Measurements']) != 1:
            return
        technique = data['Measurements'][0]['Title']
        match technique:
            case 'Open Circuit Potentiometry':
                entry = CE_NESD_OpenCircuitVoltage(data_file=file)
            case 'Chronoamperometry':
                entry = CE_NESD_Chronoamperometry(data_file=file)
            case 'Cyclic Voltammetry':
                entry = CE_NESD_CyclicVoltammetry(data_file=file)
            case 'Linear Sweep Voltammetry':
                entry = CE_NESD_LinearSweepVoltammetry(data_file=file)
            # case 'gds':
            #     entry = CE_NESD_GalvanodynamicSweep(data_file=file)
            case 'Impedance Spectroscopy':
                entry = CE_NESD_PEIS(data_file=file)
            case 'Chronopotentiometry':
                entry = CE_NESD_Chronopotentiometry(data_file=file)

        electrolyser_id = file.split('/')[-1][:8]
        set_sample_reference(archive, entry, electrolyser_id)
        entry.name = file.split('.')[0]
        file_name = f'{file}.archive.json'
        create_archive(entry, archive, file_name)

        entry_id = get_entry_id_from_file_name(file_name, archive)
        archive.data = ParsedPalmSensFile(
            activity=[get_reference(archive.metadata.upload_id, entry_id)]
        )
        archive.metadata.entry_name = file


class CENESDMetadataExcelParser(MatchingParser):
    def to_float_if_possible(self, value):
        if pd.isna(value):
            return None
        value_str = str(value).replace(',', '.')
        try:
            return float(value_str)
        except ValueError:
            return value_str

    def parse(self, mainfile: str, archive: EntryArchive, logger):
        file = mainfile.split('raw/')[-1]

        if not file.endswith('.xlsx'):
            return

        setup_entry = CE_NESD_Setup()
        setup_entry.datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        folder_path = ('/' + file).rsplit('/', 1)[0]
        setup_entry.name = f'{folder_path}/electrochemical_setup_and_electrolyte'[1:]

        sample_entry = CE_NESD_Sample()
        sample_entry.datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        sample_entry.name = f'{folder_path}/sample'[1:]

        with archive.m_context.raw_file(file, 'rb') as f:
            xls_file = pd.ExcelFile(f)
            excel_data = pd.read_excel(xls_file, sheet_name='NESD Metadata')
            excel_data['Value'] = excel_data['Value'].apply(self.to_float_if_possible)
            mapping = dict(zip(excel_data.loc[:, 'Field'], excel_data.loc[:, 'Value']))
            map_setup(setup_entry, mapping)
            map_sample(sample_entry, mapping)

        ref_electrode_file_name = f'{file}_reference_electrode.archive.json'
        reference_electrode_entry = get_reference_electrode(mapping)
        create_archive(reference_electrode_entry, archive, ref_electrode_file_name)
        ref_electrode_entry_id = get_entry_id_from_file_name(
            ref_electrode_file_name, archive
        )
        setup_entry.reference_electrode = get_reference(
            archive.metadata.upload_id, ref_electrode_entry_id
        )

        setup_file_name = f'{file}_setup.archive.json'
        create_archive(setup_entry, archive, setup_file_name)
        setup_entry_id = get_entry_id_from_file_name(setup_file_name, archive)

        sample_file_name = f'{file}_sample.archive.json'
        create_archive(sample_entry, archive, sample_file_name)
        sample_entry_id = get_entry_id_from_file_name(sample_file_name, archive)

        archive.data = ParsedMetadataExcelFile(
            entity=[
                get_reference(archive.metadata.upload_id, sample_entry_id),
                get_reference(archive.metadata.upload_id, setup_entry_id),
            ]
        )
        archive.metadata.entry_name = file

        if mapping.get('Reaction type') == 'OER':
            analysis_name = f'{folder_path}/oer_analysis'[1:]
            analysis_file_name = f'{analysis_name}.archive.json'
            create_archive(
                CE_NESD_OERAnalysis(name=analysis_name), archive, analysis_file_name
            )
