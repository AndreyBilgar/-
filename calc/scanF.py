import json, numpy as np
from sim import Model
mdl=Model(); PID=json.load(open('ident_phys.json'))['p']; opt=json.load(open('optim.json'))
ST=['S1','S2','S3','S4','S5']
LAY={'uniform':[1,1,1,1,1],'ends':[1,0,0,0,1],'node':[0,1,1,1,0],'opt':opt['60']['w']}
Fs=[0,10,20,30,45,60,80,100,150,200]
out={}
for k,w in LAY.items():
    w=np.array(w,float); w/=w.sum(); out[k]=[]
    for F in Fs:
        rec,E=mdl.run({s:F*1e3*x for s,x in zip(ST,w)},T=0.7,p=PID,rec_every=20)
        t=rec['t']; osc=rec['X']-rec['xcm']; sl=(t>=0.17)&(t<0.2)
        out[k].append(dict(F=F,Xmax200=float(-rec['X'][t<=0.2].min()*1e3),Xfin=float(-rec['xcm'][-1]*1e3),A170=float(0.5*(osc[sl].max()-osc[sl].min())*1e3)))
    print(k,[(d['F'],round(d['Xmax200'],1),round(d['Xfin'],1),round(d['A170'],2)) for d in out[k]])
json.dump(out,open('scanF.json','w'))
