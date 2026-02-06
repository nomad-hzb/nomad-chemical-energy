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

import pandas as pd
from baseclasses.chemical_energy import (
    CENECCElectrode,
    CENECCElectrodeID,
    CENECCElectrodeRecipe,
    GasChromatographyMeasurement,
    GasFEResults,
    NECCExperimentalProperties,
    NECCFeedGas,
    NECCPotentiostatMeasurement,
    PHMeasurement,
    PotentiometryGasChromatographyResults,
    SubstrateProperties,
)
from baseclasses.chemical_energy.neccelectrode import (
    CENECCElectrodeRecipeID,
    Ionomer,
    Solvent,
)
from baseclasses.helper.utilities import get_reference, search_entry_by_id
from nomad.datamodel.metainfo.basesections import CompositeSystemReference


def _round_not_zero(number):
    rounded_num = round(number, 3)
    if rounded_num == 0:
        return number
    return rounded_num


def _process_potentiostat_column(data, column_names):
    for column_name in column_names:
        if column_name in data.columns:
            return data[column_name].dropna().apply(_round_not_zero)
    return None


def _get_clean_dict(d):
    return {
        key: value
        for key, value in d.items()
        if value is not None and value not in (' ', '', {}, []) and not pd.isna(value)
    }


def read_ph_data(data):
    measurement = PHMeasurement()
    if {'pH', 'Date', 'pH Time'}.issubset(data.columns):
        measurement.ph_value = data['pH']
        date_only = pd.to_datetime(data['Date'], errors='coerce').dt.normalize()[0]
        time_only = pd.to_datetime(
            data['pH Time'].astype(str), format='mixed', errors='coerce'
        )
        data['DateTime'] = date_only + (time_only - time_only.dt.normalize())
        measurement.datetime = data['DateTime'].dropna().to_list()
    return measurement


def read_potentiostat_data(data):
    measurement = NECCPotentiostatMeasurement()
    data['time/s'] = pd.to_datetime(data['time/s'], errors='coerce')
    data = data.dropna(subset=['time/s'])
    measurement.datetime = data['time/s'].to_list()

    measurement.current = _process_potentiostat_column(
        data, ['I/mA', '<I/mA>', '<I>/mA']
    )
    measurement.working_electrode_potential = _process_potentiostat_column(
        data, ['Ewe/V', '<Ewe/V>', '<Ewe>/V']
    )
    measurement.counter_electrode_potential = _process_potentiostat_column(
        data, ['Ece/V', '<Ece/V>', '<Ece>/V']
    )
    measurement.ewe_ece_difference = _process_potentiostat_column(
        data, ['Ewe-Ece/V', '<Ewe-Ece/V>', '<Ewe-Ece>/V']
    )
    measurement.capacity = _process_potentiostat_column(data, ['dQ/C'])

    return measurement


def read_thermocouple_data(data, start_time, end_time):
    time_grouping = pd.Timedelta(minutes=3)

    data['DateTime'] = pd.to_datetime(data['Time Stamp Local'].astype(str))
    data['Date'] = pd.to_datetime(data['Date'].astype(str))
    data['DateTime'] = data['Date'] + pd.to_timedelta(
        data['DateTime'].dt.strftime('%H:%M:%S')
    )

    data = data[
        (data['DateTime'] > start_time - time_grouping) & (data['DateTime'] <= end_time)
    ]
    data = data[['DateTime', 'bar(g)', 'øC  cathode', 'øC  anode']]
    data = data.resample(
        time_grouping, on='DateTime', origin=start_time, closed='right', label='right'
    ).mean()

    datetimes = data.index
    pressure = data['bar(g)'].apply(_round_not_zero)
    temperature_cathode = data['øC  cathode'].apply(_round_not_zero)
    temperature_anode = data['øC  anode'].apply(_round_not_zero)

    return datetimes, pressure, temperature_cathode, temperature_anode


def read_gaschromatography_data(data):
    start_time, end_time = None, None

    instrument_file_names = data.loc[:, data.columns.str.startswith('Experiment name')]
    instrument_file_names.dropna(axis=0, how='all', inplace=True)

    date_only = pd.to_datetime(data['Date'], errors='coerce').dt.normalize()
    time_only = pd.to_datetime(
        data['Time '].astype(str), format='mixed', errors='coerce'
    )
    data['DateTime'] = date_only + (time_only - time_only.dt.normalize())
    datetimes = data['DateTime'].dropna()

    gas_types = data.loc[0, data.columns.str.startswith('Gas type')]
    retention_times = data.loc[:, data.columns.str.startswith('RT')]
    areas = data.loc[:, data.columns.str.startswith('area')]
    ppms = data.loc[:, data.columns.str.startswith('ppm value')]

    retention_times.dropna(axis=0, how='all', inplace=True)
    areas.dropna(axis=0, how='all', inplace=True)
    ppms.dropna(axis=0, how='all', inplace=True)

    if datetimes.size > 0:
        start_time = datetimes.iat[0]
        end_time = datetimes.iat[-1]

    gaschromatography_measurements = []
    for gas_index in range(len(gas_types)):
        file_index = 0 if gas_index < 4 else 1
        gas_type = gas_types.iat[gas_index]
        if gas_type in {'CO', 'CH4', 'C2H4', 'C2H6', 'H2', 'N2'}:
            gaschromatography_measurements.append(
                GasChromatographyMeasurement(
                    instrument_file_name=instrument_file_names.iloc[:, file_index],
                    datetime=datetimes.to_list(),
                    gas_type=gas_type,
                    retention_time=retention_times.iloc[:, gas_index],
                    area=areas.iloc[:, gas_index],
                    ppm=ppms.iloc[:, gas_index],
                )
            )
    return gaschromatography_measurements, start_time, end_time


def read_results_data(data, pH_start=None, ph_end=None):
    results_data = PotentiometryGasChromatographyResults()

    date_only = pd.to_datetime(data['Date'], errors='coerce').dt.normalize()
    time_only = pd.to_datetime(
        data['Time'].astype(str), format='mixed', errors='coerce'
    )
    data['DateTime'] = date_only + (time_only - time_only.dt.normalize())
    results_data.datetime = data['DateTime'].dropna().to_list()

    results_data.total_flow_rate = data['Total flow rate (ml/min)'].dropna()
    results_data.total_fe = data['Total FE (%)'].dropna()
    results_data.cell_current = data['Current(mA)'].dropna()
    results_data.cell_voltage = data['Cell Voltage'].dropna()

    gas_measurements = []
    current_column_headers = [col for col in data.columns if col.endswith('I (mA)')]

    for col_header in current_column_headers:
        gas_type = col_header.split(' ', 1)[0]
        current = data[col_header].dropna()
        fe = data[' '.join([gas_type, 'FE (%)'])].dropna()
        if (fe <= 0).all():
            fe = abs(fe)
        gas_measurements.append(
            GasFEResults(
                gas_type=gas_type,
                datetime=results_data.datetime,
                current=current,
                faradaic_efficiency=fe,
            )
        )
    results_data.gas_results = gas_measurements

    results_data.pH_start = pH_start
    results_data.pH_end = ph_end

    return results_data


def extract_properties(file):
    table_name = next(
        (
            name
            for name in ['Experimental details', 'Experimental Details']
            if name in file.sheet_names
        ),
        None,
    )
    data_sheet = pd.read_excel(file, sheet_name=table_name, index_col=0, header=None)

    if len(data_sheet.columns) == 0:
        return {}

    data = data_sheet[1]
    # normalize keys (different capitalization in different versions of excel template)
    data.index = data.index.str.strip().str.lower()

    experimental_properties = NECCExperimentalProperties()

    humidifier_temperature = data.get('humidifier temperature') or data.get(
        'humidifier temperature (°c)'
    )
    experimental_properties_dict = {
        'cell_type': data.get('cell type'),
        'has_reference_electrode': data.get('reference electrode (y/n)') == 'y',
        'reference_electrode_type': data.get('reference electrode type'),
        'cathode_geometric_area': data.get('cathode geometric area')
        or data.get('cathode geometric area (cm²)'),
        'membrane_type': data.get('membrane type'),
        'membrane_name': data.get('membrane name'),
        'membrane_thickness': data.get('membrane thickness')
        or data.get('membrane thickness (µm)'),
        'gasket_thickness': data.get('gasket thickness')
        or data.get('gasket thickness (µm)'),
        'anolyte_type': data.get('anolyte type'),
        'anolyte_concentration': data.get('anolyte conc. (m)'),
        'anolyte_flow_rate': data.get('anolyte flow rate (ml/min)'),
        'anolyte_volume': data.get('anolyte volume (ml)'),
        'has_humidifier': data.get('humidifier (y/n)') == 'y',
        'humidifier_temperature': 20
        if humidifier_temperature == 'RT'
        else humidifier_temperature,
        'water_trap_volume': data.get('water trap volume')
        or data.get('water trap volume (ml)'),
        'bleedline_flow_rate': data.get('bleedline flow rate')
        or data.get('bleedline flow rate (ml/min)'),
        'nitrogen_start_value': data.get('nitrogen start value')
        or data.get('nitrogen start value (ppm)'),
        'remarks': data.get('remarks'),
        'chronoanalysis_method': data.get('cp/ca'),
    }

    experimental_properties_dict = _get_clean_dict(experimental_properties_dict)
    for attribute_name, value in experimental_properties_dict.items():
        setattr(experimental_properties, attribute_name, value)

    feed_gases = []
    feed_flow_matches = data.index[
        data.index.str.contains('feed gas flow rate', case=False, na=False)
    ]
    feed_gas_flows = data.loc[feed_flow_matches]
    if not pd.isna(data.get('feed gas 1') and feed_gas_flows.iat[0]):
        feed_gases.append(
            NECCFeedGas(
                name=str(data.get('feed gas 1'))
                if pd.notna(data.get('feed gas 1'))
                else '',
                flow_rate=feed_gas_flows.iat[0],
            )
        )
    if not pd.isna(data.get('feed gas 2') and feed_gas_flows.iat[1]):
        feed_gases.append(
            NECCFeedGas(
                name=str(data.get('feed gas 2'))
                if pd.notna(data.get('feed gas 2'))
                else '',
                flow_rate=feed_gas_flows.iat[1],
            )
        )
    experimental_properties.feed_gases = feed_gases

    if not pd.isna(data.get('anode id')):
        experimental_properties.anode = CompositeSystemReference(
            lab_id=data.get('anode id').strip()
        )

    if not pd.isna(data.get('cathode id')):
        experimental_properties.cathode = CompositeSystemReference(
            lab_id=data.get('cathode id').strip()
        )

    return experimental_properties


def _get_electrode_recipe(data_series, recipe_type):
    electrode_recipe_id = CENECCElectrodeRecipeID()
    electrode_recipe_id.element = data_series.get('element')
    electrode_recipe_id.element_mass = data_series.get('element mass (mg)')
    electrode_recipe_id.deposition_method = data_series.get('deposition method')
    electrode_recipe_id.recipe_type = recipe_type
    substrate = SubstrateProperties()
    substrate.substrate_type = data_series.get('substrate')
    substrate.substrate_dimension = data_series.get('substrate dimension')
    substrate.total_area = data_series.get('substrate total area (cm²)')
    substrate.substrate_cleaning = data_series.get('substrate cleaning')
    solvents = [
        _get_clean_dict(
            {
                'type': data_series.get('solvent 1 type'),
                'volume': data_series.get('solvent 1 volume (ml)'),
            }
        ),
        _get_clean_dict(
            {
                'type': data_series.get('solvent 2 type'),
                'volume': data_series.get('solvent 2 volume (ml)'),
            }
        ),
    ]
    ionomers = [
        _get_clean_dict(
            {
                'type': data_series.get('ionomer type'),
                'mass': data_series.get('ionomer mass (mg)'),
            }
        ),
        _get_clean_dict(
            {
                'type': data_series.get('ionomer 1 type'),
                'mass': data_series.get('ionomer 1 mass (mg)'),
            }
        ),
        _get_clean_dict(
            {
                'type': data_series.get('ionomer 2 type'),
                'mass': data_series.get('ionomer 2 mass (mg)'),
            }
        ),
    ]
    solvents = [
        Solvent(type=s.get('type'), volume=s.get('volume')) for s in solvents if s
    ]  # only keep non-empty solvents
    ionomers = [
        Ionomer(type=i.get('type'), mass=i.get('mass')) for i in ionomers if i
    ]  # only keep non-empty ionomers
    recipe = CENECCElectrodeRecipe()
    recipe.name = data_series.get('recipe name', 'new_recipe_default_name')
    recipe.deposition_temperature = data_series.get('deposition temperature (°c)')
    recipe.n2_deposition_pressure = data_series.get('n2 deposition pressure (bar)')
    recipe.mass_loading = data_series.get('mass loading (mg/cm2)')
    recipe.description = data_series.get('recipe remarks')
    recipe.electrode_recipe_id = electrode_recipe_id
    recipe.substrate = substrate
    recipe.solvent = solvents
    recipe.ionomer = ionomers
    return recipe


def _get_shared_upload_id(archive, entry_type, base_id=None):
    from nomad.app.v1.models import MetadataPagination, MetadataRequired
    from nomad.search import search

    query = {'entry_type': entry_type}
    pagination = MetadataPagination()
    pagination.page_size = 1000
    required = MetadataRequired()
    required.include = (
        ['upload_id', 'results.eln.lab_ids'] if base_id else ['upload_id']
    )
    search_result = search(
        owner='all',
        query=query,
        user_id=archive.metadata.main_author.user_id,
        pagination=pagination,
        required=required,
    )
    if len(search_result.data) >= 1:
        upload_counts = {}
        for entry in search_result.data:
            if (
                base_id
                and base_id
                not in entry.get('results', {}).get('eln', {}).get('lab_ids', [''])[0]
            ):
                continue
            upload_counts[entry.get('upload_id')] = (
                upload_counts.get(entry.get('upload_id'), 0) + 1
            )
        if upload_counts:
            return max(upload_counts, key=upload_counts.get)
    return None


def _write_entry_to_upload(entry_def, entry, upload_id, file_name, overwrite=False):
    import json

    from nomad import files
    from nomad.processing import Upload

    if (
        not files.UploadFiles.get(upload_id=upload_id).raw_path_exists(file_name)
        or overwrite
    ):
        entry_dict = entry.m_to_dict(with_root_def=False)
        entry_dict['m_def'] = entry_def
        with files.UploadFiles.get(upload_id=upload_id).raw_file(
            file_name, 'w'
        ) as outfile:
            json.dump({'data': entry_dict}, outfile)
        Upload.get(upload_id).process_updated_raw_file(
            file_name, allow_modify=overwrite
        )
        return True
    else:
        return False


def _get_id_for_entry_hash(archive, entry_type, entry_dict_hash):
    from nomad.app.v1.models import MetadataPagination, MetadataRequired
    from nomad.search import search

    query = {
        'entry_type': entry_type,
        f'data.entry_dict_hash#nomad_chemical_energy.schema_packages.ce_necc_package.{entry_type}': entry_dict_hash,
    }
    pagination = MetadataPagination()
    pagination.page_size = 10
    pagination.order_by = 'entry_create_time'
    pagination.order = 'desc'
    required = MetadataRequired()
    required.include = [
        f'data.lab_id#nomad_chemical_energy.schema_packages.ce_necc_package.{entry_type}',
        'upload_id',
        'entry_id',
    ]
    search_result = search(
        owner='all',
        query=query,
        user_id=archive.metadata.main_author.user_id,
        pagination=pagination,
        required=required,
    )
    if len(search_result.data) >= 1:
        if entry_type == 'CE_NECC_Electrode':
            return search_result.data[0].get('data', {}).get('lab_id')
        return search_result.data[0]
    return None


def _get_electrode_recipe_reference(recipe_type, data_series, archive):
    recipe_entry_id = None
    recipe_upload_id = None
    if data_series.get('recipe id'):
        search_result = search_entry_by_id(archive, None, data_series.get('recipe id'))
        if len(search_result.data) == 1:
            recipe_entry_id = search_result.data[0]['entry_id']
            recipe_upload_id = search_result.data[0]['upload_id']
    else:
        electrode_recipe_entry = _get_electrode_recipe(data_series, recipe_type)
        # check if recipe already exists
        electrode_recipe_entry.set_entry_dict_hash()
        ref_id = _get_id_for_entry_hash(
            archive, 'CE_NECC_ElectrodeRecipe', electrode_recipe_entry.entry_dict_hash
        )
        if ref_id:
            return get_reference(
                ref_id.get('upload_id', ''), ref_id.get('entry_id', '')
            )
        # create new recipe if no identical recipe exists yet
        recipe_upload_id = _get_shared_upload_id(archive, 'CE_NECC_ElectrodeRecipe')
        recipe_file_name = f'{electrode_recipe_entry.name}.archive.json'
        entry_def = 'nomad_chemical_energy.schema_packages.ce_necc_package.CE_NECC_ElectrodeRecipe'
        new_recipe_written = _write_entry_to_upload(
            entry_def, electrode_recipe_entry, recipe_upload_id, recipe_file_name
        )
        if not new_recipe_written:
            return None
        from nomad.utils import hash

        recipe_entry_id = hash(recipe_upload_id, recipe_file_name)
    if recipe_entry_id and recipe_upload_id:
        electrode_recipe_ref = get_reference(recipe_upload_id, recipe_entry_id)
        return electrode_recipe_ref
    return None


def _get_electrode_comp_system_reference(archive, electrode_data, electrode_type):
    reuse_existing = electrode_data.get('already used in other\nexperiment? (y/n)')
    if electrode_type == 'anode':
        recipe_type = 'Anode Recipe (AR)'
        base_id = '_AR_'
    else:
        recipe_type = 'Cathode Recipe (CR)'
        base_id = '_CR_'
    electrode_recipe_ref = _get_electrode_recipe_reference(
        recipe_type, electrode_data, archive
    )
    electrode_entry = get_electrode(electrode_data, electrode_recipe_ref)
    if reuse_existing == 'y':
        electrode_entry.set_entry_dict_hash()
        ref_lab_id = _get_id_for_entry_hash(
            archive, 'CE_NECC_Electrode', electrode_entry.entry_dict_hash
        )
        if ref_lab_id:
            return CompositeSystemReference(lab_id=ref_lab_id)
        return None
    electrode_upload_id = _get_shared_upload_id(archive, 'CE_NECC_Electrode', base_id)
    date_str = (
        f'_{electrode_entry.electrode_id.datetime.strftime("%Y%m%d")}'
        if electrode_entry.electrode_id.datetime
        else ''
    )
    electrode_entry.name = (
        f'{electrode_type}{date_str}_{archive.data.name.replace(".xlsx", "")}'
    )
    electrode_file_name = f'{electrode_entry.name}.archive.json'
    entry_def = (
        'nomad_chemical_energy.schema_packages.ce_necc_package.CE_NECC_Electrode'
    )
    new_electrode_written = _write_entry_to_upload(
        entry_def, electrode_entry, electrode_upload_id, electrode_file_name
    )
    if not new_electrode_written:
        return None
    from nomad.utils import hash

    electrode_entry_id = hash(electrode_upload_id, electrode_file_name)
    return CompositeSystemReference(
        reference=get_reference(electrode_upload_id, electrode_entry_id)
    )


def get_electrode(data_series, recipe_reference):
    electrode_id = CENECCElectrodeID()
    electrode_id.owner = data_series.get('owner name')
    electrode_id.institute = data_series.get('group name')
    electrode_id.datetime = pd.to_datetime(data_series.get('preparation date'))
    electrode_id.recipe = recipe_reference
    electrode = CENECCElectrode()
    electrode.description = data_series.get('remarks')
    electrode.measured_mass_loading = data_series.get('measured mass loading (mg/cm2)')
    electrode.bottle_number = data_series.get('bottle n#')
    electrode.electrode_id = electrode_id
    return electrode


def set_catalyst_details(archive, file):
    data_sheet = pd.read_excel(
        file,
        sheet_name='Catalyst details',
        index_col=0,
        header=None,
    )

    if len(data_sheet.columns) == 0:
        return {}

    # normalize keys (different capitalization in different versions of excel template)
    data_sheet.index = data_sheet.index.str.strip().str.lower()
    if archive.data.properties.cathode is None:
        cathode_data = data_sheet[1].dropna()
        archive.data.properties.cathode = _get_electrode_comp_system_reference(
            archive, cathode_data, 'cathode'
        )
    if archive.data.properties.anode is None:
        anode_data = data_sheet[4].dropna()
        archive.data.properties.anode = _get_electrode_comp_system_reference(
            archive, anode_data, 'anode'
        )
