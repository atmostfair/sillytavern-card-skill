from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


REQUIRED_TOP = {"spec": str, "spec_version": str, "data": dict}
REQUIRED_DATA = {
    "name": str,
    "description": str,
    "personality": str,
    "scenario": str,
    "first_mes": str,
    "mes_example": str,
}
OPTIONAL_DATA = {
    "creator_notes": str,
    "system_prompt": str,
    "post_history_instructions": str,
    "alternate_greetings": list,
    "tags": list,
    "creator": str,
    "character_version": str,
    "extensions": dict,
    "character_book": dict,
}
BOOK_REQUIRED = {
    "name": str,
    "description": str,
    "scan_depth": int,
    "token_budget": int,
    "recursive_scanning": bool,
    "extensions": dict,
    "entries": list,
}
ENTRY_REQUIRED = {
    "keys": list,
    "content": str,
    "enabled": bool,
    "insertion_order": int,
}
ENTRY_OPTIONAL = {
    "id": int,
    "name": str,
    "comment": str,
    "secondary_keys": list,
    "constant": bool,
    "selective": bool,
    "case_sensitive": bool,
    "position": str,
    "priority": int,
    "extensions": dict,
}
ALLOWED_POSITIONS = {"before_char", "after_char"}
PLACEHOLDER_RE = re.compile(r"\b(TODO|TBD|PLACEHOLDER|undefined)\b", re.I)


def type_name(expected: type[Any]) -> str:
    return expected.__name__


def load_json(path: Path) -> tuple[dict[str, Any] | None, str, str | None]:
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        return None, "", f"could not read file: {exc}"
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError as exc:
        return None, raw, f"JSON parse failed: {exc}"
    if not isinstance(obj, dict):
        return None, raw, "top-level JSON value must be an object"
    return obj, raw, None


def check_typed_object(
    location: str,
    value: dict[str, Any],
    required: dict[str, type[Any]],
    errors: list[str],
) -> None:
    for key, expected in required.items():
        if key not in value or not isinstance(value[key], expected):
            errors.append(f"{location}.{key} must be {type_name(expected)}")


def check_optional_typed_object(
    location: str,
    value: dict[str, Any],
    optional: dict[str, type[Any]],
    errors: list[str],
) -> None:
    for key, expected in optional.items():
        if key in value and not isinstance(value[key], expected):
            errors.append(f"{location}.{key} must be {type_name(expected)}")


def validate_card(
    path: Path,
    min_entries: int,
    expect_profile: str | None,
    expect_token_budget: int | None,
) -> tuple[list[str], list[str], dict[str, Any]]:
    errors: list[str] = []
    warnings: list[str] = []
    obj, raw, load_error = load_json(path)
    if load_error:
        return [f"{path.name}: {load_error}"], warnings, {}
    assert obj is not None

    check_typed_object(path.name, obj, REQUIRED_TOP, errors)
    if obj.get("spec") != "chara_card_v2":
        errors.append(f"{path.name}: spec must be chara_card_v2")
    if obj.get("spec_version") != "2.0":
        errors.append(f"{path.name}: spec_version must be 2.0")

    data = obj.get("data") if isinstance(obj.get("data"), dict) else {}
    check_typed_object(f"{path.name}.data", data, REQUIRED_DATA, errors)
    check_optional_typed_object(f"{path.name}.data", data, OPTIONAL_DATA, errors)

    for field in REQUIRED_DATA:
        value = data.get(field)
        if isinstance(value, str) and not value.strip():
            errors.append(f"{path.name}: data.{field} must be non-empty")

    alt = data.get("alternate_greetings")
    if isinstance(alt, list) and not all(isinstance(item, str) and item.strip() for item in alt):
        errors.append(f"{path.name}: alternate_greetings must contain non-empty strings")

    tags = data.get("tags")
    if isinstance(tags, list) and not all(isinstance(item, str) for item in tags):
        errors.append(f"{path.name}: tags must contain strings")

    mes_example = data.get("mes_example")
    if isinstance(mes_example, str) and "<START>" not in mes_example:
        warnings.append(f"{path.name}: mes_example has no <START> marker")

    placeholders = sorted(set(PLACEHOLDER_RE.findall(raw)))
    if placeholders:
        errors.append(f"{path.name}: placeholder markers found: {placeholders}")

    book = data.get("character_book")
    entry_count = 0
    token_budget = None
    if book is None:
        errors.append(f"{path.name}: data.character_book is required for generated story cards")
    elif not isinstance(book, dict):
        errors.append(f"{path.name}: data.character_book must be object")
    else:
        check_typed_object(f"{path.name}.character_book", book, BOOK_REQUIRED, errors)
        token_budget = book.get("token_budget")
        if expect_token_budget is not None and token_budget != expect_token_budget:
            errors.append(f"{path.name}: character_book.token_budget must be {expect_token_budget}")

        entries = book.get("entries") if isinstance(book.get("entries"), list) else []
        entry_count = len(entries)
        if entry_count < min_entries:
            errors.append(f"{path.name}: character_book.entries has {entry_count}, expected at least {min_entries}")
        for index, entry in enumerate(entries):
            if not isinstance(entry, dict):
                errors.append(f"{path.name}: entry {index} must be object")
                continue
            check_typed_object(f"{path.name}.entry[{index}]", entry, ENTRY_REQUIRED, errors)
            check_optional_typed_object(f"{path.name}.entry[{index}]", entry, ENTRY_OPTIONAL, errors)
            keys = entry.get("keys")
            if isinstance(keys, list) and not all(isinstance(key, str) and key.strip() for key in keys):
                errors.append(f"{path.name}: entry {index}.keys must contain non-empty strings")
            secondary_keys = entry.get("secondary_keys")
            if isinstance(secondary_keys, list) and not all(isinstance(key, str) for key in secondary_keys):
                errors.append(f"{path.name}: entry {index}.secondary_keys must contain strings")
            content = entry.get("content")
            if isinstance(content, str) and not content.strip():
                errors.append(f"{path.name}: entry {index}.content must be non-empty")
            position = entry.get("position")
            if isinstance(position, str) and position not in ALLOWED_POSITIONS:
                warnings.append(
                    f"{path.name}: entry {index}.position is {position!r}; expected one of {sorted(ALLOWED_POSITIONS)}"
                )

    profile = None
    extensions = data.get("extensions")
    if isinstance(extensions, dict):
        profile = extensions.get("profile")
        if expect_profile is not None and profile != expect_profile:
            errors.append(f"{path.name}: data.extensions.profile must be {expect_profile}")
    elif expect_profile is not None:
        errors.append(f"{path.name}: data.extensions must be object with profile={expect_profile}")

    metrics = {
        "file": path.name,
        "bytes": len(raw.encode("utf-8")),
        "entries": entry_count,
        "token_budget": token_budget,
        "profile": profile,
    }
    return errors, warnings, metrics


def iter_card_paths(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    return sorted(item for item in path.glob("*.json") if item.name != "manifest.json")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate SillyTavern Character Card V2 JSON compatibility.")
    parser.add_argument("path", help="Card JSON file or directory containing card JSON files.")
    parser.add_argument("--min-entries", type=int, default=1, help="Minimum required character_book entry count.")
    parser.add_argument("--expect-profile", default=None, help="Require data.extensions.profile to match this value.")
    parser.add_argument("--expect-token-budget", type=int, default=None, help="Require character_book.token_budget.")
    parser.add_argument("--strict-warnings", action="store_true", help="Exit non-zero when warnings are present.")
    args = parser.parse_args()

    target = Path(args.path)
    paths = iter_card_paths(target)
    if not paths:
        raise SystemExit(f"no card JSON files found: {target}")

    all_errors: list[str] = []
    all_warnings: list[str] = []
    rows: list[dict[str, Any]] = []
    for path in paths:
        errors, warnings, metrics = validate_card(
            path,
            min_entries=args.min_entries,
            expect_profile=args.expect_profile,
            expect_token_budget=args.expect_token_budget,
        )
        all_errors.extend(errors)
        all_warnings.extend(warnings)
        if metrics:
            rows.append(metrics)

    print(f"checked_cards {len(rows)}")
    print("file,bytes,entries,token_budget,profile")
    for row in rows:
        print(f"{row['file']},{row['bytes']},{row['entries']},{row['token_budget']},{row['profile']}")
    print(f"errors {len(all_errors)}")
    for error in all_errors:
        print(f"ERROR: {error}")
    print(f"warnings {len(all_warnings)}")
    for warning in all_warnings:
        print(f"WARN: {warning}")

    if all_errors or (args.strict_warnings and all_warnings):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
