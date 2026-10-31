"""Paired differences and normal-approximation 95% CIs (labelled, not bootstrap)."""
import argparse,csv,json,math,statistics
from collections import defaultdict
from pathlib import Path

def analyze(path):
    grouped=defaultdict(dict)
    with open(path,newline='',encoding='utf8') as f:
        for row in csv.DictReader(f):
            key=(int(row['scenario_id']),int(row['replication']))
            grouped[key][row['policy']]=float(row['cost'])
    baselines=['failure_risk','earliest_deadline','myopic_benefit','never_active']
    reports=[]
    scenario_ids=sorted(set(s for s,r in grouped))
    for sid in scenario_ids:
        for baseline in baselines:
            diffs=[grouped[k]['critical_cost']-grouped[k][baseline]
                   for k in sorted(grouped) if k[0]==sid and 'critical_cost' in grouped[k] and baseline in grouped[k]]
            if len(diffs)<2:continue
            mean=statistics.mean(diffs);se=statistics.stdev(diffs)/math.sqrt(len(diffs))
            reports.append({'scenario_id':sid,'reference':'critical_cost','comparator':baseline,
                            'n':len(diffs),'paired_mean_cost_difference':mean,
                            'ci95_normal_approx':[mean-1.96*se,mean+1.96*se],
                            'se':se})
    return {'paired_comparisons':reports,'interpretation':'Negative difference favors critical_cost; normal approximation CI (not exact small-sample coverage).'}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('csv',nargs='?',default='results/pilot.csv')
    p.add_argument('--output',default='results/pilot_analysis.json');a=p.parse_args()
    report=analyze(a.csv);path=Path(a.output);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(report,indent=2));print(f'Wrote {path}, comparisons={len(report["paired_comparisons"])}')
