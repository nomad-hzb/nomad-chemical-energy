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
import os

from baseclasses.helper.utilities import (
    create_archive,
    find_sample_by_id,
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
    CompositeSystemReference,
)
from nomad.metainfo import (
    Quantity,
)
from nomad.parsing import MatchingParser

from nomad_chemical_energy.schema_packages.ce_wannsee_package import Wannsee_XRD_XY

'''
This is a hello world style example for an example parser/converter.
'''


class ParsedMPTFile(EntryData):
    activity = Quantity(
        type=Activity,
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
        )
    )


class ParsedXYFile(EntryData):
    activity = Quantity(
        type=Activity,
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
        )
    )


class ParsedCORFile(EntryData):
    activity = Quantity(
        type=Activity,
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
        )
    )


class MPTParser(MatchingParser):

    def parse(self, mainfile: str, archive: EntryArchive, logger):

        mainfile_split = os.path.basename(mainfile).split('.')
        notes = mainfile_split[0]
        if len(mainfile_split) > 2:
            notes = mainfile_split[1]
        cam_measurements = None

        from nomad_chemical_energy.schema_packages.file_parser.mps_file_parser import (
            read_mpt_file,
        )
        metadata, _, technique = read_mpt_file(mainfile)

        if "Cyclic Voltammetry" in technique:
            from nomad_chemical_energy.schema_packages.ce_wannsee_package import (
                Wannsee_B307_CyclicVoltammetry_ECLab,
            )
            cam_measurements = Wannsee_B307_CyclicVoltammetry_ECLab()

        if "Open Circuit Voltage" in technique:
            from nomad_chemical_energy.schema_packages.ce_wannsee_package import (
                Wannsee_B307_OpenCircuitVoltage_ECLab,
            )
            cam_measurements = Wannsee_B307_OpenCircuitVoltage_ECLab()

        if "Potentio Electrochemical Impedance Spectroscopy" in technique:
            from nomad_chemical_energy.schema_packages.ce_wannsee_package import (
                Wannsee_B307_ElectrochemicalImpedanceSpectroscopy_ECLab,
            )
            cam_measurements = Wannsee_B307_ElectrochemicalImpedanceSpectroscopy_ECLab()

        archive.metadata.entry_name = os.path.basename(mainfile)

        sample_id = metadata.get("Electrode material")
        setup_id = metadata.get("Initial state")
        environment_id = metadata.get("Electrolyte")

        from baseclasses.chemical_energy import PotentiostatSetup
        setup_parameters = PotentiostatSetup()
        setup_params = metadata.get("Comments")
        if setup_params is not None:
            setup_params = setup_params.split(",")
            for param in setup_params:
                if "=" not in param:
                    continue
                try:
                    key, value = param.split("=")
                    setattr(setup_parameters, key.strip(), value.strip())
                except:
                    pass

        cam_measurements.setup_parameters = setup_parameters
        sample_ref = find_sample_by_id(archive, sample_id)
        if sample_ref is not None:
            cam_measurements.samples = [CompositeSystemReference(reference=sample_ref)]
        environment_ref = find_sample_by_id(archive, environment_id)
        if environment_ref is not None:
            cam_measurements.environment = environment_ref
        setup_ref = find_sample_by_id(archive, setup_id)
        if setup_ref is not None:
            cam_measurements.setup = setup_ref

        cam_measurements.name = f"{mainfile_split[0]} {notes}"
        cam_measurements.description = f"Notes from file name: {notes}"
        cam_measurements.data_file = os.path.basename(mainfile)

        if cam_measurements is not None:
            file_name = f'{os.path.basename(mainfile)}.archive.json'
            create_archive(cam_measurements, archive, file_name)

            eid = get_entry_id_from_file_name(file_name, archive)
            ref = get_reference(archive.metadata.upload_id, eid)
            archive.data = ParsedMPTFile(activity=ref)
            archive.metadata.entry_name = f"{mainfile_split[0]} {notes}"


class CORParser(MatchingParser):

    def parse(self, mainfile: str, archive: EntryArchive, logger):

        mainfile_split = os.path.basename(mainfile).split('.')
        notes = mainfile_split[0]
        if len(mainfile_split) > 2:
            notes = mainfile_split[1]

        from nomad_chemical_energy.schema_packages.ce_wannsee_package import (
            Wannsee_B307_CyclicVoltammetry_CorrWare,
        )
        cam_measurements = Wannsee_B307_CyclicVoltammetry_CorrWare()

        archive.metadata.entry_name = os.path.basename(mainfile)

        search_id = mainfile_split[0]
        set_sample_reference(archive, cam_measurements, search_id)

        cam_measurements.name = f"{search_id} {notes}"
        cam_measurements.description = f"Notes from file name: {notes}"
        cam_measurements.data_file = os.path.basename(mainfile)

        file_name = f'{os.path.basename(mainfile)}.archive.json'
        create_archive(cam_measurements, archive, file_name)

        eid = get_entry_id_from_file_name(file_name, archive)
        ref = get_reference(archive.metadata.upload_id, eid)
        archive.data = ParsedCORFile(activity=ref)
        archive.metadata.entry_name = f"{mainfile_split[0]} {notes}"


class XRDParser(MatchingParser):

    def parse(self, mainfile: str, archive: EntryArchive, logger):
        # Log a hello world, just to get us started. TODO remove from an actual parser.

        mainfile_split = os.path.basename(mainfile).split('.')
        notes = ''
        if len(mainfile_split) > 2:
            notes = mainfile_split[1]
        entry = Wannsee_XRD_XY()

        archive.metadata.entry_name = os.path.basename(mainfile)
        search_id = mainfile_split[0]
        set_sample_reference(archive, entry, search_id)

        entry.name = f"{search_id} {notes}"
        entry.description = f"Notes from file name: {notes}"
        if not mainfile_split[-2] == "eqe":
            entry.data_file = os.path.basename(mainfile)
        entry.datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

        file_name = f'{os.path.basename(mainfile)}.archive.json'
        create_archive(entry, archive, file_name)

        eid = get_entry_id_from_file_name(file_name, archive)
        ref = get_reference(archive.metadata.upload_id, eid)
        archive.data = ParsedXYFile(activity=ref)
        archive.metadata.entry_name = f"{mainfile_split[0]} {notes}"
