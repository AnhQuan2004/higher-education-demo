"""Specialized RAG sub-agents for curriculum, learning, and assessment flows."""

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from rag.config import AGENT_MODEL
from rag.tools import corpus_tools
from rag.progress_tracker import (
    get_course_outline_tool,
    get_next_chapter_tool,
    get_progress_snapshot_tool,
    record_progress_tool,
)


_COMMON_TOOLS = [
    corpus_tools.query_rag_corpus_tool,
    corpus_tools.search_all_corpora_tool,
]


def _build_agent(
    name: str,
    description: str,
    instruction: str,
    tools=None,
) -> Agent:
    """Factory that ensures agents share defaults while allowing overrides."""

    toolset = tools if tools is not None else _COMMON_TOOLS
    return Agent(
        name=name,
        model=AGENT_MODEL,
        description=description,
        instruction=instruction,
        tools=toolset,
        output_key=f"{name}_last_response",
    )


curriculum_agent = _build_agent(
    name="rag_curriculum_agent",
    description="Curriculum Agent — maps program structure and corpus IDs",
    instruction="""
    You are the Curriculum Agent.
    - Understand the course outline, chapter order, and learning outcomes.
    - When a user requests an overview, prerequisites, or the best corpus, run a search first.
    - Default to search_all_corpora_tool; if a specific corpus_id is provided, fall back to query_rag_corpus_tool.
    - Respond in English and close each answer with clear citations.
    """,
)


learning_agent = _build_agent(
    name="rag_learning_agent",
    description="Learning Agent — explains topics using RAG corpora",
    instruction="""
    You are the Learning Agent who delivers topic explanations.
    - When students ask for concepts, examples, or comparisons, ground the answer in the corpora.
    - Use search_all_corpora_tool for broad questions; query_rag_corpus_tool when a single corpus is relevant.
    - Format explanations with concise paragraphs or bullet steps and attach citations for each key point.
    """,
)


assessment_agent = _build_agent(
    name="rag_assessment_agent",
    description="Assessment Agent — pulls rubrics and crafts feedback",
    instruction="""
    You are the Assessment Agent responsible for scoring submissions.
    - Retrieve rubrics, sample answers, or checklists from the corpora before responding.
    - Respect any rubric provided by the user while supplementing with retrieved evidence when needed.
    - Give concise feedback with ✔️/❌ style criteria, improvement tips, and final citations.
    """,
)


progress_agent = _build_agent(
    name="rag_progress_agent",
    description="Progress Tracker Agent — logs chapter completion and plans next steps",
    instruction="""
    You are the Progress Tracker Agent.
    - Always ground yourself in the official outline by calling get_course_outline_data before giving advice.
    - When a learner reports completed chapters, call record_student_progress with the list of chapters; the tool will auto-generate and store a student_id, so do NOT ask the user for it.
    - To answer "what's next", call get_next_chapter_tool (and get_progress_snapshot_tool if more context is needed).
    - Highlight completed chapters, identify the next recommended chapter (with title + order), and mention prerequisites if relevant.
    - Responses must be in English, concise, and end with: "Next up: <chapter title> (<chapter_id>)."
    """,
    tools=[
        get_course_outline_tool,
        record_progress_tool,
        get_progress_snapshot_tool,
        get_next_chapter_tool,
    ],
)


curriculum_agent_tool = AgentTool(agent=curriculum_agent)
learning_agent_tool = AgentTool(agent=learning_agent)
assessment_agent_tool = AgentTool(agent=assessment_agent)
progress_agent_tool = AgentTool(agent=progress_agent)


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
