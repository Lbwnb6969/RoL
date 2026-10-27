# Relics of Legends (RoL)

A narrative relic-hunting mod for **Crusader Kings III** that adds handcrafted expedition chains, legendary rewards, custom event scenes, and a multi-chain grand reveal event.

> 中文名：**传奇圣遗物 / Relics of Legends**  
> 当前施工基线：**2026-10-27**，系统深化方案见 [施工队列](docs/rol_system_deepening_20261027.md)
> 当前 `descriptor.mod`：
> - `name = "Relics of Legends"`
> - `version = "1.00"`
> - `supported_version = "1.20.0.3"`
> - `remote_file_id = "3692558151"`

---

## Overview

RoL adds a set of scripted, story-driven relic expeditions across the Mediterranean and Europe.

Each major chain uses a unified activity framework:
- discovery event
- expedition activity
- staged narrative trials
- Tier-based final judgment
- success / failure summary

The design goal is to feel closer to vanilla CK3 event presentation while delivering more bespoke legendary-content flavor.

---

## Current Main Content

### Five formal expedition chains

| Region | Discovery | Activity | Final reward |
|---|---|---|---|
| Rome | `rol_relic_discovery.1000` | `activity_rol_seek_mars_blade` | **Blade of Mars** |
| Munich | `rol_relic_discovery.1300` | `activity_rol_seek_nibelung_sphere` | **Nibelung Star Sphere** |
| Naxos / Thera | `rol_relic_discovery.1400` | `activity_rol_seek_naxos_guard` | **Adeptus Custodes unlock** |
| Sevilla | `rol_relic_discovery.1500` | `activity_rol_seek_astrolabe_of_ocean` | **Astrolabe of Ocean** |
| Carthage / Qartajana | `rol_relic_discovery.1600` | `activity_rol_seek_ash_forged_mask` | **Ash-Forged Mask of Carthage** |

### Four-chain grand event

RoL also includes a special cross-chain culmination event:
- event: `rol_legend_circle.0001`
- trigger interface:
  - `rol_has_all_major_relic_completions_trigger`
  - `rol_check_legend_circle_revelation_effect`

Current rule:
- **Rome + Munich + Naxos + Sevilla** count toward the grand reveal
- **Carthage currently does not count toward it** by design

Completing Carthage as well unlocks the separate fivefold event `rol_legend_circle.0002`.

### Connected character and relic systems

Five expeditions now feed three expertise tracks, temporary study focuses and regional retry notes. Actual attending specialists offer help and earned routes; paying the original companion builds reputation and future candidate priority. Four relics and the Naxos tradition have ten mutually exclusive uses with delayed project outcomes. Sphere observations and astrolabe charts unlock optional routes; seven kinds of records and original companion agreements can pass to heirs without copying personal XP.

The October 27 expansion adds identity-bound rival reunions and house-owned knowledge collections. Catalogue seven kinds of existing notes/charts, then let members of the same house buy limited editions for future expeditions. Fragment challenge recovery now retains the original task identity. See [the current construction plan](docs/rol_system_deepening_20261027.md) and section 19 of [the game acceptance guide](docs/rol_console_test_guide.md).

The four development stages and the comprehensive static review are complete. Retired vanilla GUI/global artifact-label overrides are archived; quality and type labels now use the current game's UI, while the legendary badge appears on RoL's own tier modifier. Gameplay, delayed scopes, UI and other mod combinations still need the maintainer's game test. Existing usable art is retained. See [the completion audit](docs/rol_completion_audit_20261007.md), [balance model](docs/rol_success_model.md) and [console test guide](docs/rol_console_test_guide.md), especially sections 6 and 16.

---

## Core Design Rules

### 1. Tier4-only final claims
Main relic claims remain **Tier4-only**.

That means:
- simply avoiding failure is **not** enough
- high-success outcomes matter
- medium / tiny success results may keep the expedition alive, but do **not** guarantee the final claim

### 2. Vanilla-style option presentation
RoL uses a unified presentation baseline for expedition options:
- exact success / failure percentages
- outcome-based tooltip structure
- only one failure/cooldown line, shown at the bottom of the failure outcome
- every clickable option includes a short `flavor` line beneath the button

### 3. Unified preparation module
All main chains use the same expedition preparation option set:
- `rol_expedition_preparation_low`
- `rol_expedition_preparation_standard`
- `rol_expedition_preparation_high`
- `rol_expedition_preparation_supreme`

This affects:
- cost
- odds
- bonus prestige / dynasty prestige on success

---

## Notable Rewards

### Artifact rewards
- **Blade of Mars** — martial commander relic
- **Nibelung Star Sphere** — regalia-slot legendary sphere with governance / learning emphasis
- **Astrolabe of Ocean** — travel / stewardship-focused legendary accessory
- **Ash-Forged Mask of Carthage** — martial / dread / control-oriented legendary helmet

### Special non-artifact reward
- **Naxos / Thera chain** unlocks a special men-at-arms line instead of generating an artifact

---

## Installation

### For players
Use the Steam Workshop version of the mod if you only want to play it.

Workshop remote ID:
- `3692558151`

### For local manual installation
1. Place the mod folder where you manage your CK3 mods.
2. Ensure the launcher descriptor points to the correct folder.
3. Clear CK3 `gfx` cache after major visual updates:
   - `Documents\Paradox Interactive\Crusader Kings III\gfx`
4. Fully restart the launcher and the game.

---

## Repository Structure

```text
common/        Gameplay definitions: activities, artifacts, modifiers, scripted effects, triggers
events/        Expedition events, discovery events, grand reveal events
gfx/           Activity icons, artifact icons, event-scene illustrations
gui/           Activity progress widgets and text icon hookups
localization/  English + Simplified Chinese localization
docs/          Test guide, handoff notes, art prompt catalog, replacement guides
```

---

## Development Notes

This repository currently follows these working rules:
- **single true source only**
- no maintained Documents-side content mirror
- text files should be saved as **UTF-8 with BOM**
- custom scripted IDs should keep the `rol_` prefix

If you are continuing development, start with:
- `docs/rol_handoff_master.md`
- `docs/rol_console_test_guide.md`

### Static validation scripts used in this project

```powershell
python "C:\Users\Administrator\.codex\skills\rol-ck3-modder\scripts\check_bom_utf8.py" "C:\CK3Mods\RoL"
python "C:\Users\Administrator\.codex\skills\rol-ck3-modder\scripts\check_rol_prefix.py" "C:\CK3Mods\RoL"
python "C:\Users\Administrator\.codex\skills\rol-ck3-modder\scripts\rol_smoke_checks.py" "C:\CK3Mods\RoL"
```

---

## Debug / Testing

For in-game testing and console workflows, see:
- `docs/rol_console_test_guide.md`

That guide includes:
- discovery event calls
- per-chain test flows
- direct artifact grant effects
- failure / cooldown reset effects
- visual regression checks
- English UI regression checks

---

## Localization

RoL currently ships with:
- English
- Simplified Chinese

Localization policy:
- active display keys should remain complete in both languages
- dead / orphan keys should be removed instead of left behind as stale clutter

---

## Current Compatibility Snapshot

From `descriptor.mod`:
- supported CK3 version: **1.20.0.3** (CK3 1.20 “Crozier”, current 1.20.0.3 hotfix)

The five activities now explicitly declare their 1.20 `header_background` assets. This removes reliance on filename discovery for the activity header and keeps the existing travel/location backgrounds unchanged.

If CK3 updates and something breaks, first re-check:
- activity UI behavior
- event background references
- artifact slot presentation
- men-at-arms icon / artwork hookups
- tooltip formatting behavior for `random_list` outcomes

---

## Credits / Intent

RoL is built as a handcrafted legendary-expedition project focused on:
- relic atmosphere
- region-specific mythic identity
- stronger narrative payoff
- cleaner UI presentation
- moddable and reusable expedition templates for future content

---

## Internal Quick Links

- Master handoff: `docs/rol_handoff_master.md`
- Console test guide: `docs/rol_console_test_guide.md`
- Background prompt catalog: `docs/rol_background_prompt_catalog.md`
- Image resolution guide: `docs/rol_image_resolution_guide.md`
- Visual replacement guide: `docs/rol_visual_replacement_guide.md`
- 1.20 compatibility and expansion roadmap: `docs/rol_roadmap_1_20.md`
