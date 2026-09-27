import json, numpy as np
from sim import Model
mdl=Model(); PID=json.load(open('ident_phys.json'))['p']
base,_=mdl.run({},T=0.2,p=PID)
dL0=base['dL'].max()-base['dL'].min(); N0=np.abs(base['NJ']).max(); X0=-base['X'].min()
out=[]
for lab,i,fac,add in [('Q0 +20%',3,1.2,0),('Q0 -20%',3,0.8,0),('P0 +10%',0,1.1,0),('P0 -10%',0,0.9,0),
                      ('tQ +1.5 ms',4,1,1.5),('tQ -1.5 ms',4,1,-1.5),('tauQ -30%',5,0.7,0),('tauQ +30%',5,1.3,0),('tauP -30%',2,0.7,0)]:
    p=list(PID); p[i]=p[i]*fac+add
    rec,_=mdl.run({},T=0.2,p=p)
    dL=rec['dL'].max()-rec['dL'].min(); N=np.abs(rec['NJ']).max(); X=-rec['X'].min()
    out.append((lab,dL/dL0-1,N/N0-1,X/X0-1)); print('%-12s dL %+6.1f%%  NJmax %+6.1f%%  Xmax200 %+6.1f%%'%(lab,100*(dL/dL0-1),100*(N/N0-1),100*(X/X0-1)))
json.dump(out,open('sens.json','w'),ensure_ascii=False)
