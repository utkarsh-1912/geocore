# Author: Utkarsh Gupta
# License: GPL v3
"""
AGS 3.1 & 4.0 Geotechnical Data Ingestion and Structured Query Engine.
Parses industry-standard AGS files into clean relational dataframes (PROJ, HOLE,
GEOL, ISPT, DCPT, SAMP, DETL) and exposes compact query tools for the SLM agent.
"""

from typing import Dict, Any, List, Optional
import io
import re
import pandas as pd
import numpy as np

from core.geoai.cpt import CPTSounding
from core.geoai.spt import SPTRecord


class AGSProjectDataset:
    """
    Structured representation of an ingested AGS (Association of Geotechnical
    and Geoenvironmental Specialists) dataset.
    """
    def __init__(self, filename: str = "dataset.ags"):
        self.filename = filename
        self.groups: Dict[str, pd.DataFrame] = {}
        self.project_info: Dict[str, Any] = {}

    @classmethod
    def parse_ags_text(cls, ags_text: str, filename: str = "dataset.ags") -> "AGSProjectDataset":
        """
        Parses raw AGS 3.1/4.0 text deterministically into structured group DataFrames.
        """
        dataset = cls(filename=filename)
        current_group: Optional[str] = None
        group_headers: List[str] = []
        group_rows: List[List[str]] = []

        lines = ags_text.splitlines()

        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue

            # Check for group definition line: "GROUP","<NAME>"
            if line_str.startswith('"GROUP"') or line_str.startswith('GROUP'):
                # Save previous group if exists
                if current_group and group_headers and group_rows:
                    df = pd.DataFrame(group_rows, columns=group_headers)
                    dataset.groups[current_group] = df

                parts = [p.strip().strip('"') for p in line_str.split(',')]
                current_group = parts[1] if len(parts) > 1 else "UNKNOWN"
                group_headers = []
                group_rows = []
                continue

            # Check for header line: "HEADING","<COL1>","<COL2>"
            if line_str.startswith('"HEADING"') or line_str.startswith('HEADING'):
                parts = [p.strip().strip('"') for p in line_str.split(',')]
                group_headers = parts[1:]
                continue

            # Skip unit/type definition lines: "UNIT", "TYPE"
            if line_str.startswith('"UNIT"') or line_str.startswith('UNIT') or \
               line_str.startswith('"TYPE"') or line_str.startswith('TYPE'):
                continue

            # Check for data line: "DATA","<VAL1>","<VAL2>"
            if line_str.startswith('"DATA"') or line_str.startswith('DATA'):
                parts = [p.strip().strip('"') for p in line_str.split(',')]
                data_vals = parts[1:]
                # Pad or slice to match headers
                if len(data_vals) < len(group_headers):
                    data_vals.extend([''] * (len(group_headers) - len(data_vals)))
                group_rows.append(data_vals[:len(group_headers)])

        # Save final group
        if current_group and group_headers and group_rows:
            df = pd.DataFrame(group_rows, columns=group_headers)
            dataset.groups[current_group] = df

        # Parse project metadata from PROJ group if available
        if "PROJ" in dataset.groups and not dataset.groups["PROJ"].empty:
            proj_df = dataset.groups["PROJ"]
            dataset.project_info = proj_df.iloc[0].to_dict()

        return dataset

    def list_boreholes(self) -> List[Dict[str, Any]]:
        """List all exploratory locations / boreholes in the dataset."""
        if "HOLE" not in self.groups:
            return []
        
        df = self.groups["HOLE"]
        holes = []
        for _, row in df.iterrows():
            hole_id = row.get("HOLE_ID", row.get("LOCA_ID", "Unknown"))
            holes.append({
                "hole_id": hole_id,
                "type": row.get("HOLE_TYPE", row.get("LOCA_TYPE", "Borehole")),
                "final_depth_m": float(row.get("HOLE_FDEP", row.get("LOCA_FDEP", 0.0)) or 0.0),
                "ground_level_m": float(row.get("HOLE_GL", row.get("LOCA_GL", 0.0)) or 0.0),
                "easting": row.get("HOLE_NATX", row.get("LOCA_NATE", None)),
                "northing": row.get("HOLE_NATY", row.get("LOCA_NATN", None)),
            })
        return holes

    def get_stratigraphy_for_hole(self, hole_id: str) -> List[Dict[str, Any]]:
        """Retrieve geological strata sequence for a given borehole."""
        if "GEOL" not in self.groups:
            return []

        df = self.groups["GEOL"]
        id_col = "HOLE_ID" if "HOLE_ID" in df.columns else "LOCA_ID"
        hole_df = df[df[id_col].astype(str).str.upper() == str(hole_id).upper()]

        strata = []
        for idx, row in hole_df.iterrows():
            top = float(row.get("GEOL_TOP", 0.0) or 0.0)
            base = float(row.get("GEOL_BASE", 0.0) or 0.0)
            desc = row.get("GEOL_DESC", row.get("GEOL_LEG", "Soil Layer"))
            code = row.get("GEOL_GEOL", row.get("GEOL_CODE", ""))
            strata.append({
                "layer": len(strata) + 1,
                "depth_from_m": top,
                "depth_to_m": base,
                "description": desc,
                "geol_code": code,
                "thickness_m": round(base - top, 2)
            })
        return strata

    def get_spt_for_hole(self, hole_id: str) -> List[Dict[str, Any]]:
        """Retrieve in-situ SPT records for a specific borehole."""
        if "ISPT" not in self.groups:
            return []

        df = self.groups["ISPT"]
        id_col = "HOLE_ID" if "HOLE_ID" in df.columns else "LOCA_ID"
        hole_df = df[df[id_col].astype(str).str.upper() == str(hole_id).upper()]

        records = []
        for _, row in hole_df.iterrows():
            try:
                depth = float(row.get("ISPT_TOP", row.get("ISPT_DPTH", 0.0)) or 0.0)
                raw_n_str = str(row.get("ISPT_NVAL", row.get("ISPT_MAIN", "0"))).strip()
                # Handle refusal cases e.g. >50
                raw_n = int(re.sub(r'[^0-9]', '', raw_n_str) or 0)
                
                spt_rec = SPTRecord(borehole_id=hole_id, depth=depth, raw_n=raw_n)
                correlations = spt_rec.correlate_granular_properties()
                records.append(correlations)
            except Exception:
                continue

        return records

    def to_compact_summary(self) -> str:
        """High-density summary of the AGS dataset for SLM prompt context."""
        holes = self.list_boreholes()
        proj_name = self.project_info.get("PROJ_NAME", self.project_info.get("PROJ_ID", "AGS Investigation"))
        
        lines = [
            f"### AGS PROJECT INVESTIGATION: {proj_name}",
            f"- Source File: `{self.filename}` | Total Exploratory Locations: {len(holes)}",
            "\n| Location ID | Type | Final Depth [m] | Strata Layers | In-Situ SPTs |",
            "|---|---|---|---|---|"
        ]

        for h in holes[:10]:
            h_id = h["hole_id"]
            strata_count = len(self.get_stratigraphy_for_hole(h_id))
            spt_count = len(self.get_spt_for_hole(h_id))
            lines.append(f"| {h_id} | {h['type']} | {h['final_depth_m']:.1f} | {strata_count} layers | {spt_count} tests |")

        return "\n".join(lines)
