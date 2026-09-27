import json, numpy as np
from scipy.linalg import eigh
RHO=7850.0; E=2.06e11
S=json.load(open('../cad/slices.json'))
P=json.load(open('../cad/parts.json'))
z0,z1=0.725,32.725; dz=0.025
zn=np.arange(z0,z1+1e-9,dz); ne=len(zn)-1; zc=0.5*(zn[:-1]+zn[1:])
mass_e=np.zeros(ne); A_e=np.zeros(ne)
excl_rail=lambda nm: 'рельс' in nm
tot=0; parts_mass=[]
for s in S:
    if excl_rail(s['part']): continue
    m=s['V']*1e-9*RHO; tot+=m
    za,zb=s['z0']/1000,s['z1']/1000
    if s['coax'] and len(s['zs'])>1:
        zs=np.array(s['zs'])/1000; A=np.array(s['A'])*1e-6
        Ai=np.interp(zc,zs,A,left=0,right=0); Ai[(zc<za)|(zc>zb)]=0
        A_e+=Ai
        w=Ai*dz
        if w.sum()>0: mass_e+=m*w/w.sum()
        else: mass_e[np.argmin(abs(zc-(za+zb)/2))]+=m
    else:
        w=np.clip(np.minimum(zn[1:],zb)-np.maximum(zn[:-1],za),0,None)
        if w.sum()>0: mass_e+=m*w/w.sum()
        else: mass_e[np.argmin(abs(zc-(za+zb)/2))]+=m
print('moving mass total %.1f kg (sum elems %.1f)'%(tot,mass_e.sum()))
M=mass_e.sum(); zcg=(mass_e*zc).sum()/M; print('CoG z = %.3f m'%zcg)
# Masses of named groups
def grp(zl,zr): return mass_e[(zc>=zl)&(zc<zr)].sum()
zJ=19.604  # PS3 flange / FK interface
m1=grp(0,zJ); m2=grp(zJ,40); print('rear m1=%.1f front m2=%.1f  mu=%.1f'%(m1,m2,m1*m2/(m1+m2)))
# article values
print('article m1=9697.2 m2=6598.3 sum=%.1f; ratio CAD/article = %.3f'%(9697.2+6598.3,(m1+m2)/(9697.2+6598.3)))
# bar stiffness: fill tiny gaps where A=0 (overlaps/fit gaps) with neighbour min
A_s=A_e.copy()
for i in range(ne):
    if A_s[i]<1e-4:
        j=np.nonzero(A_s>1e-4)[0]; A_s[i]=A_s[j[np.argmin(abs(j-i))]]
np.savez('fe_data.npz', zn=zn, zc=zc, mass_e=mass_e, A_e=A_s, A_raw=A_e)
def modes(kjoint=None, joints=(), nm=6):
    n=len(zn); K=np.zeros((n,n)); Mm=np.zeros((n,n))
    for e in range(ne):
        k=E*A_s[e]/dz
        if kjoint is not None:
            for zjt in joints:
                if zn[e]<=zjt<zn[e+1]:
                    k=1.0/(1.0/k+1.0/kjoint)
        K[e:e+2,e:e+2]+=k*np.array([[1,-1],[-1,1]])
        me=mass_e[e]; Mm[e:e+2,e:e+2]+=me/6*np.array([[2,1],[1,2]])
    w2,V=eigh(K,Mm,subset_by_index=[0,nm-1])
    return np.sqrt(np.clip(w2,0,None))/2/np.pi, V, K, Mm
f,V,K,Mm=modes()
print('rigid joints: f =', np.round(f,2))
json.dump(dict(f=f.tolist()), open('fe_rigid.json','w'))
