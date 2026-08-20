# Shallow Foundations & Settlement Analysis

Calculates vertical stress distributions, bearing capacity, and elastic/consolidation settlement for shallow footings.

## 1. Stress Distributions

Calculates vertical stress increases ($\Delta \sigma_z$) beneath loaded areas:
- **Point Load**: Boussinesq & Westergaard solutions.
- **Line Load & Strip Load**: Smooth & rough contact stress profiles.
- **Rectangular Footing**: Corner stress integration for flexible & rigid footings.
- **Circular Footing**: Centerline and edge stress profiles.

---

## 2. Bearing Capacity

- **Eurocode 7 & Vesic**: Drained and undrained bearing capacity.
- **Effective Area Calculation**:
  - Rectangular footings: $B' = B - 2e_B$, $L' = L - 2e_L$
  - Circular footings: API RP 2GEO effective area geometry.

---

## 3. Settlement Analysis

- **Elastic Settlement**: Janbu, Christian & Carrier elastic strain influence factors.
- **CPT-based Settlement**: Schmertmann (1978) strain influence diagram method.
- **Primary Consolidation**: $m_v$ method or $C_c / C_r$ compression index method.
