from nomad.config.models.ui import (
    App,
    Column,
    Dashboard,
    FilterMenu,
    FilterMenus,
    FilterMenuSizeEnum,
    Format,
    Layout,
    ModeEnum,
    RowActions,
    RowDetails,
    Rows,
    RowSelection,
    WidgetTerms,
)

eln_app = App(
    # Label of the App
    label='HZB ELN',
    # Path used in the URL, must be unique
    path='eln',
    # resource='entries',
    breadcrumb='ELN',
    # Used to categorize apps in the explore menu
    category='General Apps',
    # Brief description used in the app menu
    description='Search your experimental data',
    # Longer description that can also use markdown
    readme='### Experiments search \n'
    'This page allows you to search **your experimental data** within the HZB-NOMAD.',
    # Dictionary of search filters that are always enabled for queries made
    # within this app. This is especially important to narrow down the
    # results to the wanted subset. Any available search filter can be
    # targeted here. This example makes sure that only entries that use
    # MySchema are included.
    filters_locked={'quantities': 'data'},
    filter_menus=FilterMenus(
        options={
            'material': FilterMenu(label='Material', level=0),
            'elements': FilterMenu(label='Elements / Formula', level=1, size='xl'),
            'eln': FilterMenu(label='Electronic Lab Notebook', level=0),
            'custom_quantities': FilterMenu(
                label='User Defined Quantities', size=FilterMenuSizeEnum.L, level=0
            ),
            'author': FilterMenu(
                label='Author / Origin / Dataset', size=FilterMenuSizeEnum.M, level=0
            ),
            'metadata': FilterMenu(label='Visibility / IDs / Schema', level=0),
            'optimade': FilterMenu(label='Optimade', level=0, size='m'),
        }
    ),
    # Controls which columns are shown in the results table
    columns=[
        Column(
            quantity='entry_name',
            label='Name',
            align='left',
            selected=True,
        ),
        Column(
            quantity='results.eln.methods',
            label='Methods',
            align='left',
            selected=True,
        ),
        Column(
            quantity='results.eln.lab_ids',
            label='ID',
            align='left',
            selected=True,
        ),
        Column(
            quantity='results.material.chemical_formula_hill',
            label='Formula',
            align='left',
            selected=False,
        ),
        Column(
            quantity='entry_type',
            label='Entry type',
            align='left',
            selected=True,
        ),
        Column(
            quantity='upload_name',
            label='Upload name',
            align='left',
            selected=True,
        ),
        Column(
            quantity='upload_id',
            label='Upload id',
            align='left',
            selected=False,
        ),
        Column(
            quantity='upload_create_time',
            label='Upload time',
            align='left',
            selected=False,
            format=Format(mode=ModeEnum.DATE),
        ),
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
    rows=Rows(
        actions=RowActions(enabled=True),
        details=RowDetails(enabled=True),
        selection=RowSelection(enabled=True),
    ),
    # Controls the default dashboard shown in the search interface
    dashboard=Dashboard(
        widgets=[
            WidgetTerms(
                title='Author name',
                layout={
                    'sm': Layout(minH=3, minW=3, h=6, w=6, y=0, x=0),
                    'md': Layout(minH=3, minW=3, h=6, w=6, y=0, x=0),
                    'lg': Layout(minH=3, minW=3, h=6, w=6, y=0, x=0),
                    'xl': Layout(minH=3, minW=3, h=6, w=6, y=0, x=0),
                    'xxl': Layout(minH=3, minW=3, h=6, w=6, y=0, x=0),
                },
                search_quantity='authors.name',
                showinput=True,
                scale='linear',
            ),
            WidgetTerms(
                title='Methods',
                layout={
                    'sm': Layout(minH=3, minW=3, h=6, w=6, y=0, x=6),
                    'md': Layout(minH=3, minW=3, h=6, w=6, y=0, x=6),
                    'lg': Layout(minH=3, minW=3, h=6, w=6, y=0, x=6),
                    'xl': Layout(minH=3, minW=3, h=6, w=6, y=0, x=6),
                    'xxl': Layout(minH=3, minW=3, h=6, w=6, y=0, x=6),
                },
                search_quantity='results.eln.methods',
                showinput=True,
                scale='linear',
            ),
            WidgetTerms(
                title='Lab IDs',
                layout={
                    'sm': Layout(minH=3, minW=3, h=6, w=6, y=6, x=0),
                    'md': Layout(minH=3, minW=3, h=6, w=6, y=0, x=12),
                    'lg': Layout(minH=3, minW=3, h=6, w=6, y=0, x=12),
                    'xl': Layout(minH=3, minW=3, h=6, w=6, y=0, x=12),
                    'xxl': Layout(minH=3, minW=3, h=6, w=6, y=0, x=12),
                },
                search_quantity='results.eln.lab_ids',
                showinput=True,
                scale='linear',
            ),
            WidgetTerms(
                title='Sections',
                layout={
                    'sm': Layout(minH=3, minW=3, h=6, w=6, y=6, x=6),
                    'md': Layout(minH=3, minW=3, h=6, w=6, y=6, x=0),
                    'lg': Layout(minH=3, minW=3, h=6, w=6, y=0, x=18),
                    'xl': Layout(minH=3, minW=3, h=6, w=6, y=0, x=18),
                    'xxl': Layout(minH=3, minW=3, h=6, w=6, y=0, x=18),
                },
                search_quantity='results.eln.sections',
                showinput=True,
                scale='linear',
            ),
        ]
    ),
)
