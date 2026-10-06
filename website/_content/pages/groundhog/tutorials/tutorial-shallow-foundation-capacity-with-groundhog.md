---
title: Tutorial - Shallow foundation capacity with groundhog
slug: groundhog/tutorials/tutorial-shallow-foundation-capacity-with-groundhog
section: Groundhog Guides
description: The analysis of shallow foundation is a recurring task for geotechnical engineers.
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/dc7d554c6b8986bae30f518304546a911b1ca5ab/notebooks/Tutorial%20-%20Shallow%20foundation%20capacity%20with%20groundhog.ipynb
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.16.0
edited_by_geocore: true
geocore_edit_note: 'Converted from a Jupyter notebook: Markdown cells kept, code cells shown as code, text and image outputs reproduced, interactive Plotly/HTML outputs omitted, with a short note on how to run this in GeoCore prepended.'
notebook: notebooks/Tutorial - Shallow foundation capacity with groundhog.ipynb
---

> **Adapted from groundhog's own documentation.** Inside GeoCore, run the same calculation through a [calculation form](/docs/geocore/using/modules) or by asking **GeoAI**, which calls the same groundhog function through its validated Tool Registry. This notebook is kept for anyone who wants to call groundhog directly from their own Python code instead.

The analysis of shallow foundation is a recurring task for geotechnical engineers. While the problem at hand is rather simple (estimating the ultimate capacity of a foundation on soil) the governing equations contain several factors to account for foundation shape, depth, inclination and load inclination. Moreover, the interaction between horizontal and vertical load adds some complexity to the problem, especially for eccentrically loaded footings.

``groundhog`` contains a robust implementation of the bearing capacity equations and allows for rapid sensitivity analysis of VH capacity for shallow foundations. The code was developed based on the implementation in the API RP2 GEO standard which is aimed at offshore shallow foundations.

``groundhog`` has classes for drained and undrained analysis of shallow foundations (``ShallowFoundationCapacityDrained`` and ``ShallowFoundationCapacityUndrained`` respectively) which allows a rapid an efficient definition of a shallow foundation analysis.

We can import these classes:

```python
from groundhog.shallowfoundations.capacity import ShallowFoundationCapacityDrained, ShallowFoundationCapacityUndrained
```

In this tutorial, we will explore the capabilities of ``groundhog``. First, the VH envelope for centrically loaded foundations at the surface will be developed for drained and undrained conditions. Subsequently, an eccentrically loaded foundation will be analysed.

We can also set the style of Plotly to have a white background.

```python
import plotly.io as pio
from plotly.offline import init_notebook_mode
init_notebook_mode()
pio.templates.default = 'plotly_white'
```

## Centrically loaded foundation

When loads are applied to the center of the foundation, the maximum vertical bearing capacity can be mobilised. Any eccentricity will reduce the effective area of the foundation and this the available bearing capacity.

Here, we will analyse a mudmat of 8m long and 5m wide (typical dimensions for pipeline end terminations in deepwater).

```python
LENGTH = 8 # m
WIDTH = 5 # m
```

### Undrained conditions

Undrained soil behaviour occurs when excess pore water pressures generated during loading cannot dissipate fast enough. This will apply for short-term loading on most clays but also for rapid loading on sands with significant fines content. The rate of loading needs to be assessed in relation to the permeability of the soil to assess where a drained or undrained calculation should be performed.

#### Setting up the analysis

We can create a ``ShallowFoundationCapacityUndrained`` to define the analysis. We can give a title to the analysis.

```python
undrained_centric = ShallowFoundationCapacityUndrained(title="Undrained capacity for centric loading")
```

#### Specifying foundation dimensions

The foundation dimensions are easily specified using the ```set_geometry``` method. The default geometrical parameter are for rectangles but ``groundhog`` also encodes bearing capacity calculations for circular foundations.

The ``set_geometry`` method calculates the foundation area.

```python
undrained_centric.set_geometry(length=LENGTH, width=WIDTH)
undrained_centric.full_area
```

#### Specifying soil parameters

For undrained conditions, total stress analysis is performed and the undrained shear strength of the soil is the governing strength parameter. ``groundhog`` implements bearing capacity equations for both constant and linearly increasing shear strength profiles with depth.

Here, we will analyse a soil with a constant undrained shear strength $ S_u $ = 10kPa. We also need to specify the total unit weight $ \gamma $ of the soil. This is only used when the foundation is embedded. We will specify a total unit weight of 16kN/m$^3$.

For embedded foundations (e.g. skirted mudmats), the average undrained shear strength above the base can also be specified.

```python
undrained_centric.set_soilparameters_undrained(unit_weight=16, su_base=10, su_increase=0)
```

#### Specifying load eccentricity

The eccentricity of the load can be specified by measuring the offset between the center of the foundation and the load application point along the length and width axis. Here, we are analysing a centrically loaded foundation, so both eccentricities are zero.

```python
undrained_centric.set_eccentricity(eccentricity_width=0, eccentricity_length=0)
```

#### Undrained vertical bearing capacity

The ultimate net bearing pressure is given by the following equation:

$$ q_u = N_c \cdot S_u \cdot K_c $$

The factor $ K_c $ combines the different bearing capacity factors. For this analysis case, only the shape factor is non-zero. The formula for the shape factor is as follows:

$$ s_c = 0.18 \cdot (1 - 2 \cdot i_c) \cdot (B^{\prime} / L^{\prime}) $$ 

with the inclination factor $ i_c $ being zero. So for this case, $ K_c $ is given by:

$$ K_c = 1 + s_c = 1 + 0.18 \cdot (B^{\prime} / L^{\prime}) $$

```python
5.14 * 10 * (1 + 0.18 * 5 / 8)
```

The ultimate net bearing pressure $ q_u $ calculated with ``groundhog`` gives the exact same result. This hand-calc check is also included in the unit test suite for ``groundhog``.

```python
undrained_centric.calculate_bearing_capacity()
undrained_centric.net_bearing_pressure
```

We can also print the full output for the capacity analysis:

```python
undrained_centric.capacity
```

#### Ultimate sliding capacity

The ultimate sliding capacity is obtained by simply multiplying the undrained shear strength at the base of the foundation by the base area. The attribute ```sliding_full``` gives the full sliding capacity (base resistance + possible contribution from embedded area of the foundation). In this case, the contribution from the embedded area is zero.

```python
undrained_centric.calculate_sliding_capacity()
undrained_centric.sliding_full
```

#### Bearing capacity envelope

The interaction between vertical and horizontal load is described through a capacity envelope. The area inside this envelope shows the load combinations which can be carried by the foundation.

Safety factors are also applied to the envelope. By default, a safety factor of 2 is used for bearing and 1.5 for sliding. This means that all vertical loads are divided by 2 and all horizontal loads by 1.5 resulting in a factored envelope.

```python
undrained_centric.calculate_envelope()
```

The envelope can be plotted using the ```plot_envelope``` method.

```python
undrained_centric_plot = undrained_centric.plot_envelope()
```

### Drained conditions

Drained soil behaviour occurs when excess pore water pressures generated during loading can dissipate fast enough. This will apply for long-term loading. The rate of loading needs again to be assessed in relation to the permeability of the soil to assess where a drained or undrained calculation should be performed.

#### Analysis setup

This is done by creating an object from the ```ShallowFoundationCapacityDrained``` class.

```python
drained_centric = ShallowFoundationCapacityDrained(title="Drained capacity for centric loading")
```

#### Geometry

The same geometry is used:

```python
drained_centric.set_geometry(length=LENGTH, width=WIDTH)
drained_centric.full_area
```

#### Soil parameters

For drained analysis, we need to specify the effective unit weight, the effective friction angle of the soil beneath the base and the effective stress at base level. Here, we will model a surface foundation so this effective stress is zero.

```python
drained_centric.set_soilparameters_drained(effective_unit_weight=9, friction_angle=38, effective_stress_base=0)
```

#### Specifying load eccentricity

The eccentricity of the load can be specified as for the undrained case.

```python
drained_centric.set_eccentricity(eccentricity_length=0, eccentricity_width=0)
```

#### Drained vertical bearing capacity

The ultimate net bearing pressure is given by the following equation:

$$ q_u = \left [ p_o^{\prime} (N_q - 1) K_q + 0.5 \gamma^{\prime} B^{\prime} N_{\gamma} K_{\gamma} \right ] $$

For a surface foundation, $ p_o^{\prime} $ is zero and only the second term is evaluated.

The factors $ K_q $ and $ K_{\gamma} $ combine the different bearing capacity factors. For this analysis case, only the shape factor is non-zero. The formula for the shape factor is as follows:

$$ s_{\gamma} = 1 - \left( 0.4 \cdot i_{\gamma} \cdot (B^{\prime} / L^{\prime}) \right) $$ 

with the inclination factor $ i_{\gamma} $ being zero. So for this case, $ K_{\gamma} $ is given by:

$$ K_{\gamma} = s_{\gamma} $$

```python
0.5 * 9 * 5 * 56.17 * (1 - 0.4 * (5 / 8))
```

The ultimate net bearing pressure $ q_u $ calculated with ``groundhog`` gives almost the same result. The difference is due to the number of digits in the calculation of $ N_{\gamma} $. This hand-calc check is also included in the unit test suite for ``groundhog``.

```python
drained_centric.calculate_bearing_capacity()
drained_centric.net_bearing_pressure
```

The full output of the capacity calculation can be printed.

```python
drained_centric.capacity
```

#### Ultimate sliding capacity

The ultimate sliding capacity is dependent on the vertical load on the foundation. Therefore, this vertical load is specified. The base resistance is then obtained as the multiplication of this load with the tangent of the interface friction angle. If the interface friction angle is not specified, 5° is subtracted from the soil effective friction angle.

The attribute ```sliding_full``` gives the full sliding capacity (base resistance + possible contribution from embedded area of the foundation). In this case, the contribution from the embedded area is zero.

```python
import numpy as np
1000 * np.tan(np.radians(38 - 5))
```

This corresponds exactly with the ```groundhog``` solution.

```python
drained_centric.calculate_sliding_capacity(vertical_load=1000)
drained_centric.sliding_full
```

#### Bearing capacity envelope

The interaction between vertical and horizontal load is described through a capacity envelope. The area inside this envelope shows the load combinations which can be carried by the foundation.

Safety factors are also applied to the envelope. By default, a safety factor of 2 is used for bearing and 1.5 for sliding. This means that all vertical loads are divided by 2 and all horizontal loads by 1.5 resulting in a factored envelope.

Note that the failure envelope has a different shape to the undrained envelope. A sliding cut-off is also included.

```python
drained_centric.calculate_envelope()
```

The envelope is plotted with the ```plot_envelope``` method.

```python
drained_centric_plot = drained_centric.plot_envelope()
```

## Eccentrically loaded foundation

When a foundation is loaded eccentrically (e.g. due to moment loading of non-symmetric weight distribution), the failure envelope will shrink and the effective area needs to be taken into account.

By specifying eccentricity along the lenght and width axes, ```groundhog``` can calculate the effective bearing area and take into account these eccentric loads to calculate the resulting bearing capacity envelope. 

We can repeat the undrained and drained example for a load which is applied 1m from the center in the length direction and 0.5m from the center in the width direction.

### Undrained conditions

The analysis is reperformed using the same inputs except for the eccentricity.

The effective area is calculated as:

$$ A^{\prime} = L^{\prime} \cdot B^{\prime} = (L - 2 \cdot e_L) \cdot (B - 2 \cdot e_B) $$

```python
undrained_eccentric = ShallowFoundationCapacityUndrained(title="Undrained capacity for eccentric loading")
undrained_eccentric.set_geometry(length=LENGTH, width=WIDTH)
undrained_eccentric.set_soilparameters_undrained(unit_weight=16, su_base=10, su_increase=0)
undrained_eccentric.set_eccentricity(eccentricity_width=0.5, eccentricity_length=1)
undrained_eccentric.effective_area
```

We can see that the effective area is indeed correctly calculated.

```python
undrained_eccentric.calculate_envelope()
undrained_eccentric_plot = undrained_eccentric.plot_envelope(show_uncorrected=True)
```

The maximum vertical bearing capacity is now significantly lower then for the centric case.

We can also see that the envelope now has a horizontal portion. This is because the effective area is used for the vertical capacity calculation, while the full base area is used for the sliding capacity. Indeed, due to this horizontal capacity from the area outside the effective area, the full vertical capacity will be available until a certain horizontal load is achieved.

### Drained conditions

The analysis is reperformed using the same inputs except for the eccentricity.

```python
drained_eccentric = ShallowFoundationCapacityDrained(title="Drained capacity for eccentric loading")
drained_eccentric.set_geometry(length=LENGTH, width=WIDTH)
drained_eccentric.set_soilparameters_drained(effective_unit_weight=9, friction_angle=38, effective_stress_base=0)
drained_eccentric.set_eccentricity(eccentricity_length=1, eccentricity_width=0.5)
drained_eccentric.calculate_envelope()
drained_eccentric_plot = drained_eccentric.plot_envelope()
```

```python
import plotly.io as pio
pio.write_image(drained_eccentric_plot, 'Images/drained_envelope_2.png', scale=5)
```

The envelopes again show a significantly lower bearing capacity due to the eccentric loading. The fact that there is sliding capacity available outside the effective area again results in a horizontal portion of the envelope for the maximum vertical capacity.

## Skirted foundation

```groundhog``` can also calculate the capacity envelope for skirted or base-embedded foundations.

### Undrained capacity

The calculation for a surface foundation will be modified as follows:

   - A depth factor is added the the vertical bearing capacity calculation
   - For non-skirted, base embedded foundations a contribution from the total vertical stress at base level is taken into account
   - For sliding resistance, the passive resistance on the embedded area of the skirt is taken into account
   - The additional load eccentricity due to the embedment is taken into account.
   
We can specify this analysis and calculate the bearing capacity envelope.

```python
undrained_embedded = ShallowFoundationCapacityUndrained(title="Undrained capacity for embedded foundation")
undrained_embedded.set_geometry(length=LENGTH, width=WIDTH, depth=1, skirted=True)
undrained_embedded.set_soilparameters_undrained(unit_weight=16, su_base=10, su_increase=0)
undrained_embedded.set_eccentricity(eccentricity_width=0, eccentricity_length=0)
undrained_embedded.calculate_sliding_capacity()
undrained_embedded.sliding
```

The sliding calculation shows the additional contribution from passive resistance on the skirts.

For the load inclination, the contribution from horizontal skirt resistance and base resistance outside the effective area are subtracted. Because of this, additional horizontal resistance is available for high vertical load levels compared to the surface footing case.

```python
undrained_embedded.calculate_envelope()
undrained_embedded_plot = undrained_embedded.plot_envelope(
    plot_title="Undrained bearing capacity envelope for skirted foundation")
```

### Drained capacity

The drained capacity is modified by the following aspects:

   - Non-zero vertical effective stress at base level $ p_o^{\prime} $ results in non-zero $ N_q $ term
   - A depth factor is applied in the vertical capacity calculation
   - Passive resistance on the embedded skirt area is taken into account for the sliding resistance
   
We can specify this analysis and calculate the bearing capacity envelope.

```python
drained_embedded = ShallowFoundationCapacityDrained(title="Drained capacity for embedded foundation")
drained_embedded.set_geometry(length=LENGTH, width=WIDTH, depth=1, skirted=True)
drained_embedded.set_soilparameters_drained(effective_unit_weight=9, friction_angle=38, effective_stress_base=9)
drained_embedded.set_eccentricity(eccentricity_width=0, eccentricity_length=0)
drained_embedded.calculate_sliding_capacity(vertical_load=1000)
drained_embedded.sliding
```

The sliding calculation shows the additional contribution from the passive resistance on the skirts.

Calculating and plotting the drained bearing capacity envelope shows the additional vertical resistance due to the increased stresses at base level and the additional horizontal resistance due to the passive resistance on the skirts.

```python
drained_embedded.calculate_envelope()
drained_embedded_plot = drained_embedded.plot_envelope(
    plot_title="Drained bearing capacity envelope for skirted foundation")
```
