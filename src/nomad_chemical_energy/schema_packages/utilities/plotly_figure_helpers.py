import plotly.graph_objs as go


def make_bode_plot(measurements=None, *, frequency=None, z_modulus=None, z_angle=None):
    """
    Bode plot with |Z| (left axis) and phase (right axis) over frequency.

    Either pass `measurements`, a list of cycles with `cycle.data.frequency`,
    `.z_modulus` and `.z_angle` (one pair of traces per cycle), or pass the
    quantities `frequency`, `z_modulus` and `z_angle` directly (a single pair of
    traces, e.g. for entries that hold the data on the top level).
    """
    fig = go.Figure().update_layout(
        title_text='Bode Plot',
    )
    if measurements:
        datasets = []
        for idx, cycle in enumerate(measurements):
            data = cycle.data
            if (
                data is None
                or data.frequency is None
                or data.z_modulus is None
                or data.z_angle is None
            ):
                return fig
            datasets.append((f' {idx}', data.frequency, data.z_modulus, data.z_angle))
    elif frequency is not None and z_modulus is not None and z_angle is not None:
        datasets = [('', frequency, z_modulus, z_angle)]
    else:
        return fig
    for suffix, freq, modulus, angle in datasets:
        fig.add_trace(
            go.Scatter(
                name=f'|Z|{suffix}',
                x=freq,
                y=modulus,
                mode='lines',
                hoverinfo='x+y+name',
                yaxis='y1',
            )
        )
        fig.add_trace(
            go.Scatter(
                name=f'Phase(Z){suffix}',
                x=freq,
                y=angle,
                mode='lines',
                hoverinfo='x+y+name',
                yaxis='y2',
            )
        )
    _, freq, modulus, angle = datasets[0]
    fig.update_layout(
        title_text='Bode Plot',
        showlegend=True,
        xaxis={
            'fixedrange': False,
            'type': 'log',
            'title': _units_label('Frequency', freq),
        },
        yaxis={
            'title': _units_label('|Z|', modulus),
            'fixedrange': False,
        },
        yaxis2={
            'title': _units_label('Phase', angle),
            'overlaying': 'y',
            'side': 'right',
            'fixedrange': False,
        },
        hovermode='closest',
    )
    return fig


def make_current_plot(current, time):
    if current is None:
        return go.Figure().update_layout(
            title_text='Current over Time',
        )
    fig = go.Figure(
        data=[
            go.Scatter(
                name='Current',
                x=time,
                y=current,
                mode='lines',
                hoverinfo='x+y+name',
            )
        ]
    )
    fig.update_layout(
        title_text='Current over Time',
        xaxis={
            'fixedrange': False,
            'title': f'Time ({time.units:~P})',
        },
        yaxis={
            'fixedrange': False,
            'title': f'Current ({current.units:~P})',
        },
        hovermode='x unified',
    )
    return fig


def make_current_density_plot(current_density, time):
    if current_density is None:
        return go.Figure().update_layout(
            title_text='Current Density over Time',
        )
    fig = go.Figure(
        data=[
            go.Scatter(
                name='Current Density',
                x=time,
                y=current_density,
                mode='lines',
                hoverinfo='x+y+name',
            )
        ]
    )
    fig.update_layout(
        title_text='Current Density over Time',
        xaxis={
            'fixedrange': False,
            'title': f'Time ({time.units:~P})',
        },
        yaxis={
            'fixedrange': False,
            'title': f'Current Density ({current_density.units:~P})',
        },
        hovermode='x unified',
    )
    return fig


def make_current_density_over_voltage_rhe_plot(
    current_density, voltage_rhe_compensated
):
    if current_density is None or voltage_rhe_compensated is None:
        return go.Figure().update_layout(
            title_text='Current Density over Voltage RHE',
        )
    fig = go.Figure(
        data=[
            go.Scatter(
                name='Current Density',
                x=voltage_rhe_compensated,
                y=current_density,
                mode='lines',
                hoverinfo='x+y+name',
            )
        ]
    )
    fig.update_layout(
        title_text='Current Density over Voltage RHE',
        showlegend=True,
        xaxis={
            'fixedrange': False,
            'title': f'Voltage RHE compensated ({voltage_rhe_compensated.units:~P})',
        },
        yaxis={
            'fixedrange': False,
            'title': f'Current Density ({current_density.units:~P})',
        },
        hovermode='x unified',
    )
    return fig


def make_current_density_over_voltage_rhe_cv_plot(cycles):
    fig = go.Figure().update_layout(title_text='Current Density over Voltage RHE')
    if not cycles or cycles is None:
        return fig
    v_unit = None
    cd_unit = None
    for idx, cycle in enumerate(cycles):
        if cycle.voltage_rhe_compensated is None or cycle.current_density is None:
            continue
        if v_unit is None or cd_unit is None:
            v_unit = f'{cycle.voltage_rhe_compensated.units:~P}'
            cd_unit = f'{cycle.current_density.units:~P}'
        fig.add_trace(
            go.Scatter(
                name=f'Current Density {idx}',
                x=cycle.voltage_rhe_compensated,
                y=cycle.current_density,
                mode='lines',
                hoverinfo='x+y+name',
            )
        )
    fig.update_layout(
        showlegend=True,
        xaxis={
            'fixedrange': False,
            'title': f'Voltage RHE compensated ({v_unit})',
        },
        yaxis={
            'fixedrange': False,
            'title': f'Current Density ({cd_unit})',
        },
        hovermode='x unified',
    )
    return fig


def make_current_over_voltage_cv_plot(cycles):
    fig = go.Figure().update_layout(
        title_text='Current over Voltage',
    )
    if not cycles or cycles is None:
        return fig
    for idx, cycle in enumerate(cycles):
        if cycle.voltage is None or cycle.current is None:
            return fig
        fig.add_trace(
            go.Scatter(
                name=f'Current {idx}',
                x=cycle.voltage,
                y=cycle.current,
                mode='lines',
                hoverinfo='x+y+name',
            )
        )
    fig.update_layout(
        showlegend=True,
        xaxis={
            'fixedrange': False,
            'title': f'Voltage ({cycles[0].voltage.units:~P})',
        },
        yaxis={
            'fixedrange': False,
            'title': f'Current ({cycles[0].current.units:~P})',
        },
        hovermode='x unified',
    )
    return fig


def make_current_over_voltage_plot(current, voltage):
    if current is None or voltage is None:
        return go.Figure().update_layout(
            title_text='Current over Voltage',
        )
    fig = go.Figure(
        data=[
            go.Scatter(
                name='Current',
                x=voltage,
                y=current,
                mode='lines',
                hoverinfo='x+y+name',
            )
        ]
    )
    fig.update_layout(
        title_text='Current over Voltage',
        showlegend=True,
        xaxis={
            'fixedrange': False,
            'title': f'Voltage ({voltage.units:~P})',
        },
        yaxis={
            'fixedrange': False,
            'title': f'Current ({current.units:~P})',
        },
        hovermode='x unified',
    )
    return fig


def make_nyquist_plot(measurements=None, *, z_real=None, z_imaginary=None):
    """
    Nyquist plot (Re(Z) over -Im(Z)).

    Either pass `measurements`, a list of cycles with `cycle.data.z_real` and
    `.z_imaginary` (one trace per cycle), or pass the quantities `z_real` and
    `z_imaginary` directly (a single trace, e.g. for entries that hold the data
    on the top level).
    """
    fig = go.Figure().update_layout(
        title_text='Nyquist Plot',
    )
    if measurements:
        datasets = []
        for idx, cycle in enumerate(measurements):
            data = cycle.data
            if data is None or data.z_imaginary is None or data.z_real is None:
                return fig
            datasets.append((f'Nyquist {idx}', data.z_real, data.z_imaginary))
    elif z_real is not None and z_imaginary is not None:
        datasets = [('Nyquist', z_real, z_imaginary)]
    else:
        return fig
    for name, real, imaginary in datasets:
        fig.add_trace(
            go.Scatter(
                name=name,
                x=real,
                y=imaginary,
                mode='lines',
                hoverinfo='x+y+name',
            )
        )
    fig.update_layout(
        title_text='Nyquist Plot',
        xaxis={'fixedrange': False, 'title': 'Re(Z) (Ω)'},
        yaxis={'fixedrange': False, 'title': '-Im(Z) (Ω)'},
        hovermode='closest',
    )
    return fig


def _units_label(label, quantity):
    """Return 'label (unit)' if the quantity carries units, otherwise 'label'."""
    units = getattr(quantity, 'units', None)
    if units is None:
        return label
    try:
        return f'{label} ({units:~P})'
    except (TypeError, ValueError):
        return label


def make_xy_plot(
    x,
    y,
    title,
    x_label,
    y_label,
    trace_name=None,
    hovermode='x unified',
):
    """Generic single trace line plot for any x/y quantity pair."""
    fig = go.Figure().update_layout(title_text=title)
    if x is None or y is None:
        return fig
    fig.add_trace(
        go.Scatter(
            name=trace_name or y_label,
            x=x,
            y=y,
            mode='lines',
            hoverinfo='x+y+name',
        )
    )
    fig.update_layout(
        title_text=title,
        xaxis={'fixedrange': False, 'title': _units_label(x_label, x)},
        yaxis={'fixedrange': False, 'title': _units_label(y_label, y)},
        hovermode=hovermode,
    )
    return fig


def make_current_density_over_voltage_cv_plot(cycles):
    fig = go.Figure().update_layout(title_text='Current Density over Voltage')
    if not cycles:
        return fig
    for idx, cycle in enumerate(cycles):
        if cycle.voltage is None or cycle.current_density is None:
            return fig
        fig.add_trace(
            go.Scatter(
                name=f'Current Density {idx}',
                x=cycle.voltage,
                y=cycle.current_density,
                mode='lines',
                hoverinfo='x+y+name',
            )
        )
    fig.update_layout(
        showlegend=True,
        xaxis={
            'fixedrange': False,
            'title': _units_label('Voltage', cycles[0].voltage),
        },
        yaxis={
            'fixedrange': False,
            'title': _units_label('Current Density', cycles[0].current_density),
        },
        hovermode='x unified',
    )
    return fig


def make_charge_current_density_plot(time, current_density, charge_density):
    """Current density (left axis) and charge density (right axis) over time."""
    fig = go.Figure().update_layout(title_text='Charge and Current Density')
    if time is None or current_density is None or charge_density is None:
        return fig
    fig.add_trace(
        go.Scatter(
            name='Current Density',
            x=time,
            y=current_density,
            mode='lines',
            hoverinfo='x+y+name',
            yaxis='y1',
        )
    )
    fig.add_trace(
        go.Scatter(
            name='Charge Density',
            x=time,
            y=charge_density,
            mode='lines',
            hoverinfo='x+y+name',
            yaxis='y2',
        )
    )
    fig.update_layout(
        title_text='Charge and Current Density',
        showlegend=True,
        xaxis={'fixedrange': False, 'title': _units_label('Time', time)},
        yaxis={
            'fixedrange': False,
            'title': _units_label('Current Density', current_density),
        },
        yaxis2={
            'fixedrange': False,
            'title': _units_label('Charge Density', charge_density),
            'overlaying': 'y',
            'side': 'right',
        },
        hovermode='x unified',
    )
    return fig


def make_oxygen_plot(time, oxygen):
    return make_xy_plot(time, oxygen, 'Oxygen over Time', 'Time', 'Oxygen')


def make_flow_rate_plot(time, flow_rate_measured, flow_rate_set):
    fig = go.Figure().update_layout(title_text='Flow Rate')
    if time is None:
        return fig
    for name, values in (
        ('Flow Rate Measured', flow_rate_measured),
        ('Flow Rate Set', flow_rate_set),
    ):
        if values is None:
            continue
        fig.add_trace(
            go.Scatter(
                name=name,
                x=time,
                y=values,
                mode='lines',
                hoverinfo='x+y+name',
            )
        )
    fig.update_layout(
        title_text='Flow Rate',
        showlegend=True,
        xaxis={'fixedrange': False, 'title': _units_label('Time', time)},
        yaxis={
            'fixedrange': False,
            'title': _units_label('Flow Rate', flow_rate_measured),
        },
        hovermode='x unified',
    )
    return fig


def make_raman_plot(raman_shift, intensity, peaks_raman=None, peaks_intensity=None):
    fig = go.Figure().update_layout(title_text='Raman Spectrum')
    if raman_shift is None or intensity is None:
        return fig
    fig.add_trace(
        go.Scatter(
            name='Intensity',
            x=raman_shift,
            y=intensity,
            mode='lines',
            line={'color': 'rgb(40, 80, 130)'},
            hoverinfo='x+y+name',
        )
    )
    if peaks_raman is not None and peaks_intensity is not None:
        fig.add_trace(
            go.Scatter(
                name='Peaks',
                x=peaks_raman,
                y=peaks_intensity,
                mode='markers',
                marker={'color': 'rgb(100, 0, 0)'},
                hoverinfo='x+y+name',
            )
        )
    fig.update_layout(
        title_text='Raman Spectrum',
        showlegend=True,
        xaxis={
            'fixedrange': False,
            'title': _units_label('Raman Shift', raman_shift),
        },
        yaxis={'fixedrange': False, 'title': _units_label('Intensity', intensity)},
        hovermode='x unified',
    )
    return fig


def make_xrd_plot(traces):
    """
    XRD pattern(s). `traces` is a list of (name, angle, intensity) tuples,
    entries with missing data are skipped.
    """
    fig = go.Figure().update_layout(title_text='XRD')
    x_ref = None
    for name, angle, intensity in traces:
        if angle is None or intensity is None:
            continue
        if x_ref is None:
            x_ref = angle
        fig.add_trace(
            go.Scatter(
                name=name,
                x=angle,
                y=intensity,
                mode='lines',
                hoverinfo='x+y+name',
            )
        )
    fig.update_layout(
        title_text='XRD',
        showlegend=True,
        xaxis={'fixedrange': False, 'title': _units_label('Angle', x_ref)},
        yaxis={'fixedrange': False, 'title': 'Counts'},
        hovermode='x unified',
    )
    return fig


def make_xrd_data_plot(data):
    """XRD plot for a single `data` section with angle and intensity."""
    if data is None:
        return make_xrd_plot([])
    return make_xrd_plot([('XRD', data.angle, data.intensity)])


def make_xrd_measurements_plot(measurements, shifted_data=None):
    """XRD plot for the measurements (and optionally shifted data) of an XRD entry."""
    traces = []
    for idx, measurement in enumerate(measurements or []):
        traces.append(
            (
                f'Measurement {idx}',
                getattr(measurement, 'angle', None),
                getattr(measurement, 'intensity', None),
            )
        )
    for idx, measurement in enumerate(shifted_data or []):
        traces.append(
            (
                f'Shifted {idx}',
                getattr(measurement, 'angle', None),
                getattr(measurement, 'intensity', None),
            )
        )
    return make_xrd_plot(traces)


def make_xrd_library_plot(measurements):
    """Integrated XRD patterns (q vs. intensity) of all measurements of a library."""
    fig = go.Figure().update_layout(title_text='XRD Library')
    if not measurements:
        return fig
    for idx, measurement in enumerate(measurements):
        if measurement.q_nm_inv is None or measurement.intensity is None:
            continue
        fig.add_trace(
            go.Scatter(
                name=measurement.name or f'Measurement {idx}',
                x=measurement.q_nm_inv,
                y=measurement.intensity,
                mode='lines',
                hoverinfo='x+y+name',
            )
        )
    fig.update_layout(
        title_text='XRD Library',
        showlegend=False,
        xaxis={'fixedrange': False, 'title': 'q (1/nm)'},
        yaxis={'fixedrange': False, 'title': 'Intensity'},
        hovermode='closest',
    )
    return fig


def make_voltage_plot(time, voltage):
    if voltage is None:
        return go.Figure().update_layout(
            title_text='Voltage over Time',
        )
    fig = go.Figure(
        data=[
            go.Scatter(
                name='Voltage',
                x=time,
                y=voltage,
                mode='lines',
                hoverinfo='x+y+name',
            )
        ]
    )
    fig.update_layout(
        title_text='Voltage over Time',
        xaxis={
            'fixedrange': False,
            'title': f'Time ({time.units:~P})',
        },
        yaxis={
            'fixedrange': False,
            'title': f'Voltage ({voltage.units:~P})',
        },
        hovermode='x unified',
    )
    return fig
