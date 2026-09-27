import json, numpy as np
from scipy.linalg import eigh
from femodel_lib import *
ID=json.load(open('ident2.json')); PID=ID['p']
def pulse(t,t0,tau):
    s=(t-t0)/tau; return np.sin(np.pi*s)**2 if 0<s<1 else 0.0
class Model:
    def __init__(self, dz=0.1, kJ4=27.7e9, kjo=11.7e9, zeta=0.0148, nmodes_damp=30):
        self.zn,K,Mm,ke=build(dz,kJ4,kjo); self.K=K; self.m=Mm; self.ke=ke
        self.n=len(self.zn); self.M=Mm.sum()
        w2,V=eigh(K,np.diag(Mm)); w=np.sqrt(np.clip(w2,0,None)); w[0]=0
        self.w=w; self.V=V
        nd=nmodes_damp; self.Vd=V[:,1:nd+1]; self.cd=2*zeta*w[1:nd+1]**2/w[1]
        self.dtcrit=2/w.max()
        node=lambda z:int(np.argmin(abs(self.zn-z)))
        self.iP=node(1.28); self.iQ=node(21.3); self.iA=node(Z_A); self.iB=node(Z_B)
        self.iFK=node(Z_FK); self.st={k:node(z) for k,z in STATIONS.items()}
        # joint PS3-FK element
        self.eJ=int((JOINTS['ПС3–ФК']-self.zn[0])//dz)
    def internal(self,u):
        du=np.diff(u); N=self.ke*du  # element axial force (tension +)
        f=np.zeros(self.n); f[:-1]+=N; f[1:]-=N
        return f,N
    def run(self, Fb, T=0.2, dt=None, kb=5.6e8, Fr=None, p=PID, rec_every=10, v_eps=1e-3, stop_check=False):
        """Fb: dict station->slip force [N] for the PAIR at that station."""
        p=list(p); Fr=p[8]*1e3 if Fr is None else Fr
        dt=dt or 0.4*self.dtcrit
        nst=int(T/dt)+1
        u=np.zeros(self.n); v=np.zeros(self.n)
        st=[(self.st[k],Fb[k]) for k in Fb if Fb[k]>0]
        slip=np.array([0.0 for _ in st]); Fl=np.zeros(len(st))
        E=dict(Wext=0.0,Dfr=0.0,Drol=0.0,Ddamp=0.0)
        rec=dict(t=[],X=[],dL=[],NJ=[],vcm=[],xcm=[],Fbr=[],Ek=[],Es=[],Eb=[])
        def forces(t,u,v):
            fint,N=self.internal(u)
            f=fint
            Pf=p[0]*1e6*pulse(t,p[1]*1e-3,p[2]*1e-3); Qf=p[3]*1e6*pulse(t,p[4]*1e-3,p[5]*1e-3)
            fe=np.zeros(self.n); fe[self.iP]-=Pf; fe[self.iQ]+=Qf
            # damping (modal projection)
            qd=self.Vd.T@(self.m*v); fd=-(self.m*(self.Vd@(self.cd*qd)))
            # rolling resistance distributed by mass
            fr=-Fr*(self.m/self.M)*np.tanh(v/v_eps)
            return f+fe+fd+fr, fe, fd, fr, N
        a=np.zeros(self.n)
        f,fe,fd,fr,N=forces(0.0,u,v); a=f/self.m
        t=0.0
        for it in range(nst):
            vh=v+0.5*dt*a
            u_new=u+dt*vh
            # brakes: Jenkins elements (link spring kb + Coulomb slider)
            fb=np.zeros(self.n)
            for j,(i,Fs) in enumerate(st):
                Ftr=-kb*(u_new[i]-slip[j])
                if abs(Ftr)>Fs:
                    Ftr=np.sign(Ftr)*Fs; slip_new=u_new[i]+Ftr/kb
                    E['Dfr']+=Fs*abs(slip_new-slip[j]); slip[j]=slip_new
                Fl[j]=Ftr; fb[i]+=Ftr
            u=u_new; t+=dt
            f,fe,fd,fr,N=forces(t,u,vh)
            f=f+fb
            a_new=f/self.m
            v=vh+0.5*dt*a_new
            E['Wext']+=np.dot(fe,vh)*dt; E['Drol']-=np.dot(fr,vh)*dt; E['Ddamp']-=np.dot(fd,vh)*dt
            a=a_new
            if it%rec_every==0:
                rec['t'].append(t); rec['X'].append(u[self.iFK]); rec['dL'].append(u[self.iB]-u[self.iA])
                rec['NJ'].append(N[self.eJ]); rec['vcm'].append(np.dot(self.m,v)/self.M); rec['xcm'].append(np.dot(self.m,u)/self.M)
                rec['Fbr'].append(Fl.sum())
                Ek=0.5*np.dot(self.m,v*v); Es=0.5*np.sum(self.ke*np.diff(u)**2); Eb=sum(0.5*Fl[j]**2/kb for j in range(len(st)))
                rec['Ek'].append(Ek); rec['Es'].append(Es); rec['Eb'].append(Eb)
            if stop_check and t>0.09 and it%2000==0:
                if abs(np.dot(self.m,v)/self.M)<2e-4 and np.max(np.abs(v))<5e-3: break
        for k in rec: rec[k]=np.array(rec[k])
        E['Ek']=rec['Ek'][-1]; E['Es']=rec['Es'][-1]; E['Eb']=rec['Eb'][-1]
        E['balance_err']=(E['Wext']-(E['Ek']+E['Es']+E['Eb']+E['Dfr']+E['Drol']+E['Ddamp']))
        return rec,E
if __name__=='__main__':
    import time
    mdl=Model(); print('nodes',mdl.n,'M=%.1f'%mdl.M,'dtcrit=%.2e'%mdl.dtcrit,'f=',np.round(mdl.w[1:5]/2/np.pi,2))
    t0=time.time(); rec,E=mdl.run({}, T=0.2); print('run time %.1f s'%(time.time()-t0))
    I=ID; tI=np.array(I['t']); XI=np.array(I['X'])
    Xs=np.interp(tI,rec['t'],rec['X'])
    print('max |X_phys - X_modal| = %.3f mm'%(np.max(abs(Xs-XI))*1e3))
    print('X_FK min %.2f mm; dL range %.3f mm; |NJ|max=%.2f MN'%(rec['X'].min()*1e3,(rec['dL'].max()-rec['dL'].min())*1e3,np.abs(rec['NJ']).max()/1e6))
    print('Energy:',{k:round(v,2) for k,v in E.items()}, 'rel err %.2e'%(E['balance_err']/E['Wext']))
