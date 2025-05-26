from nomad.config.models.ui import (
    App,
    Column,
    FilterMenu,
    FilterMenus,
    Filters,
    Format,
    ModeEnum,
)

nome_oer_cp_app = App(
    # Label of the App
    label='Explore OER CP',
    # Path used in the URL, must be unique
    path='nome-oer-cp',
    # Used to categorize apps in the explore menu
    category='NOME Data',
    # Brief description used in the app menu
    description='Provides filters to explore OER CP entries of the NOME group.',
    # Longer description that can also use markdown
    readme='Provides filters to explore OER CP entries of the NOME group.',
    # Controls the available search filters. If you want to filter by
    # quantities in a schema package, you need to load the schema package
    # explicitly here. Note that you can use a glob syntax to load the
    # entire package, or just a single schema from a package.
    filters=Filters(
        include=[
            '*#nomad_chemical_energy.schema_packages.ce_nome_package.CE_NOME_CPAnalysis',
        ]
    ),
    # Controls which columns are shown in the results table
    columns=[
        Column(quantity='entry_name', label='Name', align='left', selected=True),
        Column(
            quantity='upload_name',
            label='Upload name',
            align='left',
            selected=True,
        ),
        Column(
            quantity='data.outputs[0].samples[0].lab_id#nomad_chemical_energy.schema_packages.ce_nome_package.CE_NOME_CPAnalysis',
            label='Sample ID',
            align='left',
            selected=True,
        ),
        Column(quantity='entry_type', label='Entry type', align='left', selected=True),
        Column(
            quantity='entry_create_time',
            label='Entry time',
            align='left',
            selected=True,
            format=Format(mode=ModeEnum.DATE),
        ),
        Column(
            quantity='authors',
            label='Authors',
            align='left',
            selected=True,
        ),
    ],
    # Dictionary of search filters that are always enabled for queries made
    # within this app. This is especially important to narrow down the
    # results to the wanted subset. Any available search filter can be
    # targeted here. This example makes sure that only entries that use
    # MySchema are included.
    filters_locked={
        'section_defs.definition_qualified_name': 'nomad_chemical_energy.schema_packages.ce_nome_package.CE_NOME_CPAnalysis'
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
                'type': 'periodictable',
                'scale': 'linear',
                'quantity': 'results.material.elements',
                'layout': {
                    'xxl': {'minH': 3, 'minW': 3, 'h': 9, 'w': 12, 'y': 0, 'x': 0},
                    'xl': {'minH': 3, 'minW': 3, 'h': 9, 'w': 12, 'y': 0, 'x': 0},
                    'lg': {'minH': 3, 'minW': 3, 'h': 9, 'w': 12, 'y': 0, 'x': 0},
                    'md': {'minH': 3, 'minW': 3, 'h': 9, 'w': 12, 'y': 0, 'x': 0},
                    'sm': {'minH': 3, 'minW': 3, 'h': 9, 'w': 12, 'y': 0, 'x': 0},
                },
            },
            {
                'type': 'terms',
                'showinput': True,
                'scale': 'linear',
                'quantity': 'data.outputs.reaction_type#nomad_chemical_energy.schema_packages.ce_nome_package.CE_NOME_CPAnalysis',
                'layout': {
                    'xxl': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 0, 'x': 12},
                    'xl': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 0, 'x': 12},
                    'lg': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 0, 'x': 12},
                    'md': {'minH': 3, 'minW': 3, 'h': 5, 'w': 6, 'y': 9, 'x': 0},
                    'sm': {'minH': 3, 'minW': 3, 'h': 5, 'w': 6, 'y': 12, 'x': 0},
                },
            },
            {
                'type': 'terms',
                'showinput': True,
                'scale': 'linear',
                'title': 'Current Density',
                'quantity': 'data.outputs.current_density_string#nomad_chemical_energy.schema_packages.ce_nome_package.CE_NOME_CPAnalysis',
                'layout': {
                    'xxl': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 0, 'x': 18},
                    'xl': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 0, 'x': 18},
                    'lg': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 0, 'x': 18},
                    'md': {'minH': 3, 'minW': 3, 'h': 5, 'w': 6, 'y': 9, 'x': 6},
                    'sm': {'minH': 3, 'minW': 3, 'h': 5, 'w': 6, 'y': 12, 'x': 6},
                },
            },
            {
                'type': 'histogram',
                'showinput': True,
                'autorange': False,
                'nbins': 30,
                'scale': 'linear',
                'title': 'Duration',
                'quantity': 'data.outputs.experiment_duration#nomad_chemical_energy.schema_packages.ce_nome_package.CE_NOME_CPAnalysis',
                'layout': {
                    'xxl': {'minH': 3, 'minW': 3, 'h': 3, 'w': 12, 'y': 6, 'x': 12},
                    'xl': {'minH': 3, 'minW': 3, 'h': 3, 'w': 12, 'y': 6, 'x': 12},
                    'lg': {'minH': 3, 'minW': 3, 'h': 3, 'w': 12, 'y': 6, 'x': 12},
                    'md': {'minH': 3, 'minW': 3, 'h': 3, 'w': 12, 'y': 14, 'x': 0},
                    'sm': {'minH': 3, 'minW': 3, 'h': 3, 'w': 12, 'y': 9, 'x': 0},
                },
            },
            {
                'type': 'histogram',
                'showinput': True,
                'autorange': False,
                'nbins': 30,
                'scale': 'linear',
                'title': 'Δj',
                'quantity': 'data.outputs.voltage_difference#nomad_chemical_energy.schema_packages.ce_nome_package.CE_NOME_CPAnalysis',
                'layout': {
                    'xxl': {'minH': 3, 'minW': 3, 'h': 6, 'w': 9, 'y': 9, 'x': 9},
                    'xl': {'minH': 3, 'minW': 3, 'h': 6, 'w': 9, 'y': 9, 'x': 9},
                    'lg': {'minH': 3, 'minW': 3, 'h': 6, 'w': 12, 'y': 9, 'x': 12},
                    'md': {'minH': 3, 'minW': 3, 'h': 6, 'w': 9, 'y': 17, 'x': 9},
                    'sm': {'minH': 3, 'minW': 3, 'h': 5, 'w': 6, 'y': 17, 'x': 6},
                },
            },
            {
                'type': 'scatterplot',
                'autorange': True,
                'size': 1000,
                'x': {
                    'quantity': 'data.outputs[*].voltage_avg_first5#nomad_chemical_energy.schema_packages.ce_nome_package.CE_NOME_CPAnalysis',
                    'unit': 'volt',
                },
                'y': {
                    'quantity': 'data.outputs[*].voltage_avg_last5#nomad_chemical_energy.schema_packages.ce_nome_package.CE_NOME_CPAnalysis',
                    'unit': 'volt',
                },
                'layout': {
                    'xxl': {'minH': 3, 'minW': 3, 'h': 6, 'w': 9, 'y': 9, 'x': 0},
                    'xl': {'minH': 3, 'minW': 3, 'h': 6, 'w': 9, 'y': 9, 'x': 0},
                    'lg': {'minH': 3, 'minW': 3, 'h': 6, 'w': 12, 'y': 9, 'x': 0},
                    'md': {'minH': 3, 'minW': 3, 'h': 6, 'w': 9, 'y': 17, 'x': 0},
                    'sm': {'minH': 3, 'minW': 3, 'h': 5, 'w': 6, 'y': 17, 'x': 0},
                },
            },
            {
                'type': 'histogram',
                'showinput': True,
                'autorange': False,
                'nbins': 30,
                'scale': 'linear',
                'title': 'Voltage shift',
                'quantity': 'data.outputs.voltage_shift#nomad_chemical_energy.schema_packages.ce_nome_package.CE_NOME_CPAnalysis',
                'layout': {
                    'xxl': {'minH': 3, 'minW': 3, 'h': 6, 'w': 9, 'y': 15, 'x': 0},
                    'xl': {'minH': 3, 'minW': 3, 'h': 5, 'w': 9, 'y': 15, 'x': 0},
                    'lg': {'minH': 3, 'minW': 3, 'h': 6, 'w': 12, 'y': 15, 'x': 0},
                    'md': {'minH': 3, 'minW': 3, 'h': 6, 'w': 9, 'y': 23, 'x': 0},
                    'sm': {'minH': 3, 'minW': 3, 'h': 5, 'w': 6, 'y': 22, 'x': 0},
                },
            },
            {
                'type': 'histogram',
                'showinput': True,
                'autorange': False,
                'nbins': 30,
                'scale': 'linear',
                'title': 'R',
                'quantity': 'data.outputs.resistance#nomad_chemical_energy.schema_packages.ce_nome_package.CE_NOME_CPAnalysis',
                'layout': {
                    'xxl': {'minH': 3, 'minW': 3, 'h': 6, 'w': 9, 'y': 15, 'x': 9},
                    'xl': {'minH': 3, 'minW': 3, 'h': 6, 'w': 9, 'y': 15, 'x': 9},
                    'lg': {'minH': 3, 'minW': 3, 'h': 6, 'w': 12, 'y': 15, 'x': 12},
                    'md': {'minH': 3, 'minW': 3, 'h': 6, 'w': 9, 'y': 23, 'x': 9},
                    'sm': {'minH': 3, 'minW': 3, 'h': 5, 'w': 6, 'y': 22, 'x': 6},
                },
            },
            {
                'type': 'terms',
                'showinput': True,
                'scale': 'linear',
                'quantity': 'authors.name',
                'layout': {
                    'xxl': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 21, 'x': 0},
                    'xl': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 21, 'x': 0},
                    'lg': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 21, 'x': 0},
                    'md': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 29, 'x': 0},
                    'sm': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 27, 'x': 0},
                },
            },
            {
                'type': 'histogram',
                'showinput': True,
                'autorange': False,
                'nbins': 30,
                'scale': 'linear',
                'title': 'Entry Create Time',
                'quantity': 'entry_create_time',
                'layout': {
                    'xxl': {'minH': 3, 'minW': 3, 'h': 6, 'w': 12, 'y': 21, 'x': 6},
                    'xl': {'minH': 3, 'minW': 3, 'h': 6, 'w': 12, 'y': 21, 'x': 6},
                    'lg': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 21, 'x': 6},
                    'md': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 29, 'x': 6},
                    'sm': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 27, 'x': 6},
                },
            },
        ]
    },
)
