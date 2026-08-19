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


def get_quantity_with_unit(value, unit):
    return None if value is None else value * ureg(unit)


def split_catalyst_mxene_phases(material: str) -> tuple[list[str], list[str]]:
    """
    Extract non-MXene and MXene phases from a material string.

    Returns
    -------
    (non_mxene_phases, mxene_phases)
    """

    # Remove percentages, e.g. 75%, 25%, 50%
    s = re.sub(r'\d+(?:\.\d+)?%', '', material)

    # Normalize common separators
    s = re.sub(r'[@/,+-]', ' ', s)

    # Find chemical-formula-like tokens
    tokens = re.findall(
        r'[A-Z][a-z]?(?:\d+(?:\.\d+)?)?(?:[A-Z][a-z]?(?:\d+(?:\.\d+)?)?)*', s
    )

    # MXene formulas: M_(n+1)X_n
    # Examples: Ti3C2, V2C, Nb2C, Ti3CN
    mxene_pattern = re.compile(
        r'^(?:Ti|V|Nb|Mo|Cr|Zr|Hf|Ta|W)'
        r'\d+(?:C|N|CN|C[N]?)(?:\d+)?$'
    )

    mxenes = []
    non_mxenes = []

    for token in tokens:
        if mxene_pattern.match(token):
            mxenes.append(token)
        else:
            non_mxenes.append(token)

    # Remove duplicates while preserving order
    non_mxenes = list(dict.fromkeys(non_mxenes))
    mxenes = list(dict.fromkeys(mxenes))

    return non_mxenes, mxenes


def get_components(data_dict, logger):
    catalyst_phases, mxene_phases = split_catalyst_mxene_phases(
        data_dict.get('solutes')
    )
    if not catalyst_phases or not mxene_phases:
        logger.warn(
            'Could not split given material into catalyst and mxene. Please check your "Solutes" in the metadata excel.'
        )
    components = []
    if catalyst_phases:
        for formula in catalyst_phases:
            component_catalyst = PureSubstanceComponent(
                pure_substance=PureSubstanceSection(molecular_formula=formula)
            )
            if data_dict.get('solute masses'):
                component_catalyst.mass = (
                    data_dict.get('solute masses', 0) * ureg('mg'),
                )
            components.append(component_catalyst)
    if mxene_phases:
        for formula in mxene_phases:
            component_mxene = PureSubstanceComponent(
                pure_substance=PureSubstanceSection(molecular_formula=formula)
            )
            if data_dict.get('mass mxene'):
                # this only exisits in old version of excel
                component_mxene.mass = data_dict.get('mass mxene', 0) * ureg('µg')
            if data_dict.get('mxene addition'):
                # this only exists in new version of excel
                component_mxene.mass_fraction = data_dict.get('mxene addition', 0) / 100
            components.append(component_mxene)
    return components


def get_solvents(ink_composition: str, logger) -> list[str]:
    ink_composition_list = []
    ink_list = [
        solvent.strip() for solvent in ink_composition.split(',') if solvent.strip()
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
    return ink_composition_list


def map_sample(entry, data_dict, setup_type, logger):
    entry.name = data_dict.get('active material common name')
    entry.preparation_date = data_dict.get('preparation date')
    entry.origin = data_dict.get('preparing person')
    entry.lab_id = data_dict.get('sample id')

    entry.components = get_components(data_dict, logger)

    entry.drying_temperature = data_dict.get('drying temperature')
    entry.description = data_dict.get('notes (electrode preparation)')

    entry.substrate = SubstrateProperties(
        substrate_type=data_dict.get('substrate type'),
        substrate_cleaning=data_dict.get('substrate cleaning'),
    )

    entry.active_area = get_quantity_with_unit(
        data_dict.get('working electrode: active area'), 'cm^2'
    )
    ink_composition_list = get_solvents(
        (data_dict.get('solvent volumes', '') or ''), logger
    )
    mass = data_dict.get('total mass of hybrid catalyst on electrode after drying')
    deposition_notes = data_dict.get('notes (deposition method)', '')
    entry.deposition = Deposition(
        catalyst_layer_deposition_method=data_dict.get(
            'catalyst layer deposition method'
        ),
        ink_composition=ink_composition_list,
        deposition_volume=get_quantity_with_unit(
            data_dict.get('deposition volume'), 'µl'
        ),
        catalyst_loading=get_quantity_with_unit(
            data_dict.get('catalyst loading'), 'mg/cm^2'
        ),
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
    entry.torque = get_quantity_with_unit(data_dict.get('torque'), 'newton * meter')
    entry.flow_rate = get_quantity_with_unit(data_dict.get('flow rate'), 'mL / minute')
    entry.system_temperature = data_dict.get('system temperature')
    entry.peristaltic_pump_info = find_sample_by_id(
        archive, data_dict.get('peristaltic pump info')
    )
    entry.description = data_dict.get('notes')
    entry.anode = get_electrode(data_dict, 'anode', logger)
    entry.cathode = get_electrode(data_dict, 'cathode', logger)


def get_electrode(data_dict, electrode_type, logger):
    prefix = f'{electrode_type} ' if electrode_type in ['anode', 'cathode'] else ''
    electrode = CE_NESD_Electrode()
    electrode.catalyst = data_dict.get(f'{prefix}catalyst') or data_dict.get(
        'catalyst material'
    )
    electrode.gasket_material = PubChemPureSubstanceSectionCustom(
        name=data_dict.get(f'{prefix}gasket type'), load_data=False
    )
    electrode.gasket_thickness = get_quantity_with_unit(
        data_dict.get(f'{prefix}gasket thickness'), 'mm'
    )
    electrode.ionomer = data_dict.get(f'{prefix}ionomer')
    electrode.membrane = data_dict.get(f'{prefix}membrane')
    electrode.catalyst_layer_thickness = get_quantity_with_unit(
        data_dict.get(f'{prefix}catalyst layer thickness'), 'nm'
    )
    electrode.description = data_dict.get(f'notes ({electrode_type})')
    electrode.substrate = SubstrateProperties(
        substrate_type=data_dict.get(f'{prefix}substrate type'),
        substrate_cleaning=data_dict.get(f'{prefix}substrate cleaning'),
    )

    if electrode_type == 'anode':
        electrolyte_type = 'anolyte'
    elif electrode_type == 'cathode':
        electrolyte_type = 'catholyte'
    else:
        electrolyte_type = 'electrolyte'
    electrode.electrolyte = get_environment(data_dict, electrolyte_type)

    solvent_field = (
        f'{prefix}ink composition'
        if electrode_type in ['anode', 'cathode']
        else 'solvent volumes'
    )
    electrode.preparation_method = Deposition(
        catalyst_layer_deposition_method=data_dict.get(
            f'{prefix}catalyst layer preparation method'
        ),
        ink_composition=get_solvents(data_dict.get(solvent_field, '') or '', logger),
        deposition_tool=data_dict.get(f'{prefix}deposition tool'),
        deposition_recipe=data_dict.get(f'{prefix}deposition recipe'),
        catalyst_loading=get_quantity_with_unit(
            data_dict.get(f'{prefix}catalyst loading'), 'mg/cm^2'
        ),
        binder=data_dict.get('binder'),
    )
    if electrode_type == 'half-cell':
        electrode.components = get_components(data_dict, logger)
        electrode.datetime = data_dict.get('preparation date')
        electrode.description = (
            (f'{data_dict.get("notes")}<br><br>' if data_dict.get('notes') else '')
            + f'Preparing Person: {data_dict.get("preparing person")}<br><br>'
            + f'Experimentalist: {data_dict.get("experimentalist: name")}<br><br>'
            + f'iR compensation: {data_dict.get("ir compensation")}%<br><br>'
            + f'Torque: {data_dict.get("torque")} Nm <br><br>'
            + f'Gas flow {data_dict.get("gas")}: {data_dict.get("gas flow rate")} ml/minute <br><br>'
        )
    return electrode


def get_environment(data_dict, electrolyte_type='electrolyte'):
    entry = CE_NESD_Electrolyte()
    entry.solvent = PubChemPureSubstanceSectionCustom(name='H2O', load_data=False)
    entry.substances = [
        SubstanceWithConcentration(
            name=data_dict.get(f'{electrolyte_type}: substance'),
            concentration_mmol_per_l=get_quantity_with_unit(
                data_dict.get(f'{electrolyte_type}: concentration'), 'mol/L'
            ),
            substance=PubChemPureSubstanceSectionCustom(
                name=data_dict.get(f'{electrolyte_type}: substance'), load_data=False
            ),
        )
    ]
    entry.ph_value = data_dict.get(f'{electrolyte_type}: ph')
    if data_dict.get(f'{electrolyte_type}: purging time') is not None:
        entry.purging = Purging(
            time=data_dict.get(f'{electrolyte_type}: purging time') * ureg('minute'),
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
