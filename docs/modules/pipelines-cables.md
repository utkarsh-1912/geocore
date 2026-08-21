# Offshore Pipelines & Power Cables

GeoCore provides dedicated analytical solutions for subsea pipeline and marine cable on-bottom stability, seabed touchdown embedment, and penetration geometry.

---

## 1. Seabed Penetration & Embedment

### Undrained Embedment (Clay Seabed)
- **Method 1 (Cathie et al. / Verley & Lund)**:
  $$V / (s_u D) = a \cdot (z/D)^b$$
- **Method 2 (DNV-RP-F109 / White & Randolph)**:
  Nonlinear bearing capacity factors accounting for heave, remolding, and buoyancy.

### Drained Embedment (Sand Seabed)
Relates submerged vertical pipe weight $V'$ to penetration depth $z$ using modified Hansen / Brinch Hansen wedge penetration factors:

$$\frac{V'}{D} = \gamma' \cdot z \cdot N_\gamma(z/D, \phi')$$

---

## 2. Touchdown Lay Factor (`lay_touchdown_factor`)

Calculates the dynamic amplification and lay tension multiplier applied during pipelay or cable installation in the touchdown zone (TDZ).

---

## 3. Contact Width & Penetrated Area

- `contactwidth`: Calculates chord contact width $B = 2\sqrt{D z - z^2}$ for cylindrical pipes embedded to depth $z \le D/2$.
- `penetratedarea`: Computes cross-sectional area of the submerged cylindrical segment:
  $$A_p = R^2 \arccos\left(\frac{R - z}{R}\right) - (R - z)\sqrt{2Rz - z^2}$$
