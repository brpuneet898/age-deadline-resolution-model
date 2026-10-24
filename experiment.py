"""Fixed-seed synthetic smoke test and elementary model diagnostics."""
from math import sqrt
import json
from m0 import illustrative_model, test_ordering, charge_passive_set_reversals
m=illustrative_model()
val, act=m.solve(3,5)
mu,se,fr=m.simulate(3,5,n=25000,seed=20261018)
res={
 'label':'SYNTHETIC M0 PROTOTYPE; not transportation/FedEx findings',
 'model':{'K':m.K,'c':m.c,'p0':'0.32 exp(-0.075 a)','p1':'p0+(1-p0)*0.35'},
 'example':{'age':3,'slack':5,'value_dp':val,'first_action':act,
            'mc_mean_cost':mu,'mc_se':se,'mc_failure_fraction':fr,
            'absolute_mc_gap':abs(mu-val),'mc_tolerance_5se':5*se},
 'exhaustive_agreement_max':max(abs(m.solve(a,l)[0]-m.exhaustive(a,l))
                                  for a in (0,2,5) for l in range(1,7)),
 'ordering_diagnostic':test_ordering(m,ages=range(0,21),slacks=range(1,11)),
 'charge_reversals_on_test_grid':charge_passive_set_reversals(m, ages=range(0,10),
       slacks=range(1,8),charges=[-8,-4,0,4,12,24,50,100]),
 'limitation':'Charge-index monotonicity not established by a finite-grid check; M1 and observational causal effects not implemented.'
}
assert res['example']['absolute_mc_gap'] < 5*se
assert res['exhaustive_agreement_max'] < 1.e-10
assert not res['ordering_diagnostic']['errors']
with open('smoke_results.json','w') as f:json.dump(res,f,indent=2)
print(json.dumps(res,indent=2))
