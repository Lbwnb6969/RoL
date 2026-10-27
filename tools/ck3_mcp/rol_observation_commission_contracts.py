#!/usr/bin/env python3
"""Check commissioned observation against production scripts, not CK3 runtime.

The shared model treats court membership and opinion as explicit engine snapshots.
It does not simulate invitations, court travel, opinion decay or queued-save scopes.
"""
from pathlib import Path

if __package__:
    from .rol_growth_contracts import get, parse
    from .rol_path_contracts import PathModel, Person, plain_actor, relic, optional
else:
    from rol_growth_contracts import get, parse
    from rol_path_contracts import PathModel, Person, plain_actor, relic, optional


def check_observation_commission_contract(root: Path, errors: list[str], model=None) -> int:
    count = 0
    try:
        model = model if model is not None else PathModel(root)
        configure, payoff = "rol_relic_use.1002", "rol_relic_use.0003"
        accept = "rol_relic_use_commission_option"
        pay, credit = "rol_relic_use_commission_pay_option", "rol_relic_use_commission_credit_option"
        commissioned, partner_key = "rol_relic_use_commissioned", "rol_relic_use_commission_partner"
        chart, deployed = "rol_star_observations_modifier", "rol_relic_use_2_study_modifier"
        opinion_definitions = {}
        for path in sorted((root / "common/opinion_modifiers").glob("rol*.txt")):
            opinion_definitions.update({key: value for key, _, value in parse(path.read_text(encoding="utf-8-sig"))})

        def option(event, name):
            return next(body for key, _, body in model.events[event] if key == "option" and get(body, "name") == name)

        def enabled(actor, event, name):
            return model.condition(optional(option(event, name), "trigger", []), actor)

        def click(actor, event, name):
            # A click uses the already-open window. Re-dispatch would rerun immediate
            # and accidentally replace the very candidate snapshot being checked.
            assert enabled(actor, event, name), f"commission option unavailable: {name}"
            model.run(model.option_body(option(event, name)), actor)
            model.options_seen.add((event, name))

        def force(actor, event, name):
            model.run(model.option_body(option(event, name)), actor)

        def next_window(actor, expected):
            due, event, context = actor.queue.pop(0)
            assert event == expected, f"expected {expected}, got {event}"
            model.advance(actor, due)
            assert model.dispatch(actor, event, context) is not None, f"production event blocked: {event}"

        def new_party():
            actor = plain_actor()
            item = relic(actor, "rol_nibelung_star_sphere")
            item.modifiers.update(original_modifier=None, fragment_modifier=None)
            scholar = Person(activity=None, label="original-scholar", learning=12, playable=False,
                             court_owner=actor, opinion_values={actor: 0})
            actor.court = [scholar]
            actor.variables["rol_expedition_trusted_companion"] = scholar
            return actor, item, scholar

        def open_menu(actor):
            model.decide(actor, "rol_arrange_relic_use_decision")
            next_window(actor, "rol_relic_use.0001")
            click(actor, "rol_relic_use.0001", "rol_relic_use.0001.2")
            next_window(actor, configure)

        def begin():
            actor, item, scholar = new_party()
            open_menu(actor)
            assert actor.scopes["rol_relic_use_commission_candidate"] is scholar, "configuration fails to snapshot the original scholar"
            click(actor, configure, accept)
            assert actor.gold == 3950 and commissioned in actor.flags, "commission changes the native 50-gold entry or fails to create its identity"
            assert actor.variables[partner_key] is scholar and actor.variables["rol_relic_use_artifact"] is item
            assert actor.variables["rol_relic_use_mode"] == 3 and actor.variables["rol_relic_use_generation"] == 1
            assert actor.queue[0][0] == 181 and actor.expires["rol_relic_use_waiting"] == 180
            assert item.modifiers == {"original_modifier": None, "fragment_modifier": None, deployed: None}, "commission alters unrelated artifact properties"
            return actor, item, scholar

        def snapshot(actor, item, scholar):
            return (actor.gold, actor.prestige, actor.stress, dict(actor.xp), set(actor.traits),
                    dict(actor.modifiers), set(actor.flags), dict(actor.variables),
                    scholar.gold, scholar.prestige, dict(scholar.xp), set(scholar.traits),
                    list(scholar.opinions), list(actor.opinions), dict(item.modifiers))

        def opinions(actor, scholar, expected):
            assert len(actor.opinions) == len(scholar.opinions) == 1, "commission opinions replay or omit one recipient"
            for owner, target in ((actor, scholar), (scholar, actor)):
                recipient, modifier = owner.opinions[0]
                assert recipient is target, "commission opinion targets a replacement character"
                definition = opinion_definitions[modifier]
                assert float(get(definition, "opinion")) == expected and float(get(definition, "years")) == 5, "commission relationship value/duration differs from terms"

        for ending, relation in ((pay, 10), (credit, 25)):
            actor, item, scholar = begin()
            assert not enabled(actor, payoff, ending), "commission pays before its waiting period"
            before = snapshot(actor, item, scholar)
            for name in (pay, credit, "rol_relic_use.0003.a", "rol_relic_use.0003.b"):
                force(actor, payoff, name)
            assert snapshot(actor, item, scholar) == before, "forced early payoff changes the project"
            next_window(actor, payoff)
            assert not enabled(actor, payoff, "rol_relic_use.0003.a") and not enabled(actor, payoff, "rol_relic_use.0003.b"), "commission can also collect personal XP/prestige"
            # Later expertise/affection changes do not silently revoke an agreed job.
            scholar.learning = 1
            scholar.opinion_values[actor] = -100
            replacement = Person(activity=None, label="later-trusted", court_owner=actor)
            actor.variables["rol_expedition_trusted_companion"] = replacement
            click(actor, payoff, ending)
            assert actor.prestige == 1000 and not actor.xp and not actor.traits, "commission also grants the host's ordinary reward"
            assert commissioned not in actor.flags and partner_key not in actor.variables and "rol_relic_use_pending" not in actor.flags, "settlement leaves commission/job identity open"
            assert deployed in item.modifiers and "rol_relic_use_cooldown" in actor.flags, "settlement clears deployment or cooldown"
            assert replacement.gold == 200 and replacement.prestige == 200 and not replacement.opinions, "later trusted pointer replaces the contracted scholar"
            opinions(actor, scholar, relation)
            if ending == pay:
                assert actor.gold == 3900 and scholar.gold == 250 and scholar.prestige == 200, "fee does not go exactly once to the original scholar"
                assert scholar.xp == {"rol_research": 10} and scholar.traits == {"rol_relic_seeker"}, "paid commission does not transfer the original 10 research XP to its executor"
                assert actor.modifiers[chart] == 10 and actor.modifier_expires[chart] == actor.day + 3650
                assert "rol_heard_astrolabe_legend" in actor.flags, "paid observation fails to reveal its real route"
            else:
                assert actor.gold == 3950 and scholar.gold == 200 and scholar.prestige == 300, "public attribution rewards the wrong person"
                assert not scholar.xp and not scholar.traits, "public attribution also trains its executor"
                assert chart not in actor.modifiers and "rol_heard_astrolabe_legend" not in actor.flags
            before = snapshot(actor, item, scholar)
            for name in (pay, credit, "rol_relic_use.0003.a", "rol_relic_use.0003.b", "rol_relic_use.0003.d"):
                force(actor, payoff, name)
            assert snapshot(actor, item, scholar) == before, "commission settlement replays or switches outcomes"
            if ending == pay:
                actor.activity = {"rol_expedition_growth_open": 1, "rol_expedition_first_trial_used": 0,
                                  "_activity_type": "activity_rol_seek_astrolabe_of_ocean", "activity_special_type_progression": 35}
                actor.flags.add("rol_relic_context_astrolabe")
                actor.scopes.update(activity=actor.activity, host=actor)
                model.call("rol_archive_chart_route_effect", actor, {"QUALIFICATION": "rol_star_chart_route_trigger",
                           "CHART": chart, "NEXT_EVENT": "rol_quest_sevilla.1010", "LOG_KEY": "rol_expedition_feedback_star_chart"})
                assert actor.gold == 3860 and chart not in actor.modifiers and actor.activity["rol_expedition_first_trial_used"] == 1, "commissioned chart does not enter its actual 40-gold route consumer"
                assert scholar.xp == {"rol_research": 10} and not actor.xp
            count += 1

        # Candidate thresholds and click-time changes belong to this original menu.
        for reason in ("poor", "no_trusted", "self", "dead", "child", "imprisoned", "incapable", "other_court", "unskilled", "hostile", "lost_item"):
            actor, item, scholar = new_party()
            if reason == "no_trusted":
                actor.variables.pop("rol_expedition_trusted_companion")
                actor.scopes["rol_relic_use_commission_candidate"] = scholar
            elif reason == "self":
                actor.variables["rol_expedition_trusted_companion"] = actor
                actor.court_owner = actor
            open_menu(actor)
            if reason == "poor": actor.gold = 49
            elif reason == "dead": scholar.alive = False
            elif reason == "child": scholar.adult = False
            elif reason == "imprisoned": scholar.imprisoned = True
            elif reason == "incapable": scholar.traits.add("incapable")
            elif reason == "other_court": scholar.court_owner = Person(activity=None)
            elif reason == "unskilled": scholar.learning = 11
            elif reason == "hostile": scholar.opinion_values[actor] = -1
            elif reason == "lost_item": item.owner = Person(activity=None)
            before = snapshot(actor, item, scholar)
            assert not enabled(actor, configure, accept), f"invalid commission candidate accepted: {reason}"
            force(actor, configure, accept)
            assert snapshot(actor, item, scholar) == before, f"invalid entry charges or deploys: {reason}"
            count += 1

        actor, item, scholar = new_party()
        open_menu(actor)
        replacement = Person(activity=None, label="replacement", court_owner=actor, learning=20)
        actor.variables["rol_expedition_trusted_companion"] = replacement
        click(actor, configure, accept)
        assert actor.variables[partner_key] is scholar, "menu click substitutes the current trusted pointer for its original candidate"
        count += 1

        actor, item, scholar = begin()
        next_window(actor, payoff)
        before = snapshot(actor, item, scholar)
        click(actor, payoff, "rol_relic_use.0003.c")
        assert snapshot(actor, item, scholar) == before, "defer changes the original commission"
        actor.gold = 49
        assert not enabled(actor, payoff, pay) and enabled(actor, payoff, credit), "poor host cannot use the non-gold conclusion"
        force(actor, payoff, pay)
        assert actor.gold == 49 and scholar.gold == 200 and commissioned in actor.flags, "unaffordable fee pays or consumes the project"
        model.decide(actor, "rol_review_relic_use_decision")
        next_window(actor, payoff)
        assert actor.variables[partner_key] is scholar, "recovery selects a new executor"
        click(actor, payoff, credit)
        assert scholar.prestige == 300 and actor.gold == 49 and chart not in actor.modifiers
        count += 1

        for reason in ("missing_partner", "dead", "left", "imprisoned", "incapable", "lost_item", "stopped"):
            actor, item, scholar = begin()
            if reason == "missing_partner": actor.variables.pop(partner_key)
            elif reason == "dead": scholar.alive = False
            elif reason == "left": scholar.court_owner = Person(activity=None)
            elif reason == "imprisoned": scholar.imprisoned = True
            elif reason == "incapable": scholar.traits.add("incapable")
            elif reason == "lost_item":
                item.owner = Person(activity=None)
                model.call("rol_relic_use_clear_artifact_modes_effect", actor, scope=item)
            else:
                model.call("rol_relic_use_retire_artifact_effect", actor, {"TYPE": "rol_nibelung_star_sphere"})
            model.advance(actor, 181)
            before = (actor.gold, scholar.gold, scholar.prestige, actor.prestige, dict(actor.xp))
            for name in (pay, credit, "rol_relic_use.0003.a", "rol_relic_use.0003.b"):
                force(actor, payoff, name)
            assert before == (actor.gold, scholar.gold, scholar.prestige, actor.prestige, actor.xp), f"invalid commission pays: {reason}"
            force(actor, payoff, "rol_relic_use.0003.d")
            assert commissioned not in actor.flags and partner_key not in actor.variables and "rol_relic_use_pending" not in actor.flags, f"invalid commission remains pending: {reason}"
            assert chart not in actor.modifiers and "rol_relic_use_cooldown" in actor.flags
            if reason not in ("lost_item", "stopped"): assert deployed in item.modifiers
            count += 1

        # A stale mature window cannot settle a later job, including the same NPC.
        for same_person in (True, False):
            actor, item, scholar = begin()
            next_window(actor, payoff)
            old_context = dict(actor.scopes)
            click(actor, payoff, credit)
            model.advance(actor, 366)
            later = scholar if same_person else Person(activity=None, learning=12, court_owner=actor)
            actor.variables["rol_expedition_trusted_companion"] = later
            open_menu(actor)
            click(actor, configure, accept)
            next_window(actor, payoff)
            current_context = dict(actor.scopes)
            actor.scopes = old_context
            before = snapshot(actor, item, later)
            for name in (pay, credit, "rol_relic_use.0003.d"):
                force(actor, payoff, name)
            assert snapshot(actor, item, later) == before, "old commission window pays or closes a new project"
            actor.scopes = current_context
            click(actor, payoff, pay)
            assert chart in actor.modifiers and commissioned not in actor.flags
            count += 1

        # The original personal project stays available even with an eligible friend.
        actor, item, scholar = new_party()
        open_menu(actor)
        click(actor, configure, "rol_relic_use.1002.1")
        assert commissioned not in actor.flags and partner_key not in actor.variables
        next_window(actor, payoff)
        click(actor, payoff, "rol_relic_use.0003.a")
        assert actor.xp == {"rol_research": 10} and chart in actor.modifiers and scholar.prestige == 200
        count += 1

        # Existing death cargo can move; ongoing commissions and payment identity do not.
        actor, item, scholar = begin()
        actor.modifiers["rol_expedition_mars_notes_modifier"] = 10
        heir = Person(activity=None, ai=True)
        actor.player_heir = heir
        model.call("rol_archive_export_effect", actor)
        assert "rol_archive_mars_notes" in heir.flags
        assert commissioned not in heir.flags and partner_key not in heir.variables
        assert not any(key.startswith("rol_relic_use_") for key in heir.variables) and not heir.artifacts
        count += 1

        return count
    except (AssertionError, ValueError, KeyError, AttributeError, TypeError, OSError, IndexError, StopIteration) as exc:
        errors.append(f"observation commission contract: {exc}")
        return 0


if __name__ == "__main__":
    issues = []
    result = check_observation_commission_contract(Path(__file__).resolve().parents[2], issues)
    for issue in issues:
        print(f"[ERROR] {issue}")
    if not issues:
        print(f"[OK] Observation commission: {result} production-menu, original-person, reward, generation and cleanup witnesses")
    raise SystemExit(bool(issues))
