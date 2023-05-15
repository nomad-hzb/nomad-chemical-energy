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

import os
import numpy as np

# from nomad.units import ureg
from nomad.metainfo import (
    Package,
    Quantity,
    SubSection,
    Section)
from nomad.datamodel.data import EntryData


from baseclasses import (
    ProcessOnSample, MeasurementOnSample, Deposition
)

from baseclasses.chemical import (
    Chemical
)

from baseclasses.characterizations import (
    Raman,
    SPV,
    SEM,
    TEM,
    SXM,
    XAS,
    XPEEM,
    InfraredSpectroscopy
)


from baseclasses.chemical_energy import (
    Cleaning, SolutionCleaning,
    DiamondSample,
    CENSLISample,
    WaterBath,
    Dropcast,
    CyclicVoltammetry,
    Chronoamperometry,
    OpenCircuitVoltage,
    OpticalMicorscopy,
    PhotoCurrent,
    ConstantPotential
)

m_package1 = Package(name='CE-NSLI')


def create_archive(entity, archive, file_name):
    import json
    if not archive.m_context.raw_path_exists(file_name):
        entity_entry = entity.m_to_dict(with_root_def=True)
        with archive.m_context.raw_file(file_name, 'w') as outfile:
            json.dump({"data": entity_entry}, outfile)
        archive.m_context.process_updated_raw_file(file_name)

# %% ####################### Entities


class CE_NSLI_Chemical(Chemical, EntryData):
    m_def = Section(
        a_eln=dict(hide=['lab_id', 'users']))


class CE_NSLI_Graphene(Chemical, EntryData):
    m_def = Section(
        a_eln=dict(hide=['lab_id', 'users']))


class CE_NSLI_Sample(CENSLISample, EntryData):
    m_def = Section(
        a_eln=dict(hide=['users']),
        label_quantity='sample_id'
    )


class CE_NSLI_DiamondSample(DiamondSample, EntryData):
    m_def = Section(
        a_eln=dict(hide=['users']),
        label_quantity='sample_id'
    )

# %% ####################### Cleaning


class CE_NSLI_UltrasoniceBath(Cleaning, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'users', "location", "end_time"]))

    cleaning = SubSection(
        section_def=SolutionCleaning, repeats=True)


# %% ##################### Layer Deposition


class CE_NSLI_WaterBath(WaterBath, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'users', "location", "end_time"]))


class CE_NSLI_Dropcast(Dropcast, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'users', "location", "end_time"]))


# %%####################################### Measurements


class CE_NSLI_CyclicVoltammetry(CyclicVoltammetry, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                "location",
                "end_time",
                "working_electrode",
                "counter_electrode",
                "reference_electrode",
                "electrolyte"]),
        a_plot=[
            {
                'label': 'Current',
                'x': 'voltage',
                'y': 'current',
                'layout': {
                    'yaxis': {
                        "fixedrange": False},
                    'xaxis': {
                        "fixedrange": False}},
            }])


class CE_NSLI_Chronoamperometry(Chronoamperometry, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                "location",
                "end_time",
                "working_electrode",
                "counter_electrode",
                "reference_electrode",
                "electrolyte"]),
        a_plot=[
            {
                'label': 'Current',
                'x': 'time',
                'y': 'current',
                'layout': {
                    'yaxis': {
                        "fixedrange": False},
                    'xaxis': {
                        "fixedrange": False}},
                "config": {
                    "scrollZoom": True,
                    'staticPlot': False,
                }}])


class CE_NSLI_OpenCircuitVoltage(OpenCircuitVoltage, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                "location",
                "end_time",
                "working_electrode",
                "counter_electrode",
                "reference_electrode",
                "electrolyte"]),
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


class CE_NSLI_ConstantPotential(ConstantPotential, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'users', "location", "end_time"]))


class CE_NSLI_RamanSpectroscopy(Raman, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'users', "location", "end_time"]),
        a_plot=[
            {
                'label': 'Intensity',
                'x': ['raman_shift', 'peaks_raman'],
                'y': ['intensity', 'peaks_intensity'],
                'layout': {'yaxis': {'type': 'lin'}},
                "lines": [
                    {
                        "mode": "lines",
                        "marker": {
                            "color": "rgb(40, 80, 130)"
                        }
                    },
                    {
                        "mode": "markers",
                        "line": {
                            "color": "rgb(100, 0, 0)"
                        }
                    }
                ]
            }]
    )


class CE_NSLI_InfraredSpectroscopy(InfraredSpectroscopy, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'users', "location", "end_time"]),
        a_plot=[
            {
                'label': 'Absorbance',
                'x': 'wave_number',
                'y': 'absorbance',
                'layout': {'yaxis': {'type': 'lin'}},
            }])


class CE_NSLI_XAS(XAS, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'users', "location", "end_time"]))


class CE_NSLI_OpticalMicroscopy(OpticalMicorscopy, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'users', "location", "end_time"]))


class CE_NSLI_SEM(SEM, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'users', "location", "end_time"]))


class CE_NSLI_TEM(TEM, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'users', "location", "end_time"]))


class CE_NSLI_SXM(SXM, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'users', "location", "end_time"]))


class CE_NSLI_XPEEM(XPEEM, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'users', "location", "end_time"]))


class CE_NSLI_Photocurrent(PhotoCurrent, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'users', "location", "end_time"]), a_plot=[
            {
                'label': 'Energy', 'x': 'energy', 'y': 'voltage', 'layout': {
                    'yaxis': {
                        "fixedrange": False}, 'xaxis': {
                        "fixedrange": False}}, "config": {
                    "scrollZoom": True}}])

    def normalize(self, archive, logger):
        super(CE_NSLI_Photocurrent, self).normalize(archive, logger)

        electro_measurements = {}
        if self.data_files and len(self.data_files) > 0:
            for data_file in self.data_files:
                try:
                    with archive.m_context.raw_file(data_file) as f:
                        data_file_name = os.path.basename(f.name)
                        file_name_split = os.path.splitext(data_file_name)
                        if file_name_split[-1] == ".mpt":
                            file_name = f'{file_name_split[0]}.archive.json'
                            split_file_name = file_name_split[0].split("_")
                            technique_number = int(split_file_name[-3])
                            entity = None
                            if split_file_name[-2] == "CA":
                                entity = CE_NSLI_Chronoamperometry(
                                    data_file=data_file_name,
                                    metadata_file=self.electro_meta_data_file_name if self.electro_meta_data_file_name else None,
                                    samples=self.samples if self.samples else [],
                                    name=file_name_split[0].replace("_", " "))
                            if split_file_name[-2] == "CV":
                                entity = CE_NSLI_CyclicVoltammetry(
                                    data_file=data_file_name,
                                    metadata_file=self.electro_meta_data_file_name if self.electro_meta_data_file_name else None,
                                    samples=self.samples if self.samples else [],
                                    name=file_name_split[0].replace("_", " "))
                            if split_file_name[-2] == "OCV":
                                entity = CE_NSLI_OpenCircuitVoltage(
                                    data_file=data_file_name,
                                    metadata_file=self.electro_meta_data_file_name if self.electro_meta_data_file_name else None,
                                    samples=self.samples if self.samples else [],
                                    name=file_name_split[0].replace("_", " "))
                            if entity:
                                create_archive(entity, archive, file_name)
                                electro_measurements.update(
                                    {technique_number: f'../upload/archive/mainfile/{file_name}#data'})

                except Exception as e:
                    logger.error(e)

        electro_measurements_list = []
        if electro_measurements:
            keys = sorted(electro_measurements.keys())
            for key in keys:
                electro_measurements_list.append(electro_measurements[key])
        self.electro_measurements = electro_measurements_list


class CE_NSLI_SPV(SPV, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'users', "location", "end_time"]),
        a_plot=[
            {
                'label': 'Voltage',
                'x': 'wavelength',
                'y': 'volt',
                'layout': {'yaxis': {'type': 'lin'}},
                "config": {
                    "editable": True,
                    "scrollZoom": True
                }
            }])

# %%####################################### Generic Entries


class CE_NSLI_Process(ProcessOnSample, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'users', "location", "end_time"]))

    data_file = Quantity(
        type=str,
        shape=['*'],
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))


class CE_NSLI_Deposition(Deposition, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'users', "location", "end_time"]))

    data_file = Quantity(
        type=str,
        shape=['*'],
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))


class CE_NSLI_Measurement(MeasurementOnSample, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'users', "location", "end_time"]))

    data_file = Quantity(
        type=str,
        shape=['*'],
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))
