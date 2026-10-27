"""A trained original envoy's accord feeds the existing original-rival reunion."""
from pathlib import Path
import traceback

if __package__:
    from .rol_path_contracts import PathModel, Person, get, optional, plain_actor, start_route, drive, CLAIMED
else:
    from rol_path_contracts import PathModel, Person, get, optional, plain_actor, start_route, drive, CLAIMED


def check_envoy_accord_contract(root: Path, errors: list[str], model=None) -> int:
    try:
        model = model if model is not None else PathModel(root)
        event, accord, free = 'rol_rival.1000', 'rol_expedition_envoy_accord_option', 'rol_rival.1000.d'
        memory, snapshot = 'rol_rival_relationship_partner', 'rol_rival_encounter_envoy'
        witnesses = 0

        def option(name):
            return next(v for k, _, v in model.events[event] if k == 'option' and get(v, 'name') == name)

        def enabled(actor, name=accord):
            return model.condition(optional(option(name), 'trigger', []), actor)

        def force(actor, name=accord):
            model.run(model.option_body(option(name)), actor)

        def click(actor, name=accord):
            assert enabled(actor, name), f'accord option unavailable: {name}'
            force(actor, name)
            model.options_seen.add((event, name))

        def next_window(actor, expected, definition):
            actor.queue.sort(key=lambda q: q[0])
            day, queued, context = actor.queue.pop(0)
            assert queued == expected, (expected, queued)
            model.advance(actor, day, definition)
            assert model.dispatch(actor, queued, context) is not None

        def encounter(actor=None, envoy=None, rival=None, xp=60, trait=True):
            if actor is None:
                actor = plain_actor()
                actor.learning = actor.martial = actor.prowess = actor.diplomacy = actor.intrigue = actor.stewardship = 5
            actor, definition = start_route(model, 'munich', actor=actor)
            envoy = envoy if envoy is not None else Person(activity=actor.activity, label='original-envoy',
                learning=1, prowess=1, diplomacy=20, xp={'rol_negotiation': xp} if xp else {},
                traits={'rol_relic_seeker'} if trait else set())
            rival = rival if rival is not None else Person(activity=actor.activity, label='original-rival',
                learning=1, prowess=1, diplomacy=1)
            envoy.activity = rival.activity = actor.activity
            actor.attendees = [actor, envoy, rival]
            actor = drive(model, actor, {'rol_expedition_companion.0001': 'rol_expedition_companion.0001.c'},
                          definition=definition, stop_before='rol_quest_munich.1000')
            next_window(actor, 'rol_quest_munich.1000', definition)
            body = next(v for k, _, v in model.events['rol_quest_munich.1000'] if k == 'option' and get(v, 'name') == 'rol_quest_munich.1000.a')
            actor = next(a for a in model.alternatives(model.option_body(body), actor) if any(q[1] == 'rol_quest_munich.1010' for q in a.queue))
            next_window(actor, 'rol_quest_munich.1010', definition)
            body = get(model.events['rol_quest_munich.1010'], 'option')
            actor = next(a for a in model.alternatives(model.option_body(body), actor) if any(q[1] == event for q in a.queue))
            queued = next(q for q in actor.queue if q[1] == event)
            assert queued[2][snapshot] is actor.variables['rol_expedition_companion_partner'], 'dispatcher did not capture its original envoy before the delay'
            next_window(actor, event, definition)
            return actor, actor.variables['rol_expedition_companion_partner'], actor.scopes['rol_expedition_rival'], definition

        def withdraw(actor, definition):
            actor = drive(model, actor, {'rol_quest_munich.1002': 'rol_quest_munich.1002.c'}, definition=definition)
            assert CLAIMED['munich'] not in actor.flags
            envoy = actor.variables['rol_expedition_trusted_companion']
            rival = next(p for p in actor.attendees if p.label == 'original-rival')
            return actor, envoy, rival

        def state(actor, envoy, rival):
            return (actor.prestige, actor.gold, actor.stress, dict(actor.xp), dict(actor.variables), set(actor.flags),
                    dict(envoy.xp), list(envoy.opinions), dict(rival.xp), list(rival.opinions),
                    actor.activity['activity_special_type_progression'], list(actor.activity.get('_log_records', [])))

        # Six real free mediations -> full return/payment -> cooldown, on the same
        # original envoy. Job seven buys memory; job eight consumes that memory.
        actor = envoy = rival = None
        for job in range(1, 7):
            if actor is not None: model.advance(actor, actor.day + 731)
            actor, envoy, rival, definition = encounter(actor, envoy, rival, xp=0, trait=False)
            assert not enabled(actor), 'unearned accord before the original envoy reaches 60'
            before = actor.prestige, dict(actor.xp)
            click(actor, free)
            assert envoy.xp == {'rol_negotiation': job * 10} and actor.prestige == before[0] and actor.xp == before[1]
            consumed = state(actor, envoy, rival)
            force(actor)
            assert state(actor, envoy, rival) == consumed, 'crossing 60 reopens an already consumed mediation'
            actor, envoy, rival = withdraw(actor, definition)
            assert envoy.xp == {'rol_negotiation': job * 10}, 'return credit grows the envoy again'
        model.advance(actor, actor.day + 731)
        actor, envoy, rival, definition = encounter(actor, envoy, rival)
        before = actor.prestige, actor.stress, dict(actor.xp), actor.activity['activity_special_type_progression']
        click(actor)
        assert actor.prestige == before[0] - 75 and actor.stress == max(0, before[1] - 10)
        assert actor.xp == before[2] and actor.activity['activity_special_type_progression'] == before[3] + 5
        assert envoy.xp == {'rol_negotiation': 70} and not rival.xp
        assert actor.variables[memory] is rival and actor.expires['rol_rival_cooperation_active'] == actor.day + 3650
        assert 'rol_rival_pact_choice_pending' not in actor.flags and 'rol_rival_pact_partner' not in actor.variables
        assert actor.activity['rol_expedition_companion_mediation_used'] == 1
        records = actor.activity['_log_records']
        assert [r['target'] for r in records if r['key'] == 'rol_expedition_feedback_envoy_accord'] == [rival.label]
        assert [r['target'] for r in records if r['key'] == 'rol_expedition_feedback_mediation'] == [envoy.label]
        consumed = state(actor, envoy, rival)
        force(actor)
        force(actor, free)
        assert state(actor, envoy, rival) == consumed
        actor, envoy, rival = withdraw(actor, definition)
        model.advance(actor, actor.day + 731)
        actor, envoy, rival, definition = encounter(actor, envoy, rival)
        roll = next(v for k, _, v in model.selected(model.effects['rol_try_rival_interlude_effect'], actor, 'actor') if k == 'random_list')
        assert [float(k) for k, _, _ in roll] == [75, 25] and actor.variables[memory] is rival
        assert not enabled(actor), 'existing same-person cooperation can be charged/renewed'
        before = actor.prestige, dict(actor.xp), dict(envoy.xp), actor.activity['activity_special_type_progression']
        click(actor, 'rol_rival_reunion_research_option')
        assert (actor.prestige, actor.xp, envoy.xp) == before[:3]
        assert actor.activity['activity_special_type_progression'] == before[3] + 5
        witnesses += 1

        for xp, trait, available in ((0, False, False), (59, True, False), (60, True, True), (100, True, True), (100, False, False)):
            actor, envoy, rival, _ = encounter(xp=xp, trait=trait)
            actor.prestige = 75
            assert enabled(actor) == available
            if available:
                click(actor)
                assert actor.prestige == 0 and envoy.xp == {'rol_negotiation': min(100, xp + 10)}
            else:
                before = state(actor, envoy, rival)
                force(actor)
                assert state(actor, envoy, rival) == before
                assert enabled(actor, free), 'ordinary free mediation lost at a mastery boundary'
            witnesses += 1

        for reason in ('poor', 'wrong-track', 'host-master', 'other-veteran', 'no-snapshot', 'wrong-snapshot',
                       'swapped-contract', 'left', 'dead', 'prisoner', 'incapable', 'wrong-role', 'used',
                       'rival-dead', 'wrong-rival', 'old-generation', 'missing-generation', 'closed', 'already-cooperating'):
            actor, envoy, rival, _ = encounter(xp=0 if reason in ('host-master', 'other-veteran') else 60)
            if reason == 'poor': actor.prestige = 74
            elif reason == 'wrong-track': envoy.xp = {'rol_research': 100, 'rol_exploration': 100}
            elif reason == 'host-master': actor.traits.add('rol_relic_seeker'); actor.xp['rol_negotiation'] = 100
            elif reason in ('other-veteran', 'wrong-snapshot', 'swapped-contract'):
                other = Person(activity=actor.activity, label='replacement-envoy', traits={'rol_relic_seeker'}, xp={'rol_negotiation': 100})
                actor.attendees.append(other)
                if reason == 'wrong-snapshot': actor.scopes[snapshot] = other
                if reason == 'swapped-contract': actor.variables['rol_expedition_companion_partner'] = other
            elif reason == 'no-snapshot': actor.scopes.pop(snapshot)
            elif reason == 'left': actor.attendees.remove(envoy)
            elif reason == 'dead': envoy.alive = False
            elif reason == 'prisoner': envoy.imprisoned = True
            elif reason == 'incapable': envoy.traits.add('incapable')
            elif reason == 'wrong-role': actor.activity['rol_expedition_companion_role'] = 2
            elif reason == 'used': actor.activity['rol_expedition_companion_mediation_used'] = 1
            elif reason == 'rival-dead': rival.alive = False
            elif reason == 'wrong-rival': actor.scopes['rol_expedition_rival'] = Person(label='another-rival')
            elif reason == 'old-generation':
                context = dict(actor.scopes)
                model.call('rol_rival_begin_encounter_effect', actor)
                actor.scopes = context
            elif reason == 'missing-generation': actor.scopes.pop('rol_rival_encounter_generation')
            elif reason == 'closed': actor.activity['rol_relic_quest_closed'] = 1
            else:
                actor.variables[memory] = rival
                actor.flags.add('rol_rival_cooperation_active')
            assert not enabled(actor), f'{reason}: invalid accord available'
            before = state(actor, envoy, rival)
            force(actor)
            model.call('rol_expedition_envoy_accord_effect', actor)
            assert state(actor, envoy, rival) == before, f'{reason}: invalid accord changes state'
            witnesses += 1

        for attitude in ('grudge', 'other-person', 'existing-pact', 'later-trusted'):
            actor, envoy, rival, _ = encounter()
            other = Person(label='prior-person')
            actor.variables[memory] = rival if attitude == 'grudge' else other
            actor.flags.add('rol_rival_grudge_active')
            if attitude == 'existing-pact':
                actor.flags.add('rol_rival_pact_choice_pending')
                actor.variables.update(rol_rival_pact_partner=other, rol_rival_pact_generation=7)
            if attitude == 'later-trusted': actor.variables['rol_expedition_trusted_companion'] = other
            click(actor)
            assert actor.variables[memory] is rival and 'rol_rival_grudge_active' not in actor.flags and 'rol_rival_cooperation_active' in actor.flags
            assert envoy.xp['rol_negotiation'] == 70 and not other.xp
            if attitude == 'existing-pact':
                assert actor.variables['rol_rival_pact_partner'] is other and actor.variables['rol_rival_pact_generation'] == 7 and 'rol_rival_pact_choice_pending' in actor.flags
            witnesses += 1

        # Old queued saves have no envoy snapshot; keep their original free path.
        actor, envoy, rival, _ = encounter()
        actor.scopes.pop(snapshot)
        before = actor.prestige
        click(actor, free)
        assert actor.prestige == before and envoy.xp['rol_negotiation'] == 70 and memory not in actor.variables
        witnesses += 1

        actor, envoy, rival, _ = encounter()
        actor.activity['rol_expedition_companion_role'] = 2
        model.call('rol_rival_begin_encounter_effect', actor)
        actor.activity['rol_expedition_companion_role'] = 3
        assert snapshot not in actor.scopes and not enabled(actor), 'a later encounter reuses an envoy absent from its dispatch'
        assert enabled(actor, free)
        witnesses += 1
        return witnesses
    except (AssertionError, ValueError, KeyError, AttributeError, OSError, IndexError, StopIteration) as error:
        line = traceback.extract_tb(error.__traceback__)[-1].lineno
        errors.append(f'envoy accord contract, line {line}: {error}')
        return 0


if __name__ == '__main__':
    issues = []
    result = check_envoy_accord_contract(Path(__file__).resolve().parents[2], issues)
    if issues:
        raise SystemExit('\n'.join(issues))
    print(f'[OK] {result} envoy-accord witnesses: six actual jobs, original envoy/rival, cost/replay and real later reunion')
