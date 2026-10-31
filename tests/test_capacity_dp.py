import unittest,random,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from m0 import M0
from capacity_dp import Shipment,CapacityProblem
from benchmark_capacity import example_problem,run
from policies import build_policy,POLICY_NAMES
class CapacityTests(unittest.TestCase):
    def test_one_job_matches_m0(self):
        for c in (0,5,40):
            m=M0(lambda a:.2,lambda a:.8,c,100)
            p=CapacityProblem([Shipment(m,0,3)],1)
            self.assertAlmostEqual(p.exact()['value'],m.solve(0,3)[0],places=11)
    def test_zero_capacity(self):
        m=M0(lambda a:0.,lambda a:1.,4,100)
        p=CapacityProblem([Shipment(m,0,2),Shipment(m,1,1)],0)
        self.assertEqual(p.exact()['value'],200)
    def test_resolved_and_terminal_handling(self):
        m=M0(lambda a:1.,lambda a:1.,7,100)
        p=CapacityProblem([Shipment(m,0,1),Shipment(m,0,0)],1)
        self.assertEqual(p.exact()['value'],100)
        self.assertEqual(p.sample(build_policy('never_active'),lambda i,t:.5)['cost'],100)
    def test_policy_optimality_gaps(self):
        for n in (2,3):
            output=run(n,1);opt=output['optimal']['value']
            self.assertTrue(all(r['expected_cost']>=opt-1e-9 for r in output['policies']))
            self.assertTrue(all(r['capacity_violations']==0 for r in output['policies']))
    def test_reject_infeasible_policy(self):
        p=example_problem(3,1)
        with self.assertRaises(ValueError):p.evaluate_policy(lambda prob,state,t:(0,1))
    def test_sample_seed_repeatability(self):
        p=example_problem(3,1);policy=build_policy('critical_cost')
        def run_once():
            rng=random.Random(44);draws=[[rng.random() for t in range(4)] for i in range(3)]
            return p.sample(policy,lambda i,t:draws[i][t])
        self.assertEqual(run_once(),run_once())
if __name__=='__main__':unittest.main()
