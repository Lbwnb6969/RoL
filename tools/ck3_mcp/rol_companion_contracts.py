#!/usr/bin/env python3
"""Companion integration/state checks using the limited source model, not CK3."""
from pathlib import Path

if __package__:
    from .rol_growth_contracts import Model, State, ROUTES, get, parse
else:
    from rol_growth_contracts import Model, State, ROUTES, get, parse


CONTEXTS = {"rome": "mars", "munich": "nibelung", "naxos": "naxos", "sevilla": "astrolabe", "carthage": "carthage"}


def check_companion_contract(root: Path, errors: list[str]) -> int:
    try:
        model = Model(root)
        load = lambda path: parse((root / path).read_text(encoding="utf-8-sig"))
        events = load("events/rol_expedition_companion_events.txt")
        invitation = get(events, "rol_expedition_companion.0001")
        settlement = get(events, "rol_expedition_companion.0002")
        options = [v for k, _, v in invitation if k == "option"]
        assert len(options) == 4, "invitation needs three specialists and a decline"
        for role, option in enumerate(options[:3], 1):
            assert get(get(option, "rol_expedition_companion_accept_effect"), "ROLE") == str(role), "invitation role mismatch"
        assert get(options[3], "rol_expedition_companion_continue_effect") == "yes", "decline blocks the original expedition"
        for option in options[:3]:
            assert "scope:activity" in {k for k, _, _ in get(option, "trigger")}, "invitation option does not recheck actual attendance"
        review = get(load("common/decisions/rol_expedition_companion_decisions.txt"), "rol_settle_expedition_pact_decision")
        assert get(get(review, "effect"), "trigger_event") == "rol_expedition_companion.0002", "settlement recovery is not wired"
        defer = next(v for k, _, v in settlement if k == "option" and get(v, "name").endswith(".d"))
        assert {k for k, _, _ in defer} == {"name", "flavor", "trigger", "custom_tooltip"}, "deferral modifies or rewards the pending contract"

        def party(chain="rome"):
            host = State(flags={f"rol_relic_context_{CONTEXTS[chain]}"}, variables={f"rol_{chain}_stage_count": 0})
            scholar = State(activity=None, learning=20, prowess=1, diplomacy=1)
            guard = State(activity=None, learning=1, prowess=20, diplomacy=1)
            envoy = State(activity=None, learning=1, prowess=1, diplomacy=20)
            host.attendees = [host, scholar, guard, envoy]
            model.call("rol_expedition_growth_begin_effect", host, {"ROUTE": CONTEXTS[chain]})
            model.call("rol_expedition_companion_begin_effect", host)
            model.call("rol_expedition_companion_offer_effect", host, {"NEXT_EVENT": f"rol_quest_{chain}.1000"})
            return host, scholar, guard, envoy

        for chain, (_, filename, cooldown) in ROUTES.items():
            activity = load(f"common/activities/activity_types/{filename}")[0][2]
            assert get(get(get(activity, "on_start"), "scope:host"), "rol_expedition_companion_begin_effect") == "yes", f"{chain}: companion initialization missing"
            complete = get(get(activity, "on_complete"), "scope:host")
            assert get(get(complete, "rol_expedition_companion_finish_effect"), "STAGE_VARIABLE") == f"rol_{chain}_stage_count", f"{chain}: cancellation does not close the same contract"
            chain_events = load(f"events/rol_quest_{chain}_events.txt")
            arrival_option = get(get(chain_events, f"rol_quest_{chain}.0990"), "option")
            assert get(get(get(arrival_option, "hidden_effect"), "rol_expedition_companion_offer_effect"), "NEXT_EVENT") == f"rol_quest_{chain}.1000", f"{chain}: arrival bypasses companion offer"
            trial = get(chain_events, f"rol_quest_{chain}.1000")
            for name, cost in (("rol_expedition_guard_route_option", "75"), ("rol_expedition_expert_route_option", "100")):
                option = next(v for k, _, v in trial if k == "option" and get(v, "name") == name)
                prepared = get(option, "rol_expedition_prepared_route_effect")
                assert get(prepared, "COST") == cost and get(prepared, "NEXT_EVENT") == f"rol_quest_{chain}.1010", f"{chain}: prepared route does not reach normal success progression"
            effects = load(f"common/scripted_effects/rol_quest_{chain}_effects.txt")
            for name in (f"rol_{chain}_quest_success_finalize_effect", f"rol_{chain}_quest_partial_finalize_effect", cooldown):
                assert get(get(get(effects, name), "rol_expedition_companion_finish_effect"), "STAGE_VARIABLE") == f"rol_{chain}_stage_count", f"{chain}: ending omits same-person settlement"
            host, scholar, guard, envoy = party(chain)
            assert host.scopes["rol_expedition_candidate_scholar"] is scholar and host.scopes["rol_expedition_candidate_guard"] is guard and host.scopes["rol_expedition_candidate_envoy"] is envoy, "specialists do not match their attending qualification"
            model.call("rol_expedition_companion_accept_effect", host, {"PARTNER": "scope:rol_expedition_candidate_scholar", "ROLE": 1})
            assert host.variables["rol_expedition_companion_partner"] is scholar and f"rol_quest_{chain}.1000" in host.events, f"{chain}: acceptance loses the original person or route"

        # An attending person is unavailable for another activity, but can help here.
        host, scholar, guard, envoy = party()
        scholar.available = False
        host.scopes.clear()
        host.activity["rol_expedition_companion_offer"] = 0
        scholar.learning = 12
        stronger = State(activity=None, learning=30, prowess=1, diplomacy=1)
        host.attendees.append(stronger)
        host.variables["rol_expedition_trusted_companion"] = scholar
        model.call("rol_expedition_companion_offer_effect", host, {"NEXT_EVENT": "rol_quest_rome.1000"})
        assert host.scopes["rol_expedition_candidate_scholar"] is scholar, "qualified trusted attendee is blocked by generic availability or not preferred"

        for reason in ("alone", "unqualified", "dead", "imprisoned", "incapable"):
            solo = State(flags={"rol_relic_context_mars"})
            peer = State(activity=None, learning=11, prowess=11, diplomacy=11)
            if reason != "unqualified": peer.learning = 20
            if reason == "dead": peer.alive = False
            if reason == "imprisoned": peer.imprisoned = True
            if reason == "incapable": peer.traits.add("incapable")
            solo.attendees = [solo] if reason == "alone" else [solo, peer]
            model.call("rol_expedition_growth_begin_effect", solo, {"ROUTE": "mars"})
            model.call("rol_expedition_companion_begin_effect", solo)
            model.call("rol_expedition_companion_offer_effect", solo, {"NEXT_EVENT": "rol_quest_rome.1000"})
            assert solo.events == ["rol_quest_rome.1000"], f"{reason}: no usable companion blocks normal route or creates a contract"

        for role, title, track, cost in ((1, "scholar", "rol_research", 50), (2, "guard", "rol_exploration", 50), (3, "envoy", "rol_negotiation", 75)):
            for stage in (0, 1):
                host, *_ = party()
                peer = host.scopes[f"rol_expedition_candidate_{title}"]
                model.call("rol_expedition_companion_accept_effect", host, {"PARTNER": f"scope:rol_expedition_candidate_{title}", "ROLE": role})
                host.variables["rol_rome_stage_count"] = stage
                model.call("rol_expedition_companion_finish_effect", host, {"STAGE_VARIABLE": "rol_rome_stage_count"})
                model.call("rol_expedition_companion_finish_effect", host, {"STAGE_VARIABLE": "rol_rome_stage_count"})
                assert host.events.count("rol_expedition_companion.0002") == 1, "duplicate ending queues repeated settlement"
                before = host.gold if role == 2 else host.prestige
                model.call("rol_expedition_companion_honour_effect", host)
                model.call("rol_expedition_companion_honour_effect", host)
                assert (host.gold if role == 2 else host.prestige) == before - cost, "honour payment is missing or repeated"
                assert host.xp.get(track, 0) == (10 if stage else 0), "honour XP can be farmed without stage progress or replayed"
                assert host.variables["rol_expedition_trusted_companion"] is peer and len(peer.opinions) == len(host.opinions) == 1, "trusted relationship changed person or opinion was replayed"
                assert (peer.gold == 250) if role == 2 else (peer.gold == 200), "guard payment went to another person"
                assert not model.condition(model.triggers["rol_expedition_companion_pending_trigger"], host), "fulfilled pact remains pending"

            poor, *_ = party()
            model.call("rol_expedition_companion_accept_effect", poor, {"PARTNER": f"scope:rol_expedition_candidate_{title}", "ROLE": role})
            poor.variables["rol_rome_stage_count"] = 1
            model.call("rol_expedition_companion_finish_effect", poor, {"STAGE_VARIABLE": "rol_rome_stage_count"})
            poor.gold = poor.prestige = 0
            model.call("rol_expedition_companion_honour_effect", poor)
            assert poor.gold == poor.prestige == 0 and not poor.xp and "rol_expedition_companion_settlement_pending" in poor.flags, "unaffordable payment closes or rewards agreement"

        host, scholar, guard, envoy = party()
        model.call("rol_expedition_companion_accept_effect", host, {"PARTNER": "scope:rol_expedition_candidate_guard", "ROLE": 2})
        params = {"COST": 75, "QUALIFICATION": "rol_expedition_companion_guard_trigger", "NEXT_EVENT": "rol_quest_rome.1010"}
        model.call("rol_expedition_prepared_route_effect", host, params)
        model.call("rol_expedition_prepared_route_effect", host, params)
        assert host.gold == 125 and len(host.progress_effects) == 1 and host.events.count("rol_quest_rome.1010") == 1, "guard route is not one-use"
        host.traits.add("rol_relic_seeker")
        host.xp["rol_research"] = 60
        model.call("rol_expedition_prepared_route_effect", host, {"COST": 100, "QUALIFICATION": "rol_expedition_expert_route_trigger", "NEXT_EVENT": "rol_quest_rome.1010"})
        assert host.gold == 125 and len(host.progress_effects) == 1, "expert route bypasses shared first-trial limit"
        for reason in ("left", "dead"):
            host, _, guard, _ = party()
            model.call("rol_expedition_companion_accept_effect", host, {"PARTNER": "scope:rol_expedition_candidate_guard", "ROLE": 2})
            if reason == "left": host.attendees.remove(guard)
            else: guard.alive = False
            model.call("rol_expedition_prepared_route_effect", host, params)
            assert host.gold == 200 and not host.progress_effects, "departed/dead guard still opens prepared route"
        for xp in (59, 60):
            expert, *_ = party()
            expert.traits.add("rol_relic_seeker")
            expert.xp["rol_research"] = xp
            model.call("rol_expedition_prepared_route_effect", expert, {"COST": 100, "QUALIFICATION": "rol_expedition_expert_route_trigger", "NEXT_EVENT": "rol_quest_rome.1010"})
            assert expert.gold == (100 if xp == 60 else 200), "expert route ignores its experience threshold"

        host, scholar, guard, envoy = party()
        model.call("rol_expedition_companion_accept_effect", host, {"PARTNER": "scope:rol_expedition_candidate_envoy", "ROLE": 3})
        host.scopes["rol_expedition_rival"] = State(activity=None)
        model.call("rol_expedition_companion_mediate_effect", host)
        model.call("rol_expedition_companion_mediate_effect", host)
        assert host.stress == 10 and len(host.progress_effects) == 1, "envoy mediation can be replayed"

        # Invalidation recovery retains the original person but never invents progress XP.
        host, scholar, *_ = party()
        model.call("rol_expedition_companion_accept_effect", host, {"PARTNER": "scope:rol_expedition_candidate_scholar", "ROLE": 1})
        host.activity = {}
        host.variables["rol_rome_stage_count"] = 0
        model.call("rol_expedition_companion_begin_effect", host)
        model.call("rol_expedition_companion_begin_effect", host)
        assert host.variables["rol_expedition_companion_partner"] is scholar and host.variables["rol_expedition_companion_earned_xp"] == 0 and host.events.count("rol_expedition_companion.0002") == 1, "invalidated trip loses original pact, duplicates recovery or fabricates XP"

        for choice in ("compromise", "refuse", "dead", "defer"):
            host, scholar, *_ = party()
            model.call("rol_expedition_companion_accept_effect", host, {"PARTNER": "scope:rol_expedition_candidate_scholar", "ROLE": 1})
            host.variables["rol_rome_stage_count"] = 1
            model.call("rol_expedition_companion_finish_effect", host, {"STAGE_VARIABLE": "rol_rome_stage_count"})
            if choice == "compromise":
                model.call("rol_expedition_companion_compromise_effect", host)
                model.call("rol_expedition_companion_compromise_effect", host)
                assert host.gold == 175 and scholar.gold == 225 and host.xp == {"rol_research": 5}, "compromise payment or XP repeats"
            elif choice == "refuse":
                host.traits.add("honest")
                host.variables["rol_expedition_trusted_companion"] = scholar
                model.call("rol_expedition_companion_refuse_effect", host)
                model.call("rol_expedition_companion_refuse_effect", host)
                assert host.stress == 35 and not host.xp and "rol_expedition_trusted_companion" not in host.variables, "refusal does not close old trust or repeats stress"
            elif choice == "dead":
                scholar.alive = False
                model.call("rol_expedition_companion_honour_effect", host)
                assert host.prestige == 200 and not host.xp, "dead participant is paid or replaced"
                close = next(v for k, _, v in settlement if k == "option" and get(v, "name").endswith(".e"))
                model.run([n for n in close if n[0] == "if"], host)
                assert "rol_expedition_companion_partner" not in host.variables, "absent contract does not clear"
            else:
                model.call("rol_expedition_companion_begin_effect", host)
                model.call("rol_expedition_companion_offer_effect", host, {"NEXT_EVENT": "rol_quest_rome.1000"})
                assert host.variables["rol_expedition_companion_partner"] is scholar and not host.xp, "pending agreement silently picks another partner"

        for present in (True, False):
            host, scholar, *_ = party()
            model.call("rol_expedition_companion_accept_effect", host, {"PARTNER": "scope:rol_expedition_candidate_scholar", "ROLE": 1})
            if not present: host.attendees.remove(scholar)
            for prep, modifier in (("low", -10), ("standard", 0), ("high", 10), ("supreme", 20)):
                host.preparation = prep
                for journal in (0, 5):
                    host.activity["rol_expedition_journal_bonus"] = journal
                    host.variables["rol_expedition_display_base_chance"] = 90
                    actual = model.number("rol_expedition_success_chance_90_value", host)
                    shown = model.number("rol_expedition_display_success_chance_value", host)
                    assert actual == shown == min(95, 90 + modifier + journal + (3 if present else 0)), "scholar presence, journal or displayed chance diverges"
                    assert model.number("rol_expedition_failure_chance_90_value", host) == 100 - actual, "scholar chance breaks complement"
            host.scopes["rol_expedition_host"] = host
            assert not model.condition(model.triggers["rol_expedition_rival_candidate_trigger"], host, scholar), "contracted companion can be selected as their own rival"

        return len(ROUTES)
    except (AssertionError, ValueError, KeyError, OSError, TypeError, IndexError, StopIteration, AttributeError) as error:
        errors.append(f"companion contract: {error}")
        return 0


if __name__ == "__main__":
    import sys
    issues = []
    routes = check_companion_contract(Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2], issues)
    for issue in issues: print(f"[FAIL] {issue}")
    if not issues: print(f"[OK] Companion contracts: {routes} routes, same-person settlement, aid/replay, death and probability checks (model only)")
    raise SystemExit(bool(issues))
