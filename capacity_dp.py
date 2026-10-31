"""Exact finite-N joint capacity DP with independent Bernoulli outcomes.
Resolved jobs never re-enter. Terminal jobs are charged at their deadlines.
"""
from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
from itertools import combinations,product
from math import isfinite
from m0 import M0,integer

@dataclass(frozen=True)
class Shipment:
    model: M0
    age: int
    slack: int
    def __post_init__(self):
        integer(self.age,'age');integer(self.slack,'slack')
        if not isinstance(self.model,M0):raise ValueError('model must be M0')

class CapacityProblem:
    def __init__(self,shipments,capacity):
        if not isinstance(shipments,(list,tuple)) or not shipments:
            raise ValueError('nonempty shipment list required')
        self.jobs=tuple(shipments)
        for j in self.jobs:
            if not isinstance(j,Shipment): raise ValueError('invalid shipment')
        integer(capacity,'capacity');self.capacity=capacity
        self.n=len(self.jobs)
        self.base_state=tuple(0 if j.slack>0 else -1 for j in self.jobs)
        self.initial_terminal=sum(j.model.K for j in self.jobs if j.slack==0)

    def eligible(self,state,t):
        return tuple(i for i,j in enumerate(self.jobs) if state[i]==0 and t<j.slack)

    def action_sets(self,state,t):
        elig=self.eligible(state,t)
        return (frozenset(sub) for z in range(min(self.capacity,len(elig))+1)
                for sub in combinations(elig,z))

    def transitions(self,state,t,selected):
        elig=self.eligible(state,t)
        for outcomes in product((0,1),repeat=len(elig)):
            prob=1.;next_state=list(state);terminal=0.
            for i,success in zip(elig,outcomes):
                job=self.jobs[i]
                p=job.model.probability(int(i in selected),job.age+t)
                prob*=p if success else 1-p
                if success:next_state[i]=1
                elif t+1>=job.slack:
                    next_state[i]=-1;terminal+=job.model.K
            if prob:yield prob,tuple(next_state),terminal

    def exact(self):
        @lru_cache(None)
        def rec(t,state):
            elig=self.eligible(state,t)
            if not elig:return 0.,()
            best=float('inf');chosen=()
            for sub in self.action_sets(state,t):
                immediate=sum(self.jobs[i].model.c for i in sub)
                val=immediate+sum(p*(penalty+rec(t+1,next_state)[0])
                                  for p,next_state,penalty in self.transitions(state,t,sub))
                ordered=tuple(sorted(sub))
                if val<best-1e-12 or (abs(val-best)<=1e-12 and (len(ordered),ordered)<(len(chosen),chosen)):
                    best=val;chosen=ordered
            return best,chosen
        value,action=rec(0,self.base_state)
        return {'value':value+self.initial_terminal,'initial_action':list(action),
                'states':rec.cache_info().currsize,'certificate':'exhaustive feasible joint-action Bellman enumeration',
                'capacity':self.capacity,'N':self.n}

    def evaluate_policy(self,policy):
        """Exact expected cost under a deterministic feasible policy."""
        @lru_cache(None)
        def rec(t,state):
            eligible=self.eligible(state,t)
            if not eligible:return 0.
            chosen=frozenset(policy(self,state,t))
            if not chosen.issubset(eligible) or len(chosen)>self.capacity:
                raise ValueError(f'capacity or eligibility violation at time {t}: {chosen}')
            return sum(self.jobs[i].model.c for i in chosen)+sum(
                p*(penalty+rec(t+1,next_state)) for p,next_state,penalty in self.transitions(state,t,chosen))
        val=rec(0,self.base_state)+self.initial_terminal
        return {'value':val,'states':rec.cache_info().currsize,'capacity_violations':0}

    def sample(self,policy,rng_uniform):
        """One sample path; rng_uniform(i,t) supplies common random numbers for each job/epoch."""
        state=list(self.base_state);cost=self.initial_terminal;failures=sum(s==-1 for s in state)
        total_acts=0
        for t in range(max(j.slack for j in self.jobs)):
            elig=self.eligible(state,t)
            if not elig:break
            selected=frozenset(policy(self,tuple(state),t))
            if len(selected)>self.capacity or not selected.issubset(elig):
                raise ValueError('capacity/eligibility violation')
            total_acts+=len(selected);cost+=sum(self.jobs[i].model.c for i in selected)
            for i in elig:
                job=self.jobs[i]
                if rng_uniform(i,t)<job.model.probability(int(i in selected),job.age+t):state[i]=1
                elif t+1>=job.slack:state[i]=-1;failures+=1;cost+=job.model.K
        return {'cost':cost,'failures':failures,'activations':total_acts,'capacity_violations':0}
