# Site Investigation & CPT Processing

GeoCore includes dedicated classes and functions for processing Cone Penetration Tests (CPT/PCPT), Standard Penetration Tests (SPT), and soil classification index tests.

## 1. PCPT Processing Class (`PCPTProcessing`)

The `PCPTProcessing` class reads CPT soundings ($z$, $q_c$, $f_s$, $u_2$) and automatically computes normalized parameters according to **Robertson (1990/2009/2016)** and **Lunne et al. (1997)**.

### Computed Parameters
- **Normalized Cone Resistance ($Q_{tn}$)**
- **Friction Ratio ($F_r$)**
- **Soil Behavior Type Index ($I_c$)**
- **Undrained Shear Strength ($s_u$)**:
  $$s_u = \frac{q_t - \sigma_{v0}}{N_{kt}}$$
- **Overconsolidation Ratio (OCR)**
- **Small-Strain Shear Modulus ($G_{max}$)**

---

## 2. Standard Penetration Test (`SPTProcessing`)

Corrects raw field blow counts ($N$) to standardized $N_{60}$ and $(N_1)_{60}$ values:
- Overburden correction according to **Liao & Whitman (1986)** or **ISO 22476-3**.
- Energy ratio correction ($E_r$).
- Borehole diameter and rod length factors.

---

## 3. Laboratory Index Tests

- **Plasticity Chart (`PlasticityChart`)**: Classifies fine-grained soils on Casagrande's A-line chart (USCS classification).
- **Particle Size Distribution (`PSDChart`)**: Generates grain-size distribution curves ($D_{10}$, $D_{30}$, $D_{60}$, $C_u$, $C_c$).
