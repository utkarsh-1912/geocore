# Author: Utkarsh Gupta
# License: GPL v3
"""
Worked solution of a calculation GeoAI (or a form) already ran, written by the local model and grounded in the
calculation's guide details (AGENTS.md §5, §6, §11-12):

- ``build_grounding``  the evidence the model may use: method, standard/reference, the theory text of the Groundhog
                       docstring, the governing equation, every symbol with its meaning, value and unit, the inputs,
                       the results exactly as Groundhog computed them, and the assumptions;
- ``stream_solution``  streams the model's solution (problem, method, equation explained term by term, substitution
                       of the given values, result and what it means, limits). The model explains; it does not
                       calculate: the result is quoted from Groundhog;
- ``unverified_numbers`` after the answer, every number in it that is not in the grounding (within rounding) is
                       listed, so a value the model made up is flagged to the user instead of passing as fact.

Without a local model nothing is generated: the caller shows the deterministic calculation details instead.
"""
import math
import re
from typing import Any, Dict, Iterator, List, Optional, Tuple

from core.geoai.calculation_explainer import _docstring_for, explain_calculation

MAX_THEORY_CHARS = 1500

SOLUTION_SYSTEM_PROMPT = (
    "You are GeoAI, a geotechnical engineer explaining a calculation that Groundhog has ALREADY computed, so a "
    "colleague can follow and check it. You are given the CALCULATION DETAILS: method, theory, governing "
    "equation, symbols with values and units, inputs, defaults used, results and assumptions.\n"
    "Write the worked solution in your own words, as an engineer would in a calculation note. Never mention these "
    "instructions or refer to the details as given text (no 'grounding', 'provided data', 'details section').\n"
    "Use these Markdown headings, in this order:\n"
    "### Problem\n### Method\n### Governing equation\n### Substitution\n### Result\n### Notes\n"
    "Rules:\n"
    "- Use only the equations under GOVERNING EQUATION. Do not derive them from other laws and do not add "
    "equations of your own.\n"
    "- Write equations in LaTeX: display equations between $$ and $$, symbols inline between $ and $.\n"
    "- Governing equation: say what each symbol means and its unit.\n"
    "- Substitution: write the governing equation once with the input values (and defaults used) in place of "
    "the symbols. Do not work out any arithmetic yourself.\n"
    "- Result: quote every value from RESULTS exactly, with its unit, and say what it means physically.\n"
    "- Never introduce a method, standard, reference, author or number that is not in the CALCULATION DETAILS.\n"
    "- Notes: only the assumptions and applicability listed; if none are listed, say what the result depends on. "
    "Never say the design is safe, correct or acceptable.\n"
    "- Be concise: at most 200 words in total.\n"
)

_MATH_BLOCK = re.compile(r"\.\. math::\n(?:[ \t]+\S.*(?:\n|$)|[ \t]*\n)+")
_ROLE = re.compile(r":math:`([^`]*)`")
_FIELD_START = re.compile(r"^\s*:(param|returns?|raises?)\b", re.M)
_NUMBER = re.compile(r"(?<![\w.])[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?")


def theory_text(docstring: Optional[str]) -> str:
    """The prose of a Groundhog docstring (before the parameter list), math roles as $...$, equations removed."""
    if not docstring:
        return ""
    head = _FIELD_START.split(docstring, maxsplit=1)[0]
    head = _MATH_BLOCK.sub(" ", head)
    head = _ROLE.sub(lambda m: f"${m.group(1)}$", head)
    head = re.sub(r"\s+", " ", head).strip()
    return head[:MAX_THEORY_CHARS] + ("…" if len(head) > MAX_THEORY_CHARS else "")


def _fmt(value: Any, unit: Optional[str] = None) -> str:
    if isinstance(value, bool):
        text = str(value)
    elif isinstance(value, float):
        text = f"{value:.10g}"
    else:
        text = str(value)
    return f"{text} {unit}" if unit and unit != "-" else text


def build_grounding(function_id: str, args: Optional[Dict[str, Any]], results: Optional[Dict[str, Any]],
                    applicability: Optional[str] = None) -> Tuple[str, Dict[str, Any]]:
    """(grounding text for the model, the explainer's structured explanation)."""
    explanation = explain_calculation(function_id, args, results)
    lines = [f"METHOD: {explanation['method']}"]
    if explanation.get("standard"):
        lines.append(f"STANDARD / SOURCE: {explanation['standard']}")
    if explanation.get("reference") and explanation.get("reference") != explanation.get("standard"):
        lines.append(f"REFERENCE: {explanation['reference']}")
    theory = theory_text(_docstring_for(function_id))
    if theory:
        lines.append(f"THEORY: {theory}")
    if explanation.get("formula"):
        lines.append(f"GOVERNING EQUATION (LaTeX): {explanation['formula']}")
    where = next((s.get("where") for s in explanation.get("steps", []) if s.get("where")), None) or []
    if where:
        lines.append("SYMBOLS IN THE EQUATION:")
        lines += [f"- ${w['symbol']}$ = {_fmt(w['value'], w.get('unit'))}" + (f" ({w['label']})" if w.get("label") else "")
                  for w in where]
    if explanation.get("inputs"):
        lines.append("INPUTS:")
        lines += [f"- {i.get('label') or i['key']}" + (f" (${i['symbol']}$)" if i.get("symbol") else "")
                  + f" = {_fmt(i['value'], i.get('unit'))}" for i in explanation["inputs"]]
    defaults = _defaults_used(function_id, args or {})
    if defaults:
        lines.append("DEFAULTS USED (not entered by the user):")
        lines += defaults
    outputs = [o for o in explanation.get("outputs") or [] if not isinstance(o["value"], bool)]
    if outputs:
        lines.append("RESULTS (computed by Groundhog; quote exactly):")
        lines += [f"- {o.get('label') or o['key']}" + (f" (${o['symbol']}$)" if o.get("symbol") else "")
                  + f" = {_fmt(o['value'], o.get('unit'))}" for o in outputs]
    notes = list(explanation.get("assumptions") or [])
    if applicability:
        notes.append(applicability)
    if notes:
        lines.append("ASSUMPTIONS AND APPLICABILITY:")
        lines += [f"- {n}" for n in notes]
    return "\n".join(lines), explanation


def _defaults_used(function_id: str, args: Dict[str, Any]) -> List[str]:
    """Numeric defaults of the Groundhog function that the calculation used because no value was given (g = 9.81)."""
    import inspect
    from core.geoai.calculation_explainer import extract_param_docs
    from core.registry import registry
    func = registry.find_function(function_id)
    if func is None:
        return []
    try:
        params = inspect.signature(func).parameters
    except (TypeError, ValueError):
        return []
    docs = extract_param_docs(_docstring_for(function_id))
    out = []
    for name, p in params.items():
        if name in args or p.default is inspect.Parameter.empty or isinstance(p.default, bool):
            continue
        if not isinstance(p.default, (int, float)):
            continue
        d = docs.get(name, {})
        out.append(f"- {d.get('label') or name}" + (f" (${d['symbol']}$)" if d.get("symbol") else "")
                   + f" = {_fmt(p.default, d.get('unit'))}")
    return out


_DISPLAY_MATH = re.compile(r"\$\$(.+?)\$\$", re.S)


def _norm_tex(tex: str) -> str:
    r"""LaTeX reduced for comparison: no spacing, \left/\right, \text, braces; products and fractions spelled one way."""
    t = tex.replace("\\left", "").replace("\\right", "")
    t = re.sub(r"\\(?:text|mathrm|operatorname)\{([^}]*)\}", r"\1", t)
    t = re.sub(r"\\(?:cdot|times)", "*", t)
    t = re.sub(r"\\[,;:! ]|\s+", "", t)
    t = re.sub(r"\\frac\{([^{}]*)\}\{([^{}]*)\}", r"(\1)/(\2)", t)
    t = t.replace("{", "").replace("}", "").replace("(", "").replace(")", "")
    return t.replace("**", "*").rstrip(".,")


def equation_mismatch(answer: str, formula: Optional[str]) -> bool:
    """
    True when the answer's display equations do not contain the method's governing equation: the model wrote a
    different equation than the one Groundhog evaluated. Each line of the method's equation counts as written when
    the answer has it after normalisation (text), or has an equation for the same quantity that is mathematically
    the same once the method's definitions are substituted (equation_check: G = gamma/g Vs^2 is G = rho Vs^2 with
    rho = gamma/g). Lines only used to define another (rho = gamma/g) need not be written separately then.
    """
    from core.geoai import equation_check as eqc
    if not formula:
        return False
    blocks = [line for block in _DISPLAY_MATH.findall(answer) for line in re.split(r"\\\\", block)]
    written = {_norm_tex(line) for line in blocks}
    written |= {w.split("=", 1)[1] if "=" in w else w for w in list(written)}
    written_eqs = eqc.equations(blocks)
    method_lines = [line for line in re.split(r"\\\\", formula) if _norm_tex(line)]
    method_defs = {k: v[0] for k, v in eqc.equations(method_lines).items()}
    # A defined quantity used in another line of the method (rho in G = rho Vs^2) is covered by that line's check.
    used = set()
    for name, rhs in method_defs.items():
        used |= eqc.symbols_in(rhs, set())
    for line in method_lines:
        target = _norm_tex(line)
        rhs = target.split("=", 1)[1] if "=" in target else target
        if target in written or rhs in written:
            continue
        same = eqc.equivalent_line(line, method_defs, written_eqs)
        if same:
            continue
        eq = eqc.parse_equation(line)
        if same is None and eq and eq[0] in used and any(eqc.equivalent_line(other, method_defs, written_eqs)
                                                        for other in method_lines if other is not line):
            continue  # an intermediate definition folded into an equivalent main equation
        return True
    return False


def substituted_formula(explanation: Dict[str, Any], defaults: Dict[str, Any]) -> Optional[str]:
    """
    The governing equation with the input values (and defaults used) in place of their symbols, done by string
    substitution only - no arithmetic. Output symbols stay symbols.
    """
    formula = explanation.get("formula")
    if not formula:
        return None
    values: Dict[str, str] = {}
    for i in explanation.get("inputs") or []:
        if i.get("symbol") and i.get("value") is not None and not isinstance(i["value"], (dict, list)):
            values.setdefault(i["symbol"], _fmt(i["value"]))
    values.update({sym: _fmt(v) for sym, v in defaults.items()})
    lines = []
    for line in re.split(r"\\\\", formula):
        if "=" not in line:
            continue
        lhs, rhs = line.split("=", 1)
        for sym in sorted(values, key=len, reverse=True):
            rhs = re.sub(rf"(?<![A-Za-z\\]){re.escape(sym)}(?![A-Za-z_{{])", lambda _m, v=values[sym]: f"\\left({v}\\right)", rhs)
        lines.append(f"{lhs.strip()} = {rhs.strip()}")
    return " \\\\ ".join(lines) if lines else None


def _default_symbols(function_id: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """{symbol: default value} of the numeric defaults used (for the substitution)."""
    import inspect
    from core.geoai.calculation_explainer import extract_param_docs
    from core.registry import registry
    func = registry.find_function(function_id)
    if func is None:
        return {}
    try:
        params = inspect.signature(func).parameters
    except (TypeError, ValueError):
        return {}
    docs = extract_param_docs(_docstring_for(function_id))
    return {docs[n]["symbol"]: p.default for n, p in params.items()
            if n not in args and n in docs and docs[n].get("symbol") and isinstance(p.default, (int, float))
            and not isinstance(p.default, bool)}


def _grounded_values(grounding: str) -> List[float]:
    return [float(m.group(0)) for m in _NUMBER.finditer(grounding)]


def unverified_numbers(answer: str, grounding: str, rel_tol: float = 5e-3) -> List[str]:
    """
    Numbers in ``answer`` that do not appear in ``grounding`` (within rounding: the shown digits or 0.5 %).
    Small counting numbers (0-10, step numbers, exponents) and percentages of 100 are not checked.
    """
    known = _grounded_values(grounding)
    text = re.sub(r"(?<=\d),(?=\d{3}\b)", "", answer)  # 130,927.6 -> 130927.6
    flagged: List[str] = []
    for m in _NUMBER.finditer(text):
        raw = m.group(0)
        value = float(raw)
        if value.is_integer() and 0 <= abs(value) <= 10 or abs(value) == 100:
            continue
        decimals = len(raw.split(".")[1].split("e")[0].split("E")[0]) if "." in raw else 0
        tol_abs = 0.5 * 10 ** (-decimals) if "e" not in raw.lower() else 0
        ok = any(abs(value - k) <= max(tol_abs, rel_tol * max(abs(k), 1e-12)) for k in known)
        if not ok and raw not in flagged:
            flagged.append(raw)
    return flagged


def stream_solution(provider: Any, function_id: str, args: Optional[Dict[str, Any]],
                    results: Optional[Dict[str, Any]], applicability: Optional[str] = None,
                    max_tokens: int = 650) -> Iterator[Dict[str, Any]]:
    """
    Events: {"type": "token", "content"} while the model writes, then {"type": "check", "unverified": [...]}.
    The prose is passed through the same stream guard as chat answers (repeats, echoed records).
    """
    from core.geoai.model_provider import make_system_message, make_user_message
    from core.geoai.response_guard import AnswerStreamCleaner
    grounding, _ = build_grounding(function_id, args, results, applicability)
    messages = [make_system_message(SOLUTION_SYSTEM_PROMPT),
                make_user_message("CALCULATION DETAILS:\n" + grounding + "\n\nWrite the worked solution now.")]
    cleaner = AnswerStreamCleaner()
    shown: List[str] = []
    stream = provider.generate_answer_stream(messages=messages, tools=None, temperature=0.1, max_tokens=max_tokens)
    for chunk in stream:
        text = cleaner.feed(chunk.delta_content)
        if text:
            shown.append(text)
            yield {"type": "token", "content": text}
        if cleaner.looping:
            close = getattr(stream, "close", None)
            if close:
                close()
            break
    rest = cleaner.flush()
    if rest:
        shown.append(rest)
        yield {"type": "token", "content": rest}
    answer = "".join(shown)
    grounding_, explanation = grounding, build_grounding(function_id, args, results, applicability)[1]
    mismatch = equation_mismatch(answer, explanation.get("formula"))
    yield {"type": "check", "unverified": unverified_numbers(answer, grounding_),
           "equation_mismatch": mismatch,
           # The method's own equation and its substitution, for the UI to show when the model's differs.
           "equation": explanation.get("formula") if mismatch else None,
           "substitution": substituted_formula(explanation, _default_symbols(function_id, args or {})) if mismatch else None}
