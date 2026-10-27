#!/usr/bin/env python3
"""Check identity-bound rival memory through the existing finite source model."""
from pathlib import Path


def check_rival_relationship_contract(root: Path, errors: list[str], model=None) -> int:
    # Lazy import keeps this contract usable from both static and path audits.
    if __package__:
        from .rol_path_contracts import PathModel, Person, get
    else:
        from rol_path_contracts import PathModel, Person, get

    count = 0
    try:
        model = model if model is not None else PathModel(root)
        event = model.events["rol_rival.1000"]
        research = next(v for k, _, v in event if k == "option" and get(v, "name") == "rol_rival_reunion_research_option")
        reconcile = next(v for k, _, v in event if k == "option" and get(v, "name") == "rol_rival_reunion_reconcile_option")
        assert get(research, "custom_tooltip") and get(reconcile, "custom_tooltip"), "reunion choices must explain their costs and outcomes"

        def party(attitude="cooperation"):
            actor = Person(label="host", flags={"rol_relic_context_mars", "rol_rival_route_mars"})
            actor.activity = {"_activity_type": "activity_rol_seek_mars_blade", "activity_special_type_progression": 30}
            old = Person(activity=None, label="old-rival", playable=False)
            stranger = Person(activity=None, label="stranger", playable=False)
            actor.attendees = [actor, stranger, old]
            actor.scopes = {"activity": actor.activity, "host": actor}
            actor.variables["rol_rival_relationship_partner"] = old
            actor.flags.add(f"rol_rival_{attitude}_active")
            return actor, old, stranger

        def selected_weights(actor):
            model.call("rol_select_expedition_rival_effect", actor)
            roll = next(v for k, _, v in model.selected(model.effects["rol_try_rival_interlude_effect"], actor, "actor") if k == "random_list")
            return [float(k) for k, _, _ in roll]

        def open_encounter(actor, old):
            actor.scopes["rol_expedition_host"] = actor
            actor.scopes["rol_expedition_rival"] = old
            model.call("rol_rival_begin_encounter_effect", actor)
            assert model.dispatch(actor, "rol_rival.1000", dict(actor.scopes)) is not None

        for attitude, weights in (("cooperation", [75, 25]), ("grudge", [70, 30])):
            actor, old, _ = party(attitude)
            assert selected_weights(actor) == weights and actor.scopes["rol_expedition_rival"] is old, "attending original rival loses priority or identity-bound probability"
            count += 1

        for reason in ("absent", "dead", "imprisoned", "incapable", "companion", "unidentified", "expired"):
            actor, old, stranger = party("grudge")
            actor.scopes["rol_expedition_rival"] = old  # stale context must be overwritten
            if reason == "absent": actor.attendees.remove(old)
            elif reason == "dead": old.alive = False
            elif reason == "imprisoned": old.imprisoned = True
            elif reason == "incapable": old.traits.add("incapable")
            elif reason == "companion": actor.variables["rol_expedition_companion_partner"] = old
            elif reason == "unidentified": actor.variables.pop("rol_rival_relationship_partner")
            elif reason == "expired": actor.flags.discard("rol_rival_grudge_active")
            assert selected_weights(actor) == [40, 60], f"{reason}: old relationship applies to stranger"
            assert actor.scopes["rol_expedition_rival"] is stranger, f"{reason}: invalid/absent/contracted rival selected"
            if reason in ("dead", "unidentified", "expired"):
                assert "rol_rival_relationship_partner" not in actor.variables and "rol_rival_grudge_active" not in actor.flags, f"{reason}: unusable memory was not closed"
            count += 1

        # Known absent courtier is not summoned; the ordinary court fallback remains.
        actor, old, stranger = party()
        actor.attendees = [actor]
        actor.court = [old, stranger]
        assert selected_weights(actor) == [40, 60] and actor.scopes["rol_expedition_rival"] is stranger, "absent known rival is summoned from court"
        assert actor.variables["rol_rival_relationship_partner"] is old, "absence destroys a still-valid relationship"
        count += 1

        actor, old, _ = party()
        actor.attendees = [actor]
        actor.court = [old]
        actor.scopes["rol_expedition_rival"] = old
        results = list(model.alternatives(model.effects["rol_try_rival_interlude_effect"], actor))
        for result in results:
            assert "rol_expedition_rival" not in result.scopes, "old saved scope survived an empty selection"
            assert [event for _, event, _ in result.queue] == ["$FALLBACK_EVENT$"], "empty selection blocks the existing guest route"
            assert "rol_rival_route_mars" not in result.flags and "rol_rival_encounter_partner" not in result.variables
        count += 1

        # Real dispatcher captures the selected person and serial before its delay.
        actor, old, _ = party()
        dispatched = next(result for result in model.alternatives(model.effects["rol_try_rival_interlude_effect"], actor)
                          if result.queue[0][1] == "rol_rival.1000")
        due, _, context = dispatched.queue[0]
        assert due == 4 and context["rol_rival_encounter_generation"] == dispatched.variables["rol_rival_encounter_generation"]
        assert context["rol_expedition_rival"] is dispatched.variables["rol_rival_encounter_partner"]
        count += 1

        # A real first cooperation survives a normal two-year retry interval.
        actor, old, _ = party()
        actor.variables.pop("rol_rival_relationship_partner")
        actor.flags.discard("rol_rival_cooperation_active")
        open_encounter(actor, old)
        model.choose(actor, "rol_rival.1000", "rol_rival.1000.a")
        model.choose(actor, "rol_rival.1001", "rol_rival.1001.a")
        assert actor.variables["rol_rival_relationship_partner"] is old and "rol_rival_cooperation_active" in actor.flags, "real cooperation does not record its original person"
        model.advance(actor, 731)
        actor.activity = {"_activity_type": "activity_rol_seek_mars_blade", "activity_special_type_progression": 30}
        actor.scopes = {"activity": actor.activity, "host": actor}
        assert selected_weights(actor) == [75, 25] and actor.scopes["rol_expedition_rival"] is old, "relationship expires before a normal failed-expedition retry"
        count += 1

        actor, old, _ = party()
        open_encounter(actor, old)
        before = (actor.gold, actor.prestige, dict(actor.xp))
        model.choose(actor, "rol_rival.1000", "rol_rival_reunion_research_option")
        model.options_seen.add(("rol_rival.1000", "rol_rival_reunion_research_option"))
        model.run(model.option_body(research), actor)
        assert actor.activity["activity_special_type_progression"] == 35, "joint research progress is missing or replayed"
        assert before == (actor.gold, actor.prestige, actor.xp), "joint research adds unintended cost/reward"
        assert len(actor.opinions) == len(old.opinions) == 1 and old.opinions[0][0] is actor
        assert actor.variables["rol_rival_relationship_partner"] is old and "rol_rival_encounter_partner" not in actor.variables, "encounter closure destroys memory or leaves a payable encounter"
        count += 1

        actor, old, _ = party("grudge")
        open_encounter(actor, old)
        model.choose(actor, "rol_rival.1000", "rol_rival_reunion_reconcile_option")
        model.options_seen.add(("rol_rival.1000", "rol_rival_reunion_reconcile_option"))
        model.run(model.option_body(reconcile), actor)
        assert actor.gold == 150 and old.gold == 250, "reconciliation payment does not go once to the original person"
        assert actor.activity["activity_special_type_progression"] == 30 and not actor.xp, "reconciliation grants progress/experience"
        assert "rol_rival_grudge_active" not in actor.flags and "rol_rival_cooperation_active" in actor.flags
        assert actor.flag_durations["rol_rival_cooperation_active"] == [("years", "10")]
        assert len(actor.opinions) == len(old.opinions) == 1
        count += 1

        for reason in ("poor", "left", "dead", "imprisoned", "wrong-person", "old-generation", "old-window"):
            actor, old, stranger = party("grudge")
            open_encounter(actor, old)
            if reason == "poor": actor.gold = 49
            elif reason == "left": actor.attendees.remove(old)
            elif reason == "dead": old.alive = False
            elif reason == "imprisoned": old.imprisoned = True
            elif reason == "wrong-person": actor.scopes["rol_expedition_rival"] = stranger
            elif reason == "old-generation":
                context = dict(actor.scopes)
                model.call("rol_rival_begin_encounter_effect", actor)
                actor.scopes = context
            elif reason == "old-window": actor.scopes.pop("rol_rival_encounter_generation")
            before = (actor.gold, old.gold, len(actor.opinions), len(old.opinions), dict(actor.variables), set(actor.flags))
            model.run(model.option_body(reconcile), actor)
            assert before == (actor.gold, old.gold, len(actor.opinions), len(old.opinions), actor.variables, actor.flags), f"{reason}: invalid reconciliation pays or consumes a later encounter"
            count += 1

        # A replaced relationship cannot turn another person's encounter into a reunion.
        actor, old, stranger = party()
        open_encounter(actor, old)
        actor.variables["rol_rival_relationship_partner"] = stranger
        before = actor.activity["activity_special_type_progression"]
        model.run(model.option_body(research), actor)
        assert actor.activity["activity_special_type_progression"] == before and not old.opinions
        count += 1

        # Payable pact identity/generation is independent of lasting relationship memory.
        actor, old, _ = party()
        actor.variables["rol_rival_pact_partner"] = old
        actor.flags.add("rol_rival_pact_choice_pending")
        actor.scopes["rol_expedition_rival"] = old
        model.call("rol_rival_new_pact_effect", actor)
        model.choose(actor, "rol_rival.1001", "rol_rival.1001.a")
        assert "rol_rival_pact_partner" not in actor.variables and actor.variables["rol_rival_relationship_partner"] is old
        count += 1

        actor, old, _ = party()
        actor.variables["rol_rival_pact_partner"] = old
        actor.flags.add("rol_rival_pact_choice_pending")
        actor.scopes["rol_expedition_rival"] = old
        model.call("rol_rival_new_pact_effect", actor)
        model.choose(actor, "rol_rival.1001", "rol_rival.1001.b")
        assert actor.variables["rol_rival_relationship_partner"] is old and "rol_rival_grudge_active" in actor.flags and "rol_rival_cooperation_active" not in actor.flags
        count += 1
    except (AssertionError, KeyError, ValueError, StopIteration) as exc:
        errors.append(f"rival relationship contract: {exc}")
        return 0
    return count


if __name__ == "__main__":
    issues = []
    total = check_rival_relationship_contract(Path(__file__).resolve().parents[2], issues)
    for issue in issues:
        print(f"[ERROR] {issue}")
    if not issues:
        print(f"[OK] Rival relationships: {total} identity, attendance, fallback, replay, payment and pact scenarios (source model only)")
    raise SystemExit(bool(issues))
