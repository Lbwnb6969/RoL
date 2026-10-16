"""Exercise settlement/replay in the finite source model, not the CK3 engine."""
from pathlib import Path
from copy import deepcopy

if __package__:
    from .rol_growth_contracts import Model, State, parse, get, ROUTES
    from .rol_compatibility_contracts import walk
else:
    from rol_growth_contracts import Model, State, parse, get, ROUTES
    from rol_compatibility_contracts import walk


def snapshot(actor):
    return deepcopy((actor.variables, actor.flags, actor.modifiers, actor.prestige,
                     actor.piety, actor.gold, actor.events, actor.progress_effects,
                     actor.activity, actor.house.modifiers if actor.house else None,
                     actor.dynasty.prestige if actor.dynasty else None))


def check_quest_lifecycle_contract(root: Path, errors: list[str]) -> int:
    try:
        load = lambda path: parse((root / path).read_text(encoding="utf-8-sig"))
        model = Model(root)
        for filename in ("rol_relic_framework_effects.txt", "rol_legend_circle_effects.txt", "rol_expedition_preparation_effects.txt"):
            model.effects.update({k: v for k, _, v in load("common/scripted_effects/" + filename)})
        framework = load("common/scripted_effects/rol_relic_framework_effects.txt")
        for key, _, value in walk(framework):
            if key == "add_activity_log_entry":
                assert get(value, "character") == "scope:host", "quest log treats callback ROOT as a character"
            if key == "send_interface_toast":
                assert get(value, "left_icon") == "this", "character toast leaks an activity ROOT"
        model.triggers.update({k: v for k, _, v in load("common/scripted_triggers/rol_legend_circle_triggers.txt")})
        for chain, (route, filename, cooldown) in ROUTES.items():
            effects = load(f"common/scripted_effects/rol_quest_{chain}_effects.txt")
            model.effects.update({k: v for k, _, v in effects})
            kind, _, body = load("common/activities/activity_types/" + filename)[0]
            guard, context, stage = f"rol_{chain}_quest_active_trigger", "rol_relic_context_" + route, f"rol_{chain}_stage_count"
            events = load(f"events/rol_quest_{chain}_events.txt")
            for event, _, definition in events:
                if "." in event and not event.endswith(".1090"):
                    assert get(get(definition, "trigger"), guard) == "yes", f"{event}: delayed event bypasses its route guard"
                    if not event.endswith(".1001"):
                        for key, _, option in definition:
                            if key != "option": continue
                            # Event dispatch triggers do not protect already open windows.
                            wrapper = get(option, "if")
                            assert get(wrapper, "limit") == [(guard, "=", "yes")], f"{event}: stale choice bypasses its route guard"
            terminal = get(events, f"rol_quest_{chain}.1001")
            assert get(get(get(terminal, "immediate"), "if"), "limit") == [(guard, "=", "yes")]
            assert get(get(get(body, "on_start"), "scope:host"), "rol_relic_quest_begin_effect") == "yes"
            for hook in ("on_invalidated", "on_complete"):
                assert get(get(get(body, hook), "scope:host"), f"rol_{chain}_quest_fail_now_effect") == "yes"

            def actor(progress=40, old=False):
                result = State(flags={context, f"rol_heard_{route}_legend"}, variables={stage: 1},
                               activity={"_activity_type": kind, "activity_special_type_progression": progress},
                               house=State(activity=None), dynasty=State(activity=None))
                result.scopes["host"] = result
                if not old:
                    model.call("rol_relic_quest_begin_effect", result)
                    model.call("rol_expedition_growth_begin_effect", result, {"ROUTE": route})
                return result

            outcomes = [f"rol_{chain}_quest_{ending}_finalize_effect" for ending in ("success", "partial")]
            actions = outcomes + [f"rol_{chain}_quest_progress_effect", f"rol_{chain}_quest_fail_now_effect"]
            for ending, xp, notes in zip(outcomes, (30, 20), (False, True)):
                result = actor(progress=100 if xp == 30 else 40)
                model.call(ending, result)
                paid = snapshot(result)
                for replay in actions:
                    model.call(replay, result)
                    assert snapshot(result) == paid, f"{chain}: closed expedition replays {replay}"
                assert result.activity["rol_relic_quest_closed"] == 1 and result.activity["rol_expedition_growth_open"] == 0
                assert result.variables["rol_expedition_growth_pending_xp"] == xp
                assert (f"rol_expedition_{route}_notes_modifier" in result.modifiers) == notes
                assert result.progress_effects.count(("progress_activity_phase_after", "1")) == 1
                assert model.condition(get(body, "is_valid"), result), f"{chain}: settled quest invalidates before its phase finishes"
                if notes:
                    assert "rol_apply_expedition_preparation_success_bonus_effect" not in {k for k, _, _ in get(get(effects, ending), "if")}, "partial outcome pays full triumph bonus"
            for issue in ("no_activity", "foreign_activity", "wrong_host", "no_context", "closed", "dead_host"):
                result = actor()
                if issue == "no_activity": result.activity = None
                elif issue == "foreign_activity": result.activity["_activity_type"] = "activity_feast"
                elif issue == "wrong_host": result.scopes["host"] = State()
                elif issue == "no_context": result.flags.clear()
                elif issue == "closed": result.activity["rol_relic_quest_closed"] = 1
                else: result.alive = False
                before = snapshot(result)
                for name in actions: model.call(name, result)
                model.run(get(terminal, "immediate"), result)
                for event, _, definition in events:
                    if "." not in event or event.endswith((".1090", ".1001")): continue
                    for key, _, value in definition:
                        if key == "option": model.run([("if", "=", get(value, "if"))], result)
                        if key == "immediate": model.run(value, result)
                assert snapshot(result) == before, f"{chain}: {issue} pays or alters another activity"
            for completed in (0, 1):
                result = actor()
                result.variables[stage] = completed
                model.run(get(body, "on_invalidated"), result)
                assert result.variables.get("rol_expedition_growth_pending_xp", 0) == (10 if completed else 0)
                assert stage not in result.variables and context not in result.flags
                assert model.condition(get(body, "is_valid"), result), f"{chain}: failure cooldown cancels its scheduled finish"
                before = snapshot(result)
                model.run(get(body, "on_invalidated"), result)
                assert snapshot(result) == before, f"{chain}: invalidation pays twice"
            # Native invalidation ROOT is the activity, not the host character.
            host = actor()
            callback = State(activity=host.activity, scopes={"host": host})
            assert model.condition(model.triggers[guard], callback, host), f"{chain}: guard confuses callback ROOT with its host"
            model.run(get(body, "on_invalidated"), callback)
            assert host.variables["rol_expedition_growth_pending_xp"] == 10 and not callback.variables
            assert host.activity["rol_relic_quest_closed"] == 1 and context not in host.flags
            old = actor(old=True)
            assert model.condition(model.triggers[guard], old), f"{chain}: missing marker breaks old active saves"
            model.call(outcomes[1], old)
            assert old.activity["rol_relic_quest_closed"] == 1 and "rol_expedition_growth_pending_xp" not in old.variables
            dead = actor()
            partner = State(activity=None)
            dead.variables.update(rol_expedition_companion_partner=partner, rol_expedition_companion_role=2)
            dead.flags.add("rol_expedition_companion_in_field")
            model.run(get(get(body, "on_host_death"), "scope:host"), dead)
            assert dead.variables["rol_expedition_companion_partner"] is partner and "rol_expedition_companion_in_field" in dead.flags
            assert "rol_expedition_growth_pending_xp" not in dead.variables and context not in dead.flags

        circles = load("events/rol_legend_circle_events.txt")
        core = {"rol_mars_blade_claimed", "rol_nibelung_sphere_claimed", "rol_naxos_unit_unlocked", "rol_astrolabe_of_ocean_claimed", "rol_ash_forged_mask_claimed", "rol_legend_circle_revealed", "rol_legend_circle_fivefold_revealed"}
        for suffix, modifier, reward in (("0001", "rol_legend_circle_conqueror_modifier", 500), ("0002", "rol_legend_circle_fivefold_modifier", 1000)):
            event = get(circles, "rol_legend_circle." + suffix)
            payoff = get(get(event, "option"), "hidden_effect")
            for old_paid in (False, True):
                result = State(flags=set(core), dynasty=State(activity=None), house=State(activity=None))
                if old_paid: result.modifiers[modifier] = None
                model.run(payoff, result)
                # A fresh fivefold claim also settles the independent fourfold
                # dynasty reward, regardless of which window was clicked first.
                assert result.dynasty.prestige == 200 + (0 if old_paid else reward + (500 if suffix == "0002" else 0))
                before = snapshot(result)
                model.run(payoff, result)
                assert snapshot(result) == before, f"circle {suffix}: repeat event refreshes rewards"
        trial = get(load("events/rol_quest_naxos_events.txt"), "rol_quest_naxos.1003")
        intrigue = next(v for k, _, v in trial if k == "option" and get(v, "name") == "rol_quest_naxos.1003.b")
        assert not any(k == "activity_special_type_progression_medium" for k, _, _ in walk(intrigue)), "high-intrigue success cannot reach Tier4"
        rival = get(load("events/rol_rival_events.txt"), "rol_rival.1001")
        choices = [v for k, _, v in rival if k == "option"][:3]
        for choice, option in enumerate(choices):
            for case in ("valid", "poor", "dead", "stale"):
                partner = State(activity=None, alive=case != "dead")
                result = State(activity=None, gold=49 if case == "poor" else 200,
                               flags={"rol_rival_pact_choice_pending"}, variables={"rol_rival_pact_partner": partner})
                result.scopes["rol_expedition_rival"] = State(activity=None) if case == "stale" else partner
                reward = [n for n in option if n[0] == "if"]
                model.run(reward, result)
                valid = case not in ("dead", "stale") and not (case == "poor" and choice == 0)
                assert result.prestige == 200 + ((100 if choice == 0 else 150 if choice == 1 else 0) if valid else 0)
                before = (result.prestige, result.gold, result.stress, set(result.flags), len(partner.opinions))
                model.run(reward, result)
                assert before == (result.prestige, result.gold, result.stress, result.flags, len(partner.opinions)), "rival pact pays twice"
                assert ("rol_rival_pact_choice_pending" in result.flags) != valid
        result = State(flags={"rol_rival_pact_choice_pending"}, variables={"rol_rival_pact_partner": State(alive=False)})
        model.call("rol_rival_reopen_pact_effect", result)
        assert not result.flags and not result.variables and not result.events, "dead pact cannot close through recovery"
        inheritance = get(load("events/rol_relic_legacy_events.txt"), "rol_relic_legacy.0103")
        options = [v for k, _, v in inheritance if k == "option"]
        for choice, option in enumerate(options):
            for case in ("valid", "no_source", "wrong_source", "poor", "already_answered", "already_unlocked"):
                predecessor = State(activity=None, alive=False, flags={"rol_naxos_unit_unlocked"})
                heir = State(activity=None, prestige=600, gold=99 if case == "poor" else 200)
                if case != "no_source": heir.scopes["rol_naxos_predecessor"] = predecessor
                if case == "wrong_source": predecessor.flags.clear()
                if case == "already_answered": predecessor.flags.add("rol_naxos_inheritance_answered")
                if case == "already_unlocked": heir.flags.add("rol_naxos_unit_unlocked")
                model.run([("if", "=", get(option, "if"))], heir)
                paid = case in ("valid", "poor") and (choice == 1 or case != "poor")
                assert heir.piety == (50 if paid and choice == 1 else 0), "Naxos decline pays outside its original inheritance"
                assert heir.gold == (100 if paid and choice == 0 else 99 if case == "poor" else 200), "Naxos inheritance ignores gold qualification"
                assert ("rol_naxos_inheritance_answered" in predecessor.flags) == (paid or case == "already_answered")
                before = snapshot(heir)
                model.run([("if", "=", get(option, "if"))], heir)
                assert snapshot(heir) == before, "Naxos inheritance answer pays twice"
        return len(ROUTES)
    except (AssertionError, ValueError, KeyError, OSError, TypeError, IndexError, AttributeError, StopIteration) as error:
        errors.append(f"quest lifecycle contract: {error}")
        return 0


if __name__ == "__main__":
    import sys
    issues = []
    count = check_quest_lifecycle_contract(Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2], issues)
    for issue in issues: print(f"[FAIL] {issue}")
    if not issues: print(f"[OK] Quest lifecycle: {count} routes; callback ROOT/host identity, wrong/closed scopes, replay, invalidation/death, old saves, circle/Naxos/rival rewards and high-stat progress (model only)")
    raise SystemExit(bool(issues))
