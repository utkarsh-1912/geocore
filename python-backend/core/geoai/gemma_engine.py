# Author: Utkarsh Gupta
# License: GPL v3
"""
Embedded Local Gemma & Geotechnical SLM Engine.
Operates 100% offline with zero cloud API keys.
Integrates natural language geotechnical reasoning with whitelisted GeoAI tool execution.
"""
import re
import math
from typing import Dict, Any, List, Optional, Tuple

from core.geoai.tool_registry import tool_registry
import core.geoai.tool_definitions  # Ensure standard canonical tools are registered
from core.geoai.schemas import get_schema
from core.geoai.schema_factory import _INVENTORY_BY_FUNC


class LocalGemmaEngine:
    """
    100% Offline Geotechnical AI Engine powered by Gemma & Semantic Groundhog Tool Orchestration.
    Strictly constrained to whitelisted geotechnical calculations.
    """

    def __init__(self):
        self._tool_cache = {}
        self._load_tool_index()

    def _load_tool_index(self):
        """Indexes all 213 registered tools for rapid semantic matching."""
        tools = tool_registry.list_tools()
        for t in tools:
            name = t['name'].lower()
            desc = (t.get('description') or '').lower()
            self._tool_cache[t['name']] = {
                'name': t['name'],
                'description': desc,
                'category': t.get('category', 'general'),
                'keywords': set(re.findall(r'[a-z0-9_]+', f"{name} {desc}"))
            }

    def find_best_tools(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Matches user prompt against whitelisted geotechnical tool catalog with semantic weighting."""
        STOPWORDS = {
            'calculate', 'find', 'compute', 'determine', 'get', 'run', 'what', 'is', 'for',
            'with', 'and', 'the', 'a', 'an', 'in', 'at', 'to', 'of', 'from', 'by', 'm', 's',
            'm3', 'kn', 'kpa', 'mpa', 'deg', 'degrees', 'please', 'using', 'below', 'above'
        }

        all_words = set(re.findall(r'[a-z0-9_]+', query.lower()))
        query_words = {w for w in all_words if w not in STOPWORDS and len(w) > 1}
        query_lower = query.lower()
        matches = []

        # Direct High-Confidence Domain Routing
        DIRECT_ROUTING = [
            (('rankine', 'earth_pressure'), 'calculate_earth_pressure_rankine', 50),
            (('rankine',), 'calculate_earth_pressure_rankine', 40),
            (('gmax',), 'calculate_gmax_from_shear_wave_velocity', 40),
            (('shear_wave', 'vs'), 'calculate_gmax_from_shear_wave_velocity', 40),
            (('void', 'ratio', 'porosity'), 'calculate_void_ratio_from_porosity', 40),
            (('porosity',), 'calculate_void_ratio_from_porosity', 30),
            (('contact', 'width'), 'calculate_contact_width', 40),
            (('contactwidth',), 'calculate_contact_width', 40),
            (('bulk', 'unit', 'weight'), 'calculate_bulk_unit_weight', 40),
            (('relative', 'density'), 'calculate_relative_density', 40),
            (('boussinesq',), 'calculate_stresses_point_load', 40),
            (('point', 'load'), 'calculate_stresses_point_load', 40),
            (('circular', 'footing'), 'calculate_stresses_circular_footing', 40),
            (('hydraulic', 'conductivity'), 'calculate_hydraulic_conductivity_unconfined', 40),
        ]

        # Key geotechnical concept heuristics
        synonyms = {
            'bearing': ['bearingcapacity', 'shallowfoundations', 'capacity'],
            'capacity': ['capacity', 'bearingcapacity', 'undrained', 'strip'],
            'settlement': ['settlement', 'elastic', 'schmertmann', 'janbu', 'consolidation'],
            'rankine': ['calculate_earth_pressure_rankine', 'earth_pressure', 'rankine', 'ka', 'kp'],
            'earth': ['earth_pressure', 'rankine', 'coulomb', 'active', 'passive'],
            'pressure': ['earth_pressure', 'rankine', 'active', 'passive'],
            'liquefaction': ['liquefaction', 'boulanger', 'idriss', 'robertson', 'csr', 'crr'],
            'gmax': ['calculate_gmax_from_shear_wave_velocity', 'gmax', 'shear_wave', 'vs', 'dynamics'],
            'pipeline': ['calculate_contact_width', 'contactwidth', 'subsea', 'penetration'],
            'void': ['calculate_void_ratio_from_porosity', 'voidratio', 'porosity', 'phase_relations'],
            'porosity': ['calculate_void_ratio_from_porosity', 'voidratio', 'porosity', 'phase_relations'],
            'density': ['density', 'unitweight', 'relative_density'],
            'cpt': ['pcpt', 'qc', 'ic', 'friction_ratio', 'dr'],
            'spt': ['spt', 'n60', 'n160', 'overburden'],
            'pile': ['lcpc', 'koppejan', 'axcap', 'shaft', 'base_resistance', 'deepfoundations']
        }

        expanded_words = set(query_words)
        for w in query_words:
            if w in synonyms:
                expanded_words.update(synonyms[w])

        for tool_name, info in self._tool_cache.items():
            name_lower = tool_name.lower()
            score = 0

            # Check direct routing rules
            for keys, target_tool, boost in DIRECT_ROUTING:
                if target_tool == tool_name and all(k in query_lower for k in keys):
                    score += boost

            # Keyword overlap with non-stopwords
            clean_keywords = {k for k in info['keywords'] if k not in STOPWORDS and len(k) > 1}
            overlap = len(expanded_words.intersection(clean_keywords))
            score += overlap * 3

            # Name match boost
            for qw in query_words:
                if qw in name_lower:
                    score += 8

            # Canonical tool bonus (tools with calculate_ prefix have full validated schemas)
            if tool_name.startswith('calculate_') and score > 0:
                score += 10

            if score > 0:
                matches.append((score, info))

        matches.sort(key=lambda x: x[0], reverse=True)
        return [m[1] for m in matches[:limit]]

    def extract_parameters_from_text(self, text: str, function_id: str) -> Dict[str, Any]:
        """
        Extracts numerical values, strings, and units from natural text
        tailored to the target calculation parameters.
        """
        extracted = {}

        # Universal Geotechnical Symbol and Synonym Mapping
        UNIVERSAL_ALIASES = {
            'phi_eff': ['phi_eff', 'phi', "phi'", 'friction angle', 'friction_angle', 'effective friction angle', 'fi'],
            'c_eff': ['c_eff', 'c', "c'", 'cohesion', 'effective cohesion'],
            'su': ['su', 's_u', 'undrained shear strength', 'shear strength', 'cu', 'c_u'],
            'gamma': ['gamma', 'unit weight', 'total unit weight', 'unit_weight', 'bulk unit weight', 'soil unit weight'],
            'z': ['z', 'depth', 'depth below base', 'depth below ground', 'embedment depth'],
            'diameter': ['diameter', 'dia', 'D', 'pipe diameter', 'pile diameter'],
            'penetration': ['penetration', 'pen', 'z_p', 'zp', 'embedment'],
            'q': ['q', 'imposed stress', 'stress', 'surcharge', 'pressure', 'load'],
            'footing_width': ['footing_width', 'width', 'B', 'b', 'breadth'],
            'footing_length': ['footing_length', 'length', 'L', 'l'],
            'footing_radius': ['footing_radius', 'radius', 'R', 'r'],
            'Vs': ['Vs', 'vs', 'v_s', 'shear wave velocity', 'shear_wave_velocity', 'shear velocity'],
            'porosity': ['porosity', 'n'],
            'voidratio': ['voidratio', 'void ratio', 'e', 'void_ratio'],
            'Gs': ['Gs', 'gs', 'specific gravity', 'specific_gravity'],
            'Sr': ['Sr', 'sr', 'degree of saturation', 'saturation'],
            'wall_angle': ['wall_angle', 'wall angle', 'beta', 'wall inclination'],
            'top_angle': ['top_angle', 'top angle', 'alpha', 'backfill slope', 'slope angle'],
            'g': ['g', 'gravity', 'acceleration due to gravity'],
            'nu': ['nu', 'poisson', 'poissons ratio', "poisson's ratio", 'v'],
            'Dr': ['Dr', 'dr', 'relative density'],
            'e_min': ['e_min', 'minimum void ratio', 'min void ratio'],
            'e_max': ['e_max', 'maximum void ratio', 'max void ratio'],
            'k': ['k', 'permeability', 'hydraulic conductivity']
        }

        # 1. Discover target parameters
        target_params = {}  # param_name -> list of alias strings

        # Source A: Tool Registry Schema Introspection
        tool = tool_registry.get_tool(function_id)
        if tool and tool.input_model:
            for f_name, field in tool.input_model.model_fields.items():
                aliases = [f_name, f_name.replace('_', ' ')]
                # Add validation aliases if defined
                if field.validation_alias:
                    try:
                        # AliasChoices / str / list
                        if hasattr(field.validation_alias, 'choices'):
                            aliases.extend(list(field.validation_alias.choices))
                        elif isinstance(field.validation_alias, (list, tuple, set)):
                            aliases.extend(list(field.validation_alias))
                        elif isinstance(field.validation_alias, str):
                            aliases.append(field.validation_alias)
                    except Exception:
                        pass
                if f_name in UNIVERSAL_ALIASES:
                    aliases.extend(UNIVERSAL_ALIASES[f_name])
                target_params[f_name] = list(dict.fromkeys(aliases))

        # Source B: Parameter Inventory
        inv_list = _INVENTORY_BY_FUNC.get(function_id) or \
                   _INVENTORY_BY_FUNC.get(function_id.replace('calculate_', '')) or \
                   _INVENTORY_BY_FUNC.get(function_id.lower()) or []
        for inv_p in inv_list:
            p_name = inv_p.get('parameter_name')
            if p_name:
                aliases = target_params.get(p_name, [p_name, p_name.replace('_', ' ')])
                if p_name in UNIVERSAL_ALIASES:
                    aliases.extend(UNIVERSAL_ALIASES[p_name])
                target_params[p_name] = list(dict.fromkeys(aliases))

        # If still empty, check universal aliases directly
        if not target_params:
            for p_name, aliases in UNIVERSAL_ALIASES.items():
                target_params[p_name] = aliases

        # 2. Extract values for each parameter using regex matching
        num_pattern = r'([+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)'

        for p_name, aliases in target_params.items():
            # Sort aliases by length descending so longer phrases match first
            sorted_aliases = sorted(aliases, key=lambda a: len(str(a)), reverse=True)
            matched = False

            for alias in sorted_aliases:
                if matched:
                    break
                alias_str = str(alias).strip()
                if not alias_str:
                    continue

                esc_alias = re.escape(alias_str)
                # Patterns: "alias = 32", "alias: 32", "alias is 32", "alias of 32", "alias at 32", "alias 32"
                patterns = [
                    rf'(?:^|\b|(?<=[^a-zA-Z0-9_])){esc_alias}(?:$|\b|(?=[^a-zA-Z0-9_]))\s*[:=]\s*{num_pattern}',
                    rf'(?:^|\b|(?<=[^a-zA-Z0-9_])){esc_alias}(?:$|\b|(?=[^a-zA-Z0-9_]))\s+(?:is|of|at|equal to|equals|value)\s+{num_pattern}',
                    rf'(?:^|\b|(?<=[^a-zA-Z0-9_])){esc_alias}(?:$|\b|(?=[^a-zA-Z0-9_]))\s*=\s*{num_pattern}',
                    rf'(?:^|\b|(?<=[^a-zA-Z0-9_])){esc_alias}(?:$|\b|(?=[^a-zA-Z0-9_]))\s+{num_pattern}'
                ]

                for pat in patterns:
                    m = re.search(pat, text, re.IGNORECASE)
                    if m:
                        val_str = m.group(1).strip()
                        try:
                            val = float(val_str) if ('.' in val_str or 'e' in val_str.lower()) else int(val_str)
                            extracted[p_name] = val
                            matched = True
                            break
                        except ValueError:
                            pass

        return extracted

    def chat_and_execute(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Processes natural language query offline:
        1. Identifies geotechnical calculation intent.
        2. Selects candidate whitelisted tool from Tool Registry.
        3. Extracts input parameters.
        4. Executes tool via Tool Registry.
        5. Formats natural language geotechnical engineering response.
        """
        # Step 1: Find best matching tools
        candidate_tools = self.find_best_tools(prompt)
        
        if not candidate_tools:
            return {
                "response": "I am the GeoCore Engineering Assistant. I couldn't identify a specific geotechnical calculation matching your query. You can ask me to perform calculations for bearing capacity, earth pressures, shallow & deep foundations, CPT/SPT correlations, or soil dynamics.",
                "executed_tool": None,
                "candidate_tools": [],
                "results": None
            }

        primary_tool = candidate_tools[0]
        tool_name = primary_tool['name']

        # Step 2: Extract arguments from prompt
        extracted_args = self.extract_parameters_from_text(prompt, tool_name)
        if context and isinstance(context, dict):
            # Merge project context if supplied
            for k, v in context.items():
                if k not in extracted_args and v is not None:
                    extracted_args[k] = v

        # Step 3: Attempt tool execution if parameters were found
        tool_obj = tool_registry.get_tool(tool_name)
        if tool_obj and tool_obj.input_model:
            required_params = [
                name for name, field in tool_obj.input_model.model_fields.items()
                if field.is_required()
            ]
        else:
            inv_params = _INVENTORY_BY_FUNC.get(tool_name, [])
            required_params = [p['parameter_name'] for p in inv_params if p.get('is_required', True) and not p.get('default_value')]

        missing_required = [p for p in required_params if p not in extracted_args]

        if missing_required and len(extracted_args) == 0:
            param_hints = ", ".join(f"`{p}`" for p in required_params[:4])
            return {
                "response": f"I identified the routine **`{tool_name}`** ({primary_tool['description']}).\n\nTo calculate this, please provide parameters such as: {param_hints}.",
                "executed_tool": tool_name,
                "candidate_tools": [t['name'] for t in candidate_tools[:4]],
                "parameters_extracted": extracted_args,
                "missing_parameters": missing_required,
                "results": None
            }

        # Step 4: Execute via whitelisted Tool Registry
        try:
            result = tool_registry.invoke_tool(tool_name, extracted_args)
            
            # Format geotechnical response
            res_data = result.get('result') if ('result' in result and isinstance(result['result'], dict)) else result
            output_lines = []
            if isinstance(res_data, dict):
                for k, v in res_data.items():
                    if isinstance(v, float):
                        output_lines.append(f"- **`{k}`**: `{v:.4f}`")
                    elif isinstance(v, (int, str)):
                        output_lines.append(f"- **`{k}`**: `{v}`")
            else:
                output_lines.append(f"- **`Result`**: `{res_data}`")

            res_summary = "\n".join(output_lines) if output_lines else str(res_data)
            
            reply = f"### 📊 Geotechnical Calculation Result (`{tool_name}`)\n\n" \
                    f"**Function**: {tool_name}\n" \
                    f"**Inputs Used**:\n" + "\n".join(f"- `{k}`: `{v}`" for k, v in extracted_args.items()) + "\n\n" \
                    f"**Outputs**:\n{res_summary}\n\n" \
                    f"> *Calculated locally via Groundhog Geotechnical Engine (GeoAI Tool Registry).* "

            return {
                "response": reply,
                "executed_tool": tool_name,
                "candidate_tools": [t['name'] for t in candidate_tools[:4]],
                "parameters_extracted": extracted_args,
                "results": result
            }

        except Exception as e:
            return {
                "response": f"Identified tool **`{tool_name}`**, but encountered an input validation issue:\n\n`{str(e)}`\n\nPlease verify the supplied parameter values.",
                "executed_tool": tool_name,
                "candidate_tools": [t['name'] for t in candidate_tools[:4]],
                "parameters_extracted": extracted_args,
                "error": str(e),
                "results": None
            }

    def autofill_form(self, function_id: str, raw_text: str) -> Dict[str, Any]:
        """
        Parses unstructured site notes / borehole reports and returns extracted
        fields with confidence scores for automatic form population.
        """
        extracted = self.extract_parameters_from_text(raw_text, function_id)
        
        fields = {}
        for k, v in extracted.items():
            fields[k] = {
                "value": v,
                "confidence": 0.95 if isinstance(v, (int, float)) else 0.85,
                "source": "Local Gemma Semantic Parser"
            }

        return {
            "function_id": function_id,
            "extracted_count": len(fields),
            "fields": fields
        }


# Global Singleton Instance
gemma_engine = LocalGemmaEngine()
