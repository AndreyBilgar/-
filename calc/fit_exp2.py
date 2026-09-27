import json, numpy as np
from scipy.optimize import least_squares
D=json.load(open('fig3_digitized.json')); P=json.load(open('exp1_proc.json')); p=np.array(json.load(open('fit1.json'))['p'])
tu=np.array(P['tu']); xu=np.array(P['xu'])
def model(p,tt):
    a0,a1,a2,A,al,w,ph=p; tau=(tt-72.0)*1e-3
    return a0+a1*tau+a2*tau**2+A*np.exp(-al*tau)*np.cos(w*tau+ph)
sel=(tu>=72)&(tu<=198)
res=xu[sel]-model(p,tu[sel])
# spectrum of residual
n=len(res); dt=1e-4
F=np.fft.rfftfreq(8192,dt); S=np.abs(np.fft.rfft(res*np.hanning(n),8192))
pk=np.argsort(S)[::-1][:8]; print('residual peaks Hz', sorted(set(np.round(F[pk],0))))
# two-mode fit
def model2(q,tt):
    tau=(tt-72.0)*1e-3
    a0,a1,a2,A1,al1,w1,ph1,A2,al2,w2,ph2=q
    return a0+a1*tau+a2*tau**2+A1*np.exp(-al1*tau)*np.cos(w1*tau+ph1)+A2*np.exp(-al2*tau)*np.cos(w2*tau+ph2)
best=None
for f2 in [30,45,55,75,90,110,130,160,200]:
  for ph in np.linspace(-3,3,6):
    q0=list(p)+[0.5,5.0,2*np.pi*f2,ph]
    r=least_squares(lambda q:model2(q,tu[sel])-xu[sel], q0, bounds=([-50,-500,-1e4,0,-50,300,-10,0,-50,50,-10],[50,500,1e4,10,100,500,10,10,200,2000,10]))
    if best is None or r.cost<best.cost: best=r
q=best.x; r2=model2(q,tu[sel])-xu[sel]
print('two-mode fit: f1=%.2f Hz alpha1=%.2f A1=%.2f | f2=%.2f Hz alpha2=%.2f A2=%.2f | v=%.4f m/s a=%.3f m/s2 | rms=%.3f'%(q[5]/2/np.pi,q[4],q[3],q[9]/2/np.pi,q[8],q[7],q[1]*1e-3,2*q[2]*1e-3,np.sqrt(np.mean(r2**2))))
json.dump(dict(q=q.tolist()), open('fit2.json','w'))
# dL analysis
td=np.array(D['td']); dl=np.array(D['dl']); m=td<=199; td=td[m]; dl=dl[m]
tdu=np.arange(1,199,0.1); dlu=np.interp(tdu,td,dl)
print('dL digitized: max %.3f mm at %.1f ms, min %.3f mm at %.1f ms, range %.3f mm; baseline (0-50ms) mean %.3f std %.3f'%(dlu.max(),tdu[dlu.argmax()],dlu.min(),tdu[dlu.argmin()],dlu.max()-dlu.min(), dlu[tdu<50].mean(), dlu[tdu<50].std()))
# correlation of dL oscillation with X oscillation (after 72 ms): regress dL on osc component of X
osc=(xu-(p[0]+p[1]*(tu-72)*1e-3+p[2]*((tu-72)*1e-3)**2))
s2=(tdu>=72)&(tdu<=198)
oscX=np.interp(tdu[s2],tu,osc)
Acoef=np.polyfit(oscX, dlu[s2],1); cc=np.corrcoef(oscX,dlu[s2])[0,1]
print('dL = %.4f * Xosc + %.4f, corr=%.3f'%(Acoef[0],Acoef[1],cc))
json.dump(dict(tdu=tdu.tolist(),dlu=dlu.tolist()), open('dl_proc.json','w'))
