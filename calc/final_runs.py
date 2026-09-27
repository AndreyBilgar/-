import json, numpy as np
from sim import Model
mdl=Model(); PID=json.load(open('ident_phys.json'))['p']; se=json.load(open('ident_phys.json'))['se']
ST=['S1','S2','S3','S4','S5']
out={}
for lab,Fr in [('Fr-1s',(PID[8]-se[6])*1e3),('Fr',PID[8]*1e3),('Fr+1s',(PID[8]+se[6])*1e3)]:
    rec,E=mdl.run({},T=1.2,Fr=Fr,p=PID)
    v=rec['vcm']; idx=np.nonzero(np.abs(v)>1e-3)[0]; ta=rec['t'][idx[-1]]
    print('%s=%.1f kN: final recoil %.1f mm, arrest t=%.0f ms, X(200)=%.2f'%(lab,Fr/1e3,-rec['xcm'][-1]*1e3,ta*1e3,-np.interp(0.2,rec['t'],rec['X'])*1e3))
    out[lab]=[Fr,-rec['xcm'][-1]*1e3,ta*1e3]
json.dump(out,open('recoil_unc.json','w'))
# time histories for figures
opt=json.load(open('optim.json'))
cases={'base':{},'test30':{s:6e3 for s in ST},'opt60':{s:60e3*w for s,w in zip(ST,opt['60']['w'])},'uni100':{s:20e3 for s in ST}}
TH={}
for k,Fb in cases.items():
    rec,E=mdl.run(Fb,T=0.6,p=PID,rec_every=25)
    TH[k]={kk:rec[kk].tolist() for kk in ('t','X','xcm','vcm','NJ','dL','Fbr','Ek','Es')}; TH[k]['E']={a:float(b) for a,b in E.items()}
    print(k, 'Wext=%.0f Dfr=%.0f Ddamp=%.0f Drol=%.0f Ek=%.0f Es=%.0f err=%.2e'%(E['Wext'],E['Dfr'],E['Ddamp'],E['Drol'],E['Ek'],E['Es'],E['balance_err']/E['Wext']))
json.dump(TH,open('timehist.json','w'))
# mode shapes & distributions for figures
json.dump(dict(zn=mdl.zn.tolist(),m=mdl.m.tolist(),ke=mdl.ke.tolist(),w=mdl.w[:6].tolist(),V=[mdl.V[:,k].tolist() for k in range(4)],st={k:float(mdl.zn[i]) for k,i in mdl.st.items()}),open('modes_phys.json','w'))
# quasi-static joint force from braking: N_J = F_front - m_front/M * F_sum
zJ=19.604; mf=mdl.m[mdl.zn>zJ].sum(); M=mdl.M
print('m_front=%.1f kg, share=%.4f'%(mf,mf/M))
