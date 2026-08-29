# Author: Utkarsh Gupta
# License: GPL v3
"""
First-Class Standard Penetration Test (SPT) Normalization and Empirical Correlation Engine.
Calculates standardized N60 and overburden-corrected (N1)60 values
according to Skempton (1986) and Liao & Whitman (1986), and correlates
relative density (Dr) and effective friction angle (phi').
"""

from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional, Tuple
import math


@dataclass
class SPTRecord:
    """
    Structured Standard Penetration Test (SPT) data point.
    """
    borehole_id: str
    depth: float
    raw_n: int
    energy_ratio: float = 0.60              # Er: Hammer energy ratio (standard 60% = 0.60)
    rod_length: float = 10.0                # Rod length in meters
    borehole_diameter_mm: float = 150.0     # Borehole diameter in mm
    has_liner: bool = False                 # Standard split-spoon with/without liner
    effective_overburden_kpa: Optional[float] = None  # sigma_v0' in kPa

    def calculate_n60(self) -> Tuple[float, Dict[str, float]]:
        """
        Calculates field energy-corrected N60 value according to Skempton (1986):
        N60 = N_raw * (Er / 60) * Cr * Cb * Cs
        Where:
        - Ce = Er / 0.60 (Energy ratio correction)
        - Cr = Rod length correction (0.75 for L < 4m, 0.85 for 4-6m, 0.95 for 6-10m, 1.0 for L > 10m)
        - Cb = Borehole diameter correction (1.0 for 65-115mm, 1.05 for 150mm, 1.15 for 200mm)
        - Cs = Sampler liner correction (1.0 standard with liner, 1.2 without liner / loose sand)
        """
        Ce = self.energy_ratio / 0.60

        # Rod length factor Cr (Skempton 1986)
        if self.rod_length < 4.0:
            Cr = 0.75
        elif self.rod_length < 6.0:
            Cr = 0.85
        elif self.rod_length < 10.0:
            Cr = 0.95
        else:
            Cr = 1.0

        # Borehole diameter factor Cb
        if self.borehole_diameter_mm <= 115.0:
            Cb = 1.0
        elif self.borehole_diameter_mm <= 150.0:
            Cb = 1.05
        else:
            Cb = 1.15

        # Sampler liner factor Cs
        Cs = 1.0 if self.has_liner else 1.2

        N60 = float(self.raw_n) * Ce * Cr * Cb * Cs
        corrections = {
            "Ce": round(Ce, 3),
            "Cr": round(Cr, 3),
            "Cb": round(Cb, 3),
            "Cs": round(Cs, 3),
            "total_factor": round(Ce * Cr * Cb * Cs, 3)
        }
        return round(N60, 1), corrections

    def calculate_n1_60(self, atmospheric_pressure_kpa: float = 100.0) -> Tuple[float, float, Dict[str, float]]:
        """
        Calculates stress-normalized (N1)60 value according to Liao & Whitman (1986):
        (N1)60 = N60 * CN
        Where:
        - CN = sqrt(Pa / sigma_v0') <= 2.0 (Overburden correction factor)
        """
        n60, corrections = self.calculate_n60()

        # If overburden is not provided, estimate using 18.5 kN/m3
        sigma_v0_eff = self.effective_overburden_kpa if self.effective_overburden_kpa is not None else max(10.0, 18.5 * self.depth)
        sigma_v0_eff = max(1.0, sigma_v0_eff)

        # Liao & Whitman (1986) CN formula
        Cn = math.sqrt(atmospheric_pressure_kpa / sigma_v0_eff)
        Cn = min(2.0, max(0.4, Cn))  # Standard cap at 2.0

        n1_60 = n60 * Cn
        corrections["Cn"] = round(Cn, 3)
        corrections["sigma_v0_eff_kpa"] = round(sigma_v0_eff, 1)

        return round(n60, 1), round(n1_60, 1), corrections

    def correlate_granular_properties(self) -> Dict[str, Any]:
        """
        Empirically correlates relative density and effective friction angle from (N1)60:
        - Relative Density (Dr): Skempton (1986) Dr = sqrt((N1)60 / 60) * 100 %
        - Friction Angle (phi'): Peck, Hanson & Thornburn (1974) / Wolff (1989):
          phi' = 27.1 + 0.3 * (N1)60 - 0.00054 * (N1)60^2
        """
        n60, n1_60, corrections = self.calculate_n1_60()

        # Relative density Dr [%]
        Dr = min(100.0, max(0.0, math.sqrt(max(0.0, n1_60) / 60.0) * 100.0))

        # Effective friction angle phi' [deg] (Wolff 1989)
        phi_eff = 27.1 + 0.30 * n1_60 - 0.00054 * (n1_60 ** 2)
        phi_eff = min(46.0, max(26.0, phi_eff))

        # Soil description density class (BS 5930 / ASTM D1586)
        if n1_60 < 4:
            density_class = "Very Loose"
        elif n1_60 < 10:
            density_class = "Loose"
        elif n1_60 < 30:
            density_class = "Medium Dense"
        elif n1_60 < 50:
            density_class = "Dense"
        else:
            density_class = "Very Dense"

        return {
            "borehole_id": self.borehole_id,
            "depth_m": self.depth,
            "raw_N": self.raw_n,
            "N60": n60,
            "N1_60": n1_60,
            "Dr_pct": round(Dr, 1),
            "phi_eff_deg": round(phi_eff, 1),
            "density_class": density_class,
            "corrections": corrections,
            "provenance": {
                "method_n60": "Skempton (1986) Energy & Geometry Normalization",
                "method_n1_60": "Liao & Whitman (1986) Overburden Normalization",
                "method_phi": "Wolff (1989) / Peck, Hanson & Thornburn (1974)"
            }
        }
