---
title: Tutorial - Basic use of groundhog functions
slug: groundhog/tutorials/tutorial-basic-use-of-groundhog-functions
section: Groundhog Guides
description: The
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/v0.15.0/notebooks/Tutorial%20-%20Basic%20use%20of%20groundhog%20functions.ipynb
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.15.0
edited_by_geocore: true
geocore_edit_note: 'Converted from a Jupyter notebook: Markdown cells kept, code cells shown as code, text and image outputs reproduced, interactive Plotly/HTML outputs omitted, with a short note on how to run this in GeoCore prepended.'
notebook: notebooks/Tutorial - Basic use of groundhog functions.ipynb
---

> **Adapted from groundhog's own documentation.** Inside GeoCore, run the same calculation through a [calculation form](/docs/geocore/using/modules) or by asking **GeoAI**, which calls the same groundhog function through its validated Tool Registry. This notebook is kept for anyone who wants to call groundhog directly from their own Python code instead.

The ```groundhog``` library contains geotechnical functions was built around the following core principles:

   - Transparency: Each function needs to be documented extensively and the user should always know which parameters to enter
   - Validation: When expert knowledge or calibration to experiments dictates that parameters cannot vary outside a certain range, the calculation should be prevented. At the same time, the user should be able to override this behaviour when extrapolation is required
   - Testing: Each function should be checked before being released. When new versions are released, the unit test suite is reperformed to ensure that code changes don't break previous functionality
   - Convergence: Contributions to ```groundhog``` are essential, both in terms of introducing new functions as in comments, checks and feedback on the previous ones. For this reason, ```groundhog``` is managed on Github. 
   
This notebook contains a short introduction to ```groundhog``` and shows how these core principles are reflected in the code.

## Importing ```groundhog```

```groundhog``` is a Python library and thus it needs to be imported like any other Python library. 

To check which version of ```groundhog``` you have. You can import the package and check the version as follows:

```python
from groundhog.__version__ import __version__
__version__
```

```groundhog``` contains several subpackages for a variety of applications (e.g. ```siteinvestigation``` contains functions related to geotechnical investigations. We can import specific functions using the following syntax:

```python
from groundhog.siteinvestigation.insitutests.pcpt_correlations import relativedensity_sand_jamiolkowski
```

This imports the function ```relativedensity_sand_jamiolkowski``` from the ```pcpt_correlations``` module of the ```siteinvestigation.insitutests``` subpackage.

We can check the function documentation in the notebook as follows:

```python
?relativedensity_sand_jamiolkowski
```

The documentation shows that the relative density of sand from cone resistance data based on calibration chamber test results (Jamiolkowski et al, 2003). A formula for dry and saturated sand is provided.

$$ D_{r,dry} = \frac{1}{2.96} \cdot \ln \left[ \frac{q_c / P_a}{24.94 \cdot \left( \frac{\sigma_{m}^{\prime}}{P_a} \right)^{0.46} } \right] $$

$$ D_{r,sat} = \left(  \frac{-1.87 + 2.32 \cdot \ln \left[ \frac{q_c}{\sqrt{P_a + \sigma_{vo}^{\prime}}} \right] }{100} \right) \cdot \frac{D_{r,dry}}{100} $$

The formula is fully parametric with all coefficients of the equations being modifiable as optional keyword arguments.

## Transparency

```groundhog``` has with extensive documentation. The documentation is available here: https://www.snakesonabrain.com/docs/groundhog.

Each function has a docstring contains a description of the function, a list of its input parameters with units, equations and images, a description of the output and one or more references. In almost all cases, the output of ```groundhog``` functions is a dictionary with keys containing the main output and intermediate outputs. These keys also show the unit of the outputs.

We can apply this on the function ```relativedensity_sand_jamiolkowski```. We will calculate the relative density for a vertical effective stress of 100kPa, a coefficient of lateral earth pressure of 0.8 and a cone resistance of 20MPa. Note that the docstring contains the units of these input parameters and recommendations on the acceptable ranges. All optional parameters are left at their defaults.

```python
relativedensity_sand_jamiolkowski(qc=20, sigma_vo_eff=100, k0=0.8)
```

The result is a dictionary containing two outputs; the relative density for dry and saturated soil (unitless).

If we are just interested in the relative density for saturated soil, we can simply retrieve this value from the dictionary using the corresponding key.

```python
result = relativedensity_sand_jamiolkowski(qc=20, sigma_vo_eff=100, k0=0.8)
result['Dr sat [-]']
```

## Validation

Our docstring already shows that unit and acceptable ranges are given in the docs. It is good to know what happens when we go outside acceptable ranges and how we can make ```groundhog``` return the behaviour we want.

### Default behaviour - Failing silently

By default, ```groundhog``` will not raise errors when parameters are outside validation ranges. This choice was consciously made to prevent errors from manifesting themselves too often and having to write error catching clauses in all code.

Instead, when a parameter is outside a validation range, ```groundhog``` will return ```np.nan``` for a scalar and ```None``` for a list by default, however the outputs in case of errors can be changed.

We can illustrate this behaviour by working with vertical effectice stresses ranging from 10kPa to 500kPa, with $ \sigma_{vo}^{\prime} $ < 50kPa and $ \sigma_{vo}^{\prime} $ > 400kPa being outside the validation range according to the data originally used to develop this correlation. The cone resistance is kept constant at 20MPa.

```python
import numpy as np
sigma_vo_eff = np.linspace(10, 500, 20)
dr_sat = list(map(lambda _sigma_v_eff: relativedensity_sand_jamiolkowski(
    qc=20, sigma_vo_eff=_sigma_v_eff, k0=0.8)['Dr sat [-]'], sigma_vo_eff))
```

```python
dr_sat
```

```groundhog``` will issue warnings but the calculation will still go ahead. For long lists, the warnings could be annoying. We can hide warnings with the following syntax:

```python
import warnings
warnings.filterwarnings('ignore')
```

<div class="alert alert-block alert-danger">
<b>Caution:</b> This will suppress all warnings so use it carefully!
</div>

Let's check the value of the last friction factor to see what was returned.

```python
dr_sat[-1]
```

Because the value return is ```np.nan```, plots can still be created of the results. We can create a basic Plotly plot of the result (import the necessary Plotly modules and functions first).

```python
from plotly import subplots
import plotly.graph_objs as go
from plotly.offline import init_notebook_mode
import plotly.io as pio
init_notebook_mode()
pio.templates.default = 'plotly_white'
```

```python
fig = subplots.make_subplots(rows=1, cols=1, print_grid=False)
_data = go.Scatter(x=sigma_vo_eff, y=dr_sat, showlegend=False, mode='lines',name='Dr')
fig.append_trace(_data, 1, 1)
fig['layout']['xaxis1'].update(title='Vertical effective stress [kPa]')
fig['layout']['yaxis1'].update(title='Relative density [-]')
fig['layout'].update(height=400, width=600)
fig.show()
```

The plot only shows the results for vertical effective stresses which are inside the validation range (50 - 400kPa)

### Overriding validation ranges

In certain cases, equations will still apply, even when the input parameters are outside of the validation ranges. ```groundhog``` allows us to override the default validation ranges. If we add ```<parametername>__min=``` and/or ```<parametername>__max``` to the function arguments, we are overriding the validation ranges. Let's see this in action:

```python
dr_sat_withoverride = list(map(lambda _sigma_v_eff: relativedensity_sand_jamiolkowski(
    qc=20, sigma_vo_eff=_sigma_v_eff, k0=0.8,
    sigma_vo_eff__min=10, sigma_vo_eff__max=500)['Dr sat [-]'], sigma_vo_eff))
```

The calculation now returns values for $ \sigma_{vo}^{\prime} $ outside the default range and at the same time, it is clear for a code reviewer that a validation range was manipulated here! The resulting plot is shown below.

```python
fig = subplots.make_subplots(rows=1, cols=1, print_grid=False)
_data = go.Scatter(x=sigma_vo_eff, y=dr_sat_withoverride, showlegend=False, mode='lines',name='Dr')
fig.append_trace(_data, 1, 1)
fig['layout']['xaxis1'].update(title='Vertical effective stress [kPa]')
fig['layout']['yaxis1'].update(title='Relative density [-]')
fig['layout'].update(height=400, width=600)
fig.show()
```

### Overriding the values returned when exceeding validation ranges

```groundhog``` knows which values to return when a validation range is exceeded because it uses a dictionary which defines these values. This dictionary can also be imported and printed. The name is defined as follows:

```
<functionnameuppercase>_ERRORRETURN
```

We can override this dictionary to control what ```groundhog``` returns when the validation is not met or when there are errors during function execution.

```python
from groundhog.siteinvestigation.insitutests.pcpt_correlations import RELATIVEDENSITY_SAND_JAMIOLKOWSKI_ERRORRETURN
RELATIVEDENSITY_SAND_JAMIOLKOWSKI_ERRORRETURN
```

If we modify this dictionary and pass it to the function, we can obtain another output when exceeding the validation ranges. For instance, let's return a relative density of 0 when the input is not valid:

```python
new_error_return= RELATIVEDENSITY_SAND_JAMIOLKOWSKI_ERRORRETURN
new_error_return['Dr sat [-]'] = 0.0
new_error_return
```

We need to add this dictionary to the function call by specifying the keyword argument ```customerroroutput```.

```python
dr_sat_zeroonerror = list(map(lambda _sigma_v_eff: relativedensity_sand_jamiolkowski(
    qc=20, sigma_vo_eff=_sigma_v_eff, k0=0.8,
    customerroroutput=new_error_return)['Dr sat [-]'], sigma_vo_eff))
```

If we plot the result, we can see that the function returns a relative density of 0 when the parameter is outside of the validation ranges.

```python
fig = subplots.make_subplots(rows=1, cols=1, print_grid=False)
_data = go.Scatter(x=sigma_vo_eff, y=dr_sat_zeroonerror, showlegend=False, mode='lines',name='Dr')
fig.append_trace(_data, 1, 1)
fig['layout']['xaxis1'].update(title='Vertical effective stress [kPa]')
fig['layout']['yaxis1'].update(title='Relative density [-]')
fig['layout'].update(height=400, width=600)
fig.show()
```

### Raising errors

In certain cases, you do not want the function to fail silently. To trigger raising of errors, just include the keyword argument ```fail_silently=False```.

Let's demonstrates how this raises an error which stops code execution.

```python
relativedensity_sand_jamiolkowski(qc=20, sigma_vo_eff=20, k0=0.8, fail_silently=False)
```

### Disabling validation - NOT RECOMMENDED

```groundhog``` allows you to disable all validation but this is not recommended. To disable all validation, just include the keyword argument ```validate=False```.

When entering this, no validation is performed whatsoever and physically meaningless entries (such as negative diameters are possible).

Needless to say that this should only be used in very exceptional cases.

```python
relativedensity_sand_jamiolkowski(qc=20, sigma_vo_eff=-20, k0=0.8, validate=False)
```

## Testing

Each ```groundhog``` function has one or more unit tests written for it during development. A common unit test is to perform a hand-calc for a certain combination of input parameters and assert that the calculated value from the function is equal to the result of the hand-calc.

The unit tests are hardcoded in the ```groundhog``` source code and reperformed for any release. So there will never be a function in ```groundhog``` which does not meet its unit tests and this already reduces the margin for error considerably.

Nevertheless, we cannot test all possible combinations of input parameters so if you do find an error, please report it asap. A new unit test will then be developed to prevent this error from occuring in the future.

## International collaboration

Currently, several geotechnical researchers and professionals are already using Python in their daily practice. ```groundhog``` aims to bring together different initiatives and provide a multi-purpose toolset for the geotechnical engineer.

The growth of ```groundhog``` will be the result of collaborative development. If you have functions which you regularly use, they can be included in ```groundhog```. You can contact the developers of the package, even if you have code in another language which you would like to be transformed into Python code for ```groundhog```.
