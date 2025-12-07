"""Assessment Agent — pulls rubrics and crafts feedback."""

from google.adk.tools.agent_tool import AgentTool

from rag.sub_agents.agent_factory import build_agent


# Assessment agent uses AGENT_MODEL (gemini-2.5-flash) for high-quality feedback generation
# Requires strong reasoning for grading, rubric interpretation, and constructive feedback
assessment_agent = build_agent(
    name="rag_assessment_agent",
    description="Assessment Agent — pulls rubrics and crafts feedback",
    instruction="""
    You are the Assessment Agent responsible for scoring submissions.
    - Retrieve rubrics, sample answers, or checklists from the corpora before responding.
    - Respect any rubric provided by the user while supplementing with retrieved evidence when needed.
    - Give concise feedback with ✔️/❌ style criteria, improvement tips, and final citations.
    """,
)

assessment_agent_tool = AgentTool(agent=assessment_agent)
