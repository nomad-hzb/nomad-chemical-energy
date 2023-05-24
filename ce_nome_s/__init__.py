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

# from nomad.units import ureg
from nomad.metainfo import (
    Package,
    Quantity,
    Section)
from nomad.datamodel.data import EntryData

from nomad.datamodel.metainfo.eln import Substance

from baseclasses import (
    ProcessOnSample, MeasurementOnSample, Deposition
)

from baseclasses.characterizations import (
    XASFluorescence, XASTransmission
)

from baseclasses.solar_energy import UVvisMeasurement

from baseclasses.chemical_energy import (
    CENOMESample, Electrode, Electrolyte, ElectroChemicalCell,
    ElectroChemicalSetup, Environment,
    get_next_project_sample_number,
    CyclicVoltammetry,
    Chronoamperometry, ChronoamperometryMultiple,
    Chronocoulometry,
    OpenCircuitVoltage,
    ElectrochemicalImpedanceSpectroscopy,
    ElectrochemicalImpedanceSpectroscopyMultiple,
    PreparationProtocol
)

m_package2 = Package(name='CE-NOME')


def create_archive(entity, archive, file_name):
    import json
    if not archive.m_context.raw_path_exists(file_name):
        entity_entry = entity.m_to_dict(with_root_def=True)
        with archive.m_context.raw_file(file_name, 'w') as outfile:
            json.dump({"data": entity_entry}, outfile)
        archive.m_context.process_updated_raw_file(file_name)

# %% ####################### Entities


class CE_NOME_Sample(CENOMESample, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=["users"],
            properties=dict(
                order=[
                    "name",
                    "lab_id", "chemical_composition_or_formulas",
                    "id_of_preparation_protocol"])),
        label_quantity='sample_id')


class CE_NOME_Electrode(Electrode, EntryData):
    m_def = Section(
        a_eln=dict(hide=['users', 'origin'],
                   properties=dict(
            order=[
                "name", "lab_id",
                "chemical_composition_or_formulas"
            ]))
    )


class CE_NOME_Electrolyte(Electrolyte, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'users',
                'origin'],
            properties=dict(
                editable=dict(
                    exclude=["chemical_composition_or_formulas"]),
                order=[
                    "name",
                    "lab_id",
                    "chemical_composition_or_formulas",
                    "ph_value",
                    "solvent"])))


class CE_NOME_Environment(Environment, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'users',
                'origin'],
            properties=dict(
                editable=dict(
                    exclude=["chemical_composition_or_formulas"]),
                order=[
                    "name",
                    "lab_id",
                    "chemical_composition_or_formulas",
                    "ph_value",
                    "solvent"])))


class CE_NOME_Chemical(Substance, EntryData):
    m_def = Section(
        a_eln=dict(hide=['users', 'origin']))


class CE_NOME_ElectroChemicalCell(ElectroChemicalCell, EntryData):
    m_def = Section(
        a_eln=dict(hide=['users', 'origin'],
                   properties=dict(
            order=[
                "name",
                "lab_id",
                "chemical_composition_or_formulas",
                "working_electrode",
                "reference_electrode",
                "counter_electrode",
                "electrolyte"
            ])),
    )


class CE_NOME_ElectroChemicalSetup(ElectroChemicalSetup, EntryData):
    m_def = Section(
        a_eln=dict(hide=['users', 'origin'],
                   properties=dict(
            order=[
                "name",
                "lab_id",
                "chemical_composition_or_formulas",
                "setup",
                "reference_electrode",
                "counter_electrode",
            ])),
    )


class CE_NOME_Batch(CENOMESample, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['users'],
            properties=dict(
                order=[
                    "name",
                    "lab_id",
                    "chemical_composition_or_formulas",
                    "id_of_preparation_protocol",
                    "number_of_samples",
                    "create_samples"
                ])))

    number_of_samples = Quantity(
        type=np.dtype(np.int64),
        default=0,
        a_eln=dict(
            component='NumberEditQuantity'
        ))

    create_samples = Quantity(
        type=bool,
        default=False,
        a_eln=dict(component='BoolEditQuantity')
    )

    def normalize(self, archive, logger):
        super(CE_NOME_Batch, self).normalize(archive, logger)

        if self.number_of_samples > 0 and self.create_samples:
            self.create_samples = False

            from nomad.search import search

            query = {
                'results.eln.lab_ids': archive.results.eln.lab_ids[1]
            }

            search_result = search(
                owner='all',
                query=query,
                user_id=archive.metadata.main_author.user_id)

            next_project_sample_number = get_next_project_sample_number(
                search_result.data, archive.metadata.entry_id)

            for sample_idx in range(self.number_of_samples):
                ce_nome_sample = CE_NOME_Sample(
                    origin=self.origin if self.origin is not None else None,
                    chemical_composition_or_formulas=self.chemical_composition_or_formulas if self.chemical_composition_or_formulas is not None else None,
                    sample_id=self.sample_id if self.sample_id is not None else None,
                    id_of_preparation_protocol=self.id_of_preparation_protocol if self.id_of_preparation_protocol is not None else None,
                    date_of_disposal=self.date_of_disposal if self.date_of_disposal is not None else None,
                    components=self.components if self.components is not None else None,
                    project_name_long=self.project_name_long if self.project_name_long is not None else None,
                    datetime=self.datetime if self.datetime is not None else None,
                    description=self.description if self.description is not None else None,
                    name=f'{self.name} {next_project_sample_number + sample_idx}' if self.name is not None else None,
                )

                if ce_nome_sample.sample_id is not None:
                    ce_nome_sample.sample_id.project_sample_number = next_project_sample_number + sample_idx

                file_name = f'{self.name.replace(" ","_")}_{next_project_sample_number+sample_idx}.archive.json'
                create_archive(ce_nome_sample, archive, file_name)


class CE_NOME_PreparationProtocol(PreparationProtocol, EntryData):
    m_def = Section(
        a_eln=dict(hide=['users'],
                   properties=dict(
            order=[
                "name",
                "data_file",
                "lab_id"])),
    )

# %%####################################### Measurements


class Bessy2_KMC2_XASFluorescence(XASFluorescence, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users', "location", "end_time"],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "samples"])))


class Bessy2_KMC2_XASTransmission(XASTransmission, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'solution',
                'users', "location", "end_time"],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "samples"])))


class CE_NOME_ElectrochemicalImpedanceSpectroscopy(
        ElectrochemicalImpedanceSpectroscopy, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'solution',
                'users', "location", "end_time", "metadata_file"],
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


class CE_NOME_ElectrochemicalImpedanceSpectroscopy_Multiple(
        ElectrochemicalImpedanceSpectroscopyMultiple, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'solution',
                'users', "location", "end_time"],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "environment",
                    "setup",
                    "samples",
                    "station"])),
    )


class CE_NOME_CyclicVoltammetry(CyclicVoltammetry, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'solution',
                'users', "location", "end_time", "metadata_file"],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "environment",
                    "setup",
                    "samples",
                    "station"])),
        a_plot=[{
            'label': 'Current Density over Voltage RHE',
            'x': 'cycles/:/voltage_rhe',
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
        }])


class CE_NOME_Chronoamperometry(Chronoamperometry, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'solution', 'users', "location", "end_time", "metadata_file"],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "environment",
                    "setup",
                    "samples",
                    "station"])), a_plot=[
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


class CE_NOME_Chronoamperometry_Multiple(ChronoamperometryMultiple, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'solution', 'users', "location", "end_time"],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "environment",
                    "setup",
                    "samples",
                    "station"])))


class CE_NOME_Chronocoulometry(Chronocoulometry, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'solution', 'users', "location", "end_time", "metadata_file"],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "environment",
                    "setup",
                    "samples",
                    "station"])), a_plot=[
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


class CE_NOME_OpenCircuitVoltage(OpenCircuitVoltage, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'solution',
                'users', "location", "end_time", "metadata_file"],
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
                'label': 'Voltage',
                'x': 'time',
                'y': 'voltage',
                'layout': {
                    'yaxis': {
                        "fixedrange": False},
                    'xaxis': {
                        "fixedrange": False}},
            }])


class CE_NOME_UVvismeasurement(UVvisMeasurement, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'solution',
                'users',
                'location',
                'end_time'],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "samples"])))

# %%####################################### Generic Entries


class CE_NOME_Process(ProcessOnSample, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                "location",
                "is_standard_process",
                "end_time"],
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


class CE_NOME_Deposition(Deposition, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                "is_standard_process",
                "location",
                "end_time"],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "function",
                    "batch",
                    "samples"])))

    data_file = Quantity(
        type=str,
        shape=['*'],
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))


class CE_NOME_Measurement(MeasurementOnSample, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'users', "location", "end_time"],
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
