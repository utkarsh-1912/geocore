"""
Project CPT retrieval + CPT-based pile capacity tools (AGENTS.md §9, §16-18, §25, §28-29).

Deterministic oracles:
- Groundhog classes called directly with the same inputs (results must match);
- Groundhog v0.15.0's own published test values (tests/deepfoundations/test_koppejan.py and
  test_debeer.py, data copied to tests/data/groundhog_*.csv):
  Koppejan D=0.4 m, tip 16.5 m, alpha_s=0.01, alpha_p=1 -> Frs = 1132 kN, Frb = 1404 kN;
  De Beer D=0.4 m, tip 16 m, alpha_s=0.6, alpha_b=1 -> Rs = 1313.1, Rb = 2800.4, Rc = 4113.5 kN.
"""
import json
import math
import os
import warnings

import numpy as np
import pandas as pd
import pytest

import core.geoai.tool_definitions  # noqa: F401  (registers curated tools incl. tools_cpt_piles)
import core.geoai.tools_cpt_piles as T
from core.geoai import cpt_pile_capacity as engine
from core.geoai import project_cpt
from core.geoai.exceptions import GeoAIValidationError
from core.geoai.schemas.cpt_piles import GeoAIMissingParameterError
from core.geoai.tool_registry import tool_registry

warnings.filterwarnings("ignore")
DATA = os.path.join(os.path.dirname(__file__), "data")
PILE_TOOL = "calculate_pile_capacity_from_cpt"


class FakeStore:
    """Same read interface as core.state.StateManager (list_by_type / get)."""

    def __init__(self, objects):
        self.objects = objects  # id -> (type, name, obj)

    def list_by_type(self, type_name):
        return [{"id": k, "type": t, "name": n} for k, (t, n, _) in self.objects.items()]

    def get(self, obj_id):
        return self.objects[obj_id][2]


def synthetic_cpt(dz=0.1, z_max=14.0):
    """Sand 0-2 m, soft clayey silt 2-7 m, sand below (qc [MPa], fs [kPa], u2 [kPa])."""
    z = np.round(np.arange(dz, z_max + 1e-9, dz), 3)
    qc = np.where(z < 2, 4.0, np.where(z < 7, 0.8 + 0.04 * z, 12.0 + 0.6 * (z - 7)))
    fs = np.where(z < 2, 35.0, np.where(z < 7, 22.0, 90.0))
    u2 = np.where(z < 2, 0.0, np.where(z < 7, 150.0, 40.0))
    return pd.DataFrame({"z [m]": z, "qc [MPa]": qc, "fs [kPa]": fs, "u2 [kPa]": u2})


def load_fixture(name):
    return pd.read_csv(os.path.join(DATA, name), comment="#")


@pytest.fixture
def store(monkeypatch):
    def install(objects):
        s = FakeStore(objects)
        monkeypatch.setattr(T, "_store", lambda: s)
        return s
    return install


def invoke(name, **args):
    res = tool_registry.invoke_tool(name, args)
    res.pop("_provenance", None)
    return res


# ------------------------------------------------------------------ registration & schema

def test_tools_registered_with_metadata_and_units():
    from core.geoai.tool_metadata import TOOL_METADATA
    for name in ("list_project_cpts", "get_cpt_summary", PILE_TOOL):
        assert tool_registry.get_tool(name) is not None
        assert name in TOOL_METADATA
    schema = tool_registry.get_tool(PILE_TOOL).input_model.model_json_schema()
    props = schema["properties"]
    assert set(schema["required"]) >= {"cpt_id", "method", "pile_type", "pile_diameter_m", "pile_tip_depth_m"}
    assert props["pile_diameter_m"]["unit"] == "m" and props["wall_thickness_mm"]["unit"] == "mm"
    assert set(props["method"]["enum"]) == {"lcpc", "koppejan", "debeer"}
    assert TOOL_METADATA[PILE_TOOL]["output_units"]["ultimate_total_resistance_kn"] == "kN"


def test_schema_fields_match_tool_signatures():
    import inspect
    for name in ("list_project_cpts", "get_cpt_summary", PILE_TOOL):
        tool = tool_registry.get_tool(name)
        params = set(inspect.signature(tool.func).parameters)
        assert params == set(tool.input_model.model_fields), name


def test_raw_groundhog_pile_classes_stay_hidden():
    from core.geoai.exposure_policy import is_model_exposed
    for cls in ("LCPCAxcapCalculation", "KoppejanCalculation", "DeBeerCalculation", "AxCapCalculation", "PCPTProcessing"):
        assert not is_model_exposed(cls)


# ------------------------------------------------------------------ project CPT access

def test_list_project_cpts_reads_workspace_structures(store):
    two = pd.concat([synthetic_cpt().assign(**{"CPT ID": "CPT-01"}),
                     synthetic_cpt(z_max=10).assign(**{"CPT ID": "CPT-02"})], ignore_index=True)
    from groundhog.siteinvestigation.insitutests.pcpt_processing import PCPTProcessing
    pcpt = PCPTProcessing(title="CPT-05")
    cpt5 = synthetic_cpt()
    pcpt.data = pd.DataFrame({"z [m]": cpt5["z [m]"], "qc [MPa]": cpt5["qc [MPa]"],
                              "fs [MPa]": cpt5["fs [kPa]"] / 1000.0, "u2 [MPa]": cpt5["u2 [kPa]"] / 1000.0})
    layered = pd.DataFrame({"Depth from [m]": [0, 3], "Depth to [m]": [3, 8], "Soil type": ["Sand", "Clay"]})
    no_unit = pd.DataFrame({"depth": [0.1, 0.2], "qc": [1.0, 2.0]})
    store({"a": ("SoilProfile", "site_cpts.xlsx", two), "b": ("PCPTProcessing", "PCPT_x", pcpt),
           "c": ("SoilProfile", "BH layers", layered), "d": ("SoilProfile", "CPT-09.csv", no_unit)})
    out = invoke("list_project_cpts")
    ids = [c["cpt_id"] for c in out["cpts"]]
    assert ids == ["CPT-01", "CPT-02", "CPT-05"] and out["count"] == 3
    assert out["cpts"][1]["depth_range_m"] == [0.1, 10.0]
    assert out["cpts"][2]["channels"] == ["qc", "fs", "u2"]
    assert len(out["unusable_sources"]) == 1 and "no unit" in out["unusable_sources"][0]["reason"]
    assert "CPT-09" in out["unusable_sources"][0]["source"]
    # PCPTProcessing fs [MPa] -> kPa deterministic conversion
    assert project_cpt.resolve_cpt("cpt 5", T._store()).data["fs_kpa"].iloc[-1] == pytest.approx(90.0)


def test_empty_project_explains_how_to_load_cpts(store):
    store({})
    out = invoke("list_project_cpts")
    assert out["count"] == 0 and "qc [MPa]" in out["note"]


def test_real_state_manager_upload_name_resolves(tmp_path, monkeypatch):
    from core.state import StateManager
    from groundhog.general.soilprofile import SoilProfile
    sm = StateManager()
    sm.filename = str(tmp_path / "saved_objects.json")
    sm._loaded = True
    sm.store(SoilProfile(synthetic_cpt()), "SoilProfile", name="CPT-03.xlsx")
    monkeypatch.setattr(T, "_store", lambda: sm)
    for key in ("CPT-03", "cpt 3", "CPT_003"):
        assert project_cpt.resolve_cpt(key, sm).cpt_id == "CPT-03"


def test_ags_scpt_group_is_read_with_units_and_location(store, tmp_path):
    from groundhog.general.agsconversion import AGSConverter
    rows = "\n".join(f'"DATA","CPT-07","1","{z:.2f}","{q * 1000:.0f}","{f:.0f}","{u:.0f}"'
                     for z, q, f, u in synthetic_cpt(dz=0.5, z_max=6).to_numpy())
    text = ('"GROUP","LOCA"\n"HEADING","LOCA_ID","LOCA_TYPE","LOCA_NATE","LOCA_NATN","LOCA_GL"\n'
            '"UNIT","","","m","m","m"\n"TYPE","ID","PA","2DP","2DP","2DP"\n'
            '"DATA","CPT-07","CP","1000.00","2000.00","5.00"\n\n'
            '"GROUP","SCPT"\n"HEADING","LOCA_ID","SCPG_TESN","SCPT_DPTH","SCPT_RES","SCPT_FRES","SCPT_PWP2"\n'
            '"UNIT","","","m","kPa","kPa","kPa"\n"TYPE","ID","X","2DP","2DP","0DP","0DP"\n' + rows + "\n\n")
    path = tmp_path / "site.ags"
    path.write_text(text)
    conv = AGSConverter(str(path))
    conv.extract_groupnames()
    store({"g": ("AGSConverter", "site.ags", conv)})
    cpt = project_cpt.resolve_cpt("CPT-07", T._store())
    # SCPT_RES given in kPa in this file -> converted to MPa
    assert cpt.data["qc_mpa"].iloc[0] == pytest.approx(4.0) and cpt.data["fs_kpa"].iloc[0] == 35.0
    assert cpt.location == {"easting": 1000.0, "northing": 2000.0, "ground_level": 5.0}


def test_cpt_not_found_lists_available(store):
    store({"a": ("SoilProfile", "CPT-01", synthetic_cpt())})
    with pytest.raises(GeoAIValidationError) as e:
        invoke("get_cpt_summary", cpt_id="CPT-04")
    assert "CPT-01" in e.value.message and e.value.errors[0]["type"] == "cpt_not_found"


def test_cpt_summary_layering_flags_and_provenance(store):
    df = synthetic_cpt()
    df.loc[5, "qc [MPa]"] = -0.1                                       # negative reading
    df = df[(df["z [m]"] < 9.0) | (df["z [m]"] > 10.0)]                # gap 9-10 m
    df = df.assign(**{"qc [kPa]": df["qc [MPa]"] * 1000.0}).drop(columns=["qc [MPa]", "u2 [kPa]"])
    store({"a": ("SoilProfile", "CPT-03.xlsx", df)})
    out = invoke("get_cpt_summary", cpt_id="CPT-03", max_intervals=4)
    lay = out["layering"]
    assert 1 <= len(lay) <= 4
    assert lay[0]["depth_from_m"] == 0.0 and lay[-1]["depth_to_m"] == 14.0
    assert all(a["depth_to_m"] == b["depth_from_m"] for a, b in zip(lay, lay[1:]))
    sand = lay[-1]
    assert sand["sbt_zone"] in (6, 7) and sand["qc_mpa"]["max"] == pytest.approx(16.2)  # kPa -> MPa
    assert "u2_kpa" not in sand and set(out["channels"]) == {"qc", "fs"}
    flags = " ".join(out["data_quality_flags"])
    assert "u2 channel missing" in flags and "negative qc" in flags and "gap" in flags
    prov = out["provenance"]
    assert prov["source"]["columns"]["qc"] == "qc [kPa]" and prov["source"]["object_name"] == "CPT-03.xlsx"
    assert "Robertson" in prov["interpretation"]
    assert len(json.dumps(out)) < 4000                                  # compact, no raw arrays


# ------------------------------------------------------------------ missing / invalid inputs

def test_missing_inputs_give_structured_error_with_units(store):
    with pytest.raises(GeoAIMissingParameterError) as e:
        invoke(PILE_TOOL, cpt_id="CPT-03", method="lcpc")
    fields = {d["field"]: d["unit"] for d in e.value.errors}
    assert fields == {"pile_type": "-", "pile_diameter_m": "m", "pile_tip_depth_m": "m"}
    assert "pile_diameter_m [m]" in e.value.message and "do not assume" in e.value.message


def test_open_ended_and_debeer_extra_requirements(store):
    with pytest.raises(GeoAIMissingParameterError) as e:
        invoke(PILE_TOOL, cpt_id="CPT-03", method="De Beer", pile_type="open ended steel pipe",
               pile_diameter_m=0.6, pile_tip_depth_m=10)
    assert {d["field"] for d in e.value.errors} == {"wall_thickness_mm", "open_end_condition",
                                                    "debeer_alpha_s", "debeer_alpha_b"}


def test_debeer_needs_groundwater_when_not_stored(store):
    store({"a": ("SoilProfile", "CPT-03", synthetic_cpt())})
    with pytest.raises(GeoAIMissingParameterError) as e:
        invoke(PILE_TOOL, cpt_id="CPT-03", method="debeer", pile_type="driven_precast_concrete",
               pile_diameter_m=0.4, pile_tip_depth_m=10, debeer_alpha_s=0.6, debeer_alpha_b=1.0)
    assert e.value.errors[0]["field"] == "groundwater_depth_m" and e.value.errors[0]["unit"] == "m"


def test_no_fs_requires_explicit_layers(store):
    store({"a": ("SoilProfile", "CPT-03", synthetic_cpt()[["z [m]", "qc [MPa]"]])})
    with pytest.raises(GeoAIMissingParameterError) as e:
        invoke(PILE_TOOL, cpt_id="CPT-03", method="koppejan", pile_type="cfa", pile_diameter_m=0.5,
               pile_tip_depth_m=8)
    assert e.value.errors[0]["field"] == "soil_layers"


def test_tip_below_cpt_and_insufficient_data_below_tip(store):
    store({"a": ("SoilProfile", "CPT-03", synthetic_cpt())})
    base = dict(cpt_id="CPT-03", method="koppejan", pile_type="cfa", pile_diameter_m=0.5)
    with pytest.raises(GeoAIValidationError) as e:
        invoke(PILE_TOOL, pile_tip_depth_m=15.0, **base)
    assert e.value.errors[0]["type"] == "tip_below_cpt"
    with pytest.raises(GeoAIValidationError) as e:
        invoke(PILE_TOOL, pile_tip_depth_m=12.5, **base)           # needs 12.5 + 4 x 0.5 = 14.5 m > 14.0 m
    assert e.value.errors[0]["type"] == "insufficient_cpt_below_tip" and e.value.errors[0]["required_to_m"] == 14.5


def test_method_pile_type_incompatibility(store):
    store({"a": ("SoilProfile", "CPT-03", synthetic_cpt())})
    with pytest.raises(GeoAIValidationError) as e:
        invoke(PILE_TOOL, cpt_id="CPT-03", method="lcpc", pile_type="driven_open_steel_pipe", pile_diameter_m=0.6,
               pile_tip_depth_m=9, wall_thickness_mm=20, open_end_condition="coring")
    assert e.value.errors[0]["type"] == "method_pile_incompatible"
    with pytest.raises(GeoAIValidationError, match="at least 0.2 m"):
        invoke(PILE_TOOL, cpt_id="CPT-03", method="lcpc", pile_type="cfa", pile_diameter_m=0.15, pile_tip_depth_m=9)


def test_unit_strings_are_converted(store):
    store({"a": ("SoilProfile", "CPT-03", synthetic_cpt())})
    res = invoke(PILE_TOOL, cpt_id="CPT-03", method="koppejan", pile_type="driven_open_steel_pipe",
                 pile_diameter_m="500 mm", pile_tip_depth_m="1000 cm", wall_thickness_mm="0.02 m",
                 open_end_condition="coring")
    assert res["pile"]["diameter_m"] == 0.5 and res["pile"]["tip_depth_m"] == 10.0
    assert res["pile"]["wall_thickness_mm"] == pytest.approx(20.0)
    assert res["base_details"]["base_area_m2"] == pytest.approx(round(0.25 * math.pi * (0.5 ** 2 - 0.46 ** 2), 4))


# ------------------------------------------------------------------ deterministic oracles

KOPPEJAN_LAYERS = [
    {"depth_from_m": a, "depth_to_m": b, "total_unit_weight_kn_m3": g}
    for a, b, g in zip([0, 3, 7, 14, 18.2, 21.3], [3, 7, 14, 18.2, 21.3, 22], [17, 20, 18, 20, 20, 20])]


def test_koppejan_matches_groundhog_direct_and_published_values(store):
    from groundhog.deepfoundations.axialcapacity.koppejan import KoppejanCalculation
    data = load_fixture("groundhog_cpt_koppejan.csv")
    store({"a": ("SoilProfile", "KOP-1", data)})
    res = invoke(PILE_TOOL, cpt_id="KOP-1", method="koppejan", pile_type="driven_closed_steel_pipe",
                 pile_diameter_m=0.4, pile_tip_depth_m=16.5, soil_layers=KOPPEJAN_LAYERS)
    direct = KoppejanCalculation(depth=data["z [m]"], qc=data["qc [MPa]"], diameter=0.4, penetration=16.5)
    direct.set_layer_properties(layer_data=pd.DataFrame({
        "Depth from [m]": [0, 3, 7, 14, 18.2, 21.3], "Depth to [m]": [3, 7, 14, 18.2, 21.3, 22],
        "Total unit weight [kN/m3]": [17, 20, 18, 20, 20, 20]}))
    direct.calculate_side_friction(alpha_s=0.01)
    direct.calculate_base_resistance(alpha_p=1)
    assert res["ultimate_shaft_resistance_kn"] == round(direct.Frs, 1)
    assert res["ultimate_base_resistance_kn"] == round(direct.Frb, 1)
    # Groundhog's own test values (test_koppejan.py)
    assert res["ultimate_shaft_resistance_kn"] == pytest.approx(1132, abs=0.5)
    assert res["ultimate_base_resistance_kn"] == pytest.approx(1404, abs=0.5)
    assert res["base_details"]["qcII_mpa"] == pytest.approx(16.13, abs=0.005)
    assert res["method_factors"]["alpha_s"] == 0.01 and res["method_factors"]["alpha_p"] == 1.0
    assert sum(r["shaft_resistance_kn"] for r in res["shaft_breakdown"]) == pytest.approx(
        res["ultimate_shaft_resistance_kn"], abs=0.5)


def test_debeer_matches_groundhog_published_values(store):
    from groundhog.deepfoundations.axialcapacity.debeer import DeBeerCalculation
    from groundhog.general.soilprofile import SoilProfile
    data = load_fixture("groundhog_debeer_example.csv")
    store({"a": ("SoilProfile", "DB-1", data)})
    layers = [{"depth_from_m": a, "depth_to_m": b, "soil_type": t}
              for a, b, t in zip([0, 3, 6, 15], [3, 6, 15, 20], ["Sand", "Clay", "Sand", "Loam (silt)"])]
    res = invoke(PILE_TOOL, cpt_id="DB-1", method="debeer", pile_type="driven_precast_concrete",
                 pile_diameter_m=0.4, pile_tip_depth_m=16, groundwater_depth_m=0.0,
                 debeer_alpha_s=0.6, debeer_alpha_b=1.0, soil_layers=layers)
    # Groundhog's own test values (test_debeer.py)
    assert res["ultimate_shaft_resistance_kn"] == pytest.approx(1313.1, abs=0.05)
    assert res["ultimate_base_resistance_kn"] == pytest.approx(2800.4, abs=0.05)
    assert res["ultimate_total_resistance_kn"] == pytest.approx(4113.5, abs=0.05)
    calc = DeBeerCalculation(depth=data["z [m]"], qc=data["qc [MPa]"], diameter_pile=0.4, diameter_cone=0.0357)
    calc.resample_data()
    calc.set_soil_layers(soilprofile=SoilProfile({"Depth from [m]": [0, 3, 6, 15], "Depth to [m]": [3, 6, 15, 20],
                                                  "Soil type": ["Sand", "Clay", "Sand", "Loam (silt)"]}))
    calc.calculate_base_resistance()
    calc.correct_shaft_qc(cone_type="U")
    calc.calculate_average_qc()
    calc.calculate_unit_shaft_friction()
    calc.set_shaft_base_factors(1.0, 1.0, 0.6, 0.6)
    calc.calculate_pile_resistance(pile_penetration=16, base_area=0.25 * np.pi * 0.4 ** 2, circumference=np.pi * 0.4)
    assert res["ultimate_base_resistance_kn"] == round(calc.Rb, 1)
    if abs(calc.Rs - 1313.1) > 0.05:          # pandas >= 3: Groundhog's tip truncation is a no-op
        assert any("pandas 3" in w for w in res["warnings"])
    assert res["shaft_breakdown"][-1]["depth_to_m"] == 16.0


def _lcpc_direct(depth, qc, layering, water_level, tip, d, gb, gs):
    from groundhog.deepfoundations.axialcapacity.lcpc import LCPCAxcapCalculation
    from groundhog.general.soilprofile import SoilProfile
    lay = layering.copy()
    lay["Total unit weight [kN/m3]"] = lay.get("Total unit weight [kN/m3]", 18.5)
    lay["Ignore shaft friction"] = False
    calc = LCPCAxcapCalculation(depth=np.asarray(depth), qc=np.asarray(qc), diameter_pile=d, group_base=gb, group_shaft=gs)
    calc.set_soil_layers(soilprofile=SoilProfile(lay), water_level=water_level)
    calc.qca_calculation()
    calc.calculate_base_resistance()
    calc.calculate_shaft_resistance()
    return calc.get_axialpileresistance(pile_penetration=tip)


def test_lcpc_matches_groundhog_direct_on_full_cpt_with_sbt_layering(store):
    df = synthetic_cpt(dz=0.2)
    store({"a": ("SoilProfile", "CPT-03", df)})
    res = invoke(PILE_TOOL, cpt_id="CPT-03", method="lcpc", pile_type="bored_support_fluid",
                 pile_diameter_m=0.6, pile_tip_depth_m=10.0, groundwater_depth_m=1.5)
    cpt = project_cpt.resolve_cpt("CPT-03", T._store())
    layering, source, _ = engine.build_layering("lcpc", cpt, None, 1.5)
    assert "Robertson SBT" in res["soil_layering_source"] and source == res["soil_layering_source"]
    direct = _lcpc_direct(df["z [m]"], df["qc [MPa]"], layering, 1.5, 10.0, 0.6, "I", "IA")   # untruncated CPT
    assert res["ultimate_shaft_resistance_kn"] == round(direct["Rs [kN]"], 1)
    assert res["ultimate_base_resistance_kn"] == round(direct["Rb [kN]"], 1)
    assert res["method_factors"]["group_base"] == "I" and res["method_factors"]["group_shaft"] == "IA"
    assert len(res["shaft_breakdown"]) <= engine.MAX_BREAKDOWN_ROWS
    text = json.dumps(res).lower()
    assert len(text) < 6000 and " safe" not in text and "does not establish design adequacy" in text
    assert res["cpt_depth_range_m"] == [0.2, 14.0] and res["cpt_id"] == "CPT-03"
    assert res["provenance"]["cpt_source"]["columns"]["qc"] == "qc [MPa]"


def test_shaft_start_depth_and_compact_breakdown(store):
    store({"a": ("SoilProfile", "CPT-03", synthetic_cpt())})
    common = dict(cpt_id="CPT-03", method="koppejan", pile_type="driven_precast_concrete",
                  pile_diameter_m=0.4, pile_tip_depth_m=11.0)
    full = invoke(PILE_TOOL, **common)
    part = invoke(PILE_TOOL, shaft_start_depth_m=2.0, **common)
    assert part["ultimate_base_resistance_kn"] == full["ultimate_base_resistance_kn"]
    # oracle: Groundhog's cumulative shaft resistance Frs(z) at the tip minus at the shaft start
    from groundhog.deepfoundations.axialcapacity.koppejan import KoppejanCalculation
    cpt = project_cpt.resolve_cpt("CPT-03", T._store())
    layering, _, _ = engine.build_layering("koppejan", cpt, None, None)
    lay = layering.assign(**{"Total unit weight [kN/m3]": 18.5})
    direct = KoppejanCalculation(depth=cpt.data["depth_m"], qc=cpt.data["qc_mpa"], diameter=0.4, penetration=11.0)
    direct.set_layer_properties(layer_data=lay, waterlevel=0.0)
    direct.calculate_side_friction(alpha_s=0.01)
    frs_at_2 = np.interp(2.0, direct.data["z [m]"], direct.data["Frs [kN]"].fillna(0.0))
    assert full["ultimate_shaft_resistance_kn"] == round(direct.Frs, 1)
    assert part["ultimate_shaft_resistance_kn"] == round(direct.Frs - frs_at_2, 1)
    assert part["shaft_breakdown"][0]["depth_from_m"] == 2.0
    assert sum(r["shaft_resistance_kn"] for r in part["shaft_breakdown"]) == pytest.approx(
        part["ultimate_shaft_resistance_kn"], abs=0.3)
    many = [{"depth_from_m": i * 0.5, "depth_to_m": (i + 1) * 0.5} for i in range(28)]
    fine = invoke(PILE_TOOL, soil_layers=many, **common)
    assert len(fine["shaft_breakdown"]) <= 15


# ------------------------------------------------------------------ selector

@pytest.mark.parametrize("query,tool,k", [
    ("What is the capacity of a 0.6 m driven pile to 18 m at CPT-03?", PILE_TOOL, 3),
    ("Calculate the pile capacity from CPT-03 in the current project", PILE_TOOL, 3),
    ("axial pile resistance using LCPC for a bored pile at CPT-01", PILE_TOOL, 3),
    ("Koppejan base resistance for a 0.4 m closed-ended steel pipe pile at 16.5 m", PILE_TOOL, 3),
    ("shaft friction and end bearing of a CFA pile from the cone test", PILE_TOOL, 3),
    ("De Beer pile bearing capacity at CPT-04, 0.5 m precast pile", PILE_TOOL, 3),
    ("list the cone penetration tests available", "list_project_cpts", 3),
    ("which CPTs are in the project?", "list_project_cpts", 5),
    ("summarise CPT-03 layering and soil behaviour type", "get_cpt_summary", 3),
    ("what does CPT-02 show? any data quality issues?", "get_cpt_summary", 3),
])
def test_selector_ranks_cpt_tools(query, tool, k):
    from core.registry import registry  # noqa: F401  (auto-registered Groundhog tools compete too)
    from core.geoai import tool_selector as ts
    names = [n for n, _ in ts.rank_tools(query)[:k]]
    assert tool in names, names
