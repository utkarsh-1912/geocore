"""
The standard quantity directory (core/quantity_standard.json) stays consistent and in sync.

- every entry has a unit the directory knows, whose dimension matches the entry's;
- no two quantities claim the same parameter name;
- unit spellings found in the code base map to one canonical spelling;
- units shared with core.geoai.units (the conversion engine) agree on dimension;
- the generated audit report and the app's copy of the standard are up to date
  (regenerate with ``python -m core.quantity_directory``).
"""
import collections

from core import quantity_directory as qd
from core.geoai.units import UnitDimension, get_unit_dimension

STANDARD = qd.load_standard()
QUANTITIES = STANDARD["quantities"]

# Our dimension names for the ones core.geoai.units also models.
SHARED_DIMENSIONS = {
    "pressure": UnitDimension.PRESSURE, "unit_weight": UnitDimension.UNIT_WEIGHT, "length": UnitDimension.LENGTH,
    "angle": UnitDimension.ANGLE, "velocity": UnitDimension.VELOCITY, "force": UnitDimension.FORCE,
    "force_per_length": UnitDimension.FORCE_PER_LENGTH, "time": UnitDimension.TIME,
}


def test_ids_and_exact_keys_are_unique():
    ids = [q["id"] for q in QUANTITIES]
    assert len(ids) == len(set(ids))
    owners = collections.defaultdict(set)
    for q in QUANTITIES:
        for key in q["keys"]:
            owners[key].add(q["id"])
    assert {k: v for k, v in owners.items() if len(v) > 1} == {}


def test_every_entry_is_complete_and_dimensionally_consistent():
    for q in QUANTITIES:
        for field in ("id", "name", "symbol", "latex", "category", "dimension", "unit", "keys"):
            assert q.get(field), f"{q.get('id')}: missing {field}"
        assert q["unit"] in qd.UNIT_DIMENSION, f"{q['id']}: unknown unit {q['unit']}"
        assert qd.UNIT_DIMENSION[q["unit"]] == q["dimension"], q["id"]
        assert qd.canonical_unit(q["unit"]) == q["unit"], q["id"]


def test_unit_aliases_are_unambiguous():
    seen = {}
    for canonical, spellings in STANDARD["unit_aliases"].items():
        assert canonical in qd.UNIT_DIMENSION
        for spelling in [canonical, *spellings]:
            key = qd._norm_unit(spelling)
            assert seen.setdefault(key, canonical) == canonical, f"{spelling!r} maps to two units"


def test_spelling_variants_resolve_to_one_unit():
    assert qd.canonical_unit("pct") == qd.canonical_unit("Percent") == qd.canonical_unit("%") == "%"
    assert qd.canonical_unit("kN/m3") == qd.canonical_unit("kN_m3") == qd.canonical_unit("kN/m^3") == "kN/m³"
    assert qd.canonical_unit("m^2/yr") == qd.canonical_unit("m2/yr") == "m²/yr"
    assert qd.canonical_unit(":math:`kPa`") == "kPa"
    assert qd.canonical_unit("furlong") is None


def test_dimensions_agree_with_the_conversion_engine():
    for q in QUANTITIES:
        shared = SHARED_DIMENSIONS.get(q["dimension"])
        if shared is not None:
            engine_unit = q["unit"].replace("³", "3").replace("²", "2")
            assert get_unit_dimension(engine_unit) == shared, f"{q['id']} ({q['unit']})"


def test_lookup_distinguishes_names_that_differ_only_by_case():
    assert qd.lookup("qt")["id"] == "qt"
    assert qd.lookup("Qt")["id"] == "qt_norm"
    assert qd.lookup("sigma_vo_eff")["id"] == "sigma_v_eff"
    assert qd.lookup("sigma_vo")["id"] == "sigma_v_total"
    assert qd.lookup("Vs")["id"] == "vs"
    assert qd.lookup("no_such_parameter") is None


def test_audit_reports_and_never_mutates():
    result = qd.audit([
        {"function": "f", "module": "m", "role": "input", "key": "relative_density", "label": "", "symbol": "", "unit_raw": "pct", "source": "t"},
        {"function": "f", "module": "m", "role": "input", "key": "depth", "label": "", "symbol": "", "unit_raw": "kPa", "source": "t"},
        {"function": "f", "module": "m", "role": "input", "key": "mystery", "label": "", "symbol": "", "unit_raw": None, "source": "t"},
    ])
    assert result["findings"]["percent_vs_fraction"] == ["f.relative_density [relative_density]: documented %, standard -"]
    assert any("depth" in item for item in result["findings"]["dimension_mismatch"])
    assert result["unmatched"][0]["key"] == "mystery"


def test_generated_files_are_up_to_date():
    assert qd.main(["--check"]) == 0, "run `python -m core.quantity_directory` and commit the result"


def test_function_unit_wins_over_the_standard():
    # relativedensity_spt_kulhawymayne documents Dr as a fraction/percent pair; water content in the
    # cyclic strength function is documented in %: the function's unit is shown, never the standard one.
    assert qd.resolve("watercontent_voidratio", "water_content")["unit"] == "-"
    recorded = qd.load_function_units()
    assert recorded["cyclicstrength_dsssand_watercontent"]["water_content"] == "%"
    resolved = qd.resolve("cyclicstrength_dsssand_watercontent", "water_content")
    assert (resolved["unit"], resolved["unit_source"]) == ("%", "function")
    # An explicitly documented unit beats everything, including a recorded deviation.
    assert qd.resolve("cyclicstrength_dsssand_watercontent", "water_content", documented_unit="pct")["unit"] == "%"
    assert qd.resolve("any_function", "water_content", documented_unit="-")["unit"] == "-"
    # Unknown names stay unknown: nothing is invented.
    assert qd.resolve("any_function", "no_such_parameter") is None


def test_name_collisions_are_remapped_per_function():
    assert qd.lookup("Ic")["id"] == "ic"
    assert qd.lookup_in("reinforced_circularsection_inertia", "Ic")["id"] == "second_moment_of_area"
    assert qd.resolve("reinforced_circularsection_inertia", "Ic")["unit"] == "m⁴"
    assert qd.audit()["findings"].get("dimension_mismatch", []) == [], "a name collision needs an entry in quantity_function_overrides.json"
    for entry in qd.load_overrides()["quantity"]:
        assert entry["quantity"] in {q["id"] for q in QUANTITIES}


def test_every_recorded_deviation_matches_a_documented_unit():
    from core.quantity_scan import scan_all
    documented = {}
    for o in scan_all():
        if o["unit_raw"] is not None and qd.canonical_unit(o["unit_raw"]):
            documented.setdefault((o["function"], o["key"]), set()).add(qd.canonical_unit(o["unit_raw"]))
    for function, keys in qd.load_function_units().items():
        for key, unit in keys.items():
            assert unit in documented[(function, key)], (function, key, unit)


def test_directory_cannot_affect_calculations():
    """The directory only drives what the UI shows: calculation, form and GeoAI schema code never imports it."""
    import pathlib
    core = pathlib.Path(qd.__file__).parent
    allowed = {"quantity_directory.py", "quantity_scan.py"}
    offenders = []
    for path in core.rglob("*.py"):
        if path.name in allowed or "venv" in path.parts:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if "quantity_directory" in text or "quantity_scan" in text or "quantity_standard" in text:
            offenders.append(str(path.relative_to(core)))
    assert offenders == [], offenders


def test_scan_reads_manifest_docs_indented_by_older_python(tmp_path, monkeypatch):
    # Python < 3.13 keeps a docstring's indentation in __doc__, and CI rewrites the manifest when
    # it was generated on another Python version: the scan must find the same units either way.
    import json
    from core import quantity_scan
    doc = ("Robertson & Wride behaviour index.\n\n:returns: Dictionary with the following keys:\n\n"
           "    - 'Fr [%]': Normalised friction ratio (:math:`F_r`)  [:math:`%`]\n")
    indented = doc.split("\n")[0] + "\n" + "\n".join("    " + line if line.strip() else line for line in doc.split("\n")[1:])
    manifest = {"functions": [{"name": "f", "module": "m", "doc": d} for d in (indented,)]}
    path = tmp_path / "function_manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    monkeypatch.setattr(quantity_scan, "MANIFEST_PATH", str(path))
    found = [o for o in quantity_scan.scan_all() if o["function"] == "f"]
    assert ("Fr", "%") in {(o["key"], o["unit_raw"]) for o in found}
