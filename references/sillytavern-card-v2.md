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

## High-Fidelity Profile

For digital-twin cards, token budget is secondary. Prefer a larger, more reliable card over a compact card that drifts OOC. Use `character_book.token_budget` in the 8000-20000 range when the target model and SillyTavern setup can tolerate it.

High-fidelity cards should include:

- Full identity and alias logic.
- Core contradictions and personality model.
- Likes, dislikes, routines, hobbies, motifs, and comfort objects.
- Event timeline and memory bank, including state changes.
- Relationship maps for protagonist, family, friends, rivals, factions, and recurring side characters.
- Current branch state plus inactive alternate branch warnings.
- Voice model with rhythm, register, vocabulary, taboo phrasing, and overuse warnings.
- Scene-generation rules for daily life, romance, conflict, danger, grief, intimacy, public scenes, and private scenes.
- Behavioral decision rules and refusal rules.
- Hard OOC guardrails.
- Source metadata or fact IDs for important claims.

If `character_digital_twins/<slug>/twin.json` exists, preserve the high-value nested sections in `character_book` instead of flattening them away. Important sections usually include `identity`, `personality`, `voice`, `likes_dislikes`, `life_history`, `psychological_model`, `social_model`, `relationship_models`, `memory_bank`, `boundaries`, `behavioral_rules`, `decision_rules`, `scene_generation_model`, `chat_model`, and `validation`.

When an earlier ST card has stronger manually curated visible calibration, keep those visible fields and regenerate the knowledge layer. Good seed fields are `description`, `personality`, `scenario`, `first_mes`, `mes_example`, `system_prompt`, `post_history_instructions`, and `alternate_greetings`. This is especially useful when a deterministic script can preserve facts but cannot yet write character-specific openings as well as a manual pass.

## OOC Failure Gates

Reject or revise a card before delivery when:

- The first message could fit many unrelated characters.
- Example dialogue lacks the character's concrete rhythm, vocabulary, boundaries, or relationship state.
- The card does not explain who the character likes, fears, trusts, protects, resents, or refuses.
- The card lacks key events and how those events changed the character.
- Current route state is ambiguous or reset to first meeting.
- Public/private behavior, family/friend relationships, or romance boundaries are missing.
- Catchphrases appear without rules for when not to use them.
- The card compresses away evidence needed to prevent OOC because of token concerns.
- The card sanitizes, euphemizes, or clinically flattens explicit source wording that is needed for unambiguous characterization.

## Writing Rules

- Use `{{char}}` and `{{user}}` macros where helpful.
- In Python f-strings, write doubled SillyTavern macros as `{{{{user}}}}` and `{{{{char}}}}`. Scan the whole generated card, including `system_prompt`, `post_history_instructions`, lorebook JSON blobs, and metadata, for bare `{user}` or `{char}`. Fix the generator and regenerate outputs when a collapse is found.
- Do not speak or act for `{{user}}`.
- Keep examples focused; demonstrate rhythm, relationship state, boundaries, and memory under different emotional conditions.
- For roster-scale generated cards, do not reuse the same example scaffold unchanged across characters. Prefer replay/menu-specific memory anchors first, de-duplicate repeated one-story anchors, and convert third-person profile blurbs into natural first-person lines before placing them in `mes_example`.
- Prefer 4-8 examples for high-fidelity cards. Each should start with `<START>`.
- Put high-token worldbuilding in `character_book`, not permanent fields, but do not delete it to save tokens when fidelity matters.
- If the user wants Chinese cards, write card prose in Chinese while keeping proper nouns unchanged.
- Preserve explicit source material faithfully. Keep the original meaning, intensity, concrete acts, vulgarity, kink/fetish terms, shame, desire, coercive tension, consent or lack of consent, boundaries, emotional state, and consequences when they affect characterization or relationship memory.
- Do not sanitize explicit wording into vague phrases such as "they were intimate" when the source is more specific. Use short exact source phrases only when necessary for voice or unambiguous meaning; otherwise paraphrase without weakening explicitness.
- Do not invent new explicit details or intensify beyond the source. Source fidelity is the standard.

## Validation Snippet

Prefer the bundled validator for generated card directories:

```powershell
python C:\Users\Quaternijkon\.codex\skills\generate-sillytavern-cards-from-story\scripts\validate_sillytavern_cards.py `
  .\sillytavern_cards_fidelity `
  --min-entries 10 `
  --expect-profile fidelity `
  --expect-token-budget 20000
```

Use an inline snippet only when the bundled validator is not available:

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

## Metadata Hygiene

Generated cards, manifests, and curated evidence packs should avoid JSON `null` for unknown optional metadata. Omit the field or use a clear string such as `unknown_from_source`; broad placeholder scans often include `null`, and a single unknown age or unset field can otherwise make an import-ready package look unfinished. Keep raw transcript caches separate from curated deliverables when scanning for placeholders.
