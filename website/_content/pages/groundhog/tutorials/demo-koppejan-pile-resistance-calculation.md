---
title: Demo - Koppejan's pile resistance calculation method
slug: groundhog/tutorials/demo-koppejan-pile-resistance-calculation
section: Groundhog Guides
description: A tutorial for the application of the Koppejan method is given in this notebook.
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/v0.15.0/notebooks/Demo%20-%20Koppejan%20pile%20resistance%20calculation.ipynb
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.15.0
edited_by_geocore: true
geocore_edit_note: 'Converted from a Jupyter notebook: Markdown cells kept, code cells shown as code, text and image outputs reproduced, interactive Plotly/HTML outputs omitted.'
notebook: notebooks/Demo - Koppejan pile resistance calculation.ipynb
---

A tutorial for the application of the Koppejan method is given in this notebook. This notebook can be used to apply to other CPT profiles and possibly make modifications to gain further insight in the data and solutions.

## Loading Python libraries

This notebook makes use of the ```groundhog``` Python library to load and manipulate data, visualise data and execute geotechnical calculations. The installation of these libraries is described in the [groundhog installation guide](http://snakesonabrain.com/docs/groundhog/gettingstarted.html).

```python
# Import of standard libraries for data manipulation
import numpy as np
import os
from IPython.display import HTML
import pandas as pd
```

```python
# Import of plotting libraries
from plotly import tools
import plotly.graph_objs as go
import plotly.io as pio
import plotly.figure_factory as ff
from plotly.colors import DEFAULT_PLOTLY_COLORS
from plotly.offline import init_notebook_mode
init_notebook_mode()
```

```python
# Import of geotechnical libraries
from groundhog.siteinvestigation.insitutests.pcpt_processing import PCPTProcessing
from groundhog.general.soilprofile import SoilProfile
```

### 1. CPT data loading

The CPT data can be loaded from the Excel file ```Koppejan_DeBeer_demo.xlsx```. A ```PCPTProcessing``` object can be created. The data has no sleeve friction and pore pressure data but can be plotted nonetheless. The data suggests sandy material until 2m followed by a clay layer. Underneath this clay layer, another sand layer can be found which provides more pile capacity.

```python
cpt = PCPTProcessing(title='Koppejan CPT')
cpt.load_excel("Data/Koppejan_DeBeer_demo.xlsx")
cpt.plot_raw_pcpt(qc_range=(0, 20))
```

### 2. Pile resistance calculation

The Koppejan method uses the cone tip resistance $ q_c $ to derive shaft resistance $ F_{r,s} $ and base resistance $ F_{r,b} $. The Python package ```groundhog``` implements a ```KoppejanCalculation``` class which contains the necessary methods.

```python
from groundhog.deepfoundations.axialcapacity.koppejan import KoppejanCalculation
```

### 2.1. Shaft resistance

The shaft resistance calculation modifies the cone resistance to account for the effect of the installation method. The factor $ \alpha_s $ is highest for driven closed ended piles and lower for the other pile types. Figure 2 shows the values for the different pile types.

<br><center><b>Figure 2: $ \alpha_s $ and $ \alpha_p $ according to Koppejan</b></center>
<img src="/docs/assets/groundhog/notebooks/Images/koppejan_alphas.png" width=600>

The maximum cone resistance to be used depends on the layer thickness, for layers less than 1m thick, $ q_{c,lim} = 12 \text{MPa} $ is taken. If the layer thickness is greater than 1m $ q_{c,lim} = 15 \text{MPa} $ is used.

In the profile given above, there are no layers of less than 1m thickness so $ q_{c,lim} = 15 \text{MPa} $ is used.

The maximum shaft friction is then given by the following formula:

$$ \tau_{s,max} = \alpha_s \cdot \min(q_c, q_{c,lim})  $$

Note that $ \tau_{s,max} $ is given in kPa so a conversion factor from MPa to kPa is required.

The shaft resistance is then obtained by integrating the maximum shaft friction over the pile length and the outer shaft perimeter:

$$ F_{r,s} = \int_{0}^{L} dT = \int_{0}^{L} \tau_{s,max}(z) \cdot \pi \cdot D \cdot dz $$

This equation can easily be discretised to numerical calculation of the shaft resistance. 

In our example, a closed ended tubular pile with a diameter of 0.4m is driven into the soil to a depth of 12m. 

First, we will create a ```KoppejanCalculation``` object which loads the CPT data and the pile properties:

```python
koppejanpile = KoppejanCalculation(
    depth=cpt.data['z [m]'],
    qc=cpt.data['qc [MPa]'],
    diameter=0.4,
    penetration=12)
```

We also need to provide a layering to the calculation. The layering is specified as a Pandas dataframe:

```python
layering = pd.DataFrame({
    'z from [m]': [0, 2, 8.5],
    'z to [m]': [2, 8.5, 14],
    'Total unit weight [kN/m3]': [20, 17, 20]
})
```

We can assign the layering to our calculation:

```python
koppejanpile.set_layer_properties(layering)
```

The method ```calculate_side_friction``` performs the side friction calculation described above. The factor $ \alpha_s $ needs to be read from the table. For a driven, closed-ended tubular pile, $ \alpha_s $ = 0.01.

```python
koppejanpile.calculate_side_friction(alpha_s=0.01)
```

The results of this shaft resistance calculation can be plotted. The plot shows the selected cone tip resistance for the calculation, the calculated unit shaft friction, the shaft friction increments (unit shaft resistance integrated over the pile circumference) and the cumulative shaft resistance with depth.

The calculated shaft resistance $ F_{rs} $ is plotted as a red dot.

```python
koppejanpile.plot_shaft_resistance()
```

```python
HTML("""
The calculated shaft resistance for the pile penetration of %.1fm is $ F_{r,s} = $ %.0fkN.
""" % (koppejanpile.penetration, koppejanpile.Frs))
```

### 2.2. Base resistance

#### 2.2.1. Cone resistance averaging

The base resistance is slightly more complex because the pile has a larger diameter than the CPT rod. It therefore mobilises soil resistance in a larger zone. The sketch in Figure 4 shows that the zone in which resistance is mobilised according to Koppejan extends up to 8 diameters above the pile tip and 0.7 to 4 diameters below the pile tip.

<br><center><b>Figure 4: Zone of influence of pile base</b></center>
<img src="/docs/assets/groundhog/notebooks/Images/koppejan_base_theory.png" width=400>

The tip resistance of the pile is derived by averaging the tip resistance $ q_c $ of the CPT in certain averaging windows above and below the pile.

$$ q_{c,avg} = \frac{0.5 \cdot (q_{cI} + q_{cII}) + q_{cIII}}{2} $$

The different parts of this formula are developed below. The ```KoppejanCalculation``` class implements a method ```calculate_base_resistance``` to calculate this construction for any given CPT trace. We again need to select a factor to account to the pile type and installation method ($ \alpha_p $) according to Koppejan's table.

```python
koppejanpile.calculate_base_resistance(alpha_p=1)
```

##### 2.2.1.1 $ q_{cII} $

$ q_{cII} $ is obtained by taking the average cone resistance in a window varying from $ 0.7D $ to $ 4D $. The size of this window is chosen such that $ q_{cII} $ is minimized. The reason for varying the maximum depth of this window is that weaker layers up to a certain depth below the pile tip will have an influence on the pile resistance. A weaker layer at a certain depth below the pile tip will lead to a lower value for $ q_{cII} $ as the averaging window expands.

The method ```calculate_base_resistance``` simply selects all data in an averaging window, with the size of the averaging window varying between $ 0.7D $  and $ 4D $, calculates the average and then determines the minimum for all window sizes.

```python
HTML("""
The value of $ q_{cII} $ is %.2fMPa corresponding to a depth below the tip of %.1f $ D $ .""" % (
    koppejanpile.qcII, (koppejanpile.qcIIz - koppejanpile.penetration) / koppejanpile.diameter))
```

These averages can be plotted. We can see the influence of the slightly weaker layer below our tip on the value of $ q_{cII} $. It is not surprising that the averaging window is 4$ D $ in this case.

##### 2.2.1.2. $ q_{cI} $

The value of $ q_{c,I} $ is obtained by taking the average along the same path as $ q_{c,II} $ but the cone resistance can never increase as one moves up from the cone resistance at the bottom of the averaging window.

The method ```calculate_base_resistance``` loops over the different cone resistance values from bottom to top and check if the cone resistance increases. If it does, we set the value used for averaging to the previous value.

This can be illustrated in the plot but first the construction for $ q_{cIII} $ is explained.

```python
HTML("""
$ q_{c,I} $ = %.2fMPa""" % (koppejanpile.qcI))
```

##### 2.2.1.3. $ q_{cIII} $

$ q_{cIII} $ accounts for the averaging effect in the soil above the pile tip. The averaging window ranges from the pile tip to $ 8D $ above the pile tip.

Similar to $ q_{cI} $, the cone resistance should never increase as one moves up through the averaging window.

```calculate_base_resistance``` again runs through the different cone resistace values from the bottom up and ensures that the values used for the averaging do not increase. Note that we do not start from the cone resistance at tip depth but rather from the value of $ q_{cI} $ at tip depth.

```python
HTML("""
$ q_{c,III} $ = %.2fMPa""" % (koppejanpile.qcIII))
```

We can plot the final construction to illustrate this:

```python
koppejanpile.plot_baseconstruction()
```

#### 2.2.2. Effect of increased base dimensions

The execution method of the pile determines the base dimension. Depending on how the drilling or driving was done, an increased base length and area can be used. Figure 8 shows the geometric properties which can be used in the lookup chart in Figure 9 to determine the coefficient $ \beta $.

<br><center><b>Figure 8: Pile base dimensions</b></center>
<img src="/docs/assets/groundhog/notebooks/Images/base_increase.png" width=400>

<br><center><b>Figure 9: Coefficient for pile base dimension</b></center>
<img src="/docs/assets/groundhog/notebooks/Images/base_coefficient.png" width=400>

If the pile does not have an enlarged shape, then the coeffient $ \beta $ is equal to 1.

####  2.2.3. Effect of non-circular pile cross-section

If the pile has a non-circular cross-section, a correction needs to be made for this. The coefficient $ s $ can be determined from Figure 10 where the ratio $ b/a $ is the ratio of the longest dimension to the shortest dimension of the pile cross-section.

<br><center><b>Figure 10: Coefficient for pile base cross-section</b></center>
<img src="/docs/assets/groundhog/notebooks/Images/crosssection_coefficient.png" width=400>

If the pile has a circular shape, then the coeffient $ s $ is equal to 1.

If the pile is non-uniform along its length or has a non-uniform circumference, we can use the optional arguments ```base_coefficient``` and ```crosssection_coefficient``` of the method ```calculate_base_resistance```. These are equal=1 by default.

#### 2.2.4. Base resistance

The unit end bearing base resistance is then determined using the following formulae:

$$ q_{c,avg} = \frac{0.5 \cdot (q_{cI} + q_{cII}) + q_{cIII}}{2} $$

$$ q_{b,max} = \alpha_p \cdot \beta \cdot s \cdot q_{c,avg} \leq 15 \text{MPa} $$

The value of $ \alpha_p $ can be read from the chart in Figure 2.

For the driven pile in the example, $ \alpha_p $, $ \beta $ and $ s $ are all equal to 1.

```python
HTML("""
$ q_{c,avg} = $ %.1f MPa""" % (koppejanpile.qcavg))
```

```python
HTML("""
$ q_{b,max} = $ %.1f MPa""" % (koppejanpile.qbmax))
```

The base resistance is obtained by multiplying the maximum unit end bearing by the tip area. Note that coring tubular piles can also be calculated by setting the argument ```coring=True``` and specifying a ```wall_thickness``` in mm for the ```calculate_base_resistance``` calculation.

In this example, we have a closed-ended pile, so we don't need to change anything.

```python
HTML("""
$ F_{rb} = $ %.0f kN""" % (koppejanpile.Frb))
```
