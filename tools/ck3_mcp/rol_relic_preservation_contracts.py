"""Restoration results preserve one genuine source through the house archive."""
from pathlib import Path

if __package__:
    from .rol_growth_contracts import get
    from .rol_path_contracts import PathModel, Person, plain_actor, relic, optional
    from .rol_family_archive_contracts import RECORDS
else:
    from rol_growth_contracts import get
    from rol_path_contracts import PathModel, Person, plain_actor, relic, optional
    from rol_family_archive_contracts import RECORDS


def check_relic_preservation_contract(root: Path, errors: list[str], model=None) -> int:
    count = 0
    try:
        model = model if model is not None else PathModel(root)
        result, menu = "rol_relic_use.0003", "rol_relic_use.0005"
        entry = "rol_relic_preservation_option"
        note = "rol_expedition_mars_notes_modifier"

        def option(event, name):
            return next(v for k, _, v in model.events[event] if k == "option" and get(v, "name") == name)

        def enabled(actor, event, name):
            return model.condition(optional(option(event, name), "trigger", []), actor)

        def click(actor, event, name):
            assert enabled(actor, event, name), f"unavailable preservation choice: {name}"
            model.run(model.option_body(option(event, name)), actor)
            model.options_seen.add((event, name))

        def force(actor, event, name):
            model.run(model.option_body(option(event, name)), actor)

        def next_window(actor, expected):
            due, event, context = actor.queue.pop(0)
            assert event == expected, f"expected {expected}, got {event}"
            model.advance(actor, due)
            assert model.dispatch(actor, event, context) is not None, f"blocked event: {event}"

        def begin(modifiers=None, mode=8):
            actor = plain_actor()
            actor.house = Person(activity=None, label="original-house")
            actor.modifiers = dict(modifiers if modifiers is not None else {note: 10})
            actor.modifier_expires = {key: 3650 for key in actor.modifiers}
            item = relic(actor, "rol_ash_forged_mask")
            item.modifiers.update(original_modifier=None, fragment_modifier=None)
            gold = actor.gold
            model.decide(actor, "rol_arrange_relic_use_decision")
            next_window(actor, "rol_relic_use.0001")
            click(actor, "rol_relic_use.0001", "rol_relic_use.0001.4")
            next_window(actor, "rol_relic_use.1004")
            click(actor, "rol_relic_use.1004", "rol_relic_use.1004.2" if mode == 8 else "rol_relic_use.1004.1")
            assert actor.gold == gold - 50, "restoration entry does not pay the original 50 gold once"
            next_window(actor, result)
            return actor, item

        def catalogue(actor):
            click(actor, result, entry)
            next_window(actor, menu)
            assert actor.scopes["rol_family_archive_house"] is actor.house

        def rewards(actor):
            return actor.gold, actor.prestige, actor.piety, actor.stress, dict(actor.xp), set(actor.traits)

        # Every real source becomes exactly its own master copy, then a paid heir edition.
        for name, (modifier, route) in RECORDS.items():
            actor, item = begin({modifier: 10})
            catalogue(actor)
            before, expiry = rewards(actor), actor.modifier_expires[modifier]
            choice = "rol_family_archive.0001." + name
            click(actor, menu, choice)
            assert actor.house.variables == {"rol_family_archive_" + name: 1}, "preservation records another source or house"
            assert actor.modifiers == {modifier: 10} and actor.modifier_expires[modifier] == expiry, "preservation consumes or refreshes the source"
            assert rewards(actor) == before, "preservation invents payment, personal XP, prestige or stress rewards"
            assert not (set(actor.variables) & {"rol_relic_use_mode", "rol_relic_use_artifact"})
            assert "rol_relic_use_pending" not in actor.flags and "rol_relic_use_cooldown" in actor.flags
            assert set(item.modifiers) == {"original_modifier", "fragment_modifier", "rol_relic_use_4_restoration_modifier"}
            force(actor, menu, choice)
            force(actor, result, "rol_relic_use.0003.a")
            force(actor, result, "rol_relic_use.0003.b")
            assert rewards(actor) == before, "old result pays again after preservation"

            heir = plain_actor()
            heir.house = actor.house
            before_gold = heir.gold
            model.decide(heir, "rol_print_family_knowledge_decision")
            next_window(heir, "rol_family_archive.0002")
            click(heir, "rol_family_archive.0002", "rol_family_archive.0002." + name)
            assert heir.gold == before_gold - 40 and heir.modifier_expires[modifier] == 5 * 365
            assert "rol_family_archive_print_cooldown" in heir.flags and "rol_heard_" + route + "_legend" in heir.flags
            assert not heir.xp and not heir.artifacts, "house preservation transfers personal progress"
            count += 1

        # Several real sources still consume only one project's result.
        actor, _ = begin({modifier: 10 for modifier, _ in RECORDS.values()})
        catalogue(actor)
        click(actor, menu, "rol_family_archive.0001.mars_notes")
        force(actor, menu, "rol_family_archive.0001.ocean_routes")
        assert actor.house.variables == {"rol_family_archive_mars_notes": 1}
        count += 1

        for reason in ("source-expired", "already-recorded", "other-house", "no-house", "missing-snapshot",
                       "transferred", "same-type-decoy", "retired", "changed-mode", "dead", "child", "ai"):
            actor, item = begin()
            catalogue(actor)
            house = actor.house
            if reason == "source-expired": actor.modifiers.clear()
            elif reason == "already-recorded": house.variables["rol_family_archive_mars_notes"] = 1
            elif reason == "other-house": actor.house = Person(activity=None)
            elif reason == "no-house": actor.house = None
            elif reason == "missing-snapshot": actor.scopes.pop("rol_family_archive_house")
            elif reason in ("transferred", "same-type-decoy"):
                item.owner = plain_actor()
                if reason == "same-type-decoy": relic(actor, "rol_ash_forged_mask")
            elif reason == "retired": model.call("rol_relic_use_retire_artifact_effect", actor, {"TYPE": "rol_ash_forged_mask"})
            elif reason == "changed-mode": item.modifiers.pop("rol_relic_use_4_restoration_modifier")
            elif reason == "dead": actor.alive = False
            elif reason == "child": actor.adult = False
            else: actor.ai = True
            before = rewards(actor), dict(house.variables), set(actor.flags), dict(actor.variables)
            choice = "rol_family_archive.0001.mars_notes"
            assert not enabled(actor, menu, choice), f"{reason}: invalid source remains selectable"
            force(actor, menu, choice)
            assert (rewards(actor), dict(house.variables), set(actor.flags), dict(actor.variables)) == before, f"{reason}: invalid preservation changes state"
            count += 1

        for reason in ("empty", "collected", "wrong-mode", "no-house"):
            actor, _ = begin({} if reason == "empty" else None, 7 if reason == "wrong-mode" else 8)
            if reason == "collected": actor.house.variables["rol_family_archive_mars_notes"] = 1
            if reason == "no-house": actor.house = None
            assert not enabled(actor, result, entry), f"{reason}: empty or wrong project offers preservation"
            before = list(actor.queue), rewards(actor), dict(actor.variables)
            force(actor, result, entry)
            assert (list(actor.queue), rewards(actor), dict(actor.variables)) == before
            count += 1

        # Closing the submenu keeps the original project and both ordinary choices.
        for finish in ("a", "b", "preserve"):
            actor, _ = begin()
            catalogue(actor)
            before = rewards(actor), dict(actor.variables), set(actor.flags)
            click(actor, menu, "rol_family_archive.close")
            assert (rewards(actor), dict(actor.variables), set(actor.flags)) == before
            model.decide(actor, "rol_review_relic_use_decision")
            next_window(actor, result)
            if finish == "preserve":
                catalogue(actor)
                actor.gold = -1  # Only the already-paid project is spent at maturity.
                click(actor, menu, "rol_family_archive.0001.mars_notes")
                assert actor.gold == -1 and actor.house.variables == {"rol_family_archive_mars_notes": 1}
            else:
                click(actor, result, "rol_relic_use.0003." + finish)
                assert not actor.house.variables
                assert actor.xp == ({"rol_research": 10} if finish == "a" else {})
                assert actor.prestige == before[0][1] + (100 if finish == "b" else 0)
                force(actor, menu, "rol_family_archive.0001.mars_notes")
                assert not actor.house.variables, "ordinary result can also preserve a manuscript"
            count += 1

        # Old catalogue cannot settle a later annual job, even with the same mask/house.
        actor, item = begin()
        catalogue(actor)
        old_context = dict(actor.scopes)
        model.call("rol_relic_use_record_experience_effect", actor)
        model.advance(actor, 366)
        actor.scopes["rol_relic_use_candidate"] = item
        model.call("rol_relic_use_select_artifact_effect", actor, {"TYPE": "rol_ash_forged_mask", "MODE": 8, "MODIFIER": "rol_relic_use_4_restoration_modifier"})
        next_window(actor, result)
        new_context = dict(actor.scopes)
        assert new_context["rol_relic_use_generation"] != old_context["rol_relic_use_generation"]
        actor.scopes = old_context
        before = rewards(actor), dict(actor.variables), set(actor.flags)
        force(actor, menu, "rol_family_archive.0001.mars_notes")
        assert (rewards(actor), dict(actor.variables), set(actor.flags)) == before and not actor.house.variables, "old catalogue consumes the new project"
        actor.scopes = new_context
        catalogue(actor)
        click(actor, menu, "rol_family_archive.0001.mars_notes")
        assert actor.house.variables == {"rol_family_archive_mars_notes": 1}
        count += 1
        return count
    except (AssertionError, ValueError, KeyError, AttributeError, OSError, IndexError, StopIteration) as error:
        errors.append(f"relic preservation contract: {error}")
        return 0


if __name__ == "__main__":
    issues = []
    count = check_relic_preservation_contract(Path(__file__).resolve().parents[2], issues)
    if issues:
        raise SystemExit("\n".join(issues))
    print(f"[OK] {count} restoration witnesses: genuine sources, original job/house, mutual results and heir editions")
