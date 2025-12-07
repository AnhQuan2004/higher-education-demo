"""Shared factory and utilities for building sub-agents."""

from google.adk.agents import Agent

from rag.config import AGENT_MODEL
from rag.tools import corpus_tools


COMMON_TOOLS = [
    corpus_tools.query_rag_corpus_tool,
    corpus_tools.search_all_corpora_tool,
]


def build_agent(
    name: str,
    description: str,
    instruction: str,
    tools=None,
    model_override=None,
) -> Agent:
    """Factory that ensures agents share defaults while allowing overrides.

    Args:
        name: Agent name
        description: Agent description
        instruction: Agent instruction prompt
        tools: List of tools (defaults to COMMON_TOOLS)
        model_override: Optional model to use instead of AGENT_MODEL
                       (e.g., ROUTING_MODEL for routing/classification tasks)
    """
    toolset = tools if tools is not None else COMMON_TOOLS
    model = model_override if model_override is not None else AGENT_MODEL
    return Agent(
        name=name,
        model=model,
        description=description,
        instruction=instruction,
        tools=toolset,
        output_key=f"{name}_last_response",
    )
