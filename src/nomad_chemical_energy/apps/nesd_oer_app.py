from nomad.config.models.ui import (
    App,
    Axis,
    Column,
    Dashboard,
    FilterMenu,
    FilterMenus,
    Filters,
    Format,
    Layout,
    ModeEnum,
    WidgetHistogram,
    WidgetPeriodicTable,
    WidgetScatterPlot,
    WidgetTerms,
)

schema = 'nomad_chemical_energy.schema_packages.ce_nesd_package.CE_NESD_OERAnalysis'
nesd_oer_app = App(
    # Label of the App
    label='Explore OER Analysis',
    # Path used in the URL, must be unique
    path='nesd-oer',
    # Used to categorize apps in the explore menu
    category='NESD Data',
    # Brief description used in the app menu
    description='Provides filters to explore OER entries of the NESD group.',
    # Longer description that can also use markdown
    readme='Provides filters to explore OER entries of the NESD group.',
    # Controls the available search filters. If you want to filter by
    # quantities in a schema package, you need to load the schema package
    # explicitly here. Note that you can use a glob syntax to load the
    # entire package, or just a single schema from a package.
    filters=Filters(
        include=[
            f'*#{schema}',
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
            quantity=f'data.outputs[0].samples[0].name#{schema}',
            label='Working Electrode',
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
    filters_locked={'section_defs.definition_qualified_name': f'{schema}'},
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
    dashboard=Dashboard(
        widgets=[
            WidgetPeriodicTable(
                title='Elements of the sample',
                layout={
                    'sm': Layout(minH=3, minW=3, h=9, w=12, y=0, x=0),
                    'md': Layout(minH=3, minW=3, h=9, w=12, y=0, x=0),
                    'lg': Layout(minH=3, minW=3, h=9, w=12, y=0, x=0),
                    'xl': Layout(minH=3, minW=3, h=10, w=12, y=0, x=0),
                    'xxl': Layout(minH=3, minW=3, h=10, w=12, y=0, x=0),
                },
                search_quantity='results.material.elements',
                scale='linear',
            ),
            WidgetHistogram(
                title='Overpotential',
                show_input=True,
                autorange=False,
                nbins=30,
                scale='linear',
                x=Axis(
                    search_quantity=f'data.outputs.overpotential_at_10mA_cm2#{schema}'
                ),
                layout={
                    'sm': Layout(minH=3, minW=3, h=3, w=12, y=9, x=12),
                    'md': Layout(minH=3, minW=3, h=3, w=12, y=9, x=12),
                    'lg': Layout(minH=3, minW=3, h=3, w=12, y=9, x=12),
                    'xl': Layout(minH=3, minW=3, h=3, w=12, y=0, x=12),
                    'xxl': Layout(minH=3, minW=3, h=3, w=12, y=0, x=12),
                },
            ),
            WidgetHistogram(
                title='Charge Density',
                show_input=True,
                autorange=False,
                nbins=30,
                scale='linear',
                x=Axis(search_quantity=f'data.outputs.charge_density#{schema}'),
                layout={
                    'sm': Layout(minH=3, minW=3, h=3, w=12, y=12, x=12),
                    'md': Layout(minH=3, minW=3, h=3, w=12, y=12, x=12),
                    'lg': Layout(minH=3, minW=3, h=3, w=12, y=12, x=12),
                    'xl': Layout(minH=3, minW=3, h=3, w=12, y=3, x=12),
                    'xxl': Layout(minH=3, minW=3, h=3, w=12, y=3, x=12),
                },
            ),
            WidgetTerms(
                title='Reaction Type',
                layout={
                    'sm': Layout(minH=3, minW=3, h=6, w=6, y=15, x=0),
                    'md': Layout(minH=3, minW=3, h=6, w=6, y=15, x=0),
                    'lg': Layout(minH=3, minW=3, h=6, w=6, y=15, x=0),
                    'xl': Layout(minH=3, minW=3, h=4, w=6, y=6, x=12),
                    'xxl': Layout(minH=3, minW=3, h=4, w=6, y=6, x=12),
                },
                search_quantity=f'data.outputs.reaction_type#{schema}',
                showinput=True,
                scale='linear',
            ),
            WidgetTerms(
                title='Author Name',
                layout={
                    'sm': Layout(minH=3, minW=3, h=6, w=6, y=21, x=0),
                    'md': Layout(minH=3, minW=3, h=6, w=6, y=21, x=0),
                    'lg': Layout(minH=3, minW=3, h=6, w=6, y=21, x=0),
                    'xl': Layout(minH=3, minW=3, h=8, w=8, y=10, x=0),
                    'xxl': Layout(minH=3, minW=3, h=8, w=8, y=10, x=0),
                },
                search_quantity='authors.name',
                showinput=True,
                scale='linear',
            ),
            WidgetHistogram(
                title='Entry Create Time',
                show_input=True,
                autorange=False,
                nbins=30,
                scale='linear',
                x=Axis(search_quantity='entry_create_time'),
                layout={
                    'sm': Layout(minH=3, minW=3, h=6, w=12, y=21, x=6),
                    'md': Layout(minH=3, minW=3, h=6, w=12, y=21, x=6),
                    'lg': Layout(minH=3, minW=3, h=6, w=6, y=21, x=6),
                    'xl': Layout(minH=3, minW=3, h=8, w=8, y=10, x=6),
                    'xxl': Layout(minH=3, minW=3, h=8, w=8, y=10, x=6),
                },
            ),
            WidgetScatterPlot(
                title='Overpotential vs Charge Density',
                autorange=True,
                x=Axis(
                    search_quantity=f'data.outputs[0].charge_density#{schema}',
                    unit='mC/cm**2',
                    scale='linear',
                ),
                y=Axis(
                    search_quantity=f'data.outputs[0].overpotential_at_10mA_cm2#{schema}',
                    unit='volt',
                    scale='linear',
                ),
                color=f'data.outputs[0].samples[0].name#{schema}',
                size=3000,  # maximum number of entries loaded
                layout={
                    'sm': Layout(minH=3, minW=3, h=6, w=6, y=27, x=0),
                    'md': Layout(minH=3, minW=3, h=6, w=6, y=27, x=0),
                    'lg': Layout(minH=3, minW=3, h=6, w=6, y=27, x=0),
                    'xl': Layout(minH=3, minW=3, h=8, w=8, y=10, x=12),
                    'xxl': Layout(minH=3, minW=3, h=8, w=8, y=10, x=12),
                },
            ),
        ]
    ),
)
