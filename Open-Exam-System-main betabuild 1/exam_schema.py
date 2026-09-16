import json
from typing import Any

QUESTION_TYPES = {"multiple_choice", "written", "ordering", "file_upload"}


def normalize_questions(raw: Any) -> list[dict[str, Any]]:
    if not isinstance(raw, list):
        raise ValueError("questions must be a list")
    normalized = []
    for index, question in enumerate(raw, 1):
        if not isinstance(question, dict):
            raise ValueError(f"question {index} must be an object")
        question_type = str(question.get("type", "written"))
        if question_type not in QUESTION_TYPES:
            raise ValueError(f"question {index} has unsupported type")
        prompt = str(question.get("prompt", "")).strip()
        if not prompt:
            raise ValueError(f"question {index} needs a prompt")
        item = {
            "id": str(question.get("id", f"q{index}")),
            "type": question_type,
            "prompt": prompt,
            "points": max(0, int(question.get("points", 1))),
            "part": str(question.get("part", "Part 1")),
            "required": bool(question.get("required", True)),
        }
        if question_type == "multiple_choice":
            options = [str(option).strip() for option in question.get("options", []) if str(option).strip()]
            if len(options) < 2:
                raise ValueError(f"question {index} needs at least two choices")
            item["options"] = options
            item["multiple"] = bool(question.get("multiple", False))
        elif question_type == "written":
            item["max_chars"] = max(1, min(int(question.get("max_chars", 2000)), 100000))
        elif question_type == "ordering":
            items = [str(value).strip() for value in question.get("items", []) if str(value).strip()]
            if len(items) < 2:
                raise ValueError(f"question {index} needs at least two ordering items")
            item["items"] = items
        elif question_type == "file_upload":
            item["allowed_extensions"] = [str(value).lower().lstrip(".") for value in question.get("allowed_extensions", ["pdf", "png", "jpg"])]
            item["max_mb"] = max(1, min(int(question.get("max_mb", 10)), 1000))
        if question.get("media"):
            media = question["media"]
            if not isinstance(media, dict) or media.get("kind") not in {"image", "audio"} or not media.get("url"):
                raise ValueError(f"question {index} has invalid media")
            item["media"] = {"kind": media["kind"], "url": str(media["url"]), "alt": str(media.get("alt", ""))}
        normalized.append(item)
    return normalized


def parse_questions_json(raw: str) -> list[dict[str, Any]]:
    try:
        return normalize_questions(json.loads(raw))
    except json.JSONDecodeError as error:
        raise ValueError(f"questions JSON is invalid: {error}") from error
