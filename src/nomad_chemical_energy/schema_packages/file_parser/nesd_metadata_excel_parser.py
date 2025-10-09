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

import re

from baseclasses import PubChemPureSubstanceSectionCustom
from baseclasses.chemical_energy import (
    Purging,
    SubstanceWithConcentration,
    SubstrateProperties,
)
from nomad.datamodel.metainfo.basesections import (
    PureSubstanceComponent,
    PureSubstanceSection,
)
from nomad.units import ureg

from nomad_chemical_energy.schema_packages.ce_nesd_package import (
    CE_NESD_Electrolyte,
    CE_NESD_ReferenceElectrode,
)


def split_catalyst_mxene_materials(material_str):
    # standardize the different separators (-, %, @) to comma
    standardized = re.sub(r'[-%@]', ',', material_str)
    # split by comma or whitespace
    parts = re.split(r'[, ]+', standardized)
    # remove any empty strings
    parts = [p for p in parts if p]
    # keep only strings that contain at least one letter
    materials = [p for p in parts if re.search(r'[A-Za-z]', p)]
    return materials


def map_sample(entry, data_dict, logger):
    entry.name = data_dict.get('Active Material Common Name ')
    entry.active_area = data_dict.get('Working Electrode: active area') * ureg('cm²')

    entry.preparation_date = data_dict.get('Preparation Date')
    entry.origin = data_dict.get('Preparating Person')

    materials = split_catalyst_mxene_materials(
        data_dict.get('Active Material Common Name ')
    )
    if len(materials) > 2 or not materials:
        logger.warn(
            'Could not split given material into catalyst and mxene. Please check your "Active Material Common Name" in the metadata excel.'
        )
    material_catalyst, material_mxene = (materials + [None, None])[:2]
    mass_catalyst = data_dict.get('Mass Catalyst') * ureg('µg')
    mass_mxene = data_dict.get('Mass Mxene') * ureg('µg')

    entry.components = [
        PureSubstanceComponent(
            pure_substance=PureSubstanceSection(molecular_formula=material_catalyst),
            mass=mass_catalyst,
        ),
        PureSubstanceComponent(
            pure_substance=PureSubstanceSection(molecular_formula=material_mxene),
            mass=mass_mxene,
        ),
    ]

    entry.drying_temperature = data_dict.get('Drying temperature')
    entry.description = data_dict.get('Notes')

    entry.substrate = SubstrateProperties(
        substrate_type=data_dict.get('Substrate type'),
        substrate_cleaning=data_dict.get('Substrate Cleaning'),
    )


def get_environment(data_dict):
    entry = CE_NESD_Electrolyte()
    entry.solvent = PubChemPureSubstanceSectionCustom(
        name=data_dict.get('Electrolyte: solvent'), load_data=False
    )
    entry.substances = [
        SubstanceWithConcentration(
            name=data_dict.get('Electrolyte: substance name'),
            concentration_mmol_per_l=data_dict.get(
                'Electrolyte: substance molar concentration'
            ),
            concentration_g_per_l=data_dict.get(
                'Electrolyte: substance mass concentration'
            ),
            amount_relative=data_dict.get('Electrolyte: substance amount relative'),
            substance=PubChemPureSubstanceSectionCustom(
                name=data_dict.get('Electrolyte: substance name'), load_data=False
            ),
        )
    ]
    entry.ph_value = data_dict.get('Electrolyte: pH')
    entry.purging = Purging(
        time=data_dict.get('Electrolyte: purging time'),
        temperature=data_dict.get('Electrolyte: purging temperature'),
        gas=PubChemPureSubstanceSectionCustom(
            name=data_dict.get('Electrolyte: purging gas'), load_data=False
        ),
    )
    return entry


def get_reference_electrode(data_dict):
    entry = CE_NESD_ReferenceElectrode()
    entry.name = data_dict.get('Reference electrode: Type')
    entry.standard_potential = data_dict.get(
        'Reference electrode: Standard potential at 25 °C'
    ) * ureg('V')
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
    if data_dict.get('Measurement Date'):
        entry.datetime = data_dict.get('Measurement Date')

    entry.environment = get_environment(data_dict)
    entry.ir_compensation = (
        data_dict.get('iR compensation') / 100
        if data_dict.get('iR compensation') is not None
        else None
    )

    entry.setup = data_dict.get('Electrode configuration')
    # TODO revisit when reference electrodes in the lab get ids (then link ref and counter electrodes here)
    # entry.reference_electrode_subsection = get_reference_electrode(data_dict)
    # data_dict.get('Counter electrode: Material')
    # data_dict.get('Electrode holder & conductive connection')

    # entry.setup_id = SampleIDCENESD(owner=data_dict.get('Experimentalist: Name'))
