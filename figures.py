"""Dependency-free SVG evidence plots from counterexample and capacity benchmark JSON."""
import json,html
from pathlib import Path

def svg_line(points,title,xlab,ylab,path):
    W,H=760,420;L,R,T,B=70,35,45,65
    xx=[a for a,b in points]; yy=[b for a,b in points]
    xmin,xmax=min(xx),max(xx);ymin,ymax=min(yy),max(yy)
    if xmax==xmin:xmax+=1
    if ymax==ymin:ymax+=1
    X=lambda x:L+(x-xmin)/(xmax-xmin)*(W-L-R)
    Y=lambda y:H-B-(y-ymin)/(ymax-ymin)*(H-T-B)
    poly=' '.join(f'{X(x):.1f},{Y(y):.1f}' for x,y in points)
    labels=''.join(f'<text x="{X(x):.0f}" y="{H-B+21}" text-anchor="middle" font-size="12">{x:g}</text>' for x,y in points)
    txt=f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<rect width="100%" height="100%" fill="white"/><text x="{W/2}" y="26" text-anchor="middle" font-family="Arial" font-size="17">{html.escape(title)}</text>
<path d="M {L} {T} V {H-B} H {W-R}" fill="none" stroke="#333" stroke-width="2"/>
<polyline points="{poly}" fill="none" stroke="#2463ac" stroke-width="2.5"/>
{''.join(f'<circle cx="{X(x)}" cy="{Y(y)}" r="4" fill="#2463ac"/>' for x,y in points)}
{labels}<text x="{W/2}" y="{H-13}" font-family="Arial" text-anchor="middle">{html.escape(xlab)}</text>
<text x="18" y="{H/2}" font-family="Arial" transform="rotate(-90 18 {H/2})" text-anchor="middle">{html.escape(ylab)}</text>
</svg>'''
    Path(path).parent.mkdir(parents=True,exist_ok=True);Path(path).write_text(txt)

def make_figures():
    ce=json.loads(Path('results/negative_charge_counterexample.json').read_text())
    svg_line([(row['k'],row['V_0_3']) for row in ce],
            'Three-interval counterexample: exact optimal value','Effective activation cost k','Optimal value',
            'figures/counterexample_value.svg')
    bench=json.loads(Path('results/capacity_benchmark.json').read_text())
    svg_line([(i,row['absolute_gap']) for i,row in enumerate(bench['policies'],1)],
            'Small-N: expected-cost gap to exact capacity DP','Policy ordinal (see JSON)','Absolute optimality gap',
            'figures/capacity_policy_gaps.svg')
    print('Created figures/counterexample_value.svg and figures/capacity_policy_gaps.svg')
if __name__=='__main__':make_figures()
