"""Independent short-horizon numerical verification, generates auditable JSON evidence."""
import json,platform,subprocess,sys
from itertools import product
from pathlib import Path
from m0 import M0,illustrative_model,counterexample_model

def verify():
    models=[illustrative_model(),counterexample_model(),M0(lambda a:.1,lambda a:.8,5,100),
            M0(lambda a:min(.7,.1+.03*a),lambda a:min(.9,.25+.03*a),12,40)]
    maxerr=0.;count=0;worst=None
    for m_id,m in enumerate(models):
        for a,l,k in product((0,1,3),range(0,8),(-150.,-8.,0.,5.,30.,120.)):
            charge=k-m.c
            dp=m.solve(a,l,charge=charge)[0]
            enum=m.exhaustive(a,l,charge=charge)
            err=abs(dp-enum);count+=1
            if err>maxerr:maxerr=err;worst={'model':m_id,'age':a,'slack':l,'k':k,'dp':dp,'enum':enum}
    out={'cases':count,'max_abs_dp_minus_enumeration':maxerr,'worst_case':worst,
         'tolerance':1e-10,'pass':maxerr<1e-10,'python':sys.version,'platform':platform.platform()}
    Path('evidence').mkdir(exist_ok=True)
    Path('evidence/verification.json').write_text(json.dumps(out,indent=2))
    assert out['pass'],out
    print(json.dumps(out,indent=2))
if __name__=='__main__':verify()
