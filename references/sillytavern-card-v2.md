# SillyTavern Card V2 Mapping

## Required Shape

Use JSON:

```json
{
  "spec": "chara_card_v2",
  "spec_version": "2.0",
  "data": {
    "name": "Character",
    "description": "...",
    "personality": "...",
    "scenario": "...",
    "first_mes": "...",
    "mes_example": "..."
  }
}
```

Recommended optional fields: `creator_notes`, `system_prompt`, `post_history_instructions`, `alternate_greetings`, `tags`, `creator`, `character_version`, `extensions`, and `character_book`.

## Practical Mapping

| Story model item | ST field |
| --- | --- |
| Identity, role, core contradiction | `description` |
| Personality, psychology, speech rules | `personality` |
| World, route, default user role | `scenario` |
| Best current-state scene starter | `first_mes` |
| Voice calibration exchanges | `mes_example` |
| Branch rules and no-puppeting contract | `system_prompt` |
| Route drift guard | `post_history_instructions` |
| Long memories, world rules, route details | `character_book.entries` |

## Writing Rules

- Use `{{char}}` and `{{user}}` macros where helpful.
- Do not speak or act for `{{user}}`.
- Keep examples short; demonstrate rhythm, not plot summary.
- Prefer 2-5 examples. Each should start with `<START>`.
- Put high-token worldbuilding in `character_book`, not permanent fields.
- If the user wants Chinese cards, write card prose in Chinese while keeping proper nouns unchanged.
- For explicit source material, compress into consent, boundaries, emotional state, and consequences.

## Validation Snippet

```powershell
@'
import json
from pathlib import Path
for path in Path("sillytavern_cards").glob("*.json"):
    data = json.loads(path.read_text(encoding="utf-8"))
    if path.name == "manifest.json":
        continue
    assert data["spec"] == "chara_card_v2", path
    assert data["spec_version"] == "2.0", path
    card = data["data"]
    for key in ["name", "description", "personality", "scenario", "first_mes", "mes_example"]:
        assert card.get(key, "").strip(), (path, key)
    assert "<START>" in card["mes_example"], path
print("cards passed")
'@ | python -
```

