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

from nomad.datamodel import EntryArchive
from nomad.metainfo import (
    Quantity,
)
from nomad.parsing import MatchingParser
from nomad.datamodel.data import (
    EntryData,
)

from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
)

from nomad.datamodel.metainfo.basesections import (
    Activity,
)

from baseclasses.helper.utilities import (create_archive, get_entry_id_from_file_name,
                                          get_reference, set_sample_reference)

from nomad_chemical_energy.schema_packages.hzb_general_measurement_package import (HZB_GeneralMeasurement)


class ParsedGeneralMeasurementFile(EntryData):

    activity = Quantity(
        type=Activity,
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
        )
    )


class GeneralMeasurementParser(MatchingParser):

    def parse(self, mainfile: str, archive: EntryArchive, logger) -> None:

        file_name = mainfile.split('/')[-1]
        sample_id = file_name.split(".")[0].split("-")[0]

        entry = HZB_GeneralMeasurement()
        entry.name = file_name
        entry.data_file = file_name

        archive.metadata.entry_name = file_name
        set_sample_reference(archive, entry, sample_id)
        file_name_archive = f'{file_name}.archive.json'
        create_archive(entry, archive, file_name_archive)

        eid = get_entry_id_from_file_name(file_name_archive, archive)
        ref = get_reference(archive.metadata.upload_id, eid)
        archive.data = ParsedGeneralMeasurementFile(activity=ref)
        archive.metadata.entry_name = file_name.split(".")[0].replace("-", " ")

