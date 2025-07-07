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

from nomad_chemical_energy.schema_packages.ce_amcc_package import (
    CE_AMCC_GEIS,
    CE_AMCC_PEIS,
    CE_AMCC_Chronoamperometry,
    CE_AMCC_Chronopotentiometry,
    CE_AMCC_ConstantCurrentMode,
    CE_AMCC_ConstantVoltageMode,
    CE_AMCC_CyclicVoltammetry,
    CE_AMCC_LinearSweepVoltammetry,
    CE_AMCC_Measurement,
    CE_AMCC_OpenCircuitVoltage,
    CE_AMCC_ZIR,
)
from nomad_chemical_energy.schema_packages.file_parser.biologic_parser import (
    get_header_and_data,
)


class ParsedBioLogicFile(EntryData):
    activity = Quantity(
        type=Activity,
        shape=['*'],
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
        ),
    )



class CEAMCCBioLogicParser(MatchingParser):
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
        if device_number in ['0315']:
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
                entry = CE_AMCC_Chronoamperometry(data_file=file)
            case 'coC':
                entry = CE_AMCC_ConstantCurrentMode(data_file=file)
            case 'coV':
                entry = CE_AMCC_ConstantVoltageMode(data_file=file)
            case 'CP':
                entry = CE_AMCC_Chronopotentiometry(data_file=file)
            case 'CV':
                entry = CE_AMCC_CyclicVoltammetry(data_file=file)
            case 'GEIS':
                entry = CE_AMCC_GEIS(data_file=file)
            case 'LSV':
                entry = CE_AMCC_LinearSweepVoltammetry(data_file=file)
            case 'OCV':
                entry = CE_AMCC_OpenCircuitVoltage(data_file=file)
            case 'PEIS':
                entry = CE_AMCC_PEIS(data_file=file)
            case 'ZIR':
                entry = CE_AMCC_ZIR(data_file=file)
            case _:
                entry = CE_AMCC_Measurement(data_file=file)

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

