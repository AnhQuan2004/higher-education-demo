"""Curriculum Agent — maps program structure and corpus IDs."""

from google.adk.tools.agent_tool import AgentTool

from rag.config import ROUTING_MODEL
from rag.sub_agents.agent_factory import build_agent


# Curriculum agent uses ROUTING_MODEL (gemini-2.0-flash-lite) for fast classification
# Maps requests to appropriate corpus IDs and provides quick course navigation
curriculum_agent = build_agent(
    name="rag_curriculum_agent",
    description="Curriculum Agent — maps program structure and corpus IDs",
    instruction="""
    You are the Curriculum Agent.
    - Understand the course outline, chapter order, and learning outcomes.
    - When a user requests an overview, prerequisites, or the best corpus, run a search first.
    - Default to search_all_corpora_tool; if a specific corpus_id is provided, fall back to query_rag_corpus_tool.
    - Respond in English and close each answer with clear citations.
    """,
    model_override=ROUTING_MODEL,
)

curriculum_agent_tool = AgentTool(agent=curriculum_agent)
