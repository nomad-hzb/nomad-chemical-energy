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

import numpy as np
from baseclasses import SingleSampleExperiment, BaseMeasurement
from baseclasses.catalysis import (
    CatalysisLibrary, CatalysisSample
)
from baseclasses.helper.utilities import create_archive, rewrite_json, get_entry_id_from_file_name, get_reference
from baseclasses.vapour_based_deposition import (
    MultiTargetSputtering, SputteringProcess, PECVDeposition, PECVDProcess

)
from nomad_chemical_energy.schema_packages.hzb_characterization_package import (
    HZB_SEM_Merlin, HZB_TGA, HZB_XPS, HZB_XRD, HZB_XRR, HZB_XRF, HZB_Ellipsometry,
    HZB_XRD_Library, HZB_XPS_Library, HZB_XRR_Library, HZB_XRF_Library, HZB_Ellipsometry_Library
)

from nomad.datamodel.data import EntryData
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
)
from nomad.datamodel.metainfo.basesections import (
    CompositeSystemReference
)
from nomad.datamodel.metainfo.basesections import PubChemPureSubstanceSection
# from nomad.units import ureg
from nomad.metainfo import (
    Section, SubSection, Quantity, SchemaPackage)
from nomad_measurements.catalytic_measurement.catalytic_measurement import ReactionConditions

m_package = SchemaPackage()


class CatLab_Sample(CatalysisSample, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=["users", "elemental_composition", "components"],
            properties=dict(
                order=[
                    "name",
                    "lab_id",
                ])))


class CatLab_Library(CatalysisLibrary, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=["users", "elemental_composition", "components"],
            properties=dict(
                order=[
                    "name",
                    "lab_id",
                ])))


class CatLab_Sputtering(MultiTargetSputtering, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=["users", "elemental_composition", "components", "present",
                  "instruments", "steps", "end_time", "batch", "lab_id"],
            properties=dict(
                order=[
                    "name",
                    "lab_id",
                ])))


class Catlab_SimpleCatalyticReaction(BaseMeasurement, EntryData):
    '''
    Example section for a simple catalytic reaction.
    '''
    m_def = Section(
        label='Simple Catalytic Measurement for Catlab',
        a_eln=dict(
            hide=["steps", "instruments", "results", "lab_id"]))

    data_file = Quantity(
        type=str,
        shape=["*"],
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))

    reaction = SubSection(section_def=ReactionConditions, a_eln=ELNAnnotation(label='Reaction Data'))


class CatLab_PECVD(PECVDeposition, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=["users", "elemental_composition", "components", "present",
                  "lab_id", "end_time", "batch", "instruments", "steps"],
            properties=dict(
                order=[
                    "name",
                ])))

    def normalize(self, archive, logger):
        process = PECVDProcess()
        if self.process is not None:
            process = self.process
        if self.recipe is not None and os.path.splitext(self.recipe)[
                1] == ".set":
            from baseclasses.helper.file_parser.parse_files_pecvd_pvcomb import parse_recipe
            with archive.m_context.raw_file(self.recipe) as f:
                parse_recipe(f, process)

        if self.logs is not None:
            logs = []
            for log in self.logs:
                if os.path.splitext(log)[1] == ".log":
                    from baseclasses.helper.file_parser.parse_files_pecvd_pvcomb import parse_log
                    with archive.m_context.raw_file(log) as f:
                        if process.time:
                            data = parse_log(
                                f,
                                process,
                                np.int64(0.9 * process.time),
                                np.int64(0.05 * process.time))
                        else:
                            data = parse_log(f, process)
                        data.name = log
                        logs.append(data)
            process.log_data = logs
        self.process = process

        super(CatLab_PECVD, self).normalize(archive, logger)


def create_step(archive, step_idx, step, sample_id):
    file_name = f"{step_idx}_{sample_id}_{step.method}_{step.method_type}.archive.json"
    entity = None
    if step.method_type == "Single":
        if step.method == "XRR":
            entity = HZB_XRR()
        if step.method == "XRD":
            entity = HZB_XRD()
        if step.method == "XRF":
            entity = HZB_XRF()
        if step.method == "XPS":
            entity = HZB_XPS()
        if step.method == "TGA":
            entity = HZB_TGA()
        if step.method == "Ellipsometry":
            entity = HZB_Ellipsometry()
        if step.method == "SEM_Merlin":
            entity = HZB_SEM_Merlin()
        if step.method == "Sputtering":
            entity = CatLab_Sputtering()
        if step.method == "PECVD":
            entity = CatLab_PECVD()
        if step.method == "Catalytic_Reaction":
            entity = Catlab_SimpleCatalyticReaction()
    if step.method_type == "X-Y":
        if step.method == "XRR":
            entity = HZB_XRR_Library()
        if step.method == "XRD":
            entity = HZB_XRD_Library()
        if step.method == "XRF":
            entity = HZB_XRF_Library()
        if step.method == "XPS":
            entity = HZB_XPS_Library()
        if step.method == "Ellipsometry":
            entity = HZB_Ellipsometry_Library()
        if step.method == "Catalytic_Reaction":
            entity = Catlab_SimpleCatalyticReaction()
    if not entity:
        return
    entity.samples = [CompositeSystemReference(lab_id=sample_id)]
    entity.name = step.name
    if create_archive(entity, archive, file_name):
        entry_id = get_entry_id_from_file_name(file_name, archive)
        return get_reference(archive.metadata.upload_id, entry_id)


def copy_step(entity, archive, step_idx, step, sample_id):
    step.method = entity.method
    step.method_type = "Single"
    if "Library" in entity.m_root().metadata.entry_type:
        step.method_type = "Library"
    file_name = f"{step_idx}_{sample_id}_{step.method}_{step.method_type}.archive.json"
    entity.samples = [CompositeSystemReference(lab_id=sample_id)]
    entity.name = step.name
    entity.datetime = datetime.datetime.now()

    if create_archive(entity, archive, file_name):
        entry_id = get_entry_id_from_file_name(file_name, archive)
        return get_reference(archive.metadata.upload_id, entry_id)


def create_sample(archive, sample_type, sample_id):
    if sample_type == "Sample":
        entity = CatLab_Sample()
    if sample_type == "Library":
        entity = CatLab_Library()
    entity.lab_id = sample_id
    file_name = f"{sample_id}.archive.json"
    if create_archive(entity, archive, file_name):
        entry_id = get_entry_id_from_file_name(file_name, archive)
        return get_reference(archive.metadata.upload_id, entry_id)


class CatLab_Experiment(SingleSampleExperiment, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=["users", "lab_id"],
            properties=dict(
                order=[
                    "name",
                ])))

    def normalize(self, archive, logger):
        self.method = "Single Sample Experiment"

        if self.sample and self.sample.create_sample:
            self.sample.create_sample = False
            rewrite_json(["data", "sample", "create_sample"], archive, False)
            self.sample.reference = create_sample(archive, self.sample.sample_type, self.sample.lab_id)

        if self.steps and self.sample.lab_id:
            for i, step in enumerate(self.steps):
                if not step.create_experimental_step:
                    continue
                if step.activity:
                    step.activity = copy_step(step.activity, archive, i, step, self.sample.lab_id)
                    continue

                step.create_experimental_step = False
                rewrite_json(["data", "steps", i, "create_experimental_step"], archive, False)

                step.activity = create_step(archive, i, step, self.sample.lab_id)

        super(CatLab_Experiment, self).normalize(archive, logger)


m_package.__init_metainfo__()
