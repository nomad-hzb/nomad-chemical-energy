import os

import pytest
from nomad.client import normalize_all, parse


def set_monkey_patch(monkeypatch):
    def mockreturn_search(*args):
        return None

    monkeypatch.setattr(
        'nomad_chemical_energy.parsers.ce_nome_parser.search_class', mockreturn_search
    )
    monkeypatch.setattr(
        'nomad_chemical_energy.parsers.ce_nome_parser.set_sample_reference',
        mockreturn_search,
    )
    monkeypatch.setattr(
        'nomad_chemical_energy.parsers.ce_nome_parser.find_sample_by_id',
        mockreturn_search,
    )
    monkeypatch.setattr(
        'nomad_chemical_energy.parsers.ce_necc_parser.set_sample_reference',
        mockreturn_search,
    )
    monkeypatch.setattr(
        'nomad_chemical_energy.parsers.hzb_general_parser.update_general_process_entries',
        mockreturn_search,
    )
    monkeypatch.setattr(
        'nomad_chemical_energy.schema_packages.tfc_package.set_sample_reference',
        mockreturn_search,
    )
    monkeypatch.setattr(
        'nomad_chemical_energy.parsers.ce_nesd_parser.set_sample_reference',
        mockreturn_search,
    )
    monkeypatch.setattr(
        'nomad_chemical_energy.schema_packages.ce_nesd_package.create_archive',
        mockreturn_search,
    )


@pytest.fixture(
    params=[
        '20230223_080542_NiOx_MW_Co10_1_1_Co_001_0_merged.dat',
        '20230224_011729_Co3O4_ref_tm_001_0_merged.dat',
        '230531-CA-test2.DTA',
        '3stepCACA.DTA',
        'calib_30min_0.1ppm.ABS',
        'CE-NOME_FrJo_240815_0001.0 H2O Au000001.txt',
        'CE-NOME_MiGo_240429_0001.SA_5_MM.csv',
        'CHRONOA.DTA',
        'CHRONOP.DTA',
        'CV__#3.DTA',
        'CVCA.DTA',
        'CVCAHintereinander_Pos1.DTA',
        'CVCP.DTA',
        'CVCPHintereinander_pos2.DTA',
        'CV.DTA',
        'EISPOT.DTA',
        'LSG.DTA',
        'LSVCA.DTA',
        'LSV.DTA',
        'necc_test_no_properties.xlsx',
        'OCP.DTA',
        'P-O2D109.pump.csv',
        'test1234.test2.txt',
        'test1234.test.txt',
        'test double PTFETape 3 100724000001.txt',
        'testO2.oxy.xlsx',
        'labview_metadata_nesd.tdms',
    ]
)
def parsed_archive(request, monkeypatch):
    """
    Sets up data for testing and cleans up after the test.
    """

    set_monkey_patch(monkeypatch)

    rel_file = os.path.join('tests', 'data', request.param)
    file_archive = parse(rel_file)[0]
    measurement = os.path.join('tests', 'data', request.param + '.archive.json')
    assert file_archive.data.activity
    archive_json = ''
    for file in os.listdir(os.path.join('tests/data')):
        if 'archive.json' not in file or request.param.replace('#', 'run') not in file:
            continue
        archive_json = file
        measurement = os.path.join('tests', 'data', archive_json)
        measurement_archive = parse(measurement)[0]

        if os.path.exists(measurement):
            os.remove(measurement)
    print(measurement_archive)
    yield measurement_archive

    assert archive_json


def test_normalize_all(parsed_archive, monkeypatch):
    normalize_all(parsed_archive)


def get_archive(file_base, monkeypatch):
    set_monkey_patch(monkeypatch)
    file_name = os.path.join('tests', 'data', file_base)
    parse(file_name)[0]
    for file in os.listdir(os.path.join('tests/data')):
        if 'archive.json' not in file or file_base.replace('#', 'run') not in file:
            continue
        measurement = os.path.join('tests', 'data', file)
        measurement_archive = parse(measurement)[0]

        if os.path.exists(measurement):
            os.remove(measurement)
        break
    normalize_all(measurement_archive)
    return measurement_archive


def test_biologic_eclab_constC_parser(monkeypatch):
    file = 'CstC_nesd.mpr'
    archive = get_archive(file, monkeypatch)
    assert archive.data
    assert archive.data.properties
    assert archive.data.properties.lower_limit_potential.magnitude == -2.5
    assert round(archive.data.voltage[0].magnitude, 4) == 0.0028
    assert (
        round(archive.data.setup_parameters.active_material_mass.magnitude, 3) == 0.001
    )


def test_biologic_eclab_constV_parser(monkeypatch):
    file = 'CstV_nesd.mpr'
    archive = get_archive(file, monkeypatch)
    assert archive.data
    assert archive.data.properties
    assert archive.data.properties.sample_period.magnitude == 5
    assert round(archive.data.voltage[0].magnitude, 5) == 0.00012
    assert (
        round(archive.data.setup_parameters.active_material_mass.magnitude, 3) == 0.001
    )


def test_biologic_eclab_GEIS_parser(monkeypatch):
    file = 'GEIS_nesd.mpr'
    archive = get_archive(file, monkeypatch)
    assert archive.data
    assert archive.data.description == 'abc'
    assert archive.data.measurements
    assert len(archive.data.measurements) == 3
    assert archive.data.measurements[0].initial_frequency.magnitude == 1000
    assert round(archive.data.measurements[0].data.z_real[0].magnitude, 3) == 1488.236
    assert (
        round(archive.data.setup_parameters.active_material_mass.magnitude, 3) == 0.001
    )


def test_biologic_eclab_LSV_parser(monkeypatch):
    file = 'LSV_nesd.mpr'
    archive = get_archive(file, monkeypatch)
    assert archive.data
    assert archive.data.properties
    assert archive.data.properties.final_potential.magnitude == 1
    assert round(archive.data.voltage[0].magnitude, 4) == -0.0001
    assert (
        round(archive.data.setup_parameters.active_material_mass.magnitude, 3) == 0.001
    )


def test_biologic_eclab_PEIS_parser(monkeypatch):
    file = 'PEIS_nesd.mpr'
    archive = get_archive(file, monkeypatch)
    assert archive.data
    assert archive.data.description == 'abc'
    assert archive.data.measurements
    assert len(archive.data.measurements) == 3
    assert archive.data.measurements[0].dc_voltage.magnitude == 0.25
    assert round(archive.data.measurements[0].data.z_real[0].magnitude, 3) == 1489.251
    assert (
        round(archive.data.setup_parameters.active_material_mass.magnitude, 3) == 0.001
    )


def test_gamry_EIS_parser(monkeypatch):
    file = 'EISPOT.DTA'
    archive = get_archive(file, monkeypatch)
    assert archive.data
    assert archive.data.properties
    assert archive.data.frequency[0]
    assert archive.data.z_real[0]
    assert archive.data.atmosphere[0].temperature.magnitude == 25
    assert archive.data.properties.initial_frequency.magnitude == 2 * 1e6


def test_gamry_CV_parser(monkeypatch):
    file = 'CV.DTA'
    archive = get_archive(file, monkeypatch)
    assert archive.data
    assert archive.data.properties
    assert archive.data.cycles[0].voltage[0]
    assert archive.data.atmosphere[0].temperature.magnitude == 25
    assert archive.data.properties.limit_potential_1.magnitude == 0.5


def test_labview_nesd_parser(monkeypatch):
    file = 'labview_metadata_nesd.tdms'
    archive = get_archive(file, monkeypatch)
    assert archive.data
    assert len(archive.data.time) == 344
    assert archive.data.name == '20241202_091736_Softwaretest001_001'


def test_tfc_sputtering_parser(monkeypatch):
    file = 'tfc_sputtering.xlsx'
    archive = get_archive(file, monkeypatch)
    assert archive.data
    assert archive.data.targets
    assert archive.data.process_properties
    assert archive.data.observables
    assert archive.data.holder == '6" Wafer'
    assert archive.data.process_properties[0].sputter_pressure.magnitude == 0.0167
    assert archive.data.targets[0].name == '1) Al'
    assert archive.data.observables[0].temperature.magnitude == 25
