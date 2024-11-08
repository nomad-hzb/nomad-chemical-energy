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
import pandas as pd

import plotly.graph_objs as go
from baseclasses.vapour_based_deposition import (
    MultiTargetSputtering
)
from baseclasses.chemical_energy import Equipment

from nomad.datamodel.data import EntryData
from nomad.datamodel.metainfo.plot import PlotlyFigure, PlotSection

from nomad.metainfo import Quantity, SchemaPackage, Section, SubSection

m_package = SchemaPackage()

# %% ####################### Entities


class TFC_Equipment(Equipment, EntryData):
    m_def = Section(
        a_eln=dict(hide=['users', 'origin', 'elemental_composition',
                         'components'],
                   properties=dict(
                       order=[
                           'name', 'lab_id',
                           'producer', 'location'
                       ]))
    )


# %% ####################### Deposition


class TFC_Sputtering(MultiTargetSputtering, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['layer',
                  'batch', 'present', 'positon_in_experimental_plan',
                  'end_time', 'instruments', 'steps',
                  'location'],
            properties=dict(
                order=['name'])))
    def normalize(self, archive, logger):
        if self.data_file:
            with archive.m_context.raw_file(self.data_file, "rb") as f:
                xls_file = pd.ExcelFile(f)
                if not self.targets:
                    target_df = pd.read_excel(xls_file, sheet_name='Source_Configuration', header=0)
                    from baseclasses.helper.archive_builder.prevac_archive import (
                        get_target_properties,
                    )
                    self.targets = get_target_properties(target_df)
                num_targets = len(self.targets)
                if not self.process_properties:
                    parameters_df = pd.read_excel(xls_file, sheet_name='Parameters', header=1, index_col=0)
                    from baseclasses.helper.archive_builder.prevac_archive import (
                        get_process_properties,
                    )
                    self.process_properties = get_process_properties(parameters_df, num_targets)

        super().normalize(archive, logger)





# %%######################## Measurements
# %%######################## Generic Entries
# %%######################## Analysis


m_package.__init_metainfo__()
