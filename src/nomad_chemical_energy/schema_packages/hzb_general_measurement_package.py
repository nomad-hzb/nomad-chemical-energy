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

from nomad.metainfo import (
    SchemaPackage,
    Section)
from nomad.datamodel.data import EntryData

from baseclasses.chemical_energy import (
    GeneralMeasurement,
)

m_package = SchemaPackage()

# %% ####################### Entities


class HZB_GeneralMeasurement(GeneralMeasurement, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'location', 'steps', 'atmosphere', 'instruments', 'results'],
            properties=dict(
                order=[])),
    )

    def normalize(self, archive, logger):
        super(HZB_GeneralMeasurement, self).normalize(archive, logger)


m_package.__init_metainfo__()