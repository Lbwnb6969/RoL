"""Master negotiation: cash-versus-public-credit on the actual guard agreement."""
from pathlib import Path


def check_companion_mastery_contract(root: Path, errors: list[str], model=None) -> int:
    if __package__:
        from .rol_path_contracts import PathModel, Person, get
    else:
        from rol_path_contracts import PathModel, Person, get

    count = 0
    try:
        model = model if model is not None else PathModel(root)
        event = "rol_expedition_companion.0002"
        name = "rol_expedition_companion_master_credit_option"
        definition = model.events[event]
        choice = next(v for k, _, v in definition if k == "option" and get(v, "name") == name)
        effect = model.option_body(choice)

        def new_pact(host=None, guard=None, stages=1):
            host = host if host is not None else Person(activity=None, gold=0, prestige=200,
                                                        traits={"rol_relic_seeker"}, xp={"rol_negotiation": 100})
            guard = guard if guard is not None else Person(activity=None, label="original guard", learning=1,
                                                           prowess=20, diplomacy=1, prestige=30)
            host.activity = {"_activity_type": "activity_rol_seek_mars_blade"}
            host.flags.add("rol_relic_context_mars")
            host.scopes = {"activity": host.activity, "host": host}
            host.attendees = [host, guard]
            model.call("rol_expedition_growth_begin_effect", host, {"ROUTE": "mars"})
            model.call("rol_expedition_companion_begin_effect", host)
            model.call("rol_expedition_companion_offer_effect", host, {"NEXT_EVENT": "rol_quest_rome.1000"})
            model.choose(host, "rol_expedition_companion.0001", "rol_expedition_companion.0001.b")
            host.variables["rol_rome_stage_count"] = stages
            model.call("rol_expedition_companion_finish_effect", host, {"STAGE_VARIABLE": "rol_rome_stage_count"})
            queued = next(entry for entry in reversed(host.queue) if entry[1] == event)
            host.activity = None
            assert model.dispatch(host, event, dict(queued[2])) is not None
            return host, guard

        def snapshot(host, partner):
            return (host.gold, host.prestige, partner.gold, partner.prestige,
                    dict(host.variables), set(host.flags), dict(host.xp), dict(partner.xp),
                    list(host.opinions), list(partner.opinions), dict(host.modifiers))

        # Produce the contract through the invitation and earned-stage settlement.
        host, guard = new_pact()
        xp = dict(host.xp)
        partner_xp = dict(guard.xp)
        assert host.variables["rol_expedition_companion_earned_xp"] == 10
        model.choose(host, event, name)
        model.options_seen.add((event, name))
        assert host.gold == 0 and guard.gold == 200, "public credit moves cash"
        assert host.prestige == 100 and guard.prestige == 130, "credit is not transferred to the original guard"
        assert host.variables["rol_expedition_trusted_companion"] is guard, "credit loses the original trusted companion"
        assert host.xp == xp and guard.xp == partner_xp and not host.modifiers, "credit adds expertise or reputation"
        assert host.opinions == [(guard, "rol_expedition_respect_opinion")]
        assert guard.opinions == [(host, "rol_expedition_respect_opinion")]
        assert "rol_expedition_companion_settlement_pending" not in host.flags
        settled = snapshot(host, guard)
        model.run(effect, host)
        assert snapshot(host, guard) == settled, "settled public credit can replay"
        count += 1

        # Pausing and the existing recovery decision retain identity and price.
        host, guard = new_pact()
        model.choose(host, event, "rol_expedition_companion.0002.d")
        before = snapshot(host, guard)
        model.decide(host, "rol_settle_expedition_pact_decision")
        queued = host.queue[-1]
        assert queued[1] == event and model.dispatch(host, event, dict(queued[2])) is not None
        assert snapshot(host, guard) == before, "reopening rewards or replaces the guard"
        model.choose(host, event, name)
        assert host.variables["rol_expedition_trusted_companion"] is guard and guard.prestige == 130
        count += 1

        for failure in ("poor", "not_master", "wrong_track", "no_trait", "scholar", "envoy",
                        "no_progress", "inherited", "dead", "wrong_person", "missing_person",
                        "old_generation", "missing_generation"):
            host, guard = new_pact(stages=0 if failure == "no_progress" else 1)
            if failure == "poor": host.prestige = 99
            elif failure == "not_master": host.xp["rol_negotiation"] = 99
            elif failure == "wrong_track": host.xp = {"rol_research": 100, "rol_exploration": 100}
            elif failure == "no_trait": host.traits.clear()
            elif failure in ("scholar", "envoy"):
                host.variables["rol_expedition_companion_role"] = 1 if failure == "scholar" else 3
            elif failure == "inherited": host.variables["rol_expedition_companion_earned_xp"] = 0
            elif failure == "dead": guard.alive = False
            elif failure == "wrong_person": host.scopes["rol_expedition_companion"] = Person(activity=None)
            elif failure == "missing_person": host.scopes.pop("rol_expedition_companion")
            elif failure == "old_generation": host.scopes["rol_expedition_companion_generation"] -= 1
            elif failure == "missing_generation": host.scopes.pop("rol_expedition_companion_generation")
            assert not model.condition(get(choice, "trigger"), host), f"{failure}: invalid public-credit option remains available"
            before = snapshot(host, guard)
            model.run(effect, host)
            assert snapshot(host, guard) == before, f"{failure}: invalid credit pays or consumes the agreement"
            count += 1

        # A paid previous agreement must never settle a new one, even for the same person.
        for same_person in (False, True):
            host, old = new_pact()
            context = dict(host.scopes)
            model.choose(host, event, name)
            host.prestige = 200
            next_guard = old if same_person else Person(activity=None, label="new guard", learning=1,
                                                       prowess=20, diplomacy=1, prestige=30)
            host, next_guard = new_pact(host=host, guard=next_guard)
            current = dict(host.scopes)
            host.scopes = context
            before = snapshot(host, next_guard)
            model.run(effect, host)
            assert snapshot(host, next_guard) == before, "old guard window consumes a later agreement"
            host.scopes = current
            model.choose(host, event, name)
            assert host.prestige == 100 and host.variables["rol_expedition_trusted_companion"] is next_guard
            count += 1

        # Old pending personal agreements are usable after their normal recovery.
        host, guard = new_pact()
        host.variables.pop("rol_expedition_companion_generation")
        host.scopes.pop("rol_expedition_companion_generation")
        model.decide(host, "rol_settle_expedition_pact_decision")
        assert model.dispatch(host, event, dict(host.queue[-1][2])) is not None
        model.choose(host, event, name)
        assert host.prestige == 100 and host.variables["rol_expedition_trusted_companion"] is guard
        count += 1

        # Original cash settlement and compromise keep their stronger/different payoffs.
        for outcome in ("honour", "compromise"):
            host, guard = new_pact()
            host.gold = 100
            before = host.prestige
            model.choose(host, event, "rol_expedition_companion.0002." + ("a" if outcome == "honour" else "b"))
            assert host.prestige == before and guard.prestige == 30
            if outcome == "honour":
                assert host.gold == 50 and guard.gold == 250 and host.xp.get("rol_exploration") == 10
                assert "rol_expedition_kept_word_modifier" in host.modifiers
            else:
                assert host.gold == 75 and guard.gold == 225 and host.xp.get("rol_exploration") == 5
                assert "rol_expedition_trusted_companion" not in host.variables
            count += 1
        return count
    except (AssertionError, KeyError, ValueError, StopIteration, TypeError, AttributeError, OSError) as error:
        errors.append(f"companion mastery contract: {error}")
        return 0


if __name__ == "__main__":
    issues = []
    total = check_companion_mastery_contract(Path(__file__).resolve().parents[2], issues)
    for issue in issues:
        print(f"[FAIL] {issue}")
    if not issues:
        print(f"[OK] {total} master-negotiation scenarios: original guard, earned contract, cost, recovery and replay")
    raise SystemExit(bool(issues))
