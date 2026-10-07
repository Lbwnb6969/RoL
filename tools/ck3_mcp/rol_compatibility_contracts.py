"""Check additive loading, owned IDs/references and asset wiring without CK3."""
from pathlib import Path
import os
import re

if __package__:
    from .rol_growth_contracts import parse, get
else:
    from rol_growth_contracts import parse, get

LOC = re.compile(r'^\s+([\w.-]+):(?:\d+)?\s*"', re.M)
OWNED_LOC = ("rol_", "ROL_", "artifact_rol_", "activity_rol_", "phase_rol_",
             "trait_rol_", "trait_track_rol_", "TRAVEL_NAME_FOR_activity_rol_")
HOOKS = {"yearly_playable_pulse", "on_title_gain", "on_artifact_changed_owner", "on_death"}


def walk(nodes):
    for key, operator, value in nodes:
        yield key, operator, value
        if isinstance(value, list):
            yield from walk(value)


def check_compatibility_contract(root: Path, errors: list[str]) -> tuple[int, int]:
    game = Path(os.environ.get("CK3_GAME_ROOT", r"D:\SteamLibrary\steamapps\common\Crusader Kings III")) / "game"
    symbols, events, scripts = {}, set(), []
    checked, references = 0, 0
    for directory in ("common", "events", "gui", "gfx", "localization"):
        for path in sorted((root / directory).rglob("*")):
            if not path.is_file(): continue
            relative = path.relative_to(root)
            if directory in {"common", "events", "gui", "localization"} and not path.name.startswith("rol_"):
                errors.append(f"compatibility: unowned loading filename {relative}")
            if game.exists() and (game / relative).is_file():
                errors.append(f"compatibility: active vanilla file replacement {relative}; archive or explicitly redesign it")
            if path.suffix.lower() not in {".txt", ".gui", ".gfx", ".asset", ".yml"}: continue
            try:
                text = path.read_text(encoding="utf-8-sig")
                if "\ufffd" in text or "????" in text:
                    errors.append(f"encoding: corrupted text in {relative}")
                checked += 1
                if directory == "localization":
                    for key in LOC.findall(text):
                        if not key.startswith(OWNED_LOC):
                            errors.append(f"compatibility: global localization key {key} in {relative}")
                elif directory in {"common", "events"}:
                    nodes = parse(text)
                    scripts.append((relative, nodes))
                    registry = "events" if directory == "events" else str(relative.parent)
                    for key, _, value in nodes:
                        if key == "namespace":
                            if not value.startswith("rol_"): errors.append(f"compatibility: unowned namespace {value}")
                            continue
                        if key in HOOKS and "on_action" in path.parts:
                            if {k for k, _, _ in value} != {"on_actions"}:
                                errors.append(f"compatibility: vanilla hook {key} replaces native logic in {relative}")
                            for action, _, _ in get(value, "on_actions"):
                                if not action.startswith("rol_"): errors.append(f"compatibility: unowned callback {action}")
                            continue
                        if not key.startswith(("rol_", "activity_rol_", "Rol", "@rol_")):
                            errors.append(f"compatibility: unowned registry ID {key} in {relative}")
                        identity = (registry, key)
                        if identity in symbols: errors.append(f"registry: duplicate {key} in {relative} and {symbols[identity]}")
                        symbols[identity] = relative
                        if directory == "events": events.add(key)
                for ref in re.findall(r'"(gfx/[^"\n]+)"', text):
                    if "rol_" in ref.lower():
                        references += 1
                        if not (root / ref).is_file(): errors.append(f"resource: missing {ref} in {relative}")
            except (UnicodeError, ValueError, OSError, IndexError) as error:
                errors.append(f"syntax/encoding: {relative}: {error}")
    owned_symbols = {key for _, key in symbols}
    for relative, nodes in scripts:
        for key, _, value in walk(nodes):
            for token in [key] + ([value] if isinstance(value, str) else []):
                if token.startswith("rol_") and token.endswith(("_effect", "_trigger", "_value")) and "$" not in token and token not in owned_symbols:
                    errors.append(f"reference: undefined {token} in {relative}")
            if key == "trigger_event":
                event = get(value, "id") if isinstance(value, list) else value
                if event.startswith("rol_") and event not in events: errors.append(f"reference: undefined event {event} in {relative}")
            if key == "on_actions" and isinstance(value, list):
                for action, _, _ in value:
                    if action.startswith("rol_") and action not in owned_symbols: errors.append(f"reference: undefined callback {action}")
            if key == "reference" and isinstance(value, str) and value.startswith("rol_") and value not in owned_symbols:
                errors.append(f"resource: undefined background {value} in {relative}")
            if key == "icon" and isinstance(value, str) and value.strip('"').startswith("rol_"):
                filename = value.strip('"')
                if not filename.endswith(".dds"): filename += ".dds"
                family = "artifact" if "artifacts" in relative.parts else "regimenttypes" if "men_at_arms_types" in relative.parts else None
                if family and not (root / "gfx/interface/icons" / family / filename).is_file():
                    errors.append(f"resource: missing implicit {family} icon {filename} in {relative}")
    if re.search(r"(?m)^\s*replace_path\s*=", (root / "descriptor.mod").read_text(encoding="utf-8-sig")):
        errors.append("compatibility: descriptor replace_path masks vanilla/other mods")
    return checked, references


if __name__ == "__main__":
    import sys
    issues = []
    count, refs = check_compatibility_contract(Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2], issues)
    for issue in issues: print(f"[FAIL] {issue}")
    if not issues: print(f"[OK] Compatibility: {count} text files; additive hooks, owned IDs/localization, resolved script/event/background/icon references; {refs} owned assets")
    raise SystemExit(bool(issues))
