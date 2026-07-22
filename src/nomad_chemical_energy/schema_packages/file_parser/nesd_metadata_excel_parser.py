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
from baseclasses.chemical_energy.cesample import Deposition, Solvent
from baseclasses.helper.utilities import find_sample_by_id
from nomad.datamodel.metainfo.basesections import (
    PureSubstanceComponent,
    PureSubstanceSection,
)
from nomad.units import ureg

from nomad_chemical_energy.schema_packages.ce_nesd_package import (
    CE_NESD_Electrode,
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
    materials = [p.replace('Tx', '') for p in parts if re.search(r'[A-Za-z]', p)]
    return materials


def get_components(data_dict, logger):
    materials = split_catalyst_mxene_materials(data_dict.get('solutes'))
    if len(materials) > 2 or not materials:
        logger.warn(
            'Could not split given material into catalyst and mxene. Please check your "Solutes" in the metadata excel.'
        )
    material_catalyst, material_mxene = (materials + [None, None])[:2]
    component_catalyst = PureSubstanceComponent(
        pure_substance=PureSubstanceSection(molecular_formula=material_catalyst)
    )
    component_mxene = PureSubstanceComponent(
        pure_substance=PureSubstanceSection(molecular_formula=material_mxene)
    )
    if data_dict.get('solute masses'):
        component_catalyst.mass = (data_dict.get('solute masses', 0) * ureg('mg'),)
    if data_dict.get('mass mxene'):
        # this only exisits in old version of excel
        component_mxene.mass = data_dict.get('mass mxene', 0) * ureg('µg')
    if data_dict.get('mxene addition'):
        # this only exists in new version of excel
        component_mxene.mass_fraction = data_dict.get('mass mxene', 0) * ureg('%')
    components = []
    if material_catalyst:
        components.append(component_catalyst)
    if material_mxene:
        components.append(component_mxene)
    return components


def map_sample(entry, data_dict, setup_type, logger):
    entry.name = data_dict.get('active material common name')
    entry.preparation_date = data_dict.get('preparation date')
    entry.origin = data_dict.get('preparing person')
    entry.lab_id = data_dict.get('sample id')

    entry.components = get_components(data_dict, logger)

    entry.drying_temperature = data_dict.get('drying temperature')
    entry.description = data_dict.get('notes (electrode preparation)')

    if setup_type in ['3electrode', 'RDE', 'Half-Cell', 'old_template']:
        entry.substrate = SubstrateProperties(
            substrate_type=data_dict.get('substrate type'),
            substrate_cleaning=data_dict.get('substrate cleaning'),
        )

    if setup_type in ['3electrode', 'RDE', 'old_template']:
        entry.active_area = data_dict.get('working electrode: active area') * ureg(
            'cm^2'
        )
        ink_composition_list = []
        ink_list = [
            solvent.strip()
            for solvent in (data_dict.get('solvent volumes', '') or '').split(',')
            if solvent.strip()
        ]
        pattern = re.compile(r'([\d.]+)\s*(ml|mL)\s*(.+)', re.IGNORECASE)
        for solvent in ink_list:
            m = pattern.match(solvent)
            if not m:
                logger.warn(
                    'Could not split given ink composition into Solvent name + volume.'
                    'Please check your "Solvent Volumes" field in the top part of the metadata excel.'
                )
                continue
            volume = float(m.group(1))
            unit = m.group(2).strip()
            solvent_type = m.group(3).strip()
            ink_composition_list.append(
                Solvent(type=solvent_type, volume=volume * ureg(unit))
            )
        deposition_volume = data_dict.get('deposition volume')
        catalyst_loading = data_dict.get('catalyst loading')
        mass = data_dict.get('total mass of hybrid catalyst on electrode after drying')
        deposition_notes = data_dict.get('notes (deposition method)', '')
        entry.deposition = Deposition(
            catalyst_layer_deposition_method=data_dict.get(
                'catalyst layer deposition method'
            ),
            ink_composition=ink_composition_list,
            deposition_volume=deposition_volume * ureg('µl')
            if deposition_volume is not None
            else None,
            catalyst_loading=catalyst_loading * ureg('mg/cm^2')
            if catalyst_loading is not None
            else None,
            binder=data_dict.get('binder'),
            description=(
                f'Total mass of hybrid catalyst on electrode after drying: {mass}mg <br><br>'
                if mass
                else ''
            )
            + deposition_notes,
        )


def map_electrolyser(entry, data_dict, setup_type, archive, logger):
    entry.name = data_dict.get('active material common name')
    entry.datetime = data_dict.get('preparation date')
    entry.components = get_components(data_dict, logger)
    entry.cell_name = setup_type
    entry.membrane = data_dict.get('membrane')
    entry.torque = (
        data_dict.get('torque') * ureg('newton * meter')
        if data_dict.get('torque') is not None
        else None
    )
    entry.flow_rate = (
        data_dict.get('flow rate') * ureg('mL / min')
        if data_dict.get('flow rate') is not None
        else None
    )
    entry.peristaltic_pump_info = find_sample_by_id(
        archive, data_dict.get('peristaltic pump info')
    )
    entry.description = data_dict.get('notes')
    entry.anode = get_electrode(data_dict, 'anode')
    entry.cathode = get_electrode(data_dict, 'cathode')


def get_electrode(data_dict, electrode_type):
    electrode = CE_NESD_Electrode()
    electrode.catalyst = data_dict.get(f'{electrode_type} catalyst')
    electrode.gasket_material = PubChemPureSubstanceSectionCustom(
        name=data_dict.get(f'{electrode_type} gasket type'), load_data=False
    )
    electrode.gasket_thickness = (
        data_dict.get(f'{electrode_type} gasket thickness') * ureg('mm')
        if data_dict.get(f'{electrode_type} gasket thickness') is not None
        else None
    )
    electrode.ionomer = data_dict.get(f'{electrode_type} ionomer')
    catalyst_thickness = data_dict.get(f'{electrode_type} catalyst layer thickness')
    electrode.catalyst_layer_thickness = (
        catalyst_thickness * ureg('nm') if catalyst_thickness is not None else None
    )
    electrode.description = data_dict.get(f'notes ({electrode_type})')
    electrode.substrate = SubstrateProperties(
        substrate_type=data_dict.get(f'{electrode_type} substrate type'),
        substrate_cleaning=data_dict.get(f'{electrode_type} substrate cleaning'),
    )

    electrolyte_type = 'anolyte' if electrode_type == 'anode' else 'catholyte'
    electrode.electrolyte = get_environment(data_dict, electrolyte_type)

    catalyst_loading = data_dict.get(f'{electrode_type} catalyst loading')
    electrode.preparation_method = Deposition(
        catalyst_layer_deposition_method=data_dict.get(
            f'{electrode_type} catalyst layer preparation method'
        ),
        ink_composition=data_dict.get(f'{electrode_type} ink composition'),
        deposition_tool=data_dict.get(f'{electrode_type} deposition tool'),
        deposition_recipe=data_dict.get(f'{electrode_type} deposition recipe'),
        catalyst_loading=catalyst_loading * ureg('mg/cm^2')
        if catalyst_loading is not None
        else None,
        binder=data_dict.get('binder'),
    )
    return electrode


def get_environment(data_dict, electrolyte_type='electrolyte'):
    entry = CE_NESD_Electrolyte()
    entry.solvent = PubChemPureSubstanceSectionCustom(name='H20', load_data=False)
    entry.substances = [
        SubstanceWithConcentration(
            name=data_dict.get(f'{electrolyte_type}: substance'),
            concentration_mmol_per_l=data_dict.get(
                f'{electrolyte_type}: concentration'
            ),
            substance=PubChemPureSubstanceSectionCustom(
                name=data_dict.get(f'{electrolyte_type}: substance'), load_data=False
            ),
        )
    ]
    entry.ph_value = data_dict.get(f'{electrolyte_type}: ph')
    if data_dict.get(f'{electrolyte_type}: purging time') is not None:
        entry.purging = Purging(
            time=data_dict.get(f'{electrolyte_type}: purging time') * ureg('min'),
            temperature=data_dict.get(f'{electrolyte_type}: purging temperature'),
            gas=PubChemPureSubstanceSectionCustom(
                name=data_dict.get(f'{electrolyte_type}: purging gas'), load_data=False
            ),
        )
    entry.description = data_dict.get(f'{electrolyte_type}: notes')
    return entry


def get_reference_electrode(data_dict):
    entry = CE_NESD_ReferenceElectrode()
    entry.name = data_dict.get('reference electrode: type')
    entry.standard_potential = data_dict.get(
        'reference electrode: standard potential at 25 °c'
    ) * ureg('V')
    entry.temperature = data_dict.get('reference electrode: temperature')
    return entry


def map_setup(entry, data_dict, setup_type, archive):
    entry.setup = setup_type
    entry.origin = data_dict.get('experimentalist: name')
    if data_dict.get('measurement date'):
        entry.datetime = data_dict.get('measurement date')

    potentiostat = find_sample_by_id(archive, data_dict.get('potentiostat model'))
    entry.equipment = [potentiostat] if potentiostat is not None else None
    entry.description = data_dict.get('general information and notes')

    if setup_type != 'AEM_or_PEM':
        entry.environment = get_environment(data_dict)
    entry.ir_compensation = (
        data_dict.get('ir compensation') / 100
        if data_dict.get('ir compensation') is not None
        else None
    )

    if setup_type in ['3electrode', 'RDE', 'old_template']:
        entry.counter_electrode = find_sample_by_id(
            archive, data_dict.get('counter electrode material')
        )
