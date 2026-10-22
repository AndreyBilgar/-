import json, numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams.update({'font.family':'Liberation Serif','font.size':9,'axes.titlesize':9,'axes.labelsize':9,'legend.fontsize':8,
 'xtick.labelsize':8,'ytick.labelsize':8,'axes.grid':True,'grid.color':'#d9d9d9','grid.linewidth':0.5,'axes.edgecolor':'#52514e',
 'axes.linewidth':0.6,'lines.linewidth':1.3,'figure.dpi':100,'savefig.dpi':300,'axes.spines.top':False,'axes.spines.right':False,
 'mathtext.fontset':'stix'})
from matplotlib.ticker import FuncFormatter
def _fmt(v,p):
    t='{:g}'.format(round(v,6)); return t.replace('.',',').replace('-','−')
_orig_save=plt.savefig
def _commafy_save(*a,**k):
    for ax_ in plt.gcf().axes:
        if getattr(ax_,'_img',False): continue
        if not getattr(ax_,'_cat',False): ax_.xaxis.set_major_formatter(FuncFormatter(_fmt))
        ax_.yaxis.set_major_formatter(FuncFormatter(_fmt))
    return _orig_save(*a,**k)
plt.savefig=_commafy_save
C=['#2a78d6','#eb6834','#1baf7a','#eda100','#e87ba4','#008300','#4a3aa7','#e34948']
INK='#0b0b0b'; INK2='#52514e'
W=17/2.54
F='../figures/'
def lab(ax,s): ax.text(-0.08,1.04,s,transform=ax.transAxes,fontsize=10,fontweight='bold',va='bottom')
# ---------- data
P=json.load(open('exp1_proc.json')); p=json.load(open('fit1.json'))['p']
tu=np.array(P['tu']); xu=np.array(P['xu'])
MP=json.load(open('modes_phys.json'))
TH=json.load(open('timehist.json')); ID=json.load(open('ident_phys.json'))
S=json.load(open('spring.json'))
LY=json.load(open('layouts.json'))
SF=json.load(open('scanF.json'))
OP=json.load(open('optim.json'))
# ---------- panels: experiment processing
def model(tt):
    a0,a1,a2,A,al,w,ph=p; tau=(tt-72.0)*1e-3
    return a0+a1*tau+a2*tau**2+A*np.exp(-al*tau)*np.cos(w*tau+ph), a0+a1*tau+a2*tau**2
def draw_exp_proc(a0,a1,labels='аб'):
    s=(tu>=45)
    a0.plot(tu[s],xu[s],color=INK,lw=1.0,label='эксперимент')
    tt=np.linspace(72,198,800); xm,xd=model(tt)
    a0.plot(tt,xm,color=C[1],lw=1.2,ls='--',label='модель «дрейф + форма»')
    a0.plot(tt,xd,color=C[0],lw=1.0,label='дрейф $x_d(t)$')
    a0.set_xlabel('t, мс'); a0.set_ylabel('$X_{\\mathrm{ФК}}$, мм'); a0.legend(loc='upper right',frameon=False); a0.set_xlim(45,200); lab(a0,labels[0])
    lbl=[67.13,71.43,80.48,88.35,96.62,103.96,112.78,119.51,128.52,135.00,143.73,151.08,159.41,166.17,174.92,181.61,189.66,196.71]
    L=np.array(lbl); d=np.diff(L); up=d[0::2]; dn=d[1::2]
    a1.plot(np.arange(1,len(up)+1),up,'o-',color=C[0],ms=4,label='рост (min→max)')
    a1.plot(np.arange(1,len(dn)+1),dn,'s-',color=C[1],ms=4,label='спад (max→min)')
    T=2*np.pi/p[5]*1e3; dT=1.503
    a1.axhline(T/2-dT/2,color=C[0],ls=':',lw=1); a1.axhline(T/2+dT/2,color=C[1],ls=':',lw=1)
    a1.text(4.6,9.35,'прогноз (дрейф)',fontsize=7.5,color=C[1]); a1.text(5.6,6.05,'прогноз (дрейф)',fontsize=7.5,color=C[0])
    a1.set_xlabel('номер полуцикла'); a1.set_ylabel('длительность, мс'); a1.legend(frameon=False,loc='lower right'); a1.set_ylim(3.5,10); lab(a1,labels[1])
# ---------- panels: mode shapes in relative coordinate with section schematic (no dimensions)
def draw_modes(a0,a1):
    zn=np.array(MP['zn'])
    L0,L1=zn[0],zn[-1]; xi=lambda z:(np.asarray(z)-L0)/(L1-L0)
    V=np.array(MP['V']); w=np.array(MP['w'])
    J={'ЗК–ПС1':3.645,'ПС1–ПС2':8.878,'ПС2–ПС3':14.372,'ПС3–ФК':19.604,'ФК–БТ1':21.906,'БТ1–БТ2':27.131}
    bounds=[L0]+list(J.values())+[L1]; names=['ЗК','ПС1','ПС2','ПС3','ФК','БТ1','БТ2']
    for i,nm in enumerate(names):
        x0,x1=xi(bounds[i]),xi(bounds[i+1])
        a0.add_patch(plt.Rectangle((x0,0.15),x1-x0,0.7,fc='#e6e6e6',ec=INK2,lw=0.6))
        a0.text((x0+x1)/2,0.5,nm,ha='center',va='center',fontsize=8)
    a0.set_ylim(0,1); a0.axis('off')
    for k,cc in ((1,C[0]),(2,C[1])):
        ph=V[k]/np.max(np.abs(V[k])); a1.plot(xi(zn),ph,color=cc,label='форма %d, f = %s Гц'%(k,('%.1f'%(w[k]/2/np.pi)).replace('.',',')))
    a1.axhline(0,color=INK2,lw=0.6)
    for kk,z in MP['st'].items():
        a1.plot([xi(z)],[np.interp(z,zn,V[1]/np.max(np.abs(V[1])))],'o',color=C[7],ms=5,zorder=5); a1.text(xi(z),-1.33,kk,ha='center',fontsize=8,color=INK)
    for kk,z in J.items(): a1.axvline(xi(z),color='#9a9a9a',lw=0.6,ls='--')
    a1.set_ylim(-1.45,1.25); a1.set_xlim(0,1); a1.set_xlabel('ξ = z/L'); a1.set_ylabel('$\\mathrm{\\varphi}_k$ (норм.)'); a1.legend(frameon=False,loc='upper left')
# ---------- panels: identification
def pulse(t,t0,tau):
    s=(t-t0)/tau; return np.where((s>0)&(s<1),np.sin(np.pi*s)**2,0)
def draw_ident(a0,a1,a2,labels='абв'):
    pp=ID['p']; b=TH['base']; t=np.array(b['t'])*1e3
    a0.plot(tu,xu,color=INK,lw=1.0,label='эксперимент')
    a0.plot(t,np.array(b['X'])*1e3,color=C[1],ls='--',lw=1.2,label='КЭ-модель с идентифицированными нагрузками')
    a0.plot(t,np.array(b['xcm'])*1e3,color=C[0],lw=1.0,label='центр масс (модель)')
    a0.set_ylabel('перемещение, мм'); a0.set_ylim(-26,2); a0.legend(frameon=False,loc='lower left'); lab(a0,labels[0])
    tt=np.linspace(40,200,2000)
    a1.plot(tt,pp[0]*pulse(tt,pp[1],pp[2]),color=C[0],label='$P(t)$ — казённая часть')
    a1.plot(tt,pp[3]*pulse(tt,pp[4],pp[5]),color=C[1],label='$Q(t)$ — форкамера')
    a1.axvline(48.9,color=INK2,lw=0.7,ls=':'); a1.text(35.2,2.25,'D1 = 48,9 мс',fontsize=7.5,color=INK2)
    a1.axvline(70.07,color=INK2,lw=0.7,ls=':'); a1.text(71.0,2.25,'вылет 70,07 мс',fontsize=7.5,color=INK2)
    a1.set_ylabel('сила, МН'); a1.legend(frameon=False,loc='upper right'); a1.set_ylim(0,2.7); lab(a1,labels[1])
    a2.plot(t,np.array(b['vcm']),color=C[2]); a2.axhline(0,color=INK2,lw=0.6)
    a2.set_ylabel('$v_{\\mathrm{цм}}$, м/с'); a2.set_xlabel('t, мс'); a2.set_xlim(30,200); lab(a2,labels[2])
# ---------- panels: disc spring & brake characteristic
def draw_spring(a0,a1,labels='аб',compact=False):
    s=np.array(S['s']); Fs=np.array(S['F'])
    a0.plot(s,Fs/1e3,color=C[0],label='формула Альмена — Ласло')
    a0.plot(s,34.05*s,color=INK2,ls=':',lw=1,label='линейное приближение')
    a0.axvline(0.35,color=C[7],lw=0.7,ls='--'); a0.text(0.36,2,'$s=0{,}5h_0$',fontsize=7.5,color=INK2)
    a0.set_xlabel('прогиб одной пружины s, мм'); a0.set_ylabel('F, кН'); a0.legend(frameon=False,loc='upper left'); lab(a0,labels[0])
    Dl=6*s; Nb=3*Fs/1e3
    a1.plot(Dl,Nb,color=C[0],label='нормальная сила $N$ на тормоз')
    a1.fill_between(Dl,0.3*Nb,0.8*Nb,color=C[1],alpha=0.25,lw=0,label='сила трения $\\mathrm{\\mu}_\\Sigma N$, $\\mathrm{\\mu}_\\Sigma$=0,3…0,8')
    a1.axvline(2.1,color=C[7],lw=0.7,ls='--'); a1.axhspan(3.0,3.7,color=C[2],alpha=0.35,lw=0)
    if compact: a1.text(2.9,6.0,'опыты 2–3',fontsize=7,color=INK)
    else: a1.text(2.25,6.0,'уровень опытов 2–3\n(3,0…3,7 кН на тормоз)',fontsize=7.5,color=INK)
    a1.set_xlabel('сжатие пакета Δ, мм'); a1.set_ylabel('кН'); a1.legend(frameon=False,loc='upper left',fontsize=7 if compact else 8); lab(a1,labels[1])
# ---------- panels: friction efficiency
def draw_eff(a0,label='а',loc='center left'):
    r=np.linspace(0,1,300)
    a0.plot(r,2/np.pi*np.arcsin(r),color=C[0],label='η(r) — торможение отката')
    a0.plot(r,np.sqrt(1-r**2),color=C[1],label='κ(r) — гашение колебаний')
    a0.set_xlabel('r = $V_d/(\\mathrm{\\omega} A_j)$'); a0.set_ylabel('доля от $F_j$'); a0.legend(frameon=False,loc=loc); lab(a0,label)
def draw_amp(a1,label='б'):
    amp=LY['amp']; ks=list(amp.keys()); vals=[abs(amp[k]) for k in ks]
    a1.bar(ks,vals,color=C[0],width=0.55); a1._cat=True
    for i,v in enumerate(vals): a1.text(i,v+0.03,('%.2f'%v).replace('.',','),ha='center',fontsize=8)
    a1.set_ylim(0,1.15); a1.set_ylabel('$|\\mathrm{\\varphi}_1(z_j)|$ (норм.)'); a1.grid(axis='x'); lab(a1,label)
# ---------- panels: recoil vs brake force
SCAN_NAMES={'uniform':'равномерная 1-1-1-1-1','ends':'концевая S1+S5','node':'узловая S2-S3-S4','opt':'рекомендуемая S1:S2:S3 = 0,48:0,18:0,32'}
def draw_scan(axs,labels='абв'):
    cols={'uniform':C[0],'ends':C[1],'node':C[2],'opt':C[6]}
    for k in ['uniform','ends','node','opt']:
        d=SF[k]; F_=[x['F'] for x in d]
        axs[0].plot(F_,[x['Xmax200'] for x in d],'o-',ms=3,color=cols[k],label=SCAN_NAMES[k])
        axs[1].plot(F_,[x['Xfin'] for x in d],'o-',ms=3,color=cols[k])
        axs[2].plot(F_,[x['A170'] for x in d],'o-',ms=3,color=cols[k])
    for y,t_ in ((23,'оп. 1'),(18,'оп. 2'),(17,'оп. 3')):
        axs[0].axhline(y,color=INK2,lw=0.6,ls=':'); axs[0].text(203,y,t_,fontsize=7,va='center',color=INK2)
    axs[0].set_ylabel('$X_{\\mathrm{ФК},\\max}$ (0–200 мс), мм'); axs[1].set_ylabel('полный откат, мм'); axs[2].set_ylabel('амплитуда при 170–200 мс, мм')
    for a,l in zip(axs,labels): a.set_xlabel('$F_\\Sigma$, кН'); lab(a,l); a.set_xlim(0,200)
    axs[1].set_ylim(0,42); axs[2].set_ylim(0,1.2)
# ---------- panels: Pareto at 30 and 100 kN
def draw_pareto(axs,labels='аб'):
    R=LY['results']
    num={'5 пар (1-1-1-1-1)':'1','4 пары без S1':'2','4 пары без S2':'3','4 пары без S3':'4','4 пары без S4':'5','4 пары без S5':'6','аналог 2-1-1':'7','концевые S1+S5':'8','узловая S2-S3-S4':'9','пропорц. массе':'10'}
    for a_,Fk,ttl in ((axs[0],'30','$F_\\Sigma$ = 30 кН'),(axs[1],'100','$F_\\Sigma$ = 100 кН')):
        for k,v in R.items():
            if k in ('без тормозов','рекомендуемая'): continue
            x=v[Fk]['Xfin']; y=v[Fk]['A_170_200']
            a_.plot(x,y,'o',color=C[1] if k=='аналог 2-1-1' else C[0],ms=5)
            a_.annotate(num[k],(x,y),(3,3),textcoords='offset points',fontsize=7.5,color=INK)
        rr=R['рекомендуемая'][Fk]; a_.plot(rr['Xfin'],rr['A_170_200'],'*',color=C[6],ms=11)
        a_.set_xlabel('полный откат, мм'); a_.set_title(ttl); a_.set_ylabel('амплитуда при 170–200 мс, мм')
    axs[0].plot(OP['30']['opt'][0],OP['30']['opt'][1],'D',color=C[6],ms=5)
    lab(axs[0],labels[0]); lab(axs[1],labels[1])
# ---------- panels: time histories
def draw_time(a0,a1,labels='аб'):
    names2={'base':'без тормозов (опыт 1)','test30':'5 пар, 30 кН (уровень опытов 2–3)','opt60':'рекомендуемая, 60 кН','uni100':'5 пар, 100 кН'}
    cc={'base':INK,'test30':C[0],'opt60':C[6],'uni100':C[1]}
    for k in ['base','test30','opt60','uni100']:
        d=TH[k]; t=np.array(d['t'])*1e3
        a0.plot(t,np.array(d['X'])*1e3,color=cc[k],lw=1.0,label=names2[k])
        s_=t<=200; a1.plot(t[s_],np.array(d['NJ'])[s_]/1e6,color=cc[k],lw=0.9)
    a0.set_ylabel('$X_{\\mathrm{ФК}}$, мм'); a0.set_xlabel('t, мс'); a0.legend(frameon=False,loc='upper right',ncol=2); a0.set_xlim(40,600); a0.set_ylim(-43,9); lab(a0,labels[0])
    a1.set_ylabel('$N_J$ (ПС3–ФК), МН'); a1.set_xlabel('t, мс'); a1.set_xlim(40,200); lab(a1,labels[1])

if __name__=='__main__':
    fig,ax=plt.subplots(1,2,figsize=(W,2.6),gridspec_kw=dict(width_ratios=[1.6,1]))
    draw_exp_proc(ax[0],ax[1]); plt.tight_layout(); plt.savefig(F+'fig_exp_proc.png'); plt.close()
    fig,ax=plt.subplots(2,1,figsize=(W,3.3),sharex=True,gridspec_kw=dict(height_ratios=[0.22,1]))
    draw_modes(ax[0],ax[1]); plt.tight_layout(h_pad=0.2); plt.savefig(F+'fig_modes.png'); plt.close()
    fig,ax=plt.subplots(3,1,figsize=(W,4.7),sharex=True,gridspec_kw=dict(height_ratios=[1.5,1,1]))
    draw_ident(*ax); plt.tight_layout(); plt.savefig(F+'fig_ident.png'); plt.close()
    fig,ax=plt.subplots(1,2,figsize=(W,2.6))
    draw_spring(ax[0],ax[1]); plt.tight_layout(); plt.savefig(F+'fig_spring.png'); plt.close()
    fig,ax=plt.subplots(1,2,figsize=(W,2.5),gridspec_kw=dict(width_ratios=[1.2,1]))
    draw_eff(ax[0]); draw_amp(ax[1]); plt.tight_layout(); plt.savefig(F+'fig_eff.png'); plt.close()
    print('ok')
    fig,ax=plt.subplots(1,3,figsize=(W,2.7))
    draw_scan(ax)
    fig.legend(*ax[0].get_legend_handles_labels(),loc='upper center',ncol=4,frameon=False,fontsize=7.5,bbox_to_anchor=(0.5,1.0))
    plt.tight_layout(rect=(0,0,1,0.9)); plt.savefig(F+'fig_scanF.png'); plt.close()
    fig,ax=plt.subplots(1,2,figsize=(W,2.7))
    draw_pareto(ax); plt.tight_layout(); plt.savefig(F+'fig_pareto.png'); plt.close()
    fig,ax=plt.subplots(2,1,figsize=(W,3.3))
    draw_time(ax[0],ax[1]); plt.tight_layout(); plt.savefig(F+'fig_timehist.png'); plt.close()
    print('ok2')
