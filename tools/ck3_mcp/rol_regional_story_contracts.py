"""Execute regional story options from source; excludes engine UI and time."""
from pathlib import Path
from copy import deepcopy
import sys
from rol_growth_contracts import parse, get

ROOT = Path(__file__).resolve().parents[2]
def load(root):
    global EVENTS, DECISIONS, TRIGGERS
    EVENTS = parse((root/'events/rol_asian_sites_events.txt').read_text(encoding='utf-8-sig'))
    DECISIONS = parse((root/'common/decisions/rol_asian_sites_decisions.txt').read_text(encoding='utf-8-sig'))
    TRIGGERS = parse((root/'common/scripted_triggers/rol_regional_story_triggers.txt').read_text(encoding='utf-8-sig'))
load(ROOT)
ROUTES = {'hangzhou': ('010','c_hangzhou'), 'yamashiro': ('020','c_yamashiro'), 'angkor': ('030','c_angkor'), 'baghdad': ('040','c_baghdad')}

def valid(nodes, state):
    for key, op, value in nodes:
        if key == 'NOT': result = not valid(value,state)
        elif key == 'has_character_flag': result = value in state['flags']
        elif key == 'has_title': result = state['title'] == value
        elif key == 'gold' and op == '>=': result = state['gold'] >= float(value)
        elif key == 'rol_regional_story_actor_available_trigger': result = valid(get(TRIGGERS,key),state)
        elif key in ('is_playable_character','is_ai'): result = state.get(key,key=='is_playable_character') == (value=='yes')
        elif key == 'is_available_adult': result = state.get('available',True) == (value=='yes')
        else: raise AssertionError(('unsupported trigger',key,op,value))
        if not result: return False
    return True

def execute(nodes,state):
    for key,op,value in nodes:
        if key in ('name','trigger','custom_tooltip'): continue
        if key == 'add_character_flag': state['flags'].add(value)
        elif key == 'remove_character_flag': state['flags'].discard(value)
        elif key in ('add_gold','add_stress','add_prestige'): state[key[4:]] += float(value)
        elif key == 'trigger_event': state['events'].append(value)
        elif key.startswith('title:'):
            assert state['title'] == key
            execute(value,state)
        elif key in ('add_county_modifier','add_character_modifier'):
            state['rewards'].append(get(value,'modifier'))
        elif key in ('if','else_if','else'):
            raise AssertionError('use dispatch for conditional decisions')
        else: raise AssertionError(('unsupported effect',key))

def options(eid): return [v for k,_,v in get(EVENTS,eid) if k=='option']
def choose(eid,index,state):
    option=options(eid)[index]
    gates=[v for k,_,v in option if k=='trigger']
    if gates and not valid(gates[0],state): return False
    execute(option,state); return True
def dispatch(site,state):
    effects=get(get(DECISIONS,f'rol_{site}_site_decision'),'effect')
    for key,_,body in effects:
        if key=='else' or valid(get(body,'limit'),state):
            return get(body,'trigger_event')
    raise AssertionError('no recovery route')

def audit(site):
    num,title=ROUTES[site]; first,middle,final,epilogue=[f'rol_asian_sites.{num}{n}' for n in ('0','2','1','3')]
    assert get(EVENTS,epilogue)
    for survey in (0,1):
        for outcome in (0,1):
            s={'title':'title:'+title,'flags':set(),'gold':200.,'stress':0.,'prestige':0.,'events':[],'rewards':[]}
            assert dispatch(site,s)==first
            assert not choose(final,0,s) # cannot skip investigation
            assert choose(first,0,s) and dispatch(site,s)==middle
            for key,value in [('available',False),('is_ai',True),('is_playable_character',False)]:
                blocked=deepcopy(s); blocked[key]=value; before=deepcopy(blocked)
                assert not choose(middle,survey,blocked) and blocked==before
            poor=deepcopy(s); poor['gold']=24; before=deepcopy(poor)
            assert not choose(middle,0,poor) and poor==before
            assert choose(middle,survey,s) and dispatch(site,s)==final
            old=deepcopy(s)
            assert not choose(middle,survey,s) and s==old # duplicate paid window
            if outcome==0:
                s['gold']=99; old=deepcopy(s)
                assert not choose(final,0,s) and s==old
                s['gold']=200-(25 if survey==0 else 0)
            title_snapshot=s['title']; s['title']='title:c_other'; old=deepcopy(s)
            assert not choose(final,outcome,s) and s==old
            s['title']=title_snapshot
            for key,value in [('available',False),('is_ai',True),('is_playable_character',False)]:
                blocked=deepcopy(s); blocked[key]=value; before=deepcopy(blocked)
                assert not choose(final,outcome,blocked) and blocked==before
            assert choose(final,outcome,s)
            assert f'rol_{site}_site_finished' in s['flags'] and s['events'][-1]==epilogue
            assert s['gold']==200-(25 if survey==0 else 0)-(100 if outcome==0 else 0)
            assert s['stress']==(10 if survey else 0) and s['prestige']==(100 if outcome else 0)
            assert (f'rol_{site}_site_restored' in s['flags']) == (outcome==0)
            if site=='yamashiro':
                assert ('rol_yamashiro_watch_unlocked' in s['flags']) == (outcome==0)
                assert not s['rewards']
            else:
                reward={'hangzhou':'rol_hangzhou_waterways','angkor':'rol_angkor_reservoir','baghdad':'rol_baghdad_manuscripts'}[site]
                assert s['rewards']==([reward] if outcome==0 else [])
            old=deepcopy(s)
            assert not choose(final,outcome,s) and s==old # reward replay
            assert choose(epilogue,0,s) and s==old # epilogue is read-only
    print('[OK]',site,': outcomes, recovery, availability, duplicate windows, ownership, funds, read-only epilogue')

def check_regional_story_contract(root, errors):
    try:
        load(root)
        for site in ROUTES:
            audit(site)
        legacy=parse((root/'events/rol_new_sites_events.txt').read_text(encoding='utf-8-sig'))
        for eid,title in [('0001','c_alexandria'),('0010','c_jerusalem')]:
            option=[v for k,_,v in get(legacy,'rol_new_sites.'+eid) if k=='option'][0]
            s={'title':'title:'+title,'flags':set(),'gold':200.,'stress':0.,'prestige':0.,'events':[],'rewards':[]}
            assert valid(get(option,'trigger'),s)
            for field,value in [('available',False),('is_ai',True),('is_playable_character',False),('gold',99),('title','title:c_other')]:
                blocked=deepcopy(s); blocked[field]=value
                assert not valid(get(option,'trigger'),blocked)
            execute(option,s)
            assert s['gold']==100 and not valid(get(option,'trigger'),s)
        for filename,unit in [('rol_yamashiro_maa_types.txt','rol_yamashiro_archers'),('rol_jerusalem_maa_types.txt','rol_jerusalem_watch')]:
            maa=get(parse((root/'common/men_at_arms_types'/filename).read_text(encoding='utf-8-sig')),unit)
            assert get(get(maa,'access_through_subject'),'always')=='no'
            expected='rol_yamashiro_watch_unlocked' if unit=='rol_yamashiro_archers' else 'rol_jerusalem_watch_unlocked'
            assert get(get(maa,'can_recruit'),'has_character_flag')==expected
            assert get(maa,'icon')!=unit and get(get(maa,'illustration'),'reference')
        return 6
    except (AssertionError,ValueError,OSError,KeyError) as exc:
        errors.append(f'regional story contract: {exc!r}')
        return 0

if __name__=='__main__':
    for site in sys.argv[1:] or ROUTES:
        audit(site)
