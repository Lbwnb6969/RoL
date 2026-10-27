"""Committed expedition actions must leave truthful, attributed activity records."""
from pathlib import Path
import re


def check_expedition_feedback_contract(root: Path, errors: list[str], model=None) -> int:
    if __package__:
        from .rol_path_contracts import PathModel, Person, ROUTES, get, plain_actor, start_route, drive
    else:
        from rol_path_contracts import PathModel, Person, ROUTES, get, plain_actor, start_route, drive
    try:
        model = model if model is not None else PathModel(root)
        prefix = "rol_expedition_feedback_"
        verified = set()

        def body(event, name):
            return model.option_body(next(v for k, _, v in model.events[event] if k == "option" and get(v, "name") == name))

        def records(actor):
            activity = actor.activity if actor.activity is not None else actor.scopes.get("activity", {})
            return [r for r in activity.get("_log_records", []) if r["key"].startswith(prefix)]

        def require(actor, key, target=None):
            key = prefix + key
            matches = [r for r in records(actor) if r["key"] == key]
            assert len(matches) == 1, f"{key}: absent or duplicate committed-action record"
            assert matches[0]["character"] == actor.label, f"{key}: log actor is not the host"
            assert matches[0]["target"] == (target.label if target is not None else actor.label), f"{key}: contributor changed identity"
            verified.add(key)

        def opening(chain="rome", role=None, trusted=False):
            actor, definition = start_route(model, chain, company=role is not None, actor=plain_actor())
            if trusted:
                actor.variables["rol_expedition_trusted_companion"] = actor.attendees[1]
            actor.traits.add("rol_relic_seeker")
            actor.xp["rol_research"] = 60
            choices = {"rol_expedition_companion.0001": "rol_expedition_companion.0001." + {1: "a", 2: "b", 3: "c"}[role]} if role is not None else {}
            event = f"rol_quest_{chain}.1000"
            actor = drive(model, actor, choices, definition, stop_before=event)
            due, queued, context = actor.queue.pop(0)
            assert queued == event
            model.advance(actor, due, definition)
            assert model.dispatch(actor, event, context) is not None
            return actor, definition, event

        for chain in ROUTES:
            for role, option, key, price in ((2, "rol_expedition_guard_route_option", "guard_route", 75),
                                             (None, "rol_expedition_expert_route_option", "expert_route", 100)):
                actor, _, event = opening(chain, role, trusted=chain == "rome" and role == 2)
                original = actor.variables.get("rol_expedition_companion_partner", actor)
                before_gold, progress = actor.gold, actor.activity["activity_special_type_progression"]
                model.choose(actor, event, option)
                require(actor, key, original)
                assert actor.gold == before_gold - price and actor.activity["activity_special_type_progression"] == progress + 10
                before = list(records(actor))
                model.run(body(event, option), actor)
                assert records(actor) == before, "replayed opening claims another contribution"
                if chain == "rome" and role == 2:
                    require(actor, "reunion", original)
                    actor.variables["rol_expedition_companion_partner"] = Person(label="replacement")
                    require(actor, key, original)

        # An unavailable contributor, closed expedition or missing payment must not
        # write the successful route record, even through an already-open option.
        for reason in ("left", "dead", "poor", "closed"):
            actor, _, event = opening(role=2)
            partner = actor.variables["rol_expedition_companion_partner"]
            if reason == "left": actor.attendees.remove(partner)
            elif reason == "dead": partner.alive = False
            elif reason == "poor": actor.gold = 74
            else: actor.activity["rol_expedition_growth_open"] = 0
            before = list(records(actor)), actor.gold
            model.run(body(event, "rol_expedition_guard_route_option"), actor)
            assert (records(actor), actor.gold) == before, f"{reason}: guard credit without an actual route"

        for chain, chart, key in (("sevilla", "rol_star_observations_modifier", "star_chart"),
                                   ("naxos", "rol_ocean_routes_modifier", "ocean_chart")):
            actor, _, event = opening(chain)
            actor.modifiers[chart] = 10
            name = f"rol_archive_{chain}_route_option"
            before = actor.gold
            model.choose(actor, event, name)
            require(actor, key)
            assert chart not in actor.modifiers and actor.gold == before - 40
            before = list(records(actor))
            model.run(body(event, name), actor)
            assert records(actor) == before, "chart record repeats after consumption"

        # Real partial settlements produce only their region's evidence. A later
        # real departure consumes that record and captures the separate use entry.
        for chain, (route, _, _) in ROUTES.items():
            actor, definition = start_route(model, chain, stat=5)
            actor = drive(model, actor, definition=definition)
            require(actor, route + "_evidence")
            notes = f"rol_expedition_{route}_notes_modifier"
            assert notes in actor.modifiers
            model.advance(actor, actor.day + 731)
            other = "rol_expedition_naxos_notes_modifier" if route != "naxos" else "rol_expedition_mars_notes_modifier"
            actor.modifiers[other] = 10
            actor, _ = start_route(model, chain, actor=actor)
            require(actor, route + "_notes")
            assert notes not in actor.modifiers and other in actor.modifiers
            assert actor.activity["rol_expedition_journal_bonus"] == 5

        # Envoy and rival entries name the actual contributor. Their existing
        # once-only route closure also closes their opportunity to write a log.
        for kind, name, key in (("envoy", "rol_rival.1000.d", "mediation"),
                                ("accord", "rol_expedition_envoy_accord_option", "envoy_accord"),
                                ("cooperation", "rol_rival_reunion_research_option", "joint_research"),
                                ("grudge", "rol_rival_reunion_reconcile_option", "reconciliation")):
            actor, _, _ = opening(role=3)
            envoy = actor.variables["rol_expedition_companion_partner"]
            rival = next(p for p in actor.attendees if p is not actor and p is not envoy)
            actor.scopes.update(rol_expedition_host=actor, rol_expedition_rival=rival)
            actor.flags.add("rol_rival_route_mars")
            if kind == "accord":
                envoy.traits.add("rol_relic_seeker")
                envoy.xp["rol_negotiation"] = 60
            elif kind != "envoy":
                actor.variables["rol_rival_relationship_partner"] = rival
                actor.flags.add(f"rol_rival_{kind}_active")
            model.call("rol_rival_begin_encounter_effect", actor)
            model.choose(actor, "rol_rival.1000", name)
            require(actor, key, envoy if kind == "envoy" else rival)
            if kind == "accord": require(actor, "mediation", envoy)
            before = list(records(actor))
            model.run(body("rol_rival.1000", name), actor)
            assert records(actor) == before, "closed rival encounter writes another success"

        for option, key in (("rol_expedition_growth.0010.a", "paid_recovery"),
                             ("rol_expedition_master_exploration_option", "master_recovery"),
                             ("rol_expedition_growth.0010.b", "salvage"),
                             ("rol_expedition_growth.0010.c", "retreat")):
            actor, definition, event = opening("munich")
            actor.xp["rol_exploration"] = 100
            outcomes = model.alternatives(body(event, event + ".a"), actor)
            actor = next(a for a in outcomes if any(q[1].endswith(".1011") for q in a.queue))
            crisis = "rol_expedition_growth.0010"
            actor = drive(model, actor, definition=definition, stop_before=crisis)
            due, queued, context = actor.queue.pop(0)
            assert queued == crisis
            model.advance(actor, due, definition)
            assert model.dispatch(actor, crisis, context) is not None
            valid_context = dict(actor.scopes)
            actor.variables["rol_expedition_remedy_generation"] += 1
            before = list(records(actor))
            model.run(body(crisis, option), actor)
            assert records(actor) == before, "stale crisis writes a successful decision"
            actor.variables["rol_expedition_remedy_generation"] -= 1
            actor.scopes = valid_context
            model.choose(actor, crisis, option)
            require(actor, key)
            before = list(records(actor))
            for alternate in ("rol_expedition_growth.0010.a", "rol_expedition_master_exploration_option",
                              "rol_expedition_growth.0010.b", "rol_expedition_growth.0010.c"):
                model.run(body(crisis, alternate), actor)
            assert records(actor) == before, "spent crisis writes a second decision"

        for language in ("english", "simp_chinese"):
            text = (root / "localization" / language / f"rol_expedition_feedback_l_{language}.yml").read_text(encoding="utf-8-sig")
            keys = set(re.findall(r"^\s+(rol_expedition_feedback_[\w]+):0", text, re.M))
            assert keys == verified | {key + "_title" for key in verified}, "feedback keys/titles lack actual action witnesses"
        template = model.effects["rol_expedition_feedback_effect"]
        entry = get(get(template, "scope:activity"), "add_activity_log_entry")
        assert get(entry, "character") == "scope:host" and get(entry, "target") == "$CONTRIBUTOR$"
        assert get(entry, "show_in_conclusion") == "yes"
        return len(verified)
    except (AssertionError, ValueError, KeyError, StopIteration, IndexError, OSError) as error:
        errors.append(f"expedition feedback contract: {error}")
        return 0


if __name__ == "__main__":
    issues = []
    total = check_expedition_feedback_contract(Path(__file__).resolve().parents[2], issues)
    if issues:
        raise SystemExit("\n".join(issues))
    print(f"[OK] {total} feedback types: committed actions, original contributors, replay and invalid-window isolation")
