---
title: Tutorial - Pore pressure dissipation
slug: groundhog/tutorials/tutorial-pore-pressure-dissipation
section: Groundhog Guides
description: Since v0.8.0, groundhog includes a finite difference routine to calculate pore pressure dissipation.
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/v0.15.0/notebooks/Tutorial%20-%20Pore%20pressure%20dissipation.ipynb
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.15.0
edited_by_geocore: true
geocore_edit_note: 'Converted from a Jupyter notebook: Markdown cells kept, code cells shown as code, text and image outputs reproduced, interactive Plotly/HTML outputs omitted, with a short note on how to run this in GeoCore prepended.'
notebook: notebooks/Tutorial - Pore pressure dissipation.ipynb
---

> **Adapted from groundhog's own documentation.** Inside GeoCore, run the same calculation through a [calculation form](/docs/geocore/using/modules) or by asking **GeoAI**, which calls the same groundhog function through its validated Tool Registry. This notebook is kept for anyone who wants to call groundhog directly from their own Python code instead.

Since v0.8.0, ``groundhog`` includes a finite difference routine to calculate pore pressure dissipation. 

The one-dimensional consolidation equation has the following form:

$$ \frac{\partial u}{\partial t} = c_v \frac{\partial^2 u}{\partial^2 z} $$ 

This equation can be solved using two solutions, being Fourier series and finite differences. Both are elaborated in this notebook. The finite difference solution has the advantage of greater flexibility of the input (e.g. variation of $ c_v $ with depth.

## Solution based on Fourier series

The function ``pore_pressure_fourier`` returns the excess pore pressure distribution at the specified depths for a given time. Note that the Fourier series solution only applies for uniform initial excess pore pressure distributions as commonly observed in thin layers. In thick clay layers, where triangular distributions are more common, this solution does not apply. If the stress distribution is irregular, a numerical solution should be applied.

As an infinite amount of terms cannot be evaluated, the sum is limited to a number of terms (1000 by default) which should be sufficient for convergence.

$$ \begin{align}\begin{aligned}\Delta u (z,t) = \sum_{m=0}^{\infty} \frac{2 \Delta u_0}{M} \sin \left( \frac{M \cdot z}{H_{dr}} \right) \exp \left( -M^2 T_v \right)\\M = \frac{\pi}{2} \left( 2m + 1 \right)\\T_v = \frac{c_v t}{H_{dr}^2}\end{aligned}\end{align} $$

```python
import numpy as np
```

```python
from plotly import tools, subplots
import plotly.graph_objs as go
```

As an example, the solution with Fourier series can be calculated at the time when the pore pressure increment is applied ($ t $=0) and after 1e5 seconds (for a coefficient of consolidation $ c_v $=10m$^2$/yr).

The layer considered is 1m thick and an excess pore pressure of 50kPa is applied.

```python
from groundhog.consolidation.dissipation.onedimensionalconsolidation import pore_pressure_fourier
```

```python
fourier_solution_0 = pore_pressure_fourier(
    delta_u_0=50, # kPa
    depths=np.linspace(0, 1, 100),
    time=0, # s
    cv=10, # m2/yr
    layer_thickness=1 #m
)
fourier_solution_100000 = pore_pressure_fourier(
    delta_u_0=50, # kPa
    depths=np.linspace(0, 1, 100),
    time=1e5, # s
    cv=10, # m2/yr
    layer_thickness=1 #m
)
```

The two solutions can be visualised. As expected, the excess pore pressure is uniform and equal to the applied excess pore pressure at the start of the analysis. After 1e5 seconds, the excess pore pressure at the center is still at 90% of the initial value. The double drainage condition is clearly visible from the graph.

```python
fig = subplots.make_subplots(rows=1, cols=1, print_grid=False)
_data = go.Scatter(x=fourier_solution_0['delta u [kPa]'],
                   y=np.linspace(0, 1, 100), showlegend=True, mode='lines',name='t=0s')
fig.append_trace(_data, 1, 1)
_data = go.Scatter(x=fourier_solution_100000['delta u [kPa]'],
                   y=np.linspace(0, 1, 100), showlegend=True, mode='lines',name='t=1e5s')
fig.append_trace(_data, 1, 1)
fig['layout']['xaxis1'].update(title=r'$ \Delta u \ \text{[kPa]} $')
fig['layout']['yaxis1'].update(title=r'$ z \ \text{[m]} $')
fig['layout'].update(height=500, width=600, title='Fourier series solution')
fig.show()
```

![Notebook output 1](/docs/assets/groundhog/notebooks/outputs/tutorial-pore-pressure-dissipation-1.png)

*Interactive output (Plotly/HTML) is not reproduced here; run the notebook to see it.*

## Average degree of consolidation

For certain problems, only the average degree of consolidation $ U $ needs to be known. The average degree of consolidation can be visualised as the area between the initial excess pore pressure distribution and the current isochrone.

The average degree of consolidation is interpolated from published curves.

In ``groundhog``, the function ``consolidation_degree`` contains these curves for uniform and triangular distributions.

```python
from groundhog.consolidation.dissipation.onedimensionalconsolidation import consolidation_degree
```

The average degree of consolidation can be evaluated for both distributions. Note that the drainage length for the triangular distribution is double that for the uniform distribution!

```python
times = np.logspace(0, 7, 1000)

U_uniform = list(map(lambda _t: consolidation_degree(
    time=_t, cv=10, drainage_length=0.5)['U [pct]'], times))
Tv_uniform = list(map(lambda _t: consolidation_degree(
    time=_t, cv=10, drainage_length=0.5)['Tv [-]'], times))
U_triangular = list(map(lambda _t: consolidation_degree(
    time=_t, cv=10, drainage_length=1, distribution='triangular')['U [pct]'], times))
Tv_triangular = list(map(lambda _t: consolidation_degree(
    time=_t, cv=10, drainage_length=1, distribution='triangular')['Tv [-]'], times))
```

The results can be visualised, both in terms of time factor $ T_v $ and of absolute time.

```python
fig = subplots.make_subplots(rows=2, cols=1, print_grid=False)
_data = go.Scatter(x=Tv_uniform,
                   y=U_uniform, showlegend=True, mode='lines',name='Uniform',
                   line=dict(color='blue'))
fig.append_trace(_data, 1, 1)
_data = go.Scatter(x=Tv_triangular,
                   y=U_triangular, showlegend=True, mode='lines',name='Triangular',
                   line=dict(color='red'))
fig.append_trace(_data, 1, 1)
_data = go.Scatter(x=times,
                   y=U_uniform, showlegend=False, mode='lines',name='Uniform',
                   line=dict(color='blue'))
fig.append_trace(_data, 2, 1)
_data = go.Scatter(x=times,
                   y=U_triangular, showlegend=False, mode='lines',name='Triangular',
                   line=dict(color='red'))
fig.append_trace(_data, 2, 1)
fig['layout']['xaxis1'].update(title=r'$ T_v \ \text{[-]} $', range=(0, 1.2))
fig['layout']['yaxis1'].update(title=r'$ U \ \text{[%]} $')
fig['layout']['xaxis2'].update(title=r'$ t \ \text{[s]} $', range=(0, 4e6))
fig['layout']['yaxis2'].update(title=r'$ U \ \text{[%]} $')
fig['layout'].update(height=600, width=900, title='Average degree of consolidation')
fig.show()
```

![Notebook output 2](/docs/assets/groundhog/notebooks/outputs/tutorial-pore-pressure-dissipation-2.png)

## Finite difference solution

The consolidation equation can be discretised as follows:

$$ u_{i,j+1} = u_{i,j} + \frac{c_v \Delta t}{( \Delta z )^2} \left( u_{i-1,j} - 2 u_{i,j} + u_{i+1,j} \right) $$

At permeable boundaries, the excess pore pressure is 0 ($ u = 0 $). At impervious boundaries, the following boundary condition applies:

$$ \frac{\partial u}{\partial z} = 0 = \frac{1}{2 \Delta z} \left( u_{i-1,j} - u_{i+1,j} \right) = 0$$

$$ \implies u_{i,j+1} = u_{i,j} + \frac{c_v \Delta t}{( \Delta z )^2}  \left( 2 u_{i-1,j} - 2 u_{i,j} \right) $$

To ensure stability, the timestep needs to be chosen according to the following criterion:

$$ \alpha = \frac{c_v \Delta t}{(\Delta z)^2} < \frac{1}{2} $$

Usually, $ \alpha = 0.25 $ is used to determine the timestep.

The discretisation in space and time is done as follows where the number of timesteps is usually calculated from a chosen node offset:

$$ \Delta z = \frac{H_0}{m}, \ \Delta t = \frac{t}{n} $$

``groundhog`` includes the class ``ConsolidationCalculation`` to perform the pore pressure dissipation analysis.

### Pore pressure dissipation for double drainage

The solution previously developed for Fourier series can be replicated using the finite difference solution:

```python
from groundhog.consolidation.dissipation.onedimensionalconsolidation import ConsolidationCalculation
```

The calculation is initiated by specifying the height of the layer (1m in this example) and the total duration of the analysis. The number of nodes along the depth axis is also specified.

Next, the value of $ c_v $ is set in m$ ^2$/yr.

Subsequently, the drainage conditions of top and bottom boundary are specified.

The initial excess pore pressure distribution is specified by entering an array with initial excess pore pressure values and the corresponding depths.

Finally, the times at which output is stored are specified. A plot can then be generated.

```python
calc = ConsolidationCalculation(height=1, total_time=1e6, no_nodes=51)
calc.set_cv(cv=10)
calc.set_top_boundary(freedrainage=True)
calc.set_bottom_boundary(freedrainage=True)
calc.set_initial(u0=[50, 50], u0_depths=[0, 1])
calc.set_output_times(output_times=np.array([0, 1e5, 2e5, 4e5, 1e6]))
calc.calculate()
calc.plot_results(plot_title=r'$ \text{Uniform - } c_v = 10m^2/yr $')
```

![Notebook output 3](/docs/assets/groundhog/notebooks/outputs/tutorial-pore-pressure-dissipation-3.png)

The same solution as for the Fourier series is found.

### Pore pressure dissipation for top drainage

The pore pressure dissipation for an initial triangular stress distribution and an impervious base can also be calculated.

Only the bottom drainage condition and the initial excess pore pressure distribution need to be changed.

```python
calc = ConsolidationCalculation(height=1, total_time=1e5, no_nodes=51)
calc.set_cv(cv=10)
calc.set_top_boundary(freedrainage=True)
calc.set_bottom_boundary(freedrainage=False)
calc.set_initial(u0=[0, 50], u0_depths=[0, 1])
calc.set_output_times(output_times=np.array([0, 1e5]))
calc.calculate()
calc.plot_results(plot_title=r'$ \text{Triangular - } c_v = 10m^2/yr $')
```

![Notebook output 4](/docs/assets/groundhog/notebooks/outputs/tutorial-pore-pressure-dissipation-4.png)

### Pore pressure dissipation for non-uniform $ c_v $

The pore pressure dissipation for double drainage and an uniform initial excess pore pressure distribution but with a much more non-permeable lens inside the sample can be calculated.

The specification of $ c_v $ changes to include values of $ c_v $ and their corresponding depths.

```python
from groundhog.consolidation.dissipation.onedimensionalconsolidation import ConsolidationCalculation
calc = ConsolidationCalculation(height=1, total_time=1e4, no_nodes=51)
calc.set_cv(
    cv=np.array([1000, 1000, 10, 10, 1000, 1000]),
    cv_depths=np.array([0, 0.4, 0.40000001, 0.59999999, 0.6, 1]), uniform=False)
calc.set_top_boundary(freedrainage=True)
calc.set_bottom_boundary(freedrainage=True)
calc.set_initial(u0=[50, 50], u0_depths=[0, 1])
calc.set_output_times(output_times=np.array([0, 1e3, 1e4, 1e5]))
calc.calculate()
calc.plot_results(plot_title=r'$ \text{Uniform - Impermeable lens between 0.4 and 0.6m} $')
```

![Notebook output 5](/docs/assets/groundhog/notebooks/outputs/tutorial-pore-pressure-dissipation-5.png)
