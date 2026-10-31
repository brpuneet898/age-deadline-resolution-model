import unittest,math,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from m0 import M0,illustrative_model,counterexample_model,negative_charge_counterexample

class M0Tests(unittest.TestCase):
    def test_terminal_and_last_interval(self):
        m=M0(lambda a:0.,lambda a:1.,8,100)
        self.assertEqual(m.solve(0,0),(100.,0))
        self.assertEqual(m.solve(0,1),(8.,1))
        self.assertEqual(m.exhaustive(0,0),100.)
    def test_ties_passive(self):
        m=M0(lambda a:0.,lambda a:1.,8,100)
        self.assertEqual(m.solve(0,1,charge=92.),(100.,0))
        m2=M0(lambda a:.2,lambda a:.2,0.,100.)
        self.assertEqual(m2.solve(0,2)[1],0)
    def test_invalid_age_slack_types(self):
        m=illustrative_model()
        for a in (True,-1,1.5,'1',None):
            with self.assertRaises(ValueError):m.solve(a,2)
            with self.assertRaises(ValueError):m.probability(0,a)
        for l in (False,-1,2.0,'2'):
            with self.assertRaises(ValueError):m.solve(0,l)
    def test_invalid_probabilities(self):
        for p0,p1 in ((.8,.3),(-.1,.3),(.2,1.2),(float('nan'),.9),(.2,float('inf')),('bad',.9)):
            with self.assertRaises(ValueError):M0(lambda a,v=p0:v,lambda a,v=p1:v).solve(0,1)
    def test_invalid_costs_and_actions(self):
        for c,K in ((-1,2),(1,-2),(float('nan'),2),(3,float('inf'))):
            with self.assertRaises(ValueError):M0(lambda a:.1,lambda a:.2,c,K)
        with self.assertRaises(ValueError):illustrative_model().probability(True,0)
    def test_incompatible_params(self):
        m=illustrative_model()
        for fn in (m.solve,m.evaluate_sequence):
            args=(0,2) if fn==m.solve else (0,2,(0,1))
            with self.assertRaises(ValueError):fn(*args,charge=1,passive_subsidy=1)
        with self.assertRaises(ValueError):m.solve(0,1,charge=float('nan'))
    def test_dp_enumeration(self):
        m=illustrative_model()
        for a in (0,2,5):
            for l in range(7):
                for k in (-10,0,8,40):
                    kw={'charge':k-m.c}
                    self.assertLess(abs(m.solve(a,l,**kw)[0]-m.exhaustive(a,l,**kw)),1e-10)
    def test_global_counterexample(self):
        rows=negative_charge_counterexample();m=counterexample_model()
        expected={-150:0,-100:0,-50:1,0:1,99:1,100:0,150:0}
        for row in rows:
            self.assertAlmostEqual(row['V_1_2'],row['analytic_cont'])
            self.assertAlmostEqual(row['V_0_3'],row['enumeration'])
            self.assertEqual(row['action'],expected[row['k']])
        for k in (-100,100):
            q0,q1=m.action_values(0,3,charge=k-8)
            self.assertAlmostEqual(q0,q1)
    def test_positive_charge_nesting(self):
        models=[illustrative_model(),counterexample_model(),M0(lambda a:.1,lambda a:.7,3,50)]
        for m in models:
            for age in range(4):
                for slack in range(1,6):
                    acts=[m.solve(age,slack,charge=k-m.c)[1] for k in (0,1,2,4,8,20,50,100,200)]
                    self.assertEqual(acts,sorted(acts,reverse=True))
                    critical=m.critical_cost(age,slack)
                    self.assertGreaterEqual(critical,0)
                    self.assertLessEqual(critical,m.K+1e-8)
    def test_finite_hazards_at_reachable_age(self):
        m=M0(lambda a:.1 if a<3 else 2.,lambda a:.5 if a<3 else 2.)
        with self.assertRaises(ValueError):m.solve(0,5)
if __name__=='__main__':unittest.main()
