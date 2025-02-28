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


from baseclasses import BaseMeasurement
from baseclasses.catalysis import CatalysisLibrary, CatalysisSample, CatalysisXYSample
from baseclasses.helper.utilities import export_lab_id
from baseclasses.vapour_based_deposition import MultiTargetSputtering, PECVDeposition
from nomad.datamodel.data import EntryData

# from nomad.units import ureg
from nomad.metainfo import Quantity, SchemaPackage, Section

# from nomad_measurements.catalytic_measurement.catalytic_measurement import ReactionConditions
from unidecode import unidecode

m_package = SchemaPackage()


def correct_lab_id(lab_id):
    return lab_id[4:].isdigit() and len(lab_id[4:]) == 4


def get_next_project_sample_number(data, entry_id):
    """Check the lab ids of a project id for project_sample_number (last digits of lab_id) and returns the next higher one"""
    project_sample_numbers = []
    for entry in data:
        lab_ids = entry['results']['eln']['lab_ids']
        if entry['entry_id'] == entry_id and correct_lab_id(lab_ids[0]):
            return int(lab_ids[0][4:])
        project_sample_numbers.extend(
            [int(lab_id[4:]) for lab_id in lab_ids if correct_lab_id(lab_id)]
        )
    return max(project_sample_numbers) + 1 if project_sample_numbers else 1


def create_id(archive, lab_id_base):
    from nomad.app.v1.models import MetadataPagination
    from nomad.search import search

    query = {'entry_type': 'CatLab_Sample', 'results.eln.lab_ids': lab_id_base}
    pagination = MetadataPagination()
    pagination.page_size = 9999
    search_result = search(
        owner='all',
        query=query,
        pagination=pagination,
        user_id=archive.metadata.main_author.user_id,
    )
    project_sample_number = get_next_project_sample_number(
        search_result.data, archive.metadata.entry_id
    )

    return f'{lab_id_base}{project_sample_number:04d}'


class CatLab_XYSample(CatalysisXYSample, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['users', 'components'],
            properties=dict(
                order=[
                    'name',
                    'lab_id',
                ]
            ),
        ),
        a_plot=[
            {
                'x': 'xray_diffraction/scattering_vector',
                'y': 'xray_diffraction/intensity',
                'layout': {
                    'showlegend': True,
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False},
                },
            }
        ],
    )


class CatLab_Sample(CatalysisSample, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['users', 'elemental_composition', 'components'],
            properties=dict(
                order=[
                    'name',
                    'lab_id',
                ]
            ),
        ),
    )

    lab_id = Quantity(
        type=str,
        description="""An ID string that is unique at least for the lab that produced this data.""",
    )

    def normalize(self, archive, logger):
        super().normalize(archive, logger)

        if not self.lab_id:
            author = archive.metadata.main_author
            first_short, last_short = 'S', ''
            try:
                first_short = unidecode(author.first_name)[:2]
                last_short = unidecode(author.last_name)[:2]
            except Exception:
                pass
            self.lab_id = create_id(archive, str(first_short) + str(last_short))
        export_lab_id(archive, self.lab_id)


class CatLab_Library(CatalysisLibrary, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['users', 'elemental_composition', 'components'],
            properties=dict(
                order=[
                    'name',
                    'lab_id',
                ]
            ),
        )
    )


class CatLab_Sputtering(MultiTargetSputtering, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'users',
                'elemental_composition',
                'components',
                'present',
                'instruments',
                'steps',
                'end_time',
                'batch',
                'lab_id',
            ],
            properties=dict(
                order=[
                    'name',
                    'lab_id',
                ]
            ),
        )
    )


class Catlab_SimpleCatalyticReaction(BaseMeasurement, EntryData):
    """
    Example section for a simple catalytic reaction.
    """

    m_def = Section(
        label='Simple Catalytic Measurement for Catlab',
        a_eln=dict(hide=['steps', 'instruments', 'results', 'lab_id']),
    )

    data_file = Quantity(
        type=str,
        shape=['*'],
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'),
    )

    # reaction = SubSection(section_def=ReactionConditions, a_eln=ELNAnnotation(label='Reaction Data'))


class CatLab_PECVD(PECVDeposition, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'users',
                'elemental_composition',
                'components',
                'present',
                'lab_id',
                'end_time',
                'batch',
                'instruments',
                'steps',
            ],
            properties=dict(
                order=[
                    'name',
                ]
            ),
        )
    )

    # def normalize(self, archive, logger):
    #     process = PECVDProcess()
    #     if self.process is not None:
    #         process = self.process
    #     if self.recipe is not None and os.path.splitext(self.recipe)[
    #             1] == ".set":
    #         from baseclasses.helper.file_parser.parse_files_pecvd_pvcomb import parse_recipe
    #         with archive.m_context.raw_file(self.recipe) as f:
    #             parse_recipe(f, process)

    #     if self.logs is not None:
    #         logs = []
    #         for log in self.logs:
    #             if os.path.splitext(log)[1] == ".log":
    #                 from baseclasses.helper.file_parser.parse_files_pecvd_pvcomb import parse_log
    #                 with archive.m_context.raw_file(log) as f:
    #                     if process.time:
    #                         data = parse_log(
    #                             f,
    #                             process,
    #                             np.int64(0.9 * process.time),
    #                             np.int64(0.05 * process.time))
    #                     else:
    #                         data = parse_log(f, process)
    #                     data.name = log
    #                     logs.append(data)
    #         process.log_data = logs
    #     self.process = process

    #     super(CatLab_PECVD, self).normalize(archive, logger)


# def create_step(archive, step_idx, step, sample_id):
#     file_name = f"{step_idx}_{sample_id}_{step.method}_{step.method_type}.archive.json"
#     entity = None
#     if step.method_type == "Single":
#         if step.method == "XRR":
#             entity = HZB_XRR()
#         if step.method == "XRD":
#             entity = HZB_XRD()
#         if step.method == "XRF":
#             entity = HZB_XRF()
#         if step.method == "XPS":
#             entity = HZB_XPS()
#         if step.method == "TGA":
#             entity = HZB_TGA()
#         if step.method == "Ellipsometry":
#             entity = HZB_Ellipsometry()
#         if step.method == "SEM_Merlin":
#             entity = HZB_SEM_Merlin()
#         if step.method == "Sputtering":
#             entity = CatLab_Sputtering()
#         if step.method == "PECVD":
#             entity = CatLab_PECVD()
#         if step.method == "Catalytic_Reaction":
#             entity = Catlab_SimpleCatalyticReaction()
#     if step.method_type == "X-Y":
#         if step.method == "XRR":
#             entity = HZB_XRR_Library()
#         if step.method == "XRD":
#             entity = HZB_XRD_Library()
#         if step.method == "XRF":
#             entity = HZB_XRF_Library()
#         if step.method == "XPS":
#             entity = HZB_XPS_Library()
#         if step.method == "Ellipsometry":
#             entity = HZB_Ellipsometry_Library()
#         if step.method == "Catalytic_Reaction":
#             entity = Catlab_SimpleCatalyticReaction()
#     if not entity:
#         return
#     entity.samples = [CompositeSystemReference(lab_id=sample_id)]
#     entity.name = step.name
#     if create_archive(entity, archive, file_name):
#         entry_id = get_entry_id_from_file_name(file_name, archive)
#         return get_reference(archive.metadata.upload_id, entry_id)


# def copy_step(entity, archive, step_idx, step, sample_id):
#     step.method = entity.method
#     step.method_type = "Single"
#     if "Library" in entity.m_root().metadata.entry_type:
#         step.method_type = "Library"
#     file_name = f"{step_idx}_{sample_id}_{step.method}_{step.method_type}.archive.json"
#     entity.samples = [CompositeSystemReference(lab_id=sample_id)]
#     entity.name = step.name
#     entity.datetime = datetime.datetime.now()

#     if create_archive(entity, archive, file_name):
#         entry_id = get_entry_id_from_file_name(file_name, archive)
#         return get_reference(archive.metadata.upload_id, entry_id)


# def create_sample(archive, sample_type, sample_id):
#     if sample_type == "Sample":
#         entity = CatLab_Sample()
#     if sample_type == "Library":
#         entity = CatLab_Library()
#     entity.lab_id = sample_id
#     file_name = f"{sample_id}.archive.json"
#     if create_archive(entity, archive, file_name):
#         entry_id = get_entry_id_from_file_name(file_name, archive)
#         return get_reference(archive.metadata.upload_id, entry_id)


# class CatLab_Experiment(SingleSampleExperiment, EntryData):
#     m_def = Section(
#         a_eln=dict(
#             hide=["users", "lab_id"],
#             properties=dict(
#                 order=[
#                     "name",
#                 ])))

#     def normalize(self, archive, logger):
#         self.method = "Single Sample Experiment"

#         if self.sample and self.sample.create_sample:
#             self.sample.create_sample = False
#             rewrite_json(["data", "sample", "create_sample"], archive, False)
#             self.sample.reference = create_sample(archive, self.sample.sample_type, self.sample.lab_id)

#         if self.steps and self.sample.lab_id:
#             for i, step in enumerate(self.steps):
#                 if not step.create_experimental_step:
#                     continue
#                 if step.activity:
#                     step.activity = copy_step(step.activity, archive, i, step, self.sample.lab_id)
#                     continue

#                 step.create_experimental_step = False
#                 rewrite_json(["data", "steps", i, "create_experimental_step"], archive, False)

#                 step.activity = create_step(archive, i, step, self.sample.lab_id)

#         super(CatLab_Experiment, self).normalize(archive, logger)


m_package.__init_metainfo__()
