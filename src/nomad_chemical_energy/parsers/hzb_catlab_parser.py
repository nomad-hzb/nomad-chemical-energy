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
)
from nomad.datamodel import EntryArchive
from nomad.datamodel.data import (
    EntryData,
)
from nomad.datamodel.metainfo.basesections import (
    CompositeSystem,
    CompositeSystemReference,
)
from nomad.metainfo import (
    Quantity,
)
from nomad.parsing import MatchingParser

from nomad_chemical_energy.schema_packages.hzb_catlab_package import CatLab_Sample


def find_sample_by_id(archive, sample_id):
    from nomad.search import search

    if sample_id is None:
        return None

    query = {'results.eln.lab_ids': sample_id, 'upload_id': archive.metadata.upload_id}

    search_result = search(
        owner='all', query=query, user_id=archive.metadata.main_author.user_id
    )
    if len(search_result.data) > 0:
        entry_id = search_result.data[0]['entry_id']
        upload_id = search_result.data[0]['upload_id']
        return get_reference(upload_id, entry_id)


class ParsedCatlabFile(EntryData):
    # activity = Quantity(
    #     type=Activity,
    # )

    sample = Quantity(
        type=CompositeSystem,
    )

    lab_id = Quantity(type=str)


def search_samples_in_upload(archive):
    from nomad.search import search

    query = {'entry_type': 'CatLab_Sample', 'upload_id': archive.metadata.upload_id}
    search_result = search(
        owner='all', query=query, user_id=archive.metadata.main_author.user_id
    )
    return search_result


class CatlabParser(MatchingParser):
    def parse(self, mainfile: str, archive: EntryArchive, logger) -> None:
        file = mainfile.split('/')[-1]

        sample_id = file.split('#')[0]
        results = search_samples_in_upload(archive)
        parent = None
        exist = False
        for r in results.data:
            print(r)
            if r['data'].get('lab_id') == sample_id:
                exist = True
            if r['data'].get('lab_id') == '_'.join(sample_id.split('_')[:-1]):
                parent = r['data']['lab_id']

        file_name = f'{sample_id}.archive.json'
        if not exist:
            entry = CatLab_Sample(
                lab_id=sample_id,
                name=sample_id,
                parent=CompositeSystemReference(
                    name=parent,
                    reference=find_sample_by_id(archive, parent),
                    lab_id=parent,
                ),
            )
            create_archive(entry, archive, file_name)

        entry_id = get_entry_id_from_file_name(file_name, archive)
        archive.data = ParsedCatlabFile(
            lab_id=sample_id, sample=get_reference(archive.metadata.upload_id, entry_id)
        )
        archive.metadata.entry_name = file.split('.')[0].replace('#', ' ')
