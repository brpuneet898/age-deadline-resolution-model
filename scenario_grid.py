"""Illustrative 432-cell synthetic grid. REPLACE/approve factors against frozen D0 charter.
The 432 count is specified by the email; factor levels below are illustrative, NOT charter-verified.
"""
from itertools import product
from m0 import M0
from capacity_dp import Shipment,CapacityProblem

FACTORS={
 'response_strength':[.15,.30,.45],
 'base_hazard':[.10,.25,.40],
 'deadline_type':['homogeneous','heterogeneous'],
 'misspecification':[0.,.15],
 'capacity_ratio':[.25,.50],
 'terminal_penalty':[50.,100.],
 'cost_level':[4.,8.,12.],
}
# 3*3*2*2*2*2*3 = 432

def scenarios():
    for idx,levels in enumerate(product(*FACTORS.values())):
        yield {'scenario_id':idx+1,**dict(zip(FACTORS,levels))}

def make_problem(s,n=3):
    jobs=[]
    for i in range(n):
        base=s['base_hazard']*(1+.10*(i%3-1))
        strength=s['response_strength']
        h=lambda a,base=base:max(.001,min(.95,base*(.97**a)))
        p1=lambda a,h=h,strength=strength:min(1.,h(a)+(1-h(a))*strength)
        slack=3 if s['deadline_type']=='homogeneous' else 2+(i%3)
        jobs.append(Shipment(M0(h,p1,s['cost_level'],s['terminal_penalty']),i%2,slack))
    cap=max(1,min(n,round(n*s['capacity_ratio'])))
    return CapacityProblem(jobs,cap)

def assumed_problem(problem,misspecification):
    """Decision-policy model only; true simulation outcomes retain actual problem hazards."""
    if not misspecification:return problem
    jobs=[]
    for j in problem.jobs:
        m=j.model;factor=1-misspecification
        p0=lambda a,m=m,factor=factor:max(0.,min(1.,m.p0(a)*factor))
        p1=lambda a,m=m,factor=factor:max(0.,min(1.,m.p1(a)*factor))
        jobs.append(Shipment(M0(p0,p1,m.c,m.K),j.age,j.slack))
    return CapacityProblem(jobs,problem.capacity)
