"""Actual original guard/envoy work earns expertise and changes the guard's price."""
from pathlib import Path
import traceback

if __package__:
    from .rol_path_contracts import PathModel, Person, plain_actor, start_route, drive, get, optional, CLAIMED
else:
    from rol_path_contracts import PathModel, Person, plain_actor, start_route, drive, get, optional, CLAIMED


def check_field_companion_growth_contract(root: Path, errors: list[str], model=None) -> int:
    witnesses = 0
    try:
        model = model if model is not None else PathModel(root)
        price = 'rol_expedition_guard_route_cost_value'
        personal = 'rol_expedition_guard_personal_cost_value'

        def option(event, name):
            return next(v for k, _, v in model.events[event] if k == 'option' and get(v, 'name') == name)

        def force(actor, event, name):
            model.run(model.option_body(option(event, name)), actor)

        def opening(chain='munich', role=2, xp=0, trait=False, actor=None, peer=None):
            actor = actor if actor is not None else plain_actor()
            actor, definition = start_route(model, chain, actor=actor)
            peer = peer if peer is not None else Person(activity=actor.activity, label='original-specialist', learning=1,
                prowess=20 if role == 2 else 1, diplomacy=20 if role == 3 else 1,
                traits={'rol_relic_seeker'} if trait else set(), xp={'rol_exploration': xp} if xp else {})
            peer.activity = actor.activity
            actor.attendees = [actor, peer]
            actor = drive(model, actor, definition=definition, stop_before='rol_expedition_companion.0001')
            due, event, context = actor.queue.pop(0)
            assert event == 'rol_expedition_companion.0001'
            model.advance(actor, due, definition)
            assert model.dispatch(actor, event, context) is not None
            key = 'rol_expedition_candidate_guard' if role == 2 else 'rol_expedition_candidate_envoy'
            candidate = actor.scopes[key]
            before = dict(candidate.xp), set(candidate.traits)
            if role == 2:
                assert model.number(personal, actor, candidate) == (50 if trait and xp >= 60 else 75)
            model.choose(actor, event, event + ('.b' if role == 2 else '.c'))
            original = actor.variables['rol_expedition_companion_partner']
            assert (dict(original.xp), set(original.traits)) == before, 'signing grants field experience without work'
            event = f'rol_quest_{chain}.1000'
            actor = drive(model, actor, definition=definition, stop_before=event)
            due, queued, context = actor.queue.pop(0)
            assert queued == event
            model.advance(actor, due, definition)
            assert model.dispatch(actor, event, context) is not None
            return actor, actor.variables['rol_expedition_companion_partner'], definition, event

        # Seven real expeditions: aid -> later withdrawal -> return/pay -> cooldown.
        # Withdrawal keeps the destination open for another genuine expedition.
        # The sixth fee is still 75, then the seventh uses that guard's earned 60XP.
        host = plain_actor()
        host.learning = host.martial = host.prowess = host.diplomacy = host.intrigue = host.stewardship = 5
        peer = None
        for job in range(1, 8):
            if job > 1:
                model.advance(host, host.day + 731)
            host, peer, definition, event = opening(actor=host, peer=peer, xp=(job - 1) * 10, trait=job > 1)
            before_gold, host_xp = host.gold, dict(host.xp)
            expected_cost = 50 if job == 7 else 75
            assert model.number(price, host) == expected_cost
            model.choose(host, event, 'rol_expedition_guard_route_option')
            assert host.gold == before_gold - expected_cost and host.xp == host_xp
            assert peer.xp == {'rol_exploration': job * 10} and 'rol_relic_seeker' in peer.traits
            force(host, event, 'rol_expedition_guard_route_option')
            assert peer.xp['rol_exploration'] == job * 10, 'replayed guard work grows twice'
            host = drive(model, host, {'rol_quest_munich.1002': 'rol_quest_munich.1002.c'}, definition=definition)
            assert CLAIMED['munich'] not in host.flags, 'withdrawal unexpectedly completes the destination'
            peer = host.variables['rol_expedition_trusted_companion']
            assert peer.xp == {'rol_exploration': job * 10}, 'return payment trains the specialist again'
        witnesses += 1

        for chain in ('rome', 'munich', 'naxos', 'sevilla', 'carthage'):
            for xp, trait, expected in ((0, False, 75), (59, True, 75), (60, True, 50), (100, False, 75), (100, True, 50)):
                actor, peer, _, event = opening(chain, xp=xp, trait=trait)
                actor.gold = expected
                before = dict(actor.xp), peer.gold, actor.activity['activity_special_type_progression']
                assert model.number(price, actor) == expected
                model.choose(actor, event, 'rol_expedition_guard_route_option')
                assert actor.gold == 0 and actor.xp == before[0] and peer.gold == before[1]
                assert peer.xp == {'rol_exploration': min(100, xp + 10)}
                assert actor.activity['activity_special_type_progression'] == before[2] + 10
                assert actor.activity['rol_expedition_first_trial_used'] == 1
                assert actor.queue[-1][1] == f'rol_quest_{chain}.1010'
                witnesses += 1

        for reason in ('host-master', 'wrong-track', 'other-attendee', 'later-trusted'):
            actor, peer, _, _ = opening()
            if reason == 'host-master':
                actor.traits.add('rol_relic_seeker')
                actor.xp['rol_exploration'] = 100
            elif reason == 'wrong-track':
                peer.traits.add('rol_relic_seeker')
                peer.xp = {'rol_research': 100, 'rol_negotiation': 100}
            else:
                other = Person(activity=actor.activity, label='different-veteran', traits={'rol_relic_seeker'}, xp={'rol_exploration': 100})
                actor.attendees.append(other)
                if reason == 'later-trusted': actor.variables['rol_expedition_trusted_companion'] = other
            assert model.number(price, actor) == 75, f'{reason}: another person or track discounts this guard'
            witnesses += 1

        for xp, limit in ((0, 74), (60, 49)):
            actor, peer, _, event = opening(xp=xp, trait=xp > 0)
            actor.gold = limit
            before = actor.gold, dict(peer.xp), set(peer.traits), list(actor.queue), dict(actor.activity)
            assert not model.condition(get(option(event, 'rol_expedition_guard_route_option'), 'trigger'), actor)
            force(actor, event, 'rol_expedition_guard_route_option')
            assert (actor.gold, dict(peer.xp), set(peer.traits), list(actor.queue), dict(actor.activity)) == before
            witnesses += 1

        for reason in ('left', 'dead', 'child', 'prisoner', 'incapable', 'closed', 'used', 'wrong-role', 'missing'):
            actor, peer, _, event = opening(xp=60, trait=True)
            if reason == 'left': actor.attendees.remove(peer)
            elif reason == 'dead': peer.alive = False
            elif reason == 'child': peer.adult = False
            elif reason == 'prisoner': peer.imprisoned = True
            elif reason == 'incapable': peer.traits.add('incapable')
            elif reason == 'closed': actor.activity['rol_expedition_growth_open'] = 0
            elif reason == 'used': actor.activity['rol_expedition_first_trial_used'] = 1
            elif reason == 'wrong-role': actor.activity['rol_expedition_companion_role'] = 3
            else: actor.variables.pop('rol_expedition_companion_partner')
            before = actor.gold, dict(peer.xp), set(peer.traits), list(actor.queue), dict(actor.activity)
            force(actor, event, 'rol_expedition_guard_route_option')
            assert (actor.gold, dict(peer.xp), set(peer.traits), list(actor.queue), dict(actor.activity)) == before, f'{reason}: invalid guard action still works'
            witnesses += 1

        def encounter():
            actor, envoy, definition, event = opening(role=3)
            rival = Person(activity=actor.activity, label='original-rival')
            actor.attendees.append(rival)
            actor.flags.add('rol_rival_route_nibelung')
            actor.scopes['rol_expedition_rival'] = rival
            model.call('rol_rival_begin_encounter_effect', actor)
            return actor, envoy, rival

        for initial in (0, 59, 95, 100):
            actor, peer, rival = encounter()
            if initial:
                peer.xp['rol_negotiation'] = initial
                peer.traits.add('rol_relic_seeker')
            before = dict(actor.xp), actor.gold, actor.activity['activity_special_type_progression']
            model.choose(actor, 'rol_rival.1000', 'rol_rival.1000.d')
            assert peer.xp == {'rol_negotiation': min(100, initial + 10)} and 'rol_relic_seeker' in peer.traits
            assert actor.xp == before[0] and actor.gold == before[1] and not rival.xp
            assert actor.activity['activity_special_type_progression'] == before[2] + 5
            assert actor.activity['rol_expedition_companion_mediation_used'] == 1
            force(actor, 'rol_rival.1000', 'rol_rival.1000.d')
            assert peer.xp['rol_negotiation'] == min(100, initial + 10)
            witnesses += 1

        for reason in ('left', 'dead', 'incapable', 'used', 'wrong-role', 'rival-dead', 'wrong-rival', 'old-window', 'no-encounter', 'closed'):
            actor, peer, rival = encounter()
            if reason == 'left': actor.attendees.remove(peer)
            elif reason == 'dead': peer.alive = False
            elif reason == 'incapable': peer.traits.add('incapable')
            elif reason == 'used': actor.activity['rol_expedition_companion_mediation_used'] = 1
            elif reason == 'wrong-role': actor.activity['rol_expedition_companion_role'] = 2
            elif reason == 'rival-dead': rival.alive = False
            elif reason == 'wrong-rival': actor.scopes['rol_expedition_rival'] = Person(label='another-rival')
            elif reason == 'old-window': actor.scopes['rol_rival_encounter_generation'] -= 1
            elif reason == 'no-encounter': actor.flags.discard('rol_rival_route_nibelung')
            else: actor.activity['rol_relic_quest_closed'] = 1
            before = dict(actor.xp), dict(peer.xp), set(peer.traits), actor.stress, dict(actor.activity)
            force(actor, 'rol_rival.1000', 'rol_rival.1000.d')
            model.call('rol_expedition_companion_mediate_effect', actor)
            assert (dict(actor.xp), dict(peer.xp), set(peer.traits), actor.stress, dict(actor.activity)) == before, f'{reason}: invalid mediation trains a specialist'
            witnesses += 1

        # Original expertise/chart openings do not train a guard standing nearby.
        for kind in ('expert', 'chart'):
            actor, peer, _, event = opening('sevilla')
            if kind == 'expert':
                actor.traits.add('rol_relic_seeker')
                actor.xp['rol_research'] = 60
                choice = 'rol_expedition_expert_route_option'
            else:
                actor.modifiers['rol_star_observations_modifier'] = 10
                choice = 'rol_archive_sevilla_route_option'
            model.choose(actor, event, choice)
            force(actor, event, 'rol_expedition_guard_route_option')
            assert not peer.xp and 'rol_relic_seeker' not in peer.traits, f'{kind}: bystander receives guard practice'
            witnesses += 1

        for language in ('english', 'simp_chinese'):
            text = (root / f'localization/{language}/rol_expedition_companion_l_{language}.yml').read_text(encoding='utf-8-sig')
            terms = next(line for line in text.splitlines() if ' rol_expedition_companion_guard_terms_tt:' in line)
            action = next(line for line in text.splitlines() if ' rol_expedition_guard_route_tt:' in line)
            assert f"rol_expedition_candidate_guard.MakeScope.ScriptValue('{personal}')" in terms
            assert f"SCOPE.ScriptValue('{price}')" in action, "guard price must retain the event's activity scope"
        return witnesses
    except (AssertionError, ValueError, KeyError, AttributeError, OSError, IndexError, StopIteration) as error:
        line = traceback.extract_tb(error.__traceback__)[-1].lineno
        errors.append(f'field companion growth contract, line {line}: {error}')
        return 0


if __name__ == '__main__':
    issues = []
    result = check_field_companion_growth_contract(Path(__file__).resolve().parents[2], issues)
    if issues:
        raise SystemExit('\n'.join(issues))
    print(f'[OK] {result} field-growth witnesses: earned original-person work, five route prices, caps, replay and separate payment')
