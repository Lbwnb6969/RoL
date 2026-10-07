---
name: rol-ck3-modder
description: Develop and validate the CK3 Relics of Legend (RoL) mod at C:\CK3Mods\RoL. Use for activity/event chains, character traits, interacting relic systems, modifiers, artifact/UI assets, localization, MCP regression tools, and crash triage. Preserve the single source of truth and use static-first validation.
---

# RoL CK3 Modder

## Overview

Explain in Chinese; keep script IDs and file names in English. Read the repository's `PROJECT.md` and applicable `AGENTS.md` before changing behavior. `PROJECT.md` owns current goals, implemented features, decisions, and unresolved checks; this skill owns reusable engineering guidance.

Answer design questions with concrete proposals. A proposed trait, event, or mechanic is not an implemented feature or permission to build every suggested module. For implementation requests, complete the requested scope and its minimum meaningful validation.

## Hard Constraints

- Treat `C:\CK3Mods\RoL` as the only development source of truth.
- Do not maintain or rely on any Documents-side RoL content mirror.
- Treat `Documents\Paradox Interactive\Crusader Kings III\mod\RoL.mod` as a launcher descriptor only; when visual changes seem ignored, verify that its `path` still points to `C:\CK3Mods\RoL` before touching anything else.
- Save modified CK3 mod script/localization files as UTF-8 with BOM.
- Keep custom IDs under `rol_` conventions (`activity_rol_` and `phase_rol_` are accepted compatibility forms).
- Inspect the worktree and make a Git backup before substantial changes. Retire important files into `archive/` with Git history rather than deleting them.
- Search the repository, `docs`, `UsePlanguage.md`, installed game examples, and `D:\SteamLibrary\steamapps\workshop\content\1158310` (including RICE when present) before introducing uncertain syntax. Check that examples match the installed game version and scopes; use focused reads rather than scanning every workshop file. Respect attribution/licensing when reusing code or assets.
- When editing Chinese/non-ASCII text on Windows, avoid inline Python piped through PowerShell when the script body itself contains Chinese literals; prefer `apply_patch` for small edits, or BOM-safe shell/file writes, then reopen the file to confirm no `????` corruption occurred.

## Workflow

1. Inspect the requested feature and its connected state: discovery/activity, character, artifact, rival, and dynasty as relevant. Read only the supporting references needed below.
2. Trace the real display/behavior path before editing the wrong layer: localization/custom loc -> scripted effects/triggers -> GUI/assets.
3. For any GFX issue, confirm the actual loading path and the actual wired asset before editing: descriptor/mod path -> explicit script/gui refs -> implicit filename-convention refs -> cache/DDS spec.
4. Apply minimal, modular edits via scripted effects/triggers when possible.
5. For localization/doc repairs, scan for broken `????` text before editing and confirm the repaired file contents after writing.
6. Keep full quest flow: discovery -> activity -> stage checks -> full reward / partial success / failure -> summary. Keep durable completion separate from current artifact ownership.
7. Keep observability: toast title+desc, activity logs, debug traces.
8. Align random probabilities with tooltip text.
9. Prefer the repository's maintained checks and MCP tools under `tools/ck3_mcp`; bundled scripts are fallback only. See [the test playbook](references/rol-test-playbook.md). Run the smallest check that addresses the changed behavior; do not repeat checks without new evidence.
10. Do not sync or hotfix any Documents-side RoL copy; if needed, only confirm the launcher descriptor still targets `C:\CK3Mods\RoL`.

## Feature Design and Balance

- For traits, event consequences, buffs, companions, inheritance, and cross-chain interactions, read [system design guidance](references/rol-system-design.md).
- For activity and probability changes, read [the activity template](references/rol-activity-template.md) and repository `docs/rol_success_model.md`. The current high-stat standard-preparation target is roughly 70% full completion for the intended route, not 70% for every individual roll. Verify the actual path before multiplying probabilities.
- Centralize shared probability changes in script values. Exact outcome tooltips must use the same formula as the random list, including new modifiers and caps.
- Prefer additional choices, costs, and recovery paths over adding compulsory failure rolls. Preserve Tier4 unique rewards and Tier2/3 partial outcomes unless the user changes that design.

## Validation and Reporting

- Static-first is the project default. Read `PROJECT.md` and current user instructions before launching CK3, console actions, or window automation. While game testing is delegated to the user, do not start/restart/stop their game or send input; deliver console commands instead. Resume game automation only when the user changes that instruction.
- Static success proves the checked contracts; it does not prove scope behavior, visual layout, or real activity rewards. Report those limits explicitly.
- Summarize changed behavior, touched files, checks/results, and remaining uncertainty. Include console commands and expected outcomes when a game check is relevant; a documentation-only change does not need artificial game tests or a fixed report template.

## Images and Display

- Read [asset guidance](references/rol-localization-ui-assets.md) for image or localization changes. Existing usable legacy art stays; generate only missing, explicit placeholder, or scene-incompatible assets.
- Before image generation, read `C:\Users\Administrator\Desktop\mIDDLEFILE\image_generate.md`, the available imagegen skill, and the repository prompt catalog. Inspect the existing referenced art. Follow the user-selected API configuration; never put credentials in skill files, prompts, Git, or logs.
- Event/activity scene backgrounds normally contain environment and props; character portraits are supplied by event code and `window_characters`. Preserve regional and relic visual continuity.

## Crash and Invalid-ID Triage Order

1. Verify source-of-truth path (`C:\CK3Mods\RoL`).
2. Verify the active launcher descriptor path in `Documents\Paradox Interactive\Crusader Kings III\mod\RoL.mod`; if it points to `C:\CK3Mods\RoL`, always fix `C:\CK3Mods\RoL` itself rather than creating or editing a second content copy under Documents.
3. Inspect version and existing logs. Restart only if game testing is in scope; otherwise give the user the restart step.
4. Verify UTF-8 BOM on changed files.
5. Verify namespace, event IDs, on_actions, and load order.
6. Verify `scope:activity` context assumptions.
7. Verify localization keys and encoding.
8. If text appears as `????`, verify file contents/bytes rather than trusting terminal rendering alone.
9. Re-check actual asset references, texture paths, filename conventions, and DDS specs before suspecting cache. If cache retirement is needed, move it to a dated backup during an authorized, closed-game session; do not delete it or modify a live session by default.

## High-Value RoL Heuristics

- Artifact card text, rarity labels, or color issues usually live in localization/custom loc first; inspect `common/customizable_localization` before editing `.gui`.
- Event/activity black backgrounds usually fail in this order: wrong background reference, wrong texture path, bad DDS format/size, stale gfx cache.
- A replaced image that "reverted" often means one of three things: the active descriptor is no longer pointing at `C:\CK3Mods\RoL`, the file exists but is not actually wired, or CK3 is still reading stale gfx cache.
- For activity UI art, remember many assets are wired implicitly by exact filename/activity-id convention rather than explicit script references; verify naming before touching GUI.
- New event/activity backgrounds target `1592x848` DDS (`DXT1/BC1`, no alpha unless needed); activity header backgrounds are `1100x440`. Icon dimensions vary by family; see asset guidance and actual wired examples rather than applying a background rule to icons.
- When repairing large Chinese localization/doc files, treat encoding safety as part of the fix: write with BOM, reopen with `utf-8-sig`, and re-scan for `????`.

## Supporting Resources

- [Standards](references/rol-standards.md): source, encoding, IDs, backup and state ownership.
- [Activity template](references/rol-activity-template.md): preparation, outcomes, probability and cross-chain completion.
- [System design](references/rol-system-design.md): interacting traits, events, modifiers and persistent consequences.
- [Localization and assets](references/rol-localization-ui-assets.md): bilingual keys, display path and retained art.
- [Test playbook](references/rol-test-playbook.md): static/MCP checks and user-run console validation.
- `scripts/check_bom_utf8.py`, `scripts/check_rol_prefix.py`, `scripts/rol_smoke_checks.py`: fallback checks when repository equivalents are unavailable.
