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

from nomad_chemical_energy.schema_packages.ce_nome_package import \
    (CE_NOME_Chronoamperometry, CE_NOME_CyclicVoltammetry, CE_NOME_Chronopotentiometry,
     CE_NOME_Chronocoulometry, CE_NOME_ElectrochemicalImpedanceSpectroscopy,
     CE_NOME_LinearSweepVoltammetry, CE_NOME_Measurement, CE_NOME_OpenCircuitVoltage,
     CE_NOME_PhaseFluorometryOxygen, CE_NOME_PumpRateMeasurement, CE_NOME_UVvismeasurement,
     Bessy2_KMC2_XASTransmission, Bessy2_KMC2_XASFluorescence, CE_NOME_GalvanodynamicSweep)


'''
This is a hello world style example for an example parser/converter.
'''


class ParsedGamryFile(EntryData):
    activity = Quantity(
        type=Activity,
        shape=["*"],
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
        )
    )


class ParsedKMC2File(EntryData):
    activity = Quantity(
        type=Activity,
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
        )
    )


class GamryParser(MatchingParser):

    def parse(self, mainfile: str, archive: EntryArchive, logger):
        # Log a hello world, just to get us started. TODO remove from an actual
        # parser.
        from nomad_chemical_energy.schema_packages.file_parser.gamry_parser import get_header_and_data
        metadata, _ = get_header_and_data(filename=mainfile)

        measurement_base, measurement_name = os.path.split(mainfile)

        measurements = []
        connected_experiments = []
        # if "COLLECT" in metadata["TAG"] or ("CV" in metadata["TAG"] and "WE2CURVE" in metadata):
        if "METHOD" in metadata:
            methods = metadata.get("METHOD").split("-")
        else:
            methods = [metadata.get("TAG")]

        for method in methods:
            file_name = f"{measurement_name}_{method}.archive.json"
            eid = get_entry_id_from_file_name(file_name, archive)
            connected_experiments.append(get_reference(archive.metadata.upload_id, eid))
            if "CV" in method:
                measurements.append(
                    (eid, file_name, CE_NOME_CyclicVoltammetry()))

            if "LSV" in method:
                measurements.append(
                    (eid, file_name, CE_NOME_LinearSweepVoltammetry()))

            if "LSG" in method:
                measurements.append(
                    (eid, file_name, CE_NOME_GalvanodynamicSweep()))

            if "CHRONOA" in method or "CA" in method:
                measurements.append(
                    (eid, file_name, CE_NOME_Chronoamperometry()))

            if "CHRONOP" in method or "CP" in method:
                measurements.append(
                    (eid, file_name, CE_NOME_Chronopotentiometry()))

            if "CHRONOC" in method or "CC" in method:
                measurements.append((eid, file_name, CE_NOME_Chronocoulometry()))

            if "CORPOT" in method:
                measurements.append(
                    (eid, file_name, CE_NOME_OpenCircuitVoltage()))

            if "EISPOT" in method or "PEIS" in method:
                measurements.append(
                    (eid, file_name, CE_NOME_ElectrochemicalImpedanceSpectroscopy()))

        archive.metadata.entry_name = os.path.basename(mainfile)
        nickname = metadata.get("NICK")
        sample_id = metadata.get("SAMPLEID")
        setup_id = metadata.get("ECSETUPID")
        environment_id = metadata.get("ENVIRONMENTID")
        sample_ref = find_sample_by_id(archive, sample_id)
        environment_ref = find_sample_by_id(archive, environment_id)
        setup_ref = find_sample_by_id(archive, setup_id)

        if sample_ref is None:
            sample = search_class(archive, "CE_NOME_Sample")
            if sample is not None:
                upload_id, entry_id = sample["upload_id"], sample["entry_id"]
                sample_ref = get_reference(upload_id, entry_id)

        if environment_ref is None:
            environment = search_class(archive, "CE_NOME_Environment")
            if environment is not None:
                upload_id, entry_id = environment["upload_id"], environment["entry_id"]
                environment_ref = get_reference(upload_id, entry_id)

        if setup_ref is None:
            setup = search_class(archive, "CE_NOME_ElectroChemicalSetup")
            if setup is not None:
                upload_id, entry_id = setup["upload_id"], setup["entry_id"]
                setup_ref = get_reference(upload_id, entry_id)

        refs = []
        for idx, (eid, name, measurement) in enumerate(measurements):
            measurement.name = nickname
            measurement.data_file = measurement_name
            measurement.connected_experiments = [c for c in connected_experiments if eid not in c]
            measurement.function = "Generator"
            if idx > 0:
                measurement.function = "Detector"
            if sample_ref is not None:
                measurement.samples = [CompositeSystemReference(reference=sample_ref)]
            if environment_ref is not None:
                measurement.environment = environment_ref
            if setup_ref is not None:
                measurement.setup = setup_ref
            name = name.replace("#", "run")
            create_archive(measurement, archive, name)
            refs.append(get_reference(archive.metadata.upload_id, eid))

        archive.data = ParsedGamryFile(activity=refs)
        archive.metadata.entry_name = measurement_name


class CENOMEcsvParser(MatchingParser):

    def parse(self, mainfile: str, archive: EntryArchive, logger):
        # Log a hello world, just to get us started. TODO remove from an actual parser.

        mainfile_split = os.path.basename(mainfile).split('.')
        notes = ''
        if len(mainfile_split) > 2:
            notes = mainfile_split[1]
        entry = CE_NOME_Measurement()
        if mainfile_split[-1].endswith("csv"):
            with open(mainfile) as f:
                first_line = f.readline()
            if first_line.startswith("Time;Push Pull"):
                entry = CE_NOME_PumpRateMeasurement()

            if first_line.startswith("1.5.1.23"):
                entry = CE_NOME_PhaseFluorometryOxygen()
        elif mainfile_split[-1].endswith("xlsx"):
            entry = CE_NOME_PhaseFluorometryOxygen()

        archive.metadata.entry_name = os.path.basename(mainfile)
        sample = search_class(archive, "CE_NOME_Sample")
        if sample is not None:
            upload_id, entry_id = sample["upload_id"], sample["entry_id"]
            entry.samples = [CompositeSystemReference(reference=get_reference(upload_id, entry_id))]

        environment = search_class(archive, "CE_NOME_Environment")
        if environment is not None:
            upload_id, entry_id = environment["upload_id"], environment["entry_id"]
            entry.environment = get_reference(upload_id, entry_id)

        setup = search_class(archive, "CE_NOME_ElectroChemicalSetup")
        if setup is not None:
            upload_id, entry_id = setup["upload_id"], setup["entry_id"]
            entry.setup = get_reference(upload_id, entry_id)

        entry.name = f"{mainfile_split[0]} {notes}"
        entry.description = f"Notes from file name: {notes}"
        try:
            entry.data_file = os.path.basename(mainfile)
        except:
            entry.data_file = [os.path.basename(mainfile)]
        entry.datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

        file_name = f'{os.path.basename(mainfile)}.archive.json'
        create_archive(entry, archive, file_name)


class UVvisParser(MatchingParser):

    def parse(self, mainfile: str, archive: EntryArchive, logger):
        # Log a hello world, just to get us started. TODO remove from an actual parser.

        from baseclasses.helper.utilities import get_encoding
        with open(mainfile, "br") as f:
            encoding = get_encoding(f)

        mainfile_split = os.path.basename(mainfile).split('.')
        notes = ''
        if len(mainfile_split) > 2:
            notes = mainfile_split[1]

        uvvis = CE_NOME_UVvismeasurement()

        sample_id = mainfile_split[0]
        set_sample_reference(archive, uvvis, sample_id)
        # archive.metadata.entry_name = os.path.basename(mainfile)
        # sample = search_class(archive, "CE_NOME_Sample")
        # if sample is not None:
        #     upload_id, entry_id = sample["upload_id"], sample["entry_id"]
        #     uvvis.samples = [CompositeSystemReference(reference=get_reference(upload_id, entry_id))]
        uvvis.name = f"{mainfile_split[0]} {notes}"
        uvvis.description = f"Notes from file name: {notes}"
        uvvis.data_file = [os.path.basename(mainfile)]
        uvvis.datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

        file_name = f'{os.path.basename(mainfile)}.archive.json'
        create_archive(uvvis, archive, file_name)


class XASParser(MatchingParser):

    def parse(self, mainfile: str, archive: EntryArchive, logger):
        # Log a hello world, just to get us started. TODO remove from an actual
        # parser.

        measurement_base, measurement_name = os.path.split(mainfile)
        archive.metadata.entry_name = measurement_name

        if "tm" in measurement_name:
            xas_measurement = Bessy2_KMC2_XASTransmission()
        else:
            xas_measurement = Bessy2_KMC2_XASFluorescence()

        xas_measurement.data_file = measurement_name
        xas_measurement.name = measurement_name

        sample_id = measurement_name.split(".")[0]
        sample_ref = find_sample_by_id(archive, sample_id)
        if sample_ref is not None:
            xas_measurement.samples = [CompositeSystemReference(reference=sample_ref)]

        if not xas_measurement.samples:
            sample = search_class(archive, "CE_NOME_Sample")
            if sample is not None:
                upload_id, entry_id = sample["upload_id"], sample["entry_id"]
                xas_measurement.samples = [CompositeSystemReference(reference=get_reference(upload_id, entry_id))]

        # archive.data = cam_measurements
        if xas_measurement is not None:
            file_name = f'{measurement_name}.archive.json'
            create_archive(xas_measurement, archive, file_name)
            archive.data = ParsedKMC2File(activity=get_reference(
                archive.metadata.upload_id,
                get_entry_id_from_file_name(file_name, archive)
            ))
            archive.metadata.entry_name = measurement_name
