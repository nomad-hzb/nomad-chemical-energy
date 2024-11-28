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

from nomad_chemical_energy.schema_packages.hzb_general_process_package import (
    HZB_GeneralProcess,
)


class ParsedGeneralProcessFile(EntryData):
    activity = Quantity(
        type=Activity,
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
        ),
    )


class GeneralProcessParser(MatchingParser):
    def parse(self, mainfile: str, archive: EntryArchive, logger) -> None:
        file_name = mainfile.split('/')[-1]
        sample_id = file_name.split('.')[0].split('-')[0]

        entry = HZB_GeneralProcess()
        entry.name = file_name
        entry.data_file = file_name

        archive.metadata.entry_name = file_name
        set_sample_reference(archive, entry, sample_id, archive.metadata.upload_id)
        file_name_archive = f'{file_name}.archive.json'
        create_archive(entry, archive, file_name_archive)

        eid = get_entry_id_from_file_name(file_name_archive, archive)
        ref = get_reference(archive.metadata.upload_id, eid)
        archive.data = ParsedGeneralProcessFile(activity=ref)
        archive.metadata.entry_name = file_name.split('.')[0].replace('-', ' ')

        # TODO for new measurement parsers that should replace GeneralProcess entries you can use this code inside the parser
        # file_name_archive = f'{file_name}.archive.json'
        # new_entry_created = create_archive(entry, archive, file_name_archive)
        # eid = get_entry_id_from_file_name(file_name_archive, archive)
        # ref = get_reference(archive.metadata.upload_id, eid)
        # if not new_entry_created:
        #     new_entry = update_general_process_entries(entry, eid, archive, logger, TxtMeasurement())
        #     if new_entry is not None:
        #         create_archive(new_entry, archive, file_name_archive, overwrite=True)
        # archive.data = ParsedTxtFile(activity=ref)
        # archive.metadata.entry_name = file_name.split(".")[0].replace("-", " ")


def update_general_process_entries(entry, entry_id, archive, logger, entry_class):
    from nomad import files
    from nomad.search import search

    query = {
        'entry_id': entry_id,
    }
    search_result = search(
        owner='all', query=query, user_id=archive.metadata.main_author.user_id
    )
    entry_type = (
        search_result.data[0].get('entry_type')
        if len(search_result.data) == 1
        else None
    )
    if entry_type != 'HZB_GeneralProcess':
        return None
    new_entry_dict = entry.m_to_dict()
    res = search_result.data[0]
    try:
        # Open Archives
        with files.UploadFiles.get(upload_id=res['upload_id']).read_archive(
            entry_id=res['entry_id']
        ) as archive:
            entry_id = res['entry_id']
            entry_data = archive[entry_id]['data']
            entry_data.pop('m_def', None)
            new_entry_dict.update(entry_data)
    except Exception as e:
        logger.error('Error in processing data: ', e)

    new_entry = entry_class.m_from_dict(new_entry_dict)
    return new_entry
