"""Feasible priority policies. Restricted critical-cost ranking is a heuristic for joint DP."""
from functools import lru_cache

def build_policy(name):
    options=('critical_cost','failure_risk','earliest_deadline','myopic_benefit','never_active')
    if name not in options:raise ValueError(f'Unknown policy {name}; choose from {options}')
    @lru_cache(maxsize=100000)
    def critical(model,age,slack):return model.critical_cost(age,slack)
    def policy(problem,state,t):
        elig=problem.eligible(state,t)
        def score(i):
            job=problem.jobs[i];m=job.model;a=job.age+t;l=job.slack-t
            p0,p1=m.hazards(a)
            if name=='critical_cost':return critical(m,a,l)
            if name=='failure_risk':
                surv=1.
                for j in range(l):surv*=1-m.probability(0,a+j)
                return surv*m.K
            if name=='earliest_deadline':return -l
            if name=='myopic_benefit':return (p1-p0)*m.solve(a+1,l-1)[0]-m.c
            return -float('inf')
        if name=='never_active':return ()
        ranked=sorted(elig,key=lambda i:(-score(i),i))
        if name=='earliest_deadline':return tuple(ranked[:problem.capacity])
        return tuple(i for i in ranked if score(i)>0)[:problem.capacity]
    return policy

POLICY_NAMES=('critical_cost','failure_risk','earliest_deadline','myopic_benefit','never_active')
