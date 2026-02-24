import pytest


@pytest.fixture(autouse=True)
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
    monkeypatch.setattr(
        'nomad_chemical_energy.schema_packages.ce_necc_package.set_catalyst_details',
        mockreturn_search,
    )
