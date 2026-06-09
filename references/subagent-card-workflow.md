# Subagent Card Workflow

Use this reference when generating more than one SillyTavern card from a story project.

## Coordinator Duties

The coordinator owns global consistency and final delivery. Do not delegate these decisions blindly.

1. Build a roster before drafting.
   - Include all substantial female characters.
   - Include the protagonist / player-character.
   - Record excluded candidates and the reason they are too minor or too thin.

2. Prepare shared context.
   - Project title/version.
   - Default route state and protagonist relationship assumptions.
   - Important global world rules.
   - Naming and language policy.
   - ST V2 schema requirements and output directory.

3. Prepare per-character evidence packs.
   - Target slug and display name.
   - Source paths and fact IDs.
   - Existing `character_skills/<slug>/SKILL.md`.
   - Existing `character_digital_twins/<slug>/twin.json`.
   - Prior seed card path for the same slug, if any.
   - Direct dialogue/actions involving the target.
   - Indirect mentions: narration, profiles, logs, route variables, memories, gallery/replay labels, and other characters' comments about the target.
   - Relationship facts involving other characters, summarized narrowly.
   - Known voice markers and OOC risks.

4. Dispatch subagents.
   - Prefer one target per subagent.
   - Use fresh context. In Codex multi-agent tools, prefer `fork_context: false` and pass explicit files/briefs.
   - Give each subagent a disjoint write path or ask for a structured draft only.
   - Do not let subagents edit shared manifests, scripts, or reports.
   - If the runtime exposes subagent tools but their tool policy requires explicit user authorization before spawning, do not spawn agents unless the user made that authorization. Record the constraint and run isolated local character passes instead.

5. Integrate.
   - Review every returned card before accepting it.
   - Resolve `NEEDS_CONTEXT`, `BLOCKED`, and `DONE_WITH_CONCERNS`.
   - Run JSON/ST V2 validation.
   - Check cross-card consistency and voice separation.
   - Write or update manifest/report after all card files are stable.

## Roster Rules

Default broad roster:

- Every female character with enough source evidence to model voice, memories, relationships, and behavior.
- The protagonist/player-character, even if the protagonist is represented by variables or player choices rather than normal dialogue.

Substantial evidence signals:

- Has a character dossier, digital twin, route, PAX, gallery, romance, or replay metadata.
- Appears across multiple plot scenes.
- Has recurring dialogue with the protagonist.
- Has relationship state changes, secrets, trauma, family/faction context, or route consequences.
- Has enough direct or indirect evidence to produce non-generic voice and decision rules.
- Is repeatedly discussed, remembered, feared, desired, blamed, protected, or judged by others even if direct appearances are limited.

Exclusion signals:

- One-scene cameo.
- Pure background NPC.
- Name appears only in exposition or UI labels.
- Not enough evidence to prevent generic behavior.

When story volume is uncertain, use the scoring rubric and record the decision. When gender is uncertain, put the candidate in `needs_review` unless the user resolves it. Include a borderline candidate only if the subagent can build concrete memories, relationships, and voice rules without inventing.

In Ren'Py projects, in-game character profile systems and gallery/replay lists are roster evidence. Treat records such as `Lady(...)`, `Girl(...)`, `LADIES_ORDER`, relationship/contact screens, persistent profile galleries, and replay scene titles as strong candidate signals, then confirm the candidate with dialogue volume, chapter coverage, labels, or relationship events. Use `coverage_class: secondary` for real profile/gallery characters whose evidence is narrower than the main cast.

### Roster Scoring Rubric

Use scoring to make the inclusion decision auditable. A candidate should usually receive a standalone card at 4+ points, or at 3 points when the user cares about complete heroine coverage.

| Signal | Points |
| --- | ---: |
| Independent route, romance, PAX, affection, gallery, replay, or ending state | 3 |
| Project-local character dossier or digital twin exists | 3 |
| Recurring direct dialogue with protagonist across multiple scenes | 2 |
| Recurring indirect mentions, reputation, memories, or accusations from multiple sources | 2 |
| Relationship state changes over time | 2 |
| Major world, faction, family, team, or main-plot influence | 2 |
| Distinct voice markers, catchphrases, register, or emotional pattern | 1 |
| Has secrets, trauma, unresolved promise, rivalry, or late-branch memory anchors | 1 |

Subtract or exclude when:

| Signal | Action |
| --- | --- |
| Only mentioned by name | Exclude |
| One-scene cameo with no durable relationship | Exclude |
| Mentioned often but only as a label with no behavior, relationship, or reputation detail | Usually exclude or lorebook-only |
| Alternate disguise/virtual identity of an included character | Merge unless user wants separate card |
| Gender cannot be established from evidence | Put in `needs_review` |
| Too little evidence to avoid generic behavior | Exclude with reason |

## Coverage Manifest Shape

For complete roster runs, include this information in the manifest or comparison report:

```json
{
  "run_scope": "complete_roster",
  "target_rule": "substantial female characters plus protagonist",
  "candidate_roster": [
    {
      "slug": "character-slug",
      "name": "Character Name",
      "decision": "included",
      "gender_basis": ["character metadata", "pronouns", "route label"],
      "story_volume_basis": ["digital twin exists", "recurring route scenes"],
      "evidence_paths": ["character_skills/character-slug/SKILL.md"],
      "reason": "Romance route character with enough dialogue and relationship state."
    }
  ],
  "included": ["character-slug"],
  "excluded": [
    {
      "slug": "minor-npc",
      "reason": "One-scene NPC; not enough evidence for non-generic voice."
    }
  ],
  "needs_review": [
    {
      "slug": "ambiguous-candidate",
      "reason": "Gender or story volume could not be established from available evidence."
    }
  ],
  "protagonist": {
    "included": true,
    "mode": "character_card",
    "reason": "Enough canon behavior and relationships exist to model the protagonist."
  }
}
```

If the user requested a partial roster, set `run_scope` to `partial_user_requested` and record the user's explicit target list.

## Subagent Prompt Template

Use this shape for each character-generation subagent. Fill in the bracketed fields before dispatch.

```text
You are generating exactly one SillyTavern Character Card V2 for [CHARACTER].

Goal:
- Build a source-grounded digital twin, not a generic roleplay persona.
- Preserve [CHARACTER]'s voice, memories, relationships, route state, likes/dislikes, boundaries, and decision rules.
- Avoid contamination from other characters' speech patterns or emotional logic.

Inputs:
- Shared canon brief:
[PASTE SHORT SHARED BRIEF]
- Target identity and aliases:
[PASTE TARGET NAME / ALIASES / GENDER BASIS]
- Inclusion reason:
[PASTE ROSTER DECISION REASON]
- Target evidence paths:
[LIST PATHS]
- Target fact IDs / source notes:
[LIST FACT IDS OR NOTES]
- Direct evidence:
[LIST DIALOGUE / ACTION / ON-SCREEN EVIDENCE]
- Indirect mention evidence:
[LIST NARRATION / PROFILE / LOG / MEMORY / GALLERY / THIRD-PARTY COMMENTS]
- Protagonist relationship default:
[PASTE CURRENT RELATIONSHIP STATE]
- Language policy:
[PASTE LANGUAGE REQUIREMENT]
- ST V2 field requirements:
[PASTE REQUIRED FIELD LIST OR REFERENCE]
- Prior seed card for this target, if available:
[PATH OR NONE]
- Output path:
[UNIQUE OUTPUT PATH OR "return draft only"]

Rules:
- Work only on [CHARACTER].
- Use other characters only as relationship context for [CHARACTER].
- Treat indirect mentions as first-class evidence. Record speaker/narrator, bias, reliability, implied fact, and whether the mention belongs to active canon, rumor, backstory, or branch-specific memory.
- Do not freely explore the whole project. Ask for specific missing target evidence with `NEEDS_CONTEXT`.
- Do not copy long canon passages, but do preserve the source's explicitness level and wording strength.
- Do not speak or act for {{user}}.
- Do not reset the route to first meeting unless the evidence says this card is for first meeting.
- If facts conflict, preserve branch distinctions instead of flattening them.
- For explicit source material, do not sanitize, euphemize, moralize, or clinically flatten. Preserve concrete acts, vulgarity, kink/fetish terms, shame, desire, coercive tension, consent or lack of consent, emotional state, boundaries, and consequences when they affect characterization or relationship memory. Do not invent beyond the source.

Required output:
- Status: DONE, DONE_WITH_CONCERNS, NEEDS_CONTEXT, or BLOCKED.
- The completed ST V2 JSON card or a structured card draft.
- Source coverage summary.
- Uncertainties or missing evidence.
- OOC risks and how the card prevents them.
- Any assumptions about active route/relationship state.
```

## Subagent Output Schema

Prefer this response shape when subagents return drafts instead of writing files:

```json
{
  "status": "DONE",
  "slug": "character-slug",
  "card": {
    "spec": "chara_card_v2",
    "spec_version": "2.0",
    "data": {}
  },
  "source_coverage": {
    "evidence_paths": [],
    "fact_ids": [],
    "direct_evidence_count": 0,
    "indirect_mention_count": 0,
    "missing_or_thin_areas": []
  },
  "indirect_mentions": [
    {
      "source": "",
      "speaker_or_narrator": "",
      "reliability": "confirmed|biased|rumor|joke|branch_specific",
      "implied_fact": "",
      "card_usage": ""
    }
  ],
  "assumptions": {
    "active_branch": "",
    "relationship_state": "",
    "language": "zh"
  },
  "ooc_risks": [
    {
      "risk": "",
      "mitigation": ""
    }
  ],
  "needs_coordinator_review": []
}
```

## Protagonist Prompt Additions

For the protagonist/player-character subagent, add:

```text
This target is the protagonist/player-character. Model the protagonist as {{char}} for this standalone card.

Do not confuse this card with the {{user}} macro used in other cards. Capture:
- Canon identity and aliases, including player-variable names when relevant.
- Default personality implied by choices, dialogue, narration, and relationship consequences.
- Relationship memories with every major character.
- Decision tendencies, moral limits, recurring jokes, fears, secrets, and growth arc.
- What the protagonist knows at the selected route state.
- How the protagonist should speak in direct chat without puppeting the real user.
```

If the source treats the protagonist as a flexible player projection, set the protagonist output mode to `protagonist_context_card` or `user_persona_anchor`. In that case, anchor known memories, relationships, route state, and decision constraints, but avoid inventing a fixed personality beyond source evidence.

## Review Checklist

The coordinator must reject or revise a returned card when:

- It omits a major relationship or route event.
- It ignores important indirect mentions, reputation, off-screen history, or third-party accounts that explain the target.
- It treats the protagonist as a stranger when the selected state is late-route.
- It copies another character's catchphrases or emotional posture.
- It collapses incompatible branches into one active canon without warning.
- It lacks voice examples that are specific to the target.
- It includes generic assistant behavior, therapy-bot phrasing, or encyclopedic narration where character voice is needed.
- It sanitizes explicit source facts into vague euphemisms or removes concrete details needed for voice, memory, preference, shame, trauma, intimacy, power dynamics, or OOC prevention.
- Its `character_book` entries have missing/empty keys or are not enabled.
- It changes shared world facts in a way that conflicts with other accepted cards.

## Cross-Card Review Prompt

Use a separate review subagent or local isolated pass after integrating all drafts:

```text
Review this completed SillyTavern card set for cross-character consistency and voice separation.

Inputs:
- Manifest with candidate roster and inclusion/exclusion reasons.
- Completed card files.
- Shared canon brief.

Check:
- The protagonist card exists unless this is an explicitly partial run.
- All qualifying female characters are included or have a concrete exclusion reason.
- Characters with low direct dialogue but high indirect evidence have been reviewed instead of silently dropped.
- Shared events, route state, names, aliases, and relationship stages agree across cards.
- Each card has distinct voice, emotional logic, boundaries, and example dialogue.
- No card copied another card's catchphrases or generic romance/assistant phrasing.
- Explicit source material remains unambiguous and source-faithful instead of being softened into generic intimacy summaries.
- Character book entries have usable keys, enabled entries, and source-grounded content.

Return:
- APPROVED or NEEDS_FIXES.
- Missing roster coverage.
- Cross-card contradictions.
- Voice contamination risks.
- Specific files/fields to revise.
```

## Suggested Parallel Pattern

For small casts, dispatch all eligible targets at once.

For large casts, dispatch waves:

1. Protagonist plus main route heroines.
2. Secondary recurring female characters.
3. Review/fix agents for cards that came back with concerns.

Keep each subagent's context fresh. If a subagent asks for more context, send only the missing target-specific evidence, not the entire mixed-character project context.
