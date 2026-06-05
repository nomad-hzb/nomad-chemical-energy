from nomad.config.models.ui import (
    App,
    Column,
    Dashboard,
    FilterMenu,
    FilterMenus,
    FilterMenuSizeEnum,
    Filters,
    Format,
    Layout,
    ModeEnum,
    WidgetTerms,
)

schema_name = 'baseclasses.chemical_energy.voltammetry.Voltammetry'
voltammetry_app = App(
    # Label of the App
    label='Voltammetry',
    # Path used in the URL, must be unique
    path='voltammetry',
    # Used to categorize apps in the explore menu
    category='Experiment',
    # Brief description used in the app menu
    description='An app customized for voltammetries.',
    # Longer description that can also use markdown
    readme='An app customized for voltammetries.',
    # Controls the available search filters. If you want to filter by
    # quantities in a schema package, you need to load the schema package
    # explicitly here. Note that you can use a glob syntax to load the
    # entire package, or just a single schema from a package.
    filters=Filters(
        include=[
            f'*#{schema_name}',
        ]
    ),
    # Dictionary of search filters that are always enabled for queries made
    # within this app. This is especially important to narrow down the
    # results to the wanted subset. Any available search filter can be
    # targeted here. This example makes sure that only entries that use
    # MySchema are included.
    filters_locked={'section_defs.definition_qualified_name': f'{schema_name}'},
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
            'metadata': FilterMenu(label='Visibility / IDs / Schemas', level=0),
        }
    ),
    # Controls which columns are shown in the results table
    columns=[
        Column(
            quantity=f'data.resistance#{schema_name}',
            label='Name',
            align='left',
            selected=True,
        ),
        Column(
            quantity=f'data.voltage_shift#{schema_name}',
            label='Voltage Shift',
            align='left',
            selected=True,
        ),
        Column(
            quantity=f'data.resistance#{schema_name}',
            label='Resistance',
            align='left',
            selected=True,
        ),
        Column(
            quantity='entry_type',
            label='Entry type',
            align='left',
            selected=True,
        ),
        Column(
            quantity='upload_create_time',
            label='Upload time',
            align='left',
            selected=False,
            format=Format(mode=ModeEnum.DATE),
        ),
    ],
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
                title='Measurement | Processes',
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
        ]
    ),
)
