import os
from types import SimpleNamespace

from baseclasses import CompositeSystemReference
from nomad.client import parse

from nomad_chemical_energy.schema_packages.ce_nesd_package import find_sample_in_folder


def test_recursive_sample_search(monkeypatch):
    """
    The NESD group has an implicit directory structure for each upload.
    For each entry, the function should locate the sample that is stored closest to that entry in the folder structure.
    If no sample is found in any of the parent directories, the function should return an empty list.
    """
    one_sample_file = 'tests/data/archives/nesd_test_directory/material1/sample1/palmsens_ca.pssession'
    multi_sample_file = 'tests/data/archives/nesd_test_directory/material1/sample2/palmsens_ca.pssession'
    no_sample_file = 'tests/data/archives/nesd_test_directory/material2/sample1/palmsens_ca.pssession'
    one_sample_archive = parse(one_sample_file)[0]
    multi_sample_archive = parse(multi_sample_file)[0]
    no_sample_archive = parse(no_sample_file)[0]

    for arch in [one_sample_archive, multi_sample_archive, no_sample_archive]:
        monkeypatch.setattr(
            arch,
            'm_context',
            SimpleNamespace(
                upload_files=SimpleNamespace(
                    raw_listdir=lambda folder: os.scandir(folder or '.')
                )
            ),
        )

    one_result = find_sample_in_folder(one_sample_archive, one_sample_file)
    assert len(one_result) == 1
    assert isinstance(one_result[0], CompositeSystemReference)

    first_from_multi_result = find_sample_in_folder(
        multi_sample_archive, multi_sample_file
    )
    assert len(first_from_multi_result) == 1
    assert isinstance(first_from_multi_result[0], CompositeSystemReference)
    assert str(first_from_multi_result[0].reference) != str(one_result[0].reference)

    no_result = find_sample_in_folder(no_sample_archive, no_sample_file)
    assert no_result == []

    # remove archive files that are created during parsing
    for measurement_file in [one_sample_file, multi_sample_file, no_sample_file]:
        archive_file = measurement_file + '.archive.json'
        if os.path.exists(archive_file):
            os.remove(archive_file)
