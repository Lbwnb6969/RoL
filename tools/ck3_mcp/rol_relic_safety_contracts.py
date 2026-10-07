"""Source-driven ownership, fee and replay checks; never a CK3 runtime test."""
from pathlib import Path
from rol_growth_contracts import Model, State, parse, get


def check_relic_safety_contract(root: Path, errors: list[str]) -> int:
    try:
        model = Model(root)
        load = lambda path: parse((root / path).read_text(encoding="utf-8-sig"))
        decisions = load("common/decisions/rol_fragment_decisions.txt")
        fragment = get(load("events/rol_relic_fragment_events.txt"), "rol_relic_fragment.0001")
        assert get(get(fragment, "trigger"), "rol_fragment_any_route_trigger") == "yes"
        for decision, _, body in decisions:
            assert get(get(body, "cost"), "gold") == "120", f"{decision}: native fee missing"
            params = dict((k, v) for k, _, v in get(get(body, "effect"), "rol_relic_fragment_begin_effect"))
            route, kind, last = params["ROUTE"], params["TYPE"], params["LAST_MODIFIER"]
            first = last.replace("_2_modifier", "_1_modifier")
            actor = State(activity=None)
            artifact = State(artifact_type=kind, owner=actor, modifiers={"base": None, "use": None})
            actor.artifacts = [State(artifact_type="decoy", owner=actor), artifact]
            model.call("rol_relic_fragment_begin_effect", actor, params)
            model.call("rol_relic_fragment_begin_effect", actor, params)
            assert actor.variables["rol_fragment_target"] is artifact and actor.events == ["rol_relic_fragment.0001"]
            model.call("rol_relic_fragment_success_effect", actor)
            model.call("rol_relic_fragment_success_effect", actor)
            assert first in artifact.modifiers and last not in artifact.modifiers and actor.prestige == 300
            assert "rol_fragment_target" not in actor.variables and "rol_fragment_route_" + route not in actor.flags
            assert actor.events.count("rol_relic_fragment.0002") == 1
            model.call("rol_relic_fragment_begin_effect", actor, params)
            model.call("rol_relic_fragment_success_effect", actor)
            model.call("rol_relic_fragment_begin_effect", actor, params)
            assert last in artifact.modifiers and actor.prestige == 500 and len(actor.events) == 4
            assert {"base", "use"} <= artifact.modifiers.keys(), "upgrade strips existing modifiers"
            for invalid in ("transfer", "missing", "type", "complete"):
                for outcome in ("success", "failure"):
                    actor = State(activity=None)
                    artifact = State(artifact_type=kind, owner=actor)
                    spare = State(artifact_type=kind, owner=actor)
                    actor.artifacts = [artifact, spare]
                    model.call("rol_relic_fragment_begin_effect", actor, params)
                    if invalid == "transfer": artifact.owner = State()
                    if invalid == "missing": actor.variables.pop("rol_fragment_target")
                    if invalid == "type": artifact.artifact_type = "decoy"
                    if invalid == "complete": artifact.modifiers[last] = None
                    model.call("rol_relic_fragment_" + outcome + "_effect", actor)
                    assert first not in artifact.modifiers and not spare.modifiers, "invalid project retargets/upgrades"
                    assert actor.prestige == 200 and actor.stress == 20 and len(actor.events) == 1
                    assert not model.condition(model.triggers["rol_fragment_any_route_trigger"], actor)
            actor = State(activity=None)
            artifact = State(artifact_type=kind, owner=actor)
            actor.artifacts = [artifact]
            model.call("rol_relic_fragment_begin_effect", actor, params)
            model.call("rol_relic_fragment_failure_effect", actor)
            model.call("rol_relic_fragment_failure_effect", actor)
            assert actor.stress == 40 and not artifact.modifiers and actor.prestige == 200
        options = [v for k, _, v in fragment if k == "option"]
        for option in options[:3]:
            assert get(get(option, "trigger"), "rol_fragment_target_valid_trigger") == "yes"
            assert get(get(get(option, "if"), "limit"), "rol_fragment_target_valid_trigger") == "yes"
        assert get(get(options[2], "trigger"), "gold") == "50"
        assert get(get(get(options[2], "if"), "limit"), "gold") == "50"
        assert get(options[3], "rol_clear_fragment_route_effect") == "yes"

        legacy = load("events/rol_relic_legacy_events.txt")
        transition = get(legacy, "rol_relic_legacy.0003")
        assert get(get(transition, "trigger"), "rol_legacy_selected_artifact_owned_trigger") == "yes"
        options = [v for k, _, v in transition if k == "option"]
        for choice in range(3):
            for case in ("valid", "transfer", "poor", "count2"):
                actor = State(activity=None, gold=99 if case == "poor" else 200)
                artifact = State(artifact_type="rol_blade_of_mars", owner=actor,
                                 variables={"rol_relic_legacy_transfer_count": 2 if case == "count2" else 0})
                actor.scopes["rol_legacy_artifact"] = artifact
                model.run(get(transition, "immediate"), actor)
                if case == "transfer": artifact.owner = State()
                # Public dynasty prestige is native, outside this finite model.
                if choice == 0 and case == "count2": continue
                reward = [n for n in options[choice] if n[0] == "if"]
                model.run(reward, actor)
                before = (actor.prestige, actor.gold, actor.stress, actor.learning_lifestyle_xp, dict(actor.modifiers))
                model.run(reward, actor)
                assert before == (actor.prestige, actor.gold, actor.stress, actor.learning_lifestyle_xp, actor.modifiers), "transition replays"
                valid = case != "transfer" and not (case == "poor" and choice == 2)
                assert actor.prestige == (275 if valid and choice == 0 else 200)
                assert actor.stress == (10 if valid and choice == 1 else 20)
                assert actor.learning_lifestyle_xp == ((250 if case == "count2" else 150) if valid and choice == 2 else 0)
                assert actor.gold == ((99 if case == "poor" else 200) - (100 if valid and choice == 2 else 0))
        actor = State(activity=None)
        artifact = State(artifact_type="rol_blade_of_mars", owner=actor)
        actor.artifacts = [artifact]
        model.call("rol_relic_legacy_debug_transition_effect", actor)
        assert actor.event_contexts[0][1]["rol_legacy_artifact"] is artifact
        ghost = State(activity=None)
        model.run(get(transition, "immediate"), ghost)
        assert not ghost.flags, "scope-free forced event opens qualification"
        for event_id, price in (("0002", 50), ("0101", 40), ("0102", 75)):
            option = next(v for k, _, v in get(legacy, "rol_relic_legacy." + event_id) if k == "option")
            assert get(get(option, "trigger"), "gold") == str(price)
        circles = load("common/scripted_triggers/rol_legend_circle_triggers.txt")
        model.triggers.update({k: v for k, _, v in circles})
        core = {"rol_mars_blade_claimed", "rol_nibelung_sphere_claimed", "rol_naxos_unit_unlocked", "rol_astrolabe_of_ocean_claimed"}
        for flags in (set(), core - {"rol_naxos_unit_unlocked"}, core, core | {"rol_ash_forged_mask_claimed"}):
            actor = State(flags=flags)
            assert model.condition(model.triggers["rol_has_all_major_relic_completions_trigger"], actor) == (core <= flags)
            assert model.condition(model.triggers["rol_has_all_five_relic_completions_trigger"], actor) == ((core | {"rol_ash_forged_mask_claimed"}) <= flags)
        return 4
    except (AssertionError, ValueError, KeyError, OSError, TypeError, IndexError, StopIteration, AttributeError) as error:
        errors.append(f"relic safety contract: {error}")
        return 0


if __name__ == "__main__":
    import sys
    issues = []
    count = check_relic_safety_contract(Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2], issues)
    for issue in issues: print(f"[FAIL] {issue}")
    if not issues: print(f"[OK] Relic safety: {count} fragment routes, original ownership, native fee declarations, replay/transfer guards (model only)")
    raise SystemExit(bool(issues))
