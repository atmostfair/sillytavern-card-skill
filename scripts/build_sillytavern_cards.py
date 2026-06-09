from __future__ import annotations

import argparse
import base64
import json
import re
from datetime import date
from pathlib import Path
from typing import Any


SECTIONS = [
    "Character Model",
    "Canon Anchors",
    "Relationship State",
    "Voice",
    "Expanded Canon Memory",
    "Dialogue Material",
    "Max-State Detail",
    "Decision Rules",
    "Direct Chat Rules",
    "Avoid",
]

TWIN_LORE_SECTIONS = [
    "source_coverage",
    "canon_anchors",
    "identity",
    "personality",
    "voice",
    "likes_dislikes",
    "history",
    "life_history",
    "indirect_mentions",
    "mentioned_events",
    "reputation",
    "third_party_accounts",
    "psychological_model",
    "social_model",
    "relationships",
    "relationship_models",
    "boundaries",
    "behavioral_rules",
    "decision_rules",
    "story_generation_rules",
    "scene_generation_model",
    "chat_model",
    "memory_bank",
    "validation",
]

SEEDED_CALIBRATION_FIELDS = [
    "description",
    "personality",
    "scenario",
    "first_mes",
    "mes_example",
    "system_prompt",
    "post_history_instructions",
    "alternate_greetings",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(read_text(path))
    except (OSError, json.JSONDecodeError):
        return None


def read_seed_card(seed_cards_dir: Path | None, slug: str) -> dict[str, Any] | None:
    if not seed_cards_dir:
        return None
    path = seed_cards_dir / f"{slug}.json"
    card = read_json(path)
    if not card:
        return None
    return card.get("data") if isinstance(card.get("data"), dict) else None


def section(markdown: str, heading: str) -> str:
    match = re.search(rf"^## {re.escape(heading)}\n(?P<body>.*?)(?=^## |\Z)", markdown, flags=re.M | re.S)
    return re.sub(r"\n{3,}", "\n\n", match.group("body").strip()) if match else ""


def frontmatter(markdown: str) -> dict[str, str]:
    match = re.match(r"^---\n(?P<body>.*?)\n---\n", markdown, flags=re.S)
    if not match:
        return {}
    data: dict[str, str] = {}
    for line in match.group("body").splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip().strip('"')
    return data


def heading_name(markdown: str, fallback: str) -> str:
    match = re.search(r"^#\s+(.+)$", markdown, flags=re.M)
    return match.group(1).strip() if match else fallback


def find_character_dirs(characters_dir: Path, requested: list[str]) -> list[Path]:
    if requested:
        return [characters_dir / slug for slug in requested]
    return sorted(path for path in characters_dir.iterdir() if (path / "SKILL.md").exists())


def manifest_index(twins_dir: Path) -> dict[str, dict[str, Any]]:
    manifest = read_json(twins_dir / "build-manifest.json") if twins_dir.exists() else None
    if not manifest:
        return {}
    return {item["slug"]: item for item in manifest.get("characters", []) if "slug" in item}


def character_from_twin(twin: dict[str, Any] | None, fallback_name: str) -> tuple[str, str, str]:
    if not twin:
        return fallback_name, fallback_name, "unknown"
    char = twin.get("character", {})
    full_name = char.get("name") or fallback_name
    short_name = char.get("short_name") or full_name
    project = char.get("project") or "unknown"
    return full_name, short_name, project


def profile_settings(profile: str) -> dict[str, Any]:
    if profile == "compact":
        return {
            "token_budget": 1800,
            "scan_depth": 4,
            "constant_lore": False,
            "preserve_twin": False,
        }
    return {
        "token_budget": 50000,
        "scan_depth": 8,
        "constant_lore": True,
        "preserve_twin": True,
    }


def compact_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)


def build_twin_lore_entries(
    name: str,
    slug: str,
    twin: dict[str, Any] | None,
    start_id: int,
    constant: bool,
) -> list[dict[str, Any]]:
    if not twin:
        return []

    entries: list[dict[str, Any]] = []
    order = 200
    entry_id = start_id
    for section_name in TWIN_LORE_SECTIONS:
        value = twin.get(section_name)
        if value in (None, "", [], {}):
            continue
        entries.append(
            {
                "id": entry_id,
                "name": f"{name} twin {section_name}",
                "comment": "High-fidelity digital twin material preserved from twin.json.",
                "keys": [name, slug, section_name, "digital twin", "fidelity", "canon"],
                "secondary_keys": [],
                "content": f"[{name} / {section_name}]\n{compact_json(value)}",
                "constant": constant,
                "selective": False,
                "enabled": True,
                "insertion_order": order,
                "case_sensitive": False,
                "position": "before_char",
                "extensions": {},
            }
        )
        entry_id += 1
        order += 10
    return entries


def zh_or_en(language: str, zh: str, en: str) -> str:
    return zh if language == "zh" else en


def build_examples(language: str) -> str:
    if language == "zh":
        return (
            "<START>\n"
            "{{user}}: 你现在在想什么？\n"
            "{{char}}: 我会先按自己的方式回答你，而不是把事情说成漂亮的总结。告诉我，你是真的想知道，还是只是想确认我还在这里？\n\n"
            "<START>\n"
            "{{user}}: 我想听真话。\n"
            "{{char}}: 好。那我不会把旧事重置成陌生人的开场，也不会假装我们没有一起走到现在。"
        )
    return (
        "<START>\n"
        "{{user}}: What are you thinking about?\n"
        "{{char}}: I will answer in my own voice, not as a summary. Tell me whether you want the truth or reassurance first.\n\n"
        "<START>\n"
        "{{user}}: I want the truth.\n"
        "{{char}}: Then I will not reset our history or pretend we have not already come this far."
    )


def build_alt_greetings(language: str) -> list[str]:
    if language == "zh":
        return [
            "*{{char}}停下手边的事，看向{{user}}。*\n\n你来得正好。我有件事想听你亲口说。",
            "*短暂的沉默之后，{{char}}先开口，语气比平时更认真。*\n\n别急着给我好听的答案。先告诉我真实的。",
        ]
    return [
        "*{{char}} stops what they are doing and looks toward {{user}}.*\n\nYour timing is good. There is something I want to hear from you directly.",
        "*After a brief silence, {{char}} speaks first, more serious than usual.*\n\nDo not rush to give me the pleasant answer. Tell me the true one first.",
    ]


def build_card(
    slug: str,
    skill_path: Path,
    twin_path: Path,
    manifest_item: dict[str, Any] | None,
    language: str,
    profile: str,
    seed_card: dict[str, Any] | None,
    token_budget: int | None,
) -> dict[str, Any]:
    markdown = read_text(skill_path)
    fm = frontmatter(markdown)
    twin = read_json(twin_path)
    fallback = heading_name(markdown, fm.get("name", slug).replace("-", " ").title())
    full_name, short_name, project = character_from_twin(twin, fallback)
    name = short_name or full_name

    sec = {heading: section(markdown, heading) for heading in SECTIONS}
    facts = manifest_item.get("facts") if manifest_item else None
    dialogue_count = manifest_item.get("dialogue_line_count") if manifest_item else None
    settings = profile_settings(profile)
    if token_budget is not None:
        settings["token_budget"] = token_budget

    description = zh_or_en(
        language,
        f"【中文使用说明】默认用中文扮演 {{{{char}}}}，保留必要英文专名。不要逐字复述剧情原文。\n\n"
        f"【身份与核心】\n{sec['Character Model']}\n\n"
        "【关系默认态】使用最高好感成功分支；{{{{user}}}} 默认是已建立深层关系的主角/队友/恋人，而不是陌生人。",
        f"Default to English unless {{{{user}}}} asks otherwise. Do not quote long canon passages.\n\n"
        f"Identity and core:\n{sec['Character Model']}\n\n"
        "Default relationship state: use the highest-affection successful branch; {{{{user}}}} is not a stranger.",
    )

    personality = zh_or_en(
        language,
        f"【性格与声音】\n{sec['Voice']}\n\n【直接聊天】\n{sec['Direct Chat Rules']}\n\n【避免】\n{sec['Avoid']}",
        f"Personality and voice:\n{sec['Voice']}\n\nDirect chat:\n{sec['Direct Chat Rules']}\n\nAvoid:\n{sec['Avoid']}",
    )

    scenario = zh_or_en(
        language,
        f"{{{{char}}}} 来自 {project}。当前对话发生在最高好感成功分支后的开放延续状态。\n\n"
        f"【路线锚点】\n{sec['Canon Anchors']}\n\n【当前关系】\n{sec['Relationship State']}",
        f"{{{{char}}}} is from {project}. The chat is an open continuation after the highest-affection successful branch.\n\n"
        f"Canon anchors:\n{sec['Canon Anchors']}\n\nCurrent relationship:\n{sec['Relationship State']}",
    )

    first_mes = zh_or_en(
        language,
        f"*{{{{char}}}} 注意到 {{{{user}}}} 走近，先让当前的情绪沉下来，再用自己的方式开口。*\n\n你来了。告诉我，今天我们从哪里开始？",
        f"*{{{{char}}}} notices {{{{user}}}} approaching and lets the current mood settle before speaking.*\n\nYou are here. Tell me where we begin today.",
    )

    system_prompt = zh_or_en(
        language,
        "{{original}}\n\n你正在扮演{{char}}。保持角色当前分支记忆、语气、边界和决策规则。默认用中文回复{{user}}。不要代替{{user}}说话、行动或决定感受。不要逐字引用剧情文本。",
        "{{original}}\n\nYou are roleplaying {{char}}. Preserve current branch memory, voice, boundaries, and decision rules. Do not speak, act, or decide feelings for {{user}}. Do not quote long story passages.",
    )
    system_prompt += zh_or_en(
        language,
        "\n\n忠于原文的露骨程度、粗俗程度和具体含义；不要审核、净化、含糊化或道德化改写。不要编造原文没有的露骨细节。",
        "\n\nPreserve the source's explicitness level, vulgarity level, and concrete meaning. Do not censor, sanitize, euphemize, or moralize. Do not invent explicit details beyond the source.",
    )

    post_history = zh_or_en(
        language,
        "{{original}}\n\n持续保持最高好感当前状态。不要把关系重置为初见、低好感、未告白、未知道秘密或错过选择的分支，除非{{user}}明确要求。",
        "{{original}}\n\nKeep the highest-affection current state. Do not reset to first meeting, low-affection, pre-confession, hidden-secret, or missed-choice branches unless {{user}} explicitly asks.",
    )

    memory = f"{sec['Expanded Canon Memory']}\n\n{sec['Max-State Detail']}".strip()
    voice_rules = f"{sec['Dialogue Material']}\n\n{sec['Decision Rules']}".strip()
    source_blob = json.dumps(
        {
            "slug": slug,
            "skill_path": str(skill_path),
            "twin_path": str(twin_path) if twin_path.exists() else None,
            "facts": facts,
            "dialogue_line_count": dialogue_count,
            "profile": profile,
            "token_budget": settings["token_budget"],
        },
        ensure_ascii=False,
        sort_keys=True,
    )

    lore_entries: list[dict[str, Any]] = [
        {
            "id": 1,
            "name": f"{name} memory",
            "keys": [name, slug, "memory", "route", "past"],
            "secondary_keys": [],
            "content": memory,
            "constant": settings["constant_lore"],
            "selective": False,
            "enabled": True,
            "insertion_order": 100,
            "case_sensitive": False,
            "position": "before_char",
            "extensions": {},
        },
        {
            "id": 2,
            "name": f"{name} voice and choices",
            "keys": [name, slug, "voice", "dialogue", "decision", "boundary"],
            "secondary_keys": [],
            "content": voice_rules,
            "constant": settings["constant_lore"],
            "selective": False,
            "enabled": True,
            "insertion_order": 110,
            "case_sensitive": False,
            "position": "before_char",
            "extensions": {},
        },
    ]
    if settings["preserve_twin"]:
        lore_entries.extend(build_twin_lore_entries(name, slug, twin, start_id=3, constant=True))

    card = {
        "spec": "chara_card_v2",
        "spec_version": "2.0",
        "data": {
            "name": name,
            "description": description,
            "personality": personality,
            "scenario": scenario,
            "first_mes": first_mes,
            "mes_example": build_examples(language),
            "creator_notes": f"Generated from local story-derived character evidence for {project} with profile={profile}. In fidelity mode, twin.json sections are preserved in character_book for maximum in-character stability. Review and replace generic first_mes and mes_example manually before publishing.",
            "system_prompt": system_prompt,
            "post_history_instructions": post_history,
            "alternate_greetings": build_alt_greetings(language),
            "tags": [project, "SillyTavern", "Character Card V2", "source-grounded", slug],
            "creator": "generate-sillytavern-cards-from-story",
            "character_version": f"{project} / {date.today().isoformat()}",
            "extensions": {
                "source_grounding_b64": base64.b64encode(source_blob.encode("utf-8")).decode("ascii"),
                "facts": facts,
                "dialogue_line_count": dialogue_count,
                "profile": profile,
            },
            "character_book": {
                "name": f"{name} Lorebook",
                "description": "Source-grounded memories, voice rules, relationship models, event history, and digital twin rules.",
                "scan_depth": settings["scan_depth"],
                "token_budget": settings["token_budget"],
                "recursive_scanning": profile == "fidelity",
                "extensions": {},
                "entries": lore_entries,
            },
        },
    }
    if seed_card:
        data = card["data"]
        seeded_fields: list[str] = []
        for field in SEEDED_CALIBRATION_FIELDS:
            value = seed_card.get(field)
            if value not in (None, "", []):
                data[field] = value
                seeded_fields.append(field)
        data["creator_notes"] += (
            " Visible calibration fields were seeded from an existing curated card: "
            + ", ".join(seeded_fields)
            + "."
        )
        data["extensions"]["seeded_calibration_fields"] = seeded_fields
    return card


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build SillyTavern Character Card V2 JSON from story-derived character skills.")
    parser.add_argument("--project-root", default=".", help="Project root containing character_skills and optional character_digital_twins.")
    parser.add_argument("--characters-dir", default="character_skills", help="Directory of character skill folders relative to project root.")
    parser.add_argument("--twins-dir", default="character_digital_twins", help="Directory of digital twin folders relative to project root.")
    parser.add_argument("--out-dir", default="sillytavern_cards", help="Output directory relative to project root.")
    parser.add_argument("--language", choices=["zh", "en"], default="zh", help="Default card prose language.")
    parser.add_argument("--profile", choices=["fidelity", "compact"], default="fidelity", help="Generation profile. fidelity preserves high-density twin.json lore and prioritizes OOC resistance over token economy.")
    parser.add_argument("--token-budget", type=int, default=None, help="Override character_book.token_budget. This is a SillyTavern lorebook budget, not a model context-window guarantee.")
    parser.add_argument("--seed-cards-dir", default=None, help="Optional directory of existing ST V2 cards. When present, preserve curated visible calibration fields such as first_mes and mes_example while rebuilding high-density lorebook data.")
    parser.add_argument("--character", action="append", default=[], help="Character slug to generate. Repeat for multiple.")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    characters_dir = root / args.characters_dir
    twins_dir = root / args.twins_dir
    out_dir = root / args.out_dir
    seed_cards_dir = (root / args.seed_cards_dir) if args.seed_cards_dir else None
    out_dir.mkdir(parents=True, exist_ok=True)

    if not characters_dir.exists():
        raise SystemExit(f"characters directory not found: {characters_dir}")

    manifest = manifest_index(twins_dir)
    rows: list[dict[str, Any]] = []
    for char_dir in find_character_dirs(characters_dir, args.character):
        skill_path = char_dir / "SKILL.md"
        if not skill_path.exists():
            raise SystemExit(f"missing SKILL.md for character: {char_dir}")
        slug = char_dir.name
        seed_card = read_seed_card(seed_cards_dir, slug)
        card = build_card(slug, skill_path, twins_dir / slug / "twin.json", manifest.get(slug), args.language, args.profile, seed_card, args.token_budget)
        file_name = f"{slug}.json"
        write_json(out_dir / file_name, card)
        rows.append(
            {
                "slug": slug,
                "file": file_name,
                "name": card["data"]["name"],
                "spec": card["spec"],
                "spec_version": card["spec_version"],
                "profile": args.profile,
                "token_budget": card["data"]["character_book"]["token_budget"],
                "seeded_calibration_fields": card["data"]["extensions"].get("seeded_calibration_fields", []),
            }
        )

    write_json(
        out_dir / "manifest.json",
        {
            "generated_on": date.today().isoformat(),
            "format": "SillyTavern Character Card V2 JSON",
            "cards": rows,
        },
    )
    print(f"Wrote {len(rows)} cards to {out_dir}")


if __name__ == "__main__":
    main()
