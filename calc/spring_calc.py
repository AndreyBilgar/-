import numpy as np, json
E=206000.0; nu=0.3  # MPa
De,Di,t,tp,l0=32.0,14.0,3.0,2.94,3.64
h0p=l0-tp
d=De/Di
K1=(1/np.pi)*((d-1)/d)**2/((d+1)/(d-1)-2/np.log(d))
K2=(6/np.pi)*((d-1)/np.log(d)-1)/np.log(d)
K3=(3/np.pi)*(d-1)/np.log(d)
C1=(tp/t)**2/((0.25*l0/t-tp/t+0.75)*(0.625*l0/t-tp/t+0.375))
C2=C1/(tp/t)**3*(5/32*(l0/t-1)**2+1)
K4=np.sqrt(-C1/2+np.sqrt((C1/2)**2+C2))
print('delta=%.4f K1=%.4f K2=%.4f K3=%.4f C1=%.4f C2=%.4f K4=%.4f h0p=%.3f h0p/tp=%.4f'%(d,K1,K2,K3,C1,C2,K4,h0p,h0p/tp))
Q=4*E/(1-nu**2)
def F(s): return Q*K4**2*tp**4/(K1*De**2)*(s/tp)*(K4**2*(h0p/tp-s/tp)*(h0p/tp-s/(2*tp))+1)
def sOM(s): return -Q*tp**2/(K1*De**2)*K4*(s/tp)*3/np.pi
def sII(s): return -Q*K4*tp**2/(K1*De**2)*(s/tp)*(K4*K2*(h0p/tp-s/(2*tp))+K3)
def sIII(s): return -Q*K4*tp**2/(K1*De**2)*(1/d)*(s/tp)*(K4*(K2-2*K3)*(h0p/tp-s/(2*tp))-K3)
ss=np.linspace(0,h0p,15)
rows=[]
for s in [0.1,0.2,0.3,0.35,0.4,0.5,0.525,0.6,0.7]:
    s=min(s,h0p); rows.append((s, F(s), sOM(s), sII(s), sIII(s)))
    print('s=%.3f mm (s/h0=%.2f): F=%.0f N  sigma_OM=%.0f  sigma_II=%.0f sigma_III=%.0f MPa'%(s,s/h0p,F(s),sOM(s),sII(s),sIII(s)))
k0=F(0.001)/0.001; print('initial stiffness %.0f N/mm; secant at 0.75h0: %.0f N/mm'%(k0, F(0.75*h0p)/(0.75*h0p)))
Fc=F(h0p); print('F at flat: %.0f N'%Fc)
# stack: 6 in series; brake: 3 stacks
for frac in [0.25,0.5,0.75]:
    s=frac*h0p; N=3*F(s)
    print('s/h0=%.2f: per-spring s=%.3f mm, stack deflection %.2f mm, N per brake = %.1f kN; friction per brake (mu_sum=0.3..0.8) = %.1f..%.1f kN; per pair %.1f..%.1f kN; 5 pairs %.0f..%.0f kN'%(frac,s,6*s,N/1e3,0.3*N/1e3,0.8*N/1e3,0.6*N/1e3,1.6*N/1e3,3*N/1e3,8*N/1e3))
# plate contact pressure
Aplate=203.0*50.0
print('plate area %.0f mm2; pressure at N(0.75h0)=%.2f MPa'%(Aplate,3*F(0.75*h0p)/Aplate))
json.dump(dict(K=[K1,K2,K3,K4],s=list(np.linspace(0,h0p,50)),F=[F(x) for x in np.linspace(0,h0p,50)],sOM=[sOM(x) for x in np.linspace(0,h0p,50)]),open('spring.json','w'))
