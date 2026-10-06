---
title: Soilmix
slug: groundhog/api/excavations/soilmix
section: Groundhog API Reference
description: 'API reference for groundhog.excavations.soilmix: 2 functions, 0 classes.'
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/dc7d554c6b8986bae30f518304546a911b1ca5ab/groundhog/excavations/soilmix.py
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.16.0
edited_by_geocore: true
geocore_edit_note: Generated from the docstrings of the installed groundhog package; RST converted to Markdown and parameter/return tables derived from the docstrings.
module: groundhog.excavations.soilmix
upstream_docs_urls:
- https://groundhog.readthedocs.io/en/main/excavations/soilmix.html
geocore_available: true
geocore_functions:
- bendingstiffness_soilmix_method1
- bendingstiffness_soilmix_method2
---

Module `groundhog.excavations.soilmix` (groundhog 0.16.0). [View source](https://github.com/snakesonabrain/groundhog/blob/dc7d554c6b8986bae30f518304546a911b1ca5ab/groundhog/excavations/soilmix.py).

Upstream documentation: [Soilmix](https://groundhog.readthedocs.io/en/main/excavations/soilmix.html).

**Functions:** [`bendingstiffness_soilmix_method1`](#bendingstiffness_soilmix_method1), [`bendingstiffness_soilmix_method2`](#bendingstiffness_soilmix_method2)

<a id="bendingstiffness_soilmix_method1"></a>

## `bendingstiffness_soilmix_method1`

<span class="gc-badge gc-available" data-geocore-function="bendingstiffness_soilmix_method1">Available in GeoCore</span> [Excavations › Soilmix › Bending Stiffness (Method 1)](/docs/geocore/using/modules#bendingstiffness_soilmix_method1)

```python
bendingstiffness_soilmix_method1(
    moment_inertia_reinforcement,
    modulus_soilmix,
    height_soilmix,
    reinforcement_offset,
    height_reinforcement,
    flange_thickness,
    connection_thickness,
    flange_width,
    modulus_reinforcement=210000000.0,
    participating_width=nan,
    tensile_strength_soilmix=nan,
    **kwargs,
)
```

Calculates the bending stiffness of a soilmix wall (for use in geotechnical retaining wall calculations) using the combined stiffness of reinforcements and the soilmix material itself. The stiffness is calculated as the average of the cracked and uncracked stiffness of the material according to §5.4.2.3 if EN 1992-1-1. The formulae contain simplications that result in a small error of 1 to 3%. Note that all dimensions are in meters and units of force are in kN.

$$
EI\text{-eff} = \frac{EI\text{-1} + EI\text{-2}}{2}
$$

$$
EI\text{-1}=E_a I_a + E_{sm}(I_{sm} - I_a)=E_{sm} \left[ (n-1) I_a + I_{sm}\right] \quad \text{where } n=E_a/E_{sm}
$$

$$
I_{sm} = \frac{b_{cl} h_{sm}^3}{12}
$$

$$
c_1=c_2=\frac{h_{sm}-h_a}{2}
$$

$$
d=h_{eq}-c_2-\frac{t_f}{2} \quad{where } h_{eq} \text{ can be taken as } h_{sm}
$$

$$
c_{1,b}=c_1+\frac{t_f}{2}
$$

$$
h_w=h_a-2 t_f
$$

$$
\xi_e=-(2n-1) \rho + \sqrt{(2n-1)^2 \rho^2 + 2 \left[ (n-1) \frac{h_{sm}}{d} + 1 \right] \rho}
$$

$$
\xi_e=\frac{x_e}{d}
$$

$$
\rho=\frac{A_f}{d b_{cl}}
$$

$$
A_f=t_f b_f
$$

$$
I_2=\frac{b_{cl} x_e^3}{3} + (n-1) A_f (x_e - c_{1,b})^2 + n A_f (d-x_e)^2 + n t_w \left( \frac{(x_e - c_1 - t_f)^3}{3} + \frac{(h_w - x_e + c_1 + t_f)^3}{3} \right)
$$

$$
EI\text{-2} = E_{sm} I_2
$$

$$
EI\text{-eff/m} =  EI\text{-eff} = \frac{EI\text{-1} + EI\text{-2}}{2a}
$$

![Naming conventions for reinforcement geometry](/docs/assets/groundhog/docs/excavations/images/IPE_conventions.png)

*Naming conventions for reinforcement geometry*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `moment_inertia_reinforcement` | m4 | moment_inertia_reinforcement >= 0.0 | required | Moment of inertia of the reinforcement ($I_a$) |
| `modulus_soilmix` | kPa | modulus_soilmix >= 0.0 | required | Youngs modulus of the soilmix ($E_{sm}$) |
| `height_soilmix` | m | height_soilmix >= 0.0 | required | Height of the soilmix material ($h_{sm}$) |
| `reinforcement_offset` | m | reinforcement_offset >= 0.0 | required | Offset of reinforcement elements (center to center) ($a$) |
| `height_reinforcement` | m | height_reinforcement >= 0.0 | required | Longest dimension of the reinforcement ($h_a$) |
| `flange_thickness` | m | flange_thickness >= 0.0 | required | Thickness of the flanges ($t_f$) |
| `connection_thickness` | m | connection_thickness >= 0.0 | required | Thickness of the connection between the flanges ($t_w$) |
| `flange_width` | m | flange_width >= 0.0 | required | Width of the flanges ($b_f$) |
| `modulus_reinforcement` | kPa | 0.0 <= modulus_reinforcement <= 300000000.0 | `210000000.0` | Youngs modulus of the reinforcement (steel by default) ($E_a$) |
| `participating_width` | m | participating_width >= 0.0 | `nan` | Participating width for bending. For most cases, this is equal to the center-to-center distance of reinforcement (default when np.nan is used) ($b_{c1}$) |
| `tensile_strength_soilmix` | kPa | tensile_strength_soilmix >= 0.0 | `nan` | Tensile strength of soilmix to calculate cracking moment ($f_{sm,t}$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `n [-]` | - | Ratio of reinforcement and soilmix moduli [-] ($n$) |
| `Ism [m4]` | m4 | Moment of inertia of soilmix [m4] ($I_{sm}$) |
| `EI-1 [kNm2]` | kNm2 | Bending stiffness of the uncracked section [kNm2] ($EI\text{-1}$) |
| `Mcr [kNm]` | kNm | Cracking moment (if tensile strength is specified) [kNm] ($M_{cr}$) |
| `c1 [m]` | m | Net cover above reinforcement [m] ($c_1$) |
| `c2 [m]` | m | Net cover below reinforcement [m] ($c_2$) |
| `d [m]` | m | Useful height of lower flange [m] ($d$) |
| `c1b [m]` | m | Gross cover on upper flange [m] ($c_{1b}$) |
| `hw [m]` | m | Height of the body of the reinforcement [m] ($h_w$) |
| `Af [m2]` | m2 | Flange area [m2] ($A_f$) |
| `rho [-]` | - | [-] ($\rho$) |
| `xi,e [-]` | - | [-] ($\xi_e$) |
| `xe [m]` | m | Effective height of the section [m] ($x_e$) |
| `I2 [m4]` | m4 | Moment of inertia of the cracked section [m4] ($I_2$) |
| `EI-2 [kNm2]` | kNm2 | Bending stiffness of the cracked section [kNm2] ($EI\text{-2}$) |
| `EI [kNm2]` | kNm2 | Bending stiffness of the combined section [kNm2] ($EI$) |
| `EI-eff/m [kNm2]` | kNm2 | Bending stiffness of the combined section per unit length [kNm2] ($EI\text{-eff}$) |

**References**

- Denies, N. and Huybrechts, N. (2016). Handboek soimix-wanden - Ontwerp en uitvoering, SBRCURnet

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="bendingstiffness_soilmix_method2"></a>

## `bendingstiffness_soilmix_method2`

<span class="gc-badge gc-available" data-geocore-function="bendingstiffness_soilmix_method2">Available in GeoCore</span> [Excavations › Soilmix › Bending Stiffness (Method 2)](/docs/geocore/using/modules#bendingstiffness_soilmix_method2)

```python
bendingstiffness_soilmix_method2(
    bendingstiffness_reinforcement,
    modulus_soilmix,
    height_soilmix,
    reinforcement_offset,
    participating_width=nan,
    **kwargs,
)
```

Calculates the bending stiffness of a soilmix wall with internal reinforcements according to a simplified method. The effective bending stiffness is calculated as the sum of the stiffness of the reinforcement and the stiffness of the soilmix zone under compression. This method is usually on the conservative side, with bending stiffnesses 10 to 20% lower than the ones calculated with the more accurate method 1.

$$
EI\text{-eff} = E_a I_a + E_{sm} \left[ \frac{b_{c1} \cdot \left( \frac{h_{sm}}{2} \right)^3}{3} \right]
$$

$$
EI\text{-eff} / m^{\prime} = EI\text{-eff} / a=\frac{E_a I_a}{a} + E_{sm} \left[ \frac{\left( \frac{h_{sm}}{2} \right)^3}{3} \right]
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `bendingstiffness_reinforcement` | m4 | bendingstiffness_reinforcement >= 0.0 | required | Bending stiffness of the reinforcement ($E_a I_a$) |
| `modulus_soilmix` | kPa | modulus_soilmix >= 0.0 | required | Youngs modulus of the soilmix material ($E_{sm}$) |
| `height_soilmix` | m | height_soilmix >= 0.0 | required | Height of the soilmix material ($h_{sm}$) |
| `reinforcement_offset` | m | reinforcement_offset >= 0.0 | required | Center-to-center offset of reinforcement elements ($a$) |
| `participating_width` | m | participating_width >= 0.0 | `nan` | Participating width for bending. For most cases, this is equal to the center-to-center distance of reinforcement (default when np.nan is used) ($b_{c1}$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `EaIa [kNm2]` | kNm2 | Bending stiffness of the reinforcement [kNm2] ($E_a I_a$) |
| `EI_sm [kNm2]` | kNm2 | Bending stiffness of the soilmix [kNm2] ($EI_{sm}$) |
| `EI-eff [kNm2]` | kNm2 | Effective bending stiffness of the combined section [kNm2] ($EI\text{-eff}$) |
| `EI-eff/m [kNm2/m]` | kNm2/m | Effective bending stiffness per unit wall length [kNm2/m] ($EI\text{-eff/m}$) |

**References**

- Denies, N. and Huybrechts, N. (2016). Handboek soimix-wanden - Ontwerp en uitvoering, SBRCURnet

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.
