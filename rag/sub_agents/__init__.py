"""Specialized RAG sub-agents for curriculum, learning, and assessment flows."""

from rag.sub_agents.curriculum_agent import curriculum_agent, curriculum_agent_tool
from rag.sub_agents.learning_agent import learning_agent, learning_agent_tool
from rag.sub_agents.assessment_agent import assessment_agent, assessment_agent_tool
from rag.sub_agents.progress_agent import progress_agent, progress_agent_tool


# NOTE: Streaming is handled at runner level via DEFAULT_RUN_CONFIG
# Sub-agents inherit streaming behavior from root agent runner.
# See agent.py for RunConfig with StreamingMode.SSE
# Learning and assessment agents benefit most from streaming (content generation)
# Curriculum and progress agents are fast enough without streaming overhead
__all__ = [
    "curriculum_agent",
    "learning_agent",
    "assessment_agent",
    "progress_agent",
    "curriculum_agent_tool",
    "learning_agent_tool",
    "assessment_agent_tool",
    "progress_agent_tool",
]
