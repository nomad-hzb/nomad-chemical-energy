# MIT License

# Copyright (c) 2019

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from baseclasses import PubChemPureSubstanceSectionCustom
from baseclasses.chemical_energy import Purging, SubstanceWithConcentration

from nomad_chemical_energy.schema_packages.ce_nesd_package import (
    CE_NESD_Electrolyte,
    CE_NESD_ReferenceElectrode,
    SampleIDCENESD,
)


def get_environment(data_dict):
    entry = CE_NESD_Electrolyte()
    entry.solvent = PubChemPureSubstanceSectionCustom(
        name=data_dict.get('Electrolyte solvent'), load_data=False
    )
    entry.substances = [
        SubstanceWithConcentration(
            name=data_dict.get('Electrolyte substance name'),
            concentration_mmol_per_l=data_dict.get(
                'Electrolyte substance molar concentration'
            ),
            concentration_g_per_l=data_dict.get(
                'Electrolyte substance mass concentration'
            ),
            amount_relative=data_dict.get('Electrolyte substance amount relative'),
            substance=PubChemPureSubstanceSectionCustom(
                name=data_dict.get('Electrolyte substance name'), load_data=False
            ),
        )
    ]
    entry.ph_value = data_dict.get('Electrolyte pH')
    entry.purging = Purging(
        time=data_dict.get('Electrolyte purging time'),
        temperature=data_dict.get('Electrolyte purging temperature'),
        gas=PubChemPureSubstanceSectionCustom(
            name=data_dict.get('Electrolyte purging gas'), load_data=False
        ),
    )
    return entry


def get_reference_electrode(data_dict):
    entry = CE_NESD_ReferenceElectrode()
    entry.name = data_dict.get('Reference electrode: Type')
    entry.standard_potential = data_dict.get('Reference electrode: Standard potential')
    entry.temperature = data_dict.get('Reference electrode: Temperature')
    entry.internal_solution = SubstanceWithConcentration(
        name=data_dict.get('Reference electrode: Type'),
        concentration_mmol_per_l=data_dict.get(
            'Reference electrode: Internal solution concentration'
        ),
        substance=PubChemPureSubstanceSectionCustom(
            name=data_dict.get('Reference electrode: Internal solution substance'),
            load_data=False,
        ),
    )
    return entry


def map_setup(entry, data_dict):
    entry.origin = data_dict.get('Experimentalist: Name')
    if data_dict.get('Date'):
        entry.datetime = data_dict.get('Date')

    entry.environment = get_environment(data_dict)
    entry.ir_compensation = data_dict.get('iR compensation') / 100

    entry.setup = data_dict.get('Electrode configuration')
    # TODO revisit when reference electrodes in the lab get ids (then link ref and counter electrodes here)
    # entry.reference_electrode_subsection = get_reference_electrode(data_dict)
    # data_dict.get('Counter electrode')

    entry.setup_id = SampleIDCENESD(owner=data_dict.get('Experimentalist: Name'))


def map_sample(entry, data_dict):
    entry.description = data_dict.get('Working electrode')
    entry.active_area = data_dict.get('Geometric area')
