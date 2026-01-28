from nomad.client import normalize_all, parse


def test_recipe_entry_hash():
    """
    Test for entry_dict_hash to be only equal for recipes with identical content data.
    """
    recipe1_archive = parse('tests/data/necc_test_recipe.archive.json')[0]
    recipe2_archive = parse('tests/data/necc_test_recipe.archive.json')[0]
    recipe3_archive = parse('tests/data/necc_test_recipe.archive.json')[0]

    # data only differently written with spaces
    recipe2_archive.data.substrate.substrate_dimension = '14 x 4'
    assert recipe1_archive.data.substrate.substrate_dimension == '14x4'
    assert recipe2_archive.data.substrate.substrate_dimension == '14 x 4'

    # data varies in content
    recipe3_archive.data.n2_deposition_pressure = 5
    assert recipe1_archive.data.n2_deposition_pressure.magnitude == 2
    assert recipe3_archive.data.n2_deposition_pressure.magnitude == 5

    normalize_all(recipe1_archive)
    normalize_all(recipe2_archive)
    normalize_all(recipe3_archive)

    assert recipe1_archive.data.entry_dict_hash == recipe2_archive.data.entry_dict_hash
    assert recipe1_archive.data.entry_dict_hash != recipe3_archive.data.entry_dict_hash
    assert recipe2_archive.data.entry_dict_hash != recipe3_archive.data.entry_dict_hash
