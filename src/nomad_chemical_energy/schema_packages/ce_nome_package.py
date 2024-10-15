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

import numpy as np
import os
import pandas as pd

from nomad.datamodel.metainfo.plot import PlotSection, PlotlyFigure
import plotly.graph_objs as go

# from nomad.units import ureg
from nomad.metainfo import (
    Package,
    Quantity,
    Section, SubSection, SchemaPackage)
from nomad.datamodel.data import EntryData

from nomad.datamodel.metainfo.eln import Substance
from baseclasses import PubChemPureSubstanceSectionCustom


from nomad.datamodel.metainfo.basesections import (
    Process
)

from baseclasses import (
    BaseProcess, BaseMeasurement
)

from baseclasses.design1 import Design
from baseclasses.documentation_tool import DocumentationTool

from baseclasses.characterizations import (
    XASFluorescence, XASTransmission
)

from baseclasses.voila import (
    VoilaNotebook
)

from baseclasses.solar_energy import UVvisMeasurement

from baseclasses.material_processes_misc import Annealing

from baseclasses.chemical_energy import (
    CENOMESample, SampleIDCENOME, Electrode, Electrolyte, ElectroChemicalCell, SubstrateProperties, Equipment,
    ExpectedStructure,
    CatalystSynthesis,
    ElectroChemicalSetup, Environment, Purging, SubstanceWithConcentration,
    get_next_project_sample_number,
    CyclicVoltammetry,
    Chronoamperometry,
    Chronopotentiometry,
    Chronocoulometry,
    CPAnalysis,
    OpenCircuitVoltage,
    ElectrochemicalImpedanceSpectroscopy,
    # PreparationProtocol,
    GalvanodynamicSweep,
    PhaseFluorometryOxygen,
    PumpRateMeasurement,
    LinearSweepVoltammetry,
    UVvisDataConcentration, Massspectrometry
)

from baseclasses.data_transformations import UVvisConcentrationDetection

from baseclasses.helper.utilities import create_archive, rewrite_json, find_sample_by_id
from datetime import datetime

m_package = SchemaPackage()

# %% ####################### Entities


class CE_NOME_Design(Design, EntryData):
    pass


class CE_NOME_Sample(CENOMESample, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=["users", "elemental_composition", "components"],
            properties=dict(
                order=[
                    "name",
                    "lab_id", "chemical_composition_or_formulas",
                    "id_of_preparation_protocol"])),
        label_quantity='sample_id')


class CE_NOME_Electrode(Electrode, EntryData):
    m_def = Section(
        a_eln=dict(hide=['users', 'origin', "elemental_composition", "components"],
                   properties=dict(
                       order=[
                           "name", "lab_id",
                           "chemical_composition_or_formulas", "producer", "location"
                       ]))
    )


class CE_NOME_Equipment(Equipment, EntryData):
    m_def = Section(
        a_eln=dict(hide=['users', 'origin', "elemental_composition", "components"],
                   properties=dict(
                       order=[
                           "name", "lab_id",
                           "producer", "location"
                       ]))
    )


# class CE_NOME_Electrolyte(Electrolyte, EntryData):
#     m_def = Section(
#         a_eln=dict(
#             hide=[
#                 'users',
#                 'origin', "elemental_composition", "components"],
#             properties=dict(
#                 editable=dict(
#                     exclude=["chemical_composition_or_formulas"]),
#                 order=[
#                     "name",
#                     "lab_id",
#                     "chemical_composition_or_formulas",
#                     "ph_value",
#                     "solvent"])))


class CE_NOME_Environment(Environment, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'users',
                'origin', "elemental_composition", "components", "substrate"],
            properties=dict(
                editable=dict(
                    exclude=["chemical_composition_or_formulas"]),
                order=[
                    "name",
                    "lab_id",
                    "chemical_composition_or_formulas",
                    "ph_value",
                    "solvent"])))

    environment_id = SubSection(
        section_def=SampleIDCENOME)


class CE_NOME_Chemical(Substance, EntryData):
    m_def = Section(
        a_eln=dict(hide=['users', 'origin', "elemental_composition", "components"]))


# class CE_NOME_ElectroChemicalCell(ElectroChemicalCell, EntryData):
#     m_def = Section(
#         a_eln=dict(hide=['users', 'origin', "elemental_composition", "components"],
#                    properties=dict(
#             order=[
#                 "name",
#                 "lab_id",
#                 "chemical_composition_or_formulas",
#                 "working_electrode",
#                 "reference_electrode",
#                 "counter_electrode",
#                 "electrolyte"
#             ])),
#     )

#     ecc_id = SubSection(
#         section_def=SampleIDCENOME)


class CE_NOME_ElectroChemicalSetup(ElectroChemicalSetup, EntryData):
    m_def = Section(
        a_eln=dict(hide=['users', 'origin', "elemental_composition", "components", "substrate"],
                   properties=dict(
                       order=[
                           "name",
                           "lab_id",
                           "chemical_composition_or_formulas",
                           "setup",
                           "reference_electrode",
                           "counter_electrode", "equipment"
                       ])),
    )

    setup_id = SubSection(
        section_def=SampleIDCENOME)


class CE_NOME_Annealing(Process, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'users',
                'origin', "lab_id", "instruments", "steps", "end_time"],
            properties=dict(
                order=[
                    "name"
                ])))

    properties = SubSection(section_def=Annealing)

    def normalize(self, archive, logger):
        self.method = "Annealing"
        super(CE_NOME_Annealing, self).normalize(archive, logger)


# class CE_NOME_Batch(CENOMESample, EntryData):
#     m_def = Section(
#         a_eln=dict(
#             hide=['users', "elemental_composition", "components"],
#             properties=dict(
#                 order=[
#                     "name",
#                     "lab_id",
#                     "chemical_composition_or_formulas",
#                     "id_of_preparation_protocol",
#                     "number_of_samples",
#                     "create_samples"
#                 ])))

#     number_of_samples = Quantity(
#         type=np.dtype(np.int64),
#         default=0,
#         a_eln=dict(
#             component='NumberEditQuantity'
#         ))

#     create_samples = Quantity(
#         type=bool,
#         default=False,
#         a_eln=dict(component='BoolEditQuantity')
#     )

#     def normalize(self, archive, logger):
#         super(CE_NOME_Batch, self).normalize(archive, logger)

#         if self.number_of_samples > 0 and self.create_samples:
#             self.create_samples = False

#             from nomad.search import search

#             query = {
#                 'results.eln.lab_ids': archive.results.eln.lab_ids[1]
#             }

#             search_result = search(
#                 owner='all',
#                 query=query,
#                 user_id=archive.metadata.main_author.user_id)

#             next_project_sample_number = get_next_project_sample_number(
#                 search_result.data, archive.metadata.entry_id)

#             for sample_idx in range(self.number_of_samples):
#                 ce_nome_sample = CE_NOME_Sample(
#                     origin=self.origin if self.origin is not None else None,
#                     chemical_composition_or_formulas=self.chemical_composition_or_formulas if self.chemical_composition_or_formulas is not None else None,
#                     sample_id=self.sample_id if self.sample_id is not None else None,
#                     # id_of_preparation_protocol=self.id_of_preparation_protocol if self.id_of_preparation_protocol is not None else None,
#                     date_of_disposal=self.date_of_disposal if self.date_of_disposal is not None else None,
#                     components=self.components if self.components is not None else None,
#                     project_name_long=self.project_name_long if self.project_name_long is not None else None,
#                     datetime=self.datetime if self.datetime is not None else None,
#                     description=self.description if self.description is not None else None,
#                     name=f'{self.name} {next_project_sample_number + sample_idx}' if self.name is not None else None,
#                 )

#                 if ce_nome_sample.sample_id is not None:
#                     ce_nome_sample.sample_id.project_sample_number = next_project_sample_number + sample_idx

#                 file_name = f'{self.name.replace(" ","_")}_{next_project_sample_number+sample_idx}.archive.json'
#                 create_archive(ce_nome_sample, archive, file_name)


# class CE_NOME_PreparationProtocol(PreparationProtocol, EntryData):
#     m_def = Section(
#         a_eln=dict(hide=['users'],
#                    properties=dict(
#             order=[
#                 "name",
#                 "data_file",
#                 "lab_id"])),
#     )

def get_next_free_project_number(archive, entity_id):
    from nomad.search import search
    from nomad.app.v1.models import MetadataPagination

    query = {'results.eln.lab_ids': entity_id}
    pagination = MetadataPagination()
    pagination.page_size = 9999
    search_result = search(owner='all', query=query, pagination=pagination,
                           user_id=archive.metadata.main_author.user_id)
    return get_next_project_sample_number(search_result.data, entity_id)


def get_parameter(obj, key):
    value = None
    try:
        value = obj[key]
    except:
        pass
    if pd.isna(value):
        return None
    return value


def get_number_of_substances(row, prefix):
    return sum([s.startswith(prefix) for s in list(row.keys())])


def set_setup(archive, row):
    return CE_NOME_ElectroChemicalSetup(
        name=get_parameter(row, "name"),
        setup=get_parameter(row, "setup"),
        reference_electrode=find_sample_by_id(archive, get_parameter(row, "reference_electrode")),
        counter_electrode=find_sample_by_id(archive, get_parameter(row, "counter_electrode")),
        equipment=[find_sample_by_id(archive, row[f"equipment_{i}"]) for i in range(
            5) if get_parameter(row, f"equipment_{i}") and find_sample_by_id(archive, row[f"equipment_{i}"])],
        description=get_parameter(row, "description"),
    )


def set_environment(row):
    number_of_substances_per_env = get_number_of_substances(row, "substance_name_")
    return CE_NOME_Environment(
        name=get_parameter(row, "name"),
        ph_value=get_parameter(row, "ph_value"),
        description=get_parameter(row, "description"),
        solvent=PubChemPureSubstanceSectionCustom(
            name=row["solvent_name"], load_data=False) if not pd.isna(row[f"solvent_name"]) else None,
        purging=Purging(time=get_parameter(row, "purging_time"), temperature=get_parameter(row, "purging_temperature"),
                        gas=PubChemPureSubstanceSectionCustom(name=get_parameter(row, "purging_gas_name"),
                                                              load_data=False)) if not pd.isna(
            row[f"purging_gas_name"]) else None,
        substances=[SubstanceWithConcentration(
            concentration_mmol_per_l=float(get_parameter(row, f"concentration_M_{i}")) * 1000 if get_parameter(row,
                                                                                                               f"concentration_M_{i}") else None,
            concentration_g_per_l=get_parameter(
                row, f"concentration_g_per_l_{i}"),
            amount_relative=get_parameter(
                row, f"amount_relative_{i}"),
            substance=PubChemPureSubstanceSectionCustom(name=get_parameter(row, f"substance_name_{i}"), load_data=False))
            for i in range(number_of_substances_per_env) if not pd.isna(row[f"substance_name_{i}"])],
    )


def set_sample(row):
    number_of_substances_per_synthesis = get_number_of_substances(row, "substance_name_")
    return CE_NOME_Sample(
        name=get_parameter(row, "name"),
        chemical_composition_or_formulas=get_parameter(row, "chemical_composition_or_formula"),
        component_description=get_parameter(row, "component_description"),
        origin=get_parameter(row, "producer"),
        project_name_long=get_parameter(row, "project_name_long"),
        description=get_parameter(row, "description"),
        substrate=SubstrateProperties(substrate_type=get_parameter(row, "substrate_type"),
                                      substrate_dimension=get_parameter(row, "substrate_dimension")),
        active_area=get_parameter(row, "active_area_cm**2"),
        mass_coverage=get_parameter(row, "mass_coverage_ug_cm**2"),
        expected_structure=ExpectedStructure(expected_structure_links=get_parameter(row, "expected_structure_links").split(",") if get_parameter(row, "expected_structure_links") else None,
                                             expected_structure_description=get_parameter(row, "expected_structure_description")),
        synthesis=[CatalystSynthesis(method=get_parameter(row, "synthesis_method"),
                                     description=get_parameter(row, "synthesis_description"),
                                     substances=[SubstanceWithConcentration(concentration_mmol_per_l=float(
                                         get_parameter(row, f"concentration_M_{i}")) * 1000 if get_parameter(row,
                                                                                                             f"concentration_M_{i}") else None,
                                         concentration_g_per_l=get_parameter(
                                         row, f"concentration_g_per_l_{i}"),
                                         amount_relative=get_parameter(
                                         row, f"amount_relative_{i}"),
                                         substance=PubChemPureSubstanceSectionCustom(
                                         name=get_parameter(row,
                                                            f"substance_name_{i}"),
                                         load_data=False))
            for i in range(number_of_substances_per_synthesis) if
            not pd.isna(row[f"substance_name_{i}"])]

        )])


class CE_NOME_DocumentationTool(DocumentationTool, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=["number_of_substances_per_env", "number_of_substances_per_synthesis"],
            properties=dict(
                order=[
                    "name",
                    "lab_id", "create_template", "create_entries", "data_file",
                    "number_of_substances_per_env", "number_of_substances_per_synthesis"])))

    def normalize(self, archive, logger):
        super(CE_NOME_DocumentationTool, self).normalize(archive, logger)
        if self.identifier is None:
            author = archive.metadata.main_author
            self.identifier = SampleIDCENOME(owner=f"{author.first_name} {author.last_name}")
            self.identifier.normalize(archive, logger)
            super(CE_NOME_DocumentationTool, self).normalize(archive, logger)

        if self.create_entries and self.data_file:
            if not self.lab_id:
                logger.error(
                    "no identifier information provided", normalizer=self.__class__.__name__,
                    section='system')
                return
            self.create_entries = False
            rewrite_json(["data", "create_entries"], archive, False)

            with archive.m_context.raw_file(archive.metadata.mainfile) as f:
                path = os.path.dirname(f.name)
            # load data
            xls = pd.ExcelFile(os.path.join(path, self.data_file))
            samples = pd.read_excel(xls, 'samples').astype({'id': 'str'})
            envs = pd.read_excel(xls, 'environments').astype({'id': 'str'})
            setups = pd.read_excel(xls, 'setups').astype({'id': 'str'})

            # prepare id
            id_base = "_".join(self.lab_id.split("_")[:-1])
            id_base_sample = "_".join([id_base, self.datetime.strftime('%y%m%d')])  # today??
            next_free_id = get_next_free_project_number(archive, id_base)
            next_free_id_sample = get_next_free_project_number(archive, id_base_sample)
            counter = 0
            counter_sample = 0

            # samples
            for idx, row in samples.iterrows():
                edit = True if row[0].startswith("CE-NOME") else False
                try:
                    ce_nome_sample = set_sample(row)
                    ce_nome_sample.lab_id = f"{id_base_sample}_{next_free_id_sample + counter_sample:04d}" if not edit else row[0]
                    file_name = f"{archive.metadata.mainfile.replace('.archive.json', '')}_sample_{idx}.archive.json"
                    created = create_archive(ce_nome_sample, archive, file_name, overwrite=edit)
                    samples.at[idx, "id"] = ce_nome_sample.lab_id

                    if not edit:
                        counter_sample += 1
                except Exception as e:
                    logger.error(f"could not create row {idx} for samples",
                                 normalizer=self.__class__.__name__, section='system')
                    raise e
            # environments
            for idx, row in envs.iterrows():
                edit = True if row[0].startswith("CE-NOME") else False
                try:
                    ce_nome_envs = set_environment(row)
                    ce_nome_envs.lab_id = f"{id_base}_{next_free_id + counter:04d}" if not edit else row[0]
                    file_name = f"{archive.metadata.mainfile.replace('.archive.json', '')}_env_{idx}.archive.json"
                    created = create_archive(ce_nome_envs, archive, file_name, overwrite=edit)
                    envs.at[idx, "id"] = ce_nome_envs.lab_id

                    if not edit:
                        counter += 1
                except Exception as e:
                    logger.error(f"could not create row {idx} for environment",
                                 normalizer=self.__class__.__name__, section='system')
                    raise e

            # setups
            for idx, row in setups.iterrows():
                edit = True if row[0].startswith("CE-NOME") else False
                try:
                    ce_nome_setup = set_setup(archive, row)
                    ce_nome_setup.lab_id = f"{id_base}_{next_free_id + counter:04d}" if not edit else row[0]
                    file_name = f"{archive.metadata.mainfile.replace('.archive.json', '')}_setup_{idx}.archive.json"
                    created = create_archive(ce_nome_setup, archive, file_name, overwrite=edit)
                    setups.at[idx, "id"] = ce_nome_setup.lab_id

                    if not edit:
                        counter += 1
                except Exception as e:
                    logger.error(f"could not create row {idx} for setups",
                                 normalizer=self.__class__.__name__, section='system')
                    raise e

            with pd.ExcelWriter(os.path.join(path, self.data_file)) as writer:
                samples.to_excel(writer, sheet_name='samples', index=False)
                envs.to_excel(writer, sheet_name='environments', index=False)
                setups.to_excel(writer, sheet_name='setups', index=False)

# %%####################################### Measurements


class Bessy2_KMC2_XASFluorescence(XASFluorescence, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users', "location", 'end_time', 'steps', 'instruments', 'results'],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "samples"])))

    def normalize(self, archive, logger):
        if self.data_file:
            if os.path.splitext(self.data_file)[-1] == ".dat":
                with archive.m_context.raw_file(self.data_file, "rt") as f:
                    from nomad_chemical_energy.schema_packages.file_parser.xas_parser import get_xas_data
                    data, dateline = get_xas_data(f)
                from baseclasses.helper.archive_builder.xas_archive import get_xas_archive
                get_xas_archive(data, dateline, self)

        super(Bessy2_KMC2_XASFluorescence, self).normalize(archive, logger)


class Bessy2_KMC2_XASTransmission(XASTransmission, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'solution',
                'users', "location", 'end_time', 'steps', 'instruments', 'results'],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "samples"])))

    def normalize(self, archive, logger):
        if self.data_file:
            if os.path.splitext(self.data_file)[-1] == ".dat":
                with archive.m_context.raw_file(self.data_file, "rt") as f:
                    from nomad_chemical_energy.schema_packages.file_parser.xas_parser import get_xas_data
                    data, dateline = get_xas_data(f)
                from baseclasses.helper.archive_builder.xas_archive import get_xas_archive
                get_xas_archive(data, dateline, self)
        super(Bessy2_KMC2_XASTransmission, self).normalize(archive, logger)


class CE_NOME_ElectrochemicalImpedanceSpectroscopy(
        ElectrochemicalImpedanceSpectroscopy, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'solution',
                'users', "location", 'end_time', 'steps', 'instruments', 'results', "metadata_file"],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "environment",
                    "setup",
                    "samples",
                    "station"])),
        a_plot=[
            {
                'label': 'Nyquist Plot',
                'x': 'z_real',
                'y': 'z_imaginary',
                'layout': {
                    'yaxis': {
                        "fixedrange": False, "title": "-Im(Z) (Ω)"},
                    'xaxis': {
                        "fixedrange": False, "title": "Re(Z) (Ω)"}}
            },
            {
                'label': 'Bode Plot',
                'x': ['frequency', 'frequency'],
                'y': ['./z_modulus', './z_angle'],
                'layout': {
                    "showlegend": True,
                    'yaxis': {
                        "fixedrange": False},
                    'xaxis': {
                        "fixedrange": False, 'type': 'log'}},
            }
        ]
    )

    def normalize(self, archive, logger):
        if self.data_file:
            with archive.m_context.raw_file(self.data_file, "rt") as f:
                if os.path.splitext(self.data_file)[-1] == ".DTA":
                    from nomad_chemical_energy.schema_packages.file_parser.gamry_parser import get_header_and_data
                    from baseclasses.helper.archive_builder.gamry_archive import get_eis_properties, get_eis_data, \
                        get_meta_data
                    metadata, data = get_header_and_data(f)
                    get_eis_data(data["ZCURVE"][0], self)
                    get_meta_data(metadata, self)
                    if not self.properties:
                        self.properties = get_eis_properties(metadata)
        super(CE_NOME_ElectrochemicalImpedanceSpectroscopy,
              self).normalize(archive, logger)


def get_curve_tag(methods, function):
    if not methods:
        return "CURVE"
    if "-" not in methods:
        return "CURVE"

    if "gen" in function.lower():
        return "CURVE GENERATOR"
    if "det" in function.lower():
        return "CURVE DETECTOR"


class CE_NOME_VoilaNotebook(VoilaNotebook, EntryData):
    m_def = Section(

    )

    def normalize(self, archive, logger):
        super(CE_NOME_VoilaNotebook, self).normalize(archive, logger)


class CE_NOME_CyclicVoltammetry(CyclicVoltammetry, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'solution',
                'users', "location", 'end_time', 'steps', 'instruments', 'results', "metadata_file", "voltage",
                "current", "current_density", "voltage_rhe_uncompensated", "time",
                "voltage_rhe_compensated", "voltage_ref_compensated", "charge_density", "control", "charge"],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "environment",
                    "setup",
                    "samples",
                    "station", "voltage_shift", "resistance"])),
        a_plot=[{
            'label': 'Current Density over Voltage RHE',
            'x': 'cycles/:/voltage_rhe_compensated',
            'y': 'cycles/:/current_density',
            'layout': {
                "showlegend": True,
                'yaxis': {
                    "fixedrange": False},
                'xaxis': {
                    "fixedrange": False}},
        },
            {
                'label': 'Current over Voltage',
                'x': 'cycles/:/voltage',
                'y': 'cycles/:/current',
                'layout': {
                    "showlegend": True,
                    'yaxis': {
                        "fixedrange": False},
                    'xaxis': {
                        "fixedrange": False}},
        }]
    )

    def normalize(self, archive, logger):
        if self.data_file:
            with archive.m_context.raw_file(self.data_file, "rt") as f:
                if os.path.splitext(self.data_file)[-1] == ".DTA":
                    from nomad_chemical_energy.schema_packages.file_parser.gamry_parser import get_header_and_data
                    from baseclasses.helper.archive_builder.gamry_archive import get_cv_properties, \
                        get_voltammetry_archive
                    metadata, data = get_header_and_data(f)
                    curve_key = get_curve_tag(metadata.get("METHOD"), self.function)
                    get_voltammetry_archive(data, metadata, curve_key, self, multiple=True)
                    if not self.properties:
                        self.properties = get_cv_properties(metadata)

        super(CE_NOME_CyclicVoltammetry, self).normalize(archive, logger)


class CE_NOME_LinearSweepVoltammetry(LinearSweepVoltammetry, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'solution',
                'users', "location", 'end_time', 'steps', 'instruments', 'results', "metadata_file", "control",
                "cycles", "charge", "charge_density"],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "environment",
                    "setup",
                    "samples",
                    "station", "voltage_shift", "resistance"])),
        a_plot=[{
            'label': 'Current Density over Voltage RHE',
            'x': 'voltage_rhe_compensated',
            'y': 'current_density',
            'layout': {
                "showlegend": True,
                'yaxis': {
                    "fixedrange": False},
                'xaxis': {
                    "fixedrange": False}},
        },
            {
                'label': 'Current over Voltage',
                'x': 'voltage',
                'y': 'current',
                'layout': {
                    "showlegend": True,
                    'yaxis': {
                        "fixedrange": False},
                    'xaxis': {
                        "fixedrange": False}},
        }]
    )

    def normalize(self, archive, logger):
        if self.data_file:
            with archive.m_context.raw_file(self.data_file, "rt") as f:
                if os.path.splitext(self.data_file)[-1] == ".DTA":
                    from nomad_chemical_energy.schema_packages.file_parser.gamry_parser import get_header_and_data
                    from baseclasses.helper.archive_builder.gamry_archive import get_lsv_properties, \
                        get_voltammetry_archive
                    metadata, data = get_header_and_data(f)
                    curve_key = get_curve_tag(metadata.get("METHOD"), self.function)
                    get_voltammetry_archive(data, metadata, curve_key, self)
                    if not self.properties:
                        self.properties = get_lsv_properties(metadata)

        super(CE_NOME_LinearSweepVoltammetry, self).normalize(archive, logger)


class CE_NOME_GalvanodynamicSweep(GalvanodynamicSweep, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'solution',
                'users', "location", 'end_time', 'steps', 'instruments', 'results', "metadata_file", "control",
                "cycles", "charge", "charge_density"],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "environment",
                    "setup",
                    "samples",
                    "station", "voltage_shift", "resistance"])),
        a_plot=[{
            'label': 'Current Density over Voltage RHE',
            'x': 'voltage_rhe_compensated',
            'y': 'current_density',
            'layout': {
                "showlegend": True,
                'yaxis': {
                    "fixedrange": False},
                'xaxis': {
                    "fixedrange": False}},
        },
            {
                'label': 'Current over Voltage',
                'x': 'voltage',
                'y': 'current',
                'layout': {
                    "showlegend": True,
                    'yaxis': {
                        "fixedrange": False},
                    'xaxis': {
                        "fixedrange": False}},
        }]
    )

    def normalize(self, archive, logger):
        if self.data_file:
            with archive.m_context.raw_file(self.data_file, "rt") as f:
                if os.path.splitext(self.data_file)[-1] == ".DTA":
                    from nomad_chemical_energy.schema_packages.file_parser.gamry_parser import get_header_and_data
                    from baseclasses.helper.archive_builder.gamry_archive import get_lsg_properties, \
                        get_voltammetry_archive
                    metadata, data = get_header_and_data(f)
                    curve_key = get_curve_tag(metadata.get("METHOD"), self.function)
                    get_voltammetry_archive(data, metadata, curve_key, self)
                    if not self.properties:
                        self.properties = get_lsg_properties(metadata)

        super(CE_NOME_GalvanodynamicSweep, self).normalize(archive, logger)


class CE_NOME_Chronoamperometry(Chronoamperometry, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'solution', 'users', "location", 'end_time', 'steps', 'instruments', 'results',
                "metadata_file", "charge_density", "control", "cycles", "charge", "charge_density"],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "environment",
                    "setup",
                    "samples",
                    "station", "voltage_shift", "resistance"])), a_plot=[
            {
                'label': 'Current', 'x': 'time', 'y': 'current', 'layout': {
                    'yaxis': {
                        "fixedrange": False}, 'xaxis': {
                        "fixedrange": False}}, "config": {
                    "scrollZoom": True, 'staticPlot': False, }},
            {
                'label': 'Current Density', 'x': 'time',
                'y': 'current_density', 'layout': {
                    'yaxis': {
                        "fixedrange": False}, 'xaxis': {
                        "fixedrange": False}}, "config": {
                    "scrollZoom": True, 'staticPlot': False, }}])

    def normalize(self, archive, logger):
        if self.data_file:
            with archive.m_context.raw_file(self.data_file, "rt") as f:
                if os.path.splitext(self.data_file)[-1] == ".DTA":
                    from nomad_chemical_energy.schema_packages.file_parser.gamry_parser import get_header_and_data
                    from baseclasses.helper.archive_builder.gamry_archive import get_ca_properties, \
                        get_voltammetry_archive
                    metadata, data = get_header_and_data(f)
                    curve_key = get_curve_tag(metadata.get("METHOD"), self.function)
                    get_voltammetry_archive(data, metadata, curve_key, self)
                    if not self.properties:
                        self.properties = get_ca_properties(metadata)
        super(CE_NOME_Chronoamperometry, self).normalize(archive, logger)


class CE_NOME_Chronopotentiometry(Chronopotentiometry, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'solution', 'users', "location", 'end_time', 'steps', 'instruments', 'results',
                "metadata_file", "charge_density", "control", "cycles"],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "environment",
                    "setup",
                    "samples",
                    "station", "voltage_shift", "resistance"])), a_plot=[
            {
                'label': 'Voltage', 'x': 'time', 'y': 'voltage', 'layout': {
                    'yaxis': {
                        "fixedrange": False}, 'xaxis': {
                        "fixedrange": False}}, "config": {
                    "scrollZoom": True, 'staticPlot': False, }},
        ])

    def normalize(self, archive, logger):
        if self.data_file:
            with archive.m_context.raw_file(self.data_file, "rt") as f:
                if os.path.splitext(self.data_file)[-1] == ".DTA":
                    from nomad_chemical_energy.schema_packages.file_parser.gamry_parser import get_header_and_data
                    from baseclasses.helper.archive_builder.gamry_archive import get_cp_properties, \
                        get_voltammetry_archive
                    metadata, data = get_header_and_data(f)
                    curve_key = get_curve_tag(metadata.get("METHOD"), self.function)
                    get_voltammetry_archive(data, metadata, curve_key, self)
                    if not self.properties:
                        self.properties = get_cp_properties(metadata)
        super(CE_NOME_Chronopotentiometry, self).normalize(archive, logger)


class CE_NOME_Chronocoulometry(Chronocoulometry, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'solution', 'users', "location", 'end_time', 'steps', 'instruments', 'results',
                "metadata_file", "control", "cycles"],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "environment",
                    "setup",
                    "samples",
                    "station", "voltage_shift", "resistance"])), a_plot=[
            {
                'label': 'Charge and current density',
                'x': 'time',
                'y': ['./current_density', './charge_density'],
                'layout': {
                    "showlegend": True,
                    'yaxis': {
                        "fixedrange": False},
                    'xaxis': {
                        "fixedrange": False}},
            }])

    def normalize(self, archive, logger):
        if self.data_file:
            with archive.m_context.raw_file(self.data_file, "rt") as f:
                if os.path.splitext(self.data_file)[-1] == ".DTA":
                    from nomad_chemical_energy.schema_packages.file_parser.gamry_parser import get_header_and_data
                    from baseclasses.helper.archive_builder.gamry_archive import get_cc_properties, \
                        get_voltammetry_archive
                    metadata, data = get_header_and_data(f)
                    curve_key = get_curve_tag(metadata.get("METHOD"), self.function)
                    get_voltammetry_archive(data, metadata, curve_key, self)
                    if not self.properties:
                        self.properties = get_cc_properties(metadata)
        super(CE_NOME_Chronocoulometry, self).normalize(archive, logger)


class CE_NOME_OpenCircuitVoltage(OpenCircuitVoltage, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'solution',
                'users', "location", 'end_time', 'steps', 'instruments', 'results', "metadata_file", "charge_density",
                "control", "cycles"],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "environment",
                    "setup",
                    "samples",
                    "station", "voltage_shift", "resistance"])),
        a_plot=[
            {
                'label': 'Voltage',
                'x': 'time',
                'y': 'voltage',
                'layout': {
                    'yaxis': {
                        "fixedrange": False},
                    'xaxis': {
                        "fixedrange": False}},
            }])

    def normalize(self, archive, logger):
        if self.data_file:
            with archive.m_context.raw_file(self.data_file, "rt") as f:
                if os.path.splitext(self.data_file)[-1] == ".DTA":
                    from nomad_chemical_energy.schema_packages.file_parser.gamry_parser import get_header_and_data
                    from baseclasses.helper.archive_builder.gamry_archive import get_ocv_properties, \
                        get_voltammetry_archive
                    metadata, data = get_header_and_data(f)
                    curve_key = get_curve_tag(metadata.get("METHOD"), self.function)
                    get_voltammetry_archive(data, metadata, curve_key, self)
                    if not self.properties:
                        self.properties = get_ocv_properties(metadata)
        super(CE_NOME_OpenCircuitVoltage, self).normalize(archive, logger)


class CE_NOME_UVvismeasurement(UVvisMeasurement, EntryData, PlotSection):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'solution',
                'users',
                'location',
                'end_time', 'steps', 'instruments', 'results'],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "samples"])))

    measurements = SubSection(
        section_def=UVvisDataConcentration, repeats=True)

    def normalize(self, archive, logger):
        import pandas as pd
        measurements = []

        if self.data_file is not None:
            for data_file in self.data_file:
                is_new_data = True
                for measurement in self.measurements:
                    if data_file == measurement.name:
                        is_new_data = False
                        measurements.append(measurement)
                if is_new_data:

                    datetime_object = None
                    if os.path.splitext(data_file)[-1] not in [".ABS", ".csv"]:
                        continue
                    delimiter = ''
                    if os.path.splitext(data_file)[-1] == ".csv":
                        delimiter = ','
                    if os.path.splitext(data_file)[-1] == ".ABS":
                        delimiter = '  '
                    from baseclasses.helper.archive_builder.uvvis_archive import get_uvvis_concentration_archive
                    with archive.m_context.raw_file(data_file, "rt") as f:
                        data = pd.read_csv(f, delimiter=delimiter, header=None, skiprows=2)
                    measurements.append(get_uvvis_concentration_archive(data, datetime_object, data_file))
            self.measurements = measurements

            fig = go.Figure()
            for measurement in self.measurements:
                measurement.normalize(archive, logger)
                fig.add_traces(go.Scatter(name=measurement.name, x=measurement.wavelength,
                               y=measurement.intensity, mode='lines'))
                fig.add_traces(go.Scatter(name='peaks', x=[measurement.peak_wavelength], y=[
                               measurement.peak_value], mode='markers', line_color='black', showlegend=False))
            fig.update_layout(showlegend=True, xaxis={'fixedrange': False})
            fig.update_layout(xaxis_title=f'Wavelength [{self.measurements[0].wavelength.units}]',
                              yaxis_title='Intensity',
                              title_text='UVvis')
            self.figures = [PlotlyFigure(label='figure 1', figure=fig.to_plotly_json())]

        super(CE_NOME_UVvismeasurement, self).normalize(archive, logger)


class CE_NOME_PhaseFluorometryOxygen(PhaseFluorometryOxygen, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'solution',
                'users',
                'location',
                'end_time', 'steps', 'instruments', 'results'],
            properties=dict(
                order=[
                    "name",
                    "data_file", "environment",
                    "setup",
                    "samples", "electro_chemistry_measurement"
                ])),
        a_plot=[
            {
                'label': 'Oxygen',
                'x': 'time',
                'y': 'oxygen',
                'layout': {
                    'yaxis': {
                        "fixedrange": False},
                    'xaxis': {
                        "fixedrange": False}},
            }])

    def normalize(self, archive, logger):
        if self.data_file:
            try:
                if os.path.splitext(self.data_file)[-1] == ".csv":
                    with archive.m_context.raw_file(self.data_file, "rt") as f:
                        from nomad_chemical_energy.schema_packages.file_parser.pfo_parser import get_pfo_measurement_csv
                        from baseclasses.helper.archive_builder.pfo_archive import get_pfo_archive
                        data = get_pfo_measurement_csv(f)
                        get_pfo_archive(data, self)
                if os.path.splitext(self.data_file)[-1] == ".xlsx":
                    with archive.m_context.raw_file(self.data_file, "rb") as f:
                        from nomad_chemical_energy.schema_packages.file_parser.pfo_parser import get_pfo_measurement_xlsx
                        from baseclasses.helper.archive_builder.pfo_archive import get_pfo_archive_xlsx
                        data = get_pfo_measurement_xlsx(f)
                        get_pfo_archive_xlsx(data, self)

            except Exception as e:
                raise e

        super(CE_NOME_PhaseFluorometryOxygen, self).normalize(archive, logger)


class CE_NOME_PumpRateMeasurement(PumpRateMeasurement, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'solution',
                'users',
                'location',
                'end_time', 'steps', 'instruments', 'results'],
            properties=dict(
                order=[
                    "name",
                    "data_file", "environment",
                    "setup",
                    "samples", "electro_chemistry_measurement"])),
        a_plot=[
            {
                'label': 'Flow Rate Measured',
                'x': 'time',
                'y': ['flow_rate_measured', 'flow_rate_set'],
                'layout': {
                    'yaxis': {
                        "fixedrange": False},
                    'xaxis': {
                        "fixedrange": False}},
            }])

    def normalize(self, archive, logger):
        if self.data_file:
            try:
                with archive.m_context.raw_file(self.data_file, "rt") as f:
                    if os.path.splitext(self.data_file)[-1] == ".csv":
                        from nomad_chemical_energy.schema_packages.file_parser.pumprate_parser import get_pump_rate_measurement_csv
                        from baseclasses.helper.archive_builder.pumprate_archive import get_pump_rate_archive
                        data = get_pump_rate_measurement_csv(f)
                        get_pump_rate_archive(data, self)

            except Exception as e:
                logger.error(e)
        super(CE_NOME_PumpRateMeasurement, self).normalize(archive, logger)


class CE_NOME_TIF_Image(BaseMeasurement, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                "location",
                "is_standard_process",
                'end_time', 'steps', 'instruments', 'results'],
            properties=dict(
                order=[
                    "name",
                    "image",
                    "image_png",
                ])))
    image = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))

    image_preview = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))

    def normalize(self, archive, logger):
        import hyperspy.api as hs
        import tempfile

        self.method = "Vis Image"
        if self.image:
            with archive.m_context.raw_file(self.image, "rb") as f:
                image_file_name = f.name
                file_content = f.read()

                with tempfile.NamedTemporaryFile(delete=False, suffix=".tif") as temp_file:
                    temp_file.write(file_content)
                    temp_file_path = temp_file.name
                tif_file = hs.load(temp_file_path)

            png_file = os.path.splitext(image_file_name)[0] + '.png'
            tif_file.save(png_file, overwrite=True)
            self.image_preview = os.path.basename(png_file)

        super(CE_NOME_TIF_Image, self).normalize(archive, logger)


class CE_NOME_Massspectrometry(Massspectrometry, EntryData, PlotSection):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                "location",
                'end_time', 'steps', 'instruments', 'results'],
            properties=dict(
                order=[
                    "name",
                    "data_file"]))
    )

    def normalize(self, archive, logger):
        # from datetime import datetime
        # self.method = "Vis Image"
        if self.data_file:
            with archive.m_context.raw_file(self.data_file, "rt") as f:
                from nomad_chemical_energy.schema_packages.file_parser.spectra_international_parser import parse_spectrum
                from baseclasses.helper.archive_builder.massspectrometry_archive import get_masssectromentry_archive

                metadata, data = parse_spectrum(f)
            self.settings, self.data = get_masssectromentry_archive(metadata, data)
            self.recipe = metadata.get("Recipe Name")
            self.time = data.Time.to_list()
            self.datetime = data.Time.iloc[0]

        if self.data and self.time:
            import plotly.graph_objects as go
            result_figures = []

            fig = go.Figure()
            for d in self.data:
                fig.add_trace(
                    go.Scatter(
                        x=[r.strftime("%H:%M:%S") if r else None for r in self.time],
                        y=d.spectrum_data,
                        name=d.chemical_name
                    )
                )

            layout_settings = {
                'title': 'Mass spectra over time',
                'xaxis': {
                    'title': 'Time',
                    'gridcolor': "lightgrey"
                },
                'yaxis': {
                    'title': 'Data',
                    'showgrid': True,
                    'gridcolor': "lightgrey",
                    'tickformat': '.2e',
                },
                'showlegend': True,
                'legend': {
                    'x': 0.02,
                    'y': 0.98
                },
                'plot_bgcolor': "white",
                'margin': {
                    'b': 100,
                    'r': 90
                }
            }
            fig.update_layout(layout_settings)
            result_figures.append(
                PlotlyFigure(
                    label='Mass spectra over time',
                    index=0,
                    figure=fig.to_plotly_json()
                )
            )
            self.figures = result_figures

        super(CE_NOME_Massspectrometry, self).normalize(archive, logger)


# %%####################################### Generic Entries


class CE_NOME_Process(BaseProcess, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                "location",
                "is_standard_process",
                'end_time', 'steps', 'instruments', 'results'],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "batch",
                    "station"])))

    data_file = Quantity(
        type=str,
        shape=['*'],
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))


# class CE_NOME_Deposition(WetChemicalDeposition, EntryData):
#     m_def = Section(
#         a_eln=dict(
#             hide=[
#                 'lab_id',
#                 'users',
#                 "is_standard_process",
#                 "location",
#                 'end_time',  'steps', 'instruments', 'results'],
#             properties=dict(
#                 order=[
#                     "name",
#                     "data_file",
#                     "function",
#                     "batch",
#                     "samples"])))

#     data_file = Quantity(
#         type=str,
#         shape=['*'],
#         a_eln=dict(component='FileEditQuantity'),
#         a_browser=dict(adaptor='RawFileAdaptor'))


class CE_NOME_Measurement(BaseMeasurement, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'users', "location", 'end_time', 'steps', 'instruments', 'results'],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "samples"])))

    data_file = Quantity(
        type=str,
        shape=['*'],
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))


class CE_NOME_UVvisConcentrationDetection(UVvisConcentrationDetection, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'location', 'end_time', 'method', 'steps', 'outputs'],
            properties=dict(
                order=['name', 'uvvis_measurement', 'material_name', 'minimum_peak_value', 'maximum_peak_value',
                       'slope', 'intercept', 'blank_substraction'])))


# %%####################################### Analysis


class CE_NOME_CPAnalysis(CPAnalysis, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['location', 'lab_id', 'description', 'method', 'steps'],
            properties=dict(
                order=['name'])))


m_package.__init_metainfo__()
