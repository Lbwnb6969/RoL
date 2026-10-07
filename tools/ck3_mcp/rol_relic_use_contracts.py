#!/usr/bin/env python3
"""Owned-item use lifecycle checks; finite source model, not a CK3 runtime test."""
from pathlib import Path

if __package__:
    from .rol_growth_contracts import Model, State, get, parse
else:
    from rol_growth_contracts import Model, State, get, parse


USES = (
    (1, "rol_blade_of_mars", ("field", "oath"), ("rol_exploration", "rol_negotiation"), ("brave", "just")),
    (2, "rol_nibelung_star_sphere", ("study", "display"), ("rol_research", "rol_negotiation"), ("diligent", "gregarious")),
    (3, "rol_astrolabe_of_ocean", ("navigation", "teaching"), ("rol_exploration", "rol_research"), ("brave", "diligent")),
    (4, "rol_ash_forged_mask", ("dread", "restoration"), ("rol_negotiation", "rol_research"), ("ambitious", "patient")),
    (5, None, ("field", "training"), ("rol_exploration", "rol_exploration"), ("brave", "diligent")),
)


def check_relic_use_contract(root: Path, errors: list[str]) -> int:
    try:
        model = Model(root)
        load = lambda name: parse((root / name).read_text(encoding="utf-8-sig"))
        events = load("events/rol_relic_use_events.txt")
        backgrounds = load("common/event_backgrounds/rol_event_backgrounds.txt")
        for name, _, event in events:
            if name == "namespace": continue
            get(backgrounds, get(get(event, "override_background"), "reference"))
        modifiers = load("common/modifiers/rol_relic_use_modifiers.txt")
        decisions = load("common/decisions/rol_relic_use_decisions.txt")
        menu = get(events, "rol_relic_use.0001")
        payoff = get(events, "rol_relic_use.0003")
        retire = get(events, "rol_relic_use.0004")
        assert len([v for k, _, v in menu if k == "option"]) == 6, "use menu omits a relic or cancel"
        recovery = get(decisions, "rol_review_relic_use_decision")
        assert get(get(recovery, "effect"), "rol_relic_use_reopen_effect") == "yes", "results recovery bypasses the captured generation"
        queue = get(model.effects["rol_relic_use_begin_project_effect"], "trigger_event")
        assert get(queue, "id") == "rol_relic_use.0003" and get(queue, "days") == "181", "payoff is not queued after waiting-flag expiry"
        assert get(get(payoff, "trigger"), "rol_relic_use_generation_matches_trigger") == "yes", "queued payoff has no generation guard"
        defer = next(v for k, _, v in payoff if k == "option" and get(v, "name").endswith(".c"))
        assert {k for k, _, _ in defer} == {"name", "trigger", "custom_tooltip"}, "defer pays or changes the job"
        transfer = get(load("common/on_action/rol_relic_legacy_on_actions.txt"), "rol_relic_changed_owner_on_action")
        cleanup = get(transfer, "effect")[0]
        assert get(cleanup[2], "rol_relic_use_clear_artifact_modes_effect") == "yes", "transfer does not clear old deployment before player-only processing"

        def setup(kind, type_):
            host = State(activity=None)
            artifact = State(activity=None, artifact_type=type_ or "", owner=host,
                             modifiers={"original_relic_modifier": None, "fragment_modifier": None})
            decoy = State(activity=None, artifact_type="rol_counterfeit_blade", owner=host)
            host.artifacts = [decoy, artifact]
            if kind == 5: host.flags.add("rol_naxos_unit_unlocked")
            else:
                model.run(get(get(events, f"rol_relic_use.100{kind}"), "immediate"), host)
                assert host.scopes["rol_relic_use_candidate"] is artifact, "configuration selected a different/counterfeit item"
            return host, artifact, decoy

        def mature(host):
            # Simulate expiry for contract checks, not game clock/flag-order validation.
            host.flags.discard("rol_relic_use_waiting")

        for kind, type_, names, tracks, personalities in USES:
            config = get(events, f"rol_relic_use.100{kind}")
            options = [v for k, _, v in config if k == "option"]
            assert len(options) == 3, f"{kind}: two uses and free cancel required"
            assert {k for k, _, _ in options[2]} == {"name"}, f"{kind}: cancel modifies state"
            end_option = next(v for k, _, v in retire if k == "option" and get(v, "name") == f"rol_relic_use.0004.{kind}")
            for index, (name, track, personality) in enumerate(zip(names, tracks, personalities)):
                mode = kind * 2 - 1 + index
                modifier = f"rol_relic_use_{kind}_{name}_modifier"
                get(modifiers, modifier)
                effect = "rol_relic_use_select_naxos_effect" if kind == 5 else "rol_relic_use_select_artifact_effect"
                params = {k: v for k, _, v in get(options[index], effect)}
                assert params["MODE"] == str(mode) and params["MODIFIER"] == modifier, f"{kind}: mode modifier mismatch"
                if type_: assert params["TYPE"] == type_, f"{kind}: wrong artifact type"
                host, artifact, decoy = setup(kind, type_)
                host.traits.add(personality)
                other = f"rol_relic_use_{kind}_{names[1-index]}_modifier"
                (host if kind == 5 else artifact).modifiers[other] = None
                model.call(effect, host, params)
                model.call(effect, host, params)
                target = host if kind == 5 else artifact
                assert host.gold == 150 and modifier in target.modifiers and other not in target.modifiers, "use not exclusive or charge replayed"
                assert not decoy.modifiers and (kind == 5 or set(artifact.modifiers) == {"original_relic_modifier", "fragment_modifier", modifier}), "mode affects another item or removes original/fragment modifiers"
                assert host.events == ["rol_relic_use.0003"], "choice queues multiple payoffs"
                assert host.flag_durations["rol_relic_use_waiting"] == [("days", "180")] and host.flag_durations["rol_relic_use_cooldown"] == [("years", "1")], "wait or cooldown differs from terms"
                if kind == 5: assert host.modifiers[modifier] == 3, "Naxos benefit does not expire after three years"
                else: assert host.variables["rol_relic_use_artifact"] is artifact and not host.modifiers, "artifact use leaks a character modifier or stores another item"
                model.call("rol_relic_use_record_experience_effect", host)
                model.call("rol_relic_use_publish_effect", host)
                model.call("rol_relic_use_close_invalid_effect", host)
                model.call("rol_relic_use_reopen_effect", host)
                assert not host.xp and host.prestige == 200 and "rol_relic_use_pending" in host.flags and len(host.events) == 1, "forced early review settles or queues results"
                mature(host)
                model.call("rol_relic_use_reopen_effect", host)
                assert host.scopes["rol_relic_use_generation"] == host.variables["rol_relic_use_generation"], "recovery loses generation"
                model.call("rol_relic_use_record_experience_effect", host)
                model.call("rol_relic_use_record_experience_effect", host)
                model.call("rol_relic_use_publish_effect", host)
                assert host.xp == {track: 10} and host.stress == 15 and host.prestige == 200, "experience, matching stress or alternative payoff repeats"
                assert "rol_relic_use_pending" not in host.flags and modifier in target.modifiers, "settlement keeps pending or removes use benefit"
                model.call(effect, host, params)
                assert host.gold == 150, "settlement bypasses cooldown"

                # A later project cannot be settled or closed by the old event.
                old_generation = host.scopes["rol_relic_use_generation"]
                host.flags.discard("rol_relic_use_cooldown")
                model.call(effect, host, params)
                mature(host)
                new_generation = host.variables["rol_relic_use_generation"]
                assert new_generation == old_generation + 1, "project generation is not monotonic"
                host.scopes["rol_relic_use_generation"] = old_generation
                model.call("rol_relic_use_record_experience_effect", host)
                model.call("rol_relic_use_close_invalid_effect", host)
                assert host.xp == {track: 10} and "rol_relic_use_pending" in host.flags, "old event cashes/closes a newer project"
                host.scopes["rol_relic_use_generation"] = new_generation
                model.call("rol_relic_use_publish_effect", host)
                model.call("rol_relic_use_publish_effect", host)
                assert host.prestige == 300 and host.xp == {track: 10}, "public outcome repeats or also grants XP"

                for problem in ("unaffordable", "lost_before_selection", "lost_after_selection", "changed_mode", "retire"):
                    actor, item, _ = setup(kind, type_)
                    if problem == "unaffordable": actor.gold = 49
                    if problem == "lost_before_selection":
                        if kind == 5: actor.flags.remove("rol_naxos_unit_unlocked")
                        else: item.owner = State(activity=None)
                    model.call(effect, actor, params)
                    if problem in ("unaffordable", "lost_before_selection"):
                        assert "rol_relic_use_pending" not in actor.flags and modifier not in (actor if kind == 5 else item).modifiers, "invalid entry is charged or creates benefits"
                        continue
                    if problem == "lost_after_selection":
                        if kind == 5: actor.flags.remove("rol_naxos_unit_unlocked")
                        else:
                            item.owner = State(activity=None)
                            model.run([cleanup], actor, item)
                            assert not model.condition(model.triggers["rol_relic_has_use_mode_trigger"], actor, item), "transfer leaves old mode on new owner's relic"
                    elif problem == "changed_mode": (actor if kind == 5 else item).modifiers.pop(modifier)
                    else:
                        model.run([n for n in end_option if n[0].startswith("rol_relic_use_retire_")], actor)
                        assert modifier not in (actor if kind == 5 else item).modifiers and "rol_relic_use_pending" not in actor.flags, "retirement leaves benefit or project"
                    mature(actor)
                    model.call("rol_relic_use_record_experience_effect", actor)
                    model.call("rol_relic_use_publish_effect", actor)
                    model.call("rol_relic_use_close_invalid_effect", actor)
                    assert actor.gold == 150 and not actor.xp and actor.prestige == 200 and "rol_relic_use_pending" not in actor.flags and "rol_relic_use_cooldown" in actor.flags, "invalidated/retired project awards, refunds or skips cooldown"

        # Ending an earlier deployment must not cancel a different current project.
        host, blade, _ = setup(1, "rol_blade_of_mars")
        blade.modifiers["rol_relic_use_1_field_modifier"] = None
        sphere = State(activity=None, artifact_type="rol_nibelung_star_sphere", owner=host)
        host.artifacts.append(sphere)
        host.scopes["rol_relic_use_candidate"] = sphere
        model.call("rol_relic_use_select_artifact_effect", host, {"TYPE": "rol_nibelung_star_sphere", "MODE": 3, "MODIFIER": "rol_relic_use_2_study_modifier"})
        model.call("rol_relic_use_retire_artifact_effect", host, {"TYPE": "rol_blade_of_mars"})
        assert host.variables["rol_relic_use_artifact"] is sphere and "rol_relic_use_pending" in host.flags and "rol_relic_use_2_study_modifier" in sphere.modifiers, "retiring another artifact closes current work"
        assert not model.condition(model.triggers["rol_relic_has_use_mode_trigger"], host, blade), "earlier deployment remains after retirement"
        return 10
    except (AssertionError, ValueError, KeyError, OSError, TypeError, IndexError, StopIteration, AttributeError) as error:
        errors.append(f"relic use contract: {error}")
        return 0


if __name__ == "__main__":
    import sys
    issues = []
    count = check_relic_use_contract(Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2], issues)
    for issue in issues: print(f"[FAIL] {issue}")
    if not issues: print(f"[OK] Relic use contracts: {count} modes, ownership, wait, generation/replay, replacement and retirement (model only)")
    raise SystemExit(bool(issues))
