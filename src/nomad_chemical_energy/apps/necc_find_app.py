from nomad.config.models.ui import (
    App,
    Column,
    Columns,
    Dashboard,
    Filters,
    Menu,
    MenuItemCustomQuantities,
    MenuItemHistogram,
    MenuItemOptimade,
    MenuItemPeriodicTable,
    MenuItemTerms,
    WidgetHistogram,
    WidgetTerms,
)

schema = 'nomad_chemical_energy.schema_packages.ce_necc_package.CE_NECC_EC_GC'

necc_find_experiments_app = App(
    # Label of the App
    label='Find NECC Experiments',
    # Path used in the URL, must be unique
    path='necc-find',
    # Used to categorize apps in the explore menu
    category='NECC Data',
    # Brief description used in the app menu
    description='Provides filters to quickly find NECC experiment entries.',
    # Longer description that can also use markdown
    readme='Provides filters to quickly find NECC experiment entries.',
    # Controls the available search filters. If you want to filter by
    # quantities in a schema package, you need to load the schema package
    # explicitly here. Note that you can use a glob syntax to load the
    # entire package, or just a single schema from a package.
    filters=Filters(
        include=[
            f'*#{schema}',
            '*#nomad_chemical_energy.schema_packages.ce_necc_package.CE_NECC_Electrode',
            '*#nomad_chemical_energy.schema_packages.ce_necc_package.CE_NECC_ElectrodeRecipe',
        ]
    ),
    # Controls which columns are shown in the results table
    columns=Columns(
        selected=[
            'entry_type',
            'entry_name',
            'entry_create_time',
            'authors',
            'upload_name',
            'data.properties.cathode.lab_id#nomad_chemical_energy.schema_packages.ce_necc_package.CE_NECC_Electrode',
            'data.properties.anode.lab_id#nomad_chemical_energy.schema_packages.ce_necc_package.CE_NECC_ElectrodeRecipe',
        ],
        options={
            'entry_type': Column(label='Entry type', align='left'),
            'entry_name': Column(label='Name', align='left'),
            'entry_create_time': Column(label='Entry time', align='left'),
            'authors': Column(label='Authors', align='left'),
            'upload_name': Column(label='Upload name', align='left'),
            'data.properties.cathode.lab_id#nomad_chemical_energy.schema_packages.ce_necc_package.CE_NECC_Electrode': Column(
                label='Cathode ID', align='left'
            ),
            'data.properties.anode.lab_id#nomad_chemical_energy.schema_packages.ce_necc_package.CE_NECC_ElectrodeRecipe': Column(
                label='Anode ID', align='left'
            ),
        },
    ),
    # Dictionary of search filters that are always enabled for queries made
    # within this app. This is especially important to narrow down the
    # results to the wanted subset. Any available search filter can be
    # targeted here. This example makes sure that only entries that use
    # MySchema are included.
    filters_locked={'section_defs.definition_qualified_name': f'{schema}'},
    # Controls the filter menus shown on the left
    menu=Menu(
        title='EC GC Filters',
        items=[
            Menu(
                title='EC GC',
                indentation=1,
            ),
            Menu(
                title='Anode',
                indentation=2,
                size='xxl',
                items=[
                    MenuItemPeriodicTable(
                        title='Anode Material',
                        search_quantity=f'data.result_properties.anode_material#{schema}',
                    ),
                    MenuItemTerms(
                        search_quantity=f'data.properties.anode.name#{schema}',
                        width=6,
                        options=3,
                        title='Anode ID',
                    ),
                    MenuItemTerms(
                        search_quantity=f'data.result_properties.anode_deposition_method#{schema}',
                        width=6,
                        options=3,
                    ),
                    MenuItemTerms(
                        search_quantity=f'data.result_properties.anode_substrate_type#{schema}',
                        width=6,
                        options=3,
                    ),
                    MenuItemTerms(
                        search_quantity=f'data.result_properties.anode_ionomer_type#{schema}',
                        width=6,
                        options=3,
                    ),
                    MenuItemTerms(
                        search_quantity=f'data.properties.anolyte_type#{schema}',
                        width=6,
                        options=3,
                    ),
                    MenuItemHistogram(
                        x={
                            'search_quantity': f'data.properties.anolyte_concentration#{schema}',
                            'unit': 'mol/l',
                        }
                    ),
                    MenuItemHistogram(
                        x={
                            'search_quantity': f'data.properties.anolyte_flow_rate#{schema}',
                            'unit': 'ml/ minute',
                        }
                    ),
                    MenuItemHistogram(
                        x={
                            'search_quantity': f'data.properties.anolyte_volume#{schema}',
                            'unit': 'ml',
                        }
                    ),
                ],
            ),
            Menu(
                title='Cathode',
                indentation=2,
                size='xxl',
                items=[
                    MenuItemPeriodicTable(
                        title='Cathode Material',
                        search_quantity=f'data.result_properties.anode_material#{schema}',
                    ),
                    MenuItemTerms(
                        search_quantity=f'data.properties.cathode.name#{schema}',
                        width=6,
                        options=3,
                        title='Cathode ID',
                    ),
                    MenuItemTerms(
                        search_quantity=f'data.result_properties.cathode_deposition_method#{schema}',
                        width=6,
                        options=3,
                    ),
                    MenuItemTerms(
                        search_quantity=f'data.result_properties.cathode_substrate_type#{schema}',
                        width=6,
                        options=3,
                    ),
                    MenuItemTerms(
                        search_quantity=f'data.result_properties.cathode_ionomer_type#{schema}',
                        width=6,
                        options=3,
                    ),
                    MenuItemHistogram(
                        x={
                            'search_quantity': f'data.properties.cathode_geometric_area#{schema}',
                            'unit': 'cm^2',
                        }
                    ),
                ],
            ),
            Menu(
                title='Experimental Properties',
                indentation=2,
                size='xxl',
                items=[
                    MenuItemTerms(
                        title='Feed Gas',
                        search_quantity=f'data.properties.feed_gases.name#{schema}',
                        width=6,
                        options=3,
                    ),
                    MenuItemTerms(
                        search_quantity=f'data.properties.cell_type#{schema}',
                        width=6,
                        options=3,
                    ),
                    MenuItemTerms(
                        search_quantity=f'data.properties.reference_electrode_type#{schema}',
                        width=6,
                        options=3,
                    ),
                    MenuItemTerms(
                        search_quantity=f'data.properties.chronoanalysis_method#{schema}',
                        width=6,
                        options=3,
                    ),
                    MenuItemTerms(
                        search_quantity=f'data.properties.membrane_type#{schema}',
                        width=6,
                        options=3,
                    ),
                    MenuItemTerms(
                        search_quantity=f'data.properties.membrane_name#{schema}',
                        width=6,
                        options=3,
                    ),
                    MenuItemHistogram(
                        x={
                            'search_quantity': f'data.properties.membrane_thickness#{schema}',
                            'unit': 'µm',
                        }
                    ),
                    MenuItemHistogram(
                        x={
                            'search_quantity': f'data.properties.gasket_thickness#{schema}',
                            'unit': 'µm',
                        }
                    ),
                    MenuItemHistogram(
                        x={
                            'search_quantity': f'data.properties.humidifier_temperature#{schema}'
                        }
                    ),
                    MenuItemHistogram(
                        x={
                            'search_quantity': f'data.properties.water_trap_volume#{schema}',
                            'unit': 'ml',
                        }
                    ),
                    MenuItemHistogram(
                        x={
                            'search_quantity': f'data.properties.bleedline_flow_rate#{schema}',
                            'unit': 'ml/minute',
                        }
                    ),
                    MenuItemHistogram(
                        x={
                            'search_quantity': f'data.properties.nitrogen_start_value#{schema}',
                            'unit': 'ppm',
                        }
                    ),
                ],
            ),
            Menu(
                title='Electronic Lab Notebook',
                size='md',
                items=[
                    MenuItemTerms(search_quantity='results.eln.sections'),
                    MenuItemTerms(search_quantity='results.eln.methods'),
                    MenuItemTerms(search_quantity='results.eln.tags'),
                    MenuItemTerms(search_quantity='results.eln.instruments'),
                    MenuItemTerms(search_quantity='results.eln.lab_ids'),
                ],
            ),
            Menu(
                title='Author / Dataset',
                size='md',
                items=[
                    MenuItemTerms(search_quantity='authors.name'),
                    MenuItemHistogram(x={'search_quantity': 'upload_create_time'}),
                    MenuItemTerms(search_quantity='datasets.dataset_name'),
                ],
            ),
            Menu(
                title='User Defined Quantities',
                size='xl',
                items=[
                    MenuItemCustomQuantities(),
                ],
            ),
            Menu(
                title='Optimade',
                size='xl',
                items=[
                    MenuItemOptimade(),
                ],
            ),
        ],
    ),
    # Controls the default dashboard shown in the search interface
    dashboard=Dashboard(
        widgets=[
            WidgetTerms(
                showinput=True,
                scale='linear',
                quantity='authors.name',
                layout={
                    'xxl': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 0, 'x': 0},
                    'xl': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 0, 'x': 0},
                    'lg': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 0, 'x': 0},
                    'md': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 0, 'x': 0},
                    'sm': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 0, 'x': 0},
                },
            ),
            WidgetTerms(
                showinput=True,
                scale='linear',
                quantity='results.eln.methods',
                layout={
                    'xxl': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 0, 'x': 6},
                    'xl': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 0, 'x': 6},
                    'lg': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 0, 'x': 6},
                    'md': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 0, 'x': 6},
                    'sm': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 0, 'x': 6},
                },
            ),
            WidgetTerms(
                showinput=True,
                scale='linear',
                quantity='upload_name',
                layout={
                    'xxl': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 4, 'x': 0},
                    'xl': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 4, 'x': 0},
                    'lg': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 4, 'x': 0},
                    'md': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 4, 'x': 0},
                    'sm': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 4, 'x': 0},
                },
            ),
            WidgetTerms(
                showinput=True,
                scale='linear',
                quantity='entry_name',
                layout={
                    'xxl': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 4, 'x': 6},
                    'xl': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 4, 'x': 6},
                    'lg': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 4, 'x': 6},
                    'md': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 4, 'x': 6},
                    'sm': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 4, 'x': 6},
                },
            ),
            WidgetHistogram(
                title='Entry create time',
                showinput=True,
                autorange=False,
                nbins=30,
                scale='1/4',
                quantity='entry_create_time',
                layout={
                    'xxl': {'minH': 3, 'minW': 3, 'h': 4, 'w': 12, 'y': 0, 'x': 12},
                    'xl': {'minH': 3, 'minW': 3, 'h': 4, 'w': 12, 'y': 0, 'x': 12},
                    'lg': {'minH': 3, 'minW': 3, 'h': 3, 'w': 12, 'y': 8, 'x': 12},
                    'md': {'minH': 3, 'minW': 3, 'h': 3, 'w': 12, 'y': 8, 'x': 0},
                    'sm': {'minH': 3, 'minW': 3, 'h': 3, 'w': 12, 'y': 8, 'x': 0},
                },
            ),
        ]
    ),
)
