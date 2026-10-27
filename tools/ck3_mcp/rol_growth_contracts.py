#!/usr/bin/env python3
"""Source-driven checks for the expedition growth loop.

The small evaluator covers only the effects/triggers/values used by this module.
It checks state ordering and probability arithmetic, not Clausewitz runtime or UI.
Unsupported instructions fail instead of silently passing as game verification.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


TOKEN = re.compile(r'#[^\n]*|"(?:\\.|[^"\\])*"|\?=|!=|>=|<=|[{}=<>]|[^\s{}=<>!?#]+')


def parse(text: str) -> list:
    tokens = [t for t in TOKEN.findall(text.lstrip("\ufeff")) if not t.startswith("#")]
    index = 0

    def sequence(nested: bool = False) -> list:
        nonlocal index
        result = []
        while index < len(tokens):
            key = tokens[index]
            index += 1
            if key == "}":
                if not nested:
                    raise ValueError("unexpected closing brace")
                return result
            if index == len(tokens) or tokens[index] not in ("=", "?=", "!=", ">=", "<=", ">", "<"):
                result.append((key, "", ""))  # CK3 scalar lists, e.g. intents
                continue
            operator = tokens[index]
            index += 1
            value = tokens[index]
            index += 1
            if value == "{":
                value = sequence(True)
            elif value == "}":
                raise ValueError("missing assignment value")
            result.append((key, operator, value))
        if nested:
            raise ValueError("unclosed block")
        return result

    return sequence()


def get(nodes: list, key: str):
    values = [value for name, _, value in nodes if name == key]
    if len(values) != 1:
        raise ValueError(f"expected one {key}, found {len(values)}")
    return values[0]


def expand(nodes: list, parameters: dict) -> list:
    def scalar(value: str) -> str:
        for key, replacement in parameters.items():
            value = value.replace(f"${key}$", str(replacement))
        return value
    return [(scalar(k), op, expand(v, parameters) if isinstance(v, list) else scalar(v)) for k, op, v in nodes]


@dataclass(eq=False)
class State:
    variables: dict = field(default_factory=dict)
    flags: set = field(default_factory=set)
    modifiers: dict = field(default_factory=dict)
    traits: set = field(default_factory=set)
    xp: dict = field(default_factory=dict)
    events: list = field(default_factory=list)
    stress: float = 20
    activity: dict | None = field(default_factory=dict)
    preparation: str = "standard"
    gold: float = 200
    prestige: float = 200
    learning: float = 15
    martial: float = 15
    prowess: float = 15
    diplomacy: float = 15
    stewardship: float = 15
    intrigue: float = 15
    alive: bool = True
    adult: bool = True
    available: bool = True
    imprisoned: bool = False
    scopes: dict = field(default_factory=dict)
    attendees: list = field(default_factory=list)
    opinions: list = field(default_factory=list)
    # Native relationship totals are supplied snapshots, not inferred from modifiers.
    opinion_values: dict = field(default_factory=dict)
    court_owner: State | None = None
    progress_effects: list = field(default_factory=list)
    artifact_type: str = ""
    owner: State | None = None
    artifacts: list = field(default_factory=list)
    flag_durations: dict = field(default_factory=dict)
    player_heir: State | None = None
    ai: bool = False
    lists: dict = field(default_factory=dict)
    event_contexts: list = field(default_factory=list)
    learning_lifestyle_xp: float = 0
    piety: float = 0
    house: State | None = None
    dynasty: State | None = None
    playable: bool = True
    incapable: bool = False


class Model:
    def __init__(self, root: Path):
        self.effects = dict((k, v) for k, _, v in parse((root / "common/scripted_effects/rol_expedition_growth_effects.txt").read_text(encoding="utf-8-sig")))
        companion_effects = root / "common/scripted_effects/rol_expedition_companion_effects.txt"
        if companion_effects.exists():
            self.effects.update({k: v for k, _, v in parse(companion_effects.read_text(encoding="utf-8-sig"))})
            rival = parse((root / "common/scripted_effects/rol_rival_effects.txt").read_text(encoding="utf-8-sig"))
            self.effects["rol_clear_rival_route_effect"] = get(rival, "rol_clear_rival_route_effect")
        relic_effects = root / "common/scripted_effects/rol_relic_use_effects.txt"
        if relic_effects.exists():
            self.effects.update({k: v for k, _, v in parse(relic_effects.read_text(encoding="utf-8-sig"))})
        self.triggers = {}
        self.values = {}
        for name, directory, files in (
            (self.triggers, "scripted_triggers", ("rol_expedition_growth_triggers.txt", "rol_expedition_preparation_triggers.txt", "rol_expedition_companion_triggers.txt")),
            (self.values, "script_values", ("rol_expedition_growth_values.txt", "rol_expedition_preparation_values.txt", "rol_expedition_companion_values.txt")),
        ):
            for filename in files:
                nodes = parse((root / "common" / directory / filename).read_text(encoding="utf-8-sig"))
                name.update({k: v for k, _, v in nodes})
        relic_triggers = root / "common/scripted_triggers/rol_relic_use_triggers.txt"
        if relic_triggers.exists():
            self.triggers.update({k: v for k, _, v in parse(relic_triggers.read_text(encoding="utf-8-sig"))})
        for directory, container, filename in (
            ("scripted_triggers", self.triggers, "rol_quest_lifecycle_triggers.txt"),
            ("scripted_triggers", self.triggers, "rol_rival_lifecycle_triggers.txt"),
            ("scripted_effects", self.effects, "rol_quest_lifecycle_effects.txt"),
            ("scripted_effects", self.effects, "rol_rival_lifecycle_effects.txt"),
            ("scripted_effects", self.effects, "rol_archive_effects.txt"), ("scripted_triggers", self.triggers, "rol_archive_triggers.txt"),
            ("scripted_effects", self.effects, "rol_relic_fragment_effects.txt"), ("scripted_triggers", self.triggers, "rol_fragment_triggers.txt"),
            ("scripted_effects", self.effects, "rol_relic_legacy_effects.txt"), ("scripted_triggers", self.triggers, "rol_relic_legacy_triggers.txt"),
            ("scripted_effects", self.effects, "rol_legacy_attitude_effects.txt"),
            ("scripted_effects", self.effects, "rol_expedition_feedback_effects.txt"),
        ):
            path = root / "common" / directory / filename
            if path.exists(): container.update({k: v for k, _, v in parse(path.read_text(encoding="utf-8-sig"))})

    def current(self, state: State, scope):
        return state if scope == "actor" else state.activity if scope == "activity" else scope

    def variables(self, state: State, scope) -> dict:
        current = self.current(state, scope)
        return current.variables if isinstance(current, State) else (current if current is not None else {})

    def reference(self, value: str, state: State, scope="actor"):
        if ".var:" in value:
            prefix, name = value.split(".var:", 1)
            base = self.reference(prefix, state, scope)
            return (base.variables if isinstance(base, State) else (base or {})).get(name)
        if value == "root": return state
        if value == "this": return self.current(state, scope)
        if value in ("player_heir", "house", "dynasty", "court_owner"):
            return getattr(self.current(state, scope), value)
        if value == "involved_activity": return self.current(state, scope).activity
        if value == "scope:activity": return state.activity
        if value.startswith("scope:"): return state.scopes.get(value[6:])
        if value.startswith("var:"): return self.variables(state, scope).get(value[4:])
        raise ValueError(f"unsupported reference {value}")

    def number(self, value: str, state: State, scope="actor"):
        if value in ("root", "this", "player_heir", "house", "dynasty", "court_owner"):
            return self.reference(value, state, scope)
        if value.startswith(("scope:", "var:", "root.var:")):
            resolved = self.reference(value, state, scope)
            if resolved is None: raise ValueError(f"missing value {value}")
            return resolved
        if value in ("learning", "martial", "prowess", "diplomacy", "stewardship", "intrigue", "gold", "prestige", "piety"):
            return getattr(self.current(state, scope), value)
        if value in self.values:
            return self.calculate(self.values[value], state, scope)
        return float(value)

    def condition(self, nodes: list, state: State, scope="actor") -> bool:
        def entry(key, op, value):
            current = self.current(state, scope)
            if key == "NOT":
                return not self.condition(value, state, scope)
            if key == "OR":
                return any(entry(*child) for child in value)
            if key == "AND":
                return self.condition(value, state, scope)
            if key == "always":
                return value == "yes"
            if key == "exists":
                return self.reference(value, state, scope) is not None
            if key == "trigger_if":
                return not self.condition(get(value, "limit"), state, scope) or self.condition([n for n in value if n[0] != "limit"], state, scope)
            if key == "custom_description":
                return self.condition([n for n in value if n[0] != "text"], state, scope)
            if key in ("player_heir", "house", "dynasty", "court_owner") and isinstance(value, list):
                target = getattr(current, key)
                return target is not None and self.condition(value, state, target)
            if key == "court_owner":
                return self.compare(current.court_owner, op, self.reference(value, state, scope))
            if key == "opinion":
                if len(value) != 2:
                    raise ValueError("only a target and value comparison are supported for opinion")
                target = self.reference(get(value, "target"), state, scope)
                comparison = next(node for node in value if node[0] == "value")
                return self.compare(current.opinion_values.get(target, 0), comparison[1], self.number(comparison[2], state, scope))
            if key == "involved_activity":
                return current.activity is not None and self.condition(value, state, current.activity)
            if key == "is_ai": return current.ai == (value == "yes")
            if key == "is_playable_character": return current.playable == (value == "yes")
            if key == "is_incapable": return current.incapable == (value == "yes")
            if key == "any_in_list":
                return any(self.condition([n for n in value if n[0] != "variable"], state, item) for item in current.lists.get(get(value, "variable"), []))
            if key.startswith(("scope:", "var:")) and isinstance(value, list):
                target = self.reference(key, state, scope)
                return target is not None and self.condition(value, state, "activity" if key == "scope:activity" else target)
            if key == "has_variable":
                return value in self.variables(state, scope)
            if key == "artifact_type": return current.artifact_type == value
            if key == "artifact_owner": return current.owner is self.reference(value, state, scope)
            if key == "has_artifact_modifier": return value in current.modifiers
            if key == "any_character_artifact":
                return any(artifact.owner is current and self.condition(value, state, artifact) for artifact in current.artifacts)
            if key in ("has_character_flag", "has_character_modifier", "has_trait"):
                collection = {"has_character_flag": current.flags, "has_character_modifier": current.modifiers, "has_trait": current.traits}[key]
                return value in collection
            if key in ("is_alive", "is_adult", "is_imprisoned", "is_available_adult"):
                result = {"is_alive": current.alive, "is_adult": current.adult, "is_imprisoned": current.imprisoned, "is_available_adult": current.alive and current.adult and current.available}[key]
                return result if value == "yes" else not result
            if key == "any_attending_character":
                return any(self.condition(value, state, person) for person in state.attendees)
            if key == "has_trait_xp":
                comparison = next(n for n in value if n[0] == "value")
                return get(value, "trait") in current.traits and comparison[1] == ">=" and current.xp.get(get(value, "track"), 0) >= float(comparison[2])
            if key == "has_activity_option":
                return get(value, "option") == f"rol_expedition_preparation_{state.preparation}"
            if key == "has_activity_type":
                return isinstance(current, dict) and current.get("_activity_type") == value
            if key in self.triggers:
                result = self.condition(self.triggers[key], state, scope)
                return result if value == "yes" else not result
            if key.startswith("var:"):
                variables = self.variables(state, scope)
                if key[4:] not in variables:
                    return False
                left, right = self.number(key, state, scope), self.number(value, state, scope)
                return self.compare(left, op, right)
            if key.startswith("scope:"):
                left = self.reference(key, state, scope)
                return left is not None and self.compare(left, op, self.number(value, state, scope))
            if key == "this":
                return self.compare(current, op, self.reference(value, state, scope))
            if key in ("learning", "martial", "prowess", "diplomacy", "stewardship", "intrigue", "gold", "prestige", "piety"):
                return self.compare(getattr(current, key), op, self.number(value, state, scope))
            raise ValueError(f"unsupported condition {key}")
        return all(entry(*node) for node in nodes)

    @staticmethod
    def compare(left, op, right):
        if op == "=": return left == right
        if op == "!=": return left != right
        if op == ">=": return left >= right
        if op == "<=": return left <= right
        if op == ">": return left > right
        if op == "<": return left < right
        raise ValueError(f"unsupported comparison {op}")

    def selected(self, nodes: list, state: State, scope: str):
        taken = False
        for key, op, value in nodes:
            if key in ("if", "else_if", "else"):
                eligible = key == "if" or not taken
                if key == "if":
                    taken = False
                if eligible and (key == "else" or self.condition(get(value, "limit"), state, scope)):
                    taken = True
                    yield from self.selected([n for n in value if n[0] != "limit"], state, scope)
            else:
                yield key, op, value

    def calculate(self, nodes: list, state: State, scope: str = "actor") -> float:
        total = 0.0
        for key, _, value in self.selected(nodes, state, scope):
            number = self.number(value, state, scope)
            if key == "value": total = number
            elif key == "add": total += number
            elif key == "subtract": total -= number
            elif key == "min": total = max(total, number)
            elif key == "max": total = min(total, number)
            else: raise ValueError(f"unsupported value operation {key}")
        return total

    def call(self, name: str, state: State, parameters: dict | None = None, scope="actor"):
        self.run(expand(self.effects[name], parameters or {}), state, scope)

    def run(self, nodes: list, state: State, scope="actor"):
        for key, op, value in self.selected(nodes, state, scope):
            current = self.current(state, scope)
            variables = self.variables(state, scope)
            if key == "involved_activity":
                if current.activity is not None:
                    self.run(value, state, current.activity)
            elif key.startswith(("scope:", "var:")) and isinstance(value, list):
                target = self.reference(key, state, scope)
                if target is None:
                    if op == "?=": continue
                    raise ValueError(f"required scope is missing: {key}")
                self.run(value, state, "activity" if key == "scope:activity" else target)
            elif key == "save_scope_as": state.scopes[value] = current
            elif key in ("player_heir", "house", "dynasty"):
                target = getattr(current, key)
                if target is not None: self.run(value, state, target)
                elif op != "?=": raise ValueError(f"required {key} is missing")
            elif key in ("add_to_variable_list", "remove_list_variable"):
                entries = current.lists.setdefault(get(value, "name"), [])
                target = self.reference(get(value, "target"), state, scope)
                if key == "add_to_variable_list": entries.append(target)
                elif target in entries: entries.remove(target)
            elif key in ("every_in_list", "random_in_list"):
                entries = list(current.lists.get(get(value, "variable"), []))
                body = [n for n in value if n[0] != "variable"]
                for item in (entries[:1] if key == "random_in_list" else entries): self.run(body, state, item)
            elif key == "save_scope_value_as": state.scopes[get(value, "name")] = self.number(get(value, "value"), state, scope)
            elif key == "random_character_artifact":
                candidates = [artifact for artifact in current.artifacts if artifact.owner is current and self.condition(get(value, "limit"), state, artifact)]
                # Use the first qualifying item; this checks filtering, not CK3 randomness.
                if candidates: self.run([n for n in value if n[0] != "limit"], state, candidates[0])
            elif key == "ordered_attending_character":
                candidates = [person for person in state.attendees if self.condition(get(value, "limit"), state, person)]
                candidates.sort(key=lambda person: self.number(get(value, "order_by"), state, person), reverse=True)
                body = [n for n in value if n[0] not in ("limit", "order_by", "max")]
                for person in candidates[:int(get(value, "max"))]: self.run(body, state, person)
            elif key in ("set_variable", "change_variable"):
                name = get(value, "name")
                operand = get(value, "value" if key == "set_variable" else "add")
                number = self.number(operand, state, scope)
                variables[name] = number if key == "set_variable" else variables[name] + number
            elif key == "remove_variable": variables.pop(value, None)
            elif key == "clear_saved_scope": state.scopes.pop(value, None)
            elif key == "add_character_flag":
                flag = get(value, "flag") if isinstance(value, list) else value
                current.flags.add(flag)
                if isinstance(value, list): current.flag_durations[flag] = [(k, v) for k, _, v in value if k != "flag"]
            elif key == "remove_character_flag": current.flags.discard(value)
            elif key in ("add_character_modifier", "add_house_modifier", "add_dynasty_modifier"):
                years = next((v for k, _, v in value if k == "years"), None)
                current.modifiers[get(value, "modifier")] = self.number(years, state, scope) if years is not None else None
            elif key == "remove_character_modifier": current.modifiers.pop(value, None)
            elif key == "add_artifact_modifier": current.modifiers[value] = None
            elif key == "remove_artifact_modifier": current.modifiers.pop(value, None)
            elif key == "add_trait": current.traits.add(value)
            elif key == "add_trait_xp":
                track = get(value, "track")
                current.xp[track] = min(100, current.xp.get(track, 0) + self.number(get(value, "value"), state, scope))
            elif key == "add_stress": current.stress = max(0, current.stress + self.number(value, state, scope))
            elif key == "add_prestige": current.prestige += self.number(value, state, scope)
            elif key == "add_dynasty_prestige": current.prestige += self.number(value, state, scope)
            elif key == "add_piety": current.piety += self.number(value, state, scope)
            elif key == "add_learning_lifestyle_xp": current.learning_lifestyle_xp += self.number(value, state, scope)
            elif key == "add_gold": current.gold += self.number(value, state, scope)
            elif key == "remove_short_term_gold": current.gold -= self.number(value, state, scope)
            elif key == "add_opinion": current.opinions.append((self.reference(get(value, "target"), state, scope), get(value, "modifier")))
            elif key.startswith("activity_special_type_progression_"): state.progress_effects.append(key)  # native operation recorded, not emulated
            elif key == "trigger_event":
                event = get(value, "id") if isinstance(value, list) else value
                current.events.append(event)
                current.event_contexts.append((event, dict(state.scopes)))
            elif key == "progress_activity_phase_after":
                state.progress_effects.append((key, get(value, "days")))  # Native timing is not simulated.
            elif key == "send_interface_toast": pass  # presentation only
            elif key in ("error_log", "play_sound_effect"): pass  # diagnostics/presentation only
            elif key == "hidden_effect": self.run(value, state, scope)
            elif key == "add_activity_log_entry":
                state.activity.setdefault("_log_entries", []).append(get(value, "key"))
                record = {"key": get(value, "key")}
                for field in ("character", "target"):
                    values = [v for k, _, v in value if k == field]
                    if values:
                        person = self.reference(values[0], state, scope)
                        # Labels are character identities in PathModel. Capture a
                        # scalar, so logs do not add cyclic actors to state snapshots.
                        record[field] = getattr(person, "label", id(person)) if person is not None else None
                state.activity.setdefault("_log_records", []).append(record)
            elif key in self.effects: self.call(key, state, {k: v for k, _, v in value} if isinstance(value, list) else {}, scope)
            else: raise ValueError(f"unsupported effect {key}")


ROUTES = {
    "rome": ("mars", "rol_mars_activity.txt", "rol_apply_mars_activity_cooldown_effect"),
    "munich": ("nibelung", "rol_nibelung_activity.txt", "rol_apply_nibelung_activity_cooldown_effect"),
    "naxos": ("naxos", "rol_naxos_activity.txt", "rol_apply_naxos_activity_cooldown_effect"),
    "sevilla": ("astrolabe", "rol_astrolabe_activity.txt", "rol_apply_astrolabe_activity_cooldown_effect"),
    "carthage": ("carthage", "rol_carthage_activity.txt", "rol_apply_carthage_activity_cooldown_effect"),
}


def check_growth_contract(root: Path, errors: list[str]) -> int:
    try:
        model = Model(root)
        load = lambda path: parse((root / path).read_text(encoding="utf-8-sig"))
        trait = get(load("common/traits/rol_expedition_traits.txt"), "rol_relic_seeker")
        assert get(trait, "category") == "lifestyle", "seeker trait is not an expertise trait"
        tracks = get(trait, "tracks")
        events = load("events/rol_expedition_growth_events.txt")
        reflection = get(events, "rol_expedition_growth.0001")
        assert get(get(reflection, "trigger"), "rol_expedition_growth_pending_trigger") == "yes", "reflection lacks pending-state entry guard"
        backgrounds = load("common/event_backgrounds/rol_event_backgrounds.txt")
        get(backgrounds, get(get(reflection, "override_background"), "reference"))
        review = get(load("common/decisions/rol_expedition_growth_decisions.txt"), "rol_review_expedition_journal_decision")
        assert get(get(review, "is_shown"), "rol_expedition_growth_pending_trigger") == "yes", "journal decision is not pending-only"
        assert get(get(review, "effect"), "trigger_event") == "rol_expedition_growth.0001", "journal decision does not reopen reflection"
        options = [v for k, _, v in reflection if k == "option"]
        assert len(options) == 3, "reflection needs all three focus choices"
        modifier_nodes = load("common/modifiers/rol_expedition_growth_modifiers.txt")
        for track, focus, personality, option in zip(
            ("rol_research", "rol_exploration", "rol_negotiation"),
            ("research", "exploration", "negotiation"), ("diligent", "brave", "gregarious"), options,
        ):
            assert {k for k, _, _ in get(tracks, track)} == {"20", "60", "100"}, f"{track}: missing progression thresholds"
            params = dict((k, v) for k, _, v in get(option, "rol_expedition_growth_choose_focus_effect"))
            assert params == {"TRACK": track, "FOCUS_MODIFIER": f"rol_expedition_{focus}_focus_modifier", "MATCHING_TRAIT": personality}, f"{track}: wrong focus wiring"
            get(modifier_nodes, params["FOCUS_MODIFIER"])

        for chain, (route, filename, cooldown) in ROUTES.items():
            activity = load(f"common/activities/activity_types/{filename}")[0][2]
            host = get(get(activity, "on_start"), "scope:host")
            assert get(get(host, "rol_expedition_growth_begin_effect"), "ROUTE") == route, f"{chain}: wrong start route"
            effects = load(f"common/scripted_effects/rol_quest_{chain}_effects.txt")
            for ending, xp, notes in (("success", "30", "no"), ("partial", "20", "yes")):
                body = get(get(effects, f"rol_{chain}_quest_{ending}_finalize_effect"), "if")
                params = dict((k, v) for k, _, v in get(body, "rol_expedition_growth_finish_effect"))
                assert params == {"ROUTE": route, "RESULT_XP": xp, "LEAVE_NOTES": notes}, f"{chain}: wrong {ending} reward"
            failure = [n for n in get(get(effects, cooldown), "if") if n[0] != "limit"]
            stage_guard = get(get(failure, "if"), "limit")
            assert (f"var:rol_{chain}_stage_count", ">=", "1") in stage_guard, f"{chain}: failure XP lacks completed-stage guard"
            failure_params = get(get(failure, "if"), "rol_expedition_growth_finish_effect")
            assert get(failure_params, "ROUTE") == route and get(failure_params, "RESULT_XP") == "10" and get(failure_params, "LEAVE_NOTES") == "no", f"{chain}: wrong failure reward"
            assert get(get(failure, "else"), "rol_expedition_growth_abandon_effect") == "yes", f"{chain}: unearned failure is not closed"
            for stage in (0, 1):
                failed = State(variables={f"rol_{chain}_stage_count": stage})
                model.call("rol_expedition_growth_begin_effect", failed, {"ROUTE": route})
                model.run(failure[:2], failed)
                assert failed.variables.get("rol_expedition_growth_pending_xp", 0) == (10 if stage else 0), f"{chain}: failure XP is not gated by progress"
                assert failed.activity["rol_expedition_growth_open"] == 0, f"{chain}: failed activity remains open for rewards"
            notes_modifier = f"rol_expedition_{route}_notes_modifier"
            get(modifier_nodes, notes_modifier)
            state = State(modifiers={notes_modifier: 10, "rol_expedition_other_notes_modifier": 10})
            model.call("rol_expedition_growth_begin_effect", state, {"ROUTE": route})
            assert notes_modifier not in state.modifiers and "rol_expedition_other_notes_modifier" in state.modifiers, f"{chain}: evidence consumption crosses routes"
            assert state.activity["rol_expedition_journal_bonus"] == 5, f"{chain}: notes bonus missing"
            for xp, notes in ((30, "no"), (20, "yes"), (10, "no")):
                reward = State()
                model.call("rol_expedition_growth_begin_effect", reward, {"ROUTE": route})
                params = {"ROUTE": route, "RESULT_XP": xp, "LEAVE_NOTES": notes}
                model.call("rol_expedition_growth_finish_effect", reward, params)
                model.call("rol_expedition_growth_finish_effect", reward, params)
                assert reward.variables["rol_expedition_growth_pending_xp"] == xp and len(reward.events) == 1, f"{chain}: duplicate finish pays twice"
                assert (notes_modifier in reward.modifiers) == (notes == "yes"), f"{chain}: evidence issued on wrong ending"
                if notes == "yes":
                    assert reward.modifiers[notes_modifier] == 10, f"{chain}: notes duration differs from description"

        for option in options:
            params = dict((k, v) for k, _, v in get(option, "rol_expedition_growth_choose_focus_effect"))
            state = State(traits={params["MATCHING_TRAIT"]}, modifiers={f"rol_expedition_{focus}_focus_modifier": 3 for focus in ("research", "exploration", "negotiation")})
            model.call("rol_expedition_growth_debug_queue_effect", state)
            model.call("rol_expedition_growth_choose_focus_effect", state, params)
            model.call("rol_expedition_growth_choose_focus_effect", state, params)
            assert state.xp == {params["TRACK"]: 20}, "reflection replay adds experience"
            assert state.modifiers == {params["FOCUS_MODIFIER"]: 3}, "focus benefits stack"
            assert state.stress == 15 and not state.flags and not state.variables, "reflection did not clean pending state or repeated stress reward"

        pending = State()
        model.call("rol_expedition_growth_debug_queue_effect", pending)
        model.call("rol_expedition_growth_begin_effect", pending, {"ROUTE": "mars"})
        model.call("rol_expedition_growth_finish_effect", pending, {"ROUTE": "mars", "RESULT_XP": 20, "LEAVE_NOTES": "yes"})
        assert pending.variables["rol_expedition_growth_pending_xp"] == 40 and len(pending.events) == 1, "delayed reflection loses existing XP or schedules duplicate events"

        missing = State(activity=None, modifiers={"rol_expedition_mars_notes_modifier": 10})
        model.call("rol_expedition_growth_begin_effect", missing, {"ROUTE": "mars"})
        model.call("rol_expedition_growth_finish_effect", missing, {"ROUTE": "mars", "RESULT_XP": 30, "LEAVE_NOTES": "yes"})
        assert not missing.variables and missing.modifiers == {"rol_expedition_mars_notes_modifier": 10} and not missing.events, "direct finalize without activity grants growth or consumes notes"

        for prep, adjustment in (("low", -10), ("standard", 0), ("high", 10), ("supreme", 20)):
            for bonus in (0, 5):
                for base in (35, 40, 45, 50, 55, 65, 70, 75, 80, 85, 90):
                    state = State(preparation=prep, activity={"rol_expedition_journal_bonus": bonus}, variables={"rol_expedition_display_base_chance": base})
                    actual = model.number(f"rol_expedition_success_chance_{base}_value", state)
                    failure = model.number(f"rol_expedition_failure_chance_{base}_value", state)
                    shown = model.number("rol_expedition_display_success_chance_value", state)
                    shown_failure = model.number("rol_expedition_display_failure_chance_value", state)
                    assert actual == shown == min(95, max(5, base + adjustment + bonus)), "journal/preparation formula differs from tooltip or cap"
                    assert failure == shown_failure == 100 - actual, "failure chance is not the complement"
        return len(ROUTES)
    except (AssertionError, ValueError, KeyError, OSError, TypeError, IndexError) as error:
        errors.append(f"growth contract: {error}")
        return 0


if __name__ == "__main__":
    import sys
    issues = []
    routes = check_growth_contract(Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2], issues)
    for issue in issues:
        print(f"[FAIL] {issue}")
    if not issues:
        print(f"[OK] Growth contracts: {routes} routes; evidence, replay, focus replacement and chance arithmetic passed (model only)")
    raise SystemExit(bool(issues))
