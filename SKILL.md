---
name: generate-sillytavern-cards-from-story
description: Use when Codex needs to create SillyTavern Character Card V2 files from visual novel, Ren'Py, game story text, dialogue transcripts, extracted story folders, character dossiers, or source-grounded character evidence.
---

# Generate SillyTavern Cards From Story

## Overview

Create source-grounded SillyTavern Character Card V2 JSON from story text. Evidence comes first: build compact character facts, route state, voice rules, relationship memory, and boundaries before writing polished card prose.

Use this skill for reusable card generation, not for generic character brainstorming. The finished card should roleplay the character faithfully without copying long canon passages.

## Input Decision

| Input available | Action |
| --- | --- |
| Raw `.rpy` / `.rpyc` / Ren'Py game build | Use `extract-renpy-story` first, then continue here. |
| Extracted story text only | Use `analyze-story-facts` to identify source units, speakers, facts, routes, and relationships. |
| Character dossiers / `character_skills/*/SKILL.md` | Convert directly with `scripts/build_sillytavern_cards.py`, then review manually. |
| `character_digital_twins/*/twin.json` plus evidence | Use the twins as source-of-truth and compress them into ST fields. |
| User names specific characters | Generate only those cards. Do not create a card for every named side character. |

## Card Workflow

1. Audit source files.
   - Find story order, speaker map, route variables, relationship screens, gallery/replay metadata, and existing character folders.
   - Prefer player-visible extracted text over raw code when both exist.
   - If adult route scenes exist, record consent, relationship state, boundaries, and consequences. Do not preserve explicit choreography unless the user explicitly requests mature route analysis.

2. Select target characters.
   - Use the user's requested characters when specified.
   - Otherwise choose main route, PAX, romance, party, or recurring high-dialogue characters.
   - Keep minor characters inside lorebook/context entries unless the user asks for standalone cards.

3. Build evidence before prose.
   - For each card, collect identity, role, route state, current relationship, voice markers, speech rhythm, memories, motivations, fears, refusal lines, decision rules, and "do not write" rules.
   - Separate confirmed facts from jokes, lies, dreams, virtual-only contexts, and choice-dependent branches.
   - Treat lower-affection branches as inactive unless the user requests a specific route stage.

4. Map evidence to SillyTavern fields.
   - `description`: source-grounded identity, relationship default, and current branch.
   - `personality`: traits, psychology, voice, direct-chat rules, and avoid rules.
   - `scenario`: world context, relationship state, route anchors, and default user role.
   - `first_mes`: one strong in-character opening based on current state.
   - `mes_example`: 2-5 short example exchanges that demonstrate voice without quoting canon.
   - `system_prompt`: roleplay contract, language policy, no user puppeting, no route reset.
   - `post_history_instructions`: branch drift guard and memory continuity.
   - `alternate_greetings`: 2-4 scene starters from different emotional registers.
   - `character_book`: longer memories, world rules, relationship edges, and decision rules.
   - `extensions`: source metadata such as story version, fact counts, evidence paths, and generation notes.

5. Write compactly.
   - Use the user's language for card prose unless requested otherwise.
   - Preserve original names and important proper nouns.
   - Avoid huge permanent prompts. Put long route memories and worldbuilding in `character_book`.
   - Do not copy long source passages. Paraphrase behavior patterns and cite source paths in metadata when useful.

6. Validate before completion.
   - Parse every output file as JSON.
   - Check `spec == "chara_card_v2"` and `spec_version == "2.0"`.
   - Check non-empty `name`, `description`, `personality`, `scenario`, `first_mes`, and `mes_example`.
   - Check lorebook entries are enabled and have keys.
   - Scan for placeholders: `TODO`, `TBD`, `PLACEHOLDER`, `undefined`, `null`.
   - Compare manifest coverage to the intended target characters.

## Bundled Script

Use the script when a project already has structured character dossiers:

```powershell
python C:\Users\Quaternijkon\.codex\skills\generate-sillytavern-cards-from-story\scripts\build_sillytavern_cards.py `
  --project-root . `
  --characters-dir character_skills `
  --twins-dir character_digital_twins `
  --out-dir sillytavern_cards `
  --language zh
```

The script reads `character_skills/<slug>/SKILL.md`, optionally reads `character_digital_twins/build-manifest.json` and `twin.json`, and writes ST V2 JSON plus `manifest.json`. It is a deterministic scaffold; still inspect first messages, examples, and any character-specific nuance before delivering.

Use `--character slug` repeatedly to restrict output:

```powershell
python C:\Users\Quaternijkon\.codex\skills\generate-sillytavern-cards-from-story\scripts\build_sillytavern_cards.py `
  --project-root . --character luna --character nova
```

For detailed V2 field mapping and review rules, read `references/sillytavern-card-v2.md`.

## Quality Bar

A card is acceptable only when:

- It can be imported as SillyTavern Character Card V2 JSON.
- It preserves the active branch and does not reset the relationship to first meeting.
- It tells the model how the character speaks now, what they remember, what they want, what they refuse, and how they choose under pressure.
- It includes at least one opening message and example dialogue that sound like the character without quoting the source.
- It places long memories and world rules in `character_book` instead of overloading permanent fields.
- It marks adult route material clinically as relationship state, consent, boundaries, and consequences.

## Common Mistakes

- Writing card prose before extracting facts.
- Treating every dialogue line as confirmed truth.
- Flattening incompatible branches into one canon.
- Generating cards for every named character when the user asked for main characters.
- Copying long canon text into `mes_example`.
- Leaving a generic first message that ignores current relationship state.
- Letting `{{user}}` be a stranger when the card is meant for late-route chat.
- Making the card bilingual by accident. Choose a default language and state it.
