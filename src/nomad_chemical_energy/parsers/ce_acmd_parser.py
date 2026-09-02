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
    CE_ACMD_GEIS,
    CE_ACMD_PEIS,
    CE_ACMD_Chronoamperometry,
    CE_ACMD_Chronopotentiometry,
    CE_ACMD_ConstantCurrentMode,
    CE_ACMD_ConstantVoltageMode,
    CE_ACMD_CyclicVoltammetry,
    CE_ACMD_Electrolyser,
    CE_ACMD_ElectrolyserPerformanceEvaluation,
    CE_ACMD_GalvanodynamicSweep,
    CE_ACMD_LinearSweepVoltammetry,
    CE_ACMD_Measurement,
    CE_ACMD_OERAnalysis,
    CE_ACMD_OpenCircuitVoltage,
    CE_ACMD_Sample,
    CE_ACMD_Setup,
)
from nomad_chemical_energy.schema_packages.file_parser.biologic_parser import (
    get_header_and_data,
)
from nomad_chemical_energy.schema_packages.file_parser.ch_instruments_parser import (
    parse_chi_txt_file,
    parse_metadata_chi_bin_file,
)
from nomad_chemical_energy.schema_packages.file_parser.acmd_metadata_excel_parser import (
    get_electrode,
    get_reference_electrode,
    map_electrolyser,
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


class CEACMDBioLogicParser(MatchingParser):
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
        if device_number in ['1581', '1659', '.006311']:
            return True
        return False

    def parse(self, mainfile: str, archive: EntryArchive, logger):
        if not mainfile.endswith('.mpr'):
            return

        file = mainfile.rsplit('raw/', maxsplit=1)[-1]
        with archive.m_context.raw_file(file, 'rb') as f:
            metadata, _ = get_header_and_data(f)

        technique = metadata.get('settings', {}).get('technique')
        match technique:
            case 'CA':
                entry = CE_ACMD_Chronoamperometry(data_file=file)
            case 'coC':
                entry = CE_ACMD_ConstantCurrentMode(data_file=file)
            case 'coV':
                entry = CE_ACMD_ConstantVoltageMode(data_file=file)
            case 'CP':
                entry = CE_ACMD_Chronopotentiometry(data_file=file)
            case 'CV':
                entry = CE_ACMD_CyclicVoltammetry(data_file=file)
            case 'GEIS':
                entry = CE_ACMD_GEIS(data_file=file)
            case 'LSV':
                entry = CE_ACMD_LinearSweepVoltammetry(data_file=file)
            case 'OCV':
                entry = CE_ACMD_OpenCircuitVoltage(data_file=file)
            case 'PEIS':
                entry = CE_ACMD_PEIS(data_file=file)
            case _:
                entry = CE_ACMD_Measurement(data_file=file)

        electrolyser_id = file.split('/')[-1][:8]
        set_sample_reference(archive, entry, electrolyser_id)
        entry.datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        entry.name = file.split('.')[0]
        file_name = f'{file}.archive.json'
        create_archive(entry, archive, file_name, overwrite=True)   # TODO remove overwrite after reprocessing all nesd->acmd uploads
        entry_id = get_entry_id_from_file_name(file_name, archive)
        archive.data = ParsedBioLogicFile(
            activity=[get_reference(archive.metadata.upload_id, entry_id)]
        )
        archive.metadata.entry_name = file


class CEACMDZahnerParser(MatchingParser):
    def parse(self, mainfile: str, archive: EntryArchive, logger):
        if not mainfile.endswith(('.isw', '.ism', '.isc')):
            return
        file = mainfile.rsplit('raw/', maxsplit=1)[-1]

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
                entry = CE_ACMD_Chronoamperometry(data_file=file)
            case 'cv':
                entry = CE_ACMD_CyclicVoltammetry(data_file=file)
            case 'lsv':
                entry = CE_ACMD_LinearSweepVoltammetry(data_file=file)
            case 'gds':
                entry = CE_ACMD_GalvanodynamicSweep(data_file=file)
            case 'geis':
                entry = CE_ACMD_GEIS(data_file=file)
            case 'peis':
                entry = CE_ACMD_PEIS(data_file=file)
            case 'cp':
                entry = CE_ACMD_Chronopotentiometry(data_file=file)

        electrolyser_id = file.split('/')[-1][:8]
        set_sample_reference(archive, entry, electrolyser_id)
        entry.name = file.split('.')[0]
        file_name = f'{file}.archive.json'
        create_archive(entry, archive, file_name, overwrite=True)  # TODO remove overwrite after reprocessing all nesd->acmd uploads

        entry_id = get_entry_id_from_file_name(file_name, archive)
        archive.data = ParsedZahnerFile(
            activity=[get_reference(archive.metadata.upload_id, entry_id)]
        )
        archive.metadata.entry_name = file


class CEACMDCHIParser(MatchingParser):
    def parse(self, mainfile: str, archive: EntryArchive, logger):
        if not mainfile.endswith('.txt') and not mainfile.endswith('.bin'):
            return
        file = mainfile.rsplit('raw/', maxsplit=1)[-1]

        if mainfile.endswith('.txt'):
            with archive.m_context.raw_file(file, 'tr') as f:
                m, _ = parse_chi_txt_file(f.read())
        else:
            with archive.m_context.raw_file(file, 'rb') as f:
                m, _ = parse_metadata_chi_bin_file(f.read())

        technique = m.get('method')
        match technique:
            case 'Chronoamperometry':
                entry = CE_ACMD_Chronoamperometry(data_file=file)
            case 'Cyclic Voltammetry':
                entry = CE_ACMD_CyclicVoltammetry(data_file=file)
            case 'Linear Sweep Voltammetry':
                entry = CE_ACMD_LinearSweepVoltammetry(data_file=file)
            # case 'gds':
            #     entry = CE_ACMD_GalvanodynamicSweep(data_file=file)
            # case 'geis':
            #     entry = CE_ACMD_GEIS(data_file=file)
            case 'A.C. Impedance':
                entry = CE_ACMD_PEIS(data_file=file)
            case 'Chronopotentiometry':
                entry = CE_ACMD_Chronopotentiometry(data_file=file)

        electrolyser_id = file.split('/')[-1][:8]
        set_sample_reference(archive, entry, electrolyser_id)
        entry.name = file.split('.')[0]
        file_name = f'{file}.archive.json'
        create_archive(entry, archive, file_name, overwrite=True)   # TODO remove overwrite after reprocessing all nesd->acmd uploads

        entry_id = get_entry_id_from_file_name(file_name, archive)
        archive.data = ParsedCHIFile(
            activity=[get_reference(archive.metadata.upload_id, entry_id)]
        )
        archive.metadata.entry_name = file


class CEACMDLabviewParser(MatchingParser):
    def parse(self, mainfile: str, archive: EntryArchive, logger):
        file = mainfile.rsplit('raw/', maxsplit=1)[-1]

        if not file.endswith('.tdms'):
            return

        entry = CE_ACMD_ElectrolyserPerformanceEvaluation(data_file=file)
        electrolyser_id = file.split('.')[0][:8]
        set_sample_reference(archive, entry, electrolyser_id)
        entry.datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        entry.name = file.split('.')[0]
        file_name = f'{file}.archive.json'
        create_archive(entry, archive, file_name, overwrite=True)   # TODO remove overwrite after reprocessing all nesd->acmd uploads

        entry_id = get_entry_id_from_file_name(file_name, archive)
        archive.data = ParsedLabVIEWFile(
            activity=[get_reference(archive.metadata.upload_id, entry_id)]
        )
        archive.metadata.entry_name = file


class CEACMDPalmSensParser(MatchingParser):
    def parse(self, mainfile: str, archive: EntryArchive, logger):
        if not mainfile.endswith('.pssession'):
            return
        file = mainfile.rsplit('raw/', maxsplit=1)[-1]
        with archive.m_context.raw_file(file, 'rt', encoding='utf-16') as f:
            data = get_data_from_pssession_file(f.read())

        if len(data['Measurements']) != 1:
            return
        technique = data.get('Measurements', [{}])[0].get('Title', '').split(' [')[0]
        match technique:
            case 'Open Circuit Potentiometry':
                entry = CE_ACMD_OpenCircuitVoltage(data_file=file)
            case 'Chronoamperometry':
                entry = CE_ACMD_Chronoamperometry(data_file=file)
            case 'Cyclic Voltammetry':
                entry = CE_ACMD_CyclicVoltammetry(data_file=file)
            case 'Linear Sweep Voltammetry':
                entry = CE_ACMD_LinearSweepVoltammetry(data_file=file)
            # case 'gds':
            #     entry = CE_ACMD_GalvanodynamicSweep(data_file=file)
            case 'Impedance Spectroscopy' | 'Impedance Spectroscopy [1]':
                entry = CE_ACMD_PEIS(data_file=file)
            case 'Chronopotentiometry':
                entry = CE_ACMD_Chronopotentiometry(data_file=file)

        electrolyser_id = file.split('/')[-1][:8]
        set_sample_reference(archive, entry, electrolyser_id)
        entry.name = file.split('.')[0]
        file_name = f'{file}.archive.json'
        create_archive(entry, archive, file_name, overwrite=True)   # TODO remove overwrite after reprocessing all nesd->acmd uploads

        entry_id = get_entry_id_from_file_name(file_name, archive)
        archive.data = ParsedPalmSensFile(
            activity=[get_reference(archive.metadata.upload_id, entry_id)]
        )
        archive.metadata.entry_name = file


class CEACMDMetadataExcelParser(MatchingParser):
    def to_float_if_possible(self, value):
        if pd.isna(value):
            return None
        try:
            value_str = str(value).replace(',', '.')
            return float(value_str)
        except ValueError:
            return value

    def split_experimental_techniques(self, df, logger):
        markers = {
            '3electrode': 'For 3 Electrode Setup:',
            'RDE': 'For RDE:',
            'AEM_or_PEM': 'For AEM or PEM:',
            'Half-Cell': 'For Half-Cell:',
        }

        field = df['Field'].fillna('').astype(str).str.strip()

        marker_idx = {}

        for name, marker in markers.items():
            matches = field.eq(marker.lower())
            if not matches.any():
                logger.warn(
                    f'Marker not found: {marker}. Please check for newer metadata excel template.'
                )
                # if one of the markers is missing we treat the excel like the old metadata template
                return df, 'old_template', pd.DataFrame(columns=df.columns)
            marker_idx[name] = matches.idxmax()

        technique_names = ['general', *markers.keys()]

        starts = [
            0,
            *(marker_idx[name] + 1 for name in markers),
        ]

        ends = [
            *(marker_idx[name] for name in markers),
            len(df),
        ]

        experimental_techniques = {
            name: df.iloc[start:end]
            for name, start, end in zip(
                technique_names,
                starts,
                ends,
            )
        }

        filled_counts = {
            name: (technique['Value'].fillna('').astype(str).str.strip().ne('').sum())
            for name, technique in experimental_techniques.items()
            if name != 'general'
        }

        non_empty = {name: count for name, count in filled_counts.items() if count > 0}

        if not non_empty:
            active_name = None
            active_df = None
        else:
            active_name = max(non_empty, key=non_empty.get)
            active_df = experimental_techniques[active_name]

            if len(non_empty) > 1:
                logger.warn(
                    f'Multiple experimental techniques contain values: {list(non_empty.keys())}',
                )

        return experimental_techniques['general'], active_name, active_df

    def parse(self, mainfile: str, archive: EntryArchive, logger):
        file = mainfile.rsplit('raw/', maxsplit=1)[-1]

        if not file.endswith('.xlsx'):
            return

        with archive.m_context.raw_file(file, 'rb') as f:
            xls_file = pd.ExcelFile(f)
            excel_data = pd.read_excel(xls_file, sheet_name='ACMD Metadata')
            excel_data['Value'] = excel_data['Value'].apply(self.to_float_if_possible)
            excel_data['Field'] = excel_data['Field'].str.lower().str.strip()
            general_df, setup_type, setup_df = self.split_experimental_techniques(
                excel_data, logger
            )
            mapping_df = pd.concat(
                [general_df, setup_df],
                ignore_index=True,
            ).dropna(subset=['Field'])

        mapping = dict(
            zip(
                mapping_df['Field'],
                mapping_df['Value'],
            )
        )

        folder_path = ('/' + file).rsplit('/', 1)[0]

        sample_entry = CE_ACMD_Sample()
        sample_file_name = f'{file}_sample.archive.json'
        if setup_type in ['3electrode', 'RDE', 'old_template']:
            sample_entry.datetime = datetime.datetime.now().strftime(
                '%Y-%m-%d %H:%M:%S.%f'
            )
            sample_entry.name = f'{folder_path}/sample'[1:]
            map_sample(sample_entry, mapping, setup_type, logger)
        elif setup_type in ['AEM_or_PEM']:
            sample_entry = CE_ACMD_Electrolyser()
            sample_file_name = f'{file}_electrolyser.archive.json'
            sample_entry.name = f'{folder_path}/electrolyser'[1:]
            map_electrolyser(sample_entry, mapping, setup_type, archive, logger)
        elif setup_type == 'Half-Cell':
            sample_entry = get_electrode(mapping, 'half-cell', logger)
            sample_file_name = f'{file}_half_cell.archive.json'
            sample_entry.name = f'{folder_path}/half-cell'[1:]
        create_archive(sample_entry, archive, sample_file_name, overwrite=True)  # TODO remove overwrite after reprocessing all nesd->acmd uploads
        sample_entry_id = get_entry_id_from_file_name(sample_file_name, archive)
        entity_list = [
            get_reference(archive.metadata.upload_id, sample_entry_id),
        ]

        if setup_type in ['3electrode', 'RDE', 'old_template']:
            setup_entry = CE_ACMD_Setup()
            setup_entry.datetime = datetime.datetime.now().strftime(
                '%Y-%m-%d %H:%M:%S.%f'
            )
            setup_entry.name = f'{folder_path}/electrochemical_setup_and_electrolyte'[
                1:
            ]
            map_setup(setup_entry, mapping, setup_type, archive)
            ref_electrode_file_name = f'{file}_reference_electrode.archive.json'
            reference_electrode_entry = get_reference_electrode(mapping)
            create_archive(reference_electrode_entry, archive, ref_electrode_file_name, overwrite=True)  # TODO remove overwrite after reprocessing all nesd->acmd uploads
            ref_electrode_entry_id = get_entry_id_from_file_name(
                ref_electrode_file_name, archive
            )
            setup_entry.reference_electrode = get_reference(
                archive.metadata.upload_id, ref_electrode_entry_id
            )
            setup_file_name = f'{file}_setup.archive.json'
            create_archive(setup_entry, archive, setup_file_name, overwrite=True)  # TODO remove overwrite after reprocessing all nesd->acmd uploads
            setup_entry_id = get_entry_id_from_file_name(setup_file_name, archive)
            entity_list.append(
                get_reference(archive.metadata.upload_id, setup_entry_id)
            )

        archive.data = ParsedMetadataExcelFile(entity=entity_list)
        archive.metadata.entry_name = file

        if mapping.get('reaction type') == 'OER':
            analysis_name = f'{folder_path}/oer_analysis'[1:]
            analysis_file_name = f'{analysis_name}.archive.json'
            create_archive(CE_ACMD_OERAnalysis(name=analysis_name), archive, analysis_file_name, overwrite=True)  # TODO remove overwrite after reprocessing all nesd->acmd uploads
