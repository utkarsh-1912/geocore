# Author: Utkarsh Gupta
# License: GPL v3
"""
Intelligent tool subset selection for context-constrained SLMs.
Provides dynamic filtering and ranking of the Geotechnical Tool Registry
to fit within strict context limits of local models (e.g., Gemma).
"""

import re
from typing import Dict, Any, List, Optional

from core.geoai.tool_registry import tool_registry
from core.geoai.slm_schema_generator import _clean_json_schema, generate_openai_tool_definitions


CATEGORY_KEYWORDS = {
    "site_investigation": {"cpt", "spt", "pcpt", "cone", "borehole", "n60", "qc", "ic", "friction_ratio"},
    "shallow_foundations": {"bearing", "settlement", "footing", "shallow", "foundation", "boussinesq", "vesic", "schmertmann"},
    "deep_foundations": {"pile", "shaft", "lcpc", "koppejan", "debeer", "axcap", "skin_friction", "end_bearing"},
    "earth_pressure": {"rankine", "coulomb", "earth", "pressure", "active", "passive", "retaining", "ka", "kp"},
    "excavations": {"rankine", "coulomb", "earth", "pressure", "active", "passive", "retaining", "ka", "kp", "excavation"},
    "soil_dynamics": {"liquefaction", "gmax", "shear_wave", "vs", "cyclic", "dynamic", "darendeli"},
    "phase_relations": {"void", "porosity", "density", "unit_weight", "saturation", "water_content", "gamma"},
    "consolidation": {"consolidation", "settlement", "oedometer", "cv", "isochrone"},
    "pipelines": {"pipeline", "subsea", "contact_width", "penetration", "embedment"},
    "groundwater": {"hydraulic", "conductivity", "permeability", "pumping", "aquifer", "dupuit"},
    "eurocode": {"eurocode", "ec7", "en1997", "partial_factor", "design_approach", "fractile"},
}

CATEGORY_SYNONYMS = {
    "earth_pressure": {"excavations", "earth_pressure"},
    "excavations": {"excavations", "earth_pressure"},
    "classification": {"phase_relations", "classification"},
    "phase_relations": {"phase_relations", "classification"},
}


def infer_categories(query: str) -> List[str]:
    """
    Tokenizes query and matches against CATEGORY_KEYWORDS to infer domain categories.
    Returns list of matching category names sorted by match score.
    """
    words = set(re.findall(r'[a-z0-9_]+', query.lower()))
    scores = {}
    
    for category, keywords in CATEGORY_KEYWORDS.items():
        overlap = len(words.intersection(keywords))
        if overlap > 0:
            scores[category] = overlap
            
    sorted_categories = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    return [category for category, score in sorted_categories]


def format_tools_for_prompt(tools: List[dict]) -> List[dict]:
    """
    Takes tool dicts from the registry and formats them into the OpenAI tool-calling spec.
    Strips overly verbose descriptions to save tokens.
    Ensures all schemas are JSON-serializable (no NaN/Inf).
    """
    formatted = []
    for tool in tools:
        # Normalize input whether it came from generate_openai_tool_definitions or tool_registry
        if "type" in tool and "function" in tool:
            func = tool["function"]
            name = func.get("name", "")
            desc = func.get("description", "")
            params = func.get("parameters", {})
        else:
            name = tool.get("name", "")
            desc = tool.get("description", "")
            params = tool.get("input_schema", {})
            
        # Strip long descriptions (keep first sentence roughly)
        short_desc = desc
        if short_desc:
            sentences = [s.strip() for s in short_desc.split(". ") if s.strip()]
            if sentences:
                short_desc = sentences[0]
                if not short_desc.endswith("."):
                    short_desc += "."
                
        cleaned_params = _clean_json_schema(params)
        
        formatted.append({
            "type": "function",
            "function": {
                "name": name,
                "description": short_desc,
                "parameters": cleaned_params
            }
        })
        
    return formatted


def select_relevant_tools(query: str, context: Optional[Dict[str, Any]] = None, max_tools: int = 20) -> List[dict]:
    """
    Dynamically selects a relevant subset of tools based on query and context.
    Uses slm_schema_generator for foundational schemas and formats them.
    """
    query_lower = query.lower()
    
    # 1. STOPWORDS filtering mimicking gemma_engine
    STOPWORDS = {
        'calculate', 'find', 'compute', 'determine', 'get', 'run', 'what', 'is', 'for',
        'with', 'and', 'the', 'a', 'an', 'in', 'at', 'to', 'of', 'from', 'by', 'm', 's',
        'm3', 'kn', 'kpa', 'mpa', 'deg', 'degrees', 'please', 'using', 'below', 'above'
    }
    
    all_words = set(re.findall(r'[a-z0-9_]+', query_lower))
    query_words = {w for w in all_words if w not in STOPWORDS and len(w) > 1}
    
    # Generate all tool schemas via existing generator
    all_tools_formatted = generate_openai_tool_definitions()
    
    # Get metadata for filtering
    tools_info = tool_registry.list_tools()
    tools_map = {t['name']: t for t in tools_info}
    
    active_function = context.get('activeFunction') if context else None
    active_category = None
    
    # Step 1: Active function
    if active_function and active_function in tools_map:
        active_category = tools_map[active_function].get('category')
        
    # Step 2: Category inference
    inferred_categories = infer_categories(query)
    
    candidates = []
    
    if active_category or inferred_categories:
        allowed_categories = set(inferred_categories)
        for cat in list(allowed_categories):
            if cat in CATEGORY_SYNONYMS:
                allowed_categories.update(CATEGORY_SYNONYMS[cat])
        if active_category:
            allowed_categories.add(active_category)
            if active_category in CATEGORY_SYNONYMS:
                allowed_categories.update(CATEGORY_SYNONYMS[active_category])
            
        for tool_info in tools_info:
            if tool_info.get('category') in allowed_categories or tool_info['name'] == active_function:
                candidates.append(tool_info)
        if not candidates:
            candidates = list(tools_info)
    else:
        # Fallback
        candidates = list(tools_info)
        
    # Step 3: Score and rank (reusing simplified gemma_engine logic pattern)
    scored_candidates = []
    for tool_info in candidates:
        name = tool_info['name'].lower()
        desc = (tool_info.get('description') or '').lower()
        tool_keywords = set(re.findall(r'[a-z0-9_]+', f"{name} {desc}"))
        clean_keywords = {k for k in tool_keywords if k not in STOPWORDS and len(k) > 1}
        
        score = 0
        overlap = len(query_words.intersection(clean_keywords))
        score += overlap * 3
        
        for qw in query_words:
            if qw in name:
                score += 8
                
        if name.startswith('calculate_') and score > 0:
            score += 10
                
        if name == active_function:
            score += 100
            
        if score > 0 or name == active_function:
            scored_candidates.append((score, tool_info))
            
    if not scored_candidates:
        scored_candidates = [(0, t) for t in candidates]
        
    scored_candidates.sort(key=lambda x: x[0], reverse=True)
    top_tools = [t[1] for t in scored_candidates[:max_tools]]
    
    # Map back to schemas
    formatted_map = {t['function']['name']: t for t in all_tools_formatted}
    
    selected_formatted = []
    for t in top_tools:
        if t['name'] in formatted_map:
            selected_formatted.append(formatted_map[t['name']])
            
    # Step 4: Return formatted tools
    return format_tools_for_prompt(selected_formatted)
