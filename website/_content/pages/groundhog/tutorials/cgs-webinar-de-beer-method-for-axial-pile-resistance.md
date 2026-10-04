---
title: CGS webinar - De Beer method for axial pile resistance
slug: groundhog/tutorials/cgs-webinar-de-beer-method-for-axial-pile-resistance
section: Groundhog Guides
description: CGS webinar - De Beer method for unit base resistance This notebook presents the workflow for calculating unit base resistance according to De Beer's method, which is the method in the Belgian National Annex of Eurocode…
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/v0.15.0/notebooks/CGS%20webinar%20-%20De%20Beer%20method%20for%20axial%20pile%20resistance.ipynb
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.15.0
edited_by_geocore: true
geocore_edit_note: 'Converted from a Jupyter notebook: Markdown cells kept, code cells shown as code, text and image outputs reproduced, interactive Plotly/HTML outputs omitted, with a short note on how to run this in GeoCore prepended.'
notebook: notebooks/CGS webinar - De Beer method for axial pile resistance.ipynb
---

> **Adapted from groundhog's own documentation.** Inside GeoCore, run the same calculation through a [calculation form](/docs/geocore/using/modules) or by asking **GeoAI**, which calls the same groundhog function through its validated Tool Registry. This notebook is kept for anyone who wants to call groundhog directly from their own Python code instead.

# CGS webinar - De Beer method for unit base resistance

This notebook presents the workflow for calculating unit base resistance according to De Beer's method, which is the method in the Belgian National Annex of Eurocode 7. Calculating unit base resistance from penetrometer results is also described in the Canadian Foundation Engineering Manual using the method by Bustamante and Gianselli (1982).

This notebook shows how ```groundhog``` greatly simplifies the fairly complex unit base resistance algorithm by De Beer, allowing students to focus on the interpretation of results and sensitivity studies.

The CPT information used in this tutorial is from [Databank Ondergrond Vlaanderen](https://dov.vlaanderen.be/).

## Loading libraries

For the processing of CPT data, we will need the ```DeBeerCalculation``` class from ```groundhog```. This class encodes all required functionality to perform unit base resistance calculations. We can import it as follows:

```python
from groundhog.deepfoundations.axialcapacity.debeer import DeBeerCalculation
```

We will also import the ```PCPTProcessing``` and ```SoilProfile``` objects.

```python
from groundhog.siteinvestigation.insitutests.pcpt_processing import PCPTProcessing
from groundhog.general.soilprofile import SoilProfile
```

## Data loading

We will calculate unit base resistance based on an example PCPT from the Ghent area (Belgium). This CPT is given in Excel format.

```groundhog``` allows import of CPT data from many different sources, of which Excel is one of the most straightforward.

```python
cpt = PCPTProcessing(title="CPT")
cpt.load_excel("Data/Koppejan_DeBeer_demo.xlsx")
```

We can inspect the data numerically. This shows that only cone resistance was measured. This is because many CPT investigations in Belgium are still carried out with the M1 mechanical cone.

```python
cpt.data.head()
```

We can visualise the data using the ```plot_raw_pcpt``` method and customise the $ q_c $ axis.

```python
cpt.plot_raw_pcpt(qc_range=(0,20), qc_tick=2)
```

## Unit end bearing

### Unit end bearing algorithm

The unit end bearing is calculated by processing the CPT trace using the De Beer end bearing calculation encoded in the Python package ```groundhog```.

De Beer's method accounts for scaling from a CPT to a pile in a rigorous manner. The CPT is treated as a model pile and the following effects are corrected for:

   - The pile "feels" the presence of the free surface up to deeper depths
   - The stress level on the failure surface induced by the pile is higher than on that for the CPT
   - The pile "feels" the effects of stronger and weaker layers before the CPT does

We can run the calculation and derive the value of unit end bearing $ q_{DeBeer} $ at a selected depth.

The full algorithm is described in the ```groundhog``` documentation and applies the following algorithm:

$$ \text{Step 1 - Surface correction:  } q_{p,(1)} = \frac{q_c}{\exp \left( 2 \cdot ( \beta_c - \beta_p ) \cdot \tan \varphi \right) } \\ \text{Step 2 - Stress level correction:  }  A = \frac{1 + \frac{\gamma \cdot h_{crit}^{\prime}}{2 \cdot p_o}}{1 + \frac{\gamma \cdot h_{crit}}{2 \cdot p_o}},  \text{ if } A \cdot q_{p,(1)} > q_c  \implies A \cdot q_{p,(1)} = q_c \\ \text{Step 3 - Downward correction:  } q_{p,j+1} = q_{p,j} + \left[ A \cdot q_{p,(1),j+1} - q_{p,j} \right] \cdot \frac{d}{D}
 , \text{ if } q_{p,j+1} > q_{p,(1),j+1} \implies q_{p,j+1} = q_{p,(1),j+1} \\ \text{Step 4 - Upward correction:  } q_{p,q+1} = q_{p,q} + \left[ (q_{p,j+1})_{q+1} - q_{p,q} \right] \cdot \frac{d}{D},  \text{ if } q_{p,q+1} > (q_{p,j+1})_{q+1} \implies q_{p,q+1} = (q_{p,j+1})_{q+1} $$
 
This is a complex and iterative algorithm which is clearly beyond the scope of basic geotechnical courses. However, the sound physical principles reflected in this algorithm deserve use in courses.

This is why ```groundhog``` implements this algorithm. The students only need to supply the cone resistance trace and the diameter of the pile.

### Calculation initialisation

As an example, we can set up this calculation for a 0.4m outer diameter pile. We can create a ```DeBeerCalculation``` object by telling it where to find depth data (```depth``` argument) and cone tip resistance data (```qc``` argument). We then specify the pile diameter (```diameter_pile``` argument). This diameter is required for the averaging procedure.

```python
debeer_cpt = DeBeerCalculation(
    depth=cpt.data["z [m]"],
    qc=cpt.data["qc [MPa]"],
    diameter_pile=0.8)
```

### Resampling

At this point, the algorithm has not been executed yet. We still need to perform two additional steps. The first is to resample the data to a 0.2m grid. This is because De Beer's method was based on mechanical cone penetration tests which have a push of 20cm.

We can simply carry out this resampling using the ```resample_data``` method.

```python
debeer_cpt.resample_data(spacing=0.2)
```

### Soil profile specification

De Beer's algorithm also needs a basic definition of the layering. Although this is not strictly required for the unit base resistance calculation, this is included in the workflow at an early stage. This is because the overburden calculation is also performed when the soil profile is set using the ```set_soil_layers``` method. The water table level can also be set in this step.

```python
soilprofile = SoilProfile({
    "Depth from [m]": [0, 2, 8.5],
    "Depth to [m]": [2, 8.5, 14],
    'Soil type': ['Sand', 'Clay', 'Sand']
})
debeer_cpt.set_soil_layers(soilprofile, water_level=0)
```

We can inspect the attributes ```layering``` and ```calculation_data``` of the ```DeBeerCalculation``` object after the mapping of the soil profile.

```python
debeer_cpt.layering
```

### Unit end bearing calculation

Everything is now ready for the unit end bearing calculation which is executed by calling the method ```calculate_base_resistance```.

```python
debeer_cpt.calculate_base_resistance()
```

We can inspect the calculation details which are included in the ```calc_1``` attribute.

```python
debeer_cpt.calc_1.head()
```

Visualising the results is more instructive. The method ```plot_base_resistance``` visualizes the unit base resistance. The averaging effect is clearly visible and the point with highest unit end bearing $ q_b $ can be identified from the plot.

```python
debeer_cpt.plot_base_resistance()
```

The workflow above allows students to explore the influence of the settings of De Beer's method on the calculated unit end bearing $ q_b $. This allows sensitivity studies. The results can also be carried further into a full axial pile resistance calculation according to Eurocode 7.

<img src="/docs/assets/groundhog/notebooks/Images/groundhog_banner_wide.png">
