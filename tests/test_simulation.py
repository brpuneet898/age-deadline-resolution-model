import unittest,tempfile,sys,csv
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scenario_grid import scenarios
from simulation import run
from analysis import analyze
from policies import POLICY_NAMES
class SimulationTests(unittest.TestCase):
    def test_grid_count(self):self.assertEqual(len(list(scenarios())),432)
    def test_paired_rows_and_reproducibility(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'one.csv';q=Path(d)/'two.csv'
            run(3,2,3,123,str(p));run(3,2,3,123,str(q))
            self.assertEqual(p.read_bytes(),q.read_bytes())
            with p.open(newline="") as f:
                rows=list(csv.DictReader(f))
            self.assertEqual(len(rows),3*2*len(POLICY_NAMES))
            self.assertTrue(all(int(r['capacity_violations'])==0 for r in rows))
            self.assertEqual(len(analyze(p)['paired_comparisons']),8)
if __name__=='__main__':unittest.main()
