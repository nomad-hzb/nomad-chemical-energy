#
# Copyright The NOMAD Authors.
#
# This file is part of NOMAD. See https://nomad-lab.eu for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from datetime import datetime

import numpy as np
import plotly.graph_objs as go
from baseclasses.chemical_energy.potentiostat_measurement import PotentiostatMeasurement
from baseclasses.helper.utilities import get_reference
from nomad.datamodel.metainfo.basesections import (
    Analysis,
    AnalysisResult,
    CompositeSystemReference,
    SectionReference,
)
from nomad.datamodel.metainfo.plot import PlotlyFigure, PlotSection
from nomad.datamodel.results import Material, Results
from nomad.metainfo import Quantity, Reference, Section, SubSection
from nomad.units import ureg


class NESD_OERReference(SectionReference):
    reference = Quantity(
        type=Reference(PotentiostatMeasurement.m_def),
        a_eln=dict(
            component='ReferenceEditQuantity',
            label='NESD OER Measurement',
        ),
    )


class NESD_OERComparisonResult(AnalysisResult):
    # TODO find logic for the analysis where we compare the repeated experiments and select the measurements
    #  that are closest to the mean (regarding folder leves this would be one level above the NESD_OERAnalysisResult)
    charge_densities = Quantity(
        links=['https://w3id.org/nfdi4cat/voc4cat_0007253'],
        type=np.dtype(np.float64),
        shape=['*'],
        unit=('mC/cm^2'),
    )
    overpotentials = Quantity(
        type=np.dtype(np.float64),
        description='overpotential at 10 mA/cm²',
        shape=['*'],
        unit=('mV'),
    )
    mean_charge_density = Quantity(
        type=np.dtype(np.float64),
        unit=('mC/cm^2'),
    )
    std_dev_charge_density = Quantity(
        type=np.dtype(np.float64),
        description='standard deviation of charge densities',
        unit=('mC/cm^2'),
    )
    mean_overpotential = Quantity(
        type=np.dtype(np.float64),
        description='mean of overpotentials at 10 mA/cm²',
        unit=('mV'),
    )
    std_dev_overpotential = Quantity(
        type=np.dtype(np.float64),
        description='standard deviation of overpotentials at 10 mA/cm²',
        unit=('mV'),
    )
    reaction_type = Quantity(
        type=str,
        default='OER',
    )
    samples = SubSection(
        links=['https://w3id.org/nfdi4cat/voc4cat_0005013'],
        section_def=CompositeSystemReference,
        repeats=True,
    )
    selected_inputs = SubSection(
        section_def=NESD_OERReference,
        repeats=True,
    )

    def calculate_statistics(self, quantity, quantity_name):
        supported_quantities = {
            'charge_density',
            'overpotential',
        }
        if quantity_name not in supported_quantities:
            return
        if quantity is None:
            return
        setattr(self, f'mean_{quantity_name}', np.mean(quantity))
        setattr(self, f'std_dev_{quantity_name}', np.std(quantity))

    def normalize(self, archive, logger):
        self.calculate_statistics(self.charge_densities, 'charge_density')
        self.calculate_statistics(self.overpotentials, 'overpotential')
        super().normalize(archive, logger)


class NESD_OERAnalysisResult(PlotSection, AnalysisResult):
    m_def = Section(a_eln=dict(overview=True))
    charge_density = Quantity(
        links=['https://w3id.org/nfdi4cat/voc4cat_0007253'],
        type=np.dtype(np.float64),
        unit=('mC/cm^2'),
    )
    overpotential = Quantity(
        type=np.dtype(np.float64),
        description='overpotential at 10 mA/cm²',
        shape=['*'],
        unit=('V'),
    )
    overpotential_at_10mA_cm2 = Quantity(
        type=np.dtype(np.float64),
        description='overpotential at 10 mA/cm²',
        unit=('V'),
    )
    reaction_type = Quantity(
        type=str,
        default='OER',
    )
    samples = SubSection(
        links=['https://w3id.org/nfdi4cat/voc4cat_0005013'],
        section_def=CompositeSystemReference,
        repeats=True,
    )

    def set_charge_density_plot(self, potential, current_density, charge_density):
        x_vals = potential.magnitude
        y_vals = current_density.magnitude
        x_unit = f'{potential.units:~P}'
        y_unit = f'{current_density.units:~P}'

        fig = go.Figure()

        max_idx = np.argmax(x_vals)
        mask = np.arange(len(x_vals)) <= max_idx
        fig.add_trace(
            go.Scatter(
                x=x_vals[mask],
                y=y_vals[mask],
                mode='lines',
                line=dict(color='orange'),
                name=f'Charge Density = {charge_density:.2f} mC/cm²',
                fill='tozeroy',
                fillcolor='rgba(255,165,0,0.3)',
            )
        )

        fig.add_trace(
            go.Scatter(
                x=x_vals,
                y=y_vals,
                mode='lines',
                name='Current Density',
            )
        )

        fig.update_layout(
            title_text='Charge Density (Cyclic Voltammetry)',
            showlegend=True,
            hovermode='closest',
            dragmode='zoom',
            xaxis=dict(fixedrange=False),
            yaxis=dict(fixedrange=False),
            xaxis_title=f'Potential [{x_unit} vs RHE]',
            yaxis_title=f'Current Density [{y_unit}]',
            template='plotly_white',
            legend=dict(bordercolor='LightGray', borderwidth=1),
        )

        if not self.figures:
            self.initialize_figures()
        self.figures[0].figure = fig.to_plotly_json()

    def set_overpotential_plot(self, overpotential, current_density):
        x_vals = overpotential.magnitude
        y_vals = current_density.magnitude
        x_unit = f'{overpotential.units:~P}'
        y_unit = f'{current_density.units:~P}'

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=x_vals,
                y=y_vals,
                mode='lines',
                name='Current Density',
            )
        )

        # horizontal line at y=10 mA/cm²
        fig.add_trace(
            go.Scatter(
                x=x_vals,
                y=[10] * len(x_vals),
                mode='lines',
                line=dict(color='red', dash='dash'),
                name='y = 10',
                hovertemplate=f'Overpotential at 10 mA/cm² = {self.overpotential_at_10mA_cm2}<extra></extra>',
            )
        )

        fig.update_layout(
            title_text='Overpotential (LSV)',
            xaxis_title=f'Overpotential [{x_unit}]',
            yaxis_title=f'Current Density [{y_unit}]',
            template='plotly_white',
            hovermode='closest',
            dragmode='zoom',
            xaxis=dict(fixedrange=False),
            yaxis=dict(fixedrange=False),
        )

        if not self.figures:
            self.initialize_figures()
        self.figures[1].figure = fig.to_plotly_json()

    def set_eis_plot(self):
        pass

    def set_tafel_slopes(self, current_density, potential):
        x_vals = np.log10(current_density.magnitude)
        y_vals = potential.magnitude

        y_unit = f'{potential.units:~P}'

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(x=x_vals, y=y_vals, mode='markers', name='Data Points')
        )

        fig.update_layout(
            title_text='Tafel Slope (LSV)',
            xaxis_title='log(Current Density j)',
            yaxis_title=f'Potential [{y_unit} vs RHE]',
            template='plotly_white',
            hovermode='closest',
            dragmode='zoom',
            xaxis=dict(fixedrange=False),
            yaxis=dict(fixedrange=False),
        )

        if not self.figures:
            self.initialize_figures()
        self.figures[3].figure = fig.to_plotly_json()

    def set_ecsa_plot(self):
        pass

    def initialize_figures(self):
        self.figures = [
            PlotlyFigure(
                label='Charge Density',
                figure=go.Figure().to_plotly_json(),
            ),
            PlotlyFigure(
                label='Overpotential',
                figure=go.Figure().to_plotly_json(),
            ),
            PlotlyFigure(
                label='EIS',
                figure=go.Figure().to_plotly_json(),
            ),
            PlotlyFigure(
                label='Tafel slopes',
                figure=go.Figure().to_plotly_json(),
            ),
            PlotlyFigure(
                label='ECSA (electrochemical active surface area)',
                figure=go.Figure().to_plotly_json(),
            ),
        ]

    def normalize(self, archive, logger):
        if self.figures is None:
            self.initialize_figures()
        super().normalize(archive, logger)


class NESD_OERAnalysis(Analysis):
    m_def = Section(label_quantity='name')

    inputs = Analysis.inputs.m_copy()
    inputs.section_def = NESD_OERReference

    outputs = Analysis.outputs.m_copy()
    outputs.section_def = NESD_OERAnalysisResult

    def get_entries_from_folder(self, data_archive, upload_id, folder_path, entry_type):
        from nomad.app.v1.models import MetadataPagination
        from nomad.search import search

        query = {
            'upload_id': upload_id,
            'entry_type': entry_type,
        }
        pagination = MetadataPagination()
        pagination.page_size = 10000
        search_result = search(
            owner='all',
            query=query,
            pagination=pagination,
            user_id=data_archive.metadata.main_author.user_id,
        )

        lst = search_result.data
        lst = [
            nomad_entry
            for nomad_entry in lst
            if nomad_entry.get('mainfile', '').startswith(folder_path)
        ]
        lst.sort(
            key=lambda nomad_entry: datetime.fromisoformat(
                nomad_entry.get('data', {}).get('datetime', '')
            )
        )
        refs = [
            [
                nomad_entry.get('data', {}).get('data_file'),
                get_reference(upload_id, nomad_entry.get('entry_id', '')),
            ]
            for nomad_entry in lst
        ]
        return refs

    def get_ir_drop_correction(self, eis_refs):
        # TODO maybe revisit this and select not only first EIS ref but also check for 0V
        try:
            eis_entry = eis_refs[0].reference
            z_real_values = eis_entry.measurements[0].data.z_real
            eis_value = z_real_values[0].to(ureg.ohm)
            ir_compensation = eis_entry.setup.ir_compensation
        except AttributeError:
            return None
        return eis_value * ir_compensation

    def get_cv(self, cv_refs):
        # TODO maybe revisit and select not only first CV but also check for voltage range (>1.6V while ECSA is ~100mV in non-faradaic region)
        cv_entry = cv_refs[0].reference
        return cv_entry

    def get_lsv(self, lsv_refs):
        # TODO maybe revisit because in example only the one in 1mV is used
        lsv_entry = lsv_refs[0].reference
        return lsv_entry

    def set_resistance_in_inputs(self, new_resistance, archive, logger):
        for input in self.inputs:
            entry = input.reference
            if entry.method == 'Multiple Electrochemical Impedance Spectroscopy':
                continue
            if entry.method is None:
                continue
            new_entry = entry.m_copy()
            new_entry.resistance = new_resistance
            if new_entry is not None:
                from baseclasses.helper.utilities import create_archive

                create_archive(
                    new_entry,
                    archive,
                    f'{entry.data_file}.archive.json',
                    overwrite=True,
                )

    def get_charge_density(self, cv_cycle, scan_rate):
        scan_rate = scan_rate.to('V/s').magnitude
        voltage = cv_cycle.voltage_rhe_compensated.to(ureg.V).magnitude
        current_density = cv_cycle.current_density.to('mA/cm²').magnitude

        turning_point_idx = voltage.argmax()
        # Forward Scan
        voltage_fwd = voltage[: turning_point_idx + 1]
        current_density_fwd = current_density[: turning_point_idx + 1]

        charge_density = (
            np.trapz(np.abs(current_density_fwd), voltage_fwd) / scan_rate
        )  # [mC/cm²]
        return charge_density

    def get_overpotential(self, lsv):
        theoretical_oer_potential = 1.23 * ureg.V
        overpotential = (
            lsv.voltage_rhe_compensated.to(ureg.V) - theoretical_oer_potential
        )
        return overpotential

    def get_oer_analysis_result(self, cv_refs, lsv_refs):
        cv = self.get_cv(cv_refs)
        last_cv_cycle = cv.cycles[-1]
        scan_rate = cv.get('properties').scan_rate
        charge_density = self.get_charge_density(last_cv_cycle, scan_rate)

        lsv = self.get_lsv(lsv_refs)
        overpotential = self.get_overpotential(lsv)
        overpotential_at_10 = np.interp(
            10,
            lsv.current_density.to('mA/cm²').magnitude,
            overpotential.to(ureg.V).magnitude,
        )

        result_entry = NESD_OERAnalysisResult(
            name=f'{("/" + cv.name).rsplit("/", 1)[0]}/OER_analysis'[1:],
            reaction_type='OER',
            charge_density=charge_density,
            overpotential=overpotential,
            overpotential_at_10mA_cm2=overpotential_at_10,
            samples=cv.samples,
        )
        result_entry.samples[0].name = result_entry.samples[0].reference.name
        result_entry.set_charge_density_plot(
            last_cv_cycle.voltage_rhe_compensated,
            last_cv_cycle.current_density,
            charge_density,
        )
        result_entry.set_overpotential_plot(
            overpotential,
            lsv.current_density,
        )
        result_entry.set_tafel_slopes(lsv.current_density, lsv.voltage_rhe_compensated)

        return result_entry

    def get_nesd_oer_ref_list(self, archive, folder, entry_type):
        ref_list = self.get_entries_from_folder(
            archive, archive.metadata.upload_id, folder, entry_type
        )
        refs = [NESD_OERReference(name=name, reference=ref) for [name, ref] in ref_list]
        return refs

    def normalize(self, archive, logger):
        folder = ('/' + archive.metadata.mainfile).rsplit('/', 1)[0][1:]
        cv_refs = self.get_nesd_oer_ref_list(
            archive, folder, 'CE_NESD_CyclicVoltammetry'
        )
        lsv_refs = self.get_nesd_oer_ref_list(
            archive, folder, 'CE_NESD_LinearSweepVoltammetry'
        )
        eis_refs = self.get_nesd_oer_ref_list(archive, folder, 'CE_NESD_PEIS')
        self.inputs = cv_refs + lsv_refs + eis_refs

        if self.inputs is not None and len(self.inputs) > 0:
            for sample in self.inputs[0].reference.samples:
                if sample.reference.components is not None:
                    if not archive.results:
                        archive.results = Results()
                    if not archive.results.material:
                        archive.results.material = Material()
                    try:
                        from nomad.atomutils import Formula

                        formulas = ''.join(
                            component.pure_substance.molecular_formula
                            for component in sample.reference.components
                        )
                        Formula(formulas).populate(section=archive.results.material)
                    except Exception as e:
                        logger.warn('Could not analyse material', exc_info=e)

            ir_drop_correction = self.get_ir_drop_correction(eis_refs)
            if ir_drop_correction is not None:
                self.set_resistance_in_inputs(ir_drop_correction, archive, logger)
                output = self.get_oer_analysis_result(cv_refs, lsv_refs)
                self.outputs = [output]
                for oer_output in self.outputs:
                    oer_output.normalize(archive, logger)
        super().normalize(archive, logger)
