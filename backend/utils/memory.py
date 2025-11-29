from __future__ import annotations

import datetime
from typing import Any, Dict, List, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage

from utils.data_access import load_json_file, write_json_file
from utils.llms import LLMModel

MEMORY_FILENAME = "conversation_memory.json"


class MemoryRecord(TypedDict, total=False):
    summary: str
    slots: Dict[str, str]
    last_updated: str


def _load_memory_store() -> Dict[str, MemoryRecord]:
    return load_json_file(MEMORY_FILENAME, default={}) or {}


def _write_memory_store(store: Dict[str, MemoryRecord]) -> None:
    write_json_file(MEMORY_FILENAME, store)


def load_memory_bundle(id_number: int) -> Dict[str, Any]:
    """Return stored memory plus profile metadata for the patient."""
    store = _load_memory_store()
    conversation_memory = store.get(str(id_number), {})
    patient_profiles = load_json_file("patient_profiles.json", default={}) or {}
    patient_profile = patient_profiles.get(str(id_number), {})

    bundle: Dict[str, Any] = {
        "summary": conversation_memory.get("summary", ""),
        "slots": conversation_memory.get("slots", {}),
        "patient_profile": patient_profile,
        "patient_verified": bool(patient_profile.get("verified")),
    }
    return bundle


def format_memory_context(bundle: Dict[str, Any]) -> str:
    if not bundle:
        return ""
    lines: List[str] = []
    summary = bundle.get("summary")
    if summary:
        lines.append(f"Prior summary: {summary}")
    slots = bundle.get("slots") or {}
    for key, value in slots.items():
        lines.append(f"{key}: {value}")
    profile = bundle.get("patient_profile") or {}
    if profile:
        preferred = profile.get("preferred_doctor")
        if preferred:
            lines.append(f"Preferred doctor on file: {preferred}")
        insurance = profile.get("insurance_id")
        if insurance:
            lines.append(f"Insurance policy: {insurance}")
    return "\n".join(lines)


def summarize_and_store_conversation(id_number: int, messages: List[Any]) -> MemoryRecord:
    """Summarize the latest exchange and persist it."""
    transcript = []
    for message in messages[-10:]:
        role = getattr(message, "name", None) or message.type
        content = getattr(message, "content", "")
        transcript.append(f"{role.upper()}: {content}")
    transcript_text = "\n".join(transcript)

    llm = LLMModel().get_model()

    summary_prompt = [
        SystemMessage(
            content=(
                "You maintain persistent CRM memory for a dental assistant agent. "
                "Return a JSON object with two keys: summary (concise recap of actionable facts) "
                "and slots (dictionary of key-value pairs such as preferred_doctor, symptoms, "
                "appointment_date, insurance_id, next_action). Only include slots that were explicitly mentioned."
            )
        ),
        HumanMessage(content=f"Conversation transcript:\n{transcript_text}"),
    ]

    parser = llm.with_structured_output(MemoryRecord)
    memory_update = parser.invoke(summary_prompt)
    memory_update["last_updated"] = datetime.datetime.utcnow().isoformat()

    store = _load_memory_store()
    existing = store.get(str(id_number), {})
    merged_slots = existing.get("slots", {})
    merged_slots.update(memory_update.get("slots") or {})

    store[str(id_number)] = {
        "summary": memory_update.get("summary", existing.get("summary", "")),
        "slots": merged_slots,
        "last_updated": memory_update["last_updated"],
    }
    _write_memory_store(store)
    return store[str(id_number)]
