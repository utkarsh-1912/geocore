"""
GeoAI System Prompt Builder
Builds the system prompt for the GeoAI local SLM.
"""
# Author: Utkarsh Gupta
# License: GPL v3

from typing import Dict, Any, Optional

GEOAI_IDENTITY = """You are GeoAI, a geotechnical engineering assistant integrated into GeoCore.
You help engineers with calculations, site investigation data, and engineering analysis.
You use Groundhog calculation tools for all numerical computations.
You never fabricate references, invent calculations, or claim unsupported certainty."""

TOOL_CALLING_INSTRUCTIONS = """When the user asks for a calculation, select the appropriate tool.
Extract parameter values from the user's message including units.
If required parameters are missing, ask the user for them. Do NOT invent values.
After receiving tool results, explain them in engineering context.
Always report units with numerical results."""

ENGINEERING_CAUTION_RULES = """Never say "this design is safe" — report calculated values with their basis.
Prefer "the calculated value is X based on Y method" over definitive safety claims.
If a calculation produces unexpected results, flag it and suggest verification.
Distinguish between: project data, calculation results, literature, standards, model interpretation, and assumptions.
Never silently invent missing soil parameters.
Never reproduce engineering equations yourself — use tools."""

def build_system_prompt(context: Optional[Dict[str, Any]] = None) -> str:
    """
    Builds the complete system prompt for the local SLM.
    Combines core identity, tool calling rules, and engineering caution rules.
    Injects context about active functions or categories if provided.
    
    Args:
        context: Optional dictionary containing 'activeFunction' and/or 'activeCategory'
                 to inject context into the prompt.
                 
    Returns:
        The fully formatted system prompt string.
    """
    prompt_parts = [
        GEOAI_IDENTITY,
        "\n### TOOL CALLING INSTRUCTIONS",
        TOOL_CALLING_INSTRUCTIONS,
        "\n### ENGINEERING CAUTION RULES",
        ENGINEERING_CAUTION_RULES,
    ]

    if context:
        active_func = context.get('activeFunction')
        active_cat = context.get('activeCategory')
        proj_context = context.get('project_context')
        
        if active_func or active_cat or proj_context:
            prompt_parts.append("\n### CURRENT CONTEXT")
            if active_cat:
                prompt_parts.append(f"- Current Engineering Domain: {active_cat}")
            if active_func:
                prompt_parts.append(f"- Active Calculation Tool: {active_func}")
            if proj_context:
                if hasattr(proj_context, 'get_compact_context_string'):
                    prompt_parts.append("\n" + proj_context.get_compact_context_string())
                elif isinstance(proj_context, str):
                    prompt_parts.append("\n" + proj_context)

    return "\n".join(prompt_parts)
