import json, numpy as np
from scipy.signal import savgol_filter
P=json.load(open('exp1_proc.json')); tu=np.array(P['tu'])*1e-3; xu=np.array(P['xu'])*1e-3
M=17911.5; T1=1/64.18
dt=tu[1]-tu[0]; nw=int(round(T1/dt))
# moving average over one period (boxcar) -> suppresses mode 1
k=np.ones(nw)/nw; xm=np.convolve(xu,k,mode='same')
# mark valid region
valid=(tu>tu[0]+T1/2)&(tu<tu[-1]-T1/2)
xs=savgol_filter(xm,101,3); v=np.gradient(xs,dt); a=np.gradient(v,dt)
for tt in [0.050,0.055,0.058,0.060,0.062,0.064,0.066,0.068,0.070,0.075,0.080,0.100,0.150,0.190]:
    i=np.argmin(abs(tu-tt)); print('t=%.0f ms xcm=%.2f mm v=%.3f m/s a=%.1f m/s2 F=%.2f MN'%(tt*1e3,xs[i]*1e3,v[i],a[i],M*a[i]/1e6))
iv=np.argmin(v*valid); print('peak recoil velocity %.3f m/s at %.1f ms -> momentum %.0f N*s'%(v[iv],tu[iv]*1e3,M*v[iv]))
json.dump(dict(t=tu.tolist(),xcm=xs.tolist(),v=v.tolist(),a=a.tolist()), open('rigid.json','w'))
