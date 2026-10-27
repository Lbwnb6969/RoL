#!/usr/bin/env python3
"""Trace real RoL entrances/options/queued events in a finite source model.

This is deliberately not a CK3 simulator. Native progression is read from the
installed game source; presentation is skipped explicitly, unknown syntax fails.
Time covers integer event delays and expiring flags, not travel or engine order.
"""
from __future__ import annotations

from collections import Counter, deque
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
import argparse
import json

if __package__:
    from .rol_growth_contracts import Model, State, parse, get, ROUTES
else:
    from rol_growth_contracts import Model, State, parse, get, ROUTES


GAME = Path("D:/SteamLibrary/steamapps/common/Crusader Kings III/game")
META = {"name", "flavor", "skill", "trigger", "custom_tooltip", "ai_chance"}
PRESENTATION = {"desc", "custom_tooltip", "show_as_tooltip", "highlight_portrait"}
TITLES = {"rome": "c_roma", "munich": "c_munchen", "naxos": "c_naxos",
          "sevilla": "c_sevilla", "carthage": "c_tunis"}
CLAIMED = {"rome": "rol_mars_blade_claimed", "munich": "rol_nibelung_sphere_claimed",
           "naxos": "rol_naxos_unit_unlocked", "sevilla": "rol_astrolabe_of_ocean_claimed",
           "carthage": "rol_ash_forged_mask_claimed"}


def optional(nodes, key, default=None):
    matches = [v for k, _, v in nodes if k == key]
    assert len(matches) <= 1, f"duplicate {key}"
    return matches[0] if matches else default


@dataclass(eq=False)
class Person(State):
    intrigue: float = 15
    stewardship: float = 15
    piety_level: int = 2
    titles: set = field(default_factory=set)
    at_war: bool = False
    court: list = field(default_factory=list)
    queue: list = field(default_factory=list)
    day: int = 0
    expires: dict = field(default_factory=dict)
    modifier_expires: dict = field(default_factory=dict)
    phase_end: int | None = None
    trace: list = field(default_factory=list)
    label: str = "host"


class BranchNeeded(Exception):
    def __init__(self, choices):
        self.choices = choices


class PathModel(Model):
    def __init__(self, root, game=GAME):
        super().__init__(root)
        self.root = root
        self.events, self.activities, self.decisions, self.on_actions = {}, {}, {}, {}
        for directory, target in (("common/scripted_effects", self.effects),
                                  ("common/scripted_triggers", self.triggers),
                                  ("common/script_values", self.values),
                                  ("events", self.events),
                                  ("common/activities/activity_types", self.activities),
                                  ("common/decisions", self.decisions),
                                  ("common/on_action", self.on_actions)):
            for path in sorted((root / directory).glob("rol*.txt")):
                for key, _, body in parse(path.read_text(encoding="utf-8-sig")):
                    if not isinstance(body, list): continue
                    if target is self.on_actions: target.setdefault(key, []).extend(body)
                    else:
                        assert key not in target or target in (self.effects, self.triggers, self.values), f"duplicate {key}"
                        target[key] = body
        native = parse((game / "common/scripted_effects/00_activity_effects.txt").read_text(encoding="utf-8-sig"))
        self.native = {k: v for k, _, v in native
                       if k.startswith(("activity_special_type_progression_", "activity_setup_special_type_progression_"))}
        assert self.native, "native progression source unavailable"
        self.plan, self.branch_index, self.coverage = [], 0, set()
        self.options_seen = set()
        self.random_sites = {}
        self._index_random(self.effects)
        self._index_random(self.events)
        self._index_random(self.on_actions)

    def _index_random(self, definitions):
        def visit(nodes, path):
            for i, (k, _, v) in enumerate(nodes):
                if isinstance(v, list):
                    name = f"{path}/{k}[{i}]"
                    if k == "random_list": self.random_sites[repr(v)] = name
                    visit(v, name)
        for name, nodes in definitions.items(): visit(nodes, name)

    def current(self, state, scope):
        if scope == "activity": return state.scopes.get("activity", state.activity)
        return super().current(state, scope)

    def reference(self, value, state, scope="actor"):
        if value == "scope:activity": return self.current(state, "activity")
        if value.startswith("root.") and ".var:" not in value:
            return self.reference(value[5:], state, state)
        if value.endswith(".tier"):
            title = self.reference(value[:-5], state, scope)
            return None if title is None else title["tier"]
        if "." in value and ".var:" not in value:
            prefix, attribute = value.rsplit(".", 1)
            target = self.reference(prefix, state, scope)
            return None if target is None else getattr(target, attribute)
        if value.startswith("title:"): return value[6:]
        return super().reference(value, state, scope)

    def number(self, value, state, scope="actor"):
        if value.startswith("tier_"): return value
        if value in ("martial", "intrigue", "stewardship", "piety"):
            return getattr(self.current(state, scope), value)
        return super().number(value, state, scope)

    def condition(self, nodes, state, scope="actor"):
        # Split only top-level conjunctions; base logic delegates nested conditions
        # back here, preserving NOT/OR/trigger_if and strict unknown-key behavior.
        for key, op, value in nodes:
            current = self.current(state, scope)
            if key == "OR": result = any(self.condition([child], state, scope) for child in value)
            elif key == "root" and isinstance(value, list): result = self.condition(value, state, state)
            elif key == "is_landed": result = bool(current.titles) == (value == "yes")
            elif key == "has_title": result = value.removeprefix("title:") in current.titles
            elif key == "is_at_war": result = current.at_war == (value == "yes")
            elif key == "is_available_adult":
                result = (current.alive and current.adult and current.available and
                          not current.imprisoned and not current.incapable and current.activity is None)
                result = result == (value == "yes")
            elif key in ("intrigue", "stewardship", "piety", "piety_level"):
                result = self.compare(getattr(current, key), op, self.number(value, state, scope))
            elif key == "is_activity_type_on_cooldown":
                result = value in current.expires and current.expires[value] > current.day
            elif key == "custom_tooltip" and isinstance(value, list):
                result = self.condition([n for n in value if n[0] != "text"], state, scope)
            else: result = super().condition([(key, op, value)], state, scope)
            if not result: return False
        return True

    def run(self, nodes, state, scope="actor"):
        for key, op, value in self.selected(nodes, state, scope):
            current = self.current(state, scope)
            if key in self.native:
                self.run(self.native[key] if not isinstance(value, list) else
                         self._parameters(self.native[key], value), state, scope)
            elif key in PRESENTATION: continue
            elif key == "root" and isinstance(value, list): self.run(value, state, state)
            elif key == "random_list":
                eligible = []
                for i, (weight, _, body) in enumerate(value):
                    trigger = optional(body, "trigger", [])
                    if not self.condition(trigger, state, scope): continue
                    score = float(weight)
                    for name, _, modifier in body:
                        if name != "modifier": continue
                        conditions = [n for n in modifier if n[0] not in ("add", "factor", "trigger")]
                        if not self.condition(optional(modifier, "trigger", []) + conditions, state, scope): continue
                        for action, _, operand in modifier:
                            if action == "add": score += self.number(operand, state, scope)
                            elif action == "factor": score *= self.number(operand, state, scope)
                    if score > 0: eligible.append(i)
                assert eligible, "random list has no positive branch"
                if self.branch_index == len(self.plan): raise BranchNeeded(eligible)
                choice = self.plan[self.branch_index]
                self.branch_index += 1
                assert choice in eligible, "selected zero-weight branch"
                self.coverage.add((self.random_sites.get(repr(value), repr(value)), choice))
                self.run([n for n in value[choice][2] if n[0] not in ("modifier", "trigger")], state, scope)
            elif key in ("random_attending_character", "random_courtier_or_guest"):
                population = state.attendees if key == "random_attending_character" else current.court
                candidates = [p for p in population if self.condition(get(value, "limit"), state, p)]
                if candidates: self.run([n for n in value if n[0] != "limit"], state, candidates[0])
            elif key == "create_artifact":
                artifact = Person(activity=None, owner=current, artifact_type=get(value, "type"),
                                  label=get(value, "type"))
                artifact.modifiers[get(value, "modifier")] = None
                current.artifacts.append(artifact)
                saved = optional(value, "save_scope_as")
                if saved: state.scopes[saved] = artifact
            elif key == "trigger_event":
                event = get(value, "id") if isinstance(value, list) else value
                delay = 0
                if isinstance(value, list):
                    for unit, _, amount in value:
                        if unit in ("days", "months", "years"):
                            delay += int(float(amount) * {"days": 1, "months": 30, "years": 365}[unit])
                current.queue.append((current.day + delay, event, dict(state.scopes)))
            elif key == "progress_activity_phase_after":
                host = state.scopes["host"]
                host.phase_end = host.day + int(get(value, "days"))
            elif key == "invalidation_host_death_effect":
                raise ValueError("native death invalidation must be tested in CK3")
            elif key == "every_in_list" or key == "random_in_list":
                items = list(current.lists.get(get(value, "variable"), []))
                items = [p for p in items if self.condition(optional(value, "limit", []), state, p)]
                body = [n for n in value if n[0] not in ("variable", "limit")]
                for item in (items[:1] if key == "random_in_list" else items): self.run(body, state, item)
            else:
                super().run([(key, op, value)], state, scope)
                if key == "add_character_flag" and isinstance(value, list):
                    flag = get(value, "flag")
                    duration = sum(float(v) * {"days": 1, "months": 30, "years": 365}[k]
                                   for k, _, v in value if k in ("days", "months", "years"))
                    current.expires[flag] = current.day + duration
                elif key == "add_character_modifier":
                    duration = sum(float(v) * {"days": 1, "months": 30, "years": 365}[k]
                                   for k, _, v in value if k in ("days", "months", "years"))
                    if duration: current.modifier_expires[get(value, "modifier")] = current.day + duration

    @staticmethod
    def _parameters(nodes, params):
        if __package__: from .rol_growth_contracts import expand
        else: from rol_growth_contracts import expand
        return expand(nodes, {k: v for k, _, v in params})

    def alternatives(self, nodes, initial):
        plans = [[]]
        while plans:
            plan = plans.pop()
            candidate = deepcopy(initial)
            self.plan, self.branch_index = plan, 0
            try: self.run(nodes, candidate)
            except BranchNeeded as point:
                plans.extend(plan + [choice] for choice in reversed(point.choices))
                continue
            yield candidate

    def option_body(self, option):
        return [n for n in option if n[0] not in META]

    def advance(self, actor, day, activity_definition=None):
        if actor.phase_end is not None and actor.phase_end <= day and actor.activity is not None:
            actor.day = actor.phase_end
            if activity_definition is not None:
                self.run(get(activity_definition, "on_complete"), actor)
            actor.activity = None
            actor.available = True
            actor.phase_end = None
        actor.day = day
        for flag, expiry in list(actor.expires.items()):
            if expiry <= day:
                actor.flags.discard(flag)
                del actor.expires[flag]
        for modifier, expiry in list(actor.modifier_expires.items()):
            if expiry <= day:
                actor.modifiers.pop(modifier, None)
                del actor.modifier_expires[modifier]

    def dispatch(self, actor, event, context):
        actor.scopes = context
        definition = self.events[event]
        if not self.condition(optional(definition, "trigger", []), actor): return None
        self.run(optional(definition, "immediate", []), actor)
        return definition

    def decide(self, actor, decision):
        definition = self.decisions[decision]
        assert actor.expires.get(decision, 0) <= actor.day, f"decision on cooldown: {decision}"
        for key in ("is_shown", "is_valid", "is_valid_showing_failures_only"):
            assert self.condition(optional(definition, key, []), actor), f"decision unavailable: {decision}/{key}"
        for key, _, amount in optional(definition, "cost", []):
            assert not isinstance(amount, list), "only scalar decision costs supported"
            setattr(actor, key, getattr(actor, key) - float(amount))
        self.run(get(definition, "effect"), actor)
        cooldown = optional(definition, "cooldown", [])
        if cooldown:
            actor.expires[decision] = actor.day + sum(float(v) * {"days": 1, "months": 30, "years": 365}[k]
                                                      for k, _, v in cooldown)

    def choose(self, actor, event, name):
        definition = self.dispatch(actor, event, dict(actor.scopes))
        assert definition is not None, f"event blocked: {event}"
        option = next(v for k, _, v in definition if k == "option" and get(v, "name") == name)
        assert self.condition(optional(option, "trigger", []), actor), f"option unavailable: {name}"
        self.run(self.option_body(option), actor)


def identity(value):
    if isinstance(value, Person): return (value.label, value.alive)
    if isinstance(value, dict): return tuple(sorted((k, identity(v)) for k, v in value.items() if k not in ("_log_entries", "_log_records")))
    if isinstance(value, set): return tuple(sorted(value))
    if isinstance(value, (list, tuple)): return tuple(identity(v) for v in value)
    return value


def signature(actor):
    """All mutable fields consulted by route guards, plus exact costs and progress."""
    return (actor.day, identity(actor.variables), tuple(sorted(actor.flags)), identity(actor.modifiers),
            tuple(sorted(actor.traits)), identity(actor.xp), actor.gold, actor.prestige, actor.piety,
            actor.stress, identity(actor.activity), actor.phase_end,
            tuple((due, event, identity(context)) for due, event, context in actor.queue),
            tuple((p.label, p.gold, identity(p.opinions)) for p in actor.attendees if p is not actor))


def start_route(model, chain, stat=30, company=False, actor=None, discover=True):
    actor = actor or Person(activity=None, gold=4000, prestige=1000,
                   learning=stat, martial=stat, prowess=stat, diplomacy=stat,
                   intrigue=stat, stewardship=stat, house=Person(activity=None, label="house"),
                   dynasty=Person(activity=None, label="dynasty"))
    route, filename, _ = ROUTES[chain]
    if discover:
        actor.titles.add(TITLES[chain])
        model.run(get(model.on_actions["rol_relic_discovery_yearly_on_action"], "effect"), actor)
        drive(model, actor)
    assert f"rol_heard_{route}_legend" in actor.flags, f"discovery failed: {chain}"
    kind = {
                    "rome": "activity_rol_seek_mars_blade", "munich": "activity_rol_seek_nibelung_sphere",
                    "naxos": "activity_rol_seek_naxos_guard", "sevilla": "activity_rol_seek_astrolabe_of_ocean",
                    "carthage": "activity_rol_seek_ash_forged_mask"}[chain]
    definition = model.activities[kind]
    assert model.condition(get(definition, "is_shown"), actor)
    assert model.condition(get(definition, "can_start_showing_failures_only"), actor)
    # The scalar source costs are asserted rather than guessing CK3 GUI prediction.
    base = float(get(get(get(get(definition, "cost"), "gold"), "add"), "value"))
    prep = get(get(get(definition, "options"), "rol_option_expedition_preparation"),
               "rol_expedition_preparation_" + actor.preparation)
    extra = float(get(get(get(get(prep, "cost"), "gold"), "add"), "value"))
    actor.gold -= base + extra
    actor.activity = {"_activity_type": kind}
    actor.scopes = {"host": actor, "activity": actor.activity}
    actor.attendees = [actor]
    if company:
        actor.attendees.extend(Person(activity=actor.activity, label=f"guest{i}", learning=20,
                                      prowess=20, diplomacy=20, playable=False) for i in range(3))
    # Activity-level hook ROOT differs from host; begin from actual hook, not helpers.
    callback = Person(activity=actor.activity, scopes=actor.scopes, attendees=actor.attendees,
                      label="activity-root", preparation=actor.preparation)
    model.run(get(definition, "on_start"), callback, "activity")
    actor.scopes = callback.scopes
    assert model.condition(get(definition, "is_valid"), callback, "activity")
    actor.available = False
    phase = get(definition, "phases")[0][2]
    model.run(get(phase, "on_phase_active"), actor)
    return actor, definition


def drive(model, actor, choices=None, definition=None, stop_before=None):
    """One reproducible witness: specified options, first positive RNG branch."""
    choices = choices or {}
    for _ in range(80):
        if not actor.queue: return actor
        actor.queue.sort(key=lambda q: q[0])
        if stop_before and actor.queue[0][1] == stop_before: return actor
        day, event, context = actor.queue.pop(0)
        model.advance(actor, day, definition)
        event_definition = model.dispatch(actor, event, context)
        if event_definition is None: continue
        actor.trace.append(event)
        eligible = [v for k, _, v in event_definition if k == "option" and
                    model.condition(optional(v, "trigger", []), actor)]
        if optional(event_definition, "hidden") == "yes": continue
        assert eligible, f"witness has no choice: {event}"
        name = choices.get(event, get(eligible[0], "name"))
        selected = next((v for v in eligible if get(v, "name") == name), None)
        assert selected is not None, f"witness choice unavailable: {name}"
        actor = next(model.alternatives(model.option_body(selected), actor))
        actor.trace.append(name)
        model.options_seen.add((event, name))
    raise AssertionError(f"event loop in witness: {actor.trace}")


def explore_quests(model):
    report, options_seen, discarded = {}, set(), set()
    for chain in ROUTES:
        endings = Counter()
        states = 0
        # Profiles cross the actual low/mid/high checks. Company exercises selection,
        # rival/fallback and all contract choices; no need to permute NPC identities.
        for stat, company in ((5, False), (15, False), (20, False), (30, False), (30, True)):
            initial, definition = start_route(model, chain, stat, company)
            pending, seen = deque([initial]), set()
            while pending:
                actor = pending.popleft()
                sig = signature(actor)
                if sig in seen: continue
                seen.add(sig)
                states += 1
                assert states < 100000, f"{chain}: unexpected state explosion"
                if not actor.queue:
                    assert actor.activity is None or actor.activity.get("rol_relic_quest_closed") == 1, (
                        f"{chain}: open route has no successor: {' > '.join(actor.trace)}")
                    assert f"rol_{chain}_stage_count" not in actor.variables
                    assert f"rol_relic_context_{ROUTES[chain][0]}" not in actor.flags
                    notes = f"rol_expedition_{ROUTES[chain][0]}_notes_modifier" in actor.modifiers
                    ending = "full" if CLAIMED[chain] in actor.flags else "partial" if notes else "failure"
                    endings[ending] += 1
                    if ending == "full" and chain != "naxos":
                        assert len([a for a in actor.artifacts if not a.artifact_type.startswith("rol_counterfeit")]) == 1
                    if ending != "full":
                        assert not [a for a in actor.artifacts if not a.artifact_type.startswith("rol_counterfeit")]
                    if "rol_expedition_companion_settlement_pending" in actor.flags:
                        assert model.condition(get(model.decisions["rol_settle_expedition_pact_decision"], "is_shown"), actor)
                    continue
                actor.queue.sort(key=lambda q: q[0])
                day, event, context = actor.queue.pop(0)
                model.advance(actor, day, definition)
                event_definition = model.dispatch(actor, event, context)
                actor.trace.append(event)
                if event_definition is None:
                    discarded.add(event)
                    pending.append(actor)
                    continue
                eligible = [v for k, _, v in event_definition if k == "option" and
                            model.condition(optional(v, "trigger", []), actor)]
                if optional(event_definition, "hidden") == "yes":
                    pending.append(actor)
                    continue
                assert eligible, f"no available choice at {event}: {actor.trace}"
                for option in eligible:
                    name = get(option, "name")
                    options_seen.add((event, name))
                    for outcome in model.alternatives(model.option_body(option), actor):
                        outcome.trace.append(name)
                        pending.append(outcome)
            report[chain] = {"states": states, "outcomes": dict(endings)}
        assert endings["full"] and endings["partial"] and endings["failure"], f"missing outcome in {chain}: {endings}"
    return report, options_seen, discarded


def plain_actor():
    return Person(activity=None, gold=4000, prestige=1000, martial=30, prowess=30,
                  learning=30, intrigue=30, stewardship=30, diplomacy=30,
                  house=Person(activity=None, label="house"), dynasty=Person(activity=None, label="dynasty"))


def relic(actor, artifact_type):
    item = Person(activity=None, owner=actor, artifact_type=artifact_type, label=artifact_type)
    actor.artifacts.append(item)
    return item


def start_use(model, actor, object_number, choice=1):
    model.decide(actor, "rol_arrange_relic_use_decision")
    return drive(model, actor, {"rol_relic_use.0001": f"rol_relic_use.0001.{object_number}",
                               f"rol_relic_use.100{object_number}": f"rol_relic_use.100{object_number}.{choice}"},
                 stop_before="rol_relic_use.0003")


def check_system_paths(model):
    evidence = []
    # Every original main option and every paid first-stage entrance gets a witness.
    for chain in ROUTES:
        actor, definition = start_route(model, chain, company=False,
                                        actor=plain_actor())
        # Earned expertise is a pre-existing character state, not granted by start.
        actor.traits.add("rol_relic_seeker")
        actor.xp["rol_research"] = 60
        actor = drive(model, actor, {f"rol_quest_{chain}.1000": "rol_expedition_expert_route_option"}, definition)
        assert CLAIMED[chain] in actor.flags, f"expert entrance failed: {chain}"
    evidence.append("5 expert entrances -> native first-stage progress -> full settlement/reflection")

    # Partial -> actual cooldown expiry -> consumes only same-region notes -> retry.
    for chain in ROUTES:
        actor, definition = start_route(model, chain, stat=5)
        actor = drive(model, actor, definition=definition)
        route = ROUTES[chain][0]
        notes = f"rol_expedition_{route}_notes_modifier"
        assert notes in actor.modifiers and CLAIMED[chain] not in actor.flags
        assert not model.condition(get(definition, "can_start_showing_failures_only"), actor)
        model.advance(actor, actor.day + 731)
        for attribute in ("learning", "martial", "prowess", "intrigue", "stewardship", "diplomacy"):
            setattr(actor, attribute, 30)
        actor, definition = start_route(model, chain, actor=actor)
        assert notes not in actor.modifiers and actor.activity["rol_expedition_journal_bonus"] == 5
        actor = drive(model, actor, definition=definition)
        assert CLAIMED[chain] in actor.flags
    evidence.append("5 partial outcomes -> cooldown -> notes consumed once -> full retry")

    # Ten real menu routes, time gate, defer/reopen, record/publish/retire and loss.
    types = ("rol_blade_of_mars", "rol_nibelung_star_sphere", "rol_astrolabe_of_ocean", "rol_ash_forged_mask")
    for object_number in range(1, 6):
        for choice in (1, 2):
            for ending in ("a", "b", "c", "retire", "lost"):
                actor = plain_actor()
                if object_number <= 4: relic(actor, types[object_number - 1])
                else: actor.flags.add(CLAIMED["naxos"])
                actor = start_use(model, actor, object_number, choice)
                assert actor.gold == 3950 and "rol_relic_use_pending" in actor.flags
                assert not model.condition(get(model.decisions["rol_review_relic_use_decision"], "is_shown"), actor)
                assert not model.condition(get(model.decisions["rol_arrange_relic_use_decision"], "is_valid_showing_failures_only"), actor)
                if ending == "retire":
                    model.decide(actor, "rol_retire_relic_use_decision")
                    actor = drive(model, actor, {"rol_relic_use.0004": f"rol_relic_use.0004.{object_number}"})
                else:
                    if ending == "lost":
                        if object_number <= 4:
                            item = actor.artifacts[0]
                            item.owner = plain_actor()
                            item.scopes = {"owner": item.owner}
                            model.run(get(model.on_actions["rol_relic_changed_owner_on_action"], "effect"), item)
                        else: actor.flags.discard(CLAIMED["naxos"])
                    option = "d" if ending == "lost" else ending
                    actor = drive(model, actor, {"rol_relic_use.0003": f"rol_relic_use.0003.{option}"})
                    if ending == "c":
                        assert "rol_relic_use_pending" in actor.flags
                        model.decide(actor, "rol_review_relic_use_decision")
                        actor = drive(model, actor, {"rol_relic_use.0003": "rol_relic_use.0003.a"})
                assert "rol_relic_use_pending" not in actor.flags, f"use {object_number}/{choice}/{ending} stuck"
                assert sum(actor.xp.values()) == (10 if ending in ("a", "c") else 0)
    evidence.append("10 use modes: menu -> 181-day event -> record/publish/defer+reopen/retire/loss (50 witnesses)")

    # Research links must work without owning the destination county.
    for object_number, artifact_type, use_choice, chain, chart, option in (
        (2, types[1], 1, "sevilla", "rol_star_observations_modifier", "rol_archive_sevilla_route_option"),
        (3, types[2], 1, "naxos", "rol_ocean_routes_modifier", "rol_archive_naxos_route_option"),
    ):
        actor = plain_actor()
        relic(actor, artifact_type)
        actor = start_use(model, actor, object_number, use_choice)
        actor = drive(model, actor, {"rol_relic_use.0003": "rol_relic_use.0003.a"})
        assert chart in actor.modifiers and not actor.titles
        actor, definition = start_route(model, chain, actor=actor, discover=False)
        actor = drive(model, actor, {f"rol_quest_{chain}.1000": option}, definition)
        assert chart not in actor.modifiers and CLAIMED[chain] in actor.flags
    evidence.append("2 use records -> discovery without destination title -> 40-gold chart route -> full reward")

    # Real fragment decisions, both levels, each challenge success/failure and loss.
    for route, artifact_type, decision, modifier in (
        ("rome", types[0], "mars", "rol_blade_fragment"),
        ("munich", types[1], "nibelung", "rol_nibelung_fragment"),
        ("sevilla", types[2], "astrolabe", "rol_astrolabe_fragment"),
        ("carthage", types[3], "ash", "rol_ash_fragment"),
    ):
        for challenge in ("a", "b", "c"):
            actor = plain_actor()
            relic(actor, artifact_type)
            actor.flags.add(CLAIMED[route])
            name = f"rol_seek_{decision}_fragment_decision"
            for level in (1, 2):
                model.decide(actor, name)
                day, event, context = actor.queue.pop(0)
                model.advance(actor, day)
                definition = model.dispatch(actor, event, context)
                selected = next(v for k, _, v in definition if k == "option" and get(v, "name") == f"rol_relic_fragment.0001.{challenge}")
                outcomes = list(model.alternatives(model.option_body(selected), actor))
                assert len(outcomes) == 2
                success, failure = outcomes
                assert f"{modifier}_{level}_modifier" in success.artifacts[0].modifiers
                assert not model.condition(model.triggers["rol_fragment_any_route_trigger"], failure)
                assert "rol_fragment_expedition_failure_modifier" in failure.modifiers
                actor = drive(model, success)
                model.options_seen.add((event, get(selected, "name")))
                assert not model.condition(model.triggers["rol_fragment_any_route_trigger"], actor)
                if level == 1: model.advance(actor, actor.day + 731)
            assert not model.condition(get(model.decisions[name], "is_shown"), actor), "third fragment upgrade remains shown"
        actor = plain_actor()
        item = relic(actor, artifact_type)
        actor.flags.add(CLAIMED[route])
        model.decide(actor, f"rol_seek_{decision}_fragment_decision")
        item.owner = plain_actor()
        actor = drive(model, actor, {"rol_relic_fragment.0001": "rol_relic_fragment.0001.d"})
        assert not actor.artifacts[0].modifiers and "rol_fragment_target" not in actor.variables
    evidence.append("4 fragment decisions x 3 challenges x 2 levels: success/failure + transferred target closes")

    # Annual/title callbacks both discover; unavailable AI/dead callbacks do nothing.
    for tier, title in (("tier_county", "c_naxos"), ("tier_barony", "b_thera"), ("tier_barony", "b_qartajana")):
        actor = plain_actor()
        actor.titles.add(title)
        actor.scopes["title"] = {"tier": tier}
        model.run(get(model.on_actions["rol_relic_discovery_title_gain_on_action"], "effect"), actor)
        actor = drive(model, actor)
        flag = "rol_heard_carthage_legend" if title == "b_qartajana" else "rol_heard_naxos_legend"
        assert flag in actor.flags
    evidence.append("yearly discovery plus county/barony title-gain entrances")
    evidence.extend(check_inheritance_paths(model))
    return evidence


def check_inheritance_paths(model):
    evidence = []
    # Accumulate true rewards through real activity entrances on one character.
    actor = plain_actor()
    for chain in ROUTES:
        actor, definition = start_route(model, chain, actor=actor)
        actor = drive(model, actor, definition=definition)
        assert CLAIMED[chain] in actor.flags
    assert len(actor.artifacts) == 4
    assert "rol_legend_circle_0001_reward_claimed" in actor.flags
    assert "rol_legend_circle_0002_reward_claimed" in actor.flags
    assert actor.dynasty.prestige == 1700  # initial 200 + 500 + 1000, no preparation bonus
    for ending in ("0001", "0002"):
        assert model.dispatch(actor, "rol_legend_circle." + ending, dict(actor.scopes)) is None
    evidence.append("5 complete activities on one host -> four/fivefold circle paid once -> no duplicate reward")

    # Artifact ROOT -> new-owner recipient ROOT; gift/inheritance clears only uses.
    for choice in ("a", "b", "c"):
        donor = plain_actor()
        item = relic(donor, "rol_blade_of_mars")
        item.modifiers = {"rol_blade_of_mars_modifier": None, "rol_blade_fragment_1_modifier": None,
                          "rol_relic_tier_legendary_modifier": None, "rol_relic_use_1_field_modifier": None}
        item.variables["rol_relic_legacy_transfer_count"] = 1
        heir = plain_actor()
        heir.flags = set(CLAIMED.values()) - {CLAIMED["rome"]}
        heir.artifacts = [item]
        item.owner = heir
        item.scopes = {"owner": heir, "previous_owner": donor}
        model.run(get(model.on_actions["rol_relic_changed_owner_on_action"], "effect"), item)
        assert item.variables["rol_relic_legacy_transfer_count"] == 2
        assert "rol_relic_use_1_field_modifier" not in item.modifiers
        assert {"rol_blade_of_mars_modifier", "rol_blade_fragment_1_modifier", "rol_relic_tier_legendary_modifier"} <= item.modifiers.keys()
        assert CLAIMED["rome"] in heir.flags and not donor.queue
        heir = drive(model, heir, {"rol_relic_legacy.0003": "rol_relic_legacy.0003." + choice})
        assert not ("rol_legacy_transition_choice_open" in heir.flags)
        assert "rol_legend_circle_0002_reward_claimed" in heir.flags
        assert sum(k.startswith("rol_relic_legacy_") for k in heir.modifiers) == 1
    evidence.append("artifact owner callback -> new-owner legacy choices -> circle; base/tier/fragments retained")

    # Naxos inheritance is an explicit paid choice from an actual dead predecessor.
    for choice in ("a", "b"):
        donor = plain_actor()
        heir = plain_actor()
        donor.player_heir = heir
        donor.flags.add(CLAIMED["naxos"])
        model.run(get(model.on_actions["rol_naxos_death_on_action"], "effect"), donor)
        donor.alive = False
        heir = drive(model, heir, {"rol_relic_legacy.0103": "rol_relic_legacy.0103." + choice})
        source = heir.scopes["rol_naxos_predecessor"]
        assert "rol_naxos_inheritance_answered" in source.flags
        assert (CLAIMED["naxos"] in heir.flags) == (choice == "a")
        assert heir.gold == (3900 if choice == "a" else 4000)
        assert heir.prestige == (500 if choice == "a" else 1000)
        assert model.dispatch(heir, "rol_relic_legacy.0103", dict(heir.scopes)) is None
    evidence.append("Naxos death callback -> heir accept/decline -> single answered credential")

    # A real contracted expedition dies before any progress; its original partner
    # and unconsumed records reach an heir who is still AI during the callback.
    for choice in ("a", "b", "c", "d"):
        donor, definition = start_route(model, "rome", company=True)
        donor = drive(model, donor, {"rol_expedition_companion.0001": "rol_expedition_companion.0001.b"},
                      definition, stop_before="rol_quest_rome.1000")
        assert donor.variables["rol_expedition_companion_role"] == 2
        donor.modifiers["rol_star_observations_modifier"] = 10
        donor.modifiers["rol_expedition_mars_notes_modifier"] = 10
        donor.xp["rol_research"] = 100
        donor.traits.add("rol_relic_seeker")
        heir = plain_actor()
        heir.ai = True
        donor.player_heir = heir
        model.run(get(model.on_actions["rol_archive_death_on_action"], "effect"), donor)
        donor.alive = False
        heir.ai = False
        if choice == "d": donor.variables["rol_bequest_partner"].alive = False
        heir = drive(model, heir, {"rol_archive.0001": "rol_archive.0001.b",
                                  "rol_archive.0002": "rol_archive.0002." + choice})
        assert not heir.xp and "rol_relic_seeker" not in heir.traits
        if choice == "c":
            assert model.condition(model.triggers["rol_archive_has_pacts_trigger"], heir)
            model.decide(heir, "rol_review_inherited_pacts_decision")
            heir = drive(model, heir, {"rol_archive.0002": "rol_archive.0002.a"})
        assert not model.condition(model.triggers["rol_archive_has_pacts_trigger"], heir)
        model.decide(heir, "rol_review_inherited_records_decision")
        heir = drive(model, heir, {"rol_archive.0001": "rol_archive.0001.a"})
        assert heir.modifiers["rol_star_observations_modifier"] == 5
        assert heir.modifiers["rol_expedition_mars_notes_modifier"] == 5
        assert "rol_heard_astrolabe_legend" in heir.flags and not heir.xp
        assert not model.condition(model.triggers["rol_archive_has_cargo_trigger"], heir)
        # Inherited observations actually unlock and complete the destination.
        heir, definition = start_route(model, "sevilla", actor=heir, discover=False)
        heir = drive(model, heir, {"rol_quest_sevilla.1000": "rol_archive_sevilla_route_option"}, definition)
        assert CLAIMED["sevilla"] in heir.flags
    evidence.append("active companion death -> AI heir snapshot -> adopt/decline/defer/dead partner -> pay original (0 inherited XP)")
    evidence.append("inherited records defer -> decision reopen -> five-year copies -> actual cross-chain activity completes")

    # Each annual pulse leaf enters a visible event or an intentional no-event arm.
    for naxos in (False, True):
        actor = plain_actor()
        relic(actor, "rol_blade_of_mars")
        if naxos: actor.flags.add(CLAIMED["naxos"])
        alternatives = list(model.alternatives(get(model.on_actions["rol_relic_legacy_yearly_on_action"], "effect"), actor))
        assert len(alternatives) == (9 if naxos else 3)
        for witness in alternatives:
            for _, event, context in witness.queue:
                candidate = deepcopy(witness)
                candidate.queue = []
                definition = model.dispatch(candidate, event, context)
                assert definition is not None
                options = [v for k, _, v in definition if k == "option" and model.condition(optional(v, "trigger", []), candidate)]
                assert options
                for option in options:
                    next(model.alternatives(model.option_body(option), candidate))
                    model.options_seen.add((event, get(option, "name")))
    evidence.append("yearly legacy pulse -> all 4 holder/Naxos events -> both options and intentional no-event arms")
    check_recurring_windows(model)
    evidence.append("4 annual windows: lost qualification/insufficient funds/replay/old generation have no payout")
    check_stale_agreements(model)
    evidence.append("reopened companion window cannot pay/refuse/clear a later agreement; legacy pending pact remains payable")
    check_stale_rival_pacts(model)
    evidence.append("repeated pact with same rival: old choices/closure cannot consume the next agreement")
    check_neutral_paths(model)
    evidence.extend(check_new_expansion_paths(model))
    return evidence


def check_stale_rival_pacts(model):
    for ending in ("a", "b", "c", "lost"):
        actor = plain_actor()
        rival = Person(activity=None, label="same-rival")
        actor.variables["rol_rival_pact_partner"] = rival
        actor.flags.add("rol_rival_pact_choice_pending")
        actor.scopes["rol_expedition_rival"] = rival
        # Legacy record starts without a generation, initialized by the first event.
        definition = model.dispatch(actor, "rol_rival.1001", dict(actor.scopes))
        original = dict(actor.scopes)
        first = next(v for k, _, v in definition if k == "option" and get(v, "name").endswith(".a"))
        model.run(model.option_body(first), actor)
        assert "rol_rival_pact_choice_pending" not in actor.flags
        model.call("rol_rival_new_pact_effect", actor)
        actor.flags.add("rol_rival_pact_choice_pending")
        actor.variables["rol_rival_pact_partner"] = rival
        actor.scopes = original
        name = "rol_rival_context_lost_option" if ending == "lost" else "rol_rival.1001." + ending
        stale = next(v for k, _, v in definition if k == "option" and get(v, "name") == name)
        before = (actor.gold, actor.prestige, actor.stress, len(rival.opinions))
        model.run(model.option_body(stale), actor)
        assert before == (actor.gold, actor.prestige, actor.stress, len(rival.opinions))
        assert "rol_rival_pact_choice_pending" in actor.flags
        model.decide(actor, "rol_review_rival_pact_decision")
        actor = drive(model, actor)
        assert "rol_rival_pact_choice_pending" not in actor.flags
        if ending == "lost": model.options_seen.add(("rol_rival.1001", name))


def check_neutral_paths(model):
    for event in ("0001", "1001", "1002", "1003", "1004", "1005", "0004"):
        actor = plain_actor()
        actor.flags.add(CLAIMED["naxos"])
        for artifact_type in ("rol_blade_of_mars", "rol_nibelung_star_sphere", "rol_astrolabe_of_ocean", "rol_ash_forged_mask"):
            item = relic(actor, artifact_type)
            item.modifiers["rol_relic_use_1_field_modifier"] = None
        actor.scopes = {}
        model.choose(actor, "rol_relic_use." + event, "rol_relic_use.cancel")
        assert actor.gold == 4000 and not model.condition(model.triggers["rol_relic_use_pending_trigger"], actor)
        model.options_seen.add(("rol_relic_use." + event, "rol_relic_use.cancel"))
    actor = plain_actor()
    actor.flags.add("rol_archive_mars_notes")
    model.choose(actor, "rol_archive.0001", "rol_archive.0001.c")
    assert not model.condition(model.triggers["rol_archive_has_cargo_trigger"], actor)
    assert actor.gold == 4000 and actor.prestige == 1000
    model.options_seen.add(("rol_archive.0001", "rol_archive.0001.c"))
    actor, definition = start_route(model, "rome", company=True)
    actor.scopes["rol_expedition_rival"] = actor.attendees[1]
    actor.flags.add("rol_rival_route_mars")
    model.call("rol_rival_begin_encounter_effect", actor)
    rival_event = model.dispatch(actor, "rol_rival.1000", dict(actor.scopes))
    actor.scopes["rol_expedition_rival"].alive = False
    close = next(v for k, _, v in rival_event if k == "option" and get(v, "name") == "rol_rival_context_lost_option")
    assert model.condition(get(close, "trigger"), actor)
    model.run(model.option_body(close), actor)
    model.options_seen.add(("rol_rival.1000", get(close, "name")))
    actor = plain_actor()
    item = relic(actor, "rol_blade_of_mars")
    actor.scopes["rol_legacy_artifact"] = item
    event = model.dispatch(actor, "rol_relic_legacy.0003", dict(actor.scopes))
    old_context = dict(actor.scopes)
    item.owner = plain_actor()
    close = next(v for k, _, v in event if k == "option" and get(v, "name").endswith(".d"))
    assert model.condition(get(close, "trigger"), actor)
    model.run(model.option_body(close), actor)
    assert "rol_legacy_transition_choice_open" not in actor.flags
    model.options_seen.add(("rol_relic_legacy.0003", get(close, "name")))
    item.owner = actor
    model.advance(actor, 5 * 365 + 1)
    assert model.dispatch(actor, "rol_relic_legacy.0003", {"rol_legacy_artifact": item}) is not None
    actor.scopes = old_context
    for k, _, option in event:
        if k == "option": model.run(model.option_body(option), actor)
    assert "rol_legacy_transition_choice_open" in actor.flags


def check_stale_agreements(model):
    for same_partner in (False, True):
        for ending in ("a", "b", "c", "e"):
            actor = plain_actor()
            partner = Person(activity=None, label="original-companion")
            actor.variables.update(rol_expedition_companion_partner=partner,
                                   rol_expedition_companion_role=2,
                                   rol_expedition_companion_earned_xp=10)
            actor.flags.add("rol_expedition_companion_settlement_pending")
            definition = model.dispatch(actor, "rol_expedition_companion.0002", {})
            old_context = dict(actor.scopes)
            honour = next(v for k, _, v in definition if k == "option" and get(v, "name").endswith(".a"))
            model.run(model.option_body(honour), actor)
            assert not model.condition(model.triggers["rol_expedition_companion_pending_trigger"], actor)
            assert partner.gold == 250 and actor.xp["rol_exploration"] == 10
            new_partner = partner if same_partner else Person(activity=None, label="new-companion")
            actor.variables.update(rol_expedition_companion_partner=new_partner,
                                   rol_expedition_companion_role=2,
                                   rol_expedition_companion_earned_xp=10)
            model.call("rol_expedition_companion_new_agreement_effect", actor)
            actor.flags.add("rol_expedition_companion_settlement_pending")
            actor.scopes = old_context
            before = (actor.gold, actor.prestige, actor.stress, dict(actor.xp),
                      new_partner.gold, len(new_partner.opinions))
            stale = next(v for k, _, v in definition if k == "option" and get(v, "name").endswith("." + ending))
            model.run(model.option_body(stale), actor)
            assert before == (actor.gold, actor.prestige, actor.stress, actor.xp,
                              new_partner.gold, len(new_partner.opinions)), "stale agreement paid a new contract"
            assert model.condition(model.triggers["rol_expedition_companion_pending_trigger"], actor)
            if ending == "e": model.options_seen.add(("rol_expedition_companion.0002", get(stale, "name")))
            model.decide(actor, "rol_settle_expedition_pact_decision")
            actor = drive(model, actor)
            assert not model.condition(model.triggers["rol_expedition_companion_pending_trigger"], actor)


def check_recurring_windows(model):
    for suffix, name, price in (("0001", "duty", 0), ("0002", "study", 50),
                                ("0101", "review", 40), ("0102", "veteran", 75)):
        event = "rol_relic_legacy." + suffix
        for case in ("valid", "lost", "poor", "old_generation"):
            actor = plain_actor()
            if name in ("duty", "study"): relic(actor, "rol_blade_of_mars")
            else: actor.flags.add(CLAIMED["naxos"])
            definition = model.dispatch(actor, event, {})
            assert definition is not None
            old_context = dict(actor.scopes)
            if case == "lost":
                if actor.artifacts: actor.artifacts[0].owner = plain_actor()
                else: actor.flags.discard(CLAIMED["naxos"])
            elif case == "poor": actor.gold = 0
            elif case == "old_generation":
                model.advance(actor, 5 * 365 + 1)
                assert model.dispatch(actor, event, {}) is not None
                actor.scopes = old_context
            first, second, close = [v for k, _, v in definition if k == "option"]
            before = (actor.gold, actor.prestige, actor.piety, actor.stress)
            model.run(model.option_body(first), actor)
            paid = case == "valid" or (case == "poor" and price == 0)
            after = (actor.gold, actor.prestige, actor.piety, actor.stress)
            assert (after != before) == paid, f"{event}/{case}: stale annual payout"
            model.run(model.option_body(first), actor)
            assert after == (actor.gold, actor.prestige, actor.piety, actor.stress), f"{event}: replay reward"
            if case == "old_generation":
                model.run(model.option_body(close), actor)
                assert f"rol_legacy_{name}_choice_open" in actor.flags, f"{event}: old window consumes new one"
                assert not model.condition(get(first, "trigger"), actor)
            if case == "lost":
                assert model.condition(get(close, "trigger"), actor)
                model.run(model.option_body(close), actor)
                assert f"rol_legacy_{name}_choice_open" not in actor.flags
                model.options_seen.add((event, get(close, "name")))
            if case == "poor" and price:
                assert model.condition(get(second, "trigger"), actor), f"{event}: broke player cannot close"
                model.run(model.option_body(second), actor)
                assert f"rol_legacy_{name}_choice_open" not in actor.flags


def event_reachability(model):
    """Follow event/effect calls with actual macro arguments from production roots."""
    reached, examined = set(), set()

    def visit(nodes):
        for key, _, value in nodes:
            if key == "trigger_event":
                event = get(value, "id") if isinstance(value, list) else value
                assert "$" not in event, f"unbound successor: {event}"
                assert event in model.events, f"missing successor: {event}"
                if event not in reached:
                    reached.add(event)
                    visit(model.events[event])
            elif key in model.effects:
                params = {k: v for k, _, v in value} if isinstance(value, list) else {}
                marker = (key, tuple(sorted(params.items())))
                if marker not in examined:
                    examined.add(marker)
                    from_nodes = model._parameters(model.effects[key], value) if isinstance(value, list) else model.effects[key]
                    visit(from_nodes)
            elif key == "on_actions":
                for action, _, _ in value:
                    assert action in model.on_actions, f"unresolved on_action: {action}"
                    marker = ("on_action", action)
                    if marker not in examined:
                        examined.add(marker)
                        visit(model.on_actions[action])
            elif isinstance(value, list): visit(value)
    for definitions in (model.activities, model.decisions):
        for nodes in definitions.values(): visit(nodes)
    for native_action in ("yearly_playable_pulse", "on_title_gain", "on_death", "on_artifact_changed_owner"):
        visit(model.on_actions[native_action])
    missing = sorted(set(model.events) - reached)
    assert not missing, f"events without a production entrance: {missing}"
    return len(reached)


def run_audit(root, game):
    model = PathModel(root, game)
    routes, choices, discarded = explore_quests(model)
    systems = check_system_paths(model)
    if __package__:
        from .rol_rival_relationship_contracts import check_rival_relationship_contract
        from .rol_family_archive_contracts import check_family_archive_contract
        from .rol_observation_commission_contracts import check_observation_commission_contract
        from .rol_companion_mastery_contracts import check_companion_mastery_contract
        from .rol_exploration_mastery_contracts import check_exploration_mastery_contract
        from .rol_expedition_feedback_contracts import check_expedition_feedback_contract
        from .rol_scholar_growth_contracts import check_scholar_growth_contract
        from .rol_relic_preservation_contracts import check_relic_preservation_contract
        from .rol_archive_status_contracts import check_archive_status_contract
        from .rol_field_companion_growth_contracts import check_field_companion_growth_contract
        from .rol_envoy_accord_contracts import check_envoy_accord_contract
    else:
        from rol_rival_relationship_contracts import check_rival_relationship_contract
        from rol_family_archive_contracts import check_family_archive_contract
        from rol_observation_commission_contracts import check_observation_commission_contract
        from rol_companion_mastery_contracts import check_companion_mastery_contract
        from rol_exploration_mastery_contracts import check_exploration_mastery_contract
        from rol_expedition_feedback_contracts import check_expedition_feedback_contract
        from rol_scholar_growth_contracts import check_scholar_growth_contract
        from rol_relic_preservation_contracts import check_relic_preservation_contract
        from rol_archive_status_contracts import check_archive_status_contract
        from rol_field_companion_growth_contracts import check_field_companion_growth_contract
        from rol_envoy_accord_contracts import check_envoy_accord_contract
    errors = []
    rival_witnesses = check_rival_relationship_contract(root, errors, model=model)
    family_records = check_family_archive_contract(root, errors, model=model)
    commission_witnesses = check_observation_commission_contract(root, errors, model=model)
    negotiation_witnesses = check_companion_mastery_contract(root, errors, model=model)
    exploration_witnesses = check_exploration_mastery_contract(root, errors, model=model)
    feedback_types = check_expedition_feedback_contract(root, errors, model=model)
    scholar_witnesses = check_scholar_growth_contract(root, errors, model=model)
    preservation_witnesses = check_relic_preservation_contract(root, errors, model=model)
    archive_status_witnesses = check_archive_status_contract(root, errors, model=model)
    field_growth_witnesses = check_field_companion_growth_contract(root, errors, model=model)
    envoy_accord_witnesses = check_envoy_accord_contract(root, errors, model=model)
    assert not errors, "; ".join(errors)
    systems.append(f"{rival_witnesses} identity-bound rival witnesses; {family_records} house knowledge records with catalogue/print consumers")
    systems.append(f"{commission_witnesses} original-scholar commissions; {negotiation_witnesses} guard-credit and {exploration_witnesses} master-detour witnesses")
    systems.append(f"{feedback_types} committed log types retain host/contributor identity and reject invalid/replayed actions")
    systems.append(f"{scholar_witnesses} scholar-growth witnesses: original commissioned observer, attending help, tier boundaries and exact odds")
    systems.append(f"{preservation_witnesses} restoration witnesses: seven genuine sources, original job/house, mutually exclusive rewards and paid heir editions")
    systems.append(f"{archive_status_witnesses} read-only archive status witnesses: live house, personal sources, real catalogue/printing/expiry and bilingual wiring")
    systems.append(f"{field_growth_witnesses} original guard/envoy field-work witnesses: personal growth, six-job threshold, five dynamic fees and replay isolation")
    systems.append(f"{envoy_accord_witnesses} trained-envoy accords: original envoy/rival snapshots, single mediation and actual later cooperative reunion")
    choices |= model.options_seen
    all_choices = {(event, get(v, "name")) for event, nodes in model.events.items()
                   for k, _, v in nodes if k == "option"}
    assert not (all_choices - choices), f"uncovered event options: {sorted(all_choices - choices)}"
    return {"evidence": "finite source model; CK3 runtime not executed", "routes": routes,
            "event_options": len(choices), "random_branches": len(model.coverage),
            "system_paths": systems, "reachable_events": event_reachability(model),
            "discarded_after_close": sorted(discarded)}


def check_new_expansion_paths(model):
    evidence = []
    # 1. Fragment resonance choices (.0002.a, .0002.b, .0002.c) and dynamic odds
    for res_opt, mod_name in (
        ("a", "rol_fragment_resonance_might_modifier"),
        ("b", "rol_fragment_resonance_wisdom_modifier"),
        ("c", "rol_fragment_resonance_court_modifier"),
    ):
        actor = plain_actor()
        relic(actor, "rol_blade_of_mars")
        actor.flags.add(CLAIMED["rome"])
        model.decide(actor, "rol_seek_mars_fragment_decision")
        actor = drive(
            model,
            actor,
            {
                "rol_relic_fragment.0001": "rol_relic_fragment.0001.c",
                "rol_relic_fragment.0002": f"rol_relic_fragment.0002.{res_opt}",
            },
        )
        assert mod_name in actor.modifiers
        assert "rol_fragment_masterwork_surplus_modifier" in actor.modifiers
    evidence.append("fragment dynamic odds + masterwork c branch + 3 resonance attunements (.0002.a/b/c)")

    # 2. Mid-expedition crisis remedy (.0010.a press on, .0010.b salvage partial, .0010.c retreat, .0010.d stale close)
    for remedy_choice in ("a", "b", "c"):
        actor = plain_actor()
        actor.traits.add("rol_relic_seeker")
        actor.xp["rol_exploration"] = 60
        actor, definition = start_route(model, "munich", stat=25, actor=actor)
        # Advance arrival 0990 -> 1000
        day, ev, ctx = actor.queue.pop(0)
        model.advance(actor, day, definition)
        defn = model.dispatch(actor, ev, ctx)
        opt = next(v for k, _, v in defn if k == "option")
        actor = next(model.alternatives(model.option_body(opt), actor))
        # At 1000, take failure branch of option a to reach 1011
        day, ev, ctx = actor.queue.pop(0)
        model.advance(actor, day, definition)
        defn = model.dispatch(actor, ev, ctx)
        opt_a = next(v for k, _, v in defn if k == "option" and get(v, "name") == "rol_quest_munich.1000.a")
        outcomes = list(model.alternatives(model.option_body(opt_a), actor))
        failed_stage = outcomes[1]
        actor = drive(
            model,
            failed_stage,
            {"rol_expedition_growth.0010": f"rol_expedition_growth.0010.{remedy_choice}"},
            definition=definition,
        )
        if remedy_choice == "a":
            assert CLAIMED["munich"] in actor.flags
        elif remedy_choice == "b":
            assert "rol_expedition_nibelung_notes_modifier" in actor.modifiers
        else:
            assert "rol_recent_nibelung_quest_failure" not in actor.flags  # cleared at 1090
    # Stale .0010.d close
    stale_actor = plain_actor()
    stale_actor.flags.add("rol_expedition_remedy_pending")
    stale_actor.variables["rol_expedition_remedy_generation"] = 1
    stale_actor.scopes["rol_expedition_remedy_generation"] = 1
    model.choose(stale_actor, "rol_expedition_growth.0010", "rol_expedition_growth.0010.d")
    assert "rol_expedition_remedy_pending" not in stale_actor.flags
    model.options_seen.add(("rol_expedition_growth.0010", "rol_expedition_growth.0010.d"))
    evidence.append("mid-expedition crisis remedy (.0010.a press on / .0010.b partial salvage / .0010.c retreat / .0010.d close)")

    # 3. Rival recruitment (.1001.d) + Trusted companion reunion bonus
    actor = plain_actor()
    rival = Person(activity=None, label="recruited-rival", learning=22, prowess=22, diplomacy=22, playable=False)
    actor.variables["rol_rival_pact_partner"] = rival
    actor.flags.add("rol_rival_pact_choice_pending")
    actor.scopes["rol_expedition_rival"] = rival
    model.choose(actor, "rol_rival.1001", "rol_rival.1001.d")
    model.options_seen.add(("rol_rival.1001", "rol_rival.1001.d"))
    assert actor.variables.get("rol_expedition_trusted_companion") is rival
    assert actor.xp.get("rol_negotiation", 0) == 10
    evidence.append("rival recruitment (.1001.d) -> trusted companion + negotiation XP")

    # 4. Multi-Relic Resonance decision & event (rol_harmonize_relics_decision -> rol_relic_legacy.0010.a/b/c + invalid close)
    for res_choice, items, mod_name in (
        ("a", ("rol_blade_of_mars", "rol_ash_forged_mask"), "rol_resonance_imperial_might_modifier"),
        ("b", ("rol_nibelung_star_sphere", "rol_astrolabe_of_ocean"), "rol_resonance_cosmic_chart_modifier"),
        ("c", ("rol_blade_of_mars", "rol_nibelung_star_sphere"), "rol_resonance_sovereign_awe_modifier"),
    ):
        actor = plain_actor()
        for item_type in items:
            relic(actor, item_type)
        model.decide(actor, "rol_harmonize_relics_decision")
        actor = drive(model, actor, {"rol_relic_legacy.0010": f"rol_relic_legacy.0010.{res_choice}"})
        assert mod_name in actor.modifiers
        assert "rol_legacy_resonance_choice_open" not in actor.flags
    # Invalid close on 0010 when relics are lost before clicking
    lost_actor = plain_actor()
    r1 = relic(lost_actor, "rol_blade_of_mars")
    r2 = relic(lost_actor, "rol_ash_forged_mask")
    model.decide(lost_actor, "rol_harmonize_relics_decision")
    r1.owner = plain_actor()
    r2.owner = plain_actor()
    lost_actor = drive(model, lost_actor, {"rol_relic_legacy.0010": "rol_legacy_unavailable_option"})
    model.options_seen.add(("rol_relic_legacy.0010", "rol_legacy_unavailable_option"))
    assert "rol_legacy_resonance_choice_open" not in lost_actor.flags
    evidence.append("multi-relic harmonization decision -> .0010.a/b/c doctrines + invalid close")
    if __package__:
        from .rol_expansion_regressions import check_expansion_regressions
    else:
        from rol_expansion_regressions import check_expansion_regressions
    evidence.extend(check_expansion_regressions(model, Person, plain_actor, start_route, drive, CLAIMED))
    return evidence


if __name__ == "__main__":
    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args.add_argument("--game", type=Path, default=GAME)
    args.add_argument("--report", type=Path)
    options = args.parse_args()
    result = run_audit(options.root, options.game)
    if options.report:
        options.report.parent.mkdir(parents=True, exist_ok=True)
        options.report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
