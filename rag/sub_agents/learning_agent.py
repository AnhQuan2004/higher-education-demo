"""Learning Agent — explains topics using RAG corpora."""

from google.adk.tools.agent_tool import AgentTool

from rag.sub_agents.agent_factory import build_agent


# Learning agent uses AGENT_MODEL (gemini-2.5-flash) for high-quality content generation
# Needs stronger reasoning for explanations, examples, and comparisons
learning_agent = build_agent(
    name="rag_learning_agent",
    description="Learning Agent — explains topics using RAG corpora",
    instruction="""
    You are the Learning Agent who delivers topic explanations.
    - When students ask for concepts, examples, or comparisons, ground the answer in the corpora.
    - Use search_all_corpora_tool for broad questions; query_rag_corpus_tool when a single corpus is relevant.
    - Format explanations with concise paragraphs or bullet steps and attach citations for each key point.
    """,
)

learning_agent_tool = AgentTool(agent=learning_agent)
