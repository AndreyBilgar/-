import numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
D=np.load('tess.npy',allow_pickle=True)
z0,z1=21.12e3,21.93e3
sel=[]
for o in D:
    P=o['P']
    if P[:,2].max()<z0 or P[:,2].min()>z1: continue
    if 'шпилька' in o['nm'] or 'баллистическая' in o['nm'] or '162(фланец)' in o['nm'] or 'Шайба 42' in o['nm']: continue
    sel.append(o)
def color(o):
    s=o['grp']+' '+o['nm']
    if 'Пружина' in s: return np.array([0.95,0.75,0.1])
    if 'пластина фрикц' in s: return np.array([0.35,0.2,0.1])
    if 'тормоз' in s: return np.array([0.85,0.2,0.2])
    if 'рельс' in s: return np.array([0.72,0.72,0.72])
    if 'тяга' in s or 'ось)' in s: return np.array([0.2,0.6,0.2])
    if 'хомут' in s or 'колесо' in s or 'прижим' in s: return np.array([0.55,0.55,0.6])
    if 'форкамер' in s: return np.array([0.25,0.45,0.75])
    if 'баллист' in s: return np.array([0.95,0.55,0.2])
    return np.array([0.6,0.6,0.6])
# view: azimuth/elevation
az,el=np.radians(-50),np.radians(22)
R1=np.array([[np.cos(az),0,np.sin(az)],[0,1,0],[-np.sin(az),0,np.cos(az)]])
R2=np.array([[1,0,0],[0,np.cos(el),-np.sin(el)],[0,np.sin(el),np.cos(el)]])
R=R2@R1
light=np.array([0.4,0.8,0.6]); light/=np.linalg.norm(light)
polys=[];cols=[];depth=[]
for o in sel:
    P=o['P'].astype(float).copy(); T=o['T']
    # clip rail to window
    tri=P[T]
    cz=tri[:,:,2].mean(1); tri=tri[(cz>=z0)&(cz<=z1)]
    if len(tri)==0: continue
    if 'рельс' in o['nm']:
        keep=(tri[:,:,2].min(1)>=z0-200)&(tri[:,:,2].max(1)<=z1+200)
        tri=tri[keep]
        if len(tri)==0:
            # rail triangles are long; draw box instead
            pass
    c0=color(o)
    tri=tri-np.array([0,300,21550])
    tr=tri@R.T
    n=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]); nn=np.linalg.norm(n,axis=1)+1e-12; n=n/nn[:,None]
    sh=0.35+0.65*np.abs(n@light)
    polys.append(tr[:,:,:2]); cols.append(np.clip(c0[None,:]*sh[:,None],0,1)); depth.append(tr[:,:,2].mean(1))
# rails as boxes (clipped)
for xs in (362.5,-362.5):
    x0,x1=xs-75,xs+75; y0,y1=0,178.8
    V=np.array([[x0,y0,z0],[x1,y0,z0],[x1,y1,z0],[x0,y1,z0],[x0,y0,z1],[x1,y0,z1],[x1,y1,z1],[x0,y1,z1]],float)
    F=[[0,1,2],[0,2,3],[4,6,5],[4,7,6],[3,2,6],[3,6,7],[0,4,5],[0,5,1],[1,5,6],[1,6,2],[0,3,7],[0,7,4]]
    tri=V[np.array(F)]-np.array([0,300,21550]); tr=tri@R.T
    n=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]); n=n/np.linalg.norm(n,axis=1)[:,None]
    polys.append(tr[:,:,:2]); cols.append(np.clip(np.array([0.75,0.75,0.75])[None,:]*(0.35+0.65*np.abs(n@light))[:,None],0,1)); depth.append(tr[:,:,2].mean(1))
polys=np.concatenate(polys); cols=np.concatenate(cols); depth=np.concatenate(depth)
o=np.argsort(depth)  # far first (more negative z in view = farther?) 
fig,ax=plt.subplots(figsize=(8,5.2))
ax.add_collection(PolyCollection(polys[o],facecolors=cols[o],edgecolors='none',antialiased=False))
ax.set_xlim(polys[:,:,0].min(),polys[:,:,0].max()); ax.set_ylim(polys[:,:,1].min(),polys[:,:,1].max()); ax.set_aspect('equal'); ax.axis('off')
plt.tight_layout(); plt.savefig('../figures/fig_brake3d.png',dpi=150)
print(len(polys))
