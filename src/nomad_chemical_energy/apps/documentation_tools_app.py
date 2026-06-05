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

schema_name = 'baseclasses.documentation_tool.DocumentationTool'
documentation_tools_app = App(
    # Label of the App
    label='Documentation Tools',
    # Path used in the URL, must be unique
    path='doctool',
    # Used to categorize apps in the explore menu
    category='NOME Data',
    # Brief description used in the app menu
    description='Search and find your documentation tools.',
    # Longer description that can also use markdown
    readme='Search and find your documentation tools.',
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
            'custom_quantities': FilterMenu(
                label='User Defined Quantities', size=FilterMenuSizeEnum.L, level=0
            ),
            'author': FilterMenu(
                label='Author / Origin / Dataset', size=FilterMenuSizeEnum.M, level=0
            ),
            'metadata': FilterMenu(label='Visibility / IDs / Schema', level=0),
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
            quantity='entry_create_time',
            label='Entry time',
            align='left',
            selected=True,
            format=Format(mode=ModeEnum.DATE),
        ),
        Column(
            quantity='entry_type',
            label='Entry type',
            align='left',
            selected=True,
        ),
        Column(
            quantity='authors',
            label='Authors',
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
        ]
    ),
)
