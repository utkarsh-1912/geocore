---
title: Shallow foundations
slug: groundhog/guides/topics/shallowfoundations
section: Groundhog Guides
description: Overview of groundhog's shallow foundations functionality with links to the API reference.
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/v0.15.0/docs/shallowfoundations/shallowfoundations_toplevel.rst
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.15.0
edited_by_geocore: true
geocore_edit_note: Upstream toctree/autodoc structure restructured into a single topic page that links to the API reference instead of duplicating it, with a short note on how to run this in GeoCore prepended.
upstream_docs_url: https://groundhog.readthedocs.io/en/main/shallowfoundations/shallowfoundations_toplevel.html
---

> **Adapted from groundhog's own documentation.** Inside GeoCore, these functions run through the [calculation catalogue](/docs/geocore/using/modules) or through **GeoAI**, which selects and calls them through its validated Tool Registry — you never need to install Python or groundhog yourself.

This page follows the structure of the upstream groundhog documentation for *Shallow foundations*. For each function it gives the method summary and key formulas from the groundhog docstrings, with a link to the full API reference.

## Stress distributions

Upstream page: [Stress distributions](https://groundhog.readthedocs.io/en/main/shallowfoundations/stressdistribution.html)

Module [`groundhog.shallowfoundations.stressdistribution`](/docs/groundhog/api/shallowfoundations/stressdistribution). Summaries and formulas below are taken from the docstrings; the API reference has parameters, units and outputs.

### stresses_pointload

Function [`stresses_pointload`](/docs/groundhog/api/shallowfoundations/stressdistribution#stresses_pointload).

Calculates the stresses at a point below a line load according the solution proposed by Boussinesq (1885).

$$
\Delta \sigma_z = \frac{3Q}{2 \pi z^2 \left[ 1 + \left( \frac{r}{z} \right)^2 \right]^{5/2}}
$$

$$
\Delta \sigma_r = \frac{Q}{2 \pi} \left( \frac{3 r^2 z}{(r^2 + z^2)^{5/2}} - \frac{1 - 2 \nu}{r^2 + z^2 + z \left( r^2 + z^2 \right)^{1/2}}\right)
$$

*2 more formulas in the full reference.*

*Reference:* Budhu (2011). Soil mechanics and foundation engineering

### stresses_stripload

Function [`stresses_stripload`](/docs/groundhog/api/shallowfoundations/stressdistribution#stresses_stripload).

Calculates the stress redistribution at a point in the subsoil due to a strip load with a given width, applied at the surface.

$$
R_1 = \sqrt{x^2 + z^2}
$$

$$
R_2 = \sqrt{(x - B)^2 + z^2}
$$

*10 more formulas in the full reference.*

*Reference:* Budhu (2011). Soil mechanics and foundation engineering

### stresses_circle

Function [`stresses_circle`](/docs/groundhog/api/shallowfoundations/stressdistribution#stresses_circle).

Calculates the stress distribution below a uniformly loaded circular foundation.

$$
\Delta \sigma_z = q_s \left[ 1 - \left( \frac{1}{1 + (r_0 / z)^2} \right)^{3/2} \right]
$$

$$
\Delta \sigma_r = \Delta \sigma_{\theta} = \frac{q_s}{2} \left[ (1 + 2 \nu) - \frac{4 (1 + \nu)}{\sqrt{1 + (r_0 / z)^2}} + \frac{1}{\left[ 1 + (r_0 / z)^2 \right]^{3/2}} \right]
$$

*Reference:* Budhu (2011). Soil mechanics and foundation engineering

### stresses_rectangle

Function [`stresses_rectangle`](/docs/groundhog/api/shallowfoundations/stressdistribution#stresses_rectangle).

Calculates the stresses under the corner of a uniformly loaded rectangular area.

$$
\Delta \sigma_z = \frac{q_s}{2 \pi} \left[ \tan^{-1} \frac{L B}{z R_3} + \frac{L B z}{R_3} \left( \frac{1}{R_1^2} + \frac{1}{R_2^2} \right) \right]
$$

$$
\Delta \sigma_x = \frac{q_s}{2 \pi} \left[ \tan^{-1} \frac{L B}{z R_3} - \frac{L B z}{R_1^2 R_3} \right]
$$

*6 more formulas in the full reference.*

*Reference:* Budhu (2011). Soil mechanics and foundation engineering

### stresses_lineload_retainingwall

Function [`stresses_lineload_retainingwall`](/docs/groundhog/api/shallowfoundations/stressdistribution#stresses_lineload_retainingwall).

Calculates the elastic stress increase due to a line load (infinitely long out of plane) next to a buried earth-retaining structure.

$$
\Delta \sigma_x = \frac{4 Q a^2 b}{\pi H_0 \left( a^2 + b^2 \right)^2}
$$

$$
\Delta P_x = \frac{2 Q}{\pi \left( a^2 + 1 \right)}
$$

*Reference:* Budhu (2011). Soil mechanics and foundation engineering

### stresses_stripload_retainingwall

Function [`stresses_stripload_retainingwall`](/docs/groundhog/api/shallowfoundations/stressdistribution#stresses_stripload_retainingwall).

Calculates the elastic stress increase due to a strip load (infinitely long out of plane) at an offset from a buried earth-retaining structure.

$$
\Delta \sigma_x = \frac{2 q_s}{\pi} \left( \beta - \sin \beta \cos 2 \alpha \right)
$$

$$
\Delta P_x = \frac{q_s}{90} \left[ H_0 \left( \theta_2 - \theta_1 \right) \right]
$$

*5 more formulas in the full reference.*

*Reference:* Budhu (2011). Soil mechanics and foundation engineering

## Shallow foundation capacity

Upstream page: [Shallow foundation capacity](https://groundhog.readthedocs.io/en/main/shallowfoundations/capacity.html)

### ShallowFoundationCapacityUndrained

Class [`ShallowFoundationCapacityUndrained`](/docs/groundhog/api/shallowfoundations/capacity#shallowfoundationcapacityundrained).

### ShallowFoundationCapacityDrained

Class [`ShallowFoundationCapacityDrained`](/docs/groundhog/api/shallowfoundations/capacity#shallowfoundationcapacitydrained).

Module [`groundhog.shallowfoundations.capacity`](/docs/groundhog/api/shallowfoundations/capacity). Summaries and formulas below are taken from the docstrings; the API reference has parameters, units and outputs.

### verticalcapacity_undrained_api

Function [`verticalcapacity_undrained_api`](/docs/groundhog/api/shallowfoundations/capacity#verticalcapacity_undrained_api).

Calculates the vertical capacity for a shallow foundation in clay with constant or linearly increasing undrained shear strength according to API RP 2GEO.

$$
q_u = s_u \cdot N_c \cdot K_c \quad \text{ (constant)}
$$

$$
q_u = F \cdot \left( s_{uo} \cdot N_c + \frac{\kappa \cdot B^{\prime}}{4} \right) \cdot K_c  \quad \text{ (linearly increasing) }
$$

*21 more formulas in the full reference.*

*Reference:* API RP 2GEO, 2011. API RP 2GEO Geotechnical and Foundation Design Considerations

### verticalcapacity_drained_api

Function [`verticalcapacity_drained_api`](/docs/groundhog/api/shallowfoundations/capacity#verticalcapacity_drained_api).

Calculates the vertical capacity for a shallow foundation in sand with effective friction angle characterized from drained triaxial tests.

$$
q_u = p_o^{\prime} (N_q - 1) K_q + 0.5 \gamma^{\prime} B^{\prime} N_{\gamma} K_{\gamma}
$$

$$
Q_d^{\prime} = \left[ p_o^{\prime} (N_q - 1) K_q + 0.5 \gamma^{\prime} B^{\prime} N_{\gamma} K_{\gamma} \right] A^{\prime}
$$

*14 more formulas in the full reference.*

*Reference:* API RP 2GEO, 2011. API RP 2GEO Geotechnical and Foundation Design Considerations

### slidingcapacity_undrained_api

Function [`slidingcapacity_undrained_api`](/docs/groundhog/api/shallowfoundations/capacity#slidingcapacity_undrained_api).

Calculates the undrained sliding capacity for a shallow foundation on clay, the contribution of skirt resistance is taken into account.

$$
H_d = S_{uo} \cdot A
$$

$$
\Delta H = K_{ru} \cdot (S_{u,ave}) \cdot A_h
$$

*Reference:* API RP 2GEO, 2011. API RP 2GEO Geotechnical and Foundation Design Considerations

### slidingcapacity_drained_api

Function [`slidingcapacity_drained_api`](/docs/groundhog/api/shallowfoundations/capacity#slidingcapacity_drained_api).

Calculates the drained sliding capacity for a shallow foundation.

$$
H_d^{\prime} = Q \cdot \tan \phi^{\prime}
$$

$$
\Delta H = 0.5 \cdot K_{rd} \cdot \gamma^{\prime} \cdot D_b \cdot A_h
$$

*2 more formulas in the full reference.*

*Reference:* API RP 2GEO, 2011. API RP 2GEO Geotechnical and Foundation Design Considerations

### effectivearea_rectangle_api

Function [`effectivearea_rectangle_api`](/docs/groundhog/api/shallowfoundations/capacity#effectivearea_rectangle_api).

Calculates the reduced area of a rectangular footing to account for eccentricty of the load.

$$
e_1 = \frac{M_1}{Q}
$$

$$
e_2 = \frac{M_2}{Q}
$$

*3 more formulas in the full reference.*

*Reference:* API RP 2GEO, 2011. API RP 2GEO Geotechnical and Foundation Design Considerations

### effectivearea_circle_api

Function [`effectivearea_circle_api`](/docs/groundhog/api/shallowfoundations/capacity#effectivearea_circle_api).

Calculates the reduced area for a circular foundation to account for load eccentricity.

$$
A^{\prime} = 2s=B^{\prime} L^{\prime}
$$

$$
L^{\prime}=\left( 2s \sqrt{\frac{R+e_2}{R-e_2}} \right)^{1/2}
$$

*2 more formulas in the full reference.*

*Reference:* API RP 2GEO, 2011. API RP 2GEO Geotechnical and Foundation Design Considerations

### envelope_drained_api

Function [`envelope_drained_api`](/docs/groundhog/api/shallowfoundations/capacity#envelope_drained_api).

Calculates a drained failure envelope for shallow foundations according to API RP 2GEO.

$$
\tan(\text{inclination}) = \frac{H_{eff}}{Q} = \frac{H - H_{\text{outside eff}} - \Delta H}{Q}
$$

*Reference:* API RP 2GEO

### envelope_undrained_api

Function [`envelope_undrained_api`](/docs/groundhog/api/shallowfoundations/capacity#envelope_undrained_api).

Calculates the undrained failure envelope according to API RP 2GEO.

$$
\Delta e = D \cdot \tan \theta
$$

*Reference:* API RP 2GEO, 2011. API RP 2GEO Geotechnical and Foundation Design Considerations

### nq_frictionangle_sand

Function [`nq_frictionangle_sand`](/docs/groundhog/api/shallowfoundations/capacity#nq_frictionangle_sand).

Calculate the bearing capacity factor Nq from the friction angle

$$
N_q = e^{\pi \tan \phi_p^{\prime}} \tan^2 \left( 45^{\circ} + \frac{ \phi_p^{\prime}}{2} \right)
$$

*Reference:* Budhu (2011) Introduction to soil mechanics and foundations

### ngamma_frictionangle_vesic

Function [`ngamma_frictionangle_vesic`](/docs/groundhog/api/shallowfoundations/capacity#ngamma_frictionangle_vesic).

Calculates the bearing capacity factor Ngamma according to the equation proposed by Vesic (1973).

$$
N_{\gamma} = 2 (N_q + 1) \tan \phi_p^{\prime}
$$

*Reference:* Budhu (2011) Introduction to soil mechanics and foundations

### ngamma_frictionangle_meyerhof

Function [`ngamma_frictionangle_meyerhof`](/docs/groundhog/api/shallowfoundations/capacity#ngamma_frictionangle_meyerhof).

Calculates the bearing capacity factor Ngamma according to the equation proposed by Meyerhof (1976).

$$
N_{\gamma} = (N_q - 1) \tan (1.4 \phi_p^{\prime})
$$

*Reference:* Budhu (2011) Introduction to soil mechanics and foundations

### ngamma_frictionangle_davisbooker

Function [`ngamma_frictionangle_davisbooker`](/docs/groundhog/api/shallowfoundations/capacity#ngamma_frictionangle_davisbooker).

Calculates the bearing capacity factor Ngamma according to the equation proposed by Davis and Booker (1971).

$$
N_{\gamma} = \begin{cases}
    0.1054 \exp (9.6 \phi_p^{\prime})       & \quad \text{for rough footings}\\
    0.0663 \exp(9.3 \phi_p^{\prime})  & \quad \text{for smooth footings}
  \end{cases}
$$

*Reference:* Budhu (2011) Introduction to soil mechanics and foundations

### failuremechanism_prandtl

Function [`failuremechanism_prandtl`](/docs/groundhog/api/shallowfoundations/capacity#failuremechanism_prandtl).

Calculates the shape of the Prandtl failure mechanism for a given friction angle.

$$
\theta = \frac{\pi}{4} + \frac{\varphi^{\prime}}{2}
$$

$$
r = r_0 \cdot e^{\frac{\pi}{2} \tan \varphi^{\prime}}
$$

*Reference:* Budhu (2010). Soil Mechanics and Foundations

### ShallowFoundationCapacity

Class [`ShallowFoundationCapacity`](/docs/groundhog/api/shallowfoundations/capacity#shallowfoundationcapacity).

### ShallowFoundationCapacityUndrained

Class [`ShallowFoundationCapacityUndrained`](/docs/groundhog/api/shallowfoundations/capacity#shallowfoundationcapacityundrained).

### ShallowFoundationCapacityDrained

Class [`ShallowFoundationCapacityDrained`](/docs/groundhog/api/shallowfoundations/capacity#shallowfoundationcapacitydrained).

## Settlement

Upstream page: [Settlement](https://groundhog.readthedocs.io/en/main/shallowfoundations/settlement.html)

Module [`groundhog.shallowfoundations.settlement`](/docs/groundhog/api/shallowfoundations/settlement). Summaries and formulas below are taken from the docstrings; the API reference has parameters, units and outputs.

### primaryconsolidationsettlement_nc

Function [`primaryconsolidationsettlement_nc`](/docs/groundhog/api/shallowfoundations/settlement#primaryconsolidationsettlement_nc).

Calculates the primary consolidation settlement for normally consolidated fine grained soil.

$$
\Delta z = \frac{H_0}{1 + e_0} C_c \log_{10} \frac{\sigma_{v0}^{\prime} + \Delta \sigma_v^{\prime}}{\sigma_{v0}^{\prime}}
$$

$$
\Delta e = C_c \log_{10} \frac{\sigma_{v0}^{\prime} + \Delta \sigma_v^{\prime}}{\sigma_{v0}^{\prime}}
$$

*Reference:* Budhu (2011). Soil mechanics and foundation engineering

### primaryconsolidationsettlement_oc

Function [`primaryconsolidationsettlement_oc`](/docs/groundhog/api/shallowfoundations/settlement#primaryconsolidationsettlement_oc).

Calculates the primary consolidation settlement for an overconsolidated clay.

$$
\Delta z = \frac{H_0}{1 + e_0} C_r \log_{10} \frac{\sigma_{v0}^{\prime} + \Delta \sigma_v^{\prime}}{\sigma_{v0}^{\prime}}; \ \sigma_{v0}^{\prime} + \Delta \sigma_v^{\prime} < p_c^{\prime}
$$

$$
\Delta z = \frac{H_0}{1 + e_0} \left( C_r \log_{10} \frac{p_c^{\prime}}{\sigma_{v0}^{\prime}} + C_c \log_{10} \frac{\sigma_{v0}^{\prime} + \Delta \sigma_v^{\prime}}{p_c^{\prime}} \right); \ \sigma_{v0}^{\prime} + \Delta \sigma_v^{\prime} > p_c^{\prime}
$$

*2 more formulas in the full reference.*

*Reference:* Budhu (2011). Soil mechanics and foundation engineering

### consolidationsettlement_mv

Function [`consolidationsettlement_mv`](/docs/groundhog/api/shallowfoundations/settlement#consolidationsettlement_mv).

Calculates the consolidation settlement using the compressibility m_v (inverse of constrained modulus M).

$$
\Delta \epsilon = m_v \cdot \Delta \sigma_v^{\prime}
$$

$$
\Delta z = \Delta \epsilon \cdot H_0
$$

*1 more formula in the full reference.*

*Reference:* Budhu (2011). Soil mechanics and foundation engineering

### SettlementCalculation

Class [`SettlementCalculation`](/docs/groundhog/api/shallowfoundations/settlement#settlementcalculation).

Calculates shallow foundation settlement under a certain distributed load

### SettlementCalculation

Class [`SettlementCalculation`](/docs/groundhog/api/shallowfoundations/settlement#settlementcalculation).

Calculates shallow foundation settlement under a certain distributed load
