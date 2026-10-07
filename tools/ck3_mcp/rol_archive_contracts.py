#!/usr/bin/env python3
"""Knowledge/estate contracts against source; does not emulate CK3 succession."""
from pathlib import Path
if __package__:
    from .rol_growth_contracts import Model, State, get, parse
else:
    from rol_growth_contracts import Model, State, get, parse

RECORDS = {
    "mars_notes": "rol_expedition_mars_notes_modifier", "nibelung_notes": "rol_expedition_nibelung_notes_modifier",
    "naxos_notes": "rol_expedition_naxos_notes_modifier", "astrolabe_notes": "rol_expedition_astrolabe_notes_modifier",
    "carthage_notes": "rol_expedition_carthage_notes_modifier", "star_observations": "rol_star_observations_modifier",
    "ocean_routes": "rol_ocean_routes_modifier",
}


def check_archive_contract(root: Path, errors: list[str]) -> int:
    try:
        model = Model(root)
        load = lambda file: parse((root/file).read_text(encoding="utf-8-sig"))
        events = load("events/rol_archive_events.txt")
        backgrounds = load("common/event_backgrounds/rol_event_backgrounds.txt")
        for name, _, event in events:
            if name != "namespace": get(backgrounds, get(get(event, "override_background"), "reference"))
        actions = load("common/on_action/rol_archive_on_actions.txt")
        assert get(get(actions, "on_death"), "on_actions")[0][0] == "rol_archive_death_on_action", "archive export has no real death entry"
        assert get(get(get(actions, "rol_archive_death_on_action"), "effect"), "rol_archive_export_effect") == "yes", "death callback omits export"
        legacy = get(load("common/on_action/rol_relic_legacy_on_actions.txt"), "rol_naxos_death_on_action")
        assert get(get(get(get(legacy, "effect"), "if"), "limit"), "player_heir") == [("is_alive", "=", "yes")], "Naxos callback prematurely checks the heir's AI status"
        legacy_event = get(load("events/rol_relic_legacy_events.txt"), "rol_relic_legacy.0103")
        option = next(v for k, _, v in legacy_event if k == "option" and get(v, "name").endswith(".a"))
        assert get(get(option, "trigger"), "gold") == "100", "Naxos inheritance does not check its gold cost"
        decisions = load("common/decisions/rol_archive_decisions.txt")
        assert get(get(get(decisions, "rol_review_inherited_records_decision"), "effect"), "trigger_event") == "rol_archive.0001", "archive recovery missing"
        get(get(get(decisions, "rol_review_inherited_pacts_decision"), "effect"), "rol_archive_open_pact_effect")

        for mode, type_, modifier, chart, chain, trigger in (
            (3, "rol_nibelung_star_sphere", "rol_relic_use_2_study_modifier", "rol_star_observations_modifier", "sevilla", "rol_star_chart_route_trigger"),
            (5, "rol_astrolabe_of_ocean", "rol_relic_use_3_navigation_modifier", "rol_ocean_routes_modifier", "naxos", "rol_ocean_chart_route_trigger"),
        ):
            host = State(activity=None)
            item = State(activity=None, artifact_type=type_, owner=host)
            host.scopes["rol_relic_use_candidate"] = item
            model.call("rol_relic_use_select_artifact_effect", host, {"TYPE": type_, "MODE": mode, "MODIFIER": modifier})
            model.call("rol_relic_use_record_knowledge_effect", host)
            assert chart not in host.modifiers, "early knowledge payoff bypasses project wait"
            host.flags.remove("rol_relic_use_waiting")
            model.call("rol_relic_use_record_experience_effect", host)
            model.call("rol_relic_use_record_experience_effect", host)
            assert host.modifiers[chart] == 10, "real record payoff does not produce a ten-year chart"
            context = "astrolabe" if chain == "sevilla" else "naxos"
            assert f"rol_heard_{context}_legend" in host.flags, "chart does not reveal its route"
            chain_event = get(load(f"events/rol_quest_{chain}_events.txt"), f"rol_quest_{chain}.1000")
            option = next(v for k, _, v in chain_event if k == "option" and get(v, "name") == f"rol_archive_{chain}_route_option")
            params = {k: v for k, _, v in get(get(option, "if"), "rol_archive_chart_route_effect")}
            assert params == {"QUALIFICATION": trigger, "CHART": chart, "NEXT_EVENT": f"rol_quest_{chain}.1010"}, "chart option is wired to wrong chain or evidence"
            for situation in ("correct", "wrong_region", "unaffordable", "already_used", "no_activity"):
                actor = State(flags={f"rol_relic_context_{context}"}, modifiers={chart: 10}, variables={f"rol_{chain}_stage_count": 0}, activity={"rol_expedition_growth_open": 1, "rol_expedition_first_trial_used": 0})
                if situation == "wrong_region": actor.flags = {"rol_relic_context_mars"}
                if situation == "unaffordable": actor.gold = 39
                if situation == "already_used": actor.activity["rol_expedition_first_trial_used"] = 1
                if situation == "no_activity": actor.activity = None
                before = actor.gold
                model.call("rol_archive_chart_route_effect", actor, params)
                model.call("rol_archive_chart_route_effect", actor, params)
                assert actor.gold == before - (40 if situation == "correct" else 0), "chart charge ignores validity or replays"
                assert (chart not in actor.modifiers) == (situation == "correct"), "wrong-region/failed/replayed use consumes evidence"
                assert len(actor.progress_effects) == (1 if situation == "correct" else 0), "chart advances outside its real opening or repeats"
            # Publishing instead yields no route chart.
            pub = State(activity=None, variables={"rol_relic_use_mode": mode, "rol_relic_use_generation": 1, "rol_relic_use_artifact": item}, flags={"rol_relic_use_pending"})
            item.owner = pub
            pub.scopes["rol_relic_use_generation"] = 1
            model.call("rol_relic_use_publish_effect", pub)
            assert chart not in pub.modifiers and pub.prestige == 300, "public outcome also produces knowledge"

        donor = State(activity=None, modifiers={value: 10 for value in RECORDS.values()},
                      traits={"rol_relic_seeker"}, xp={"rol_research": 100}, flags={"rol_mars_blade_claimed", "rol_expedition_growth_pending"},
                      variables={"rol_expedition_growth_pending_xp": 30})
        heir = State(activity=None, ai=True, modifiers={RECORDS["mars_notes"]: 9})
        donor.player_heir = heir
        model.call("rol_archive_export_effect", donor)
        model.call("rol_archive_export_effect", donor)
        assert all(f"rol_archive_{name}" in heir.flags for name in RECORDS) and heir.events == ["rol_archive.0001"], "export loses records, rejects the still-AI heir or repeats"
        assert not heir.xp and "rol_relic_seeker" not in heir.traits and "rol_mars_blade_claimed" not in heir.flags and not heir.artifacts and not heir.variables, "archive copies expertise, completion, artifact or pending XP"
        heir.ai = False
        model.call("rol_archive_accept_records_effect", heir)
        model.call("rol_archive_accept_records_effect", heir)
        assert heir.prestige == 150 and heir.modifiers[RECORDS["mars_notes"]] == 9, "archive charge replays or overwrites existing duration"
        assert all(heir.modifiers[value] == 5 for name, value in RECORDS.items() if name != "mars_notes"), "restored records do not last five years"
        assert all(f"rol_heard_{route}_legend" in heir.flags for route in ("mars", "nibelung", "naxos", "astrolabe", "carthage")), "inherited notes fail to reveal their activity entries"
        assert not model.condition(model.triggers["rol_archive_has_cargo_trigger"], heir) and not heir.xp, "read cargo persists or grants ancestor XP"
        for unavailable in ("no_heir", "dead_heir", "ai_donor", "empty"):
            parent = State(activity=None, modifiers={RECORDS["star_observations"]: 10})
            child = State(activity=None)
            parent.player_heir = child
            if unavailable == "no_heir": parent.player_heir = None
            if unavailable == "dead_heir": child.alive = False
            if unavailable == "ai_donor": parent.ai = True
            if unavailable == "empty": parent.modifiers.clear()
            model.call("rol_archive_export_effect", parent)
            assert not child.flags and not child.events, f"{unavailable}: export creates an invalid bequest"

        # Multiple actual donors and unresolved previous generations remain distinct.
        child = State(activity=None)
        parents, partners = [], []
        for role in (1, 2, 3):
            peer = State(activity=None)
            parent = State(activity=None, player_heir=child, flags={"rol_expedition_companion_settlement_pending"},
                           variables={"rol_expedition_companion_partner": peer, "rol_expedition_companion_role": role, "rol_expedition_companion_earned_xp": 10})
            model.call("rol_archive_export_effect", parent)
            model.call("rol_archive_export_effect", parent)
            parents.append(parent); partners.append(peer)
        assert child.lists["rol_archive_pact_sources"] == parents, "multiple inherited pacts overwrite or duplicate a donor"
        assert all(event == "rol_archive.0002" and context["rol_archive_heir"] is child and context["rol_archive_pact_source"] in parents for event, context in child.event_contexts), "queued pact context is addressed to another heir or changes source"
        next_heir = State(activity=None, ai=True)
        child.player_heir = next_heir
        child.flags.add("rol_archive_star_observations")
        model.call("rol_archive_export_effect", child)
        assert next_heir.lists["rol_archive_pact_sources"] == parents and "rol_archive_star_observations" in next_heir.flags, "unread cargo/pact queue is lost on another death"

        child.scopes["rol_archive_pact_source"] = parents[0]
        current = State(activity=None)
        child.variables["rol_expedition_companion_partner"] = current
        child.flags.add("rol_expedition_companion_in_field")
        model.call("rol_archive_adopt_pact_effect", child)
        assert child.variables["rol_expedition_companion_partner"] is current and child.lists["rol_archive_pact_sources"] == parents, "adoption overwrites a personal active pact"
        child.flags.remove("rol_expedition_companion_in_field")
        parents[0].variables["rol_expedition_companion_partner"] = State(activity=None)
        model.call("rol_archive_adopt_pact_effect", child)
        model.call("rol_archive_adopt_pact_effect", child)
        assert child.variables["rol_expedition_companion_partner"] is partners[0] and child.variables["rol_expedition_companion_earned_xp"] == 0, "adoption changes original participant or copies earned XP"
        assert child.lists["rol_archive_pact_sources"] == parents[1:], "adoption removes unrelated bequests or replays"
        model.call("rol_expedition_companion_honour_effect", child)
        assert child.prestige == 150 and not child.xp and child.variables["rol_expedition_trusted_companion"] is partners[0], "inherited honour grants old XP or changes payer/partner"
        child.scopes["rol_archive_pact_source"] = parents[1]
        partners[1].alive = False
        model.call("rol_archive_adopt_pact_effect", child)
        assert "rol_expedition_companion_settlement_pending" not in child.flags, "dead inherited participant is adopted"
        model.call("rol_archive_drop_selected_pact_effect", child)
        model.call("rol_archive_drop_selected_pact_effect", child)
        assert child.lists["rol_archive_pact_sources"] == parents[2:] and child.gold == 200, "dead/declined bequest pays or removes unrelated record"
        child.scopes["rol_archive_pact_source"] = parents[2]
        before = dict(child.modifiers)
        model.call("rol_archive_drop_selected_pact_effect", child)
        assert not child.lists["rol_archive_pact_sources"] and child.modifiers == before, "declining bequest inherits a stigma or leaves it pending"
        return 2, 7
    except (AssertionError, ValueError, KeyError, OSError, TypeError, IndexError, StopIteration, AttributeError) as error:
        errors.append(f"archive contract: {error}")
        return 0, 0

if __name__ == "__main__":
    import sys
    issues = []
    routes, records = check_archive_contract(Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2], issues)
    for issue in issues: print(f"[FAIL] {issue}")
    if not issues: print(f"[OK] Archive contracts: {routes} cross-chain routes, {records} records, inheritance/queue identity, no inherited XP (model only)")
    raise SystemExit(bool(issues))
