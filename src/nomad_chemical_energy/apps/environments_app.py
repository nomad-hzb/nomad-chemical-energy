from nomad.config.models.ui import (
    App,
    Column,
    FilterMenu,
    FilterMenus,
    FilterMenuSizeEnum,
    Filters,
    Format,
    ModeEnum,
)

schema_name = 'baseclasses.chemical_energy.cesample.Environment'
environments_app = App(
    # Label of the App
    label='Environments',
    # Path used in the URL, must be unique
    path='environments',
    # Used to categorize apps in the explore menu
    category='Experiment',
    # Brief description used in the app menu
    description='An app customized for environments in electro chemistry.',
    # Longer description that can also use markdown
    readme='An app customized for environments in electro chemistry.',
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
            'metadata': FilterMenu(label='Visibility / IDs / Schema', level=0),
        }
    ),
    # Controls which columns are shown in the results table
    columns=[
        Column(
            quantity='results.eln.lab_ids',
            label='ID',
            align='left',
            selected=True,
        ),
        Column(
            quantity=f'data.solvent.name#{schema_name}',
            label='Solvent',
            align='left',
            selected=True,
        ),
        Column(
            quantity=f'data.substances.name#{schema_name}',
            label='Substances',
            align='left',
            selected=True,
        ),
        Column(
            quantity=f'data.ph_value#{schema_name}',
            label='pH',
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
)
