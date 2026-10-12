# Author: Utkarsh Gupta
# License: GPL v3
"""
Groundhog functions that GeoCore overrides because the installed version (0.16.0) returns a wrong number or fails.

Each correction keeps the Groundhog function's name, module, signature, docstring, validation and return
keys, so the desktop calculators and the GeoAI tools (both built from ``Registry.function_map``) use it
without further changes. Every entry is checked against a closed form in tests/test_groundhog_corrections.py
and should be dropped once Groundhog fixes it upstream.

mohrcoulomb_triaxial_compression
    Groundhog solves for the axial stress at failure with ``np.sin(np.radians(phi) * np.tan(np.radians(phi)))``
    where the derivation has ``sin(phi) * tan(phi)``. The result is exact only at phi = 0 and 45 degrees and is
    otherwise too high: sigma_3 = 100 kPa, c = 0, phi = 30 degrees gives 301.57 kPa instead of 300, and the
    Mohr circle then misses the failure envelope. The circle, the figure and the other outputs are Groundhog's
    own construction (Budhu, 2011), only fed with the correct sigma_1.

acousticimpedance_bulkunitweight_chen
    Groundhog validates its documented ranges (G_s 1.0-3.0, gamma 12-22 kN/m3) and then calls the phase-relation
    helpers voidratio_bulkunitweight and porosity_voidratio, which validate again with narrower ranges (G_s
    2.4-2.9, e <= 5). Outside those the helpers return their error output: for G_s = 2.0 the void-ratio helper
    returns no 'w [-]' and the function raises KeyError: 'w [-]'; for gamma = 12 kN/m3 (e = 7.25) the porosity
    is NaN and so is the impedance. The correction calls the same helpers without that second validation; the
    equations and outputs are Groundhog's.
"""
import functools

import numpy as np
import pandas as pd
import plotly.graph_objs as go
from groundhog.constitutivemodels import general
from groundhog.general.validation import Validator
from groundhog.siteinvestigation.classification import phaserelations
from groundhog.siteinvestigation.correlations import general as correlations_general
from plotly import subplots


@Validator(general.MOHRCOULOMB_TRIAXIAL_COMPRESSION, general.MOHRCOULOMB_TRIAXIAL_COMPRESSION_ERRORRETURN)
def _mohrcoulomb_triaxial_compression(sigma_3, cohesion, phi, latex_titles=True, **kwargs):
    phi_rad = np.radians(phi)
    if np.sin(phi_rad) >= 1.0:
        # phi = 90 degrees: the axial stress at failure is unbounded. Raising makes the Validator return NaN,
        # as it does for any other input Groundhog cannot solve.
        raise ZeroDivisionError("The axial stress at failure is unbounded for phi = 90 degrees.")

    # Closed form of  R cos(phi) = c + (R + sigma_3 - R sin(phi)) tan(phi),  sigma_1 = sigma_3 + 2R.
    _sigma_1_f = (sigma_3 * (1 + np.sin(phi_rad)) + 2 * cohesion * np.cos(phi_rad)) / (1 - np.sin(phi_rad))

    _center = 0.5 * (sigma_3 + _sigma_1_f)
    _radius = 0.5 * (_sigma_1_f - sigma_3)

    _failure_angle = 0.5 * (np.rad2deg(0.5 * np.pi - phi_rad))

    _tau_f = _radius * np.cos(phi_rad)
    _sigma_f = _center - _radius * np.sin(phi_rad)

    _mohr_circle = pd.DataFrame({
        'tau [kPa]': _radius * np.sin(np.linspace(0, 2 * np.pi, 250)),
        'sigma [kPa]': _center + _radius * np.cos(np.linspace(0, 2 * np.pi, 250))
    })
    fig = subplots.make_subplots(rows=1, cols=2, print_grid=False, column_widths=[0.7, 0.3])
    fig.append_trace(go.Scatter(
        x=_mohr_circle['sigma [kPa]'], y=_mohr_circle['tau [kPa]'],
        showlegend=True, mode='lines', name='Mohr circle',
        line=dict(color='black')), 1, 1)
    fig.append_trace(go.Scatter(
        x=np.linspace(0, _sigma_1_f, 250), y=cohesion + np.tan(phi_rad) * np.linspace(0, _sigma_1_f, 250),
        showlegend=True, mode='lines', name='Mohr-Coulomb criterion',
        line=dict(color='red', dash='dot')), 1, 1)
    fig.append_trace(go.Scatter(
        x=[_center, _sigma_f], y=[0, _tau_f], showlegend=False, mode='lines',
        name='Location of stress state', line=dict(color='green')), 1, 1)
    fig.append_trace(go.Scatter(
        x=[_sigma_f, ], y=[_tau_f, ], showlegend=False, mode='markers', name='Location of stress state',
        marker=dict(size=7, color='green', line=dict(width=1, color='black'))), 1, 1)
    fig.append_trace(go.Scatter(
        x=[0, 1, 1, 0, 0], y=[0, 0, 1, 1, 0], showlegend=True, mode='lines',
        name='Sample', line=dict(color='black')), 1, 2)
    fig.append_trace(go.Scatter(
        x=[0.5 + 0.5 * np.tan(np.radians(_failure_angle)), 0.5 + -0.5 * np.tan(np.radians(_failure_angle))], y=[0, 1],
        showlegend=True, mode='lines', name='Orientation of selected plane', line=dict(dash='dot')), 1, 2)

    if latex_titles:
        fig['layout']['xaxis1'].update(title=r'$ \sigma \ \text{[kPa]}$')
        fig['layout']['yaxis1'].update(title=r'$ \tau \ \text{[kPa]}$', scaleanchor='x', scaleratio=1.0)
        fig['layout']['xaxis2'].update(title=r'$ X $')
        fig['layout']['yaxis2'].update(title=r'$ Y $', scaleanchor='x2', scaleratio=1.0)
    else:
        fig['layout']['xaxis1'].update(title='sigma [kPa]')
        fig['layout']['yaxis1'].update(title='tau [kPa]', scaleanchor='x', scaleratio=1.0)
        fig['layout']['xaxis2'].update(title='X')
        fig['layout']['yaxis2'].update(title='Y', scaleanchor='x2', scaleratio=1.0)
    fig['layout'].update(height=500, width=900)

    return {
        'sigma_1_f [kPa]': _sigma_1_f,
        'sigma_3_f [kPa]': sigma_3,
        'Failure angle [deg]': _failure_angle,
        'tau_f [kPa]': _tau_f,
        'sigma_f [kPa]': _sigma_f,
        'center [kPa]': _center,
        'radius [kPa]': _radius,
        'Mohr circle': _mohr_circle,
        'Plot': fig,
    }


# Name, module, docstring and signature of Groundhog's function, so everything built from it is unchanged.
mohrcoulomb_triaxial_compression = functools.wraps(general.mohrcoulomb_triaxial_compression)(
    _mohrcoulomb_triaxial_compression)



@Validator(correlations_general.ACOUSTICIMPEDANCE_BULKUNITWEIGHT_CHEN,
           correlations_general.ACOUSTICIMPEDANCE_BULKUNITWEIGHT_CHEN_ERRORRETURN)
def _acousticimpedance_bulkunitweight_chen(
        bulkunitweight, specific_gravity=2.65, saturation=1.0, gamma_w=10.0, calibration_factor_4=0.0001315,
        calibration_factor_3=-0.03776, calibration_factor_2=4.201, calibration_factor_1=-245.0,
        calibration_factor_0=8603.0, **kwargs):
    # The inputs were validated above against this function's own ranges; the helpers only compute.
    _e = phaserelations.voidratio_bulkunitweight(
        bulkunitweight=bulkunitweight, saturation=saturation, specific_gravity=specific_gravity,
        unitweight_water=gamma_w, validate=False, fail_silently=False)['e [-]']
    if _e < 0:
        # gamma > G_s gamma_w: denser than the solids themselves. Raising makes the Validator return NaN,
        # as Groundhog's porosity helper did for a negative void ratio.
        raise ValueError(f"Bulk unit weight {bulkunitweight} kN/m3 exceeds G_s * gamma_w = "
                         f"{specific_gravity * gamma_w:g} kN/m3: the void ratio would be negative.")
    _n = phaserelations.porosity_voidratio(voidratio=_e, validate=False, fail_silently=False)['porosity [-]']
    _I = calibration_factor_4 * (100 * _n) ** 4 +         calibration_factor_3 * (100 * _n) ** 3 +         calibration_factor_2 * (100 * _n) ** 2 +         calibration_factor_1 * (100 * _n) +         calibration_factor_0

    return {
        'e [-]': _e,
        'n [-]': _n,
        'I [(m/s).(g/cm3)]': _I,
    }


acousticimpedance_bulkunitweight_chen = functools.wraps(correlations_general.acousticimpedance_bulkunitweight_chen)(
    _acousticimpedance_bulkunitweight_chen)

#: function name -> corrected callable; Registry.function_map takes these over Groundhog's.
CORRECTED_FUNCTIONS = {
    "mohrcoulomb_triaxial_compression": mohrcoulomb_triaxial_compression,
    "acousticimpedance_bulkunitweight_chen": acousticimpedance_bulkunitweight_chen,
}
