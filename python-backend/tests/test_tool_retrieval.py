"""Tool-retrieval selector: normalisation, cards, BM25 ranking and recall regression."""
import time
from collections import Counter

import pytest

import core.geoai.tool_definitions  # noqa: F401  (registers canonical tools)
from core.geoai import tool_retrieval as tr
from core.geoai import tool_selector as ts
from core.geoai.tool_registry import GeoAITool, tool_registry


def _names(tools):
    return [t["function"]["name"] for t in tools]


def _index():
    return ts._index()


# ---------------------------------------------------------------- normalisation

@pytest.mark.parametrize("words", [
    ("settlement", "settlements", "settle"),
    ("calculated", "calculation", "calculates", "calculate"),
    ("normalised", "normalization", "normalize", "normalising"),
    ("behaviour", "behavior", "behaviours"),
    ("stresses", "stress"),
    ("consolidated", "consolidation"),
    ("embedment", "embedded"),
])
def test_stemmer_maps_inflections_and_spellings_together(words):
    assert len({tr.stem(w) for w in words}) == 1, {w: tr.stem(w) for w in words}


def test_stemmer_is_deterministic_and_keeps_symbols():
    for sym in ("n60", "k0", "d10", "cpt", "spt", "su", "gmax"):
        assert tr.stem(sym) == tr.stem(sym)
    assert tr.stem("n60") == "n60" and tr.stem("d10") == "d10"


def test_split_identifier_snake_camel_and_digits():
    assert tr.split_identifier("AxCapCalculation") == ["ax", "cap", "calculation"]
    assert tr.split_identifier("PCPTProcessing") == ["pcpt", "processing"]
    assert tr.split_identifier("porosity_voidratio") == ["porosity", "voidratio"]
    assert "eurocode" in tr.split_identifier("Eurocode7_factoring_STR_GEO")
    assert tr.split_identifier("spt_N60_correction") == ["spt", "n60", "correction"]


def test_segment_compound_groundhog_names():
    vocab = {"earth", "pressure", "coefficients", "bulk", "unit", "weight", "void", "ratio", "earthpressure"}
    assert tr.segment_compound("earthpressurecoefficients", vocab) == ["earth", "pressure", "coefficients"]
    assert tr.segment_compound("bulkunitweight", vocab) == ["bulk", "unit", "weight"]
    assert tr.segment_compound("voidratio", vocab) == ["void", "ratio"]
    assert tr.segment_compound("porosity", vocab) == []


def test_clean_doc_text_collapses_math_symbols():
    text = tr.clean_doc_text("Bearing capacity factor (:math:`N_q`) and :math:`K_{ac}` .. math:: N_q = e^{x}")
    toks = tr.raw_tokens(text)
    assert "nq" in toks and "kac" in toks
    assert "k" not in toks                    # K of K_ac must not collide with k = permeability


# ---------------------------------------------------------------- concepts

@pytest.mark.parametrize("a,b,concept", [
    ("Ic", "soil behaviour type index", "~sbt_index"),
    ("k", "hydraulic conductivity", "~permeability"),
    ("Dr", "relative density", "~relative_density"),
    ("qc", "cone resistance", "~cone_resistance"),
    ("fs", "sleeve friction", "~sleeve_friction"),
    ("N60", "SPT blow count", "~spt"),
    ("cu", "undrained shear strength", "~undrained_strength"),
    ("phi", "angle of shearing resistance", "~friction_angle"),
    ("G0", "small-strain shear modulus", "~gmax"),
    ("Vs", "shear wave velocity", "~shear_wave_velocity"),
    ("Kp", "passive earth pressure", "~passive_pressure"),
    ("CSR", "liquefaction", "~liquefaction"),
])
def test_synonyms_share_a_concept_token(a, b, concept):
    assert concept in tr.analyze(a)
    assert concept in tr.analyze(b)


def test_property_synonyms_from_context_resolver_are_reused():
    groups = tr.concept_groups()
    # PROPERTY_SYNONYMS 'phi_eff' / 'friction_angle' are folded into one concept
    assert any("effective friction angle" in p for p in groups["friction_angle"])
    assert tr.analyze("effective friction angle").count("~friction_angle") == 1


def test_stopwords_and_numbers_are_dropped():
    terms = tr.analyze("Please calculate the value for 12.5 kPa using the current project")
    assert "calcul" not in terms and "12" not in terms and "project" not in terms


def test_query_head_and_name_target():
    assert tr.query_head("What is the porosity if the void ratio is 0.6?") == "What is the porosity"
    assert tr.query_head("We have porosity = 0.4. Convert porosity to void ratio.") == "void ratio"
    assert tr.name_target("porosity_voidratio") == "porosity"
    assert tr.name_target("calculate_void_ratio_from_porosity") == "void ratio"
    assert tr.name_target("AxCapCalculation") == "AxCapCalculation"


# ---------------------------------------------------------------- cards / BM25

def test_cards_are_built_from_existing_registry_data():
    idx = _index()
    assert set(idx.names) == set(tool_registry._tools)
    rankine = idx.cards[idx.position["calculate_earth_pressure_rankine"]]
    assert rankine.canonical
    assert "rankin" in rankine.fields["metadata"]            # tool_metadata.TOOL_METADATA method
    assert "backfill" in rankine.fields["parameters"]        # input-schema parameter description
    assert "~friction_angle" in rankine.fields["parameters"]  # concept from parameter text
    if "nq_frictionangle_sand" in idx.position:              # Groundhog tool: docstring returns + name split
        nq = idx.cards[idx.position["nq_frictionangle_sand"]]
        assert not nq.canonical
        assert "nq" in nq.fields["outputs"]
        assert {"frict", "angl"} <= set(nq.fields["name"])


def test_bm25_prefers_documents_with_rare_query_terms():
    docs = [Counter({"pile": 2.0, "capacity": 1.0}), Counter({"capacity": 1.0, "bearing": 1.0}), Counter({"void": 1.0})]
    bm = tr.BM25Index(docs)
    s = bm.scores(["pile", "capacity"])
    assert s[0] > s[1] > s[2] == 0.0
    assert bm.scores(["unknown"]) == [0.0, 0.0, 0.0]


# ---------------------------------------------------------------- selector behaviour

def test_active_function_is_always_offered_first():
    ctx = {"activeFunction": "calculate_stresses_point_load"}
    tools = ts.select_relevant_tools("rankine earth pressure coefficients", context=ctx, max_tools=1)
    assert _names(tools) == ["calculate_stresses_point_load"]
    tools = ts.select_relevant_tools("unrelated query", context=ctx, max_tools=5)
    assert _names(tools)[0] == "calculate_stresses_point_load"


def test_categories_are_boosts_not_filters():
    # The old selector gated this query to the two hand-written shallow_foundations tools.
    names = _names(ts.select_relevant_tools("Calculate the bearing capacity factor Nq for the sand", max_tools=5))
    assert "nq_frictionangle_sand" in names


def test_curated_tool_preferred_over_auto_registered_duplicate():
    names = _names(ts.select_relevant_tools("Calculate the bulk unit weight", max_tools=5))
    assert "calculate_bulk_unit_weight" in names
    if "bulkunitweight" in names:
        assert names.index("calculate_bulk_unit_weight") < names.index("bulkunitweight")


def test_research_questions_offer_document_search():
    names = _names(ts.select_relevant_tools("What does the literature say about negative skin friction on piles?", max_tools=3))
    assert names[0] == "search_local_documents"
    # numeric inputs make it a calculation request, not research
    names = _names(ts.select_relevant_tools("Compare Ka and Kp for phi = 30 deg using Rankine", max_tools=3))
    assert "search_local_documents" not in names


def test_optional_schema_token_budget():
    q = "Calculate the liquefaction probability from the CPT"
    unbounded = ts.select_relevant_tools(q, max_tools=5)
    budget = 1200
    bounded = ts.select_relevant_tools(q, max_tools=5, max_schema_tokens=budget)
    assert bounded and _names(bounded)[0] == _names(unbounded)[0]
    assert len(bounded) == 1 or sum(ts.schema_tokens(t) for t in bounded) <= budget


def test_prompt_schemas_drop_math_blocks_and_titles():
    tool = {"name": "t", "description": "Does x. More text.", "input_schema": {
        "type": "object", "properties": {
            "title": {"type": "string", "title": "Title", "description": "Kept param (:math:`q_s`)  .. math:: a = b"}}}}
    params = ts.format_tools_for_prompt([tool])[0]["function"]["parameters"]
    assert params["properties"]["title"] == {"type": "string", "description": "Kept param (q_s)"}


def test_selection_is_deterministic():
    q = "Estimate su, phi' and Dr from the CPT with qc = 5 MPa and fs = 40 kPa"
    first = ts.select_relevant_tools(q, max_tools=10)
    assert ts.select_relevant_tools(q, max_tools=10) == first
    tr.clear_index_cache()
    assert ts.select_relevant_tools(q, max_tools=10) == first


def test_index_rebuilds_when_registry_changes():
    from core.geoai.schemas.base import GeoAIBaseModel

    class _In(GeoAIBaseModel):
        x: float = 1.0

    name = "zzqx_frobnication_index_test"
    before = _index()
    tool_registry._tools[name] = GeoAITool(name, "Computes the zzqx frobnication index.", "testing", _In, None,
                                           lambda **kw: {"r": 1})
    try:
        assert _names(ts.select_relevant_tools("zzqx frobnication index", max_tools=3))[0] == name
        assert _index() is not before
    finally:
        del tool_registry._tools[name]
    assert name not in _index().position


def test_selection_latency_after_warm_up():
    queries = ["Calculate the settlement of the clay layer with mv = 0.0003 m2/kN",
               "What is Gmax if Vs = 200 m/s and gamma = 18 kN/m3?",
               "Classify the CPT soil behaviour type with qc = 3 MPa and fs = 50 kPa",
               "Search our documents for pile capacity guidance"] * 10
    ts.select_relevant_tools("warm up", max_tools=5)
    times = []
    for q in queries:
        t0 = time.perf_counter()
        ts.select_relevant_tools(q, max_tools=5)
        times.append(time.perf_counter() - t0)
    times.sort()
    assert times[int(0.95 * (len(times) - 1))] < 0.05


# ---------------------------------------------------------------- recall regression (eval_val only)

def test_selector_recall_on_eval_val_regression():
    from core.geoai.eval.selector_recall import load_split, selector_recall

    examples = load_split("val")
    if not examples:
        pytest.skip("eval_val.jsonl not generated")
    res = selector_recall(examples, (1, 3, 5))
    # Achieved 0.963 / 1.000 / 1.000 when tuned; thresholds leave a little headroom.
    assert res["recall"][5] >= 0.97
    assert res["recall"][3] >= 0.95
    assert res["recall"][1] >= 0.90


# ---------------------------------------------------------------- natural phrasing (generalisation)

@pytest.mark.parametrize("words", [
    ("liquefy", "liquefies", "liquefied", "liquefiable", "liquefaction"),
    ("dense", "density"),
    ("settle", "settled", "settlement"),
    ("consolidate", "consolidated", "consolidation"),
    ("sensitive", "sensitivity"),
    ("permeable", "permeability"),
    ("classify", "classified", "classification"),
    ("slide", "sliding"),
])
def test_stemmer_joins_verb_adjective_and_noun_forms(words):
    assert len({tr.stem(w) for w in words}) == 1, {w: tr.stem(w) for w in words}


def test_stemmer_leaves_look_alike_words_alone():
    assert tr.stem("water") == "water" and tr.stem("paper") == "paper" and tr.stem("resistance") == "resist"
    assert tr.stem("embed") == "embed" and tr.stem("n60") == "n60"


@pytest.mark.parametrize("text,words", [
    ("M7.5 event, PGA 0.3g", ("earthquake magnitude", "peak ground acceleration")),
    ("Mw 6.5", ("earthquake magnitude",)),
    ("E from the SPT", ("youngs modulus",)),
    ("e = 0.62 and w = 22%", ("void ratio", "water content")),
    ("what's e?", ("void ratio",)),
    ("N = 18", ("blow count",)),
    ("want kN/m3", ("unit weight",)),
])
def test_notation_is_expanded_case_sensitively(text, words):
    out = tr.normalize_notation(text)
    for w in words:
        assert w in out


def test_notation_does_not_fire_on_lengths_or_prose():
    assert "magnitude" not in tr.normalize_notation("a 5 m deep excavation with M 10 m spacing")
    assert "void ratio" not in tr.normalize_notation("see e.g. the report")
    assert "magnitude" not in tr.normalize_notation("M5 kN")


def test_unseparated_abbreviations_share_concepts():
    assert "~min_void_ratio" in tr.analyze("emin 0.45") and "~min_void_ratio" in tr.analyze("e_min", identifier=True)
    assert "~cone_resistance" in tr.analyze("cone tip 2 MPa")
    assert "~sleeve_friction" in tr.analyze("sleeve 45 kPa")
    assert "~seismic" in tr.analyze("PGA of 0.2")


def test_shorter_phrase_inside_longer_match_is_suppressed():
    terms = tr.analyze("standard penetration test")
    assert "~spt" in terms and "~research" not in terms
    assert "~research" in tr.analyze("which standard covers this?")


def test_query_head_finds_the_requested_quantity():
    assert tr.query_head("porosity is 38% - what's e?") == "what's e"
    assert tr.query_head("turn a void ratio of 0.85 into porosity") == "porosity"
    assert tr.query_head("saturated sample, w = 40%, void ratio?").strip() == "void ratio"


@pytest.mark.parametrize("query,family", [
    ("will it liquefy? M7.5, PGA 0.3g, sand at 6 m", ("liquef", "csr_", "crr_", "cyclicstressratio")),
    ("how dense is this sand? e = 0.62, emin 0.48, emax 0.91", ("relative_density",)),
    ("what soil is this? cone tip 2.1 MPa, sleeve 45 kPa at 8 m", ("soil_behavior", "soilclass", "behaviourindex")),
])
def test_colloquial_questions_reach_the_right_family(query, family):
    names = _names(ts.select_relevant_tools(query, max_tools=5))
    assert any(key in n.lower() for n in names[:3] for key in family), names


def test_research_questions_prefer_search_over_indexing():
    names = _names(ts.select_relevant_tools("what does the research say about set-up of driven piles in clay?",
                                            max_tools=3))
    assert names[0] == "search_local_documents"
    names = _names(ts.select_relevant_tools("index this site investigation report into the library", max_tools=3))
    assert "index_document_text" in names


def test_selector_recall_on_natural_dev_set_regression():
    from core.geoai.eval.selector_recall import load_split, selector_recall

    res = selector_recall(load_split("natural"), (1, 3, 5))
    assert res["n"] >= 60
    # Achieved 0.975 / 0.988 / 1.000 when tuned on this set (it is a dev set, not a blind test).
    assert res["recall"][5] >= 0.95
    assert res["recall"][3] >= 0.93
    assert res["recall"][1] >= 0.88
