"""Progress Tracker Agent — logs chapter completion and plans next steps."""

from google.adk.tools.agent_tool import AgentTool

from rag.config import ROUTING_MODEL
from rag.progress_tracker import (
    get_course_outline_tool,
    get_next_chapter_tool,
    get_progress_snapshot_tool,
    record_progress_tool,
)
from rag.sub_agents.agent_factory import build_agent


# Progress agent uses ROUTING_MODEL (gemini-2.0-flash-lite) for simple routing/lookups
# Performs straightforward data retrieval and next-chapter recommendations
progress_agent = build_agent(
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
    model_override=ROUTING_MODEL,
)

progress_agent_tool = AgentTool(agent=progress_agent)
