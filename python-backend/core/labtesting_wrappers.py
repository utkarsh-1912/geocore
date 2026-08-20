# Author: Utkarsh Gupta
# License: GPL v2


import numpy as np
import json
import plotly.io
from groundhog.siteinvestigation.labtesting.indextests import PlasticityChart, PSDChart
from scipy.interpolate import interp1d
from scipy.optimize import root

def plasticitychart_wrapper(args):
    chart = PlasticityChart(
        plot_height=args.get('plot_height', 500),
        plot_width=args.get('plot_width', 800),
        plot_title=args.get('plot_title')
    )
    
    ll = args.get('ll')
    pi = args.get('pi')
    name = args.get('name', 'Sample')
    
    if ll and pi:
        chart.add_trace(ll, pi, name)
        
    json_str = plotly.io.to_json(chart.fig)
    fig_dict = json.loads(json_str)
    return {
        "type": "plotly",
        "data": fig_dict['data'],
        "layout": fig_dict['layout']
    }

def psdchart_wrapper(args):
    chart = PSDChart(
        plot_title=args.get('plot_title')
    )
    
    grainsize = args.get('grainsize')
    pctpassing = args.get('pctpassing')
    name = args.get('name', 'Sample')
    
    if grainsize and pctpassing:
        chart.add_trace(grainsize, pctpassing, name)
        
    json_str = plotly.io.to_json(chart.fig)
    fig_dict = json.loads(json_str)
    return {
        "type": "plotly",
        "data": fig_dict['data'],
        "layout": fig_dict['layout']
    }

def roottimemethod_wrapper(args):
    """
    Non-interactive version of roottimemethod.
    If 'selection_points' is provided, uses them.
    Otherwise, returns the data for the plot to allow selection in frontend.
    """
    times = np.array(args.get('times'))
    settlements = np.array(args.get('settlements'))
    drainagelength = float(args.get('drainagelength'))
    selection = args.get('selection') # Expecting list of 2 points [[x1,y1], [x2,y2]]
    
    if not selection or len(selection) < 2:
        # Return data for plotting so user can select
        return {
            "type": "plotly",
            "message": "Please select point O and a point on the straight portion OA.",
            "data": [{
                "x": np.sqrt(times).tolist(),
                "y": settlements.tolist(),
                "mode": "lines+markers",
                "name": "Data"
            }],
            "layout": {
                "xaxis": {"title": "sqrt(t)"},
                "yaxis": {"title": "Settlement [mm]", "autorange": "reversed"}
            },
            "interactive_required": True,
            "steps": ["Select Origin O", "Select point on OA"]
        }

    # Core Logic (adapted from groundhog)
    settlement_abcis = 1.1 * settlements.max()
    xy = selection
    
    # Interpolate the selection
    pointO = (xy[0][0], np.interp(xy[0][0], np.sqrt(times), settlements))
    pointD = (xy[1][0], np.interp(xy[1][0], np.sqrt(times), settlements))

    # Create the interpolation function
    roottime_interpolation_func = interp1d([pointO[1], pointD[1]], [pointO[0], pointD[0]], fill_value='extrapolate')
    pointA = (float(roottime_interpolation_func(settlement_abcis)), float(settlement_abcis))
    pointB = (1.15 * pointA[0], float(settlement_abcis))

    # Find the intersection of OB and the data
    OB_func = interp1d([pointO[0], pointB[0]], [pointO[1], pointB[1]], fill_value='extrapolate')
    data_func = interp1d(np.sqrt(times), settlements)

    def intersection(x):
        return OB_func(x) - data_func(x)
    
    initial_guess = pointA[0]
    sqrt_t90 = float(root(intersection, initial_guess).x[0])

    cv_roottime = (0.848 * (drainagelength) ** 2) / (sqrt_t90 ** 2)
    cv_roottime_m2year = cv_roottime * 3600 * 24 * 365
    
    return {
        "t90 [s]": sqrt_t90 ** 2,
        "cv [m2/s]": cv_roottime,
        "cv [m2/yr]": cv_roottime_m2year,
        "pointO": pointO,
        "pointA": pointA,
        "pointB": pointB,
        "sqrt_t90": sqrt_t90
    }

def logtimemethod_wrapper(args):
    """
    Non-interactive version of logtimemethod.
    """
    times = np.array(args.get('times'))
    settlements = np.array(args.get('settlements'))
    drainagelength = float(args.get('drainagelength'))
    
    # Needs: xy_primary (2 pts), xy_secondary (2 pts), pointB (1 pt)
    xy_primary = args.get('xy_primary')
    xy_secondary = args.get('xy_secondary')
    xy_B_input = args.get('pointB')
    
    if not (xy_primary and xy_secondary and xy_B_input):
         return {
            "type": "plotly",
            "message": "Interactive selection required.",
            "data": [{
                "x": np.log10(times).tolist(),
                "y": settlements.tolist(),
                "mode": "lines+markers",
                "name": "Data"
            }],
            "layout": {
                "xaxis": {"title": "log10(t)", "type": "linear"},
                "yaxis": {"title": "Settlement [mm]", "autorange": "reversed"}
            },
            "interactive_required": True,
            "steps": [
                "Select 2 points on primary consolidation",
                "Select 2 points on secondary consolidation",
                "Select point B close to head (U < 60%)"
            ]
        }

    # Core logic
    log_times = np.log10(times)
    
    y1_p = np.interp(xy_primary[0][0], log_times, settlements)
    y2_p = np.interp(xy_primary[1][0], log_times, settlements)
    primary_func = interp1d([xy_primary[0][0], xy_primary[1][0]], [y1_p, y2_p], fill_value='extrapolate')
    
    y1_s = np.interp(xy_secondary[0][0], log_times, settlements)
    y2_s = np.interp(xy_secondary[1][0], log_times, settlements)
    secondary_func = interp1d([xy_secondary[0][0], xy_secondary[1][0]], [y1_s, y2_s], fill_value='extrapolate')
    
    def intersection_primary_secondary(x):
        return primary_func(x) - secondary_func(x)
    
    log_t100 = float(root(intersection_primary_secondary, xy_primary[0][0]).x[0])
    yA = float(primary_func(log_t100))
    
    xB = xy_B_input[0][0]
    yB = float(np.interp(xB, log_times, settlements))
    xC = np.log10(10**xB * 4)
    yC = float(np.interp(xC, log_times, settlements))
    
    Delta_d = abs(yC - yB)
    yD = yB - Delta_d
    yE = 0.5 * (yD + yA)
    # Reversing for interpolation: find x for a given y
    xE = float(np.interp(yE, settlements, log_times))
    t50 = 10**xE
    
    cv_logtime = (0.197 * (drainagelength)**2) / t50
    cv_logtime_m2year = cv_logtime * 3600 * 24 * 365
    
    return {
        "t100 [s]": 10**log_t100,
        "t50 [s]": t50,
        "cv [m2/s]": cv_logtime,
        "cv [m2/yr]": cv_logtime_m2year,
        "point_d100": (log_t100, yA),
        "point_d0": (xB, yD),
        "point_d50": (xE, yE)
    }
