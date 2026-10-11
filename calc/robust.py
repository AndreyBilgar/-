import json, numpy as np
from sim import Model
mdl=Model(); PID=json.load(open('ident_phys.json'))['p']; opt=json.load(open('optim.json'))
ST=['S1','S2','S3','S4','S5']; wr=np.array(opt['60']['w']); wr/=wr.sum()
def run(w,F,p):
    rec,E=mdl.run({s:F*x for s,x in zip(ST,w)},T=0.6,p=p)
    t=rec['t']; osc=rec['X']-rec['xcm']; s=(t>=0.17)&(t<0.2)
    return -rec['xcm'][-1]*1e3, 0.5*(osc[s].max()-osc[s].min())*1e3
out={}
for lab,i,fac in [('P0 -6%',0,0.94),('base',0,1.0),('P0 +6%',0,1.06),('Q0 -10%',3,0.9),('Q0 +10%',3,1.1)]:
    p=list(PID); p[i]*=fac
    u=run(np.ones(5)/5,60e3,p); r=run(wr,60e3,p)
    out[lab]=dict(uni=u,rec=r)
    print('%-8s uniform Xfin=%.2f A=%.3f | rec Xfin=%.2f A=%.3f | dX=%.1f%% dA=%.1f%%'%(lab,u[0],u[1],r[0],r[1],100*(r[0]/u[0]-1),100*(r[1]/u[1]-1)))
json.dump(out,open('robust.json','w'))
