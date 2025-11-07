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
    WidgetScatterPlot,
    WidgetTerms,
)

schema = 'nomad_chemical_energy.schema_packages.ce_necc_package.CE_NECC_EC_GC'

necc_compare_app = App(
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
            '*#{schema}',
            #'*#nomad_chemical_energy.schema_packages.ce_necc_package.CE_NECC_Electrode',
            #'*#nomad_chemical_energy.schema_packages.ce_necc_package.CE_NECC_ElectrodeRecipe',
        ]
    ),
    # Controls which columns are shown in the results table
    columns=[
        Column(quantity='entry_type', label='Entry type', align='left', selected=False),
        Column(quantity='entry_name', label='Name', align='left', selected=True),
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
        Column(
            quantity='upload_name',
            label='Upload name',
            align='left',
            selected=True,
        ),
        Column(
            quantity=f'data.lab_id#{schema}',
            label='Experiment ID',
            align='left',
            selected=True,
        ),
        Column(
            quantity=f'data.properties.cathode.lab_id#{schema}',
            label='Cathode ID',
            align='left',
            selected=True,
        ),
        Column(
            quantity=f'data.properties.anode.lab_id#{schema}',
            label='Anode ID',
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
            WidgetTerms(
                title='Author Name',
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
            WidgetHistogram(
                title='Minimal FE per gas (in %)',
                show_input=True,
                autorange=False,
                nbins=30,
                scale='1/4',
                x=Axis(
                    search_quantity=f'data.fe_results.gas_results.minimum_fe#{schema}'
                ),
                layout={
                    'sm': Layout(minH=3, minW=3, h=6, w=12, y=18, x=0),
                    'md': Layout(minH=3, minW=3, h=6, w=12, y=18, x=0),
                    'lg': Layout(minH=3, minW=3, h=6, w=12, y=18, x=0),
                    'xl': Layout(minH=3, minW=3, h=6, w=12, y=18, x=0),
                    'xxl': Layout(minH=3, minW=3, h=6, w=12, y=18, x=0),
                },
            ),
            WidgetTerms(
                title='Cell type',
                layout={
                    'sm': Layout(minH=3, minW=3, h=6, w=6, y=6, x=0),
                    'md': Layout(minH=3, minW=3, h=6, w=6, y=6, x=0),
                    'lg': Layout(minH=3, minW=3, h=6, w=6, y=6, x=0),
                    'xl': Layout(minH=3, minW=3, h=6, w=6, y=6, x=0),
                    'xxl': Layout(minH=3, minW=3, h=6, w=6, y=6, x=0),
                },
                search_quantity=f'data.properties.cell_type#{schema}',
                showinput=True,
                scale='linear',
            ),
            WidgetTerms(
                title='Anolyte type',
                layout={
                    'sm': Layout(minH=3, minW=3, h=6, w=6, y=6, x=6),
                    'md': Layout(minH=3, minW=3, h=6, w=6, y=6, x=6),
                    'lg': Layout(minH=3, minW=3, h=6, w=6, y=6, x=6),
                    'xl': Layout(minH=3, minW=3, h=6, w=6, y=6, x=6),
                    'xxl': Layout(minH=3, minW=3, h=6, w=6, y=6, x=6),
                },
                search_quantity=f'data.properties.anolyte_type#{schema}',
                showinput=True,
                scale='linear',
            ),
            WidgetTerms(
                title='Membrane type',
                layout={
                    'sm': Layout(minH=3, minW=3, h=6, w=6, y=12, x=0),
                    'md': Layout(minH=3, minW=3, h=6, w=6, y=12, x=0),
                    'lg': Layout(minH=3, minW=3, h=6, w=6, y=12, x=0),
                    'xl': Layout(minH=3, minW=3, h=6, w=6, y=12, x=0),
                    'xxl': Layout(minH=3, minW=3, h=6, w=6, y=12, x=0),
                },
                search_quantity=f'data.properties.membrane_type#{schema}',
                showinput=True,
                scale='linear',
            ),
            WidgetTerms(
                title='Membrane name',
                layout={
                    'sm': Layout(minH=3, minW=3, h=6, w=6, y=12, x=6),
                    'md': Layout(minH=3, minW=3, h=6, w=6, y=12, x=6),
                    'lg': Layout(minH=3, minW=3, h=6, w=6, y=12, x=6),
                    'xl': Layout(minH=3, minW=3, h=6, w=6, y=12, x=6),
                    'xxl': Layout(minH=3, minW=3, h=6, w=6, y=12, x=6),
                },
                search_quantity=f'data.properties.membrane_name#{schema}',
                showinput=True,
                scale='linear',
            ),
            WidgetScatterPlot(
                title='CO FE',
                autorange=True,
                x=Axis(
                    search_quantity=f'data.properties.anolyte_concentration#{schema}',
                    title='Anolyte Concentration',
                    unit='mol / l',
                    scale='linear',
                ),
                y=Axis(
                    title='CO FE',
                    search_quantity=f'data.fe_results.gas_results[0].minimum_fe#{schema}',
                    unit='%',
                    scale='linear',
                ),
                color=f'data.properties.anolyte_type#{schema}',
                size=3000,  # maximum number of entries loaded
                layout={
                    'sm': Layout(minH=3, minW=3, h=6, w=12, y=24, x=0),
                    'md': Layout(minH=3, minW=3, h=6, w=12, y=24, x=0),
                    'lg': Layout(minH=3, minW=3, h=6, w=12, y=0, x=12),
                    'xl': Layout(minH=3, minW=3, h=6, w=12, y=0, x=12),
                    'xxl': Layout(minH=3, minW=3, h=6, w=12, y=0, x=12),
                },
            ),
            WidgetScatterPlot(
                title='CH4 FE',
                autorange=True,
                x=Axis(
                    search_quantity=f'data.properties.anolyte_concentration#{schema}',
                    title='Anolyte Concentration',
                    unit='mol / l',
                    scale='linear',
                ),
                y=Axis(
                    title='CH4 FE',
                    search_quantity=f'data.fe_results.gas_results[1].minimum_fe#{schema}',
                    unit='%',
                    scale='linear',
                ),
                color=f'data.properties.anolyte_type#{schema}',
                size=3000,  # maximum number of entries loaded
                layout={
                    'sm': Layout(minH=3, minW=3, h=6, w=12, y=30, x=0),
                    'md': Layout(minH=3, minW=3, h=6, w=12, y=30, x=0),
                    'lg': Layout(minH=3, minW=3, h=6, w=12, y=6, x=12),
                    'xl': Layout(minH=3, minW=3, h=6, w=12, y=6, x=12),
                    'xxl': Layout(minH=3, minW=3, h=6, w=12, y=6, x=12),
                },
            ),
            WidgetScatterPlot(
                title='C2H4 FE',
                autorange=True,
                x=Axis(
                    search_quantity=f'data.properties.anolyte_concentration#{schema}',
                    title='Anolyte Concentration',
                    unit='mol / l',
                    scale='linear',
                ),
                y=Axis(
                    title='C2H4 FE',
                    search_quantity=f'data.fe_results.gas_results[2].minimum_fe#{schema}',
                    unit='%',
                    scale='linear',
                ),
                color=f'data.properties.anolyte_type#{schema}',
                size=3000,  # maximum number of entries loaded
                layout={
                    'sm': Layout(minH=3, minW=3, h=6, w=12, y=36, x=0),
                    'md': Layout(minH=3, minW=3, h=6, w=12, y=36, x=0),
                    'lg': Layout(minH=3, minW=3, h=6, w=12, y=12, x=12),
                    'xl': Layout(minH=3, minW=3, h=6, w=12, y=12, x=12),
                    'xxl': Layout(minH=3, minW=3, h=6, w=12, y=12, x=12),
                },
            ),
            WidgetScatterPlot(
                title='H2 FE',
                autorange=True,
                x=Axis(
                    search_quantity=f'data.properties.anolyte_concentration#{schema}',
                    title='Anolyte Concentration',
                    unit='mol / l',
                    scale='linear',
                ),
                y=Axis(
                    title='H2 FE',
                    search_quantity=f'data.fe_results.gas_results[3].minimum_fe#{schema}',
                    unit='%',
                    scale='linear',
                ),
                color=f'data.properties.anolyte_type#{schema}',
                size=3000,  # maximum number of entries loaded
                layout={
                    'sm': Layout(minH=3, minW=3, h=6, w=12, y=42, x=0),
                    'md': Layout(minH=3, minW=3, h=6, w=12, y=42, x=0),
                    'lg': Layout(minH=3, minW=3, h=6, w=12, y=18, x=12),
                    'xl': Layout(minH=3, minW=3, h=6, w=12, y=18, x=12),
                    'xxl': Layout(minH=3, minW=3, h=6, w=12, y=18, x=12),
                },
            ),
        ],
    ),
)
