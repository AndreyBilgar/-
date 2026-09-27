import json, numpy as np
from scipy.optimize import brentq
from sim import Model
mdl=Model(); PID=json.load(open('ident_phys.json'))['p']
def xmax(fac):
    p=list(PID); p[0]*=fac; rec,_=mdl.run({},T=0.2,p=p); return -rec['X'].min()*1e3
for tgt in (18.0,17.0):
    f=brentq(lambda a: xmax(a)-tgt,0.85,1.0,xtol=1e-4); print('no brakes, X=%.0f mm <=> P0 x %.4f (%.1f%%), I_P change %.0f N s'%(tgt,f,(f-1)*100,(f-1)*PID[0]*1e6*PID[2]*1e-3/2))
