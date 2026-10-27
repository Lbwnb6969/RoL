"""Behavioral regression witnesses for the Gemini integration; no CK3 input."""
from itertools import permutations

if __package__:
    from .rol_growth_contracts import get
else:
    from rol_growth_contracts import get


def walk(nodes):
    for node in nodes:
        yield node
        if isinstance(node[2], list):
            yield from walk(node[2])


def check_expansion_regressions(model, Person, plain_actor, start_route, drive, claimed):
    evidence = []

    def option(event, name):
        return next(v for k, _, v in model.events[event] if k == "option" and get(v, "name") == name)

    def rewards(a):
        return (a.gold, a.prestige, a.piety, a.stress, a.learning_lifestyle_xp,
                dict(a.xp), set(a.flags), dict(a.modifiers))

    def arm(a, chain, loss=10):
        model.call("rol_expedition_record_trial_failure_effect", a, {"LOSS": str(loss)})
        model.call("rol_expedition_try_remedy_or_fail_effect", a, {"CHAIN": chain})
        assert model.condition(model.triggers["rol_expedition_remedy_window_valid_trigger"], a)

    for chain, base in (("rome", 30), ("munich", 35), ("naxos", 30), ("sevilla", 35), ("carthage", 35)):
        starts = []
        for preparation in ("standard", "supreme"):
            a = plain_actor()
            a.preparation = preparation
            a, _ = start_route(model, chain, actor=a)
            assert a.activity["activity_special_type_progression"] == base + (5 if preparation == "supreme" else 0)
            starts.append(a)
        assert starts[0].gold - starts[1].gold == 1600
        assert starts[0].stress - starts[1].stress == 15
    evidence.append("all 5 native on_start hooks: selected preparation cost, supreme +5 progress / -15 stress")

    # Derive the loss from every actual RNG outcome that dispatches a crisis.
    losses = []
    for event, nodes in model.events.items():
        if not event.startswith("rol_quest_"):
            continue
        for k, _, branches in walk(nodes):
            if k != "random_list":
                continue
            for _, _, branch in branches:
                if not isinstance(branch, list):
                    continue
                leaves = list(walk(branch))
                if not any(key == "trigger_event" and isinstance(body, list) and
                           get(body, "id").endswith((".1011", ".1021", ".1031", ".1041"))
                           for key, _, body in leaves):
                    continue
                native = [key for key, _, _ in leaves if key in model.native]
                loss = 10 if "activity_special_type_progression_negative_major" in native else 5 if "activity_special_type_progression_negative" in native else 0
                records = [body for key, _, body in leaves if key == "rol_expedition_record_trial_failure_effect"]
                assert len(records) == 1 and float(get(records[0], "LOSS")) == loss, event
                losses.append(loss)
    assert len(losses) == 64 and set(losses) == {0, 5, 10}
    for loss in set(losses):
        a, _ = start_route(model, "munich", actor=plain_actor())
        a.traits.add("rol_relic_seeker")
        a.xp["rol_research"] = 60
        a.activity["activity_special_type_progression"] = 35 - loss
        arm(a, "munich", loss)
        # An interlude that runs while the crisis is queued must retain its +3.
        a.activity["activity_special_type_progression"] += 3
        model.call("rol_expedition_remedy_press_on_effect", a)
        assert a.activity["activity_special_type_progression"] == 48
        before = rewards(a)
        model.call("rol_expedition_remedy_press_on_effect", a)
        assert rewards(a) == before
    evidence.append("64 real failure losses recorded; 0/-5/-10 recover to +10 without erasing interlude progress or replay")

    for qualification in ("novice", "expert", "notes", "trusted"):
        a, _ = start_route(model, "munich", actor=plain_actor())
        a.traits.add("rol_relic_seeker")
        if qualification == "expert":
            a.xp["rol_exploration"] = 60
        elif qualification == "notes":
            a.activity["rol_expedition_journal_bonus"] = 5
        elif qualification == "trusted":
            partner = Person(activity=a.activity, label="trusted", playable=False)
            a.attendees.append(partner)
            a.variables.update(rol_expedition_companion_partner=partner, rol_expedition_trusted_companion=partner)
            a.activity["rol_expedition_companion_open"] = 1
        arm(a, "munich")
        press = model.condition(model.triggers["rol_expedition_remedy_press_on_qualified_trigger"], a)
        assert press == (qualification != "novice")
        if qualification == "novice":
            before = rewards(a)
            model.call("rol_expedition_remedy_press_on_effect", a)
            assert rewards(a) == before and "rol_expedition_remedy_pending" in a.flags
    evidence.append("novice can salvage/retreat; press-on requires 60XP, consumed same-region notes or attending trusted partner")

    for chain, cap in (("rome", 69), ("munich", 54), ("naxos", 59), ("sevilla", 54), ("carthage", 54)):
        a, _ = start_route(model, chain, actor=plain_actor())
        a.traits.add("rol_relic_seeker")
        a.activity["activity_special_type_progression"] = 100
        arm(a, chain)
        model.call("rol_expedition_remedy_salvage_partial_effect", a)
        assert a.activity["activity_special_type_progression"] == cap
        assert a.variables["rol_recent_relic_result_tier"] == 3
        assert not a.artifacts and claimed[chain] not in a.flags
        assert a.variables["rol_expedition_growth_pending_xp"] == 20
    evidence.append("all 5 salvage paths cap at Tier3, retain 20XP/notes, never award unique relic/completion")

    a, _ = start_route(model, "munich", actor=plain_actor())
    a.traits.add("rol_relic_seeker")
    arm(a, "munich")
    old_context = dict(a.scopes)
    model.call("rol_munich_quest_fail_now_effect", a)
    a.activity = None
    a.scopes = {}
    a.available = True
    a.queue = []
    a.phase_end = None
    a, _ = start_route(model, "rome", actor=a)
    arm(a, "rome")
    current_context = dict(a.scopes)
    before = rewards(a)
    a.scopes = old_context
    for k, _, body in model.events["rol_expedition_growth.0010"]:
        if k == "option":
            model.run(model.option_body(body), a)
    a.scopes = current_context
    assert rewards(a) == before
    assert model.condition(model.triggers["rol_expedition_remedy_window_valid_trigger"], a)
    evidence.append("old crisis payouts AND neutral close preserve a different expedition's pending crisis")

    # The native involved_activity entry reconstructs the real host/activity
    # scopes without borrowing an obsolete window's captured context.
    a, definition = start_route(model, "munich", actor=plain_actor())
    a.traits.add("rol_relic_seeker")
    a.activity["rol_expedition_remedy_used"] = 1
    a.flags.add("rol_expedition_remedy_pending")
    a.scopes = {}
    a.queue = []
    model.decide(a, "rol_review_expedition_crisis_decision")
    assert a.scopes["host"] is a and a.scopes["activity"] is a.activity
    assert model.condition(model.triggers["rol_expedition_remedy_window_valid_trigger"], a)
    press = option("rol_expedition_growth.0010", "rol_expedition_growth.0010.a")
    assert not model.condition(get(press, "trigger"), a), "legacy crisis invents unknown loss"
    a = drive(model, a, {"rol_expedition_growth.0010": "rol_expedition_growth.0010.b"}, definition)
    assert claimed["munich"] not in a.flags and "rol_expedition_nibelung_notes_modifier" in a.modifiers
    a = plain_actor()
    a.flags.add("rol_fragment_upgrade_pending")
    model.decide(a, "rol_review_fragment_resonance_decision")
    a = drive(model, a, {"rol_relic_fragment.0002": "rol_relic_fragment.0002.b"})
    assert a.xp["rol_research"] == 5 and "rol_fragment_upgrade_pending" not in a.flags
    evidence.append("legacy unnumbered crisis/fragment recovery decisions reconstruct original qualification without extra uses/rewards")

    # Challenge windows, not only their later resonance, belong to one fragment job.
    a = plain_actor()
    blade = Person(activity=None, owner=a, artifact_type="rol_blade_of_mars", label="blade")
    sphere = Person(activity=None, owner=a, artifact_type="rol_nibelung_star_sphere", label="sphere")
    a.artifacts.extend((blade, sphere))
    a.flags.update((claimed["rome"], claimed["munich"]))
    model.decide(a, "rol_seek_mars_fragment_decision")
    day, event, context = a.queue.pop(0)
    model.advance(a, day)
    model.dispatch(a, event, context)
    old_context = dict(a.scopes)
    model.choose(a, event, "rol_relic_fragment.0001.d")
    model.decide(a, "rol_seek_nibelung_fragment_decision")
    current_context = dict(a.scopes)
    a.scopes = old_context
    before = rewards(a), dict(a.variables), list(a.queue)
    for k, _, candidate in model.events[event]:
        if k == "option":
            model.run(model.option_body(candidate), a)
    assert (rewards(a), a.variables, a.queue) == before
    model.choose(a, event, "rol_relic_fragment.0001.e")
    model.options_seen.add((event, "rol_relic_fragment.0001.e"))
    assert "rol_fragment_route_nibelung" in a.flags and a.variables["rol_fragment_target"] is sphere
    a.scopes = current_context
    a = drive(model, a)
    assert "rol_nibelung_fragment_1_modifier" in a.artifacts[1].modifiers and not a.artifacts[0].modifiers
    a = plain_actor()
    blade = Person(activity=None, owner=a, artifact_type="rol_blade_of_mars", label="legacy blade")
    a.artifacts.append(blade)
    a.flags.add("rol_fragment_route_mars")
    a.variables["rol_fragment_target"] = blade
    before_gold = a.gold
    model.decide(a, "rol_review_fragment_expedition_decision")
    a = drive(model, a)
    assert "rol_blade_fragment_1_modifier" in a.artifacts[0].modifiers and a.gold == before_gold
    assert a.variables["rol_fragment_route_generation"] == 1
    evidence.append("fragment challenge old windows cannot pay/upgrade/cancel a later relic job; legacy recovery keeps the original item and fee")

    for choice in ("a", "b", "c"):
        a = plain_actor()
        item = Person(activity=None, owner=a, artifact_type="rol_blade_of_mars", label="blade")
        a.artifacts.append(item)
        a.flags.add(claimed["rome"])
        model.decide(a, "rol_seek_mars_fragment_decision")
        a = drive(model, a, {"rol_relic_fragment.0001": "rol_relic_fragment.0001.c"}, stop_before="rol_relic_fragment.0002")
        day, event, context = a.queue.pop(0)
        model.advance(a, day)
        model.dispatch(a, event, context)
        old_context = dict(a.scopes)
        # Pending rewards cannot be overwritten by starting another fragment job.
        assert not model.condition(get(model.decisions["rol_seek_mars_fragment_decision"], "is_valid_showing_failures_only"), a)
        pending_generation = a.variables["rol_fragment_resonance_generation"]
        model.call("rol_relic_fragment_begin_effect", a, {
            "TYPE": "rol_blade_of_mars", "ROUTE": "mars", "LAST_MODIFIER": "rol_blade_fragment_2_modifier"})
        assert a.variables["rol_fragment_resonance_generation"] == pending_generation
        assert "rol_fragment_target" not in a.variables
        body = model.option_body(option(event, event + "." + choice))
        model.run(body, a)
        paid = rewards(a)
        for k, _, candidate in model.events[event]:
            if k == "option":
                model.run(model.option_body(candidate), a)
        assert rewards(a) == paid
        # A real second upgrade, not just another arbitrary pending flag.
        model.advance(a, a.day + 731)
        model.decide(a, "rol_seek_mars_fragment_decision")
        a = drive(model, a, {"rol_relic_fragment.0001": "rol_relic_fragment.0001.c"}, stop_before=event)
        day, _, context = a.queue.pop(0)
        model.advance(a, day)
        model.dispatch(a, event, context)
        new_context = dict(a.scopes)
        a.scopes = old_context
        before = rewards(a)
        model.run(body, a)
        assert rewards(a) == before
        a.scopes = new_context
        model.run(body, a)
        assert "rol_fragment_upgrade_pending" not in a.flags
        assert a.xp[{"a": "rol_exploration", "b": "rol_research", "c": "rol_negotiation"}[choice]] == 10
    # Give the newly added neutral option a state witness as well.
    a = plain_actor()
    a.flags.add("rol_fragment_upgrade_pending")
    a.variables["rol_fragment_resonance_generation"] = 2
    a.scopes["rol_fragment_resonance_generation"] = 1
    model.choose(a, "rol_relic_fragment.0002", "rol_legacy_unavailable_option")
    assert "rol_fragment_upgrade_pending" in a.flags
    model.options_seen.add(("rol_relic_fragment.0002", "rol_legacy_unavailable_option"))
    evidence.append("all 3 fragment resonance rewards execute once; real second upgrade rejects old windows; neutral close preserves new pending")

    core = set(claimed.values()) | {"rol_legend_circle_revealed", "rol_legend_circle_fivefold_revealed"}
    for order in permutations(("0001", "0002")):
        a = plain_actor()
        a.flags.update(core)
        before = a.dynasty.prestige
        for suffix in order:
            event = "rol_legend_circle." + suffix
            model.run(model.option_body(option(event, event + ".a")), a)
        assert a.dynasty.prestige - before == 1500
        assert set(a.dynasty.modifiers) == {"rol_legend_circle_dynasty_modifier", "rol_legend_circle_dynasty_fivefold_modifier"}
        assert "rol_legend_circle_fivefold_modifier" in a.modifiers and "rol_legend_circle_conqueror_modifier" not in a.modifiers
        paid = rewards(a), a.dynasty.prestige, dict(a.house.modifier_expires)
        for suffix in order:
            event = "rol_legend_circle." + suffix
            model.run(model.option_body(option(event, event + ".a")), a)
        assert (rewards(a), a.dynasty.prestige, a.house.modifier_expires) == paid
    a = plain_actor()
    a.modifiers.update(rol_legend_circle_conqueror_modifier=None, rol_legend_circle_fivefold_modifier=None)
    before = a.dynasty.prestige
    for _ in range(2):
        model.call("rol_legend_circle_migrate_effect", a)
    assert a.dynasty.prestige == before
    assert "rol_legend_circle_conqueror_modifier" not in a.modifiers
    assert {"rol_legend_circle_0001_reward_claimed", "rol_legend_circle_0002_reward_claimed"} <= a.flags
    evidence.append("both circle claim orders pay 1500 dynasty prestige once; legacy double personal buffs migrate without new rewards")
    return evidence
