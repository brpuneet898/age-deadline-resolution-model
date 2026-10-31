"""Single-shipment M0: independent of external/private datasets.
Decision at start of interval, success during last interval is timely.
Tie convention: passive (u=0). Terminal unresolved penalty K.
"""
from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
from itertools import product
from math import isfinite
from typing import Callable

Hazard = Callable[[int], float]

def integer(value, name):
    if type(value) is not int or value < 0:
        raise ValueError(f'{name} must be a nonnegative integer (bool excluded)')
    return value

def finite(value, name):
    if isinstance(value, bool) or not isinstance(value, (int,float)) or not isfinite(value):
        raise ValueError(f'{name} must be a finite real number')
    return float(value)

@dataclass(frozen=True)
class M0:
    p0: Hazard
    p1: Hazard
    c: float = 8.
    K: float = 100.

    def __post_init__(self):
        if not callable(self.p0) or not callable(self.p1):
            raise ValueError('hazards must be callable')
        if finite(self.c,'c') < 0 or finite(self.K,'K') < 0:
            raise ValueError('c and K must be nonnegative')

    def hazards(self, age):
        integer(age,'age')
        p0,p1 = finite(self.p0(age),'p0'),finite(self.p1(age),'p1')
        if not 0 <= p0 <= p1 <= 1:
            raise ValueError(f'require 0 <= p0({age}) <= p1({age}) <= 1; got {p0}, {p1}')
        return p0,p1

    def probability(self,u,age):
        if type(u) is not int or u not in (0,1):
            raise ValueError('action must be 0 or 1')
        return self.hazards(age)[u]

    @staticmethod
    def _params(charge,passive_subsidy):
        charge,passive_subsidy=finite(charge,'charge'),finite(passive_subsidy,'passive_subsidy')
        if charge != 0 and passive_subsidy != 0:
            raise ValueError('charge and passive subsidy must not be combined')
        return charge,passive_subsidy

    def solve(self,age,slack,*,charge=0.,passive_subsidy=0.):
        integer(age,'age'); integer(slack,'slack')
        charge,sub=self._params(charge,passive_subsidy)
        @lru_cache(None)
        def rec(a,l):
            if l == 0: return (float(self.K),0)
            cont=rec(a+1,l-1)[0]
            p0,p1=self.hazards(a)
            passive=-sub+(1-p0)*cont
            active=self.c+charge+(1-p1)*cont
            return (passive,0) if passive <= active else (active,1)
        return rec(age,slack)

    def action_values(self,age,slack,*,charge=0.,passive_subsidy=0.):
        integer(age,'age');integer(slack,'slack')
        charge,sub=self._params(charge,passive_subsidy)
        if slack == 0: return (self.K,self.K) # no decision exists at zero slack
        cont=self.solve(age+1,slack-1,charge=charge,passive_subsidy=sub)[0]
        p0,p1=self.hazards(age)
        return (-sub+(1-p0)*cont,self.c+charge+(1-p1)*cont)

    def evaluate_sequence(self,age,slack,actions,*,charge=0.,passive_subsidy=0.):
        integer(age,'age');integer(slack,'slack')
        charge,sub=self._params(charge,passive_subsidy)
        if not isinstance(actions,(tuple,list)) or len(actions)!=slack or any(type(u) is not int or u not in (0,1) for u in actions):
            raise ValueError('actions must contain exactly slack binary decisions')
        survival=1.;cost=0.
        for t,u in enumerate(actions):
            cost+=survival*(u*(self.c+charge)-(1-u)*sub)
            survival*=1-self.probability(u,age+t)
        return cost+survival*self.K

    def exhaustive(self,age,slack,*,charge=0.,passive_subsidy=0.):
        integer(age,'age');integer(slack,'slack')
        if slack>18: raise ValueError('exhaustive oracle limited to slack <= 18')
        return min(self.evaluate_sequence(age,slack,actions,charge=charge,passive_subsidy=passive_subsidy)
                   for actions in product((0,1),repeat=slack))

    def critical_cost(self,age,slack,*,tol=1e-9):
        """Root/boundary of strict-active region for k>=0; score is NOT a Whittle index.
        Returns k_crit in [0, delta*K], with passive selected at equality.
        """
        integer(age,'age');integer(slack,'slack')
        if slack==0: return 0.
        p0,p1=self.hazards(age)
        delta=p1-p0
        if delta==0 or self.K==0: return 0.
        hi=delta*self.K
        def active(k):
            q0,q1=self.action_values(age,slack,charge=k-self.c)
            return q1<q0
        if not active(0.): return 0.
        lo=0.
        for _ in range(90):
            mid=(lo+hi)/2
            if active(mid): lo=mid
            else:hi=mid
            if hi-lo<=tol:break
        return (lo+hi)/2

def illustrative_model():
    from math import exp
    p0=lambda a:.32*exp(-.075*a)
    return M0(p0,lambda a:p0(a)+(1-p0(a))*.35,8.,100.)

def counterexample_model():
    return M0(lambda a:0.,lambda a:1. if a==0 else 0.,8.,100.)

def negative_charge_counterexample():
    model=counterexample_model()
    entries=[]
    for k in (-150.,-100.,-50.,0.,99.,100.,150.):
        cont=model.solve(1,2,charge=k-model.c)[0]
        q0,q1=model.action_values(0,3,charge=k-model.c)
        value,action=model.solve(0,3,charge=k-model.c)
        entries.append(dict(k=k,lam=k-model.c,V_1_2=cont,Q_passive=q0,Q_active=q1,V_0_3=value,action=action,
                            analytic_cont=100+2*min(0,k),
                            enumeration=model.exhaustive(0,3,charge=k-model.c)))
    return entries
