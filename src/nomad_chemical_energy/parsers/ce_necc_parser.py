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

import pandas as pd
import datetime

from nomad.datamodel import EntryArchive
from nomad.metainfo import (
    Quantity,
)
from nomad.parsing import MatchingParser
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
)
from nomad.datamodel.data import (
    EntryData,
)

from nomad.datamodel.metainfo.basesections import (
    Activity,
)

from baseclasses.helper.utilities import (create_archive, get_entry_id_from_file_name,
                                          get_reference, set_sample_reference)

from nomad_chemical_energy.schema_packages.ce_necc_package import (CE_NECC_EC_GC)


class ParsedExcelFile(EntryData):
    activity = Quantity(
        type=Activity,
        shape=['*'],
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
        )
    )


class NECCXlsxParser(MatchingParser):

    def parse(self, mainfile: str, archive: EntryArchive, logger) -> None:
        entry = None
        file = mainfile.split('/')[-1]

        if not file.endswith(".xlsx"):
            return

        xls_file = pd.ExcelFile(mainfile)
        num_sheets = len(xls_file.sheet_names)
        if num_sheets != 4:
            return
        entry = CE_NECC_EC_GC(data_file=file)

        search_id = file.split("#")[0]
        set_sample_reference(archive, entry, search_id)
        entry.datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        entry.name = f"{search_id}"
        file_name = f'{file}.archive.json'
        create_archive(entry, archive, file_name)

        entry_id = get_entry_id_from_file_name(file_name, archive)
        archive.data = ParsedExcelFile(activity=[get_reference(archive.metadata.upload_id, entry_id)])
        archive.metadata.entry_name = file
