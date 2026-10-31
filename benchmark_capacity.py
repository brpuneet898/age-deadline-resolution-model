"""Small-N exact optimality gap benchmarks, safe for N<=5, short horizons."""
import argparse,json
from pathlib import Path
from m0 import M0
from capacity_dp import Shipment,CapacityProblem
from policies import POLICY_NAMES,build_policy

def example_problem(n=3,capacity=1):
    jobs=[]
    for i in range(n):
        base=.12+.03*(i%3);gain=.22+.035*(i%3)
        p0=lambda a,base=base:max(0.,base-.008*a)
        p1=lambda a,p0=p0,gain=gain:min(1.,p0(a)+gain)
        jobs.append(Shipment(M0(p0,p1,7.+i,80.+10*i),i%2,2+i%3))
    return CapacityProblem(jobs,capacity)

def run(n=3,capacity=1):
    pr=example_problem(n,capacity);opt=pr.exact()
    rows=[]
    for name in POLICY_NAMES:
        result=pr.evaluate_policy(build_policy(name))
        rows.append({'policy':name,'expected_cost':result['value'],
                     'absolute_gap':max(0.,result['value']-opt['value']),
                     'relative_gap':(result['value']-opt['value'])/max(1e-12,abs(opt['value'])),
                     'capacity_violations':result['capacity_violations']})
    return {'optimal':opt,'policies':rows,'note':'Exact small-N benchmark only; no index-policy optimality theorem'}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--n',type=int,default=3)
    parser.add_argument('--capacity',type=int,default=1);parser.add_argument('--output',default='results/capacity_benchmark.json')
    args=parser.parse_args();out=run(args.n,args.capacity)
    path=Path(args.output);path.parent.mkdir(exist_ok=True,parents=True)
    path.write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
