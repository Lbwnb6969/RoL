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


@dataclass
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


class Model:
    def __init__(self, root: Path):
        self.effects = dict((k, v) for k, _, v in parse((root / "common/scripted_effects/rol_expedition_growth_effects.txt").read_text(encoding="utf-8-sig")))
        self.triggers = {}
        self.values = {}
        for name, directory, files in (
            (self.triggers, "scripted_triggers", ("rol_expedition_growth_triggers.txt", "rol_expedition_preparation_triggers.txt")),
            (self.values, "script_values", ("rol_expedition_growth_values.txt", "rol_expedition_preparation_values.txt")),
        ):
            for filename in files:
                nodes = parse((root / "common" / directory / filename).read_text(encoding="utf-8-sig"))
                name.update({k: v for k, _, v in nodes})

    def number(self, value: str, state: State, scope: str = "actor") -> float:
        if value.startswith("scope:activity.var:"):
            return state.activity[value.split("var:", 1)[1]]
        if value.startswith("var:"):
            return (state.variables if scope == "actor" else state.activity)[value[4:]]
        if value in self.values:
            return self.calculate(self.values[value], state, scope)
        return float(value)

    def condition(self, nodes: list, state: State, scope: str = "actor") -> bool:
        def entry(key, op, value):
            if key == "NOT":
                return not self.condition(value, state, scope)
            if key == "OR":
                return any(entry(*child) for child in value)
            if key == "AND":
                return self.condition(value, state, scope)
            if key == "always":
                return value == "yes"
            if key == "exists":
                if value != "scope:activity":
                    raise ValueError(f"unsupported exists {value}")
                return state.activity is not None
            if key == "scope:activity":
                return state.activity is not None and self.condition(value, state, "activity")
            if key == "has_variable":
                return value in (state.variables if scope == "actor" else (state.activity or {}))
            if key in ("has_character_flag", "has_character_modifier", "has_trait"):
                collection = {"has_character_flag": state.flags, "has_character_modifier": state.modifiers, "has_trait": state.traits}[key]
                return value in collection
            if key == "has_activity_option":
                return get(value, "option") == f"rol_expedition_preparation_{state.preparation}"
            if key in self.triggers:
                result = self.condition(self.triggers[key], state, scope)
                return result if value == "yes" else not result
            if key.startswith("var:"):
                variables = state.variables if scope == "actor" else (state.activity or {})
                if key[4:] not in variables:
                    return False
                left, right = self.number(key, state, scope), self.number(value, state, scope)
                return {"=": left == right, "!=": left != right, ">": left > right, "<": left < right, ">=": left >= right, "<=": left <= right}[op]
            raise ValueError(f"unsupported condition {key}")
        return all(entry(*node) for node in nodes)

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

    def call(self, name: str, state: State, parameters: dict | None = None):
        self.run(expand(self.effects[name], parameters or {}), state)

    def run(self, nodes: list, state: State, scope: str = "actor"):
        for key, op, value in self.selected(nodes, state, scope):
            variables = state.variables if scope == "actor" else state.activity
            if key == "scope:activity":
                if state.activity is None:
                    if op == "?=": continue
                    raise ValueError("required activity scope is missing")
                self.run(value, state, "activity")
            elif key in ("set_variable", "change_variable"):
                name = get(value, "name")
                operand = get(value, "value" if key == "set_variable" else "add")
                number = self.number(operand, state, scope)
                variables[name] = number if key == "set_variable" else variables[name] + number
            elif key == "remove_variable": variables.pop(value, None)
            elif key == "add_character_flag": state.flags.add(value)
            elif key == "remove_character_flag": state.flags.discard(value)
            elif key == "add_character_modifier": state.modifiers[get(value, "modifier")] = self.number(get(value, "years"), state)
            elif key == "remove_character_modifier": state.modifiers.pop(value, None)
            elif key == "add_trait": state.traits.add(value)
            elif key == "add_trait_xp":
                track = get(value, "track")
                state.xp[track] = min(100, state.xp.get(track, 0) + self.number(get(value, "value"), state))
            elif key == "add_stress": state.stress = max(0, state.stress + self.number(value, state))
            elif key == "trigger_event": state.events.append(get(value, "id") if isinstance(value, list) else value)
            elif key == "send_interface_toast": pass  # presentation only
            elif key in self.effects: self.call(key, state, {k: v for k, _, v in value} if isinstance(value, list) else {})
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
                body = get(effects, f"rol_{chain}_quest_{ending}_finalize_effect")
                params = dict((k, v) for k, _, v in get(body, "rol_expedition_growth_finish_effect"))
                assert params == {"ROUTE": route, "RESULT_XP": xp, "LEAVE_NOTES": notes}, f"{chain}: wrong {ending} reward"
            failure = get(effects, cooldown)
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
