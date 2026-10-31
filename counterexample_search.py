"""Exact negative-charge counterexample, numerical structural search and CSV evidence.
Search is a diagnostic; do not mistake finite grids for global theorems.
"""
import argparse,csv,json
from pathlib import Path
from itertools import product
from m0 import M0,negative_charge_counterexample

def search():
    failures=[]
    for p00,p01,p10,p11 in product((0.,.2,.6),repeat=4):
        if not (p00<=p10 and p01<=p11):continue
        model=M0(lambda a,x=p00,y=p01:x if a==0 else y,
                 lambda a,x=p10,y=p11:x if a==0 else y,c=8.,K=100.)
        # detect unsupported age threshold when hazard sufficient conditions fail
        for slack in (1,2,3):
            for age in (0,1):
                active_here=model.solve(age,slack)[1]
                active_next=model.solve(age+1,slack)[1]
                if active_here and not active_next:
                    failures.append({'kind':'age_active_upper_set_violation','age':age,'slack':slack,
                                     'p00':p00,'p01':p01,'p10':p10,'p11':p11,'c':8.,'K':100.})
                    break
            if failures:break
        if len(failures)>=30:break
    return failures

def main():
    dest=Path('results');dest.mkdir(exist_ok=True)
    ce=negative_charge_counterexample()
    (dest/'negative_charge_counterexample.json').write_text(json.dumps(ce,indent=2))
    fails=search()
    (dest/'structural_search.json').write_text(json.dumps({'examples':fails,'note':'finite search; no minimality certificate'},indent=2))
    print('Saved analytical charge values:',len(ce),'structural violations found:',len(fails))
if __name__=='__main__': main()
