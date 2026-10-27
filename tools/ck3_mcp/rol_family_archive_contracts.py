"""House-owned master copies and paid editions, evaluated from actual menus.

This checks source state transitions, not CK3 house persistence or event UI.
"""
from pathlib import Path

if __package__:
    from .rol_growth_contracts import get
    from .rol_path_contracts import PathModel, Person
else:
    from rol_growth_contracts import get
    from rol_path_contracts import PathModel, Person


RECORDS = {
    "mars_notes": ("rol_expedition_mars_notes_modifier", "mars"),
    "nibelung_notes": ("rol_expedition_nibelung_notes_modifier", "nibelung"),
    "naxos_notes": ("rol_expedition_naxos_notes_modifier", "naxos"),
    "astrolabe_notes": ("rol_expedition_astrolabe_notes_modifier", "astrolabe"),
    "carthage_notes": ("rol_expedition_carthage_notes_modifier", "carthage"),
    "star_observations": ("rol_star_observations_modifier", "astrolabe"),
    "ocean_routes": ("rol_ocean_routes_modifier", "naxos"),
}


def check_family_archive_contract(root: Path, errors: list[str], model=None) -> int:
    try:
        model = model or PathModel(root)
        catalogue = "rol_catalogue_family_knowledge_decision"
        printing = "rol_print_family_knowledge_decision"
        cooldown = "rol_family_archive_print_cooldown"

        def actor(house=None, **kwargs):
            return Person(activity=None, house=house, gold=1000, **kwargs)

        def body(event, choice):
            definition = model.events[event]
            option = next(v for k, _, v in definition if k == "option" and get(v, "name") == choice)
            return model.option_body(option)

        def open_menu(person, decision, event):
            model.decide(person, decision)
            due, queued, context = person.queue.pop(0)
            assert queued == event and due == person.day, "house menu is not opened by its real decision"
            assert model.dispatch(person, queued, context) is not None
            assert person.scopes["rol_family_archive_house"] is person.house, "menu omitted original house snapshot"

        def choose(person, event, name):
            model.choose(person, event, name)
            model.options_seen.add((event, name))

        def unchanged_rewards(person):
            return person.prestige, person.piety, person.stress, dict(person.xp), set(person.traits), list(person.artifacts)

        for name, (modifier, route) in RECORDS.items():
            house = Person(activity=None, label="source-house")
            founder = actor(house, modifiers={modifier: 10}, modifier_expires={modifier: 3650})
            before = unchanged_rewards(founder)
            open_menu(founder, catalogue, "rol_family_archive.0001")
            choice = "rol_family_archive.0001." + name
            choose(founder, "rol_family_archive.0001", choice)
            assert founder.gold == 900, "cataloguing is not charged once at the normal price"
            assert house.variables == {"rol_family_archive_" + name: 1}, "wrong house record was catalogued"
            assert founder.modifiers == {modifier: 10} and founder.modifier_expires[modifier] == 3650, "cataloguing consumes or refreshes the source"
            assert unchanged_rewards(founder) == before and not founder.flags, "cataloguing invents expertise or completion"
            model.run(body("rol_family_archive.0001", choice), founder)
            assert founder.gold == 900, "a duplicate catalogue click charges again"

            # Same-house succession needs no export or completion backfill.
            heir = actor(house, label="same-house-heir")
            before = unchanged_rewards(heir)
            open_menu(heir, printing, "rol_family_archive.0002")
            choice = "rol_family_archive.0002." + name
            choose(heir, "rol_family_archive.0002", choice)
            assert heir.gold == 960 and heir.modifiers == {modifier: 5}, "same-house heir cannot print the selected edition"
            assert heir.modifier_expires[modifier] == 5 * 365, "printed edition has wrong duration"
            assert heir.flags == {cooldown, "rol_heard_" + route + "_legend"}, "edition reveals wrong route or sets completion flags"
            assert heir.expires[cooldown] == 3 * 365, "printing cooldown is not shared for three years"
            assert unchanged_rewards(heir) == before, "printing copies personal expertise or artifacts"
            model.run(body("rol_family_archive.0002", choice), heir)
            assert heir.gold == 960 and heir.modifier_expires[modifier] == 5 * 365, "replay charges or refreshes an edition"

            # The edition really enters the existing regional/chart consumer.
            heir.activity = {"rol_expedition_growth_open": 1, "rol_expedition_first_trial_used": 0,
                             "activity_special_type_progression": 30}
            heir.scopes.update(activity=heir.activity, host=heir)
            if name.endswith("_notes"):
                model.call("rol_expedition_growth_begin_effect", heir, {"ROUTE": name[:-6]})
                assert heir.activity["rol_expedition_journal_bonus"] == 5, "printed notes do not feed the existing retry bonus"
            else:
                context = "astrolabe" if name == "star_observations" else "naxos"
                chain = "sevilla" if name == "star_observations" else "naxos"
                heir.flags.add("rol_relic_context_" + context)
                model.call("rol_archive_chart_route_effect", heir, {
                    "QUALIFICATION": "rol_star_chart_route_trigger" if name == "star_observations" else "rol_ocean_chart_route_trigger",
                    "CHART": modifier, "NEXT_EVENT": "rol_quest_" + chain + ".1010",
                    "LOG_KEY": "rol_expedition_feedback_star_chart" if name == "star_observations" else "rol_expedition_feedback_ocean_chart",
                })
                assert heir.gold == 920 and heir.activity["rol_expedition_first_trial_used"] == 1, "printed chart bypasses the existing route charge or limit"
            assert modifier not in heir.modifiers, "existing expedition does not consume the edition"
            before_gold = heir.gold
            model.run(body("rol_family_archive.0002", choice), heir)
            assert heir.gold == before_gold and modifier not in heir.modifiers, "consuming an edition bypasses printing cooldown"
            assert house.variables == {"rol_family_archive_" + name: 1}, "using an edition consumes the house master copy"

            outsider = actor(Person(activity=None, label="other-house"))
            assert not model.condition(get(model.decisions[printing], "is_shown"), outsider), "another house can see this archive"
            outsider.scopes["rol_family_archive_house"] = outsider.house
            model.run(body("rol_family_archive.0002", choice), outsider)
            assert outsider.gold == 1000 and not outsider.modifiers, "another house obtains a master copy"

        name, (modifier, route) = next(iter(RECORDS.items()))
        catalogue_choice = "rol_family_archive.0001." + name
        print_choice = "rol_family_archive.0002." + name
        for research, has_trait, expected in ((0, False, 100), (99, True, 100), (100, True, 50), (100, False, 100)):
            person = actor(Person(activity=None), modifiers={modifier: 10})
            person.xp["rol_research"] = research
            if has_trait: person.traits.add("rol_relic_seeker")
            person.gold = expected
            open_menu(person, catalogue, "rol_family_archive.0001")
            choose(person, "rol_family_archive.0001", catalogue_choice)
            assert person.gold == 0, "research discount is not tied to the real 100-XP track"

        for operation, decision, event, choice, price in (
            ("catalogue", catalogue, "rol_family_archive.0001", catalogue_choice, 100),
            ("print", printing, "rol_family_archive.0002", print_choice, 40),
        ):
            for failure in ("poor", "changed_house", "no_house", "missing_snapshot", "expired_or_existing", "cooldown", "dead", "ai", "child"):
                house = Person(activity=None)
                if operation == "catalogue":
                    person = actor(house, modifiers={modifier: 10})
                else:
                    house.variables["rol_family_archive_" + name] = 1
                    person = actor(house)
                open_menu(person, decision, event)
                if failure == "poor": person.gold = price - 1
                elif failure == "changed_house":
                    person.house = Person(activity=None)
                    person.house.variables["rol_family_archive_" + name] = 1
                elif failure == "no_house": person.house = None
                elif failure == "missing_snapshot": person.scopes.clear()
                elif failure == "expired_or_existing":
                    if operation == "catalogue": person.modifiers.clear()
                    else: person.modifiers[modifier] = 2
                elif failure == "cooldown":
                    if operation == "catalogue": continue  # Catalogue has no cooldown.
                    person.flags.add(cooldown)
                elif failure == "dead": person.alive = False
                elif failure == "ai": person.ai = True
                elif failure == "child": person.adult = False
                before = person.gold, dict(person.modifiers), dict(house.variables), set(person.flags)
                model.run(body(event, choice), person)
                after = person.gold, dict(person.modifiers), dict(house.variables), set(person.flags)
                assert after == before, f"{operation} ignores changed click-time state: {failure}"

        # The common cooldown follows the person, including a later house change.
        house = Person(activity=None, variables={"rol_family_archive_" + n: 1 for n in RECORDS})
        person = actor(house)
        open_menu(person, printing, "rol_family_archive.0002")
        choose(person, "rol_family_archive.0002", print_choice)
        second = "nibelung_notes"
        second_modifier = RECORDS[second][0]
        model.run(body("rol_family_archive.0002", "rol_family_archive.0002." + second), person)
        assert person.gold == 960 and second_modifier not in person.modifiers, "printing another kind ignores shared cooldown"
        person.house = Person(activity=None, variables={"rol_family_archive_" + second: 1})
        person.scopes["rol_family_archive_house"] = person.house
        assert not model.condition(get(model.decisions[printing], "is_valid_showing_failures_only"), person), "changing house resets the personal printing cooldown"
        model.run(body("rol_family_archive.0002", "rol_family_archive.0002." + second), person)
        assert person.gold == 960 and second_modifier not in person.modifiers, "new-house edition ignores the same personal cooldown"
        person.house = house
        person.scopes["rol_family_archive_house"] = house
        model.advance(person, 1096)
        model.run(body("rol_family_archive.0002", print_choice), person)
        assert person.gold == 960 and person.modifier_expires[modifier] == 1825, "cooldown expiry refreshes an existing edition"
        model.advance(person, 1826)
        open_menu(person, printing, "rol_family_archive.0002")
        choose(person, "rol_family_archive.0002", print_choice)
        assert person.gold == 920 and person.modifier_expires[modifier] == 1826 + 1825, "expired edition cannot be reprinted"

        for decision, event in ((catalogue, "rol_family_archive.0001"), (printing, "rol_family_archive.0002")):
            house = Person(activity=None, variables={"rol_family_archive_" + name: 1})
            person = actor(house, modifiers={modifier: 10} if decision == catalogue else {})
            open_menu(person, decision, event)
            person.house = None
            choose(person, event, "rol_family_archive.close")
            assert person.gold == 1000, "neutral close pays or modifies archive state"

        return len(RECORDS)
    except (AssertionError, ValueError, KeyError, IndexError, OSError) as error:
        errors.append(f"family archive contract: {error}")
        return 0


if __name__ == "__main__":
    issues = []
    count = check_family_archive_contract(Path(__file__).resolve().parents[2], issues)
    if issues:
        raise SystemExit("\n".join(issues))
    print(f"[OK] {count} house records: paid cataloguing, editions, original consumers, membership, expiry and replay")
