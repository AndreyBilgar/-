import json, numpy as np
from scipy.linalg import eigh
from scipy.optimize import brentq
d=np.load('fe_data.npz'); zn=d['zn']; zc=d['zc']; me=d['mass_e']; A=d['A_e']
E=2.06e11; dz=zn[1]-zn[0]; ne=len(zc); n=len(zn)
JOINTS={'ЗК–ПС1':3.645,'ПС1–ПС2':8.878,'ПС2–ПС3':14.372,'ПС3–ФК':19.604,'ФК–БТ1':21.906,'БТ1–БТ2':27.131}
zA,zB=19.532,19.532+0.10944
def assemble(kj):  # kj: dict joint->stiffness (N/m) or None
    K=np.zeros((n,n)); Mm=np.zeros((n,n))
    for e in range(ne):
        k=E*A[e]/dz
        for name,zj in JOINTS.items():
            if kj.get(name) and zn[e]<=zj<zn[e+1]: k=1/(1/k+1/kj[name])
        K[e:e+2,e:e+2]+=k*np.array([[1,-1],[-1,1]])
        Mm[e:e+2,e:e+2]+=me[e]/6*np.array([[2,1],[1,2]])
    return K,Mm
def modal(kj,nm=5):
    K,Mm=assemble(kj); w2,V=eigh(K,Mm,subset_by_index=[0,nm-1])
    return np.sqrt(np.clip(w2,0,None)), V, K, Mm
def gain(V):
    phi=V[:,1]; uA=np.interp(zA,zn,phi); uB=np.interp(zB,zn,phi); return (uB-uA)/uB
w,V,K,Mm=modal({})
phi=V[:,1]; phi=phi/np.interp(zB,zn,phi)
node=zn[np.nonzero(np.diff(np.sign(phi)))[0][0]]
print('RIGID: f1=%.2f f2=%.2f f3=%.2f Hz; node at z=%.2f m; gain dL/X_FK=%.4f'%(w[1]/2/np.pi,w[2]/2/np.pi,w[3]/2/np.pi,node,gain(V)))
# 1) calibrate uniform joint stiffness for all 6 joints to f1 target
for ft in (64.18,64.6):
    g=lambda lk: modal({k:10**lk for k in JOINTS})[0][1]/2/np.pi-ft
    lk=brentq(g,8,12); w,V,_,_=modal({k:10**lk for k in JOINTS})
    print('uniform joints -> f1=%.2f: k_j=%.3g N/m (%.0f MN/m); f2=%.2f; gain=%.4f'%(ft,10**lk,10**lk/1e6,w[2]/2/np.pi,gain(V)))
# 2) two-parameter calibration: k_J4 from gain, k_other from f1
target_gain=0.056; target_f=64.18
def solve(tg,tf):
    kJ4=1e10; ko=1e10
    for it in range(30):
        g2=lambda lk: gain(modal({**{k:ko for k in JOINTS if k!='ПС3–ФК'},'ПС3–ФК':10**lk})[1])-tg
        try: kJ4=10**brentq(g2,7,12)
        except ValueError: kJ4=None; break
        g1=lambda lk: modal({**{k:10**lk for k in JOINTS if k!='ПС3–ФК'},'ПС3–ФК':kJ4})[0][1]/2/np.pi-tf
        try: ko=10**brentq(g1,7.5,13)
        except ValueError: ko=np.inf; break
    return kJ4,ko
for tg in (0.056,0.070):
    kJ4,ko=solve(tg,target_f)
    print('gain %.3f & f1 %.2f -> k(PS3-FK)=%s MN/m, k(other joints)=%s MN/m'%(tg,target_f, None if kJ4 is None else round(kJ4/1e6), None if ko is None else (round(ko/1e6) if np.isfinite(ko) else 'inf')))
# save rigid mode shapes
w,V,K,Mm=modal({},nm=5)
modes=[]
for i in range(1,5):
    ph=V[:,i]/np.max(np.abs(V[:,i])); modes.append(ph.tolist())
json.dump(dict(zn=zn.tolist(), f=(w/2/np.pi).tolist(), modes=modes), open('fe_modes_rigid.json','w'))
