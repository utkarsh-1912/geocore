# One-Dimensional Consolidation & Dissipation

GeoCore provides numerical and analytical solutions for Terzaghi's 1D consolidation equation, excess pore pressure dissipation, and laboratory $c_v$ curve-fitting methods.

---

## 1. Terzaghi's 1D Consolidation Equation (`ConsolidationCalculation`)

Governing partial differential equation for excess pore water pressure $u(z, t)$:

$$\frac{\partial u}{\partial t} = c_v \frac{\partial^2 u}{\partial z^2}$$

Where:
- $c_v$ = Coefficient of consolidation ($c_v = \frac{k}{\gamma_w m_v}$).
- $z$ = Depth within compressible clay layer ($0 \le z \le 2H$).
- $t$ = Elapsed dissipation time.

### Boundary & Drainage Options
- **Top Boundary**: Free draining ($u = 0$) or Impermeable ($\partial u / \partial z = 0$).
- **Bottom Boundary**: Free draining ($u = 0$) or Impermeable ($\partial u / \partial z = 0$).
- **Initial Pressure $u_0(z)$**: Uniform, triangular, trapezoidal, or arbitrary discrete profile.

### Visualizing Isochrones
GeoCore computes excess pore water pressure dissipation at discrete time intervals and renders smooth interactive **isochrones** ($u$ vs. $z$) in Plotly.

---

## 2. Degree of Consolidation ($U_v$)

Average degree of consolidation over layer thickness $H$:

$$U_v = 1 - \sum_{m=0}^{\infty} \frac{2}{M^2} e^{-M^2 T_v}$$

Where $M = \frac{\pi}{2}(2m + 1)$ and $T_v = \frac{c_v t}{d^2}$ is the dimensionless time factor.

---

## 3. Laboratory $c_v$ Determination Wrappers

- **Casagrande Log-Time Method (`logtimemethod`)**: Finds $t_{50}$ from the intersection of initial tangent and late-time linear asymptote on semi-log scale ($c_v = 0.197 d^2 / t_{50}$).
- **Taylor Root-Time Method (`roottimemethod`)**: Finds $t_{90}$ from the 1.15 reciprocal slope line on $\sqrt{t}$ scale ($c_v = 0.848 d^2 / t_{90}$).
