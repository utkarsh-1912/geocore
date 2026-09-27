"""
Keep parameter_inventory.json consistent with Groundhog's own input validation.

Groundhog decorates its functions with ``@Validator(SPEC, ERRORRETURN)``; SPEC holds the
authoritative type and ``min_value``/``max_value`` of each parameter (outside that range
Groundhog returns its NaN error output). The auto-generated GeoAI schemas read their bounds
from parameter_inventory.json at start-up (no Groundhog imports), so the inventory is synced
from SPEC offline:

    python -m core.geoai.inventory_sync

- numeric parameters with a Groundhog SPEC entry get exactly Groundhog's bounds
  (None -> no bound) and Groundhog's int/float type;
- functions exposed by the registry but missing from the inventory get rows built from
  the Groundhog signature, SPEC and docstring.

Bounds of parameters without a SPEC entry (classes/wrappers without a Validator) are left
unchanged. tests/test_geoai_bounds.py fails if the inventory drifts from Groundhog.
"""
import inspect
import json
import os
from typing import Any, Dict, List, Optional

INVENTORY_PATH = os.path.join(os.path.dirname(__file__), "parameter_inventory.json")

_SPEC_TYPE_TO_PYTHON = {"float": "float", "int": "int", "string": "str", "bool": "bool", "list": "list"}


def resolve_groundhog_object(obj: Any) -> Any:
    """Real Groundhog object behind a LazyGroundhogCallable stand-in (imports its module)."""
    return obj.resolve() if hasattr(obj, "resolve") else obj


def groundhog_validation_spec(obj: Any) -> Optional[Dict[str, Dict[str, Any]]]:
    """The validation dict passed to Groundhog's ``@Validator`` for ``obj``, or None."""
    from groundhog.general.validation import Validator

    fn = resolve_groundhog_object(obj)
    for _ in range(5):
        if fn is None:
            break
        for cell in (getattr(fn, "__closure__", None) or ()):
            try:
                value = cell.cell_contents
            except ValueError:
                continue
            if isinstance(value, Validator):
                return value.validationspec
        fn = getattr(fn, "__wrapped__", None)
    return None


def _bound(value: Any) -> Any:
    return "" if value is None else float(value)


def _new_rows(func_name: str, obj: Any, spec: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    from core.geoai.schema_factory import _docstring_param_line, resolve_parameter_unit

    rows = []
    doc = getattr(obj, "__doc__", "") or ""
    for p_name, param in inspect.signature(obj).parameters.items():
        if param.kind in (param.VAR_KEYWORD, param.VAR_POSITIONAL) or p_name in ("self", "cls"):
            continue
        s = spec.get(p_name, {})
        _, line = _docstring_param_line(doc, p_name)
        py_type = _SPEC_TYPE_TO_PYTHON.get(s.get("type"))
        if py_type is None and (line or "").strip().lower().startswith("list"):
            py_type = "list"  # e.g. pile_y is documented as a list but missing from SPEC
        if py_type is None:
            default = param.default
            py_type = ("bool" if isinstance(default, bool) else "str" if isinstance(default, str)
                       else "list" if isinstance(default, (list, tuple)) else "float")
        unit = resolve_parameter_unit(func_name, obj, p_name)
        numeric = s.get("type") in ("float", "int")
        default = "" if param.default is inspect.Parameter.empty else str(param.default)
        rows.append({
            "module_id": obj.__module__,
            "function_id": func_name,
            "parameter_name": p_name,
            "python_type": py_type,
            "canonical_unit": unit,
            "display_unit": unit,
            "min_value": _bound(s.get("min_value")) if numeric else "",
            "max_value": _bound(s.get("max_value")) if numeric else "",
            "is_nullable": False,
            "default_value": default,
            "physical_meaning": (line or p_name.replace("_", " ").title()).strip(),
        })
    return rows


def sync_inventory(function_map: Dict[str, Any], inventory: List[Dict[str, Any]]) -> Dict[str, int]:
    """Update ``inventory`` in place from Groundhog validation specs; return change counts."""
    stats = {"bounds_updated": 0, "types_updated": 0, "rows_added": 0}
    by_func: Dict[str, List[Dict[str, Any]]] = {}
    for row in inventory:
        by_func.setdefault(row["function_id"], []).append(row)

    for func_name, obj in function_map.items():
        try:
            spec = groundhog_validation_spec(obj) or {}
        except Exception:
            continue
        rows = by_func.get(func_name)
        if rows is None:
            try:
                new = _new_rows(func_name, resolve_groundhog_object(obj), spec)
            except (TypeError, ValueError):
                continue
            inventory.extend(new)
            stats["rows_added"] += len(new)
            continue
        for row in rows:
            s = spec.get(row["parameter_name"])
            if not s or s.get("type") not in ("float", "int"):
                continue
            if row.get("python_type") in ("int", "float") and row["python_type"] != s["type"]:
                row["python_type"] = s["type"]  # e.g. C_FC is a float in Groundhog, not an int
                stats["types_updated"] += 1
            lo, hi = _bound(s.get("min_value")), _bound(s.get("max_value"))
            if (row.get("min_value"), row.get("max_value")) != (lo, hi):
                row["min_value"], row["max_value"] = lo, hi
                stats["bounds_updated"] += 1
    return stats


def main() -> int:
    from core.registry import registry

    with open(INVENTORY_PATH, "r", encoding="utf-8") as f:
        inventory = json.load(f)
    stats = sync_inventory(registry.function_map, inventory)
    with open(INVENTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(inventory, f, indent=2)  # same layout as the existing file
    print(json.dumps(stats))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
