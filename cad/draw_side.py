import numpy as np, json, re
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'Liberation Serif','font.size':9})
from matplotlib.collections import PolyCollection
D=np.load('tess.npy',allow_pickle=True)
def cat(g,nm):
    s=g+' '+nm
    if 'рельс' in s: return 'rail'
    if 'тормоз' in s: return 'brake'
    if 'тележка' in s or 'колесо' in s or 'хомут' in s or 'люнет' in s or 'седло' in s or 'рама' in s: return 'carriage'
    if 'форкамер' in s: return 'fk'
    if 'зарядн' in s or 'затвор' in s: return 'zk'
    if 'поршнев' in s: return 'ps'
    if 'баллист' in s or 'надульн' in s: return 'bt'
    if 'муфт' in s: return 'coupling'
    return 'other'
col={'rail':'#b9b9b9','brake':'#d62728','carriage':'#8c8c8c','fk':'#1f77b4','zk':'#2ca02c','ps':'#9467bd','bt':'#ff7f0e','coupling':'#17becf','other':'#7f7f7f'}
VEX=4.0
fig,ax=plt.subplots(figsize=(17/2.54*1.6,3.2))
order=['rail','carriage','other','coupling','zk','ps','fk','bt','brake']
for c in order:
    polys=[]
    for o in D:
        if cat(o['grp'],o['nm'])!=c: continue
        P=o['P']; T=o['T']
        if c=='rail' : 
            # draw rail as rectangle only
            continue
        tri=P[T]  # (n,3,3)
        zz=tri[:,:,2]/1000; yy=tri[:,:,1]/1000*VEX
        polys.append(np.stack([zz,yy],-1))
    if polys:
        pc=PolyCollection(np.concatenate(polys),facecolors=col[c],edgecolors='none',linewidths=0,antialiased=False)
        ax.add_collection(pc)
ax.fill_between([0,33.2],[0,0],[0.1788*VEX]*2,color=col['rail'],zorder=0)
# stations, joints, gauge
st={'S1':2.955,'S2':9.023,'S3':14.524,'S4':21.361,'S5':27.232}
for k,z in st.items():
    ax.annotate(k,(z,0.24*VEX),(z,-0.42),ha='center',fontsize=9,color='#d62728',arrowprops=dict(arrowstyle='->',color='#d62728',lw=0.8))
J={'ЗК–ПС1':3.645,'ПС1–ПС2':8.878,'ПС2–ПС3':14.372,'ПС3–ФК':19.604,'ФК–БТ1':21.906,'БТ1–БТ2':27.131}
for k,z in J.items():
    ax.plot([z,z],[0.62*VEX,0.80*VEX],color='k',lw=0.8); ax.text(z,0.82*VEX,k,rotation=90,fontsize=7,ha='center',va='bottom')
ax.axvline(14.51,color='#008300',ls=':',lw=1); ax.text(14.75,4.55,'центр масс z = 14,51 м',color='#008300',fontsize=8)
ax.text(33.1,4.55,'вертикальный масштаб увеличен в 4 раза',fontsize=7.5,ha='right',color='#52514e')
labels=[(2.2,'зарядная камера'),(6.1,'ПС1'),(11.6,'ПС2'),(17.1,'ПС3'),(20.7,'ФК'),(24.4,'БТ1'),(29.9,'БТ2')]
for z,l in labels: ax.text(z,0.25*VEX,l,fontsize=8,ha='center',color='w' if l in('ПС1','ПС2','ПС3','БТ1') else 'k')
ax.set_xlim(0,33.2); ax.set_ylim(-0.6,4.9); ax.set_xlabel('z, м'); ax.set_yticks([])
ax.set_title('')
for s in ['top','right','left']: ax.spines[s].set_visible(False)
plt.tight_layout(); plt.savefig('../figures/fig_cad_side.png',dpi=220)
print('ok')
