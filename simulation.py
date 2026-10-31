"""Paired policy comparison using common random numbers per shipment and decision epoch.
CSV records are replication-level; deterministic with fixed seed and grid configuration.
"""
import argparse,csv,json,random,sys,platform,subprocess
from pathlib import Path
from scenario_grid import scenarios,make_problem,assumed_problem
from policies import POLICY_NAMES,build_policy

def run(reps=10,scenario_limit=2,n=3,seed=20261031,output='results/pilot.csv'):
    if reps<2 or n<1 or (scenario_limit is not None and scenario_limit<1):raise ValueError('bad experiment configuration')
    path=Path(output);path.parent.mkdir(parents=True,exist_ok=True)
    selected=list(scenarios())[:scenario_limit]
    fieldnames=['scenario_id','replication','policy','cost','failures','activations','capacity_violations','seed']
    with path.open('w',newline='',encoding='utf8') as f:
        writer=csv.DictWriter(f,fieldnames=fieldnames);writer.writeheader()
        for s in selected:
            actual=make_problem(s,n)
            assumed=assumed_problem(actual,s['misspecification'])
            # same state definition, capacity and ordering between actual and assumed
            for r in range(reps):
                rng=random.Random(seed+1000003*s['scenario_id']+r)
                matrix=[[rng.random() for t in range(max(j.slack for j in actual.jobs))] for i in range(n)]
                uniform=lambda i,t,matrix=matrix:matrix[i][t]
                for name in POLICY_NAMES:
                    decision=build_policy(name)
                    # policy operates on the assumed model; evolution uses actual independent hazards
                    policy=lambda prob,state,t,decision=decision:decision(assumed,state,t)
                    res=actual.sample(policy,uniform)
                    writer.writerow({'scenario_id':s['scenario_id'],'replication':r,'policy':name,**res,'seed':seed})
    manifest={'reps':reps,'scenario_count':len(selected),'n':n,'seed':seed,
        'scenario_grid_source':'illustrative, MUST be checked against charter',
        'python':sys.version,'platform':platform.platform(),'policy_names':list(POLICY_NAMES),
        'output':str(path),'git_commit':git_commit()}
    path.with_suffix('.manifest.json').write_text(json.dumps(manifest,indent=2))
    return manifest

def git_commit():
    try:return subprocess.check_output(['git','rev-parse','HEAD'],stderr=subprocess.DEVNULL,text=True).strip()
    except (OSError,subprocess.CalledProcessError):return 'not available'

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--reps',type=int,default=10)
    p.add_argument('--scenarios',type=int,default=2,help='432 for all illustrative scenarios')
    p.add_argument('--n',type=int,default=3)
    p.add_argument('--seed',type=int,default=20261031)
    p.add_argument('--output',default='results/pilot.csv')
    a=p.parse_args();print(json.dumps(run(a.reps,a.scenarios,a.n,a.seed,a.output),indent=2))
