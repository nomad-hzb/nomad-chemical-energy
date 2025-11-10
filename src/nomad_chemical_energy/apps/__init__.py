from nomad.config.models.plugins import AppEntryPoint

from nomad_chemical_energy.apps.amcc_reproducibility_app import amcc_reproducibility_app
from nomad_chemical_energy.apps.catlab_combinatorial_app import catlab_combinatorial_app
from nomad_chemical_energy.apps.catlab_pixel_app import catlab_pixel_app
from nomad_chemical_energy.apps.necc_compare_app import necc_compare_app
from nomad_chemical_energy.apps.necc_find_app import necc_find_experiments_app
from nomad_chemical_energy.apps.nesd_oer_app import nesd_oer_app
from nomad_chemical_energy.apps.nome_oer_cp_app import nome_oer_cp_app
from nomad_chemical_energy.apps.nome_sample_app import nome_sample_app
from nomad_chemical_energy.apps.voila_finder_app import voila_finder_app

voila_finder_app = AppEntryPoint(
    name='voila',
    description='Find and launch your Voila Tools.',
    app=voila_finder_app,
)

nome_sample_app = AppEntryPoint(
    name='ExploreNOMESample',
    description='Search and find your NOME samples.',
    app=nome_sample_app,
)

nome_oer_cp_analysis_app = AppEntryPoint(
    name='ExploreOERCP',
    description='Provides filters to explore OER CP entries of the NOME group.',
    app=nome_oer_cp_app,
)

nesd_oer_app = AppEntryPoint(
    name='ExploreOER',
    description='Provides filters to explore OER analysis entries of the NESD group.',
    app=nesd_oer_app,
)

amcc_reproducibility_app = AppEntryPoint(
    name='ExploreReproducibility',
    description='Provides filters to explore entries of the reproducibility study.',
    app=amcc_reproducibility_app,
)

catlab_combinatorial_library_app = AppEntryPoint(
    name='Combinatorial Samples',
    description='Provides filters to investigate combinatorial libraries.',
    app=catlab_combinatorial_app,
)

catlab_pixel_app = AppEntryPoint(
    name='Combinatorial Catalysis Libraries composition',
    description='Provides filters to investigate combinatorial library pixels.',
    app=catlab_pixel_app,
)

necc_find_app = AppEntryPoint(
    name='FindNECCExperiments',
    description='Provides filters to quickly find NECC experiment entries.',
    app=necc_find_experiments_app,
)

necc_compare_app = AppEntryPoint(
    name='CompareNECCExperiments',
    description='Compare and filter experimental NECC data.',
    app=necc_compare_app,
)
