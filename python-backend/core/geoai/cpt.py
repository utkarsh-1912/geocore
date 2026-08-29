# Author: Utkarsh Gupta
# License: GPL v3
"""
First-Class CPT Data Model and Deterministic Interpretation Engine.
Provides structured storage, normalization (Qt, Fr, Bq, Ic),
Soil Behavior Type (SBT) classification, and empirical parameter derivations
(su, phi', Dr, Gmax, OCR) preserving complete engineering provenance.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd

from core.geoai.provenance import CalculationProvenance


# Robertson (1990 / 2010) Soil Behavior Type (SBTn) Classification Zones by Ic:
# Zone 1: Sensitive fine-grained
# Zone 2: Clay - organic soil
# Zone 3: Clays: clay to silty clay (Ic > 2.95)
# Zone 4: Silt mixtures: clayey silt to silty clay (2.60 < Ic <= 2.95)
# Zone 5: Sand mixtures: silty sand to sandy silt (2.05 < Ic <= 2.60)
# Zone 6: Sands: clean sand to silty sand (1.31 < Ic <= 2.05)
# Zone 7: Gravelly sand to dense sand (Ic <= 1.31)
# Zone 8: Very stiff sand to clayey sand (heavily overconsolidated or cemented)
# Zone 9: Very stiff fine-grained (heavily overconsolidated or cemented)

SBT_ZONES_IC: List[Tuple[float, float, int, str]] = [
    (3.60, 10.0, 2, "Organic Soils - Peat"),
    (2.95, 3.60, 3, "Clays - Clay to Silty Clay"),
    (2.60, 2.95, 4, "Silt Mixtures - Clayey Silt to Silty Clay"),
    (2.05, 2.60, 5, "Sand Mixtures - Silty Sand to Sandy Silt"),
    (1.31, 2.05, 6, "Sands - Clean Sand to Silty Sand"),
    (0.00, 1.31, 7, "Gravelly Sand to Dense Sand"),
]


@dataclass
class CPTSounding:
    """
    First-class structured CPT sounding data object.
    Holds raw measurements, normalized parameters, and derived soil properties.
    """
    sounding_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    raw_data: pd.DataFrame = field(default_factory=pd.DataFrame)
    derived_data: pd.DataFrame = field(default_factory=pd.DataFrame)

    def __post_init__(self):
        if not self.raw_data.empty and self.derived_data.empty:
            self.calculate_normalized_parameters()

    @property
    def total_depth(self) -> float:
        if not self.raw_data.empty and "depth" in self.raw_data.columns:
            return float(self.raw_data["depth"].max())
        return 0.0

    @property
    def depth_interval(self) -> float:
        if len(self.raw_data) > 1 and "depth" in self.raw_data.columns:
            return float(self.raw_data["depth"].iloc[1] - self.raw_data["depth"].iloc[0])
        return 0.02

    def calculate_normalized_parameters(
        self,
        water_table_depth: float = 0.0,
        gamma_soil: float = 18.5,
        cone_net_area_ratio_a: float = 0.80,
        atmospheric_pressure_pa: float = 100.0
    ) -> pd.DataFrame:
        """
        Calculates normalized CPT parameters according to Robertson (1990/2009):
        - Total cone resistance: qt = qc + u2 * (1 - a)
        - Net cone resistance: qn = qt - sigma_v0
        - Normalized cone resistance: Qt = (qt - sigma_v0) / sigma_v0'
        - Normalized friction ratio: Fr = (fs / (qt - sigma_v0)) * 100 %
        - Pore pressure ratio: Bq = (u2 - u0) / (qt - sigma_v0)
        - Soil Behavior Type Index: Ic = sqrt((3.47 - log10(Qt))^2 + (log10(Fr) + 1.22)^2)
        """
        df = self.raw_data.copy()
        if "depth" not in df.columns:
            self.derived_data = pd.DataFrame()
            return self.derived_data

        z = df["depth"].to_numpy()
        qc = df["qc"].to_numpy() if "qc" in df.columns else np.zeros_like(z)      # [MPa]
        fs = df["fs"].to_numpy() if "fs" in df.columns else np.zeros_like(z)      # [kPa]
        u2 = df["u2"].to_numpy() if "u2" in df.columns else np.zeros_like(z)      # [kPa]

        # Convert qc to kPa for stress calculations
        qc_kpa = qc * 1000.0

        # Calculate in-situ total and effective vertical stresses [kPa]
        gamma_w = 9.81
        sigma_v0 = gamma_soil * z
        u0 = np.where(z > water_table_depth, gamma_w * (z - water_table_depth), 0.0)
        sigma_v0_eff = np.maximum(sigma_v0 - u0, 1.0)  # avoid division by zero

        # Correct cone resistance for pore pressure effects on unequal area
        # qt = qc + u2 * (1 - a)
        u2_kpa = u2
        qt_kpa = qc_kpa + u2_kpa * (1.0 - cone_net_area_ratio_a)
        qt_mpa = qt_kpa / 1000.0
        qn_kpa = np.maximum(qt_kpa - sigma_v0, 0.1)

        # Dimensionless Normalized Parameters (Robertson 1990)
        Qt = qn_kpa / sigma_v0_eff
        Qt = np.clip(Qt, 0.1, 10000.0)

        # Normalized friction ratio Fr [%]
        Fr = np.where(qn_kpa > 0.1, (fs / qn_kpa) * 100.0, 0.1)
        Fr = np.clip(Fr, 0.01, 100.0)

        # Pore pressure ratio Bq [-]
        Bq = np.where(qn_kpa > 0.1, (u2_kpa - u0) / qn_kpa, 0.0)

        # Soil Behavior Type Index Ic (Robertson & Wride 1998 / Robertson 2009)
        log_Qt = np.log10(Qt)
        log_Fr = np.log10(Fr)
        Ic = np.sqrt(np.maximum((3.47 - log_Qt)**2 + (log_Fr + 1.22)**2, 0.0))

        # SBT classification lookup
        sbt_names = []
        sbt_zones = []
        for ic_val in Ic:
            matched = False
            for ic_min, ic_max, zone, name in SBT_ZONES_IC:
                if ic_min <= ic_val < ic_max:
                    sbt_zones.append(zone)
                    sbt_names.append(name)
                    matched = True
                    break
            if not matched:
                if ic_val >= 3.60:
                    sbt_zones.append(2)
                    sbt_names.append("Organic Soils - Peat")
                else:
                    sbt_zones.append(7)
                    sbt_names.append("Gravelly Sand to Dense Sand")

        derived = pd.DataFrame({
            "depth": z,
            "qc_mpa": qc,
            "fs_kpa": fs,
            "u2_kpa": u2,
            "qt_mpa": qt_mpa,
            "qn_kpa": qn_kpa,
            "sigma_v0_kpa": sigma_v0,
            "sigma_v0_eff_kpa": sigma_v0_eff,
            "u0_kpa": u0,
            "Qt": Qt,
            "Fr_pct": Fr,
            "Bq": Bq,
            "Ic": Ic,
            "SBT_zone": sbt_zones,
            "SBT_description": sbt_names
        })

        self.derived_data = derived
        return derived

    def get_summary_at_depth(self, z: float) -> Dict[str, Any]:
        """Fetch exact or interpolated CPT measurements and derived parameters at depth z [m]."""
        if self.derived_data.empty:
            self.calculate_normalized_parameters()

        df = self.derived_data
        if df.empty or "depth" not in df.columns:
            return {}

        # Find closest depth row
        idx = (df["depth"] - z).abs().idxmin()
        row = df.loc[idx]

        return {
            "sounding_id": self.sounding_id,
            "depth_m": float(row["depth"]),
            "qc_mpa": float(row["qc_mpa"]),
            "fs_kpa": float(row["fs_kpa"]),
            "u2_kpa": float(row["u2_kpa"]),
            "qt_mpa": float(row["qt_mpa"]),
            "Qt": float(row["Qt"]),
            "Fr_pct": float(row["Fr_pct"]),
            "Bq": float(row["Bq"]),
            "Ic": float(row["Ic"]),
            "sbt_zone": int(row["SBT_zone"]),
            "sbt_description": str(row["SBT_description"])
        }

    def derive_soil_parameters(
        self,
        z: float,
        Nkt: float = 15.0
    ) -> Dict[str, Any]:
        """
        Derives authoritative geotechnical design parameters at depth z [m]:
        - Undrained shear strength: su = (qt - sigma_v0) / Nkt [kPa] (fine-grained, Ic > 2.60)
        - Effective friction angle: phi' = 17.6 + 11.0 * log10(Qt) [deg] (coarse-grained, Robertson & Campanella 1983)
        - Relative density: Dr = sqrt(Qt / 305) * 100 [%] (coarse-grained, Jamiolkowski et al. 2003)
        - Small-strain shear modulus: Gmax = 0.0188 * 10^(0.55*Ic + 1.68) * (qt - sigma_v0) [kPa] (Robertson 2009)
        """
        pt = self.get_summary_at_depth(z)
        if not pt:
            return {}

        ic = pt["Ic"]
        qt_kpa = pt["qt_mpa"] * 1000.0
        qn_kpa = pt["qt_mpa"] * 1000.0 - pt.get("sigma_v0_kpa", 18.5 * z)
        qt_norm = pt["Qt"]
        is_clay = ic > 2.60

        derived_params: Dict[str, Any] = {
            "depth_m": z,
            "sounding_id": self.sounding_id,
            "Ic": ic,
            "sbt_description": pt["sbt_description"]
        }

        if is_clay:
            # Fine-grained correlation
            su = max(1.0, qn_kpa / Nkt)
            derived_params["su_kpa"] = round(su, 1)
            derived_params["method_su"] = f"Cone net resistance with Nkt = {Nkt}"
            derived_params["phi_eff_deg"] = 0.0
            derived_params["Dr_pct"] = None
        else:
            # Coarse-grained correlations
            phi_eff = min(45.0, max(28.0, 17.6 + 11.0 * np.log10(max(1.0, qt_norm))))
            Dr = min(100.0, max(0.0, np.sqrt(max(0.0, qt_norm) / 305.0) * 100.0))
            derived_params["phi_eff_deg"] = round(phi_eff, 1)
            derived_params["Dr_pct"] = round(Dr, 1)
            derived_params["method_phi"] = "Robertson & Campanella (1983) / Kulhawy & Mayne (1990)"
            derived_params["method_Dr"] = "Jamiolkowski et al. (2003)"
            derived_params["su_kpa"] = None

        # Small strain shear modulus Gmax [kPa] (Robertson 2009)
        alpha_g = 0.0188 * (10.0 ** (0.55 * ic + 1.68))
        Gmax = alpha_g * max(10.0, qn_kpa)
        derived_params["Gmax_kpa"] = round(Gmax, 1)
        derived_params["method_Gmax"] = "Robertson (2009) SBT-based Gmax formulation"

        return derived_params

    def to_compact_summary(self, max_layers: int = 8) -> str:
        """
        Creates a high-density tabular summary of interpreted stratigraphy layers
        from the CPT sounding. Ideal for local SLM context injection.
        """
        if self.derived_data.empty:
            self.calculate_normalized_parameters()

        df = self.derived_data
        if df.empty:
            return f"CPT Sounding '{self.sounding_id}': No data."

        lines = [
            f"### CPT SOUNDING SUMMARY: {self.sounding_id}",
            f"- Total Depth: {self.total_depth:.2f} m | Average Interval: {self.depth_interval:.3f} m",
            "\n| Depth Interval [m] | Mean qc [MPa] | Mean Ic | SBT Classification | Typical Parameters |",
            "|---|---|---|---|---|"
        ]

        # Discretize into homogeneous strata by SBT zone changes
        # Group contiguous SBT zones
        sbt_series = df["SBT_zone"]
        change_mask = sbt_series != sbt_series.shift()
        group_ids = change_mask.cumsum()

        strata = []
        for g_id, group in df.groupby(group_ids):
            z_top = float(group["depth"].min())
            z_bot = float(group["depth"].max())
            mean_qc = float(group["qc_mpa"].mean())
            mean_ic = float(group["Ic"].mean())
            sbt_desc = group["SBT_description"].iloc[0]
            strata.append({
                "z_top": z_top,
                "z_bot": z_bot,
                "mean_qc": mean_qc,
                "mean_ic": mean_ic,
                "sbt": sbt_desc,
                "thickness": z_bot - z_top
            })

        # Filter strata thinner than 0.2m unless few layers
        if len(strata) > max_layers:
            strata = [s for s in strata if s["thickness"] >= 0.2][:max_layers]

        for s in strata:
            z_str = f"{s['z_top']:.1f} - {s['z_bot']:.1f}"
            param_snippet = f"su ~ {s['mean_qc']*1000/15:.0f} kPa" if s['mean_ic'] > 2.6 else f"phi' ~ {17.6 + 11*np.log10(max(1, s['mean_qc']*1000/100)):.1f}°"
            lines.append(f"| {z_str} | {s['mean_qc']:.2f} | {s['mean_ic']:.2f} | {s['sbt']} | {param_snippet} |")

        return "\n".join(lines)
