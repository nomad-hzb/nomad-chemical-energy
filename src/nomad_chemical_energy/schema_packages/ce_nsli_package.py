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


# from nomad.units import ureg
from baseclasses.characterizations import (
    SPV,
    SXM,
    TEM,
    XAS,
    XPEEM,
    XRD,
    InfraredSpectroscopy,
    Raman,
)
from baseclasses.characterizations.electron_microscopy import (
    SEM_Microscope_Merlin,
)
from baseclasses.chemical_energy import (
    Chronoamperometry,
    ConstantPotential,
    CyclicVoltammetry,
    DiamondSample,
    OpenCircuitVoltage,
    OpticalMicorscopy,
    PhotoCurrent,
    SubstrateProperties,
)
from baseclasses.mxene_solution import MXeneSolution
from baseclasses.wet_chemical_deposition import (
    DropCasting,
    SpinCoating,
    WetChemicalDeposition,
)
from nomad.datamodel.data import EntryData
from nomad.metainfo import (
    Quantity,
    Reference,
    SchemaPackage,
    Section,
    SubSection,
)

from .utilities.ce_nsli_id import CENSLIIdentifier

m_package = SchemaPackage()


def find_id(archive, lab_id, method):
    from nomad.search import search

    i = 1
    while True:
        next_lab_id = f'{lab_id}_{method}{i}'
        query = {'results.eln.lab_ids': next_lab_id}
        search_result = search(owner='all', query=query, user_id=archive.metadata.main_author.user_id)
        if len(search_result.data) == 0:
            return next_lab_id
        i += 1


def assign_id(obj, archive, method):
    if not obj.lab_id and obj.solution and obj.solution[0].solution and obj.solution[0].solution.lab_id:
        obj.lab_id = find_id(archive, obj.solution[0].solution.lab_id, method)


def get_processes(archive, entry_id, lab_id):
    from nomad import files
    from nomad.app.v1.models import MetadataPagination
    from nomad.search import search

    # search for all archives referencing this archive
    query = {
        'entry_references.target_entry_id': entry_id,
    }
    pagination = MetadataPagination()
    pagination.page_size = 100
    search_result = search(owner='all', query=query, pagination=pagination, user_id=archive.metadata.main_author.user_id)
    processes = []
    for res in search_result.data:
        with files.UploadFiles.get(upload_id=res['upload_id']).read_archive(entry_id=res['entry_id']) as archive_entry:
            entry_id = res['entry_id']
            entry_data = archive_entry[entry_id]['data']
            if 'lab_id' in entry_data and entry_data.get('lab_id').startswith(lab_id):
                processes.append((entry_data.get('lab_id'), entry_data.get('name')))
    return sorted(processes, key=lambda pair: pair[0])


# %% ####################### Entities


class CE_NSLI_MXene_Solution(MXeneSolution, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'users',
                'components',
                'elemental_composition',
            ],
            properties=dict(
                order=['name', 'create_overview', 'overview', 'MAX_phase', 'etching', 'delamination', 'washing', 'concentration', 'properties'],
            ),
        )
    )

    create_overview = Quantity(type=bool, default=False, a_eln=dict(component='BoolEditQuantity'))

    overview = Quantity(type=str, a_eln=dict(component='FileEditQuantity'), a_browser=dict(adaptor='RawFileAdaptor'))

    sample_id = SubSection(section_def=CENSLIIdentifier)

    def normalize(self, archive, logger):
        super().normalize(archive, logger)

        if self.create_overview and self.lab_id:
            self.create_overview = False

            data = [[p[0], p[1]] for p in get_processes(archive, archive.entry_id, self.lab_id)]
            import pandas as pd

            df = pd.DataFrame(data, columns=['process_id', 'process_name'])
            export_file_name = f'list_of_sample_preparations_{self.lab_id}.csv'
            with archive.m_context.raw_file(export_file_name, 'w') as outfile:
                df.to_csv(outfile.name)
            self.overview = export_file_name


# class CE_NSLI_Graphene(Chemical, EntryData):
#     m_def = Section(
#         a_eln=dict(hide=['lab_id', 'users']))


# class CE_NSLI_Sample(CENSLISample, EntryData):
#     m_def = Section(
#         a_eln=dict(hide=['users', 'components', 'elemental_composition']),
#         label_quantity='sample_id'
#     )


class CE_NSLI_DiamondSample(DiamondSample, EntryData):
    m_def = Section(a_eln=dict(hide=['users']), label_quantity='sample_id')


# %% ####################### Cleaning


# class CE_NSLI_UltrasoniceBath(Cleaning, EntryData):
#     m_def = Section(
#         a_eln=dict(
#             hide=[
#                 'lab_id', 'users', "location", "end_time"]))

#     cleaning = SubSection(
#         section_def=SolutionCleaning, repeats=True)


# %% ##################### Layer Deposition


# class CE_NSLI_WaterBath(WaterBath, EntryData):
#     m_def = Section(
#         a_eln=dict(
#             hide=[
#                 'lab_id', 'users', "location", "end_time"]))


class CE_NSLI_DropCasting(DropCasting, EntryData):
    m_def = Section(
        a_eln=dict(hide=['users', 'end_time', 'steps', 'instruments', 'results', 'samples', 'positon_in_experimental_plan', 'present', 'batch', 'layer'], properties=dict(order=['name', 'location', 'datetime', 'solution', 'substrate', 'properties', 'quenching', 'annealing', 'sintering']))
    )

    substrate = SubSection(section_def=SubstrateProperties)

    def normalize(self, archive, logger):
        assign_id(self, archive, 'dc')
        super().normalize(archive, logger)


class CE_NSLI_SpinCoating(SpinCoating, EntryData):
    m_def = Section(
        a_eln=dict(hide=['users', 'end_time', 'steps', 'instruments', 'results', 'recipe', 'samples', 'positon_in_experimental_plan', 'present', 'batch', 'layer'], properties=dict(order=['name', 'location', 'datetime', 'solution', 'substrate', 'recipe_steps', 'quenching', 'annealing', 'sintering']))
    )

    substrate = SubSection(section_def=SubstrateProperties)

    def normalize(self, archive, logger):
        assign_id(self, archive, 'sc')
        super().normalize(archive, logger)


class CE_NSLI_SEM(SEM_Microscope_Merlin, EntryData):
    m_def = Section(a_eln=dict(hide=['lab_id', 'users', 'location', 'end_time', 'steps', 'instruments', 'results', 'detector_data_folder', 'external_sample_url'], properties=dict(order=['name', 'detector_data', 'datetime', 'description', 'sample_preparation', 'samples'])))

    sample_preparation = Quantity(type=Reference(WetChemicalDeposition.m_def), a_eln=dict(component='ReferenceEditQuantity'))


class CE_NSLI_XRD_XY(XRD, EntryData):
    m_def = Section(
        a_eln=dict(hide=['lab_id', 'users', 'location', 'end_time', 'steps', 'instruments', 'results', 'steps', 'instruments', 'results', 'metadata_file', 'shifted_data', 'identifier'], properties=dict(order=['name', 'data_file', 'datetime', 'description', 'sample_preparation', 'samples'])),
        a_plot=[
            {'x': ['data/angle'], 'y': ['data/intensity'], 'layout': {'yaxis': {'fixedrange': False, 'title': 'Counts'}, 'xaxis': {'fixedrange': False}}},
        ],
    )

    sample_preparation = Quantity(type=Reference(WetChemicalDeposition.m_def), a_eln=dict(component='ReferenceEditQuantity'))

    # def normalize(self, archive, logger):

    #     if self.data_file:
    #         data_file_split = os.path.basename(self.data_file).split('.')
    #         with archive.m_context.raw_file(self.data_file) as f:
    #             file_name = f.name

    #         if os.path.splitext(self.data_file)[-1] == ".xy" and self.data is None:
    #             import pandas as pd
    #             skiprows = 0
    #             data = pd.read_csv(file_name, sep=" |\t", header=None, skiprows=skiprows)
    #             self.data = XRDData(angle=data[0], intensity=data[1])

    #             if len(data_file_split) > 2:
    #                 if self.description:
    #                     self.description += f"<br> Notes from file name: {data_file_split[1]}"
    #                 else:
    #                     self.description = f"Notes from file name: {data_file_split[1]}"

    #         preparation_id = data_file_split[0]
    #         if not self.sample_preparation:
    #             self.sample_preparation = get_entry_reference(archive, self, preparation_id)

    #         sample_id = "_".join(preparation_id.split("_")[:-1])
    #         if not self.samples:
    #             set_sample_reference(archive, self, sample_id)

    #     super(CE_NSLI_XRD_XY, self).normalize(archive, logger)


# %%####################################### Measurements


class CE_NSLI_CyclicVoltammetry(CyclicVoltammetry, EntryData):
    m_def = Section(
        a_eln=dict(hide=['lab_id', 'solution', 'users', 'location', 'end_time', 'working_electrode', 'counter_electrode', 'reference_electrode', 'electrolyte']),
        a_plot=[
            {
                'label': 'Current',
                'x': 'voltage',
                'y': 'current',
                'layout': {'yaxis': {'fixedrange': False}, 'xaxis': {'fixedrange': False}},
            }
        ],
    )


class CE_NSLI_Chronoamperometry(Chronoamperometry, EntryData):
    m_def = Section(
        a_eln=dict(hide=['lab_id', 'solution', 'users', 'location', 'end_time', 'working_electrode', 'counter_electrode', 'reference_electrode', 'electrolyte']),
        a_plot=[
            {
                'label': 'Current',
                'x': 'time',
                'y': 'current',
                'layout': {'yaxis': {'fixedrange': False}, 'xaxis': {'fixedrange': False}},
                'config': {
                    'scrollZoom': True,
                    'staticPlot': False,
                },
            }
        ],
    )


class CE_NSLI_OpenCircuitVoltage(OpenCircuitVoltage, EntryData):
    m_def = Section(
        a_eln=dict(hide=['lab_id', 'solution', 'users', 'location', 'end_time', 'working_electrode', 'counter_electrode', 'reference_electrode', 'electrolyte']),
        a_plot=[
            {
                'label': 'Voltage',
                'x': 'time',
                'y': 'voltage',
                'layout': {'yaxis': {'fixedrange': False}, 'xaxis': {'fixedrange': False}},
            }
        ],
    )


class CE_NSLI_ConstantPotential(ConstantPotential, EntryData):
    m_def = Section(a_eln=dict(hide=['lab_id', 'solution', 'users', 'location', 'end_time']))


class CE_NSLI_RamanSpectroscopy(Raman, EntryData):
    m_def = Section(
        a_eln=dict(hide=['lab_id', 'solution', 'users', 'location', 'end_time']),
        a_plot=[{'label': 'Intensity', 'x': ['raman_shift', 'peaks_raman'], 'y': ['intensity', 'peaks_intensity'], 'layout': {'yaxis': {'type': 'lin'}}, 'lines': [{'mode': 'lines', 'marker': {'color': 'rgb(40, 80, 130)'}}, {'mode': 'markers', 'line': {'color': 'rgb(100, 0, 0)'}}]}],
    )


class CE_NSLI_InfraredSpectroscopy(InfraredSpectroscopy, EntryData):
    m_def = Section(
        a_eln=dict(hide=['lab_id', 'solution', 'users', 'location', 'end_time']),
        a_plot=[
            {
                'label': 'Absorbance',
                'x': 'wave_number',
                'y': 'absorbance',
                'layout': {'yaxis': {'type': 'lin'}},
            }
        ],
    )


class CE_NSLI_XAS(XAS, EntryData):
    m_def = Section(a_eln=dict(hide=['lab_id', 'solution', 'users', 'location', 'end_time']))


class CE_NSLI_OpticalMicroscopy(OpticalMicorscopy, EntryData):
    m_def = Section(a_eln=dict(hide=['lab_id', 'solution', 'users', 'location', 'end_time']))


class CE_NSLI_TEM(TEM, EntryData):
    m_def = Section(a_eln=dict(hide=['lab_id', 'solution', 'users', 'location', 'end_time']))


class CE_NSLI_SXM(SXM, EntryData):
    m_def = Section(a_eln=dict(hide=['lab_id', 'solution', 'users', 'location', 'end_time']))


class CE_NSLI_XPEEM(XPEEM, EntryData):
    m_def = Section(a_eln=dict(hide=['lab_id', 'solution', 'users', 'location', 'end_time']))


class CE_NSLI_Photocurrent(PhotoCurrent, EntryData):
    m_def = Section(a_eln=dict(hide=['lab_id', 'solution', 'users', 'location', 'end_time']), a_plot=[{'label': 'Energy', 'x': 'energy', 'y': 'voltage', 'layout': {'yaxis': {'fixedrange': False}, 'xaxis': {'fixedrange': False}}, 'config': {'scrollZoom': True}}])

    # def normalize(self, archive, logger):
    #     super(CE_NSLI_Photocurrent, self).normalize(archive, logger)

    #     electro_measurements = {}
    #     if self.data_files and len(self.data_files) > 0:
    #         for data_file in self.data_files:
    #             try:
    #                 with archive.m_context.raw_file(data_file) as f:
    #                     data_file_name = os.path.basename(f.name)
    #                     file_name_split = os.path.splitext(data_file_name)
    #                     if file_name_split[-1] == ".mpt":
    #                         file_name = f'{file_name_split[0]}.archive.json'
    #                         split_file_name = file_name_split[0].split("_")
    #                         technique_number = int(split_file_name[-3])
    #                         entity = None
    #                         if split_file_name[-2] == "CA":
    #                             entity = CE_NSLI_Chronoamperometry(
    #                                 data_file=data_file_name,
    #                                 metadata_file=self.electro_meta_data_file_name if self.electro_meta_data_file_name else None,
    #                                 samples=self.samples if self.samples else [],
    #                                 name=file_name_split[0].replace("_", " "))
    #                         if split_file_name[-2] == "CV":
    #                             entity = CE_NSLI_CyclicVoltammetry(
    #                                 data_file=data_file_name,
    #                                 metadata_file=self.electro_meta_data_file_name if self.electro_meta_data_file_name else None,
    #                                 samples=self.samples if self.samples else [],
    #                                 name=file_name_split[0].replace("_", " "))
    #                         if split_file_name[-2] == "OCV":
    #                             entity = CE_NSLI_OpenCircuitVoltage(
    #                                 data_file=data_file_name,
    #                                 metadata_file=self.electro_meta_data_file_name if self.electro_meta_data_file_name else None,
    #                                 samples=self.samples if self.samples else [],
    #                                 name=file_name_split[0].replace("_", " "))
    #                         if entity:
    #                             create_archive(entity, archive, file_name)
    #                             electro_measurements.update(
    #                                 {technique_number: f'../upload/archive/mainfile/{file_name}#data'})

    #             except Exception as e:
    #                 logger.error(e)

    #     electro_measurements_list = []
    #     if electro_measurements:
    #         keys = sorted(electro_measurements.keys())
    #         for key in keys:
    #             electro_measurements_list.append(electro_measurements[key])
    #     self.electro_measurements = electro_measurements_list


class CE_NSLI_SPV(SPV, EntryData):
    m_def = Section(a_eln=dict(hide=['lab_id', 'solution', 'users', 'location', 'end_time']), a_plot=[{'label': 'Voltage', 'x': 'wavelength', 'y': 'volt', 'layout': {'yaxis': {'type': 'lin'}}, 'config': {'editable': True, 'scrollZoom': True}}])


# %%####################################### Generic Entries


# class CE_NSLI_Process(ProcessOnSample, EntryData):
#     m_def = Section(
#         a_eln=dict(
#             hide=[
#                 'lab_id', 'users', "location", "end_time"]))

#     data_file = Quantity(
#         type=str,
#         shape=['*'],
#         a_eln=dict(component='FileEditQuantity'),
#         a_browser=dict(adaptor='RawFileAdaptor'))


# class CE_NSLI_Deposition(Deposition, EntryData):
#     m_def = Section(
#         a_eln=dict(
#             hide=[
#                 'lab_id', 'users', "location", "end_time"]))

#     data_file = Quantity(
#         type=str,
#         shape=['*'],
#         a_eln=dict(component='FileEditQuantity'),
#         a_browser=dict(adaptor='RawFileAdaptor'))


# class CE_NSLI_Measurement(MeasurementOnSample, EntryData):
#     m_def = Section(
#         a_eln=dict(
#             hide=[
#                 'lab_id', 'users', "location", "end_time"]))

#     data_file = Quantity(
#         type=str,
#         shape=['*'],
#         a_eln=dict(component='FileEditQuantity'),
#         a_browser=dict(adaptor='RawFileAdaptor'))

m_package.__init_metainfo__()
