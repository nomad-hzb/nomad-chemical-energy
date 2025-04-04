from nomad.config.models.ui import (
    App,
    Column,
    Columns,
    FilterMenu,
    FilterMenus,
    Filters,
)

necc_find_experiments_app = App(
    # Label of the App
    label='Find NECC Experiments',
    # Path used in the URL, must be unique
    path='necc-find',
    # Used to categorize apps in the explore menu
    category='NECC Data',
    # Brief description used in the app menu
    description='Provides filters to quickly find NECC experiment entries.',
    # Longer description that can also use markdown
    readme='Provides filters to quickly find NECC experiment entries.',
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
            'author': FilterMenu(label='Author / Origin / Dataset', level=0, size='m'),
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
                'quantity': 'entry_create_time',
                'layout': {
                    'xxl': {'minH': 3, 'minW': 3, 'h': 3, 'w': 12, 'y': 0, 'x': 12},
                    'xl': {'minH': 3, 'minW': 3, 'h': 3, 'w': 12, 'y': 0, 'x': 12},
                    'lg': {'minH': 3, 'minW': 3, 'h': 3, 'w': 12, 'y': 0, 'x': 12},
                    'md': {'minH': 3, 'minW': 3, 'h': 3, 'w': 12, 'y': 6, 'x': 0},
                    'sm': {'minH': 3, 'minW': 3, 'h': 3, 'w': 12, 'y': 6, 'x': 0},
                },
            },
            {
                'type': 'terms',
                'showinput': True,
                'scale': 'linear',
                'quantity': 'data.properties.anode.name#nomad_chemical_energy.schema_packages.ce_necc_package.CE_NECC_EC_GC',
                'title': 'Anode ID',
                'layout': {
                    'xxl': {'minH': 3, 'minW': 3, 'h': 5, 'w': 6, 'y': 9, 'x': 0},
                    'xl': {'minH': 3, 'minW': 3, 'h': 5, 'w': 6, 'y': 9, 'x': 0},
                    'lg': {'minH': 3, 'minW': 3, 'h': 5, 'w': 6, 'y': 9, 'x': 0},
                    'md': {'minH': 3, 'minW': 3, 'h': 5, 'w': 6, 'y': 9, 'x': 0},
                    'sm': {'minH': 3, 'minW': 3, 'h': 5, 'w': 6, 'y': 9, 'x': 0},
                },
            },
            {
                'type': 'terms',
                'showinput': True,
                'scale': 'linear',
                'quantity': 'data.properties.cathode.name#nomad_chemical_energy.schema_packages.ce_necc_package.CE_NECC_EC_GC',
                'title': 'Cathode ID',
                'layout': {
                    'xxl': {'minH': 3, 'minW': 3, 'h': 5, 'w': 6, 'y': 9, 'x': 6},
                    'xl': {'minH': 3, 'minW': 3, 'h': 5, 'w': 6, 'y': 9, 'x': 6},
                    'lg': {'minH': 3, 'minW': 3, 'h': 5, 'w': 6, 'y': 9, 'x': 6},
                    'md': {'minH': 3, 'minW': 3, 'h': 5, 'w': 6, 'y': 9, 'x': 6},
                    'sm': {'minH': 3, 'minW': 3, 'h': 5, 'w': 6, 'y': 9, 'x': 6},
                },
            },
            {
                'type': 'terms',
                'showinput': True,
                'scale': 'linear',
                'quantity': 'data.result_properties.anode_material#nomad_chemical_energy.schema_packages.ce_necc_package.CE_NECC_EC_GC',
                'layout': {
                    'xxl': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 14, 'x': 0},
                    'xl': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 14, 'x': 0},
                    'lg': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 14, 'x': 0},
                    'md': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 14, 'x': 0},
                    'sm': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 14, 'x': 0},
                },
            },
            {
                'type': 'terms',
                'showinput': True,
                'scale': 'linear',
                'quantity': 'data.result_properties.cathode_material#nomad_chemical_energy.schema_packages.ce_necc_package.CE_NECC_EC_GC',
                'layout': {
                    'xxl': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 14, 'x': 6},
                    'xl': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 14, 'x': 6},
                    'lg': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 14, 'x': 6},
                    'md': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 14, 'x': 6},
                    'sm': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 14, 'x': 6},
                },
            },
            {
                'type': 'terms',
                'showinput': True,
                'scale': 'linear',
                'quantity': 'data.result_properties.anode_deposition_method#nomad_chemical_energy.schema_packages.ce_necc_package.CE_NECC_EC_GC',
                'layout': {
                    'xxl': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 18, 'x': 0},
                    'xl': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 18, 'x': 0},
                    'lg': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 18, 'x': 0},
                    'md': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 18, 'x': 0},
                    'sm': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 18, 'x': 0},
                },
            },
            {
                'type': 'terms',
                'showinput': True,
                'scale': 'linear',
                'quantity': 'data.result_properties.cathode_deposition_method#nomad_chemical_energy.schema_packages.ce_necc_package.CE_NECC_EC_GC',
                'layout': {
                    'xxl': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 18, 'x': 6},
                    'xl': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 18, 'x': 6},
                    'lg': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 18, 'x': 6},
                    'md': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 18, 'x': 6},
                    'sm': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 18, 'x': 6},
                },
            },
            {
                'type': 'terms',
                'showinput': True,
                'scale': 'linear',
                'quantity': 'data.result_properties.anode_substrate_type#nomad_chemical_energy.schema_packages.ce_necc_package.CE_NECC_EC_GC',
                'layout': {
                    'xxl': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 22, 'x': 0},
                    'xl': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 22, 'x': 0},
                    'lg': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 22, 'x': 0},
                    'md': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 22, 'x': 0},
                    'sm': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 22, 'x': 0},
                },
            },
            {
                'type': 'terms',
                'showinput': True,
                'scale': 'linear',
                'quantity': 'data.result_properties.cathode_substrate_type#nomad_chemical_energy.schema_packages.ce_necc_package.CE_NECC_EC_GC',
                'layout': {
                    'xxl': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 22, 'x': 6},
                    'xl': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 22, 'x': 6},
                    'lg': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 22, 'x': 6},
                    'md': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 22, 'x': 6},
                    'sm': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 22, 'x': 6},
                },
            },
            {
                'type': 'terms',
                'showinput': True,
                'scale': 'linear',
                'quantity': 'data.result_properties.anode_ionomer_type#nomad_chemical_energy.schema_packages.ce_necc_package.CE_NECC_EC_GC',
                'layout': {
                    'xxl': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 26, 'x': 0},
                    'xl': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 26, 'x': 0},
                    'lg': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 26, 'x': 0},
                    'md': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 26, 'x': 0},
                    'sm': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 26, 'x': 0},
                },
            },
            {
                'type': 'terms',
                'showinput': True,
                'scale': 'linear',
                'quantity': 'data.result_properties.cathode_ionomer_type#nomad_chemical_energy.schema_packages.ce_necc_package.CE_NECC_EC_GC',
                'layout': {
                    'xxl': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 26, 'x': 6},
                    'xl': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 26, 'x': 6},
                    'lg': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 26, 'x': 6},
                    'md': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 26, 'x': 6},
                    'sm': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 26, 'x': 6},
                },
            },
        ]
    },
)
