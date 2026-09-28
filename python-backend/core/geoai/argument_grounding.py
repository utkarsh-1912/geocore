# Author: Utkarsh Gupta
# License: GPL v3
"""
Runtime check that a model's tool-call arguments come from the user (AGENTS.md §5, §17).

Small models fill required inputs they were never given (e.g. qc = 120 for a relative
density question that only stated Dr = 0.95). Such a call must not reach Groundhog: GeoAI
asks for the missing values instead. The grounding rule is the eval scorer's
``no_invented`` criterion, so the runtime guard and the benchmark agree.
"""
import re
from typing import Any, Dict, List

from core.geoai.eval.scoring import (
    canonicalise_keys,
    extract_numbers,
    field_unit,
    normalise_field_value,
    value_grounded,
    values_match,
)


def ungrounded_arguments(input_model, args: Dict[str, Any], grounding_text: str) -> List[str]:
    """
    Names of numeric arguments whose values appear nowhere in ``grounding_text`` (the user's
    messages and any project context). Restating a schema default is not an invention.
    """
    numbers = extract_numbers(grounding_text)
    canon, _unknown = canonicalise_keys(input_model, args)
    invented = []
    for name, raw in canon.items():
        fi = input_model.model_fields.get(name)
        if fi is None:
            continue
        norm = normalise_field_value(input_model, name, raw)
        if not fi.is_required() and values_match(fi.default, norm, rel_tol=1e-9, abs_tol=1e-12):
            continue
        unit = field_unit(fi)
        if not value_grounded(norm, numbers, unit) and not value_grounded(raw, numbers, "-"):
            invented.append(name)
    return invented


def _plain_description(description: str) -> str:
    """'Cone tip resistance (<span>q_c</span>) [MPa] - Suggested range: ...' -> readable text."""
    text = re.sub(r"<[^>]+>", "", description or "")
    name, _, rest = text.partition(" - ")
    name = re.sub(r"\s*[(\[].*$", "", name).strip().rstrip(".")
    rng = re.search(r"Suggested range:\s*(.+)", rest)
    return name + (f" (suggested range: {rng.group(1).strip().rstrip('.')})" if rng and name else "")


def missing_inputs_message(tool_name: str, input_model, names: List[str]) -> str:
    """Clarification asking the user for the inputs the model could not take from the question."""
    lines = []
    for name in names:
        fi = input_model.model_fields.get(name)
        desc = _plain_description(fi.description) if fi is not None else ""
        unit = field_unit(fi) if fi is not None else "-"
        label = f"`{name}`" + (f" [{unit}]" if unit != "-" else "")
        lines.append(f"- {label}" + (f": {desc}" if desc else ""))
    return (f"To run **{tool_name}** I need values you have not given yet:\n"
            + "\n".join(lines)
            + "\n\nPlease provide them (with units). I will not assume values for these inputs.")
