# Deep Foundations & Pile Calculations

GeoCore provides comprehensive algorithms for evaluating pile capacity, load distribution, and settlement.

## 1. LCPC Method (Bustamante & Gianeselli)

Calculates pile base and shaft resistance using CPT cone resistance ($q_c$).

### Input Parameters
- **Soil Profile**: CSV / Excel file containing CPT depth and $q_c$ data.
- **Pile Diameter ($D$)**: Outside diameter of the pile in meters.
- **Soil Group**:
  - Base Group: Group I or Group II.
  - Shaft Group: Group IA, IB, IIA, or IIB.

---

## 2. Koppejan Method

Calculates pile resistance according to Koppejan's method.

### Input Parameters
- **Soil Profile**: CPT dataset with $q_c$ and total unit weight.
- **Pile Diameter ($D$)**: Diameter in meters.
- **Target Penetration Depth**: Depth for detailed resistance construction plots.
