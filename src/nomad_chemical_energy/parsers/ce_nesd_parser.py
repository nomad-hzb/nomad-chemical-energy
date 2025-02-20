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

from nomad_chemical_energy.schema_packages.ce_nesd_package import (
    CE_NESD_GEIS,
    CE_NESD_PEIS,
    CE_NESD_Chronoamperometry,
    CE_NESD_Chronopotentiometry,
    CE_NESD_ConstantCurrentMode,
    CE_NESD_ConstantVoltageMode,
    CE_NESD_CyclicVoltammetry,
    CE_NESD_ElectrolyserPerformanceEvaluation,
    CE_NESD_LinearSweepVoltammetry,
    CE_NESD_Measurement,
    CE_NESD_OpenCircuitVoltage,
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
        if device_number == '1581':
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
        pass
