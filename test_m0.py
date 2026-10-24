"""Unittest verification suite for the D1 first solver release."""
import unittest
from math import isclose
from m0 import M0, illustrative_model, test_ordering, charge_passive_set_reversals

class M0Tests(unittest.TestCase):
    def test_terminal(self):
        m=illustrative_model()
        self.assertEqual(m.solve(3,0),(100.0,0))
    def test_one_step_exact(self):
        m=M0(lambda a:.2, lambda a:.5, c=6, K=100)
        self.assertEqual(m.solve(0,1),(56.0,1))
        self.assertEqual(m.solve(0,1,charge=30),(80.0,0))
    def test_hazards_validated_on_reachable_path(self):
        m=M0(lambda a:.5,lambda a:1.1)
        with self.assertRaises(ValueError):m.solve(0,2)
    def test_exhaustive_vs_backward(self):
        models=[illustrative_model(),
                M0(lambda a:.25,lambda a:.75,c=12,K=100),
                M0(lambda a:.1+.04*min(7,a),lambda a:.2+.04*min(7,a),c=8,K=100)]
        for m in models:
            for a in (0,2,5):
                for l in range(1,7):
                    self.assertLess(abs(m.solve(a,l)[0]-m.exhaustive(a,l)),1.e-10)
    def test_charge_and_subsidy_separately(self):
        m=illustrative_model()
        for a,l in ((0,3),(3,5),(7,2)):
            for kw in ({'charge':-4.0},{'charge':12.0},{'passive_subsidy':3.0}):
                self.assertLess(abs(m.solve(a,l,**kw)[0]-m.exhaustive(a,l,**kw)),1.e-10)
        with self.assertRaises(ValueError):m.solve(0,3,charge=1,passive_subsidy=1)
    def test_corner_cases(self):
        for p0,p1,c,K in ((0,1,0,100),(1,1,10,100),(0,0,10,100),(.2,.2,0,100)):
            m=M0(lambda a,x=p0:x, lambda a,x=p1:x, c=c,K=K)
            for l in (1,2,4):self.assertLess(abs(m.solve(0,l)[0]-m.exhaustive(0,l)),1.e-10)
    def test_age_slack_and_identity(self):
        d=test_ordering(illustrative_model(),ages=range(0,21),slacks=range(1,11))
        self.assertEqual(d['errors'],[])
    def test_charge_passive_nesting_sample_only(self):
        m=illustrative_model()
        reversals=charge_passive_set_reversals(m,ages=range(0,10),slacks=range(1,8),charges=[-8,-4,0,4,12,24,50,100])
        self.assertEqual(reversals,[])

if __name__=='__main__':unittest.main(verbosity=2)
