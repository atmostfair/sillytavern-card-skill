---
name: generate-sillytavern-cards-from-story
description: Use when Codex needs to create SillyTavern Character Card V2 files from visual novel, Ren'Py, game story text, dialogue transcripts, extracted story folders, character dossiers, or source-grounded character evidence.
---

# Generate SillyTavern Cards From Story

## Overview

Create source-grounded SillyTavern Character Card V2 JSON from story text. Evidence comes first: build compact character facts, route state, voice rules, relationship memory, and boundaries before writing polished card prose.

Use this skill for reusable card generation, not for generic character brainstorming. The finished card should roleplay the character faithfully without copying long canon passages.

## Digital Twin First Standard

Fidelity over token economy. The default goal is not a small prompt or a convenient summary; the default goal is a high-density roleplay card that behaves like a source-grounded character digital twin.

OOC is a blocking failure. Do not deliver a card if the character's voice, values, memories, relationships, event history, current branch state, likes/dislikes, fears, boundaries, or decision rules are thin, generic, contradictory, or likely to drift out of character.

When enough source material exists, require a strict-deep model before final card delivery:

- Identity and aliases.
- Personality, core contradictions, emotional tells, stress responses, growth arc.
- Likes, dislikes, routines, hobbies, aesthetics, and recurring motifs.
- Life history and event timeline with state changes.
- Current route/relationship state, including inactive alternate branches.
- Relationships to the protagonist, family, friends, rivals, factions, and side characters.
- Speech model: rhythm, register, vocabulary, catchphrases, taboo phrasing, examples, and when not to overuse markers.
- Memory bank: key scenes, private memories, unresolved threads, promises, secrets, traumas, and late-branch anchors.
- Behavioral and decision rules for comfort, conflict, danger, intimacy, refusal, jealousy, grief, and public/private contexts.
- OOC guardrails and hard "do not write" rules.
- Evidence or source pointers for important claims.

Do not deliver a generic scaffold. If the bundled script produces generic `first_mes`, `mes_example`, sparse lorebook entries, or a card that only contains traits, treat it as an intermediate artifact and manually deepen it before final delivery.

## Input Decision

| Input available | Action |
| --- | --- |
| Raw `.rpy` / `.rpyc` / Ren'Py game build | Use `extract-renpy-story` first, then continue here. |
| Extracted story text only | Use `analyze-story-facts` to identify source units, speakers, facts, routes, and relationships. |
| Character dossiers / `character_skills/*/SKILL.md` | Convert directly with `scripts/build_sillytavern_cards.py`, then review manually. |
| `character_digital_twins/*/twin.json` plus evidence | Use the twins as source-of-truth and compress them into ST fields. |
| User names specific characters | Generate only those cards. Do not create a card for every named side character. |

## Target Coverage

Unless the user explicitly limits the roster, generate cards for:

- Every female character with substantial story volume.
- The protagonist / player-character ("me") even when the protagonist has no normal speaker dossier.

If the user explicitly asks for a narrow set, respect that scope and say the output is a partial roster run. Do not add the full cast unless the user asked for a complete roster.

Treat a female character as substantial when any of these are true: she has a project-local character dossier or digital twin, she is a romance/PAX/route/gallery character, she has recurring relationship scenes with the protagonist, she appears across multiple plot scenes, or the extracted story gives enough dialogue/events to model voice, memory, and relationships. Determine gender from source evidence such as character metadata, pronouns, titles, relationship labels, route labels, portraits, or user instruction; do not infer only from names. Mark uncertain candidates as `needs_review` instead of silently excluding them. Exclude one-off NPCs, cameo-only names, and characters with too little evidence to prevent OOC; record exclusions in the manifest or final report.

For the protagonist card, model the player-character's canon identity, relationships, route memories, decision style, and current-state assumptions. Do not confuse the protagonist card with the `{{user}}` macro in other character cards. If the protagonist is intentionally player-shaped with too little fixed personality, create a protagonist context/persona card that anchors known relationships and memories without inventing unsupported traits.

## Parallel Subagent Workflow

Use subagents for cast-wide generation when more than one target character qualifies and subagent tools are available. The purpose is speed and context isolation: each character's voice, memories, and relationship model should be built in a fresh context that is not polluted by another character's diction or emotional logic.

When using subagents:

- The coordinator first audits sources, builds the target roster, and prepares a small shared canon brief plus per-character evidence packs.
- Dispatch one subagent per target character when practical. If the cast is large, shard by character groups, but never put characters with easily confused voices in the same subagent.
- Give each subagent only the shared canon brief, target identity/aliases, inclusion reason, target source paths/fact IDs/twin/dossier, protagonist relationship default, language policy, ST V2 field requirements, target output path, and explicit avoid rules. Do not let subagents freely explore the whole project by default. Do not give them full cards for other characters except short relationship facts needed by the target.
- Assign disjoint write scopes such as `<out-dir>/<slug>.json` or ask subagents to return structured drafts for the coordinator to write. Do not let multiple subagents edit the same manifest, comparison report, or shared script.
- Require every subagent to return status (`DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, or `BLOCKED`), source coverage, uncertainty notes, and OOC risks for its character.
- The coordinator reviews every returned card for source grounding, ST V2 compatibility, cross-character consistency, and voice contamination before delivery.
- Borrow only the fresh-context, curated-input, status-handling, and review-loop ideas from subagent workflows. Do not import software-development mechanics such as TDD, branch policy, commits, or code-quality review into card generation tasks.

If subagent tools are unavailable, do not silently collapse into one long mixed-character generation pass. Process each target in isolated local passes, state that subagents were unavailable, and preserve the same per-character evidence-pack discipline.

For reusable subagent prompt templates and coordinator checklists, read `references/subagent-card-workflow.md` when generating more than one card.

## Card Workflow

1. Audit source files.
   - Find story order, speaker map, route variables, relationship screens, gallery/replay metadata, and existing character folders.
   - Prefer player-visible extracted text over raw code when both exist.
   - If adult route scenes exist, record consent, relationship state, boundaries, and consequences. Do not preserve explicit choreography unless the user explicitly requests mature route analysis.

2. Select target characters.
   - Use the user's requested characters when specified.
   - Otherwise apply Target Coverage: all substantial female characters plus the protagonist/player-character.
   - Keep minor characters inside lorebook/context entries unless the user asks for standalone cards.
   - Record candidate roster, included targets, excluded targets, `needs_review` targets, gender basis, story-volume basis, and reasons.

3. Build evidence before prose.
   - For each card, collect identity, role, route state, current relationship, voice markers, speech rhythm, memories, motivations, fears, refusal lines, decision rules, and "do not write" rules.
   - Separate confirmed facts from jokes, lies, dreams, virtual-only contexts, and choice-dependent branches.
   - Treat lower-affection branches as inactive unless the user requests a specific route stage.
   - If `character-digital-twin-builder` output exists, use `character_digital_twins/<slug>/twin.json` as the primary knowledge object. Treat project-local character `SKILL.md` files as loaders or summaries, not as the complete model.
   - If no strict-deep twin exists for a major character, build or deepen one first when the user asks for maximum fidelity.
   - For cast-wide work, build per-character evidence packs and send them to subagents instead of loading all characters into one drafting context.

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
   - High-fidelity cards should use large `character_book` entries liberally. Token budget is secondary to in-character stability.
   - If a prior curated ST card exists, seed visible calibration fields from it (`description`, `personality`, `scenario`, `first_mes`, `mes_example`, `system_prompt`, `post_history_instructions`, `alternate_greetings`) while rebuilding the high-density lorebook from current evidence. Do not throw away a better voice calibration just because the knowledge layer is being regenerated.

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
   - Run `scripts/validate_sillytavern_cards.py` for type-level SillyTavern V2 compatibility checks when a generated card directory exists.
   - Scan for placeholders: `TODO`, `TBD`, `PLACEHOLDER`, `undefined`, `null`.
   - Compare manifest coverage to the intended target characters, including every substantial female character and the protagonist unless the user narrowed scope.
   - Require manifest/report coverage fields for `candidate_roster`, `included`, `excluded`, `needs_review`, `gender_basis`, `story_volume_basis`, and `evidence_paths` on complete roster runs.
   - Check subagent status reports and resolve `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, or `BLOCKED` before delivery.
   - Fail the card if it lacks concrete relationship maps, key events, likes/dislikes, voice rules, or branch drift guards.
   - Fail the card if examples sound interchangeable with another character.
   - Fail the card if the first message could be used by a generic assistant or generic romance character.
   - Fail the set if multiple cards share the same voice template, catchphrases, emotional logic, or relationship assumptions without source evidence.

7. Iterate the skill before final response.
   - Update this skill after every task. Capture newly learned reusable experience, source-layout quirks, field-mapping improvements, validation failures, prompt-quality issues, or precautions discovered while using the skill.
   - Keep updates concise and reusable. Put durable workflow rules in `SKILL.md`, detailed SillyTavern format notes in `references/sillytavern-card-v2.md`, and deterministic fixes in `scripts/build_sillytavern_cards.py`.
   - Do not add one-off project facts, user-private story spoilers, generated card prose, or bulky logs to the skill. Add only knowledge that improves future card-generation tasks.
   - Re-run validation after any skill iteration.
   - Commit the skill iteration and push it to GitHub before claiming the task is complete.

## After Each Use

Every use of this skill must end with a short maintenance pass:

1. Review what happened during the task.
   - Did a source layout, transcript format, Ren'Py extraction artifact, character dossier shape, SillyTavern import behavior, or validation failure reveal something future runs should know?
   - Did the bundled script need a fix, option, or safer default?
   - Did manual review find a recurring card-quality issue such as generic openings, branch drift, missing lorebook keys, bad macro escaping, or overlong permanent prompts?

2. Update the skill when there is reusable learning.
   - Edit `SKILL.md`, `references/sillytavern-card-v2.md`, or `scripts/build_sillytavern_cards.py` as appropriate.
   - If there is no reusable learning, still record that decision in the final response after checking deliberately.

3. Validate the updated skill.
   - Run `quick_validate.py` on the skill folder.
   - Run any changed bundled script on a small representative input when practical.
   - Parse generated cards as JSON if script behavior changed.

4. Push the iteration.
   - Commit the skill update with a clear message.
   - Push the skill repository to GitHub after each iteration.
   - If there is no skill-file change after a deliberate maintenance pass, do not create an empty commit; report that there was no reusable update to push.
   - If `git push` fails because authentication, remote configuration, or network access is unavailable, report the exact failure and leave the local commit intact.

## Bundled Script

Use the script when a project already has structured character dossiers:

```powershell
python C:\Users\Quaternijkon\.codex\skills\generate-sillytavern-cards-from-story\scripts\build_sillytavern_cards.py `
  --project-root . `
  --characters-dir character_skills `
  --twins-dir character_digital_twins `
  --out-dir sillytavern_cards `
  --language zh `
  --profile fidelity `
  --seed-cards-dir sillytavern_cards
```

The script reads `character_skills/<slug>/SKILL.md`, optionally reads `character_digital_twins/build-manifest.json` and `twin.json`, and writes ST V2 JSON plus `manifest.json`. In `--profile fidelity` mode, it preserves high-density `twin.json` sections in the character book with a large token budget. With `--seed-cards-dir`, it preserves curated visible fields from an earlier good card while replacing the knowledge layer with the high-fidelity model. It is still a deterministic scaffold; inspect and manually rewrite first messages, examples, and any character-specific nuance before delivering.

Validate generated cards with:

```powershell
python C:\Users\Quaternijkon\.codex\skills\generate-sillytavern-cards-from-story\scripts\validate_sillytavern_cards.py `
  .\sillytavern_cards `
  --min-entries 1
```

For high-fidelity generated cards, prefer stricter checks:

```powershell
python C:\Users\Quaternijkon\.codex\skills\generate-sillytavern-cards-from-story\scripts\validate_sillytavern_cards.py `
  .\sillytavern_cards_fidelity `
  --min-entries 10 `
  --expect-profile fidelity `
  --expect-token-budget 20000
```

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
- It tells the model how the character speaks now, what they remember, what they like and dislike, what events shaped them, what they want, what they refuse, and how they choose under pressure.
- It includes enough relationship and event history that a downstream model can answer detailed questions about the character without inventing.
- It includes at least one opening message and example dialogue that sound like the character without quoting the source.
- It places long memories, world rules, relationship maps, event timelines, and behavioral rules in `character_book`; do not remove them merely to save tokens.
- It marks adult route material clinically as relationship state, consent, boundaries, and consequences.
- It passes an OOC review: the card should not plausibly speak like a different cast member under ordinary chat, romance, conflict, or mission prompts.

## Common Mistakes

- Writing card prose before extracting facts.
- Treating every dialogue line as confirmed truth.
- Flattening incompatible branches into one canon.
- Generating cards for every named character when the user asked for main characters.
- Copying long canon text into `mes_example`.
- Leaving a generic first message that ignores current relationship state.
- Letting `{{user}}` be a stranger when the card is meant for late-route chat.
- Making the card bilingual by accident. Choose a default language and state it.
