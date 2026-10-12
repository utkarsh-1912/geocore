---
title: Indian Standard (BIS) calculations
slug: geocore/using/indian-standards
section: Using GeoCore
description: Theory, equations, clause references and inputs for GeoCore's IS 6403, IS 1498, IS 2131, IS 1892, IS 1904, IS 2950 and IS 2720 calculators.
origin: geocore
source_url: https://github.com/utkarsh-1912/geocore/blob/main/website/_content/geocore/indian-standards.md
license: GPL-3.0
author: Utkarsh Gupta
attribution: GeoCore documentation by Utkarsh Gupta, licensed under the GNU GPL v3.
groundhog_version: 0.16.0
edited_by_geocore: false
sources:
- python-backend/core/standards/bis/README.md
- website/_build/bis_docs.py
---

GeoCore implements a set of Indian Standard (Bureau of Indian Standards) calculations that groundhog does not
cover. They are in the app under **Indian Standards (BIS)** in the *Library* view (and under their engineering task
in the *By task* view), and GeoAI can call them as validated tools.

Each calculation takes SI inputs and cites the clause it applies. Inputs outside the scope of a clause are reported
as errors, never adjusted. Clause notes come back as warnings with the result.

The sections below are generated from the same source as the app's Guide & Theory pages
(`website/_build/bis_docs.py`). Parameter descriptions and units are read from the implementation, so they match
the calculator.

> **Editions implemented.**
> - IS 6403:1981 (Reaffirmed) with Amendment 1. Under revision by BIS.
> - IS 1904:2021.
> - IS 1892:2021.
> - IS 2131:1981. The 2025 revision is not encoded.
> - IS 1498:1970.
> - IS 2950 (Part 1):1981 with Amendment 1.
> - IS 2720 Parts 3/Sec 1 (1980), 5 (1985) and 17 (1986).
>
> Check results against the current edition of each code. BIS code texts are copyrighted and are not included
> with GeoCore.

## IS 6403 Bearing Capacity (Shallow Foundation)

*Net ultimate (and optionally net safe) bearing capacity of a shallow foundation on the shear criterion, IS 6403:1981 cl. 5.1-5.3.*

IS 6403 gives the **net ultimate bearing capacity** of a shallow foundation on the shear criterion. GeoCore
evaluates the general equation of cl. 5.1.2 with the factors of Tables 1-3:

$$q_d = c\,N_c\,s_c\,d_c\,i_c + q\,(N_q - 1)\,s_q\,d_q\,i_q + \tfrac{1}{2}\,B\,\gamma\,N_\gamma\,s_\gamma\,d_\gamma\,i_\gamma\,W'$$

where $q$ is the effective overburden pressure at the founding level.

### Bearing capacity factors (Table 1)

$$N_q = e^{\pi \tan\phi}\,\tan^2\!\left(45^\circ + \frac{\phi}{2}\right), \qquad N_c = (N_q - 1)\cot\phi, \qquad N_\gamma = 2\,(N_q + 1)\tan\phi$$

These closed forms reproduce Table 1 for $\phi$ = 0-50°. For $\phi = 0$, $N_c = 2 + \pi = 5.14$, $N_q = 1$ and
$N_\gamma = 0$ (cl. 5.3.1.1). For $\phi$ between 20° and 50°, $N_q$ and $N_\gamma$ come from Groundhog
(`nq_frictionangle_sand`, `ngamma_frictionangle_vesic`), which use the same equations.

### Failure mode

- **General shear:** the factors are read at $\phi$ with cohesion $c$.
- **Local shear (cl. 5.1.1):** $c' = \tfrac{2}{3}c$, and the factors are read at $\phi' = \tan^{-1}(0.67\tan\phi)$.
  GeoCore also evaluates the depth and inclination factors with $\phi'$.
- **From relative density (Table 3):** general shear for $D_r > 70\,\%$ and local shear for $D_r < 20\,\%$.
  Between these, $q_d$ is interpolated linearly between the local and general values.

### Shape factors (Table 2)

| Shape | $s_c$ | $s_q$ | $s_\gamma$ |
|---|---|---|---|
| Strip | 1 | 1 | 1 |
| Square | 1.3 | 1.2 | 0.8 |
| Circle | 1.3 | 1.2 | 0.6 |
| Rectangle | $1 + 0.2\,B/L$ | $1 + 0.2\,B/L$ | $1 - 0.4\,B/L$ |

### Depth factors (cl. 5.1.2.2, optional)

The code allows depth factors only when the backfill is properly compacted, so they are off by default.
With $\sqrt{N_\phi} = \tan(45^\circ + \phi/2)$:

$$d_c = 1 + 0.2\,\frac{D_f}{B}\sqrt{N_\phi}, \qquad d_q = d_\gamma = \begin{cases}1 & \phi < 10^\circ \\ 1 + 0.1\,\dfrac{D_f}{B}\sqrt{N_\phi} & \phi \ge 10^\circ\end{cases}$$

### Inclination factors (cl. 5.1.2.3)

For a load inclined at $\alpha$ to the vertical:

$$i_c = i_q = \left(1 - \frac{\alpha}{90}\right)^2, \qquad i_\gamma = \left(1 - \frac{\alpha}{\phi}\right)^2$$

$i_\gamma = 0$ when $\alpha \ge \phi$.

### Water table (cl. 5.1.2.4 and cl. 2.2.2)

- $W' = 1$ when the water table is at or below $D_f + B$.
- $W' = 0.5$ when it is at or above the founding level $D_f$.
- Between these, $W'$ is interpolated linearly.

The effective surcharge $q$ uses the bulk unit weight above the water table and the submerged unit weight
$\gamma_{sat} - \gamma_w$ below it.

### Eccentric loads (cl. 5.0.1)

The effective dimensions are $B' = B - 2e_B$ and $L' = L - 2e_L$. An eccentric square becomes a
$B' \times L'$ rectangle. Eccentric loading of a circular footing is outside the clause and is rejected.

### Net safe bearing capacity

If a factor of safety $F$ is given, $q_{ns} = q_{nu}/F$. By cl. 6.1, the allowable bearing capacity is the
lesser of $q_{nu}/F$ and the pressure that keeps settlement within the IS 1904 limits. This calculator gives
the shear criterion only.

### Limitations

- The graphical methods of IS 6403 are not implemented: the SPT chart (Fig. 1), the static cone chart
  (Fig. 2), two-layer clay (Fig. 3) and desiccated clay (Table 4).
- GeoCore warns when $D_f > B$ (the code covers shallow foundations, cl. 2.2.5).
- GeoCore warns when the founding depth is less than the 500 mm minimum of IS 1904:2021 cl. 7.2.
- IS 6403 is under revision by BIS.

### Inputs

| Input | Symbol | Unit | Range | Description |
|---|---|---|---|---|
| `width` | $B$ | m | — | Footing width B; diameter for a circle |
| `depth` | $D_f$ | m | — | Founding depth Df below the surrounding ground level |
| `water_table_depth` | $d_w$ | m | — | Depth of the (highest likely) water table below ground level |
| `unit_weight` | $\gamma$ | kN/m3 | — | Bulk unit weight gamma of the foundation soil |
| `cohesion` | $c$ | kPa | — | Cohesion c (undrained cohesion for phi = 0 analysis) |
| `friction_angle` | $\phi$ | deg | 0 to 50 deg (Table 1) | Angle of shearing resistance phi, 0-50 |
| `shape` | — | — | — | Footing shape. Options: strip, square, circle, rectangle |
| `length` | $L$ | m | — | Footing length L, required for a rectangle (L >= B) |
| `failure_mode` | — | — | — | Shear failure mode. Options: general, local, from_relative_density |
| `relative_density` | $D_r$ | % | 0 to 100 % | Relative density for failure_mode = from_relative_density |
| `load_inclination` | $\alpha$ | deg | 0 to below 90 deg | Inclination alpha of the resultant load to the vertical |
| `eccentricity_width` | $e_B$ | m | — | Load eccentricity along the width eB |
| `eccentricity_length` | $e_L$ | m | — | Load eccentricity along the length eL |
| `saturated_unit_weight` | $\gamma_{sat}$ | kN/m3 | — | Saturated unit weight, needed when the water table is above the base |
| `apply_depth_factors` | — | — | — | Apply cl. 5.1.2.2 depth factors (only if backfill is properly compacted) |
| `factor_of_safety` | $F$ | — | — | Factor of safety on net ultimate capacity for the net safe value |
| `unit_weight_water` | $\gamma_w$ | kN/m3 | — | Unit weight of water |

### Outputs

- Bearing capacity factors $N_c$, $N_q$, $N_\gamma$, and the shape, depth and inclination factors.
- $W'$, the effective surcharge $q$ [kPa], and the effective dimensions $B'$ and $L'$ [m].
- The cohesion, surcharge and unit weight terms [kPa].
- The net ultimate bearing capacity $q_{nu}$ [kPa].
- The net ultimate load on the effective area [kN/m for a strip, kN otherwise].
- With a factor of safety, the net safe bearing capacity $q_{ns}$ [kPa].
- Clause notes as warnings.

### References

- IS 6403:1981 (Reaffirmed), including Amendment No. 1 (1984). Bureau of Indian Standards. Under revision by BIS (CED 43).
- IS 1904:2021 (fourth revision). Bureau of Indian Standards.

Implementation: [`core/standards/bis/is6403.py`](https://github.com/utkarsh-1912/geocore/blob/main/python-backend/core/standards/bis/is6403.py#L141) (`bearing_capacity_is6403`).

## IS 1498 Soil Classification

*Laboratory classification of a soil into an IS 1498 group symbol and name (cl. 3.5, Table 3).*

IS 1498 classifies soil from its grading and plasticity.

### Division (cl. 3.1, 3.2)

- **Coarse-grained:** more than half of the material is retained on the 75-micron IS sieve (fines ≤ 50 %).
  The soil is a gravel (G) if more of the coarse fraction is gravel (retained on 4.75 mm) than sand,
  otherwise a sand (S).
- **Fine-grained:** more than 50 % fines. The liquid limit sets the compressibility: L for
  $w_L < 35\,\%$, I for 35-50 %, H for $w_L > 50\,\%$.
- **Peat (Pt)** is identified visually (colour, odour, fibrous texture) and is flagged by the user.

### Coarse-grained soils (Table 3)

With $5\,\%$ fines or less, the grading is assessed from

$$C_u = \frac{D_{60}}{D_{10}}, \qquad C_c = \frac{D_{30}^2}{D_{10}\,D_{60}}$$

- **GW:** $C_u > 4$ and $1 \le C_c \le 3$.
- **SW:** $C_u > 6$ and $1 \le C_c \le 3$.
- Otherwise the soil is poorly graded (GP, SP).

The fines content sets the symbol:

- **< 5 % fines:** clean soil (GW, GP, SW, SP).
- **> 12 % fines:** M if the fines plot below the A-line or $I_p < 4$, C if above with $I_p > 7$, and the dual
  symbol GM-GC or SM-SC if above with $I_p$ 4-7.
- **5-12 % fines:** borderline, with a dual symbol such as SP-SM. A borderline case of a borderline case
  takes the non-plastic symbol (cl. 3.5.2).

### Fine-grained soils (cl. 3.5.3, 3.5.4)

The A-line on the plasticity chart is

$$I_p = 0.73\,(w_L - 20)$$

- **Above the A-line:** clay (CL, CI, CH).
- **Below it:** silt (ML, MI, MH), or organic soil (OL, OI, OH) when the oven-dried liquid limit is below
  $\tfrac{3}{4}$ of the liquid limit before drying (cl. 3.5.3.1).
- **Above the A-line with $I_p$ 4-7:** ML-CL.
- **On the A-line, or on the $w_L$ = 35 or 50 lines** (within the boundary tolerance): a boundary symbol is
  given (cl. 3.5.4).

$I_p = w_L - w_P$, taken as 0 when $w_P \ge w_L$ (IS 2720 Part 5 cl. 8.2).

### Inputs

| Input | Symbol | Unit | Range | Description |
|---|---|---|---|---|
| `percent_fines` | — | % | 0 to 100 % (fines + gravel ≤ 100 %) | Percentage passing the 75-micron IS sieve |
| `percent_gravel` | — | % | 0 to 100 % | Percentage retained on the 4.75 mm IS sieve (gravel, 80-4.75 mm) |
| `liquid_limit` | $w_L$ | % | — | Liquid limit wL |
| `plastic_limit` | $w_P$ | % | — | Plastic limit wP |
| `non_plastic` | — | — | — | True when the plastic limit cannot be determined (Ip reported as NP) |
| `d10` | $D_{10}$ | mm | — | Particle size with 10 percent finer |
| `d30` | $D_{30}$ | mm | — | Particle size with 30 percent finer |
| `d60` | $D_{60}$ | mm | — | Particle size with 60 percent finer |
| `liquid_limit_oven_dried` | — | % | — | Liquid limit after oven drying, to identify organic fines |
| `highly_organic` | — | — | — | True for peat / highly organic soil identified visually (Pt) |
| `boundary_tolerance` | — | % | — | Distance from the A-line or the wL = 35 / 50 lines within which a soil is treated as lying on the line |

### Outputs

- Group symbol, group name and division.
- Gravel, sand and fines percentages.
- $C_u$ and $C_c$ where graded.
- $w_L$, $I_p$ and the A-line $I_p$ for fine-grained soil, plus the organic check if given.
- Boundary-classification notes.

### References

- IS 1498:1970 (Reaffirmed). Bureau of Indian Standards.
- IS 2720 (Part 5):1985. Bureau of Indian Standards.

Implementation: [`core/standards/bis/is1498.py`](https://github.com/utkarsh-1912/geocore/blob/main/python-backend/core/standards/bis/is1498.py#L69) (`classify_soil_is1498`).

## IS 2131 SPT N Corrections

*Overburden and dilatancy corrections of the SPT N value in cohesionless soil, IS 2131:1981 cl. 3.6.*

### Overburden correction (cl. 3.6.1, Fig. 1)

The observed N is multiplied by the factor of Fig. 1. That figure plots the Peck, Hanson and Thornburn (1974)
curve:

$$C_N = 0.77\,\log_{10}\!\left(\frac{20}{\sigma'_v}\right) \le 2.0, \qquad N' = C_N\,N$$

with $\sigma'_v$ in kgf/cm², where 1 kgf/cm² = 98.0665 kPa. Fig. 1 covers 0-5 kgf/cm² (about 490 kPa);
beyond that $C_N$ is extrapolated and a warning is given.

### Dilatancy correction (cl. 3.6.2)

For fine sand or silt below the water table, when $N' > 15$:

$$N'' = 15 + \tfrac{1}{2}\,(N' - 15)$$

### Optional energy normalisation (not IS 2131:1981)

If a measured hammer energy ratio ER [%] is given, N is first normalised as

$$N_{60} = N\,\frac{ER}{60}$$

This follows ISO 22476-3 and is labelled as such in the result. IS 2131 was revised in 2025; that edition's
energy correction is not encoded here.

### Inputs

| Input | Symbol | Unit | Range | Description |
|---|---|---|---|---|
| `n_observed` | $N$ | — | — | Observed N value, blows per 300 mm penetration |
| `effective_overburden_pressure` | $\sigma'_v$ | kPa | — | Effective vertical overburden pressure at the test depth |
| `fine_sand_or_silt_below_water_table` | — | — | — | True if the stratum is fine sand or silt below the water table (cl. 3.6.2) |
| `energy_ratio` | $ER$ | % | 0 to 100 % | Measured hammer energy ratio; if given N is first normalised to 60 % energy (not part of IS 2131:1981) |

### Outputs

- Effective overburden [kgf/cm²] and $C_N$.
- $N'$ after the overburden correction.
- $N''$ after the dilatancy correction (where it applies).
- The corrected N.
- $N_{60}$ when an energy ratio is given.

### References

- IS 2131:1981 (Reaffirmed). Bureau of Indian Standards. The 2025 revision is not encoded in GeoCore.
- Peck, R.B., Hanson, W.E. and Thornburn, T.H. (1974). Foundation Engineering, 2nd ed. Wiley. (The curve plotted in IS 2131 Fig. 1.)
- ISO 22476-3. Geotechnical investigation and testing: Field testing, Part 3: Standard penetration test. (Optional N60 normalisation only; not part of IS 2131:1981.)

Implementation: [`core/standards/bis/is2131.py`](https://github.com/utkarsh-1912/geocore/blob/main/python-backend/core/standards/bis/is2131.py#L33) (`spt_correction_is2131`).

## IS 1892 Depth of Investigation

*Guideline depth of subsurface investigation for a foundation type, IS 1892:2021 cl. 5.6.3.*

IS 1892 cl. 5.6.3.2 gives guideline depths of exploration, measured below the reference level:

| Foundation | Guideline depth | Reference level |
|---|---|---|
| Shallow (non-raft) | 2 to 3 × the largest foundation width $B$ | Founding level |
| Raft | 1.0 to 2.0 × the raft width ($B$ taken as at least 6 m) | Founding level |
| Pile | at least the greater of 5 m and $5D$ | Pile termination level |
| Embankment | 1.0 to 2.0 × the embankment height $H$ | Base of the embankment |
| Well | 1.5 to 2.0 × the well width or diameter | Well termination level |

Where the founding depth is given, GeoCore adds it to report depths below ground level. Embankments are
excluded from this.

Two further requirements apply to every case, and the calculator states them as notes:

- Investigate at least to the depth where the stress increase from the foundation is below **10 %** of the
  in-situ stress, and deeper where weaker layers lie below that zone (cl. 5.6.3.1).
- If rock is met earlier, extend the boreholes at least **5 m into rock**, depending on its characteristics
  (cl. 5.6.3.2).

The clause says these values "may be followed"; they are guidelines, not limits.

### Inputs

| Input | Symbol | Unit | Range | Description |
|---|---|---|---|---|
| `foundation_type` | — | — | — | Foundation type. Options: shallow, raft, pile, embankment, well |
| `width` | $B$ | m | — | Largest foundation width (shallow), raft width, or well width/diameter |
| `pile_diameter` | $D$ | m | — | Pile diameter, for pile foundations |
| `embankment_height` | $H$ | m | — | Embankment height, for embankments |
| `founding_depth` | $D_f$ | m | — | Founding level (pile tip / well termination for those types) below ground level |

### Outputs

- The rule applied and the reference level.
- Minimum and maximum guideline depth below the reference level [m].
- Where applicable, the same depths below ground level [m].

### References

- IS 1892:2021 (second revision). Bureau of Indian Standards.

Implementation: [`core/standards/bis/is1892.py`](https://github.com/utkarsh-1912/geocore/blob/main/python-backend/core/standards/bis/is1892.py#L30) (`investigation_depth_is1892`).

## IS 1892 Borehole Disposition

*Minimum number and disposition of boreholes by type of structure, IS 1892:2021 cl. 5.6.2, Table 2.*

IS 1892 Table 2 sets the minimum disposition of boreholes or trial pits:

| Structure category | Rule (Table 2) | GeoCore count |
|---|---|---|
| Light residential (single or double storey, lightly loaded) | At least one at the centre of the building | 1 |
| Site of about 0.4 ha | One in each corner and one in the centre | 5 |
| Large plan or multiple buildings | Grid with points not more than 50 m apart, minimum two, covering the built-up area | $\max\!\left(2,\ n_x\,n_y\right)$ |
| Building higher than 50 m | Minimum three at each building | 3 |
| Linear structure (road, railway, pipeline, wall, line) | 50 m to 500 m spacing: closer in erratic strata, wider in uniform strata | count at 500 m and at 50 m |
| Solar power plant | One per 2 to 5 ha, minimum 5 per site | count at 1 per 5 ha and 1 per 2 ha |

For the grid, $n_x = \lceil L/50 \rceil + 1$ and $n_y = \lceil W/50 \rceil + 1$. This assumes a rectangular
built-up area covered by a regular 50 m grid.

For a linear structure of length $L$, the count is $\lceil L/s \rceil + 1$ at spacing $s$.

Boreholes are preferred to trial pits. Add boreholes where the stratification varies significantly
(cl. 5.6.2).

### Inputs

| Input | Symbol | Unit | Range | Description |
|---|---|---|---|---|
| `structure_type` | — | — | — | Structure category. Options: light_residential, site_0_4_ha, large_plan_or_multiple_buildings, tall_building, linear, solar_plant |
| `plan_length` | $L$ | m | — | Plan length of the built-up area, for large_plan_or_multiple_buildings |
| `plan_width` | $W$ | m | — | Plan width of the built-up area, for large_plan_or_multiple_buildings |
| `route_length` | $L$ | m | — | Length of a linear structure (road, railway, pipeline, wall, line) |
| `site_area` | $A$ | ha | — | Site area, for a solar power plant |

### Outputs

- The Table 2 rule.
- The minimum number of boreholes, or the counts at both ends of the permitted spacing.
- Grid points along the length and width where a grid applies.

### References

- IS 1892:2021 (second revision). Bureau of Indian Standards.

Implementation: [`core/standards/bis/is1892.py`](https://github.com/utkarsh-1912/geocore/blob/main/python-backend/core/standards/bis/is1892.py#L91) (`borehole_layout_is1892`).

## IS 1904 Permissible Settlement

*Permissible maximum settlement, differential settlement and angular distortion of shallow foundations, IS 1904:2021 Table 1, with an optional check of calculated values.*

IS 1904:2021 Table 1 (cl. 16.3.4) gives permissible settlements by:

- foundation type (isolated or raft);
- type of structure;
- soil group: sand and hard clay, or plastic clay.

| Foundation | Structure | Sand / hard clay: max [mm] | Sand / hard clay: differential | Plastic clay: max [mm] | Plastic clay: differential | Angular distortion |
|---|---|---|---|---|---|---|
| Isolated | Steel | 50 | 0.0033 L | 50 | 0.0033 L | 1/300 |
| Isolated | Reinforced concrete | 50 | 0.0015 L | 75 | 0.0015 L | 1/666 |
| Isolated | Multistorey framed | 60 | 0.002 L | 75 | 0.002 L | 1/500 |
| Isolated | Water tower / silo | 50 | 0.0015 L | 75 | 0.0015 L | 1/666 |
| Raft | Steel | 75 | 0.0033 L | 100 | 0.0033 L | 1/300 |
| Raft | Reinforced concrete | 75 | 0.0021 L | 125 | 0.002 L | 1/500 |
| Raft | Multistorey framed | 75 | 0.0025 L | 125 | 0.0033 L | 1/400 (sand), 1/300 (clay) |
| Raft | Water tower / silo | 100 | 0.0025 L | 125 | 0.0025 L | 1/400 |

**Load bearing walls** (isolated foundations, either soil group): 60 mm maximum, with limits that depend on
$L/H$:

- 0.0002 L and 1/5000 at $L/H = 2$;
- 0.0004 L and 1/2500 at $L/H = 7$;
- interpolated linearly between.

The code gives no limits for rafts under load bearing walls.

The 2021 revision raised the limit for **rafts under RC structures on plastic clay to 125 mm** (100 mm in
IS 1904:1986).

### Check

The permissible differential settlement over a span $L$ is $\delta_{perm} = k\,L$, where $k$ is the Table 1
coefficient. If calculated values are given, GeoCore compares:

- the maximum settlement with the permissible maximum;
- the differential settlement with $\delta_{perm}$.

The calculated angular distortion is $\delta / L$ (cl. 16.3.5).

The code notes that the values are a guide; the designer decides the permissible settlements in each case.

### Inputs

| Input | Symbol | Unit | Range | Description |
|---|---|---|---|---|
| `foundation_type` | — | — | — | Foundation type. Options: isolated, raft |
| `structure_type` | — | — | — | Structure type. Options: steel, reinforced_concrete, multistorey_framed, load_bearing_walls, water_tower_silo |
| `soil_type` | — | — | — | Soil group of Table 1. Options: sand_hard_clay, plastic_clay |
| `span_length` | $L$ | m | — | L, length of the deflected part of wall/raft or centre-to-centre column distance |
| `length_height_ratio` | $L/H$ | — | 2 to 7 | L/H of a load bearing wall (2 to 7) |
| `calculated_max_settlement` | — | mm | — | Calculated maximum settlement to check |
| `calculated_differential_settlement` | — | mm | — | Calculated differential settlement over span_length to check |

### Outputs

- Permissible maximum settlement [mm], the differential coefficient (× L) and the angular distortion.
- With a span, the permissible differential settlement [mm].
- With calculated values, whether each is within the limit.

### References

- IS 1904:2021 (fourth revision). Bureau of Indian Standards.

Implementation: [`core/standards/bis/is1904.py`](https://github.com/utkarsh-1912/geocore/blob/main/python-backend/core/standards/bis/is1904.py#L63) (`permissible_settlement_is1904`).

## IS 1904 Sliding / Overturning Check

*Factor of safety against sliding or overturning compared with the IS 1904:2021 cl. 17.1 minimum.*

The factor of safety is the ratio of the resisting action to the disturbing action, in consistent units:

$$F = \frac{\text{resisting force or moment}}{\text{disturbing force or moment}}$$

IS 1904:2021 cl. 17.1 sets these minimum values:

| Check | Dead, imposed and earth pressure loads | Including wind or seismic forces |
|---|---|---|
| Sliding (cl. 17.1.1) | 1.75 | 1.5 |
| Overturning (cl. 17.1.2) | 2.0 | 1.5 |

The engineer computes the resisting and disturbing actions for the governing load combination; this
calculator only compares their ratio with the clause minimum.

### Inputs

| Input | Symbol | Unit | Range | Description |
|---|---|---|---|---|
| `check` | — | — | — | Stability check. Options: sliding, overturning |
| `resisting` | — | — | — | Resisting force [kN] (sliding) or resisting moment [kNm] (overturning), in consistent units |
| `disturbing` | — | — | — | Disturbing force or overturning moment, in the same units as resisting |
| `wind_or_seismic` | — | — | — | True when wind load or seismic forces are included with dead, imposed and earth pressure loads |

### Outputs

- The factor of safety.
- The required minimum.
- Whether the minimum is met.

### References

- IS 1904:2021 (fourth revision). Bureau of Indian Standards.

Implementation: [`core/standards/bis/is1904.py`](https://github.com/utkarsh-1912/geocore/blob/main/python-backend/core/standards/bis/is1904.py#L126) (`stability_check_is1904`).

## IS 2950 Raft Rigidity (Rigid / Flexible)

*Whether a raft may be analysed as rigid (conventional method) or flexible, from IS 2950 (Part 1) Appendix C.*

### Relative stiffness factor (Appendix C-2)

$$K = \frac{E}{12\,E_s}\left(\frac{d}{b}\right)^3 \quad\text{(rectangular)}, \qquad K = \frac{E}{12\,E_s}\left(\frac{d}{2R}\right)^3 \quad\text{(circular)}$$

where:

- $d$ is the raft thickness;
- $b$ is the length of the section in the bending axis;
- $R$ is the radius of a circular raft;
- $E$ is the concrete modulus and $E_s$ the modulus of compressibility of the soil.

$K > 0.5$ means the raft is rigid (C-2.1.1); $K \le 0.5$ means flexible (cl. 5.2.1).

### Column spacing criterion (Appendix C-3, cl. 5.1.1)

With the modulus of subgrade reaction $k$:

$$\lambda = \left(\frac{k\,B}{4\,E_c\,I}\right)^{1/4}$$

The conventional (rigid) method may be used when the column spacing is less than $1.75/\lambda$. By default
$I = B\,d^3/12$ (a solid slab of uniform thickness), in which case $\lambda$ does not depend on $B$.

Cl. 5.1.1 allows the rigid method when either criterion holds. Adjacent column loads and spacings must also
not vary by more than 20 % (cl. 5.1.3, 5.2.1); the engineer checks this.

### Inputs

| Input | Symbol | Unit | Range | Description |
|---|---|---|---|---|
| `shape` | — | — | — | Raft shape. Options: rectangular, circular |
| `raft_thickness` | $d$ | m | — | Raft thickness d |
| `concrete_modulus` | $E$ | kPa | — | Modulus of elasticity of the raft concrete E |
| `soil_modulus` | $E_s$ | kPa | — | Modulus of compressibility of the foundation soil Es |
| `raft_length` | $b$ | m | — | Rectangular raft: length b of the section in the bending axis |
| `raft_radius` | $R$ | m | — | Circular raft: radius R |
| `subgrade_modulus` | $k$ | kN/m3 | — | Modulus of subgrade reaction k for the raft width (IS 2950 App. B, IS 9214) |
| `raft_width` | $B$ | m | — | Raft width B for lambda |
| `moment_of_inertia` | $I$ | m4 | — | Moment of inertia I of the raft over width B; default B d^3 / 12 (solid slab) |
| `column_spacing` | — | m | — | Column spacing to compare with 1.75 / lambda |

### Outputs

- $K$ and the K criterion.
- With $k$: $\lambda$ [1/m] and the critical spacing $1.75/\lambda$ [m].
- With a column spacing: the spacing criterion.
- The resulting choice of analysis method.

### References

- IS 2950 (Part 1):1981 (Reaffirmed), including Amendment No. 1. Bureau of Indian Standards.

Implementation: [`core/standards/bis/is2950.py`](https://github.com/utkarsh-1912/geocore/blob/main/python-backend/core/standards/bis/is2950.py#L25) (`raft_rigidity_is2950`).

## IS 2720-3 Specific Gravity

*Specific gravity of soil particles by the density bottle method, referred to 27 °C, IS 2720 (Part 3/Sec 1):1980 cl. 5.*

From the four weighings of the density bottle method:

$$G = \frac{m_2 - m_1}{(m_4 - m_1) - (m_3 - m_2)}$$

- $m_1$: empty bottle;
- $m_2$: bottle and dry soil;
- $m_3$: bottle, soil and water;
- $m_4$: bottle full of water.

The value is referred to 27 °C by the ratio of water densities:

$$G_{27} = G\,\frac{\rho_w(T)}{\rho_w(27\,^\circ\mathrm{C})}$$

IS 2720 does not tabulate water density. GeoCore uses the Tanaka et al. (2001) correlation for air-free water,
valid for 0-40 °C.

Report the average of two determinations to 0.01, and repeat the test if they differ by more than 0.03
(cl. 6.1). A value outside 2.0-3.2 triggers a check-the-readings warning.

### Inputs

| Input | Symbol | Unit | Range | Description |
|---|---|---|---|---|
| `mass_bottle` | $m_1$ | g | — | m1, mass of the empty density bottle |
| `mass_bottle_soil` | $m_2$ | g | — | m2, mass of bottle and dry soil |
| `mass_bottle_soil_water` | $m_3$ | g | — | m3, mass of bottle, soil and water |
| `mass_bottle_water` | $m_4$ | g | — | m4, mass of bottle full of water only |
| `temperature` | $T$ | degC | 0 to 40 degC | Room/test temperature |

### Outputs

- $G$ at the test temperature.
- The temperature correction factor.
- $G_{27}$.

### References

- IS 2720 (Part 3/Section 1):1980. Bureau of Indian Standards.
- Tanaka, M., Girard, G., Davis, R., Peuto, A. and Bignell, N. (2001). Recommended table for the density of water between 0 °C and 40 °C based on recent experimental reports. Metrologia 38, 301-309.

Implementation: [`core/standards/bis/is2720.py`](https://github.com/utkarsh-1912/geocore/blob/main/python-backend/core/standards/bis/is2720.py#L26) (`specific_gravity_is2720`).

## IS 2720-5 Flow Index

*Flow index from two points of the flow curve, IS 2720 (Part 5):1985 cl. 3.5.2.*

The flow curve plots water content against the logarithm of the number of drops. Its slope is the flow index:

$$I_f = \frac{w_1 - w_2}{\log_{10}(N_2 / N_1)}$$

The two points ($w_1$, $N_1$) and ($w_2$, $N_2$) must have different numbers of drops. $I_f$ is used for the
toughness index $I_t = I_p / I_f$.

### Inputs

| Input | Symbol | Unit | Range | Description |
|---|---|---|---|---|
| `water_content_1` | $w_1$ | % | — | Water content w1 at N1 drops |
| `blows_1` | $N_1$ | — | — | Number of drops N1 |
| `water_content_2` | $w_2$ | % | — | Water content w2 at N2 drops |
| `blows_2` | $N_2$ | — | — | Number of drops N2 |

### Outputs

- Flow index $I_f$ [%].

### References

- IS 2720 (Part 5):1985. Bureau of Indian Standards.

Implementation: [`core/standards/bis/is2720.py`](https://github.com/utkarsh-1912/geocore/blob/main/python-backend/core/standards/bis/is2720.py#L57) (`flow_index_is2720`).

## IS 2720-5 One-Point Liquid Limit

*Liquid limit from a single trial, Casagrande (cl. 5.6) or cone (cl. 6.5), IS 2720 (Part 5):1985.*

### Casagrande apparatus (cl. 5.6)

$$w_L = \frac{w_N}{1.3215 - 0.23\,\log_{10} N}$$

valid for 15 to 35 drops.

### Cone penetrometer (cl. 6.5)

Two relationships are given, and both are reported:

$$w_L = \frac{w_N}{0.77\,\log_{10} D} \qquad\text{and}\qquad w_L = \frac{w_N}{0.65 + 0.0175\,D}$$

valid for a penetration $D$ of 16 to 26 mm.

Here $w_N$ is the water content of the accepted trial. The one-point method is not for highly organic soils.
Its constants are regional, so national and international reports should use the multi-point or cone method
(cl. 1.1.1).

### Inputs

| Input | Symbol | Unit | Range | Description |
|---|---|---|---|---|
| `water_content` | $w_N$ | % | — | Water content wN of the accepted trial |
| `method` | — | — | — | Apparatus. Options: casagrande, cone |
| `blows` | $N$ | — | 15 to 35 | Casagrande: number of drops to close the groove, 15-35 |
| `cone_penetration` | $D$ | mm | 16 to 26 mm | Cone: penetration D of the accepted trial, 16-26 |

### Outputs

- Liquid limit $w_L$ [%].
- For the cone, both the log and the linear relationship.

### References

- IS 2720 (Part 5):1985. Bureau of Indian Standards.

Implementation: [`core/standards/bis/is2720.py`](https://github.com/utkarsh-1912/geocore/blob/main/python-backend/core/standards/bis/is2720.py#L75) (`liquid_limit_one_point_is2720`).

## IS 2720-5 Consistency Indices

*Plasticity, liquidity, consistency and toughness indices, IS 2720 (Part 5):1985 cl. 8-11.*

$$I_p = w_L - w_P \qquad \text{(cl. 8)}$$

$I_p$ is reported as 0 when $w_P \ge w_L$ (cl. 8.2). The other indices are then undefined.

$$I_L = \frac{w_0 - w_P}{I_p}\ \ \text{(cl. 10)}, \qquad I_c = \frac{w_L - w_0}{I_p}\ \ \text{(cl. 11)}, \qquad I_t = \frac{I_p}{I_f}\ \ \text{(cl. 9)}$$

$I_L$ and $I_c$ need the natural water content $w_0$; $I_t$ needs the flow index $I_f$.

### Inputs

| Input | Symbol | Unit | Range | Description |
|---|---|---|---|---|
| `liquid_limit` | $w_L$ | % | — | Liquid limit wL |
| `plastic_limit` | $w_P$ | % | — | Plastic limit wP |
| `natural_water_content` | $w_0$ | % | — | Natural water content w0 |
| `flow_index` | $I_f$ | % | — | Flow index If, for the toughness index |

### Outputs

- $I_p$ [%].
- As the inputs allow: $I_L$, $I_c$ and $I_t$.

### References

- IS 2720 (Part 5):1985. Bureau of Indian Standards.

Implementation: [`core/standards/bis/is2720.py`](https://github.com/utkarsh-1912/geocore/blob/main/python-backend/core/standards/bis/is2720.py#L109) (`consistency_indices_is2720`).

## IS 2720-17 Constant Head Permeability

*Coefficient of permeability by the constant head test, referred to 27 °C, IS 2720 (Part 17):1986 cl. 5.4.*

$$k_T = \frac{Q\,L}{A\,h\,t}, \qquad i = \frac{h}{L}$$

- $Q$: volume of water collected in time $t$;
- $L$: length between the head-measuring points;
- $A$: cross-sectional area of the specimen;
- $h$: head loss.

The result is referred to 27 °C by the viscosity ratio:

$$k_{27} = k_T\,\frac{\eta_T}{\eta_{27}}$$

Water viscosity is not tabulated in IS 2720. GeoCore uses the Vogel equation,
$\eta = 2.414\times10^{-5}\cdot 10^{247.8/(T_K - 140)}$ Pa·s, which is within about 0.5 % of reference
values for 0-40 °C.

The test suits $k$ between $10^{-3}$ and $10^{-7}$ cm/s (cl. 1.1). Results outside that range are flagged.

### Inputs

| Input | Symbol | Unit | Range | Description |
|---|---|---|---|---|
| `discharge_volume` | $Q$ | cm3 | — | Quantity of water Q collected |
| `specimen_length` | $L$ | cm | — | Length of specimen L between head measuring points |
| `specimen_area` | $A$ | cm2 | — | Cross-sectional area of specimen A |
| `head_loss` | $h$ | cm | — | Head loss h over length L |
| `time` | $t$ | s | — | Collection time t |
| `temperature` | $T$ | degC | 0 to 40 degC | Water temperature T |

### Outputs

- Hydraulic gradient $i$.
- $k_T$ [cm/s].
- The viscosity ratio.
- $k_{27}$ [cm/s].

### References

- IS 2720 (Part 17):1986. Bureau of Indian Standards.

Implementation: [`core/standards/bis/is2720.py`](https://github.com/utkarsh-1912/geocore/blob/main/python-backend/core/standards/bis/is2720.py#L147) (`permeability_constant_head_is2720`).

## IS 2720-17 Falling Head Permeability

*Coefficient of permeability by the falling head test, referred to 27 °C, IS 2720 (Part 17):1986 cl. 6.3.*

$$k_T = 2.303\,\frac{a\,L}{A\,t}\,\log_{10}\!\left(\frac{h_1}{h_2}\right)$$

- $a$: area of the stand-pipe;
- $A$: area of the specimen;
- $L$: specimen length;
- $h_1$ and $h_2$: initial and final heads, with $h_2 < h_1$;
- $t$: elapsed time.

The result is referred to 27 °C as in the constant head test:

$$k_{27} = k_T\,\frac{\eta_T}{\eta_{27}}$$

Water viscosity comes from the Vogel equation (0-40 °C). Results outside the $10^{-3}$ to $10^{-7}$ cm/s range
recommended for the test (cl. 1.1) are flagged.

### Inputs

| Input | Symbol | Unit | Range | Description |
|---|---|---|---|---|
| `standpipe_area` | $a$ | cm2 | — | Cross-sectional area of the stand-pipe a |
| `specimen_length` | $L$ | cm | — | Length of specimen L |
| `specimen_area` | $A$ | cm2 | — | Cross-sectional area of specimen A |
| `initial_head` | $h_1$ | cm | — | Initial head h1 |
| `final_head` | $h_2$ | cm | — | Final head h2 |
| `time` | $t$ | s | — | Elapsed time tf - ti |
| `temperature` | $T$ | degC | 0 to 40 degC | Water temperature T |

### Outputs

- $k_T$ [cm/s].
- The viscosity ratio.
- $k_{27}$ [cm/s].

### References

- IS 2720 (Part 17):1986. Bureau of Indian Standards.

Implementation: [`core/standards/bis/is2720.py`](https://github.com/utkarsh-1912/geocore/blob/main/python-backend/core/standards/bis/is2720.py#L173) (`permeability_falling_head_is2720`).
