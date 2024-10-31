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
    TGA,
    XPS,
    XRD,
    XRF,
    XRR,
    Ellipsometry,
    EllipsometryLibrary,
    XPSLibrary,
    XRDLibrary,
    XRFLibrary,
    XRRLibrary,
)

# from nomad_measurements.xrd import XRayDiffraction
from baseclasses.characterizations.electron_microscopy import SEM_Microscope_Merlin
from nomad.datamodel.data import EntryData
from nomad.metainfo import SchemaPackage, Section

m_package = SchemaPackage()

# %% ####################### Entities

# %% Microscopy


class HZB_SEM_Merlin(SEM_Microscope_Merlin, EntryData):
    m_def = Section(
        a_eln=dict(hide=['lab_id',
                         'users',
                         "location",
                         'end_time', 'steps', 'instruments', 'results', "detector_data_folder", "external_sample_url"],
                   properties=dict(
                       order=[
                           "name",
                           "detector_data",
                           "samples"])))


# %%
class HZB_Ellipsometry(Ellipsometry, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                "location",
                'end_time', 'steps', 'instruments', 'results',
                "identifier"],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "samples"])))


class HZB_Ellipsometry_Library(EllipsometryLibrary, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                "location",
                'end_time', 'steps', 'instruments', 'results',
                "identifier"],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "samples"])))


class HZB_XRR(XRR, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                "location",
                'end_time', 'steps', 'instruments', 'results',
                "identifier"],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "samples"])))

    def normalize(self, archive, logger):
        super().normalize(archive, logger)


class HZB_XRR_Library(XRRLibrary, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                "location",
                'end_time', 'steps', 'instruments', 'results',
                "identifier"],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "samples"])))

    def normalize(self, archive, logger):
        super().normalize(archive, logger)


class HZB_XRF(XRF, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                "location",
                'end_time', 'steps', 'instruments', 'results',
                "metadata_file",
                "shifted_data",
                "identifier"],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "samples"])))

    def normalize(self, archive, logger):
        super().normalize(archive, logger)


class HZB_XRF_Library(XRFLibrary, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                "location",
                'end_time', 'steps', 'instruments', 'results',
                "metadata_file",
                "shifted_data",
                "identifier"],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "samples"])))

    def normalize(self, archive, logger):
        super().normalize(archive, logger)


class HZB_XRD(XRD, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                "location",
                'end_time', 'steps', 'instruments', 'results',
                "metadata_file",
                "shifted_data",
                "identifier"],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "samples"])),
        a_plot=[
            {
                'x': [
                    'data/angle'],
                'y': [
                    'data/intensity'],
                'layout': {
                    'yaxis': {
                        "fixedrange": False,
                        "title": "Counts"},
                    'xaxis': {
                        "fixedrange": False}}},
        ])

    # def normalize(self, archive, logger):

    #     if self.data_file:
    #         with archive.m_context.raw_file(self.data_file) as f:

    #             if os.path.splitext(self.data_file)[-1] == ".xy" and self.data is None:
    #                 import pandas as pd
    #                 if "Id" in f.readline():
    #                     skiprows = 1
    #                     data = pd.read_csv(f.name, sep=" |\t", header=None, skiprows=skiprows)
    #                 else:
    #                     skiprows = 0
    #                     data = pd.read_csv(f.name, sep=" |\t", header=None, skiprows=skiprows)
    #                 self.data = XRDData(angle=data[0], intensity=data[1])
    #     super(HZB_XRD, self).normalize(archive, logger)


# class HZB_XRD2(XRayDiffraction, EntryData):
#     m_def = Section(
#         a_eln=dict(
#             hide=[
#                 'lab_id',
#                 'users',
#                 "location",
#                 'end_time', 'steps', 'instruments', 'results',
#                 "metadata_file",
#                 "shifted_data",
#                 "identifier"],
#             properties=dict(
#                 order=[
#                     "name",
#                     "data_file",
#                     "samples"])))
#
#     def normalize(self, archive, logger):
#         super(HZB_XRD2, self).normalize(archive, logger)


class HZB_XRD_Library(XRDLibrary, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                "location",
                'end_time', 'steps', 'instruments', 'results',
                "metadata_file",
                "shifted_data",
                "identifier"],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "samples"])))

    def normalize(self, archive, logger):
        super().normalize(archive, logger)


class HZB_XPS(XPS, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                "location",
                'end_time', 'steps', 'instruments', 'results',
                "identifier"],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "samples"])))


class HZB_XPS_Library(XPSLibrary, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                "location",
                'end_time', 'steps', 'instruments', 'results',
                "metadata_file",
                "shifted_data",
                "identifier"],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "samples"])))


class HZB_TGA(TGA, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                "location",
                'end_time', 'steps', 'instruments', 'results',
                "identifier"],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "samples"])))


m_package.__init_metainfo__()
