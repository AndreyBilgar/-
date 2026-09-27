from PIL import Image
import numpy as np, json
c=np.array(Image.open('../figures/src/fig3_white.png')).astype(int)
r,g,b=c[:,:,0],c[:,:,1],c[:,:,2]
red=(r>170)&(g<130)&(b<130)
A=[-0.04119912,5.11870276]
out=[]; prev=124.5; lastcol=80
for col in range(80,1175):
    ys=np.nonzero(red[10:245,col])[0]+10
    if len(ys)==0: continue
    runs=np.split(ys, np.nonzero(np.diff(ys)>1)[0]+1)
    d,run=min([(abs(rr.mean()-prev),rr) for rr in runs],key=lambda z:z[0])
    if d<=8+4*(col-lastcol):
        out.append((col,run.mean())); prev=run.mean(); lastcol=col
out=np.array(out); t=(out[:,0]-77)/5.01; dl=np.polyval(A,out[:,1])/10
tdu=np.arange(1,199,0.1); dlu=np.interp(tdu,t,dl)
print('max %.3f at %.2f, min %.3f at %.2f, range %.3f'%(dlu.max(),tdu[dlu.argmax()],dlu.min(),tdu[dlu.argmin()],dlu.max()-dlu.min()))
json.dump(dict(tdu=tdu.tolist(),dlu=dlu.tolist()), open('dl_proc.json','w'))
P=json.load(open('exp1_proc.json')); p=np.array(json.load(open('fit1.json'))['p'])
tu=np.array(P['tu']); xu=np.array(P['xu'])
osc=xu-(p[0]+p[1]*(tu-72)*1e-3+p[2]*((tu-72)*1e-3)**2)
s2=(tdu>=72)&(tdu<=198); oscX=np.interp(tdu[s2],tu,osc)
k=np.polyfit(oscX,dlu[s2],1); print('dL = %.4f*Xosc + %.4f corr %.3f'%(k[0],k[1],np.corrcoef(oscX,dlu[s2])[0,1]))
# excluding the 105-118 ms event
s3=s2&~((tdu>104)&(tdu<120)); oscX3=np.interp(tdu[s3],tu,osc)
k3=np.polyfit(oscX3,dlu[s3],1); print('excl. event: dL = %.4f*Xosc + %.4f corr %.3f'%(k3[0],k3[1],np.corrcoef(oscX3,dlu[s3])[0,1]))
