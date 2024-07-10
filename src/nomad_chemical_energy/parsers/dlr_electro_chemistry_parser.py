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

from nomad.datamodel.metainfo.basesections import CompositeSystemReference
from nomad.datamodel import EntryArchive
from nomad.parsing import MatchingParser
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
)
from nomad.datamodel.data import (
    EntryData,
)
from nomad.metainfo import (
    Quantity,
)
from nomad.datamodel.metainfo.basesections import (
    Activity, CompositeSystemReference,
)
import os
import datetime

from baseclasses.helper.utilities import (find_sample_by_id, create_archive, get_entry_id_from_file_name, get_reference,
                                          search_class, set_sample_reference)

from nomad_chemical_energy.schema_packages.dlr_electro_chemistry_package import \
    (DLR_Chronopotentiometry, DLR_CyclicVoltammetry, DLR_ElectrochemicalImpedanceSpectroscopy)


'''
This is a hello world style example for an example parser/converter.
'''


class ParsedDLRECFile(EntryData):
    activity = Quantity(
        type=Activity,
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
        )
    )


def create_ec_entry(archive, mainfile, entry):
    mainfile_split = os.path.basename(mainfile).split('.')
    notes = ''
    if len(mainfile_split) > 2:
        notes = mainfile_split[1]
    archive.metadata.entry_name = os.path.basename(mainfile)

    search_id = mainfile_split[0]
    set_sample_reference(archive, entry, search_id)

    entry.name = f"{search_id} {notes}"
    entry.description = f"Notes from file name: {notes}"

    entry.data_file = os.path.basename(mainfile)
    entry.datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

    file_name = f'{os.path.basename(mainfile)}.archive.json'
    eid = get_entry_id_from_file_name(file_name, archive)
    archive.data = ParsedDLRECFile(activity=get_reference(archive.metadata.upload_id, eid))
    create_archive(entry, archive, file_name)


class DLRECCVParser(MatchingParser):

    def parse(self, mainfile: str, archive: EntryArchive, logger):
        # Log a hello world, just to get us started. TODO remove from an actual parser.
        entry = DLR_CyclicVoltammetry()
        create_ec_entry(archive, mainfile, entry)


class DLRECEISParser(MatchingParser):

    def parse(self, mainfile: str, archive: EntryArchive, logger):
        # Log a hello world, just to get us started. TODO remove from an actual parser.

        entry = DLR_ElectrochemicalImpedanceSpectroscopy()
        create_ec_entry(archive, mainfile, entry)


class DLRECCPParser(MatchingParser):

    def parse(self, mainfile: str, archive: EntryArchive, logger):
        # Log a hello world, just to get us started. TODO remove from an actual parser.
        entry = DLR_Chronopotentiometry()
        create_ec_entry(archive, mainfile, entry)
