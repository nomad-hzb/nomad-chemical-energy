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
)
from nomad.metainfo import (
    Quantity,
)
from nomad.parsing import MatchingParser

from nomad_chemical_energy.parsers.ce_nesd_parser import ParsedBioLogicFile
from nomad_chemical_energy.schema_packages.ce_necc_package import (
    CE_NECC_EC_GC,
    CE_NECC_GEIS,
    CE_NECC_PEIS,
    CE_NECC_Chronoamperometry,
    CE_NECC_Chronopotentiometry,
    CE_NECC_ConstantCurrentMode,
    CE_NECC_ConstantVoltageMode,
    CE_NECC_CyclicVoltammetry,
    CE_NECC_LinearSweepVoltammetry,
    CE_NECC_Measurement,
    CE_NECC_OpenCircuitVoltage,
)
from nomad_chemical_energy.schema_packages.file_parser.biologic_parser import (
    get_header_and_data,
)


class ParsedExcelFile(EntryData):
    activity = Quantity(
        type=Activity,
        shape=['*'],
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
        ),
    )


class NECCXlsxParser(MatchingParser):
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
        excel_sheets = pd.ExcelFile(filename).sheet_names
        required_sheets_v1 = [
            'Catalyst details',
            'Experimental details',
            'Raw Data',
            'Results',
        ]
        required_sheets_v2 = [
            'Experimental Details',
            'Time_Calc',
            'FID Data',
            'TCD Data',
            'Pot Data',
            'Thermo Data',
            'GC Calc',
            'Results',
        ]
        is_v1_excel = all(sheet in excel_sheets for sheet in required_sheets_v1)
        is_v2_excel = all(sheet in excel_sheets for sheet in required_sheets_v2)
        return is_v1_excel or is_v2_excel

    def parse(self, mainfile: str, archive: EntryArchive, logger) -> None:
        file = mainfile.rsplit('/', maxsplit=1)[-1]
        if not file.endswith('.xlsx'):
            return

        xls_file = pd.ExcelFile(mainfile)
        num_sheets = len(xls_file.sheet_names)
        if num_sheets not in (4, 5, 8):
            return
        entry = CE_NECC_EC_GC(data_file=file)

        search_id = file.split('#')[0]
        set_sample_reference(archive, entry, search_id)
        entry.datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        entry.name = f'{search_id}'
        file_name = f'{file}.archive.json'
        create_archive(entry, archive, file_name)

        entry_id = get_entry_id_from_file_name(file_name, archive)
        archive.data = ParsedExcelFile(
            activity=[get_reference(archive.metadata.upload_id, entry_id)]
        )
        archive.metadata.entry_name = file


class CENECCBioLogicParser(MatchingParser):
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
        if device_number in ['0694', '1284', '1285']:
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
                entry = CE_NECC_Chronoamperometry(data_file=file)
            case 'coC':
                entry = CE_NECC_ConstantCurrentMode(data_file=file)
            case 'coV':
                entry = CE_NECC_ConstantVoltageMode(data_file=file)
            case 'CP':
                entry = CE_NECC_Chronopotentiometry(data_file=file)
            case 'CV':
                entry = CE_NECC_CyclicVoltammetry(data_file=file)
            case 'GEIS':
                entry = CE_NECC_GEIS(data_file=file)
            case 'LSV':
                entry = CE_NECC_LinearSweepVoltammetry(data_file=file)
            case 'OCV':
                entry = CE_NECC_OpenCircuitVoltage(data_file=file)
            case 'PEIS':
                entry = CE_NECC_PEIS(data_file=file)
            case _:
                entry = CE_NECC_Measurement(data_file=file)

        entry.datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        entry.name = file.split('.')[0]
        file_name = f'{file}.archive.json'
        create_archive(entry, archive, file_name)

        entry_id = get_entry_id_from_file_name(file_name, archive)
        archive.data = ParsedBioLogicFile(
            activity=[get_reference(archive.metadata.upload_id, entry_id)]
        )
        archive.metadata.entry_name = file
