import numpy as np
from scipy.linalg import eigh
E=2.06e11
JOINTS={'ЗК–ПС1':3.645,'ПС1–ПС2':8.878,'ПС2–ПС3':14.372,'ПС3–ФК':19.604,'ФК–БТ1':21.906,'БТ1–БТ2':27.131}
Z_A,Z_B=19.532,19.532+0.10944   # gauge marks (PS3 flange, FK)
Z_FK=Z_B
STATIONS={'S1':2.955,'S2':9.02,'S3':14.52,'S4':21.36,'S5':27.23}  # clamp positions carrying brake links
def build(dz=0.05, kJ4=27.7e9, kjo=11.7e9, rigid=False):
    d=np.load('fe_data.npz'); zn0=d['zn']; zc0=d['zc']; me0=d['mass_e']; A0=d['A_e']
    zn=np.arange(zn0[0], zn0[-1]+1e-9, dz); ne=len(zn)-1; zc=0.5*(zn[:-1]+zn[1:])
    # re-bin mass and stiffness (series springs) from fine mesh
    me=np.zeros(ne); kin=np.zeros(ne)
    idx=np.minimum((zc0-zn[0])//dz,ne-1).astype(int)
    np.add.at(me,idx,me0)
    dz0=zn0[1]-zn0[0]
    np.add.at(kin,idx,dz0/(E*A0))  # compliance
    for name,zj in JOINTS.items():
        if rigid: break
        k=kJ4 if name=='ПС3–ФК' else kjo
        e=int((zj-zn[0])//dz); kin[e]+=1.0/k
    ke=1.0/kin
    n=ne+1
    K=np.zeros((n,n)); Mm=np.zeros(n)
    for e in range(ne):
        K[e:e+2,e:e+2]+=ke[e]*np.array([[1,-1],[-1,1]])
        Mm[e]+=me[e]/2; Mm[e+1]+=me[e]/2
    return zn, K, Mm, ke
def modes(zn,K,Mm,nm=12):
    w2,V=eigh(K,np.diag(Mm),subset_by_index=[0,nm-1])
    w=np.sqrt(np.clip(w2,0,None)); w[0]=0.0
    # mass-normalised already (eigh with B): V.T M V = I
    return w,V
def interp_mode(zn,V,z):
    return np.array([np.interp(z,zn,V[:,k]) for k in range(V.shape[1])])
