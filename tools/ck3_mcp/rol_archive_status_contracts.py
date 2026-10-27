"""Read-only archive presentation follows live house, copies and printing state.

Selects custom-loc entries using vanilla's documented first-valid rule. This does
not execute Jomini localization expressions, render a window or save engine scopes.
"""
from pathlib import Path
import re

if __package__:
    from .rol_growth_contracts import get, parse
    from .rol_path_contracts import PathModel, Person, optional
    from .rol_family_archive_contracts import RECORDS
else:
    from rol_growth_contracts import get, parse
    from rol_path_contracts import PathModel, Person, optional
    from rol_family_archive_contracts import RECORDS


def check_archive_status_contract(root: Path, errors: list[str], model=None) -> int:
    try:
        model = model if model is not None else PathModel(root)
        definitions = dict((k, v) for k, _, v in parse((root / 'common/customizable_localization/rol_family_archive_custom_loc.txt').read_text(encoding='utf-8-sig')))
        # No setup_scope/effects or randomized entries: reading never changes state.
        for definition in definitions.values():
            assert get(definition, 'type') == 'character'
            assert {key for key, _, _ in definition} == {'type', 'text'}
            for key, _, body in definition:
                if key == 'text':
                    assert {k for k, _, _ in body} <= {'trigger', 'localization_key', 'fallback'}

        def status(actor, name):
            return next(get(v, 'localization_key') for k, _, v in definitions[name] if k == 'text' and model.condition(optional(v, 'trigger', []), actor))

        def row(actor, record):
            return status(actor, 'rol_family_archive_' + record + '_status')

        def short(actor, record):
            return row(actor, record).removeprefix('rol_family_archive_status_')

        def count(actor):
            return model.number('rol_family_archive_record_count_value', actor)

        witnesses = 0
        for record, (modifier, _) in RECORDS.items():
            for archived, held, expected in ((False, False, 'unrecorded_missing'), (False, True, 'unrecorded_copy'),
                                              (True, False, 'saved_missing'), (True, True, 'saved_copy')):
                actor = Person(activity=None, house=Person(activity=None))
                if archived: actor.house.variables['rol_family_archive_' + record] = 1
                if held: actor.modifiers[modifier] = 5
                assert short(actor, record) == expected, f'{record}: house and personal-copy state confused'
                assert count(actor) == int(archived), f'{record}: catalogue counter reads a personal copy or another source'
                # Other rows must not inherit this source's state.
                for other in set(RECORDS) - {record}:
                    assert short(actor, other) == 'unrecorded_missing', f'{record}: status leaks into {other}'
                witnesses += 1
            actor.house = None
            assert short(actor, record) == 'no_house' and count(actor) == 0
            witnesses += 1

        # Real paid actions, time and consumption feed the display without caches.
        actor = Person(activity=None, house=Person(activity=None), gold=1000)
        for record, (modifier, _) in RECORDS.items():
            actor.modifiers[modifier] = 5
            actor.modifier_expires[modifier] = 1825
            model.call('rol_family_archive_open_effect', actor, {'EVENT': 'rol_family_archive.0001'})
            model.call('rol_family_archive_catalogue_effect', actor, {'NAME': record, 'MODIFIER': modifier})
            assert short(actor, record) == 'saved_copy'
        assert count(actor) == 7
        old_house = actor.house
        actor.house = Person(activity=None)
        assert count(actor) == 0 and all(short(actor, record) == 'unrecorded_copy' for record in RECORDS), 'changing house keeps the old collection on display'
        actor.house = old_house
        record, (modifier, _) = next(iter(RECORDS.items()))
        actor.modifiers.pop(modifier)
        assert short(actor, record) == 'saved_missing', 'consumed personal source still displayed as held'
        actor.modifier_expires.pop(modifier)
        model.call('rol_family_archive_open_effect', actor, {'EVENT': 'rol_family_archive.0002'})
        model.call('rol_family_archive_print_effect', actor, {'NAME': record, 'MODIFIER': modifier, 'HEARD_FLAG': 'rol_heard_mars_legend'})
        assert short(actor, record) == 'saved_copy' and count(actor) == 7
        assert status(actor, 'rol_family_archive_print_status') == 'rol_family_archive_status_cooldown'
        model.advance(actor, 1096)
        assert status(actor, 'rol_family_archive_print_status') == 'rol_family_archive_status_ready'
        assert short(actor, record) == 'saved_copy'
        model.advance(actor, 1826)
        assert short(actor, record) == 'saved_missing' and count(actor) == 7
        witnesses += 1

        # Both the decision preview (including blocked entry) and actual catalogue
        # use the same complete inventory, rather than a separately maintained list.
        keys = {get(v, 'localization_key') for definition in definitions.values() for k, _, v in definition if k == 'text'}
        for language in ('english', 'simp_chinese'):
            text = (root / f'localization/{language}/rol_family_archive_l_{language}.yml').read_text(encoding='utf-8-sig')
            loc = dict(re.findall(r'^\s+([\w.-]+):\d*\s+"(.*)"$', text, re.M))
            assert keys <= loc.keys(), f'{language}: custom-loc status text missing'
            for key in ('rol_catalogue_family_knowledge_decision_desc', 'rol_print_family_knowledge_decision_desc', 'rol_family_archive.0001.desc', 'rol_family_archive.0002.desc'):
                assert '$rol_family_archive_inventory$' in loc[key], f'{language}: {key} omits the shared archive view'
            summary = loc['rol_family_archive_inventory']
            for record, (modifier, _) in RECORDS.items():
                assert summary.count(f"ROOT.Char.Custom('rol_family_archive_{record}_status')") == 1
                assert summary.count('$' + modifier + '$') == 1
            assert "ROOT.Char.Custom('rol_family_archive_print_status')" in summary
            assert "ROOT.Char.MakeScope.ScriptValue('rol_family_archive_record_count_value')" in summary
        return witnesses
    except (AssertionError, ValueError, KeyError, AttributeError, OSError, StopIteration) as error:
        errors.append(f'archive status contract: {error}')
        return 0


if __name__ == '__main__':
    issues = []
    result = check_archive_status_contract(Path(__file__).resolve().parents[2], issues)
    if issues:
        raise SystemExit('\n'.join(issues))
    print(f'[OK] {result} archive status witnesses: seven sources, live house/copies, real actions and bilingual wiring')
