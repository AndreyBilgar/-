from PIL import Image
import numpy as np, json
c=np.array(Image.open('../figures/src/fig3_white.png')).astype(int)
r,g,b=c[:,:,0],c[:,:,1],c[:,:,2]
H,W=r.shape
X0,SX=77.0,5.01
rows=np.array([27,76,124.5,173,221,270,318,367,415,464,513,561,610,658,707]); vals=np.arange(4,-25,-2)
A=np.polyfit(rows,vals,1); print('y calib', A)
tms=lambda col:(col-X0)/SX
ymm=lambda row:np.polyval(A,row)
black=(r<110)&(g<110)&(b<110)
red=(r>180)&(g<110)&(b<110)
def track(mask, col0, col1, row_start, maxjump, rowlim=(0,H)):
    out=[]; prev=row_start
    for col in range(col0,col1):
        ys=np.nonzero(mask[rowlim[0]:rowlim[1],col])[0]+rowlim[0]
        if len(ys)==0: continue
        # group into runs
        runs=np.split(ys, np.nonzero(np.diff(ys)>1)[0]+1)
        cands=[(abs(run.mean()-prev),run) for run in runs]
        d,run=min(cands,key=lambda x:x[0])
        if d<=maxjump:
            y=run.mean(); out.append((col,y)); prev=y
    return np.array(out)
bl=track(black, 80, 1190, 124.5, 14)
# remove the region of legend/labels? report gaps
t=tms(bl[:,0]); x=ymm(bl[:,1])
rd=track(red, 80, 1190, 124.5, 12, rowlim=(15,245))
t2=tms(rd[:,0]); d=ymm(rd[:,1])/10.0
json.dump(dict(t=t.tolist(),x=x.tolist(),td=t2.tolist(),dl=d.tolist()), open('fig3_digitized.json','w'))
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
fig,ax=plt.subplots(2,1,figsize=(14,8))
ax[0].imshow(c[:,:,:3].astype(np.uint8)); ax[0].plot(bl[:,0],bl[:,1],'g-',lw=0.8); ax[0].plot(rd[:,0],rd[:,1],'c-',lw=0.8)
ax[1].plot(t,x,'k-'); ax[1].plot(t2,d*10,'r-'); ax[1].grid()
plt.savefig('digit_check.png',dpi=80)
print(len(t), t.min(), t.max(), x.min(), len(t2))
