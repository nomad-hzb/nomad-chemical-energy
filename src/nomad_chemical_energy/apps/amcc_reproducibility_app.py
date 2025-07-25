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
    WidgetScatterPlot,
    WidgetTerms,
)

schema = (
    'nomad_chemical_energy.schema_packages.ce_amcc_package.CE_AMCC_ReproducibilityStudy'
)
amcc_reproducibility_app = App(
    # Label of the App
    label='Explore Reproducibility Study',
    # Path used in the URL, must be unique
    path='amcc-reproducibility',
    # Used to categorize apps in the explore menu
    category='AMCC Data',
    # Brief description used in the app menu
    description='Provides filters to explore entries of the reproducibility study.',
    # Longer description that can also use markdown
    readme='Provides filters to explore entries of the reproducibility study.',
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
    filters_locked={'section_defs.definition_qualified_name': [schema]},
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
                title='Group Name',
                layout={
                    'lg': Layout(minH=3, minW=3, h=7, w=6, y=0, x=0),
                    'sm': Layout(minH=3, minW=3, h=7, w=6, y=0, x=0),
                },
                search_quantity=f'data.group_name#{schema}',
                showinput=True,
                scale='linear',
            ),
            WidgetTerms(
                title='Procedure Number',
                layout={
                    'lg': Layout(minH=3, minW=3, h=7, w=6, y=0, x=6),
                    'sm': Layout(minH=3, minW=3, h=7, w=6, y=0, x=6),
                },
                search_quantity=f'data.procedure_number#{schema}',
                showinput=True,
                scale='linear',
            ),
            WidgetScatterPlot(
                title='Overpotential at 1 mA/cm² (mV)',
                autorange=True,
                x=Axis(
                    search_quantity=f'data.cv_metrics[*].overpotential_at_1_mA_cm2#{schema}',
                    title='Overpotential at 1 mA/cm²',
                    unit='mV',
                    scale='linear',
                ),
                y=Axis(
                    search_quantity=f'data.cv_metrics[*].cycle_number#{schema}',
                    unit='dimensionless',
                    scale='linear',
                ),
                color=f'data.cv_metrics[*].study_type#{schema}',
                size=1000,  # maximum number of entries loaded
                layout={'md': Layout(minH=3, minW=3, h=5, w=18, y=8, x=0)},
            ),
            WidgetScatterPlot(
                title='Current Density at 1.5 V RHE (mA/cm²)',
                autorange=True,
                x=Axis(
                    search_quantity=f'data.cv_metrics[*].current_density_at_1_5_RHE#{schema}',
                    title='Current Density at 1.5 V RHE',
                    unit='mA/cm**2',
                    scale='log',
                ),
                y=Axis(
                    search_quantity=f'data.cv_metrics[*].cycle_number#{schema}',
                    unit='dimensionless',
                    scale='linear',
                ),
                color=f'data.cv_metrics[*].study_type#{schema}',
                size=1000,  # maximum number of entries loaded
                layout={'lg': Layout(minH=3, minW=3, h=5, w=18, y=13, x=0)},
            ),
            WidgetScatterPlot(
                title='Reduction Peak Integral (mC)',
                autorange=True,
                x=Axis(
                    search_quantity=f'data.cv_metrics[*].reduction_peak_integral#{schema}',
                    unit='mC',
                    scale='linear',
                ),
                y=Axis(
                    search_quantity=f'data.cv_metrics[*].cycle_number#{schema}',
                    unit='dimensionless',
                    scale='linear',
                ),
                color=f'data.cv_metrics[*].study_type#{schema}',
                size=1000,  # maximum number of entries loaded
                layout={'lg': Layout(minH=3, minW=3, h=5, w=18, y=18, x=0)},
            ),
            WidgetScatterPlot(
                title='Tafel slope (mV/dec)',
                autorange=True,
                x=Axis(
                    search_quantity=f'data.cv_metrics[*].tafel_slope#{schema}',
                    unit='dimensionless',
                    scale='linear',
                ),
                y=Axis(
                    search_quantity=f'data.cv_metrics[*].cycle_number#{schema}',
                    unit='dimensionless',
                    scale='linear',
                ),
                color=f'data.cv_metrics[*].study_type#{schema}',
                size=1000,  # maximum number of entries loaded
                layout={'lg': Layout(minH=3, minW=3, h=5, w=18, y=23, x=0)},
            ),
        ]
    ),
)
