"""Deterministic helpers and tools for tracking student progress."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from google.adk.tools import FunctionTool, ToolContext


_COURSE_DATA: Optional[Dict[str, Any]] = None
_CHAPTER_ORDER: List[str] = []
_CHAPTER_MAP: Dict[str, Dict[str, Any]] = {}
_ALIAS_MAP: Dict[str, str] = {}
_PROGRESS_STATE: Dict[str, Dict[str, Any]] = {}
_STATE_STUDENT_ID_KEY = "progress_student_id"


def _course_path() -> Path:
    return Path(__file__).resolve().parent / "data" / "course.json"


def _ensure_course_loaded() -> Dict[str, Any]:
    global _COURSE_DATA, _CHAPTER_ORDER, _CHAPTER_MAP, _ALIAS_MAP
    if _COURSE_DATA is not None:
        return _COURSE_DATA

    course_json = json.loads(_course_path().read_text())
    chapters = sorted(course_json.get("chapters", []), key=lambda c: c.get("order", 0))
    course_json["chapters"] = chapters

    _CHAPTER_ORDER = []
    _CHAPTER_MAP = {}
    _ALIAS_MAP = {}
    for chapter in chapters:
        cid = (chapter.get("chapter_id") or "").strip()
        if not cid:
            continue
        normalized_id = cid.lower()
        _CHAPTER_ORDER.append(normalized_id)
        _CHAPTER_MAP[normalized_id] = chapter

        title = (chapter.get("title") or "").lower()
        week_label = (chapter.get("week_label") or "").lower()
        order_alias = f"chapter {chapter.get('order')}" if chapter.get("order") else ""
        aliases = {normalized_id, title, week_label, order_alias}
        for alias in aliases:
            if alias:
                _ALIAS_MAP[alias] = normalized_id

    _COURSE_DATA = course_json
    return _COURSE_DATA


def _normalize_student_id(student_id: Optional[str]) -> str:
    if not student_id:
        return "default_student"
    return student_id.strip().lower() or "default_student"


def _generate_student_id() -> str:
    return f"student_{uuid4().hex[:8]}"


def _resolve_student_id(
    student_id: Optional[str],
    tool_context: Optional[ToolContext] = None,
) -> str:
    provided = _normalize_student_id(student_id)
    if student_id and provided:
        # explicit ID supplied
        if tool_context is not None:
            tool_context.state[_STATE_STUDENT_ID_KEY] = provided
        return provided

    if tool_context is not None:
        existing = tool_context.state.get(_STATE_STUDENT_ID_KEY)
        if existing:
            return existing
        generated = _generate_student_id()
        tool_context.state[_STATE_STUDENT_ID_KEY] = generated
        return generated

    return _generate_student_id()


def _normalize_chapter_id(chapter_label: Optional[str]) -> Optional[str]:
    if not chapter_label:
        return None
    _ensure_course_loaded()
    key = chapter_label.strip().lower()
    if not key:
        return None
    if key in _ALIAS_MAP:
        return _ALIAS_MAP[key]
    if key in _CHAPTER_ORDER:
        return key
    return None


def _chapter_summary(chapter_id: Optional[str]) -> Optional[Dict[str, Any]]:
    if not chapter_id:
        return None
    _ensure_course_loaded()
    chapter = _CHAPTER_MAP.get(chapter_id)
    if not chapter:
        return None
    return {
        "chapter_id": chapter.get("chapter_id"),
        "title": chapter.get("title"),
        "order": chapter.get("order"),
        "week_label": chapter.get("week_label"),
        "learning_outcomes": chapter.get("learning_outcomes", []),
    }


def _build_snapshot(student_id: str) -> Dict[str, Any]:
    _ensure_course_loaded()
    normalized_student = _normalize_student_id(student_id)
    progress = _PROGRESS_STATE.get(normalized_student, {"completed": []})
    completed_ids = progress.get("completed", [])
    ordered_completed = sorted(completed_ids, key=_CHAPTER_ORDER.index)

    next_chapter_id = next(
        (cid for cid in _CHAPTER_ORDER if cid not in ordered_completed),
        None,
    )

    return {
        "student_id": normalized_student,
        "completed_chapters": [
            _chapter_summary(cid) for cid in ordered_completed if _chapter_summary(cid)
        ],
        "next_chapter": _chapter_summary(next_chapter_id),
    }


def get_course_outline_data() -> Dict[str, Any]:
    """Return the canonical course outline for grounding progress responses."""

    course = _ensure_course_loaded()
    return {
        "unit_id": course.get("unit_id"),
        "unit_name": course.get("unit_name"),
        "description": course.get("description"),
        "learning_outcomes_overall": course.get("learning_outcomes_overall", []),
        "chapters": [
            {
                "chapter_id": chapter.get("chapter_id"),
                "title": chapter.get("title"),
                "order": chapter.get("order"),
                "week_label": chapter.get("week_label"),
                "learning_outcomes": chapter.get("learning_outcomes", []),
                "prerequisites": chapter.get("prerequisites", []),
            }
            for chapter in course.get("chapters", [])
        ],
    }


def record_student_progress(
    student_id: Optional[str] = None,
    completed_chapters: Optional[List[str]] = None,
    note: Optional[str] = None,
    tool_context: Optional[ToolContext] = None,
) -> Dict[str, Any]:
    """Persist completed chapters for a student and return the updated snapshot."""

    _ensure_course_loaded()
    normalized_student = _resolve_student_id(student_id, tool_context)
    progress = _PROGRESS_STATE.setdefault(normalized_student, {"completed": [], "notes": []})
    completed_ids = set(progress["completed"])
    newly_added: List[str] = []

    for chapter in completed_chapters or []:
        normalized_chapter = _normalize_chapter_id(chapter)
        if normalized_chapter and normalized_chapter not in completed_ids:
            progress["completed"].append(normalized_chapter)
            completed_ids.add(normalized_chapter)
            newly_added.append(normalized_chapter)

    progress["completed"].sort(key=_CHAPTER_ORDER.index)
    if note:
        progress.setdefault("notes", []).append(note)

    snapshot = _build_snapshot(normalized_student)
    return {
        "status": "success",
        "student_id": normalized_student,
        "added_chapters": [
            _chapter_summary(cid) for cid in newly_added if _chapter_summary(cid)
        ],
        "snapshot": snapshot,
        "message": "Progress updated" if newly_added else "No new chapters recorded",
    }


def get_progress_snapshot(
    student_id: Optional[str] = None,
    tool_context: Optional[ToolContext] = None,
) -> Dict[str, Any]:
    """Return completed chapters and the upcoming recommendation for a student."""

    normalized_student = _resolve_student_id(student_id, tool_context)
    snapshot = _build_snapshot(normalized_student)
    snapshot["status"] = "success"
    snapshot["message"] = "Progress snapshot retrieved"
    return snapshot


def get_next_chapter_recommendation(
    student_id: Optional[str] = None,
    tool_context: Optional[ToolContext] = None,
) -> Dict[str, Any]:
    """Return only the next chapter recommendation for a student."""

    normalized_student = _resolve_student_id(student_id, tool_context)
    snapshot = _build_snapshot(normalized_student)
    return {
        "status": "success",
        "student_id": snapshot["student_id"],
        "next_chapter": snapshot.get("next_chapter"),
        "completed_count": len(snapshot.get("completed_chapters", [])),
        "message": "Next chapter recommendation computed",
    }


get_course_outline_tool = FunctionTool(get_course_outline_data)
record_progress_tool = FunctionTool(record_student_progress)
get_progress_snapshot_tool = FunctionTool(get_progress_snapshot)
get_next_chapter_tool = FunctionTool(get_next_chapter_recommendation)


__all__ = [
    "get_course_outline_tool",
    "record_progress_tool",
    "get_progress_snapshot_tool",
    "get_next_chapter_tool",
    "get_course_outline_data",
    "record_student_progress",
    "get_progress_snapshot",
    "get_next_chapter_recommendation",
]
