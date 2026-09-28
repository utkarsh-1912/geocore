# Author: Utkarsh Gupta
# License: GPL v3
"""
Registry-validated training / evaluation examples for the project-data GeoAI tools
(AGENTS.md §9, §14, §17, §20-21, §28-29):

    list_project_cpts, get_cpt_summary, calculate_pile_capacity_from_cpt,
    calculate_shallow_foundation_capacity, calculate_foundation_settlement

These tools read the *current project* (CPT soundings, soil profile), so every example is
generated -- and every expected call executed through the GeoAI Tool Registry -- against the
deterministic synthetic project in ``core.geoai.eval.synthetic_project`` (or an explicitly
empty project). The example records which one in ``metadata['project_fixture']`` so the
scorer / runner can load the same project, and project-context examples carry exactly the
context string the agent's system prompt shows (``ProjectContext.get_compact_context_string``).

Covers the AGENTS §20 categories for these tools: correct requests (inline parameters and
units, and project-context requests), unit traps (mm diameter, ft tip, MPa su, kPa unit weight),
missing data (clarify naming the missing inputs, each refused by the registry), ambiguous
requests, conflicting data, tool failures (tip below the CPT end, CPT not in the project,
method/pile mismatch, tool-reported missing parameters) and multi-turn trajectories
``list_project_cpts -> get_cpt_summary -> calculate_pile_capacity_from_cpt -> grounded answer``.

Determinism: this builder has its own RNG stream (``seed | RNG_SALT``) and runs after every
other scaleup builder, uses its own strata, and only appends drafts -- the rest of the
generated dataset is unchanged by it. LCPC is used at most twice (Groundhog's LCPC is slow).
"""
import json
import random
import re
from collections import Counter
from typing import Any, Dict, List, Optional, Sequence, Tuple

from core.geoai.eval import synthetic_project as SP
from core.geoai.eval.example import EvalExample
from core.geoai.eval.scoring import effective_arguments, values_match

LIST = "list_project_cpts"
SUMMARY = "get_cpt_summary"
PILE = "calculate_pile_capacity_from_cpt"
CAP = "calculate_shallow_foundation_capacity"
SET = "calculate_foundation_settlement"
PROJECT_TOOLS = (LIST, SUMMARY, PILE, CAP, SET)
RNG_SALT = "project_tools_v1"
FULL_SIZE_PER_TOOL = 30          # counts below are for per_tool = 30 and scale down with it

_REQUIRED_BY_TOOL = "tool"       # metadata marker: required by the tool, not by the JSON schema

PILE_PHRASES = {
    "driven_closed_steel_pipe": ("closed-ended driven steel pipe pile", "driven closed-end steel tube pile",
                                 "closed-ended steel pipe pile (driven)"),
    "driven_open_steel_pipe": ("open-ended driven steel pipe pile", "driven open-ended steel tube"),
    "driven_precast_concrete": ("driven precast concrete pile", "precast concrete driven pile",
                                "driven precast pile"),
    "bored_support_fluid": ("bored pile drilled under bentonite", "bored cast-in-situ pile with support fluid"),
    "cfa": ("CFA pile", "continuous flight auger pile"),
}
METHOD_PHRASES = {
    "koppejan": ("Koppejan", "the Koppejan method", "Koppejan's method"),
    "debeer": ("De Beer", "the De Beer method", "De Beer (Belgian practice)"),
    "lcpc": ("LCPC", "the LCPC method", "LCPC (Bustamante & Gianeselli)"),
}
METHOD_LABEL = {"koppejan": "Koppejan method", "debeer": "De Beer method (Belgian practice)",
                "lcpc": "LCPC method (Bustamante & Gianeselli 1982)"}
METHOD_MENTIONS = {"koppejan": ["koppejan"], "debeer": ["de beer", "debeer"], "lcpc": ["lcpc", "bustamante"]}
BELOW_TIP_D = {"koppejan": 4.0, "debeer": 1.0, "lcpc": 1.5}

PILE_CLARIFY = {
    "pile_diameter_m": ["diameter", "pile size", "pile_diameter"],
    "pile_tip_depth_m": ["tip", "toe", "penetration", "embedment", "pile length", "depth"],
    "method": ["method", "lcpc", "koppejan", "de beer", "debeer"],
    "pile_type": ["pile type", "type of pile", "installation", "driven", "bored", "cfa"],
    "cpt_id": ["which cpt", "cpt", "location"],
    "wall_thickness_mm": ["wall thickness", "wall"],
    "open_end_condition": ["plug", "coring", "open end", "open-end"],
    "debeer_alpha_s": ["alpha_s", "alpha", "shaft factor"],
    "debeer_alpha_b": ["alpha_b", "alpha", "base factor"],
}
PILE_LABEL = {"pile_diameter_m": "pile diameter (m)", "pile_tip_depth_m": "pile tip depth below ground (m)",
              "method": "calculation method (LCPC, Koppejan or De Beer)",
              "pile_type": "pile type / installation method (e.g. driven closed-ended steel pipe, precast "
                           "concrete, bored with support fluid, CFA)",
              "cpt_id": "CPT to use (the project has CPT-01, CPT-02 and CPT-03)",
              "wall_thickness_mm": "steel wall thickness of the open-ended pipe (mm)",
              "open_end_condition": "whether the open end should be treated as plugged or coring",
              "debeer_alpha_s": "De Beer shaft factor alpha_s for this pile type",
              "debeer_alpha_b": "De Beer base factor alpha_b for this pile type"}

SHAPE_WORDS = {"square": "square", "strip": "strip", "rectangular": "rectangular", "circular": "circular"}


def _fmt(v: float, nd: int = 2) -> str:
    if nd <= 0:
        return str(int(round(v)))
    s = f"{v:.{nd}f}".rstrip("0").rstrip(".")
    return s if s not in ("", "-0") else "0"


def _sig(v: float, sig: int = 4) -> str:
    from core.geoai.training.scaleup import fmt_result
    return fmt_result(float(v)) if sig == 4 else f"{v:.{sig}g}"


def _a(phrase: str) -> str:
    return ("an " if phrase[:1].lower() in "aeiou" else "a ") + phrase


def _clean(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\s+([,.?:;])", r"\1", text)
    text = re.sub(r"([,:;])(?=[,.?])", "", text)
    text = re.sub(r"\.\.+", ".", text)
    return text[:1].upper() + text[1:]


def _param_text(name: str, v: Dict[str, Any]) -> str:
    unit = "" if v.get("unit") in (None, "", "-") else f" {v['unit']}"
    return f"{name} = {v['value']:g}{unit} ({v['source']})"


def _numeric(result: Dict[str, Any]) -> Dict[str, float]:
    return {k: float(v) for k, v in result.items()
            if not k.startswith("_") and isinstance(v, (int, float)) and not isinstance(v, bool)}


def _stable(s: str) -> str:
    import hashlib
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:10]


def tool_call_text(name: str, arguments: Dict[str, Any]) -> str:
    """Reference completion of a tool-call turn (Hermes/Qwen format parsed by the scorer)."""
    return "<tool_call>" + json.dumps({"name": name, "arguments": arguments}, ensure_ascii=False) + "</tool_call>"


class ProjectToolExamples:
    """Adds drafts for the project-data tools to a scaleup ``_Generator``."""

    def __init__(self, g, seed: int, per_tool: int = FULL_SIZE_PER_TOOL):
        self.g = g
        self.rng = random.Random(f"{seed}|{RNG_SALT}")
        self.scale = min(1.0, max(0.1, per_tool / FULL_SIZE_PER_TOOL))
        self.context = SP.eval_context(SP.FIXTURE)
        self.made: Counter = Counter()

    # ------------------------------------------------------------ plumbing
    def n(self, full: int, minimum: int = 2) -> int:
        return max(minimum, int(round(full * self.scale)))

    def run(self, tool: str, args: Dict[str, Any], fixture: str):
        with SP.loaded(fixture):
            return self.g._execute(tool, args)

    def _meta(self, fixture: str, **extra) -> Dict[str, Any]:
        return {"project_fixture": fixture, **extra}

    def _ctx(self, fixture: str) -> Optional[Dict[str, str]]:
        return self.context if fixture == SP.FIXTURE else None

    def _expected(self, tool: str, args: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Canonical effective values of the stated arguments (None if the schema rejects them)."""
        model = self.g._tool(tool).input_model
        eff, err = effective_arguments(model, args)
        if err is not None:
            return None
        from core.geoai.eval.scoring import canonicalise_keys
        canon, _ = canonicalise_keys(model, args)
        return {k: eff[k] for k in canon}

    # ------------------------------------------------------------ example factories
    def trajectory(self, *, category: str, stratum: str, template: str, prompt: str, fixture: str,
                   calls: Sequence[Tuple[str, Dict[str, Any]]], answer_fn, unit_trap=None,
                   expected_first: Optional[Dict[str, Any]] = None, final_values_fn=None,
                   final_mentions: Optional[List[List[str]]] = None, expect_error_at: Optional[int] = None) -> bool:
        """
        One user request answered by ``calls`` executed in order through the registry, then a
        grounded final answer. Emits the decision example, one decision example per later step
        (prefix = earlier calls + real results) and the final-answer example.
        ``expect_error_at``: index of the call that must fail (tool-reported error); all calls
        before it must succeed.
        """
        executed = []
        for k, (tool, args) in enumerate(calls):
            res, err = self.run(tool, args, fixture)
            must_fail = expect_error_at == k
            if (err is not None) != must_fail:
                self.g.dropped[f"{category}:{'unexpected_success' if must_fail else 'execution_failed'}"] += 1
                return False
            executed.append((tool, args, res, err))
        base = f"call_{_stable(stratum + '|' + prompt)}"
        user = {"role": "user", "content": prompt}
        meta = self._meta(fixture)
        msgs: List[Dict[str, Any]] = []
        prefixes = []
        for k, (tool, args, res, err) in enumerate(executed):
            prefixes.append(list(msgs))
            cid = f"{base}_{k + 1}"
            msgs.append({"role": "assistant", "content": "",
                         "tool_calls": [{"id": cid, "type": "function", "function": {"name": tool, "arguments": args}}]})
            tm = self.g._tool_msg(tool, res, err)
            tm["tool_call_id"] = cid
            msgs.append(tm)
        answer = answer_fn(executed)
        steps = []
        for k, (tool, args, res, err) in enumerate(executed):
            expected = expected_first if (k == 0 and expected_first is not None) else self._expected(tool, args)
            if expected is None:
                self.g.dropped[f"{category}:normalisation_mismatch"] += 1
                return False
            steps.append(dict(expected_tool=tool, expected_arguments=expected, provided_params=sorted(expected),
                              expected_result=_numeric(res) if err is None else None))
        first_tool, first_args = executed[0][0], executed[0][1]
        d = self.g._add(category=category, stratum=stratum, template=template, prompt=prompt,
                        context=self._ctx(fixture), expected_action="tool_call", unit_trap=unit_trap,
                        metadata=dict(meta, required_params=sorted(
                            n for n, f in self.g._tool(first_tool).input_model.model_fields.items() if f.is_required())),
                        target_call={"name": first_tool, "arguments": first_args},
                        tool_message=msgs[1], final_answer=answer, **steps[0])
        d.trajectory = msgs + [{"role": "assistant", "content": answer}]
        for k in range(1, len(executed)):
            tool, args = executed[k][0], executed[k][1]
            d.followups.append(EvalExample(
                id=f"step{k + 1}", category=category, expected_action="tool_call",
                messages=[user] + prefixes[k], reference_response=tool_call_text(tool, args),
                metadata=dict(meta, step=k + 1), **steps[k]))
        values, units = (final_values_fn(executed) if final_values_fn else (None, {}))
        d.followups.append(EvalExample(
            id="final", category=category, expected_action="synthesize", turn_type="final_answer",
            messages=[user] + msgs, expected_result_values=values or None,
            required_mentions=final_mentions or [], reference_response=answer,
            metadata=dict(meta, result_units=units)))
        self.made[(category, stratum)] += 1
        return True

    def clarify(self, *, category: str, stratum: str, template: str, prompt: str, fixture: str,
                tool: str, present: Dict[str, Any], missing: List[str], keywords: List[List[str]],
                reference: str, unit_trap=None, acceptable_actions=None, check_refused: bool = True,
                provided: Optional[Sequence[str]] = None) -> bool:
        """A request the agent must answer with a question (never a call); the registry must refuse it."""
        if check_refused:
            _, err = self.run(tool, present, fixture)
            if err is None:
                self.g.dropped[f"{category}:registry_accepted_incomplete_call"] += 1
                return False
        fields = self.g._tool(tool).input_model.model_fields
        meta = self._meta(fixture)
        if missing and not all(fields[m].is_required() for m in missing if m in fields):
            meta["required_by"] = _REQUIRED_BY_TOOL
        self.g._add(category=category, stratum=stratum, template=template, prompt=prompt,
                    context=self._ctx(fixture), expected_action="clarify", expected_tool=tool,
                    acceptable_actions=list(acceptable_actions or []),
                    provided_params=sorted(present if provided is None else provided),
                    missing_params=list(missing), unit_trap=unit_trap, clarify_keywords=keywords,
                    reference_response=reference, metadata=meta)
        self.made[(category, stratum)] += 1
        return True

    # =================================================================== piles
    def _pile_case(self, method: str, cpt: Optional[str] = None, pile_type: Optional[str] = None) -> Dict[str, Any]:
        rng = self.rng
        if cpt is None:
            cpt = rng.choice(["CPT-01", "CPT-03", "CPT-03"] + ([] if method == "debeer" else ["CPT-02"]))
        if pile_type is None:
            types = list(PILE_PHRASES)
            if method != "koppejan":
                types.remove("driven_open_steel_pipe")
            pile_type = rng.choice(types)
        d = rng.choice((0.3, 0.35, 0.4, 0.45, 0.5, 0.6, 0.7, 0.8))
        z_end = SP.CPT_SPECS[cpt][1]
        tip_max = min(20.0, z_end - BELOW_TIP_D[method] * d - 0.3)
        tips = [t / 2 for t in range(12, int(tip_max * 2) + 1)]
        args: Dict[str, Any] = {"cpt_id": cpt, "method": method, "pile_type": pile_type,
                                "pile_diameter_m": d, "pile_tip_depth_m": rng.choice(tips)}
        if pile_type == "driven_open_steel_pipe":
            args["wall_thickness_mm"] = float(rng.choice((12, 16, 20, 25)))
            args["open_end_condition"] = rng.choice(("coring", "plugged"))
        if method == "debeer":
            args["debeer_alpha_s"] = rng.choice((0.5, 0.6, 0.7))
            args["debeer_alpha_b"] = rng.choice((0.8, 0.9, 1.0))
        return args

    def _pile_parts(self, args: Dict[str, Any], d_text: Optional[str] = None,
                    tip_text: Optional[str] = None) -> Dict[str, str]:
        rng = self.rng
        parts: Dict[str, str] = {}
        ptype = rng.choice(PILE_PHRASES[args["pile_type"]]) if "pile_type" in args else "pile"
        if "pile_diameter_m" in args:
            dt = d_text or f"{_fmt(args['pile_diameter_m'])} m"
            parts["pile"] = _a(f"{dt} {ptype}") if rng.random() < 0.6 else _a(f"{ptype} of {dt} diameter")
        else:
            parts["pile"] = _a(ptype)
        if "pile_tip_depth_m" in args:
            tt = tip_text or f"{_fmt(args['pile_tip_depth_m'])} m"
            parts["tip"] = rng.choice((f"to {tt}", f"with the tip at {tt}", f"founded at {tt} below ground",
                                       f"with a toe depth of {tt}"))
        if "cpt_id" in args:
            parts["cpt_id"] = args["cpt_id"]
            parts["cpt"] = rng.choice((f"at {args['cpt_id']}", f"at location {args['cpt_id']}",
                                       f"using {args['cpt_id']}"))
        if "method" in args:
            parts["method"] = rng.choice(METHOD_PHRASES[args["method"]])
            parts["method_bare"] = METHOD_PHRASES[args["method"]][0]
        extra = []
        if "wall_thickness_mm" in args:
            extra.append(f"wall thickness {_fmt(args['wall_thickness_mm'])} mm")
        if "open_end_condition" in args:
            extra.append("treat the base as plugged" if args["open_end_condition"] == "plugged"
                         else "assume a coring, unplugged base")
        if "debeer_alpha_s" in args:
            extra.append(f"alpha_s = {_fmt(args['debeer_alpha_s'])}")
        if "debeer_alpha_b" in args:
            extra.append(f"alpha_b = {_fmt(args['debeer_alpha_b'])}")
        if "groundwater_depth_m" in args:
            extra.append(f"groundwater at {_fmt(args['groundwater_depth_m'])} m")
        parts["extra"] = ", ".join(extra)
        return parts

    @staticmethod
    def _pile_prompt(idx: int, p: Dict[str, str]) -> str:
        pile, tip, cpt = p.get("pile", ""), p.get("tip", ""), p.get("cpt", "")
        m, mb, extra = p.get("method", ""), p.get("method_bare", ""), p.get("extra", "")
        use = f" Use {m}." if m else ""
        ex = f" ({extra})" if extra else ""
        ex_s = f" {extra[:1].upper() + extra[1:]}." if extra else ""
        frames = [
            f"Calculate the axial pile capacity {cpt} for {pile} {tip}{' using ' + m if m else ''}{ex}.",
            f"What's the ultimate compression capacity of {pile} {tip} {cpt}?{use}{ex_s}",
            f"Using the current project, give me the {mb + ' ' if mb else ''}capacity of {pile} {tip} {cpt}{ex}.",
            f"{p['cpt_id'] + ': ' if p.get('cpt_id') else ''}{mb + ' ' if mb else ''}shaft and base resistance for {pile} {tip}{ex}.",
            f"Can you estimate Rs, Rb and Rc for {pile} {tip} {cpt}?{use}{ex_s}",
            f"I need the pile capacity {cpt} - {pile} {tip}{', ' + mb + ' please' if mb else ''}{ex}.",
            f"Pile capacity estimate {cpt}: {pile} {tip}.{use}{ex_s}",
            f"How much axial load can {pile} {tip} {cpt} carry (ultimate)?{use}{ex_s}",
        ]
        return _clean(frames[idx % len(frames)])

    def _pile_answer(self, res: Dict[str, Any], lead: str = "") -> str:
        p = res["pile"]
        src = res["provenance"]["cpt_source"]
        f = res["method_factors"]
        if res["method"] == "koppejan":
            factors = f"alpha_p = {_fmt(f['alpha_p'], 3)}, alpha_s = {_fmt(f['alpha_s'], 3)} ({f['table_row']})"
        elif res["method"] == "debeer":
            factors = f"alpha_s = {_fmt(f['alpha_s'], 3)}, alpha_b = {_fmt(f['alpha_b'], 3)} (user-specified)"
        else:
            factors = f"base group {f['group_base']}, shaft group {f['group_shaft']} ({f['pile_category']})"
        pile = f"{p['description']}, D = {_fmt(p['diameter_m'])} m, tip at {_fmt(p['tip_depth_m'])} m"
        if p.get("wall_thickness_mm") is not None:
            pile += f", wall {_fmt(p['wall_thickness_mm'])} mm, {p['open_end_condition']} base"
        lines = ([lead] if lead else []) + [
            f"Result from `calculate_pile_capacity_from_cpt` at {res['cpt_id']} ({METHOD_LABEL[res['method']]}, "
            f"Groundhog {res['groundhog_class'].rsplit('.', 1)[-1]}):",
            f"- Ultimate shaft resistance Rs = {res['ultimate_shaft_resistance_kn']:.1f} kN",
            f"- Ultimate base resistance Rb = {res['ultimate_base_resistance_kn']:.1f} kN",
            f"- Ultimate total compression resistance Rc = {res['ultimate_total_resistance_kn']:.1f} kN",
            "",
            f"Pile: {pile}.",
            f"Provenance: CPT data from {src['object_type']} '{src['object_name']}' (qc column "
            f"'{src['columns']['qc']}', {res['cpt_depth_range_m'][0]:g}-{res['cpt_depth_range_m'][1]:g} m); "
            f"soil layering {res['soil_layering_source']}; factors {factors}.",
        ]
        if res.get("warnings"):
            lines.append("Warnings from the tool: " + " ".join(res["warnings"][:2]))
        lines.append("These are ultimate (unfactored) values: partial and model factors, group effects, negative "
                     "skin friction and settlement are not included, so this result alone does not establish "
                     "design adequacy.")
        return "\n".join(lines)

    @staticmethod
    def _pile_values(executed) -> Tuple[Dict[str, float], Dict[str, str]]:
        res = executed[-1][2]
        keys = ("ultimate_shaft_resistance_kn", "ultimate_base_resistance_kn", "ultimate_total_resistance_kn")
        return {k: float(res[k]) for k in keys}, {k: "kN" for k in keys}

    def build_piles(self):
        rng = self.rng
        # -------- correct requests (project CPTs, all inputs stated)
        plan = ["koppejan"] * self.n(18, 6) + ["debeer"] * self.n(5, 2) + ["lcpc"] * 2
        for i, method in enumerate(plan):
            args = self._pile_case(method)
            prompt = self._pile_prompt(i, self._pile_parts(args))
            self.trajectory(category="correct_request", stratum=PILE, template=f"P{i % 8}", prompt=prompt,
                            fixture=SP.FIXTURE, calls=[(PILE, args)],
                            answer_fn=lambda ex: self._pile_answer(ex[-1][2]),
                            final_values_fn=self._pile_values,
                            final_mentions=[[args["cpt_id"].lower()], METHOD_MENTIONS[method], ["unfactored", "ultimate"]])

        # -------- unit traps (convertible: diameter in mm, tip in ft, wall thickness in m)
        for i in range(self.n(10, 4)):
            args = self._pile_case("koppejan", pile_type="driven_open_steel_pipe" if i % 5 == 4 else None)
            kind = ("mm", "mm", "ft", "mm", "wall")[i % 5]
            d_text = tip_text = None
            trained = dict(args)
            if kind == "mm":
                given = f"{int(round(args['pile_diameter_m'] * 1000))} mm"
                d_text, trained["pile_diameter_m"], param = given, given, "pile_diameter_m"
            elif kind == "ft":
                ft = round(args["pile_tip_depth_m"] / 0.3048)
                given = f"{ft} ft"
                args["pile_tip_depth_m"] = round(ft * 0.3048, 4)
                tip_text, trained["pile_tip_depth_m"], param = given, given, "pile_tip_depth_m"
            else:
                given = f"{_fmt(args['wall_thickness_mm'] / 1000.0, 3)} m"
                trained["wall_thickness_mm"], param = given, "wall_thickness_mm"
            parts = self._pile_parts(args, d_text=d_text, tip_text=tip_text)
            if kind == "wall":
                parts["extra"] = parts["extra"].replace(f"wall thickness {_fmt(args['wall_thickness_mm'])} mm",
                                                        f"wall thickness {given}")
            prompt = self._pile_prompt(i + 3, parts)
            expected = self._expected(PILE, trained)
            if expected is None or not values_match(args[param], expected[param], rel_tol=1e-6):
                self.g.dropped["wrong_units:normalisation_mismatch"] += 1
                continue
            self.trajectory(category="wrong_units", stratum=PILE, template=f"U{i % 5}", prompt=prompt,
                            fixture=SP.FIXTURE, calls=[(PILE, trained)], expected_first=expected,
                            unit_trap={"param": param, "kind": "convertible", "given": given},
                            answer_fn=lambda ex: self._pile_answer(ex[-1][2]), final_values_fn=self._pile_values)

        # -------- missing data -> clarify naming the missing input(s)
        drops = ["pile_diameter_m", "method", "pile_tip_depth_m", "pile_type", "pile_diameter_m", "method",
                 "wall_thickness_mm", "debeer_alpha_s"]
        for i in range(self.n(16, 8)):
            drop = drops[i % len(drops)]
            method = "debeer" if drop == "debeer_alpha_s" else "koppejan"
            args = self._pile_case(method, pile_type="driven_open_steel_pipe" if drop == "wall_thickness_mm" else None)
            missing = [drop] + (["debeer_alpha_b"] if drop == "debeer_alpha_s" else [])
            present = {k: v for k, v in args.items() if k not in missing}
            prompt = self._pile_prompt(i, self._pile_parts(present))
            asks = [PILE_LABEL[m] for m in missing]
            ref = (f"Before I run the CPT pile calculation at {args['cpt_id']} I need the "
                   + " and the ".join(asks) + ", which you have not given. Could you provide "
                   + ("them" if len(asks) > 1 else "it") + "? I won't assume a value because the capacity depends on it.")
            self.clarify(category="missing_data", stratum=PILE, template=f"M{i % 8}", prompt=prompt,
                         fixture=SP.FIXTURE, tool=PILE, present=present, missing=missing,
                         keywords=[PILE_CLARIFY[m] + [m] for m in missing[:1]], reference=ref)
        # no CPT named although the project holds three
        for i in range(self.n(4, 2)):
            args = self._pile_case("koppejan")
            present = {k: v for k, v in args.items() if k != "cpt_id"}
            prompt = self._pile_prompt(i + 1, self._pile_parts(present))
            ref = ("Which CPT should I use? The project has CPT-01, CPT-02 and CPT-03 and the capacity depends on "
                   "the CPT profile at the pile location. Tell me the CPT (or ask me to list them with their depth "
                   "ranges) and I will run the calculation.")
            self.clarify(category="missing_data", stratum=PILE, template=f"N{i % 4}", prompt=prompt,
                         fixture=SP.FIXTURE, tool=PILE, present=present, missing=["cpt_id"],
                         keywords=[PILE_CLARIFY["cpt_id"], ["cpt-01", "cpt-02", "cpt-03", "list", "which"]],
                         reference=ref)

        # -------- tool failures (real registry errors -> grounded explanation)
        self._pile_failures()

        # -------- tool reports a missing input it alone can know about (De Beer groundwater at CPT-02)
        for i in range(self.n(3, 2)):
            args = self._pile_case("debeer", cpt="CPT-02")
            args["pile_tip_depth_m"] = min(args["pile_tip_depth_m"], 12.0)
            prompt = self._pile_prompt(i + 2, self._pile_parts(args))

            def answer(ex, cpt=args["cpt_id"]):
                return (f"The De Beer calculation at {cpt} was not run: the tool needs the groundwater depth below "
                        f"ground level (m), because De Beer works with effective stresses and no groundwater level "
                        f"is stored with {cpt}. Could you give me the groundwater depth at this location? I won't "
                        f"assume one.")
            self.trajectory(category="tool_failure", stratum="pile_missing_groundwater", template=f"G{i}",
                            prompt=prompt, fixture=SP.FIXTURE, calls=[(PILE, args)], expect_error_at=0,
                            answer_fn=answer,
                            final_mentions=[["groundwater", "water table", "water level"], ["cpt-02"]])

        # -------- ambiguous request with a loaded project
        prompts = [
            ("Calculate the pile capacity for my project.",
             [["diameter", "size", "dimension"], ["tip", "depth", "length", "penetration"],
              ["cpt", "which", "location", "method", "lcpc", "koppejan", "de beer"]]),
            ("What capacity will the piles have on this site?",
             [["diameter", "size", "dimension"], ["tip", "depth", "length", "penetration"], ["type", "driven", "bored", "cfa"]]),
            ("Run the CPT pile calculation.",
             [["cpt", "which", "location"], ["diameter", "size"], ["tip", "depth", "length", "penetration"]]),
            ("Can you do the pile design from the CPTs?",
             [["diameter", "size", "geometry"], ["load", "tip", "depth", "length"], ["method", "which", "cpt"]]),
            ("How much load can a pile take here?",
             [["diameter", "size", "type"], ["tip", "depth", "length", "penetration"], ["cpt", "which", "location"]]),
        ]
        wrappers = ("{p}", "{p} Use the current project data.")
        for pi, (base, kws) in enumerate(prompts):
            for wi, wrap in enumerate(wrappers[: 1 if self.scale < 0.5 else 2]):
                ref = ("I can run a CPT-based pile capacity calculation from the project CPTs (CPT-01, CPT-02, "
                       "CPT-03), but I need: the CPT/location, the pile type, the pile diameter (m), the tip depth "
                       "(m) and the method (LCPC, Koppejan or De Beer). Which values should I use?")
                self.clarify(category="ambiguous_request", stratum="pile_project_vague", template=f"A{pi}",
                             prompt=wrap.format(p=base), fixture=SP.FIXTURE, tool=PILE, present={}, missing=[],
                             keywords=kws, reference=ref, check_refused=False)

        # -------- multi-turn trajectories: list -> summary -> capacity -> grounded answer
        self._pile_multiturn()

    def _pile_failures(self):
        rng = self.rng
        cases = []
        for i in range(self.n(5, 2)):                                   # tip below the end of CPT-02 (15 m)
            args = self._pile_case("koppejan", cpt="CPT-02")
            args["pile_tip_depth_m"] = float(rng.choice((16, 17, 18, 19.5, 21, 24)))
            cases.append(("tip_below_cpt", args, [["cpt-02"], ["15"], ["deeper", "shallower", "does not reach", "below the end"]]))
        for i in range(self.n(4, 2)):                                   # 4D below the tip not available (CPT-01, 22 m)
            args = self._pile_case("koppejan", cpt="CPT-01", pile_type="cfa")
            args["pile_diameter_m"] = rng.choice((0.6, 0.7, 0.8))
            args["pile_tip_depth_m"] = float(rng.choice((20, 20.5, 21)))
            cases.append(("insufficient_cpt", args, [["cpt-01"], ["4d", "below the tip", "22"], ["shallower", "deeper"]]))
        for i in range(self.n(3, 2)):                                   # LCPC has no open-ended option
            args = self._pile_case("koppejan", pile_type="driven_open_steel_pipe")
            args["method"] = "lcpc"
            cases.append(("method_pile", args, [["lcpc"], ["open-ended", "open ended", "plug"], ["koppejan"]]))
        for i in range(self.n(4, 2)):                                   # CPT not in the project
            args = self._pile_case("koppejan", cpt="CPT-03")
            args["cpt_id"] = rng.choice(("CPT-07", "CPT-12", "CPT-04", "SCPT-02"))
            cases.append(("cpt_not_found", args, [[args["cpt_id"].lower()], ["cpt-01", "cpt-02", "cpt-03", "available"]]))
        for i, (kind, args, mentions) in enumerate(cases):
            prompt = self._pile_prompt(i, self._pile_parts(args))

            def answer(ex, kind=kind, a=args):
                err = ex[-1][3]
                reason = err.split(": ", 1)[-1] if "input validation failed" in err else err
                tail = {
                    "tip_below_cpt": " Options: a deeper CPT at this location, a shallower pile tip, or another project "
                                     "CPT that reaches the required depth - which would you like?",
                    "insufficient_cpt": " I can rerun it with a shallower tip or a smaller diameter, or use a deeper CPT "
                                        "(CPT-03 reaches 26 m) - which do you prefer?",
                    "method_pile": " Should I run the Koppejan method instead, or is the pile actually closed-ended?",
                    "cpt_not_found": " Which of the available CPTs should I use, or can you import the missing one?",
                }[kind]
                return f"The calculation was not run. The tool reported: {reason}{tail} I have not estimated a capacity."
            self.trajectory(category="tool_failure", stratum=f"pile_{kind}", template=f"F{i % 8}", prompt=prompt,
                            fixture=SP.FIXTURE, calls=[(PILE, args)], expect_error_at=0, answer_fn=answer,
                            final_mentions=mentions + [["not run", "not calculated", "have not estimated", "no capacity"]])

    def _pile_multiturn(self):
        rng = self.rng
        frames = [
            ("Which CPTs do we have? Take the deepest one, tell me what it shows and then give me the {method} "
             "capacity of {pile} {tip}.{extra}", "deepest"),
            ("Use the deepest CPT in the project for a {method} capacity check of {pile} {tip} - first describe the "
             "layering it passes through.{extra}", "deepest"),
            ("List the project CPTs, summarise the one at E 512300 / N 181200 and calculate the {method} capacity of "
             "{pile} {tip} there.{extra}", "CPT-01"),
            ("I don't remember the CPT names. Find the one at easting 512300, northing 181200, summarise it and "
             "work out the ultimate capacity of {pile} {tip} with {method}.{extra}", "CPT-01"),
        ]
        for i in range(self.n(8, 4)):
            frame, which = frames[i % len(frames)]
            cpt = "CPT-03" if which == "deepest" else which
            method = "debeer" if i % 4 == 3 else "koppejan"
            args = self._pile_case(method, cpt=cpt)
            p = self._pile_parts(args)
            extra = f" {p['extra'][:1].upper() + p['extra'][1:]}." if p["extra"] else ""
            prompt = _clean(frame.format(method=METHOD_PHRASES[method][0], pile=p["pile"], tip=p["tip"],
                                         extra=extra))
            calls = [(LIST, {}), (SUMMARY, {"cpt_id": cpt}), (PILE, args)]

            def answer(ex, cpt=cpt, which=which):
                listing, summary, res = ex[0][2], ex[1][2], ex[2][2]
                ids = ", ".join(f"{c['cpt_id']} ({c['depth_range_m'][0]:g}-{c['depth_range_m'][1]:g} m)"
                                for c in listing["cpts"])
                why = ("it is the deepest" if which == "deepest"
                       else "it is the CPT at E 512300 / N 181200")
                lay = "; ".join(f"{l['depth_from_m']:g}-{l['depth_to_m']:g} m {l['sbt']} (qc mean "
                                f"{l['qc_mpa']['mean']:g} MPa)" for l in summary["layering"])
                lead = (f"Project CPTs: {ids}. I used {cpt} because {why}.\n"
                        f"{cpt} layering (Robertson SBT interpretation of the CPT, not a borehole log): {lay}.\n")
                return self._pile_answer(res, lead=lead)
            self.trajectory(category="correct_request", stratum="pile_multiturn", template=f"T{i % 4}",
                            prompt=prompt, fixture=SP.FIXTURE, calls=calls, answer_fn=answer,
                            final_values_fn=self._pile_values,
                            final_mentions=[[cpt.lower()], METHOD_MENTIONS[method], ["sbt", "layering", "robertson"]])

    # =================================================================== CPT listing / summary
    @staticmethod
    def _list_answer(res: Dict[str, Any]) -> str:
        if not res["count"]:
            return ("No usable CPT is loaded in the current project, so there is nothing to list or calculate from yet. "
                    "Load a CPT table with depth and qc columns and units in the headers (e.g. 'z [m]', 'qc [MPa]', "
                    "'fs [kPa]', 'u2 [kPa]') or an AGS file with an SCPT group, and ask again.")
        lines = [f"The project has {res['count']} CPTs (from `list_project_cpts`):"]
        for c in res["cpts"]:
            gw = f", groundwater {c['groundwater_depth_m']:g} m" if c.get("groundwater_depth_m") is not None else ""
            lines.append(f"- {c['cpt_id']}: {c['depth_range_m'][0]:g}-{c['depth_range_m'][1]:g} m, "
                         f"{c['n_points']} readings, channels {', '.join(c['channels'])}{gw} ({c['source']})")
        lines.append("I can summarise any of them or use one for a CPT-based calculation.")
        return "\n".join(lines)

    @staticmethod
    def _summary_answer(res: Dict[str, Any]) -> str:
        src = res["provenance"]["source"]
        lines = [f"{res['cpt_id']}: {res['depth_range_m'][0]:g}-{res['depth_range_m'][1]:g} m, {res['n_points']} "
                 f"readings, channels {', '.join(res['channels'])} ({src['object_type']} '{src['object_name']}', "
                 f"qc column '{src['columns']['qc']}').",
                 "Soil behaviour type layering (Robertson SBT interpretation of the CPT, not a borehole log):"]
        for l in res["layering"]:
            lines.append(f"- {l['depth_from_m']:g}-{l['depth_to_m']:g} m: {l['sbt']} (zone {l['sbt_zone']}, Ic "
                         f"{l['ic_mean']:g}), qc {l['qc_mpa']['min']:g}-{l['qc_mpa']['max']:g} MPa (mean "
                         f"{l['qc_mpa']['mean']:g} MPa)")
        flags = res["data_quality_flags"]
        lines.append("Data quality: " + ("; ".join(flags) if flags else "no flags raised."))
        if src["columns"]["qc"].endswith("[kPa]"):
            lines.append("qc was stored in kPa and converted deterministically to MPa.")
        return "\n".join(lines)

    def build_cpt_tools(self):
        rng = self.rng
        list_prompts = [
            "Which CPTs do we have in this project?", "List the cone penetration tests that are loaded.",
            "What CPT data is available for the site?", "How many CPTs are there and how deep do they go?",
            "Show me the CPT soundings in the current project.", "Do we have any CPTs? Which ones have pore pressure?",
            "what cpts are in the workspace", "Give me an overview of the CPT locations in the project.",
        ]
        for i, prompt in enumerate(list_prompts[: self.n(8, 4)]):
            self.trajectory(category="correct_request", stratum=LIST, template=f"L{i}", prompt=prompt,
                            fixture=SP.FIXTURE, calls=[(LIST, {})], answer_fn=lambda ex: self._list_answer(ex[0][2]),
                            final_values_fn=lambda ex: ({"count": float(ex[0][2]["count"])}, {"count": "-"}),
                            final_mentions=[["cpt-01"], ["cpt-02"], ["cpt-03"]])
        for i, prompt in enumerate(["Which CPTs do we have?", "List the CPTs in the project and their depths.",
                                    "Use the project CPTs - which are available?"][: self.n(3, 2)]):
            self.trajectory(category="tool_failure", stratum="no_cpts_loaded", template=f"E{i}", prompt=prompt,
                            fixture=SP.EMPTY, calls=[(LIST, {})], answer_fn=lambda ex: self._list_answer(ex[0][2]),
                            final_mentions=[["no usable cpt", "no cpt", "not loaded", "none"], ["load", "import", "upload"]])
        summary_frames = [
            "Summarise {c}.", "What soil layers does {c} show?", "Any data quality issues with {c}?",
            "Give me the soil behaviour type layering at {c}.", "Describe the stratigraphy from {c} with qc ranges.",
            "What does {c} tell us about the ground?", "Interpret {c} for me - layers and cone resistance.",
            "Can you check {c} and summarise the SBT intervals?", "{c}: layering, channels and QA flags please.",
            "Quick summary of {c}?",
        ]
        cpts = ["CPT-01", "CPT-02", "CPT-03"]
        for i in range(self.n(10, 5)):
            c = cpts[i % 3]
            prompt = summary_frames[i % len(summary_frames)].format(c=c)
            self.trajectory(category="correct_request", stratum=SUMMARY, template=f"S{i % 10}", prompt=prompt,
                            fixture=SP.FIXTURE, calls=[(SUMMARY, {"cpt_id": c})],
                            answer_fn=lambda ex: self._summary_answer(ex[0][2]),
                            final_mentions=[[c.lower()], ["sbt", "soil behaviour", "robertson"], ["mpa"]])
        for i in range(self.n(3, 2)):
            c = rng.choice(("CPT-05", "CPT-09", "CPT-14"))
            prompt = summary_frames[(i + 3) % len(summary_frames)].format(c=c)

            def answer(ex, c=c):
                return (f"{c} is not in the current project; the tool reports the available CPTs are CPT-01, CPT-02 and "
                        f"CPT-03. Did you mean one of those, or can you import {c}? I won't describe a CPT I don't have.")
            self.trajectory(category="tool_failure", stratum="cpt_summary_not_found", template=f"X{i}", prompt=prompt,
                            fixture=SP.FIXTURE, calls=[(SUMMARY, {"cpt_id": c})], expect_error_at=0, answer_fn=answer,
                            final_mentions=[[c.lower()], ["not in", "not found", "not available"], ["cpt-01", "cpt-02", "cpt-03"]])

    # =================================================================== shallow foundations
    def _footing(self, shape: str, b: float, l: Optional[float] = None, b_text: Optional[str] = None) -> Tuple[str, Dict[str, Any]]:
        bt = b_text or f"{_fmt(b)} m"
        rng = self.rng
        if shape == "square":
            text = rng.choice((f"a {bt} square pad", f"a {bt} x {bt} square footing" if not b_text else f"a {bt} square footing"))
        elif shape == "strip":
            text = rng.choice((f"a {bt} wide strip footing", f"a strip footing of width {bt}"))
        elif shape == "rectangular":
            text = f"a {bt} x {_fmt(l)} m rectangular pad"
        else:
            text = rng.choice((f"a {bt} diameter circular footing", f"a circular base of {bt} diameter"))
        args: Dict[str, Any] = {"foundation_shape": shape, "width_m": b}
        if shape == "rectangular":
            args["length_m"] = l
        return text, args

    def _depth_text(self, df: float, df_text: Optional[str] = None) -> str:
        t = df_text or f"{_fmt(df)} m"
        return self.rng.choice((f"at {t} depth", f"founded {t} below ground", f"with Df = {t}", f"embedded {t}"))

    def _cap_answer(self, res: Dict[str, Any]) -> str:
        cap = (f"- Ultimate vertical capacity Q_ult = {_sig(res['Q_ult_kn_per_m'])} kN/m (per metre run)"
               if res.get("Q_ult_kn_per_m") is not None else f"- Ultimate vertical capacity Q_ult = {_sig(res['Q_ult_kn'])} kN")
        params = "; ".join(_param_text(k, v) for k, v in res["soil_parameters"].items())
        lines = [f"Result from `calculate_shallow_foundation_capacity` ({res['analysis']} analysis, API RP 2GEO bearing "
                 f"capacity via Groundhog):",
                 f"- Ultimate bearing pressure q_ult = {_sig(res['q_ult_kpa'])} kPa ({res['bearing_pressure_basis']})",
                 cap, "", f"Soil parameters used: {params}."]
        if res.get("warnings"):
            lines.append("Warnings: " + " ".join(res["warnings"][:2]))
        lines.append("These are ultimate (unfactored) values; factors of safety or partial factors, settlement and the "
                     "design decision are separate engineering steps.")
        return "\n".join(lines)

    @staticmethod
    def _cap_values(ex) -> Tuple[Dict[str, float], Dict[str, str]]:
        res = ex[-1][2]
        vals = {"q_ult_kpa": float(res["q_ult_kpa"])}
        units = {"q_ult_kpa": "kPa"}
        if res.get("Q_ult_kn") is not None:
            vals["Q_ult_kn"], units["Q_ult_kn"] = float(res["Q_ult_kn"]), "kN"
        elif res.get("Q_ult_kn_per_m") is not None:
            vals["Q_ult_kn_per_m"], units["Q_ult_kn_per_m"] = float(res["Q_ult_kn_per_m"]), "kN/m"
        return vals, units

    def _cap_case(self, analysis: str) -> Dict[str, Any]:
        rng = self.rng
        shape = rng.choice(("square", "strip", "rectangular", "circular"))
        b = rng.choice((1.0, 1.2, 1.5, 1.8, 2.0, 2.5, 3.0))
        l = round(b * rng.choice((1.5, 2.0, 2.5)), 1) if shape == "rectangular" else None
        case = {"shape": shape, "b": b, "l": l, "df": rng.choice((0.5, 0.8, 1.0, 1.2, 1.5, 2.0))}
        case["gamma"] = round(rng.uniform(17.0, 20.0), 1)
        if analysis == "drained":
            case["phi"] = float(rng.randint(28, 38))
            case["gwt"] = rng.choice((1.0, 1.5, 2.0, 3.0, 4.0, 6.0))
        else:
            case["su"] = float(rng.choice((25, 30, 40, 50, 60, 75, 90, 120)))
        return case

    def _cap_prompt(self, idx: int, footing: str, depth: str, soil: str) -> str:
        frames = [
            f"What's the ultimate bearing capacity of {footing} {depth}? {soil}.",
            f"Calculate the bearing capacity of {footing} {depth} on {soil}.",
            f"Bearing capacity check: {footing} {depth}; {soil}.",
            f"Can you work out q_ult for {footing} {depth}? Ground: {soil}.",
            f"How much vertical load can {footing} {depth} take (ultimate)? {soil}.",
            f"I need the ultimate capacity of {footing} {depth}, {soil}.",
        ]
        return _clean(frames[idx % len(frames)])

    def _cap_soil(self, case: Dict[str, Any], analysis: str, texts: Optional[Dict[str, str]] = None,
                  omit: Sequence[str] = ()) -> Tuple[str, Dict[str, Any]]:
        t = texts or {}
        args: Dict[str, Any] = {}
        bits = []
        if analysis == "drained":
            bits.append("sand")
            if "phi" not in omit:
                bits.append(f"phi' = {_fmt(case['phi'], 0)}°")
                args["friction_angle_deg"] = case["phi"]
        else:
            bits.append("clay")
            if "su" not in omit:
                bits.append(f"su = {t.get('su', _fmt(case['su'], 0) + ' kPa')}")
                args["undrained_shear_strength_kpa"] = case["su"]
        if "gamma" not in omit:
            bits.append(f"gamma = {t.get('gamma', _fmt(case['gamma'], 1) + ' kN/m3')}")
            args["unit_weight_kn_m3"] = case["gamma"]
        if analysis == "drained" and "gwt" not in omit:
            bits.append(f"groundwater {_fmt(case['gwt'])} m below ground")
            args["groundwater_depth_m"] = case["gwt"]
        return bits[0] + " with " + ", ".join(bits[1:]) if len(bits) > 1 else bits[0], args

    def build_shallow_capacity(self):
        rng = self.rng
        # -------- correct requests, inputs stated (empty project: nothing is looked up)
        for i in range(self.n(12, 6)):
            analysis = "drained" if i % 2 == 0 else "undrained"
            c = self._cap_case(analysis)
            ftxt, fargs = self._footing(c["shape"], c["b"], c["l"])
            soil, sargs = self._cap_soil(c, analysis)
            args = dict(fargs, foundation_depth_m=c["df"], **sargs)
            prompt = self._cap_prompt(i, ftxt, self._depth_text(c["df"]), soil)
            self.trajectory(category="correct_request", stratum=CAP, template=f"C{i % 6}", prompt=prompt,
                            fixture=SP.EMPTY, calls=[(CAP, args)], answer_fn=lambda ex: self._cap_answer(ex[-1][2]),
                            final_values_fn=self._cap_values, final_mentions=[["ultimate", "unfactored"]])
        # -------- project soil profile supplies the soil parameters (with provenance)
        geoms = [("undrained", "square", 2.0, None, 4.5), ("undrained", "strip", 1.5, None, 5.0),
                 ("undrained", "rectangular", 2.0, 4.0, 4.0), ("undrained", "circular", 3.0, None, 5.0),
                 ("drained", "square", 1.5, None, 1.0), ("drained", "strip", 1.2, None, 0.8),
                 ("drained", "rectangular", 1.5, 3.0, 1.0), ("drained", "circular", 1.8, None, 1.0)]
        frames = ["Using the project soil profile, what's the {a} bearing capacity of {f} {d}?",
                  "Calculate the {a} bearing capacity of {f} {d} for the current project.",
                  "Take the soil parameters from BH-01: {a} capacity of {f} {d}.",
                  "{F} {d} - {a} ultimate bearing capacity from the project data please."]
        for i, (analysis, shape, b, l, df) in enumerate(geoms[: self.n(8, 4)]):
            ftxt, fargs = self._footing(shape, b, l)
            prompt = _clean(frames[i % 4].format(a=analysis, f=ftxt, F=ftxt[:1].upper() + ftxt[1:], d=self._depth_text(df)))
            args = dict(fargs, foundation_depth_m=df, analysis=analysis)
            self.trajectory(category="correct_request", stratum=CAP, template=f"P{i % 4}", prompt=prompt,
                            fixture=SP.FIXTURE, calls=[(CAP, args)], answer_fn=lambda ex: self._cap_answer(ex[-1][2]),
                            final_values_fn=self._cap_values, final_mentions=[["bh-01"], ["ultimate", "unfactored"]])
        # -------- missing data -> clarify (empty project: nothing to take the value from)
        drops = [("phi", "drained", "friction_angle_deg", ["friction angle", "phi"]),
                 ("su", "undrained", "undrained_shear_strength_kpa", ["undrained shear strength", "su", "cu"]),
                 ("gwt", "drained", "groundwater_depth_m", ["groundwater", "water table", "water level"]),
                 ("gamma", "undrained", "unit_weight_kn_m3", ["unit weight", "gamma"]),
                 ("width", "undrained", "width_m", ["width", "size", "dimension", "diameter"])]
        for i in range(self.n(10, 5)):
            key, analysis, field, kws = drops[i % len(drops)]
            c = self._cap_case(analysis)
            if key == "gamma":
                c["df"] = max(c["df"], 1.0)
            ftxt, fargs = self._footing(c["shape"], c["b"], c["l"])
            soil, sargs = self._cap_soil(c, analysis, omit=(key,))
            present = dict(fargs, foundation_depth_m=c["df"], **sargs)
            if key == "width":
                present.pop("width_m")
                present.pop("length_m", None)
                ftxt = {"square": "a square pad", "strip": "a strip footing", "rectangular": "a rectangular pad",
                        "circular": "a circular footing"}[c["shape"]]
            prompt = self._cap_prompt(i + 1, ftxt, self._depth_text(c["df"]), soil)
            label = {"friction_angle_deg": "effective friction angle phi' (deg)",
                     "undrained_shear_strength_kpa": "undrained shear strength su (kPa)",
                     "groundwater_depth_m": "groundwater depth below ground (m)",
                     "unit_weight_kn_m3": "soil unit weight gamma (kN/m3)",
                     "width_m": "footing width B (m)"}[field]
            ref = (f"To calculate the bearing capacity I also need the {label}, which is not given and there is no "
                   f"project soil profile to take it from. Could you provide it? I won't assume a typical value.")
            self.clarify(category="missing_data", stratum=CAP, template=f"M{i % 5}", prompt=prompt, fixture=SP.EMPTY,
                         tool=CAP, present=present, missing=[field], keywords=[kws + [field]], reference=ref)
        # -------- the project profile cannot supply phi' over clay -> tool asks for it
        for i, (shape, b, df) in enumerate([("square", 2.0, 5.0), ("strip", 1.5, 4.5), ("circular", 2.5, 6.0)][: self.n(3, 2)]):
            ftxt, fargs = self._footing(shape, b)
            prompt = _clean(f"Drained bearing capacity of {ftxt} {self._depth_text(df)} using the project soil profile.")
            args = dict(fargs, foundation_depth_m=df, analysis="drained")
            self.trajectory(category="tool_failure", stratum="cap_project_missing_phi", template=f"G{i}", prompt=prompt,
                            fixture=SP.FIXTURE, calls=[(CAP, args)], expect_error_at=0,
                            answer_fn=lambda ex: ("I could not run the drained calculation: the project profile BH-01 has "
                                                  "no effective friction angle over the zone below this footing (it is "
                                                  "soft clay there), and I won't assume one. Could you give me phi' for "
                                                  "a drained check, or should I run an undrained analysis with su from "
                                                  "BH-01 instead?"),
                            final_mentions=[["friction angle", "phi"], ["clay"], ["undrained", "provide", "give me"]])
        # -------- unit traps
        for i in range(self.n(6, 3)):
            kind = ("mm", "mpa", "mm")[i % 3]
            analysis = "undrained" if kind == "mpa" else rng.choice(("drained", "undrained"))
            c = self._cap_case(analysis)
            texts, trained_over = {}, {}
            if kind == "mm":
                given = f"{int(round(c['b'] * 1000))} mm"
                ftxt, fargs = self._footing(c["shape"], c["b"], c["l"], b_text=given)
                trained_over["width_m"], param = given, "width_m"
            else:
                given = f"{_fmt(c['su'] / 1000.0, 3)} MPa"
                texts["su"] = given
                ftxt, fargs = self._footing(c["shape"], c["b"], c["l"])
                trained_over["undrained_shear_strength_kpa"], param = given, "undrained_shear_strength_kpa"
            soil, sargs = self._cap_soil(c, analysis, texts=texts)
            args = dict(fargs, foundation_depth_m=c["df"], **sargs)
            trained = dict(args, **trained_over)
            expected = self._expected(CAP, trained)
            if expected is None or not values_match(args[param], expected[param], rel_tol=1e-6):
                self.g.dropped["wrong_units:normalisation_mismatch"] += 1
                continue
            prompt = self._cap_prompt(i + 2, ftxt, self._depth_text(c["df"]), soil)
            self.trajectory(category="wrong_units", stratum=CAP, template=f"U{i % 3}", prompt=prompt,
                            fixture=SP.EMPTY, calls=[(CAP, trained)], expected_first=expected,
                            unit_trap={"param": param, "kind": "convertible", "given": given},
                            answer_fn=lambda ex: self._cap_answer(ex[-1][2]), final_values_fn=self._cap_values)
        for i in range(self.n(3, 2)):                                   # dimension traps: gamma in kPa, su in kN
            analysis = "undrained"
            c = self._cap_case(analysis)
            param, wrong = (("unit_weight_kn_m3", "kPa"), ("undrained_shear_strength_kpa", "kN"))[i % 2]
            num = _fmt(c["gamma"], 1) if param == "unit_weight_kn_m3" else _fmt(c["su"], 0)
            given = f"{num} {wrong}"
            texts = {"gamma": given} if param == "unit_weight_kn_m3" else {"su": given}
            ftxt, fargs = self._footing(c["shape"], c["b"], c["l"])
            soil, sargs = self._cap_soil(c, analysis, texts=texts)
            bad = dict(fargs, foundation_depth_m=c["df"], **sargs)
            bad[param] = given
            canon = "kN/m3" if param == "unit_weight_kn_m3" else "kPa"
            name = "unit weight gamma" if param == "unit_weight_kn_m3" else "undrained shear strength su"
            prompt = self._cap_prompt(i + 4, ftxt, self._depth_text(c["df"]), soil)
            ref = (f"Unit problem: the {name} was given as {given}, but '{wrong}' is not a valid unit for this quantity "
                   f"(expected {canon}). Did you mean {num} {canon}? Please confirm before I run the calculation.")
            self.clarify(category="wrong_units", stratum=CAP, template=f"D{i % 2}", prompt=prompt, fixture=SP.EMPTY,
                         tool=CAP, present=bad, missing=[], provided=[k for k in bad if k != param],
                         keywords=[[name.split()[-1], param, "unit weight" if canon == "kN/m3" else "shear strength"],
                                   ["unit", wrong.lower(), canon.lower()]],
                         reference=ref, unit_trap={"param": param, "kind": "dimension_mismatch", "given": given})
        # -------- conflicting data
        srcs = [("the lab UU testing", "the CPT correlation"), ("BH-01", "BH-02"), ("the 2019 report", "the 2024 GIR")]
        for i in range(self.n(4, 2)):
            c = self._cap_case("undrained")
            su2 = float(round(c["su"] * rng.choice((0.7, 1.3, 1.4))))
            s1, s2 = srcs[i % len(srcs)]
            ftxt, fargs = self._footing(c["shape"], c["b"], c["l"])
            prompt = _clean(f"According to {s1}, su = {_fmt(c['su'], 0)} kPa, but {s2} gives "
                            f"{_fmt(su2, 0)} kPa. Undrained bearing capacity of {ftxt} {self._depth_text(c['df'])}, "
                            f"gamma = {_fmt(c['gamma'], 1)} kN/m3.")
            ref = (f"The inputs conflict: {s1} gives su = {_fmt(c['su'], 0)} kPa whereas {s2} gives {_fmt(su2, 0)} kPa. "
                   f"Which value should I adopt? I can also run both to show the sensitivity, but I won't pick one silently.")
            self.clarify(category="conflicting_data", stratum=CAP, template=f"X{i % 3}", prompt=prompt,
                         fixture=SP.EMPTY, tool=CAP, present={}, missing=[], check_refused=False,
                         acceptable_actions=["synthesize"],
                         keywords=[["su", "undrained shear strength"],
                                   ["which", "confirm", "both", "either", "sensitiv", "choose", "adopt"]],
                         reference=ref)

    # =================================================================== settlement
    def _set_answer(self, res: Dict[str, Any]) -> str:
        layers = "; ".join(f"{l['layer']}: {_sig(l['settlement_mm'])} mm ({l['method']})" for l in res["compressible_layers"])
        params = "; ".join(_param_text(k, v) for k, v in list(res["soil_parameters"].items())[:6])
        lines = [f"Result from `calculate_foundation_settlement` (1D primary consolidation, Groundhog routines):",
                 f"- Calculated primary consolidation settlement = {_sig(res['settlement_mm'])} mm below the footing centre",
                 f"- Gross pressure {_sig(res['applied_pressure_kpa'])} kPa, net pressure {_sig(res['net_pressure_kpa'])} kPa",
                 f"- Per layer: {layers}", "", f"Parameters: {params}."]
        if res.get("warnings"):
            lines.append("Warnings: " + " ".join(res["warnings"][:2]))
        lines.append("Immediate (elastic) and secondary compression settlement are not included, and whether this "
                     "settlement is acceptable is a separate engineering judgement.")
        return "\n".join(lines)

    @staticmethod
    def _set_values(ex) -> Tuple[Dict[str, float], Dict[str, str]]:
        return {"settlement_mm": float(ex[-1][2]["settlement_mm"])}, {"settlement_mm": "mm"}

    def _set_case(self, mv: bool = False) -> Dict[str, Any]:
        rng = self.rng
        c = {"shape": rng.choice(("square", "strip", "rectangular", "circular")),
             "b": rng.choice((1.5, 2.0, 2.5, 3.0)), "df": rng.choice((0.8, 1.0, 1.5)),
             "q": float(rng.choice((80, 100, 120, 150, 180, 200, 250))),
             "top": rng.choice((2.0, 2.5, 3.0)), "gamma": round(rng.uniform(17.0, 19.5), 1)}
        c["l"] = round(c["b"] * 2, 1) if c["shape"] == "rectangular" else None
        c["bottom"] = c["top"] + rng.choice((3.0, 4.0, 5.0, 6.0))
        if mv:
            c["mv"] = rng.choice((0.0002, 0.0003, 0.0005, 0.0008))
        else:
            c["cc"] = rng.choice((0.2, 0.25, 0.3, 0.4, 0.5))
            c["e0"] = rng.choice((0.8, 1.0, 1.2, 1.4))
            c["gwt"] = rng.choice((1.0, 1.5, 2.0))
        return c

    def _set_parts(self, c: Dict[str, Any], texts: Optional[Dict[str, str]] = None,
                   omit: Sequence[str] = ()) -> Tuple[str, Dict[str, Any]]:
        t = texts or {}
        args: Dict[str, Any] = {"clay_top_depth_m": c["top"], "clay_bottom_depth_m": c["bottom"]}
        bits = [f"clay from {_fmt(c['top'])} m to {_fmt(c['bottom'])} m"]
        if "mv" in c:
            bits.append(f"mv = {c['mv']:g} m2/kN")
            args["mv_per_kpa"] = c["mv"]
        else:
            if "cc" not in omit:
                bits.append(f"Cc = {_fmt(c['cc'])}")
                args["compression_index"] = c["cc"]
            if "e0" not in omit:
                bits.append(f"e0 = {_fmt(c['e0'])}")
                args["initial_void_ratio"] = c["e0"]
            bits.append("OCR = 1 (normally consolidated)")
            args["ocr"] = 1.0
            bits.append(f"water table at {_fmt(c['gwt'])} m")
            args["groundwater_depth_m"] = c["gwt"]
        bits.append(f"gamma = {t.get('gamma', _fmt(c['gamma'], 1) + ' kN/m3')}")
        args["unit_weight_kn_m3"] = c["gamma"]
        return ", ".join(bits), args

    def _set_prompt(self, idx: int, footing: str, depth: str, load: str, soil: str) -> str:
        frames = [
            f"How much will {footing} {depth} settle under {load}? {soil}.",
            f"Calculate the consolidation settlement of {footing} {depth} carrying {load}; {soil}.",
            f"Settlement check for {footing} {depth}, {load}: {soil}.",
            f"Estimate the primary consolidation settlement: {footing} {depth}, {load}, {soil}.",
            f"What settlement do we get for {footing} {depth} with {load}? Soil: {soil}.",
        ]
        return _clean(frames[idx % len(frames)])

    def build_settlement(self):
        rng = self.rng
        for i in range(self.n(8, 4)):
            c = self._set_case(mv=(i % 4 == 3))
            ftxt, fargs = self._footing(c["shape"], c["b"], c["l"])
            soil, sargs = self._set_parts(c)
            args = dict(fargs, foundation_depth_m=c["df"], applied_pressure_kpa=c["q"], **sargs)
            prompt = self._set_prompt(i, ftxt, self._depth_text(c["df"]), f"{_fmt(c['q'], 0)} kPa", soil)
            self.trajectory(category="correct_request", stratum=SET, template=f"C{i % 5}", prompt=prompt,
                            fixture=SP.EMPTY, calls=[(SET, args)], answer_fn=lambda ex: self._set_answer(ex[-1][2]),
                            final_values_fn=self._set_values, final_mentions=[["primary consolidation", "consolidation"]])
        frames = ["How much will {f} {d} settle under {q} in the current project?",
                  "Using the project soil profile, calculate the settlement of {f} {d} with a bearing pressure of {q}.",
                  "Settlement of {f} {d} for {q}, take the clay parameters from BH-01.",
                  "{F} {d} carrying {q}: consolidation settlement from the project data please."]
        for i in range(self.n(6, 3)):
            shape = ("square", "strip", "rectangular", "circular")[i % 4]
            b = rng.choice((1.5, 2.0, 2.5))
            ftxt, fargs = self._footing(shape, b, round(b * 2, 1) if shape == "rectangular" else None)
            df = rng.choice((1.0, 1.5))
            q = float(rng.choice((100, 120, 150, 200)))
            prompt = _clean(frames[i % 4].format(f=ftxt, F=ftxt[:1].upper() + ftxt[1:], d=self._depth_text(df),
                                                 q=f"{_fmt(q, 0)} kPa"))
            args = dict(fargs, foundation_depth_m=df, applied_pressure_kpa=q)
            self.trajectory(category="correct_request", stratum=SET, template=f"P{i % 4}", prompt=prompt,
                            fixture=SP.FIXTURE, calls=[(SET, args)], answer_fn=lambda ex: self._set_answer(ex[-1][2]),
                            final_values_fn=self._set_values, final_mentions=[["bh-01"], ["soft clay"]])
        drops = [("q", "applied_pressure_kpa", ["pressure", "load"], "applied bearing pressure (kPa) or the vertical load (kN)"),
                 ("cc", "compression_index", ["compression index", "cc"], "compression index Cc"),
                 ("e0", "initial_void_ratio", ["void ratio", "e0"], "initial void ratio e0")]
        for i in range(self.n(8, 3)):
            key, field, kws, label = drops[i % 3]
            c = self._set_case()
            ftxt, fargs = self._footing(c["shape"], c["b"], c["l"])
            soil, sargs = self._set_parts(c, omit=(key,))
            present = dict(fargs, foundation_depth_m=c["df"], **sargs)
            load = "its load"
            if key != "q":
                present["applied_pressure_kpa"] = c["q"]
                load = f"{_fmt(c['q'], 0)} kPa"
            prompt = self._set_prompt(i + 1, ftxt, self._depth_text(c["df"]), load, soil)
            ref = (f"To calculate the settlement I also need the {label}, which is not given (and there is no project "
                   f"soil profile to take it from). Could you provide it? I won't assume a value.")
            self.clarify(category="missing_data", stratum=SET, template=f"M{i % 3}", prompt=prompt, fixture=SP.EMPTY,
                         tool=SET, present=present, missing=[field], keywords=[kws + [field]], reference=ref)
        for i in range(self.n(5, 2)):
            c = self._set_case()
            kind = ("mpa", "mm")[i % 2]
            ftxt, fargs = self._footing(c["shape"], c["b"], c["l"],
                                        b_text=f"{int(round(c['b'] * 1000))} mm" if kind == "mm" else None)
            soil, sargs = self._set_parts(c)
            args = dict(fargs, foundation_depth_m=c["df"], applied_pressure_kpa=c["q"], **sargs)
            if kind == "mpa":
                given, param = f"{_fmt(c['q'] / 1000.0, 3)} MPa", "applied_pressure_kpa"
            else:
                given, param = f"{int(round(c['b'] * 1000))} mm", "width_m"
            trained = dict(args, **{param: given})
            expected = self._expected(SET, trained)
            if expected is None or not values_match(args[param], expected[param], rel_tol=1e-6):
                self.g.dropped["wrong_units:normalisation_mismatch"] += 1
                continue
            load = given if kind == "mpa" else f"{_fmt(c['q'], 0)} kPa"
            prompt = self._set_prompt(i + 3, ftxt, self._depth_text(c["df"]), load, soil)
            self.trajectory(category="wrong_units", stratum=SET, template=f"U{i % 2}", prompt=prompt,
                            fixture=SP.EMPTY, calls=[(SET, trained)], expected_first=expected,
                            unit_trap={"param": param, "kind": "convertible", "given": given},
                            answer_fn=lambda ex: self._set_answer(ex[-1][2]), final_values_fn=self._set_values)
        prompts = [("How much will the building settle?", [["footing", "foundation", "size", "width", "dimension"],
                                                           ["load", "pressure"]]),
                   ("Work out the foundation capacity for the current project.",
                    [["pile", "shallow", "footing", "which", "type"], ["size", "width", "diameter", "dimension", "geometry"]]),
                   ("Bearing capacity for the project please.", [["size", "width", "dimension", "shape"],
                                                                 ["depth", "embedment", "founded"]])]
        for pi, (p, kws) in enumerate(prompts):
            ref = ("I can calculate this from the project soil profile BH-01, but I need the foundation geometry "
                   "(type, shape, width/size and founding depth) and, for settlement, the applied load or pressure. "
                   "Which values should I use?")
            self.clarify(category="ambiguous_request", stratum="shallow_project_vague", template=f"A{pi}", prompt=p,
                         fixture=SP.FIXTURE, tool=SET if pi == 0 else CAP, present={}, missing=[], keywords=kws,
                         reference=ref, check_refused=False)


def build_project_tool_examples(g, seed: int, per_tool: int = FULL_SIZE_PER_TOOL) -> Counter:
    """Append the project-data tool drafts to generator ``g``; returns counts per (category, stratum)."""
    missing = [t for t in PROJECT_TOOLS if g._tool(t) is None]
    if missing:
        for t in missing:
            g.skipped[t] = "not registered"
        return Counter()
    b = ProjectToolExamples(g, seed, per_tool)
    b.build_piles()
    b.build_cpt_tools()
    b.build_shallow_capacity()
    b.build_settlement()
    return b.made
