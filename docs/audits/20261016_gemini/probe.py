"""Read-only diagnostic evidence for the unmodified 2026-10-15 Gemini delivery.

This reproduces defects using the maintained finite source interpreter; no CK3
process, console, UI or mod script is modified. Expected defect assertions must
be updated after fixes. It is not an engine integration test.
"""
from pathlib import Path
import sys,json,re,argparse
args=argparse.ArgumentParser()
args.add_argument('--root',type=Path,default=Path(r'C:\CK3Mods\ROL-gemini\RoL'))
args.add_argument('--baseline',type=Path,default=Path(r'C:\CK3Mods\RoL'))
opts=args.parse_args()
ROOT=opts.root
sys.path.insert(0,str(ROOT/'tools/ck3_mcp'))
from rol_path_contracts import PathModel,Person,plain_actor,start_route,drive,get,optional,relic,CLAIMED
m=PathModel(ROOT)
report={}
# Execute actual on_start via the maintained interpreter and native progression code.
starts={}
for chain in ('rome','munich','naxos','sevilla','carthage'):
    starts[chain]={}
    for prep in ('standard','supreme'):
        a,definition=start_route(m,chain,actor=plain_actor())
        # start_route's callback defaults to standard even for a supreme host.
        # Supply the real selected option to both actors when isolating the hook.
        a.preparation=prep;a.stress=20;a.activity={"_activity_type":a.activity['_activity_type']}
        a.scopes={'host':a,'activity':a.activity};a.attendees=[a]
        callback=Person(activity=a.activity,scopes=a.scopes,attendees=a.attendees,preparation=prep,label='activity-root')
        m.run(get(definition,'on_start'),callback,'activity')
        starts[chain][prep]={'progress':a.activity['activity_special_type_progression'],'stress':a.stress}
report['start_bonus']=starts

def option(event,name):
    return next(v for k,_,v in m.events[event] if k=='option' and get(v,'name')==name)

# A saved event window executes option effects; it does not dispatch the event again.
a=plain_actor();a.flags.add('rol_fragment_upgrade_pending')
body=m.option_body(option('rol_relic_fragment.0002','rol_relic_fragment.0002.a'))
m.run(body,a);first=(a.prestige,dict(a.xp));m.run(body,a)
report['fragment_saved_window_replay']={'after_first':first,'after_second':(a.prestige,a.xp)}

# Read every failure outcome feeding a remedied stage and sum native progress effects.
def walk(nodes):
    for k,op,v in nodes:
        yield k,op,v
        if isinstance(v,list):yield from walk(v)
def rnd(nodes):
    for k,_,v in nodes:
        if k=='random_list':yield v
        elif isinstance(v,list):yield from rnd(v)
deltas={}
for ev,nodes in m.events.items():
    if not ev.startswith('rol_quest_'):continue
    for rl in rnd(nodes):
        for _,_,outcome in rl:
            if not isinstance(outcome,list):continue
            targets=[get(v,'id') for k,_,v in walk(outcome) if k=='trigger_event' and isinstance(v,list)]
            if not any(re.search(r'\.(1011|1021|1031|1041)$',t) for t in targets):continue
            delta=0
            for key,_,_ in walk(outcome):
                if key in m.native:
                    for nk,_,nv in walk(m.native[key]):
                        if nk=='change_variable' and get(nv,'name')=='activity_special_type_progression':
                            delta+=float(get(nv,'add'))
            deltas.setdefault(ev.split('.')[0],{}).setdefault(str(delta),0)
            deltas[ev.split('.')[0]][str(delta)]+=1
report['remedied_failure_progress_deltas']=deltas

# Full production witness: main success + rival .c success + final roll failure.
a,definition=start_route(m,'munich',company=True,actor=plain_actor())
a.traits.add('rol_relic_seeker')
a=drive(m,a,{'rol_expedition_companion.0001':'rol_expedition_companion.0001.d',
             'rol_rival.1000':'rol_rival.1000.c'},definition,stop_before='rol_quest_munich.1002')
before=a.activity['activity_special_type_progression']
day,ev,ctx=a.queue.pop(0);m.advance(a,day,definition);m.dispatch(a,ev,ctx)
failed=list(m.alternatives(m.option_body(option(ev,'rol_quest_munich.1002.a')),a))[1]
after_fail=failed.activity['activity_special_type_progression']
failed=drive(m,failed,definition=definition,stop_before='rol_expedition_growth.0010')
day,ev,ctx=failed.queue.pop(0);m.advance(failed,day,definition);m.dispatch(failed,ev,ctx)
m.run(m.option_body(option(ev,'rol_expedition_growth.0010.b')),failed)
report['real_salvage_tier4_witness']={'before_final':before,'after_final_failure':after_fail,
    'tier':failed.variables.get('rol_recent_relic_result_tier'),'artifacts':len(failed.artifacts),
    'full_flag':CLAIMED['munich'] in failed.flags,'trace':failed.trace}

# Old inactive crisis window must not erase a different activity's pending crisis.
a,definition=start_route(m,'munich',actor=plain_actor());old_ctx=dict(a.scopes)
old_ctx['activity']['rol_relic_quest_closed']=1
a.scopes={};a.activity=None;a.available=True;a.queue=[];a.phase_end=None
a.flags.discard('rol_relic_context_nibelung')
a,newdef=start_route(m,'rome',actor=a);new_ctx=dict(a.scopes)
a.activity['rol_expedition_remedy_used']=1;a.flags.add('rol_expedition_remedy_pending')
before=m.condition(m.triggers['rol_expedition_remedy_window_valid_trigger'],a)
a.scopes=old_ctx
close=option('rol_expedition_growth.0010','rol_expedition_growth.0010.d')
old_close_available=m.condition(get(close,'trigger'),a)
m.run(m.option_body(close),a);a.scopes=new_ctx
report['old_remedy_close_erases_new']={'new_valid_before':before,'old_close_available':old_close_available,
    'new_valid_after':m.condition(m.triggers['rol_expedition_remedy_window_valid_trigger'],a),
    'pending_after':'rol_expedition_remedy_pending' in a.flags}

# Existing fully rewarded saves already have both permanent circle modifiers.
a=plain_actor();a.flags.update(CLAIMED.values());a.flags.update({'rol_legend_circle_revealed','rol_legend_circle_fivefold_revealed',
    'rol_legend_circle_0001_reward_claimed','rol_legend_circle_0002_reward_claimed'})
a.modifiers['rol_legend_circle_conqueror_modifier']=None;a.modifiers['rol_legend_circle_fivefold_modifier']=None
report['legacy_circle_migration']={'fivefold_event_available':m.condition(get(m.events['rol_legend_circle.0002'],'trigger'),a),
    'modifiers':list(a.modifiers),'cleanup_references':[(str(p.relative_to(ROOT)),i) for p in (ROOT/'common').rglob('*.txt')
        for i,line in enumerate(p.read_text(encoding='utf-8-sig').splitlines(),1) if 'remove_character_modifier = rol_legend_circle_conqueror_modifier' in line]}

circle_orders=[]
for order in [('0001','0002'),('0002','0001')]:
    a=plain_actor();a.flags.update(CLAIMED.values());a.flags.update({'rol_legend_circle_revealed','rol_legend_circle_fivefold_revealed'})
    before=a.dynasty.prestige
    for suffix in order:
        ev='rol_legend_circle.'+suffix
        m.run(m.option_body(option(ev,ev+'.a')),a)
    circle_orders.append({'order':order,'dynasty_prestige_awarded':a.dynasty.prestige-before,
        'dynasty_modifiers':list(a.dynasty.modifiers),'fourfold_reward_claimed':'rol_legend_circle_0001_reward_claimed' in a.flags})
report['circle_choice_order']=circle_orders

# Check every true relic pair and loss after the doctrine has been chosen.
from itertools import combinations
types=['rol_blade_of_mars','rol_nibelung_star_sphere','rol_astrolabe_of_ocean','rol_ash_forged_mask','naxos']
pairs=[]
for pair in combinations(types,2):
    a=plain_actor()
    for item in pair:
        if item=='naxos':a.flags.add(CLAIMED['naxos'])
        else:relic(a,item)
    assert m.condition(m.triggers['rol_relic_count_at_least_two_trigger'],a)
    pairs.append(pair)
report['harmonization_pairs']=pairs
a=plain_actor();r1=relic(a,types[0]);r2=relic(a,types[1])
m.decide(a,'rol_harmonize_relics_decision');a=drive(m,a,{'rol_relic_legacy.0010':'rol_relic_legacy.0010.c'})
for item in a.artifacts:item.owner=plain_actor()
report['harmonization_after_loss']={'qualifies':m.condition(m.triggers['rol_relic_count_at_least_two_trigger'],a),
    'modifiers':list(a.modifiers),'expires':a.modifier_expires}

# Verify exact chance formula on threshold boundaries, including XP60.
odds=[]
for stat in (5,14,15,21,22,30):
    for xp in (0,60):
        a=plain_actor();a.learning=a.prowess=a.stewardship=stat
        if xp:a.traits.add('rol_relic_seeker')
        a.xp={'rol_research':xp,'rol_exploration':xp,'rol_negotiation':xp}
        chances={}
        for attr in ('learning','prowess','stewardship'):
            s=m.number('rol_fragment_'+attr+'_success_chance_value',a)
            f=m.number('rol_fragment_'+attr+'_failure_chance_value',a)
            assert s+f==100
            chances[attr]=s
        odds.append({'stat':stat,'xp':xp,**chances})
report['fragment_odds']=odds

# Localization values must end on their own physical line in Clausewitz localization.
broken=[]
for p in (ROOT/'localization').rglob('*.yml'):
    for n,line in enumerate(p.read_text(encoding='utf-8-sig').splitlines(),1):
        if re.match(r'^\s*\w[\w.]*:\d*\s+"',line) and not re.search(r'(?<!\\)"\s*(?:#.*)?$',line.split('"',1)[1]):
            broken.append({'file':p.relative_to(ROOT).as_posix(),'line':n,'key':line.split(':')[0].strip()})
for row in broken:
    baseline=opts.baseline/row['file']
    baseline_lines=baseline.read_text(encoding='utf-8-sig').splitlines()
    original=next(s for s in baseline_lines if re.match(r'^\s*'+re.escape(row['key'])+r':',s))
    row['new_regression']=original.rstrip().endswith('"')
report['multiline_localization_keys']=broken
assert all(v['standard']['progress']==v['supreme']['progress'] and
           v['standard']['stress']-v['supreme']['stress']==15 for v in starts.values())
assert report['fragment_saved_window_replay']['after_second'][0]-first[0]==75
assert report['real_salvage_tier4_witness']['tier']==4 and not report['real_salvage_tier4_witness']['full_flag']
assert report['old_remedy_close_erases_new']=={'new_valid_before':True,'old_close_available':True,'new_valid_after':False,'pending_after':False}
assert [v['dynasty_prestige_awarded'] for v in circle_orders]==[1500,1000]
assert report['legacy_circle_migration']['fivefold_event_available'] is False
assert sum(r['new_regression'] for r in broken)==8 and len(broken)==26
out=Path(__file__).with_name('probe_results.json')
out.write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
