"""Exploration mastery exchanges the existing crisis fee for personal stress."""
from pathlib import Path


def check_exploration_mastery_contract(root: Path, errors: list[str], model=None) -> int:
    if __package__:
        from .rol_path_contracts import PathModel, Person, get, start_route, plain_actor, drive, CLAIMED, ROUTES, signature
    else:
        from rol_path_contracts import PathModel, Person, get, start_route, plain_actor, drive, CLAIMED, ROUTES, signature

    count = 0
    try:
        model = model if model is not None else PathModel(root)
        crisis = "rol_expedition_growth.0010"
        name = "rol_expedition_master_exploration_option"
        choice = next(v for k, _, v in model.events[crisis] if k == "option" and get(v, "name") == name)
        body = model.option_body(choice)
        paid = next(v for k, _, v in model.events[crisis] if k == "option" and get(v, "name") == crisis + ".a")
        paid_body = model.option_body(paid)

        def explorer():
            actor = plain_actor()
            actor.traits.add("rol_relic_seeker")
            actor.xp["rol_exploration"] = 100
            return actor

        def arm(chain="munich", loss=10, actor=None):
            actor, definition = start_route(model, chain, actor=actor if actor is not None else explorer(),
                                            discover=actor is None)
            # Exercise the native loss/recovery math independently of a given roll.
            initial = actor.activity["activity_special_type_progression"]
            actor.activity["activity_special_type_progression"] -= loss
            model.call("rol_expedition_record_trial_failure_effect", actor, {"LOSS": str(loss)})
            model.call("rol_expedition_try_remedy_or_fail_effect", actor, {"CHAIN": chain})
            assert model.condition(model.triggers["rol_expedition_remedy_window_valid_trigger"], actor)
            return actor, definition, initial

        # Actual activity -> first real failed roll -> crisis -> original remaining
        # stage events and Tier4 reward. No synthetic completion or reward helper.
        for chain in ROUTES:
            actor, definition = start_route(model, chain, actor=explorer())
            trial_event = "rol_quest_" + chain + ".1000"
            actor = drive(model, actor, definition=definition, stop_before=trial_event)
            due, event, context = actor.queue.pop(0)
            assert event == trial_event
            model.advance(actor, due, definition)
            trial = model.dispatch(actor, event, context)
            trial_choice = next(v for k, _, v in trial if k == "option" and get(v, "name") == trial_event + ".a")
            failures = [a for a in model.alternatives(model.option_body(trial_choice), actor)
                        if any(q[1].endswith(".1011") for q in a.queue)]
            assert len(failures) == 1, f"{chain}: failed real first trial no longer produces its crisis route"
            actor = drive(model, failures[0], definition=definition, stop_before=crisis)
            due, event, context = actor.queue.pop(0)
            assert event == crisis
            model.advance(actor, due, definition)
            assert model.dispatch(actor, event, context) is not None
            actor.gold = 0
            before_progress = actor.activity["activity_special_type_progression"]
            actual_loss = actor.activity["rol_expedition_trial_failure_loss"]
            before_stress, before_xp = actor.stress, dict(actor.xp)
            model.choose(actor, crisis, name)
            model.options_seen.add((crisis, name))
            assert actor.gold == 0 and actor.stress == before_stress + 25 and actor.xp == before_xp, f"{chain}: mastery cost or immediate XP changed"
            assert actor.activity["activity_special_type_progression"] == before_progress + actual_loss + 10, f"{chain}: mastery fails to restore only this trial's loss"
            settled = signature(actor)
            model.run(body, actor)
            model.run(paid_body, actor)
            assert signature(actor) == settled, f"{chain}: mastery/paid continuation replays the same crisis"
            actor = drive(model, actor, definition=definition)
            assert CLAIMED[chain] in actor.flags, f"{chain}: mastery continuation cannot reach its real Tier4 outcome"
            count += 1

        # Both prices recover exactly 0/5/10 points while retaining a later +3
        # interlude; the alternate payment cannot be claimed after either one.
        for loss in (0, 5, 10):
            for option, cost, stress in ((name, 0, 25), (crisis + ".a", 50, 10)):
                actor, _, initial = arm(loss=loss)
                model.run([("activity_special_type_progression_tiny", "=", "yes")], actor, "activity")
                before_gold, before_stress, before_xp = actor.gold, actor.stress, dict(actor.xp)
                model.choose(actor, crisis, option)
                assert actor.activity["activity_special_type_progression"] == initial + 3 + 10, "continuation erases another interlude or adds excess recovery"
                assert (actor.gold, actor.stress, actor.xp) == (before_gold - cost, before_stress + stress, before_xp), "continuation's fee, stress or XP differs from the selected cost"
                settled = signature(actor)
                model.run(body, actor)
                model.run(paid_body, actor)
                assert signature(actor) == settled, "the two prices do not share the same once-only crisis"
                count += 1

        for balance in (49, 0, -10):
            actor, _, _ = arm()
            actor.gold = balance
            assert model.condition(get(choice, "trigger"), actor), "mastery is incorrectly blocked by lack of cash or debt"
            assert not model.condition(get(paid, "trigger"), actor), "the old paid option ignores insufficient cash"
            before = signature(actor)
            model.run(paid_body, actor)
            assert signature(actor) == before, "paid continuation mutates an unaffordable crisis"
            model.choose(actor, crisis, name)
            assert actor.gold == balance and "rol_expedition_remedy_pending" not in actor.flags
            count += 1

        for reason in ("99xp", "wrong_track", "no_trait", "missing_loss", "old_generation",
                       "missing_generation", "closed_activity", "closed_growth", "wrong_host", "dead_host"):
            actor, _, _ = arm()
            if reason == "99xp": actor.xp["rol_exploration"] = 99
            elif reason == "wrong_track": actor.xp = {"rol_research": 100, "rol_negotiation": 100}
            elif reason == "no_trait": actor.traits.clear()
            elif reason == "missing_loss": actor.activity.pop("rol_expedition_trial_failure_loss")
            elif reason == "old_generation": actor.scopes["rol_expedition_remedy_generation"] -= 1
            elif reason == "missing_generation": actor.scopes.pop("rol_expedition_remedy_generation")
            elif reason == "closed_activity": actor.activity["rol_relic_quest_closed"] = 1
            elif reason == "closed_growth": actor.activity["rol_expedition_growth_open"] = 0
            elif reason == "wrong_host": actor.scopes["host"] = Person(activity=None)
            elif reason == "dead_host": actor.alive = False
            assert not model.condition(get(choice, "trigger"), actor), f"{reason}: invalid mastery choice remains available"
            before = signature(actor)
            model.run(body, actor)
            assert signature(actor) == before, f"{reason}: invalid mastery spends stress or advances a later crisis"
            count += 1

        # A prior same-region window must not spend the next expedition's crisis.
        actor, definition, _ = arm()
        old_context = dict(actor.scopes)
        model.choose(actor, crisis, name)
        model.call("rol_munich_quest_fail_now_effect", actor)
        model.advance(actor, actor.day + 731, definition)
        actor, _, _ = arm(actor=actor)
        assert actor.variables["rol_expedition_remedy_generation"] == old_context["rol_expedition_remedy_generation"] + 1
        current_context = dict(actor.scopes)
        # Keep the new activity context to prove that the old number itself fails;
        # an old closed activity is already rejected independently above.
        actor.scopes = {**actor.scopes, "rol_expedition_remedy_generation": old_context["rol_expedition_remedy_generation"]}
        before = signature(actor)
        model.run(body, actor)
        model.run(paid_body, actor)
        assert signature(actor) == before, "old continuation window spends the next expedition's crisis"
        actor.scopes = current_context
        model.choose(actor, crisis, name)
        assert "rol_expedition_remedy_pending" not in actor.flags
        count += 1
        return count
    except (AssertionError, KeyError, ValueError, StopIteration, TypeError, AttributeError, OSError) as error:
        errors.append(f"exploration mastery contract: {error}")
        return 0


if __name__ == "__main__":
    issues = []
    total = check_exploration_mastery_contract(Path(__file__).resolve().parents[2], issues)
    for issue in issues:
        print(f"[FAIL] {issue}")
    if not issues:
        print(f"[OK] {total} exploration mastery scenarios: five real Tier4 routes, cost choice, loss preservation and replay")
    raise SystemExit(bool(issues))
