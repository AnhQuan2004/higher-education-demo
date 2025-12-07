# ADK RAG Student Assistant

This project packages a multi-agent student assistant on top of Google's [Agent Development Kit (ADK)] and Vertex AI RAG Engine. The orchestrator agent lives in `rag/agent.py` and delegates requests to specialist sub-agents for curriculum search, learning support, assessment feedback, and progress tracking while still exposing the full suite of Vertex AI RAG + Google Cloud Storage management tools.

## Repository Layout

```
higher-education-demo/
├── rag/
│   ├── agent.py                # Root agent configuration and routing instructions
│   ├── sub_agents.py           # Curriculum / Learning / Assessment / Progress agents
│   ├── progress_tracker.py     # Deterministic helpers backed by data/course.json
│   ├── data/course.json        # Canonical course outline used by the progress agent
│   ├── tools/                  # FunctionTool wrappers for Vertex AI RAG + GCS APIs
│   └── config/                 # Config loader that pulls values from .env
├── software_tutor/             # Reference tutor app using the same RAG helpers
├── requirements.txt            # Python dependencies for local execution
└── README.md
```

## Multi-Agent Architecture

| Agent | Purpose | Key Tools |
| --- | --- | --- |
| `root_agent` | Student-facing conductor; decides which skill handles each request; owns infra tools (corpora, files, GCS). | `rag.tools.*`, `storage_tools.*`, ADK memory, sub-agent tools |
| `rag_curriculum_agent` | Reads the syllabus, finds relevant corpora/chapters, cites search results. | `query_rag_corpus`, `search_all_corpora` |
| `rag_learning_agent` | Explains topics, compares concepts, formats study notes with citations. | `query_rag_corpus`, `search_all_corpora` |
| `rag_assessment_agent` | Fetches rubrics, judges submissions, delivers ✔️/❌ feedback. | `query_rag_corpus`, `search_all_corpora` |
| `rag_progress_agent` | Logs finished chapters, reads `data/course.json`, recommends next objectives. | `progress_tracker` FunctionTools |

Routing rules live directly in `rag/agent.py`. The root prompt forces any conceptual request to flow through one of the sub-agents before those agents call the Vertex AI RAG search tools.

## Configuration

All runtime settings come from `.env`. The config loader (`rag/config/__init__.py`) reads both the root `.env` file and a legacy `rag/config/.env` (if present). Key variables:

```
# GCP + Vertex AI
GOOGLE_CLOUD_PROJECT=...
GOOGLE_CLOUD_LOCATION=asia-east1
VERTEXAI_PROJECT=...
VERTEXAI_LOCATION=asia-east1

# Agents
RAG_AGENT_NAME=rag_corpus_manager
RAG_AGENT_MODEL=gemini-2.5-flash              # Sub-agents: quality generation
RAG_ROUTING_MODEL=gemini-2.0-flash-lite       # Root: fast routing decisions (NEW)
RAG_AGENT_OUTPUT_KEY=last_response

# RAG defaults (OPTIMIZED)
RAG_DEFAULT_EMBEDDING_MODEL=text-embedding-004
RAG_DEFAULT_TOP_K=3                            # Was 10 (60% reduction)
RAG_DEFAULT_SEARCH_TOP_K=3                     # Was 5 (40% reduction)
RAG_DEFAULT_VECTOR_DISTANCE_THRESHOLD=0.5
RAG_DEFAULT_PAGE_SIZE=50

# Context optimization (NEW)
RAG_MAX_HISTORY_TURNS=5                        # Limit conversation history

# GCS defaults
GCS_DEFAULT_STORAGE_CLASS=STANDARD
GCS_DEFAULT_LOCATION=US
GCS_LIST_BUCKETS_MAX_RESULTS=50
GCS_LIST_BLOBS_MAX_RESULTS=100
GCS_DEFAULT_CONTENT_TYPE=application/pdf

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

Update `.env` with your project IDs and credentials. See `.env.example` for reference.

## Setup

1. **Python environment**
   ```bash
   cd /Users/vbi2/Documents/paper/adk_copy
   python3.11 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. **Authenticate**
   - Ensure `gcloud auth application-default login` has been run for the target project **or** provide service account credentials through the usual ADC variables.
3. **Configure environment**
   - Copy `.env.example` if you have one, or edit `.env` directly with the values shown above.

## Running the Agents

The repository works with the ADK CLI. From `adk_copy/` run:

```bash
adk run rag
```

This launches the root `rag` app defined in `rag/agent.py`. Open the ADK Dev UI (default `127.0.0.1:8000/dev-ui/?app=rag`) to interact with the student assistant. The greeting will introduce the agent as “a student assistant that coordinates specialist tutors and tools for you.”

### Common Workflows

- **Curriculum/Learning questions**: Ask conceptual prompts. The trace should show `rag_curriculum_agent` or `rag_learning_agent` calling `search_all_corpora` before responding.
- **Assessment check**: Provide a JSON payload with `topic`, `submission`, and optional `rubric`. The root agent routes to `rag_assessment_agent` for scoring.
- **Progress tracking**: Tell the agent which chapters a student finished (include a `student_id`). The root agent invokes `rag_progress_agent`, which uses the deterministic tools to log completion and suggest the next chapter from `data/course.json`.
- **Corpus / GCS management**: Explicitly ask to create/list/delete corpora or buckets. These instructions bypass the sub-agents and use the FunctionTool wrappers defined in `rag/tools/`.

## Progress Tracker Data Contract

`rag/progress_tracker.py` keeps an in-memory store of completed chapters per student. It loads `data/course.json` once at startup, normalizes chapter aliases (IDs, titles, week labels, “chapter N”), and exposes these FunctionTools:

- `get_course_outline_tool`: returns the entire outline for grounding responses.
- `record_progress_tool`: takes `student_id`, `completed_chapters`, and optional `note`.
- `get_progress_snapshot_tool`: lists completed chapters + next recommendation.
- `get_next_chapter_tool`: quick “what’s next” call used by the agent prompt.

Because this is an in-memory tracker, restarting the process resets progress. Persist to a database before production use.

## Developer Tips

- **Sub-agent prompts** live in `rag/sub_agents.py`. Adjust instructions or swap tools to change behavior.
- **Tool wiring** is centralized in `rag/agent.py`. Adding a new specialist requires importing its `AgentTool` and listing it in the root `tools` array.
- **RAG/GCS helpers** in `rag/tools/` are plain `FunctionTool`s built on Vertex AI and `google-cloud-storage`. They rely on the env vars above.
- **Testing routes**: Use the ADK Dev UI trace tab to confirm that the root agent always calls a sub-agent before the RAG query tools when handling instructional content.

## Performance Optimizations

This system includes six performance optimization phases (Dec 2025):

### Quick Performance Summary

| Optimization | What Changed | Expected Gain |
| --- | --- | --- |
| **Config Tuning** | RAG top_k: 10→3, added lightweight routing model | -15% latency, -40% context |
| **Parallel Search** | ThreadPoolExecutor for multi-corpus queries | -75% latency (4+ corpora) |
| **Routing Model** | Root uses gemini-2.0-flash-lite instead of gemini-2.5-flash | -70% routing latency, -80% cost |
| **Observability** | LatencyLogger tracks per-operation metrics | Bottleneck identification |
| **Context Management** | Conversation history limited to 5 turns | -80% context for long sessions |
| **Streaming** | SSE mode for progressive response delivery | TTFT <1.2s, better UX |

### Monitoring Performance

Use the latency logger to track operation times:

```python
from rag.utils import log_latency, get_metrics_summary

# Automatic timing
with log_latency("search_query", query=user_input):
    results = search_all_corpora(user_input)

# View metrics
summary = get_metrics_summary()
print(f"Average search latency: {summary['search_query']['avg_ms']:.0f}ms")
```

### Configuration Tuning

Adjust these environment variables to trade latency vs quality:

```bash
# More aggressive (faster but fewer results)
RAG_DEFAULT_TOP_K=2
RAG_MAX_HISTORY_TURNS=3

# More conservative (slower but higher quality)
RAG_DEFAULT_TOP_K=5
RAG_MAX_HISTORY_TURNS=10
```

## Troubleshooting

| Issue | Fix |
| --- | --- |
| `google.api_core.exceptions.PermissionDenied` | Verify the service account has Vertex AI Admin + Storage Admin roles and that `GOOGLE_CLOUD_PROJECT` matches the resources. |
| Agent introductions don't mention the student assistant line | Ensure your `.env` sets the proper model values and restart `adk run rag` so the updated prompt loads. |
| Progress agent can't find a chapter | Use exact IDs (`ch1`, `ch2`, …) or the chapter title; check `data/course.json` for valid entries. |
| Slow search responses | Check `RAG_DEFAULT_TOP_K` and `RAG_DEFAULT_SEARCH_TOP_K` values. Lower values = faster. Use latency logger to identify bottlenecks. |
| High memory usage | Verify `RAG_MAX_HISTORY_TURNS` is set (limits conversation history). |
