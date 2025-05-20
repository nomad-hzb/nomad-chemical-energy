import plotly.graph_objs as go


def make_bode_plot(measurements):
    fig = go.Figure().update_layout(
        title_text='Bode Plot',
    )
    if measurements is None:
        return fig
    for idx, cycle in enumerate(measurements):
        if cycle.data is None:
            return fig
        if (
            cycle.data.frequency is None
            or cycle.data.z_modulus is None
            or cycle.data.z_angle is None
        ):
            return fig
        fig.add_traces(
            go.Scatter(
                name=f'|Z| {idx}',
                x=cycle.data.frequency,
                y=cycle.data.z_modulus,
                mode='lines',
                hoverinfo='x+y+name',
                yaxis='y1',
            )
        )
        fig.add_traces(
            go.Scatter(
                name=f'Phase(Z) {idx}',
                x=cycle.data.frequency,
                y=cycle.data.z_angle,
                mode='lines',
                hoverinfo='x+y+name',
                yaxis='y2',
            )
        )
    fig.update_layout(
        title_text='Bode Plot',
        showlegend=True,
        xaxis={
            'fixedrange': False,
            'type': 'log',
            'title': f'Frequency ({measurements[0].data.frequency.units:~P})',
        },
        yaxis={
            'title': f'|Z| ({measurements[0].data.z_modulus.units:~P})',
            'fixedrange': False,
        },
        yaxis2={
            'title': f'Phase ({measurements[0].data.z_angle.units:~P})',
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
    for idx, cycle in enumerate(cycles):
        if cycle.voltage_rhe_compensated is None or cycle.current_density is None:
            return fig
        fig.add_traces(
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
            'title': f'Voltage RHE compensated ({cycles[0].voltage_rhe_compensated.units:~P})',
        },
        yaxis={
            'fixedrange': False,
            'title': f'Current Density ({cycles[0].current_density.units:~P})',
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
        fig.add_traces(
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


def make_nyquist_plot(measurements):
    fig = go.Figure().update_layout(
        title_text='Nyquist Plot',
    )
    if measurements is None:
        return fig
    for idx, cycle in enumerate(measurements):
        if cycle.data is None:
            return fig
        if cycle.data.z_imaginary is None or cycle.data.z_real is None:
            return fig
        fig.add_traces(
            go.Scatter(
                name=f'Nyquist {idx}',
                x=cycle.data.z_real,
                y=cycle.data.z_imaginary,
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
