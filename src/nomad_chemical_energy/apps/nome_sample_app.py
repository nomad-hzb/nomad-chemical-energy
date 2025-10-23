from nomad.config.models.ui import (
    App,
    Axis,
    Column,
    Dashboard,
    FilterMenu,
    FilterMenus,
    Filters,
    FilterMenu,
    FilterMenus,
    FilterMenuSizeEnum,
    Format,
    Layout,
    ModeEnum,
    RowActionNorth,
    RowActions,
    RowActionURL,
    RowDetails,
    Rows,
    RowSelection,
    WidgetHistogram,
    WidgetPeriodicTable,
    WidgetScatterPlot,
    WidgetTerms,
)

schema = 'nomad_chemical_energy.schema_packages.ce_nome_package.CE_NOME_Sample'
nome_sample_app = App(
    # Label of the App
    label='Explore NOME Samples',
    # Path used in the URL, must be unique
    path='nome-samples',
    # Used to categorize apps in the explore menu
    category='NOME Data',
    # Brief description used in the app menu
    description='Search and find your NOME samples.',
    # Longer description that can also use markdown
    readme='Search and find your NOME samples.',
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
            quantity=f'data.lab_id#{schema}',
            label='Sample ID',
            align='left',
            selected=True,
        ),
        Column(
            quantity=f'data.chemical_composition_or_formulas#{schema}',
            label='Materials',
            align='left',
            selected=True,
        ),
        Column(quantity='entry_type', label='Entry type', align='left', selected=False),
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
        'section_defs.definition_qualified_name': f'{schema}'
    },
    filter_menus=FilterMenus(
        options={
            'material': FilterMenu(label='Material', level=0,),
            'elements': FilterMenu(label='Elements / Formula', level=1, size=FilterMenuSizeEnum.XL,),
            'eln': FilterMenu(label='Electronic Lab Notebook', level=0,),
            'custom_quantities': FilterMenu(
                label='User Defined Quantities', level=0, size=FilterMenuSizeEnum.L,
            ),
            'author': FilterMenu(label='Author', size=FilterMenuSizeEnum.M,),
            'metadata': FilterMenu(label='Visibility / IDs', level=0,),
            'optimade': FilterMenu(label='Optimade', level=0, size=FilterMenuSizeEnum.M,),
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
                    'xl': Layout(minH=3, minW=3, h=9, w=12, y=0, x=0),
                    'xxl': Layout(minH=3, minW=3, h=9, w=12, y=0, x=0),
                },
                search_quantity='results.material.elements',
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
                    'sm': Layout(minH=3, minW=3, h=3, w=12, y=9, x=0),
                    'md': Layout(minH=3, minW=3, h=3, w=12, y=9, x=0),
                    'lg': Layout(minH=3, minW=3, h=3, w=12, y=9, x=0),
                    'xl': Layout(minH=3, minW=3, h=3, w=12, y=0, x=12),
                    'xxl': Layout(minH=3, minW=3, h=3, w=12, y=0, x=12),
                },
            ),
            WidgetTerms(
                title='Author Name',
                layout={
                    'sm': Layout(minH=3, minW=3, h=6, w=6, y=12, x=0),
                    'md': Layout(minH=3, minW=3, h=6, w=6, y=12, x=0),
                    'lg': Layout(minH=3, minW=3, h=6, w=6, y=12, x=0),
                    'xl': Layout(minH=3, minW=3, h=6, w=6, y=3, x=12),
                    'xxl': Layout(minH=3, minW=3, h=6, w=6, y=3, x=12),
                },
                search_quantity='authors.name',
                showinput=True,
                scale='linear',
            ),
            WidgetTerms(
                title='Sample IDs',
                layout={
                    'sm': Layout(minH=3, minW=3, h=6, w=6, y=12, x=6),
                    'md': Layout(minH=3, minW=3, h=6, w=6, y=12, x=6),
                    'lg': Layout(minH=3, minW=3, h=6, w=6, y=12, x=6),
                    'xl': Layout(minH=3, minW=3, h=6, w=6, y=3, x=18),
                    'xxl': Layout(minH=3, minW=3, h=6, w=6, y=3, x=18),
                },
                search_quantity='results.eln.lab_ids',
                showinput=True,
                scale='linear',
            ),
            WidgetTerms(
                title='Substrate Type',
                layout={
                    'sm': Layout(minH=3, minW=3, h=6, w=6, y=18, x=0),
                    'md': Layout(minH=3, minW=3, h=6, w=6, y=18, x=0),
                    'lg': Layout(minH=3, minW=3, h=6, w=6, y=18, x=0),
                    'xl': Layout(minH=3, minW=3, h=6, w=6, y=9, x=0),
                    'xxl': Layout(minH=3, minW=3, h=6, w=6, y=9, x=0),
                },
                search_quantity=f'data.substrate.substrate_type#{schema}',
                showinput=True,
                scale='linear',
            ),
            WidgetTerms(
                title='Synthesis Method',
                layout={
                    'sm': Layout(minH=3, minW=3, h=6, w=6, y=18, x=6),
                    'md': Layout(minH=3, minW=3, h=6, w=6, y=18, x=6),
                    'lg': Layout(minH=3, minW=3, h=6, w=6, y=18, x=6),
                    'xl': Layout(minH=3, minW=3, h=6, w=6, y=9, x=6),
                    'xxl': Layout(minH=3, minW=3, h=6, w=6, y=9, x=6),
                },
                search_quantity=f'data.synthesis.method#{schema}',
                showinput=True,
                scale='linear',
            ),
        ]
    ),
)
