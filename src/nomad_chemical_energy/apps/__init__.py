from nomad.config.models.plugins import AppEntryPoint
from nomad.config.models.ui import (
    App,
    Column,
    Columns,
    FilterMenu,
    FilterMenus,
    FilterMenuSizeEnum,
    Filters,
    Format,
    ModeEnum,
    RowActionNorth,
    RowActions,
    RowActionURL,
    RowDetails,
    Rows,
    RowSelection,
)

from nomad_chemical_energy.apps.catlab_combinatorial_app import catlab_combinatorial_app
from nomad_chemical_energy.apps.necc_find_app import necc_find_experiments_app
from nomad_chemical_energy.apps.nome_oer_cp_app import nome_oer_cp_app

schema_name = (
    'nomad_chemical_energy.schema_packages.ce_nome_package.CE_NOME_VoilaNotebook'
)
nome_documentation_app = AppEntryPoint(
    name='voila',
    description='Find and launch your Voila Tools.',
    app=App(
        # Label of the App
        label='Voila',
        # Path used in the URL, must be unique
        path='voila',
        # Used to categorize apps in the explore menu
        category='use cases',
        # Brief description used in the app menu
        description='Find and launch your Voila Tools.',
        # Longer description that can also use markdown
        readme='Find and launch your Voila Tools.',
        # Controls the available search filters. If you want to filter by
        # quantities in a schema package, you need to load the schema package
        # explicitly here. Note that you can use a glob syntax to load the
        # entire package, or just a single schema from a package.
        filters=Filters(
            include=[
                '*#nomad_chemical_energy.schema_packages.ce_nome_package.CE_NOME_VoilaNotebook',
            ]
        ),
        # Dictionary of search filters that are always enabled for queries made
        # within this app. This is especially important to narrow down the
        # results to the wanted subset. Any available search filter can be
        # targeted here. This example makes sure that only entries that use
        # MySchema are included.
        filters_locked={
            'section_defs.definition_qualified_name': 'nomad_chemical_energy.schema_packages.ce_nome_package.CE_NOME_VoilaNotebook'
        },
        filter_menus=FilterMenus(
            options={
                'custom_quantities': FilterMenu(
                    label='Notebooks', size=FilterMenuSizeEnum.L
                ),
                'author': FilterMenu(label='Author', size=FilterMenuSizeEnum.M),
                'metadata': FilterMenu(label='Visibility / IDs'),
            }
        ),
        columns=[
            Column(quantity=f'data.name#{schema_name}', selected=True),
            Column(
                quantity='entry_type', label='Entry type', align='left', selected=True
            ),
            Column(
                quantity='entry_create_time',
                label='Entry time',
                align='left',
                selected=True,
                format=Format(mode=ModeEnum.DATE),
            ),
            Column(
                quantity='upload_name',
                label='Upload name',
                align='left',
                selected=True,
            ),
            Column(
                quantity='authors',
                label='Authors',
                align='left',
                selected=True,
            ),
            Column(quantity='entry_id'),
            Column(quantity='upload_id'),
            Column(quantity=f'data.notebook_file#{schema_name}'),
        ],
        rows=Rows(
            actions=RowActions(
                items=[
                    RowActionNorth(
                        filepath=f'data.notebook_file#{schema_name}',
                        tool_name='voila',
                        description='Launch voila tool in new tab',
                        icon='rocket_launch',
                    ),
                    RowActionURL(
                        path=f'data.file_uri#{schema_name}',
                        description='View in file browser',
                        icon='search',
                    ),
                ]
            ),
            details=RowDetails(),
            selection=RowSelection(),
        ),
    ),
)

nome_oer_cp_analysis_app = AppEntryPoint(
    name='ExploreOERCP',
    description='Provides filters to explore OER CP entries of the NOME group.',
    app=nome_oer_cp_app,
)

catlab_combinatorial_library_app = AppEntryPoint(
    name='Combinatorial Samples',
    description='Provides filters to investigate combinatorial libraries.',
    app=catlab_combinatorial_app,
)

necc_find_app = AppEntryPoint(
    name='FindNECCExperiments',
    description='Provides filters to quickly find NECC experiment entries.',
    app=necc_find_experiments_app,
)

necc_compare_app = AppEntryPoint(
    name='CompareNECCExperiments',
    description='Compare and filter experimental NECC data.',
    app=App(
        # Label of the App
        label='Compare NECC Experiments',
        # Path used in the URL, must be unique
        path='necc-compare',
        # Used to categorize apps in the explore menu
        category='NECC Data',
        # Brief description used in the app menu
        description='Compare and filter experimental NECC data.',
        # Longer description that can also use markdown
        readme='Compare and filter experimental NECC data.',
        # Controls the available search filters. If you want to filter by
        # quantities in a schema package, you need to load the schema package
        # explicitly here. Note that you can use a glob syntax to load the
        # entire package, or just a single schema from a package.
        filters=Filters(
            include=[
                '*#nomad_chemical_energy.schema_packages.ce_necc_package.CE_NECC_EC_GC',
                '*#nomad_chemical_energy.schema_packages.ce_necc_package.CE_NECC_Electrode',
                '*#nomad_chemical_energy.schema_packages.ce_necc_package.CE_NECC_ElectrodeRecipe',
            ]
        ),
        # Controls which columns are shown in the results table
        columns=Columns(
            selected=[
                'entry_type',
                'entry_name',
                'entry_create_time',
                'authors',
                'upload_name',
                'data.lab_id#nomad_chemical_energy.schema_packages.ce_necc_package.CE_NECC_EC_GC',
                'data.properties.cathode.lab_id#nomad_chemical_energy.schema_packages.ce_necc_package.CE_NECC_Electrode',
                'data.properties.anode.lab_id#nomad_chemical_energy.schema_packages.ce_necc_package.CE_NECC_ElectrodeRecipe',
            ],
            options={
                'entry_type': Column(label='Entry type', align='left'),
                'entry_name': Column(label='Name', align='left'),
                'entry_create_time': Column(label='Entry time', align='left'),
                'authors': Column(label='Authors', align='left'),
                'upload_name': Column(label='Upload name', align='left'),
                'data.lab_id#nomad_chemical_energy.schema_packages.ce_necc_package.CE_NECC_EC_GC': Column(
                    label='Experiment ID', align='left'
                ),
                'data.properties.cathode.lab_id#nomad_chemical_energy.schema_packages.ce_necc_package.CE_NECC_Electrode': Column(
                    label='Cathode ID', align='left'
                ),
                'data.properties.anode.lab_id#nomad_chemical_energy.schema_packages.ce_necc_package.CE_NECC_ElectrodeRecipe': Column(
                    label='Anode ID', align='left'
                ),
            },
        ),
        # Dictionary of search filters that are always enabled for queries made
        # within this app. This is especially important to narrow down the
        # results to the wanted subset. Any available search filter can be
        # targeted here. This example makes sure that only entries that use
        # MySchema are included.
        filters_locked={
            'section_defs.definition_qualified_name': 'nomad_chemical_energy.schema_packages.ce_necc_package.CE_NECC_EC_GC'
        },
        # Controls the filter menus shown on the left
        filter_menus=FilterMenus(
            options={
                'material': FilterMenu(label='Material', level=0),
                'elements': FilterMenu(label='Elements / Formula', level=1, size='xl'),
                'eln': FilterMenu(label='Electronic Lab Notebook', level=0),
                'custom_quantities': FilterMenu(
                    label='User Defined Quantities', level=0, size='l'
                ),
                'author': FilterMenu(
                    label='Author / Origin / Dataset', level=0, size='m'
                ),
                'metadata': FilterMenu(label='Visibility / IDs / Schema', level=0),
                'optimade': FilterMenu(label='Optimade', level=0, size='m'),
            }
        ),
        # Controls the default dashboard shown in the search interface
        dashboard={
            'widgets': [
                {
                    'type': 'terms',
                    'showinput': True,
                    'scale': 'linear',
                    'quantity': 'authors.name',
                    'layout': {
                        'xxl': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 0, 'x': 0},
                        'xl': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 0, 'x': 0},
                        'lg': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 0, 'x': 0},
                        'md': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 0, 'x': 0},
                        'sm': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 0, 'x': 0},
                    },
                },
                {
                    'type': 'terms',
                    'showinput': True,
                    'scale': 'linear',
                    'quantity': 'results.eln.methods',
                    'layout': {
                        'xxl': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 0, 'x': 6},
                        'xl': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 0, 'x': 6},
                        'lg': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 0, 'x': 6},
                        'md': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 0, 'x': 6},
                        'sm': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 0, 'x': 6},
                    },
                },
                {
                    'type': 'histogram',
                    'showinput': True,
                    'autorange': False,
                    'nbins': 30,
                    'scale': '1/4',
                    'quantity': 'data.fe_results.gas_results.minimum_fe#nomad_chemical_energy.schema_packages.ce_necc_package.CE_NECC_EC_GC',
                    'title': 'Minimal FE per gas (in %)',
                    'layout': {
                        'xxl': {'minH': 3, 'minW': 3, 'h': 6, 'w': 12, 'y': 18, 'x': 0},
                        'xl': {'minH': 3, 'minW': 3, 'h': 6, 'w': 12, 'y': 18, 'x': 0},
                        'lg': {'minH': 3, 'minW': 3, 'h': 6, 'w': 12, 'y': 18, 'x': 0},
                        'md': {'minH': 3, 'minW': 3, 'h': 6, 'w': 12, 'y': 18, 'x': 0},
                        'sm': {'minH': 3, 'minW': 3, 'h': 6, 'w': 12, 'y': 18, 'x': 0},
                    },
                },
                {
                    'type': 'scatterplot',
                    'autorange': True,
                    'size': 1000,
                    'markers': {
                        'color': {
                            'quantity': 'data.properties.anolyte_type#nomad_chemical_energy.schema_packages.ce_necc_package.CE_NECC_EC_GC',
                        }
                    },
                    'y': {
                        'title': 'CO FE (in%)',
                        'quantity': 'data.fe_results.gas_results[0].minimum_fe#nomad_chemical_energy.schema_packages.ce_necc_package.CE_NECC_EC_GC',
                    },
                    'x': {
                        'quantity': 'data.properties.anolyte_concentration#nomad_chemical_energy.schema_packages.ce_necc_package.CE_NECC_EC_GC',
                        'scale': 'linear',
                        'unit': 'mol / l',
                    },
                    'title': 'CO FE',
                    'layout': {
                        'xxl': {'minH': 3, 'minW': 3, 'h': 6, 'w': 12, 'y': 0, 'x': 12},
                        'xl': {'minH': 3, 'minW': 3, 'h': 6, 'w': 12, 'y': 0, 'x': 12},
                        'lg': {'minH': 3, 'minW': 3, 'h': 6, 'w': 12, 'y': 0, 'x': 12},
                        'md': {'minH': 3, 'minW': 3, 'h': 6, 'w': 12, 'y': 24, 'x': 0},
                        'sm': {'minH': 3, 'minW': 3, 'h': 6, 'w': 12, 'y': 24, 'x': 0},
                    },
                },
                {
                    'type': 'terms',
                    'showinput': True,
                    'scale': 'linear',
                    'quantity': 'data.properties.cell_type#nomad_chemical_energy.schema_packages.ce_necc_package.CE_NECC_EC_GC',
                    'layout': {
                        'xxl': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 6, 'x': 0},
                        'xl': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 6, 'x': 0},
                        'lg': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 6, 'x': 0},
                        'md': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 6, 'x': 0},
                        'sm': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 6, 'x': 0},
                    },
                },
                {
                    'type': 'terms',
                    'showinput': True,
                    'scale': 'linear',
                    'quantity': 'data.properties.membrane_type#nomad_chemical_energy.schema_packages.ce_necc_package.CE_NECC_EC_GC',
                    'layout': {
                        'xxl': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 12, 'x': 0},
                        'xl': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 12, 'x': 0},
                        'lg': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 12, 'x': 0},
                        'md': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 12, 'x': 0},
                        'sm': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 12, 'x': 0},
                    },
                },
                {
                    'type': 'terms',
                    'showinput': True,
                    'scale': 'linear',
                    'quantity': 'data.properties.membrane_name#nomad_chemical_energy.schema_packages.ce_necc_package.CE_NECC_EC_GC',
                    'layout': {
                        'xxl': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 12, 'x': 6},
                        'xl': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 12, 'x': 6},
                        'lg': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 12, 'x': 6},
                        'md': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 12, 'x': 6},
                        'sm': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 12, 'x': 6},
                    },
                },
                {
                    'type': 'terms',
                    'showinput': True,
                    'scale': 'linear',
                    'quantity': 'data.properties.anolyte_type#nomad_chemical_energy.schema_packages.ce_necc_package.CE_NECC_EC_GC',
                    'layout': {
                        'xxl': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 6, 'x': 6},
                        'xl': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 6, 'x': 6},
                        'lg': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 6, 'x': 6},
                        'md': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 6, 'x': 6},
                        'sm': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 6, 'x': 6},
                    },
                },
                {
                    'type': 'scatterplot',
                    'autorange': True,
                    'size': 1000,
                    'markers': {
                        'color': {
                            'quantity': 'data.properties.anolyte_type#nomad_chemical_energy.schema_packages.ce_necc_package.CE_NECC_EC_GC',
                        }
                    },
                    'y': {
                        'title': 'CH4 FE (in%)',
                        'quantity': 'data.fe_results.gas_results[1].minimum_fe#nomad_chemical_energy.schema_packages.ce_necc_package.CE_NECC_EC_GC',
                    },
                    'x': {
                        'quantity': 'data.properties.anolyte_concentration#nomad_chemical_energy.schema_packages.ce_necc_package.CE_NECC_EC_GC',
                        'scale': 'linear',
                        'unit': 'mol / l',
                    },
                    'title': 'CH4 FE',
                    'layout': {
                        'xxl': {'minH': 3, 'minW': 3, 'h': 6, 'w': 12, 'y': 6, 'x': 12},
                        'xl': {'minH': 3, 'minW': 3, 'h': 6, 'w': 12, 'y': 6, 'x': 12},
                        'lg': {'minH': 3, 'minW': 3, 'h': 6, 'w': 12, 'y': 6, 'x': 12},
                        'md': {'minH': 3, 'minW': 3, 'h': 6, 'w': 12, 'y': 30, 'x': 0},
                        'sm': {'minH': 3, 'minW': 3, 'h': 6, 'w': 12, 'y': 30, 'x': 0},
                    },
                },
                {
                    'type': 'scatterplot',
                    'autorange': True,
                    'size': 1000,
                    'markers': {
                        'color': {
                            'quantity': 'data.properties.anolyte_type#nomad_chemical_energy.schema_packages.ce_necc_package.CE_NECC_EC_GC',
                        }
                    },
                    'y': {
                        'title': 'C2H4 FE (in%)',
                        'quantity': 'data.fe_results.gas_results[2].minimum_fe#nomad_chemical_energy.schema_packages.ce_necc_package.CE_NECC_EC_GC',
                    },
                    'x': {
                        'quantity': 'data.properties.anolyte_concentration#nomad_chemical_energy.schema_packages.ce_necc_package.CE_NECC_EC_GC',
                        'scale': 'linear',
                        'unit': 'mol / l',
                    },
                    'title': 'C2H4 FE',
                    'layout': {
                        'xxl': {
                            'minH': 3,
                            'minW': 3,
                            'h': 6,
                            'w': 12,
                            'y': 12,
                            'x': 12,
                        },
                        'xl': {'minH': 3, 'minW': 3, 'h': 6, 'w': 12, 'y': 12, 'x': 12},
                        'lg': {'minH': 3, 'minW': 3, 'h': 6, 'w': 12, 'y': 0, 'x': 12},
                        'md': {'minH': 3, 'minW': 3, 'h': 6, 'w': 12, 'y': 36, 'x': 0},
                        'sm': {'minH': 3, 'minW': 3, 'h': 6, 'w': 12, 'y': 36, 'x': 0},
                    },
                },
                {
                    'type': 'scatterplot',
                    'autorange': True,
                    'size': 1000,
                    'markers': {
                        'color': {
                            'quantity': 'data.properties.anolyte_type#nomad_chemical_energy.schema_packages.ce_necc_package.CE_NECC_EC_GC',
                        }
                    },
                    'y': {
                        'title': 'H2 FE (in%)',
                        'quantity': 'data.fe_results.gas_results[3].minimum_fe#nomad_chemical_energy.schema_packages.ce_necc_package.CE_NECC_EC_GC',
                    },
                    'x': {
                        'quantity': 'data.properties.anolyte_concentration#nomad_chemical_energy.schema_packages.ce_necc_package.CE_NECC_EC_GC',
                        'scale': 'linear',
                        'unit': 'mol / l',
                    },
                    'title': 'H2 FE',
                    'layout': {
                        'xxl': {
                            'minH': 3,
                            'minW': 3,
                            'h': 6,
                            'w': 12,
                            'y': 18,
                            'x': 12,
                        },
                        'xl': {'minH': 3, 'minW': 3, 'h': 6, 'w': 12, 'y': 18, 'x': 12},
                        'lg': {'minH': 3, 'minW': 3, 'h': 6, 'w': 12, 'y': 18, 'x': 12},
                        'md': {'minH': 3, 'minW': 3, 'h': 6, 'w': 12, 'y': 42, 'x': 0},
                        'sm': {'minH': 3, 'minW': 3, 'h': 6, 'w': 12, 'y': 42, 'x': 0},
                    },
                },
            ]
        },
    ),
)
