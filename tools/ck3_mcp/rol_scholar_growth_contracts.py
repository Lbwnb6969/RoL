"""Original observer's earned research must affect that person's field help."""
from pathlib import Path


def check_scholar_growth_contract(root: Path, errors: list[str], model=None) -> int:
    if __package__:
        from .rol_path_contracts import PathModel, Person, get, start_route, plain_actor, relic, drive
    else:
        from rol_path_contracts import PathModel, Person, get, start_route, plain_actor, relic, drive
    count = 0
    try:
        model = model if model is not None else PathModel(root)
        personal = "rol_expedition_scholar_personal_bonus_value"
        active = "rol_expedition_companion_scholar_chance_modifier"

        def next_window(actor, expected):
            due, event, context = actor.queue.pop(0)
            assert event == expected
            model.advance(actor, due)
            assert model.dispatch(actor, event, context) is not None

        # Six normal annual jobs train the same observer, rather than granting
        # experience through a test-only effect or increasing the patron's track.
        actor = plain_actor()
        relic(actor, "rol_nibelung_star_sphere")
        scholar = Person(activity=None, label="original-observer", learning=12,
                         court_owner=actor, playable=False)
        actor.court = [scholar]
        actor.variables["rol_expedition_trusted_companion"] = scholar
        for job in range(1, 7):
            started = actor.day
            model.decide(actor, "rol_arrange_relic_use_decision")
            next_window(actor, "rol_relic_use.0001")
            model.choose(actor, "rol_relic_use.0001", "rol_relic_use.0001.2")
            next_window(actor, "rol_relic_use.1002")
            model.choose(actor, "rol_relic_use.1002", "rol_relic_use_commission_option")
            next_window(actor, "rol_relic_use.0003")
            model.choose(actor, "rol_relic_use.0003", "rol_relic_use_commission_pay_option")
            assert scholar.xp == {"rol_research": job * 10} and not actor.xp, "commission growth is not earned by the original observer"
            assert model.number(personal, actor, scholar) == (5 if job == 6 else 3), "field tier does not follow the actual observer's earned research"
            if job != 6:
                model.advance(actor, started + 366)
        count += 1

        # Actual departure -> invitation -> original candidate -> accepted role.
        actor, definition = start_route(model, "munich", actor=actor)
        actor.attendees.append(scholar)
        actor = drive(model, actor, definition=definition, stop_before="rol_expedition_companion.0001")
        next_window(actor, "rol_expedition_companion.0001")
        original = actor.variables["rol_expedition_trusted_companion"]
        assert actor.scopes["rol_expedition_candidate_scholar"] is original
        assert original.xp["rol_research"] == 60 and model.number(personal, actor, original) == 5
        model.choose(actor, "rol_expedition_companion.0001", "rol_expedition_companion.0001.a")
        assert actor.variables["rol_expedition_companion_partner"] is original
        assert model.number(active, actor) == 5, "trained original observer loses the field bonus after the real invitation"
        count += 1

        def party(xp=60, trait=True, role=1):
            host = plain_actor()
            host.activity = {"rol_expedition_companion_open": 1, "rol_expedition_companion_role": role,
                             "rol_expedition_journal_bonus": 0}
            host.scopes = {"host": host, "activity": host.activity}
            peer = Person(activity=host.activity, label="contracted-scholar", learning=12,
                          traits={"rol_relic_seeker"} if trait else set(), xp={"rol_research": xp})
            host.variables["rol_expedition_companion_partner"] = peer
            host.attendees = [host, peer]
            return host, peer

        for xp, trait, expected in ((0, False, 3), (59, True, 3), (60, True, 5),
                                     (100, True, 5), (100, False, 3)):
            host, peer = party(xp, trait)
            assert model.number(personal, host, peer) == model.number(active, host) == expected, "candidate terms and actual help disagree at a tier boundary"
            count += 1

        for reason in ("host-master", "wrong-track", "other-trained-attendee", "later-trusted"):
            host, peer = party(0)
            if reason == "host-master":
                host.traits.add("rol_relic_seeker")
                host.xp["rol_research"] = 100
            elif reason == "wrong-track": peer.xp = {"rol_exploration": 100, "rol_negotiation": 100}
            else:
                other = Person(activity=host.activity, label="other-scholar", traits={"rol_relic_seeker"}, xp={"rol_research": 100})
                host.attendees.append(other)
                if reason == "later-trusted": host.variables["rol_expedition_trusted_companion"] = other
            assert model.number(active, host) == 3, f"{reason}: someone else's expertise increases the contracted person's help"
            count += 1

        for reason in ("left", "dead", "child", "prisoner", "incapable", "closed", "guard", "envoy", "missing"):
            host, peer = party()
            if reason == "left": host.attendees.remove(peer)
            elif reason == "dead": peer.alive = False
            elif reason == "child": peer.adult = False
            elif reason == "prisoner": peer.imprisoned = True
            elif reason == "incapable": peer.traits.add("incapable")
            elif reason == "closed": host.activity["rol_expedition_companion_open"] = 0
            elif reason in ("guard", "envoy"): host.activity["rol_expedition_companion_role"] = 2 if reason == "guard" else 3
            else: host.variables.pop("rol_expedition_companion_partner")
            assert model.number(active, host) == 0, f"{reason}: inactive specialist still supplies scholar help"
            host.variables["rol_expedition_display_base_chance"] = 90
            assert model.number("rol_expedition_success_chance_90_value", host) == model.number("rol_expedition_display_success_chance_value", host) == 90
            count += 1

        # Shared actual/tooltip formula, including a low branch and the 95% cap.
        for xp, bonus in ((59, 3), (60, 5)):
            host, peer = party(xp)
            for prep, adjustment in (("low", -10), ("standard", 0), ("high", 10), ("supreme", 20)):
                host.preparation = prep
                for notes in (0, 5):
                    host.activity["rol_expedition_journal_bonus"] = notes
                    for base in (35, 65, 90):
                        host.variables["rol_expedition_display_base_chance"] = base
                        expected = min(95, max(5, base + adjustment + notes + bonus))
                        assert model.number(f"rol_expedition_success_chance_{base}_value", host) == model.number("rol_expedition_display_success_chance_value", host) == expected
                        assert model.number(f"rol_expedition_failure_chance_{base}_value", host) == model.number("rol_expedition_display_failure_chance_value", host) == 100 - expected
            count += 1

        # The two computations share their eligibility trigger and numeric values.
        # The invitation evaluates on its actual candidate, not ROOT/patron.
        for language in ("english", "simp_chinese"):
            text = (root / "localization" / language / f"rol_expedition_companion_l_{language}.yml").read_text(encoding="utf-8-sig")
            line = next(line for line in text.splitlines() if " rol_expedition_companion_scholar_terms_tt:" in line)
            assert f"rol_expedition_candidate_scholar.MakeScope.ScriptValue('{personal}')" in line, "scholar invitation displays the patron's expertise or a hard-coded benefit"
        return count
    except (AssertionError, ValueError, KeyError, AttributeError, OSError, IndexError, StopIteration) as error:
        errors.append(f"scholar growth contract: {error}")
        return 0


if __name__ == "__main__":
    issues = []
    total = check_scholar_growth_contract(Path(__file__).resolve().parents[2], issues)
    if issues:
        raise SystemExit("\n".join(issues))
    print(f"[OK] {total} scholar witnesses: earned commissions, original attendance, tiers and exact odds")
