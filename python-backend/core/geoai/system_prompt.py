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

TOOL_CALLING_INSTRUCTIONS = """When the user asks what something is or asks you to explain a concept, answer in words:
do not call a tool and do not ask for input values.
When the user asks for a calculation, select the appropriate tool.
Extract parameter values from the user's message including units.
If required parameters are missing, ask the user for them. Do NOT invent values.
After receiving tool results, explain them in engineering context.
The app shows tool results to the user as tables and charts: do not copy whole tables, highlight the key values.
Report each result with the unit the tool gives in output_units; "-" means dimensionless, so give no unit.
Earlier assistant turns may end with a [Calculation record]. For follow-up questions about that result
(e.g. "explain the calculation"), explain it from the record: method, inputs, outputs and what they mean.
Do not call the tool again unless the user gives new inputs.
Be brief: one short paragraph or a few short bullet points, unless the user asks for more detail.
Write plain text and Markdown only, no LaTeX.
Do not repeat sentences."""

ENGINEERING_CAUTION_RULES = """Never say "this design is safe" — report calculated values with their basis.
Prefer "the calculated value is X based on Y method" over definitive safety claims.
If a calculation produces unexpected results, flag it and suggest verification.
Distinguish between: project data, calculation results, literature, standards, model interpretation, and assumptions.
Never silently invent missing soil parameters.
Describe the project only from the CURRENT CONTEXT and tool results; never invent layers, test data or soil descriptions.
Name standards and classification systems exactly; if unsure of a definition, say so instead of guessing.
A CPT soil behaviour type (SBT) describes in-situ behaviour; it is not a USCS soil class, which needs grain size and Atterberg limits.
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

    if context and context.get('agent_role'):
        prompt_parts.append("\n### YOUR ROLE\n" + str(context['agent_role']))

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
