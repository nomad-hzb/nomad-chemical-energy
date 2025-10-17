from nomad.config.models.ui import (
    App,
    Column,
    Columns,
    FilterMenu,
    FilterMenus,
    Filters,
)

catlab_pixel_app = App(
    label='Library pixel explorer',
    path='catlab-pixels',
    category='High-Throughput Experimentation',
    description="""
    Explore the pixels from HZB's material library samples.
    """,
    readme="""
    Explore combinatorial libraries and samples.
    """,
    filters=Filters(
        include=[
            '*#nomad_chemical_energy.schema_packages.hzb_catlab_package.CatLab_XYSample',
        ]
    ),
    columns=Columns(
        selected=[
            'results.material.elements',
            'entry_type',
        ],
        options={
            'entry_type': Column(label='Entry type', align='left'),
            'entry_name': Column(label='Name', align='left'),
            'entry_create_time': Column(label='Entry time', align='left'),
            'authors': Column(label='Authors', align='left'),
            'upload_name': Column(label='Upload name', align='left'),
            'results.material.elements': Column(label='Elements', align='left'),
        },
    ),
    filters_locked={
        'section_defs.definition_qualified_name': 'nomad_chemical_energy.schema_packages.hzb_catlab_package.CatLab_XYSample'
    },
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

    dashboard={
        'widgets': [

            # Element selector (periodic table)
            {
                'type': 'periodictable',
                'search_quantity': 'results.material.elements',
                'title': 'Material composition',
                'layout': {
                    'xxl': {'minH': 3, 'minW': 3, 'h': 9, 'w': 12, 'y': 0, 'x': 0},
                    'xl': {'minH': 3, 'minW': 3, 'h': 6, 'w': 9, 'y': 0, 'x': 4},
                    'lg': {'minH': 3, 'minW': 3, 'h': 6, 'w': 11, 'y': 0, 'x': 4},
                    'md': {'minH': 3, 'minW': 3, 'h': 9, 'w': 12, 'y': 3, 'x': 0},
                    'sm': {'minH': 3, 'minW': 3, 'h': 9, 'w': 12, 'y': 0, 'x': 0},
                },
            },


            # library selector (terms)
            {
                'type': 'terms',
                'show_input': True,
                'search_quantity': 'data.library.name#nomad_chemical_energy.schema_packages.hzb_catlab_package.CatLab_XYSample',
                'title': 'Select one',
                'layout': {
                    'xxl': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 0, 'x': 6},
                    'xl': {'minH': 3, 'minW': 3, 'h': 13, 'w': 4, 'y': 0, 'x': 0},
                    'lg': {'minH': 3, 'minW': 3, 'h': 18, 'w': 4, 'y': 0, 'x': 0},
                    'md': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 12, 'x': 0},
                    'sm': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 0, 'x': 6},
                },
            },


            # thickness selector (histogram)
            {
                'type': 'histogram',
                'show_input': True,
                'autorange': False,
                'nbins': 30,
                'y': {
                    'scale': 'linear',
                },
                'x': {
                    'title': 'Thickness',
                    'unit': 'nm',
                    'search_quantity': 'data.thickness.value#nomad_chemical_energy.schema_packages.hzb_catlab_package.CatLab_XYSample',
                    'scale': 'linear',
                },
                'title': 'Select',
                'layout': {
                    'xxl': {'minH': 3, 'minW': 3, 'h': 3, 'w': 8, 'y': 0, 'x': 0},
                    'xl': {'minH': 3, 'minW': 3, 'h': 3, 'w': 8, 'y': 3, 'x': 13},
                    'lg': {'minH': 3, 'minW': 3, 'h': 3, 'w': 9, 'y': 0, 'x': 15},
                    'md': {'minH': 3, 'minW': 3, 'h': 3, 'w': 8, 'y': 0, 'x': 8},
                    'sm': {'minH': 3, 'minW': 3, 'h': 3, 'w': 8, 'y': 0, 'x': 0},
                },
            },


            # atomic fraction selector (histogram)
            {
                'type': 'histogram',
                'show_input': True,
                'autorange': True,
                'nbins': 30,
                'y': {
                    'scale': 'linear',
                },
                'x': {
                    'title': 'Atomic fraction',
                    'search_quantity': 'data.elemental_composition.atomic_fraction#nomad_chemical_energy.schema_packages.hzb_catlab_package.CatLab_XYSample',
                    'scale': 'linear',
                },
                'title': 'Select',
                'layout': {
                    'xxl': {'minH': 3, 'minW': 3, 'h': 3, 'w': 8, 'y': 0, 'x': 0},
                    'xl': {'minH': 3, 'minW': 3, 'h': 3, 'w': 8, 'y': 0, 'x': 13},
                    'lg': {'minH': 3, 'minW': 3, 'h': 3, 'w': 9, 'y': 3, 'x': 15},
                    'md': {'minH': 3, 'minW': 3, 'h': 3, 'w': 8, 'y': 0, 'x': 0},
                    'sm': {'minH': 3, 'minW': 3, 'h': 3, 'w': 8, 'y': 0, 'x': 0},
                },
            },


            # Atomic fraction Ti (scatterplot)
            {
                'type': 'scatterplot',
                'autorange': True,
                'size': 1000,
                'markers': {
                    'color': {
                        'title': 'Atomic fraction Ti',
                        'search_quantity': "min(data.elemental_composition[?element == 'Ti'].atomic_fraction#nomad_chemical_energy.schema_packages.hzb_catlab_package.CatLab_XYSample)",
                        'scale': 'linear',
                    },
                },
                'y': {
                    'title': 'Y',
                    'unit': 'mm',
                    'search_quantity': 'data.position.y#nomad_chemical_energy.schema_packages.hzb_catlab_package.CatLab_XYSample',
                    'scale': 'linear',
                },
                'x': {
                    'title': 'X',
                    'unit': 'mm',
                    'search_quantity': 'data.position.x#nomad_chemical_energy.schema_packages.hzb_catlab_package.CatLab_XYSample',
                    'scale': 'linear',
                },
                'title': 'Ti',
                'layout': {
                    'xxl': {'minH': 6, 'minW': 6, 'h': 6, 'w': 6, 'y': 0, 'x': 10},
                    'xl': {'minH': 6, 'minW': 6, 'h': 6, 'w': 6, 'y': 0, 'x': 21},
                    'lg': {'minH': 6, 'minW': 6, 'h': 6, 'w': 6, 'y': 6, 'x': 4},
                    'md': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 42, 'x': 0},
                    'sm': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 0, 'x': 10},

                },
            },

            # Atomic fraction Co (scatterplot)
            {
                'type': 'scatterplot',
                'autorange': True,
                'size': 1000,
                'markers': {
                    'color': {
                        'title': 'Atomic fraction Co',
                        'search_quantity': "min(data.elemental_composition[?element == 'Co'].atomic_fraction#nomad_chemical_energy.schema_packages.hzb_catlab_package.CatLab_XYSample)",
                        'scale': 'linear',
                    },
                },
                'y': {
                    'title': 'Y',
                    'unit': 'mm',
                    'search_quantity': 'data.position.y#nomad_chemical_energy.schema_packages.hzb_catlab_package.CatLab_XYSample',
                    'scale': 'linear',
                },
                'x': {
                    'title': 'X',
                    'unit': 'mm',
                    'search_quantity': 'data.position.x#nomad_chemical_energy.schema_packages.hzb_catlab_package.CatLab_XYSample',
                    'scale': 'linear',
                },
                'title': 'Co',
                'layout': {
                    'xxl': {'minH': 6, 'minW': 6, 'h': 6, 'w': 6, 'y': 0, 'x': 10},
                    'xl': {'minH': 6, 'minW': 6, 'h': 6, 'w': 6, 'y': 7, 'x': 4},
                    'lg': {'minH': 6, 'minW': 6, 'h': 6, 'w': 6, 'y': 6, 'x': 10},
                    'md': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 36, 'x': 0},
                    'sm': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 0, 'x': 10},


                },
            },

            # thickness (scatterplot)
            {
                'type': 'scatterplot',
                'autorange': True,
                'size': 1000,
                'markers': {
                    'color': {
                        'title': 'Thickness',
                        'unit': 'nm',
                        'search_quantity': 'data.thickness.value#nomad_chemical_energy.schema_packages.hzb_catlab_package.CatLab_XYSample',

                        'scale': 'linear',
                    },
                },
                'y': {
                    'title': 'Y (mm)',
                    'unit': 'mm',
                    'search_quantity': 'data.position.y#nomad_chemical_energy.schema_packages.hzb_catlab_package.CatLab_XYSample',
                    'scale': 'linear',
                },
                'x': {
                    'title': 'X (mm)',
                    'unit': 'mm',
                    'search_quantity': 'data.position.x#nomad_chemical_energy.schema_packages.hzb_catlab_package.CatLab_XYSample',
                    'scale': 'linear',
                },
                'title': 'Thickness',
                'layout': {
                    'xxl': {'minH': 6, 'minW': 6, 'h': 6, 'w': 6, 'y': 0, 'x': 10},
                    'xl': {'minH': 6, 'minW': 6, 'h': 6, 'w': 6, 'y': 7, 'x': 10},
                    'lg': {'minH': 6, 'minW': 6, 'h': 6, 'w': 6, 'y': 6, 'x': 16},
                    'md': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 30, 'x': 0},
                    'sm': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 0, 'x': 10},
                },
            },


            # Atomic fraction Pd (scatterplot)
            {
                'type': 'scatterplot',
                'autorange': True,
                'size': 1000,
                'markers': {
                    'color': {
                        'title': 'Atomic fraction Pd',
                        'search_quantity': "min(data.elemental_composition[?element == 'Pd'].atomic_fraction#nomad_chemical_energy.schema_packages.hzb_catlab_package.CatLab_XYSample)",
                        'scale': 'linear',
                    },
                },
                'y': {
                    'title': 'Y',
                    'unit': 'mm',
                    'search_quantity': 'data.position.y#nomad_chemical_energy.schema_packages.hzb_catlab_package.CatLab_XYSample',
                    'scale': 'linear',
                },
                'x': {
                    'title': 'X',
                    'unit': 'mm',
                    'search_quantity': 'data.position.x#nomad_chemical_energy.schema_packages.hzb_catlab_package.CatLab_XYSample',
                    'scale': 'linear',
                },
                'title': 'Pd',
                'layout': {
                    'xxl': {'minH': 6, 'minW': 6, 'h': 6, 'w': 6, 'y': 0, 'x': 10},
                    'xl': {'minH': 6, 'minW': 6, 'h': 6, 'w': 6, 'y': 7, 'x': 16},
                    'lg': {'minH': 6, 'minW': 6, 'h': 6, 'w': 6, 'y': 12, 'x': 4},
                    'md': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 24, 'x': 0},
                    'sm': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 0, 'x': 10},
                },
            },

            # Atomic fraction Ag (scatterplot)
            {
                'type': 'scatterplot',
                'autorange': True,
                'size': 1000,
                'markers': {
                    'color': {
                        'title': 'Atomic fraction Ag',
                        'search_quantity': "min(data.elemental_composition[?element == 'Ag'].atomic_fraction#nomad_chemical_energy.schema_packages.hzb_catlab_package.CatLab_XYSample)",
                        'scale': 'linear',
                    },
                },
                'y': {
                    'title': 'Y',
                    'unit': 'mm',
                    'search_quantity': 'data.position.y#nomad_chemical_energy.schema_packages.hzb_catlab_package.CatLab_XYSample',
                    'scale': 'linear',
                },
                'x': {
                    'title': 'X',
                    'unit': 'mm',
                    'search_quantity': 'data.position.x#nomad_chemical_energy.schema_packages.hzb_catlab_package.CatLab_XYSample',
                    'scale': 'linear',
                },
                'title': 'Ag',
                'layout': {
                    'xxl': {'minH': 6, 'minW': 6, 'h': 6, 'w': 6, 'y': 0, 'x': 10},
                    'xl': {'minH': 6, 'minW': 6, 'h': 6, 'w': 6, 'y': 7, 'x': 22},
                    'lg': {'minH': 6, 'minW': 6, 'h': 6, 'w': 6, 'y': 12, 'x': 10},
                    'md': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 18, 'x': 0},
                    'sm': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 0, 'x': 10},
                },
            },




        ]
    },
)
