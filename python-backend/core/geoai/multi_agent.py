"""
Multi-agent orchestration for GeoAI (AGENTS.md §2, §7, §14).

A compound request ("classify CPT-03, then size a footing, and find guidance on settlement limits")
touches several engineering domains. Offering every domain's tools to one small model overflows its
context and blurs tool selection, so the request is *planned* into steps and each step runs on a
specialist: an ordinary ``GeoAIAgent`` limited to the tools of its domains and given a short role
note. Everything still goes through the validated Tool Registry; specialists never see each
other's schemas and later steps receive earlier results as [Calculation record]s, so values flow
between steps with provenance instead of being retyped by a model.

* Planner: deterministic (domain keyword inference, ``tool_selector.infer_categories``). It makes no
  model call, so planning adds no CPU latency. A request with fewer than two steps is not
  multi-agent at all and runs on the plain agent, unchanged.
* Specialists: ``AgentRole`` (domains + instructions).
* Verifier: deterministic checks over the tool results (failures, steps that ran nothing).
* Output: the specialists' answers under role headings plus the verifier notes. Intermediate
  progress is streamed as stage / tool events; the combined answer is emitted once at the end.
"""

import json
import logging
import re
from dataclasses import asdict, dataclass
from typing import Any, Dict, Iterator, List, Optional, Tuple

from .agent import AgentResponse, AgentStreamEvent, GeoAIAgent
from .model_provider import ModelProvider
from .tool_registry import GeoAIToolRegistry
from .tool_selector import _NUMERIC_INPUT, infer_categories

logger = logging.getLogger(__name__)

MAX_STEPS = 4


@dataclass(frozen=True)
class AgentRole:
    name: str
    label: str
    domains: Tuple[str, ...]  # tool_selector.DOMAIN_MARKERS keys
    instructions: str


ROLES: Dict[str, AgentRole] = {r.name: r for r in (
    AgentRole(
        "site_investigation", "Site investigation",
        ("site_investigation",),
        "You are the site-investigation specialist: CPT, SPT, borehole and AGS data, soil behaviour "
        "classification and derived soil parameters. Report derived values with their method."),
    AgentRole(
        "foundations", "Foundations",
        ("shallow_foundations", "deep_foundations", "consolidation", "eurocode"),
        "You are the foundations specialist: bearing capacity, settlement, pile capacity and "
        "consolidation. Use values from earlier [Calculation record]s and the project; never invent soil parameters."),
    AgentRole(
        "geotechnical_analysis", "Geotechnical analysis",
        ("phase_relations", "earth_pressure", "excavations", "soil_dynamics", "groundwater", "pipelines"),
        "You are the geotechnical-analysis specialist: phase relations and unit weights, earth pressure, "
        "excavations, soil dynamics, groundwater flow and pipelines."),
    AgentRole(
        "research", "Research",
        ("research",),
        "You are the research specialist. Answer only from retrieved local documents and say which "
        "source each claim comes from; distinguish literature and standards from project measurements. "
        "If nothing relevant is retrieved, say so."),
)}

_DOMAIN_ROLE: Dict[str, str] = {d: r.name for r in ROLES.values() for d in r.domains}

# Phrases that start a new step; sentence ends and semicolons also split.
_CLAUSE_SPLIT = re.compile(
    r"(?<=[.?!;])\s+|\s*,?\s*\b(?:and then|then|after that|afterwards|next|also)\b[\s,]*", re.IGNORECASE)
_AND_SPLIT = re.compile(r"\s+\band\b\s+", re.IGNORECASE)


@dataclass
class PlanStep:
    id: int
    role: str
    task: str


def _clause_role(clause: str) -> Optional[str]:
    domains = infer_categories(clause)
    if "research" in domains and not _NUMERIC_INPUT.search(clause):
        return "research"  # literature wording outranks the topic's calculators, as in rank_tools
    for domain in domains:
        if domain in _DOMAIN_ROLE:
            return _DOMAIN_ROLE[domain]
    return None


def _clauses(message: str) -> List[Tuple[str, Optional[str]]]:
    """Split a request into (text, role) clauses; "A and B" splits only when A, B have different roles."""
    out: List[Tuple[str, Optional[str]]] = []
    for part in _CLAUSE_SPLIT.split(message or ""):
        part = (part or "").strip(" ,.;")
        if not part:
            continue
        pieces = [p.strip(" ,") for p in _AND_SPLIT.split(part) if p.strip(" ,")]
        roles = [_clause_role(p) for p in pieces]
        if len(pieces) > 1 and all(roles) and len(set(roles)) > 1:
            out.extend(zip(pieces, roles))
        else:
            out.append((part, _clause_role(part)))
    return out


def plan_request(message: str) -> List[PlanStep]:
    """
    Plan a request into specialist steps. Role-less clauses ("with B = 2 m") join the step before
    them; adjacent clauses with the same role form one step. Fewer than two steps = not compound.
    """
    steps: List[PlanStep] = []
    pending = ""  # leading role-less text, prepended to the first step
    for text, role in _clauses(message):
        if role is None:
            if steps:
                steps[-1].task += ", " + text
            else:
                pending = (pending + " " + text).strip()
        elif steps and steps[-1].role == role:
            steps[-1].task += ", " + text
        else:
            steps.append(PlanStep(len(steps) + 1, role, (pending + " " + text).strip()))
            pending = ""
    if len(steps) > MAX_STEPS:
        steps = steps[:MAX_STEPS]
    return steps


def verify_results(steps: List[PlanStep], step_tools: List[List[Dict[str, Any]]]) -> List[str]:
    """Deterministic post-checks; one line per problem a reader must know about."""
    issues: List[str] = []
    for step, tools in zip(steps, step_tools):
        label = ROLES[step.role].label
        if not tools:
            issues.append(f"{label}: no calculation or retrieval was run for \"{step.task}\".")
        for t in tools:
            wrapper = t.get("result") if isinstance(t.get("result"), dict) else {}
            if wrapper.get("status") == "error":
                issues.append(f"{label}: {t.get('name')} failed ({wrapper.get('error')}).")
    return issues


def _history_for(original: str, previous: List[List[Dict[str, Any]]],
                 history: Optional[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """History for the next specialist: the original request plus every earlier tool result."""
    items = list(history or []) + [{"role": "user", "content": original}]
    for tools in previous:
        for t in tools:
            items.append({"role": "assistant", "content": "",
                          "tool": {"name": t.get("name"), "arguments": t.get("arguments"),
                                   "result": t.get("result")}})
    return items


class MultiAgentOrchestrator:
    """Same ``run`` / ``run_stream`` surface as ``GeoAIAgent``; compound requests fan out to specialists."""

    def __init__(self, provider: ModelProvider, registry: GeoAIToolRegistry, **agent_kwargs: Any):
        self._provider = provider
        self._registry = registry
        self._kwargs = agent_kwargs

    def _plain(self) -> GeoAIAgent:
        return GeoAIAgent(self._provider, self._registry, **self._kwargs)

    def _specialist(self, role: AgentRole) -> GeoAIAgent:
        return GeoAIAgent(self._provider, self._registry, domains=role.domains,
                          role_instructions=role.instructions, **self._kwargs)

    @staticmethod
    def _combine(steps: List[PlanStep], texts: List[str], step_tools: List[List[Dict[str, Any]]]) -> str:
        parts = [f"**{ROLES[s.role].label}**\n{(t or '').strip() or '(no answer)'}" for s, t in zip(steps, texts)]
        issues = verify_results(steps, step_tools)
        if issues:
            parts.append("**Checks**\n" + "\n".join(f"- {i}" for i in issues))
        return "\n\n".join(parts)

    def run(self, user_message: str, context: Optional[Dict[str, Any]] = None,
            history: Optional[List[Dict[str, Any]]] = None) -> AgentResponse:
        steps = plan_request(user_message)
        if len(steps) < 2:
            return self._plain().run(user_message, context, history)
        texts: List[str] = []
        step_tools: List[List[Dict[str, Any]]] = []
        for step in steps:
            resp = self._specialist(ROLES[step.role]).run(
                step.task, context, _history_for(user_message, step_tools, history))
            texts.append(resp.response_text)
            step_tools.append(list(resp.tools_used))
        return AgentResponse(response_text=self._combine(steps, texts, step_tools),
                             tools_used=[t for tools in step_tools for t in tools],
                             finish_reason="complete")

    def run_stream(self, user_message: str, context: Optional[Dict[str, Any]] = None,
                   history: Optional[List[Dict[str, Any]]] = None) -> Iterator[AgentStreamEvent]:
        steps = plan_request(user_message)
        if len(steps) < 2:
            yield from self._plain().run_stream(user_message, context, history)
            return
        yield AgentStreamEvent(type="plan", content=json.dumps([asdict(s) for s in steps]))
        texts: List[str] = []
        step_tools: List[List[Dict[str, Any]]] = []
        for step in steps:
            role = ROLES[step.role]
            yield AgentStreamEvent(type="stage", content=f"agent:{role.label}")
            tokens: List[str] = []
            tools: List[Dict[str, Any]] = []
            started: Dict[str, Any] = {}
            for ev in self._specialist(role).run_stream(
                    step.task, context, _history_for(user_message, step_tools, history)):
                if ev.type == "token":
                    tokens.append(ev.content or "")  # the combined answer is emitted once, below
                    continue
                if ev.type == "done":
                    continue
                if ev.type == "tool_start":
                    started[ev.tool_name] = ev.tool_args
                elif ev.type == "tool_result":
                    tools.append({"name": ev.tool_name, "arguments": started.pop(ev.tool_name, None),
                                  "result": ev.tool_result, "visuals": ev.visuals or []})
                yield ev
            texts.append("".join(tokens))
            step_tools.append(tools)
        yield AgentStreamEvent(type="stage", content="writing_answer")
        yield AgentStreamEvent(type="token", content=self._combine(steps, texts, step_tools))
        yield AgentStreamEvent(type="done")


__all__ = ["AgentRole", "MultiAgentOrchestrator", "PlanStep", "ROLES", "plan_request", "verify_results"]
