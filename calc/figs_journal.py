# Composite figures for the journal version (limit of 5-7 figures): 11 article figures -> 7.
# Panels are drawn by the same functions as in figs.py, so data and styling are identical.
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from figs import *
J=F+'journal/'
import os; os.makedirs(J,exist_ok=True)
BOLD='/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf'
def ink_bbox(im,box):
    a=np.asarray(im.convert('L').crop(box))<128
    ys,xs=np.nonzero(a)
    return (box[0]+xs.min(),box[1]+ys.min(),box[0]+xs.max(),box[1]+ys.max())
def relabel(im,box,letter,size):
    x0,y0,x1,y1=ink_bbox(im,box); d=ImageDraw.Draw(im)
    d.rectangle((x0-2,y0-2,x1+2,y1+2),fill='white')
    d.text((x0,y1),letter,fill='black',font=ImageFont.truetype(BOLD,size),anchor='ls')
# ---------- Fig 1: object (photo, video frame) + brake station (render, section)
top=Image.open(F+'fig_setup.png').convert('RGB')
brk=Image.open(F+'fig_brake.png').convert('RGB')
# panel letters of fig_brake: 'а' x-height 20 px (y 25-45) -> Liberation Serif Bold 44 px gives the same letter size
relabel(brk,(0,0,70,70),'в',44); relabel(brk,(1020,0,1100,70),'г',44)
brk=brk.resize((top.width,int(round(brk.height*top.width/brk.width))),Image.LANCZOS)
gap=24; out=Image.new('RGB',(top.width,top.height+gap+brk.height),'white')
out.paste(top,(0,0)); out.paste(brk,(0,top.height+gap)); out.save(J+'fig1_object.png',dpi=(300,300))
# ---------- Fig 2: record of test 1 + processing
img=np.asarray(Image.open('../figures/src/image5.png').convert('RGB'))[:,1:]  # drop the 1-px black left border
fig=plt.figure(figsize=(W,5.6))
gs=fig.add_gridspec(2,2,height_ratios=[1.5,1],width_ratios=[1.6,1])
ai=fig.add_subplot(gs[0,:]); ai.imshow(img,interpolation='lanczos'); ai.axis('off'); ai._img=True
ai.text(0.115,1.0,'а',transform=ai.transAxes,fontsize=10,fontweight='bold',va='bottom')
a0=fig.add_subplot(gs[1,0]); a1=fig.add_subplot(gs[1,1])
draw_exp_proc(a0,a1,labels='бв'); plt.tight_layout(h_pad=0.6); plt.savefig(J+'fig2_test1.png'); plt.close()
# ---------- Fig 3: modes (unchanged)
Image.open(F+'fig_modes.png').save(J+'fig3_modes.png',dpi=(300,300))
# ---------- Fig 4: identification (unchanged)
Image.open(F+'fig_ident.png').save(J+'fig4_ident.png',dpi=(300,300))
# ---------- Fig 5: disc spring and brake characteristic + dry friction efficiency
fig,ax=plt.subplots(1,3,figsize=(W,2.55),gridspec_kw=dict(width_ratios=[1,1.1,0.95]))
draw_spring(ax[0],ax[1],labels='аб',compact=True); draw_eff(ax[2],label='в',loc='upper center')
ax[0].set_ylim(-1,33); ax[0].legend(frameon=True,loc='upper left',fontsize=7,facecolor='white',edgecolor='none',framealpha=1)
leg=ax[1].get_legend(); leg.set_frame_on(True); leg.get_frame().set(facecolor='white',edgecolor='none',alpha=1)
ax[1].set_ylim(0,95); ax[2].set_ylim(0,1.5); ax[2].set_yticks([0,0.2,0.4,0.6,0.8,1.0])
plt.tight_layout(w_pad=0.8); plt.savefig(J+'fig5_brake_eff.png'); plt.close()
# ---------- Fig 6: brake force scan + Pareto comparison of layouts
fig=plt.figure(figsize=(W,5.5))
gs=fig.add_gridspec(2,6,height_ratios=[1,1])
axs=[fig.add_subplot(gs[0,2*i:2*i+2]) for i in range(3)]
draw_scan(axs,labels='абв')
fig.legend(*axs[0].get_legend_handles_labels(),loc='upper center',ncol=4,frameon=False,fontsize=7.5,bbox_to_anchor=(0.5,1.0))
axp=[fig.add_subplot(gs[1,0:3]),fig.add_subplot(gs[1,3:6])]
draw_pareto(axp,labels='гд')
plt.tight_layout(rect=(0,0,1,0.955),h_pad=1.0); plt.savefig(J+'fig6_layouts.png'); plt.close()
# ---------- Fig 7: time histories (unchanged)
Image.open(F+'fig_timehist.png').save(J+'fig7_time.png',dpi=(300,300))
print('journal figures ok')
# ---------- rule 8: figure files for submission (.tif/.jpg, 300 dpi) and compact copies for the docx (archive <= 5 MB)
SUB='../article/journal/submission/'
os.makedirs(SUB,exist_ok=True)
NAMES=['fig1_object','fig2_test1','fig3_modes','fig4_ident','fig5_brake_eff','fig6_layouts','fig7_time']
for k,nm in enumerate(NAMES,1):
    im=Image.open(J+nm+'.png').convert('RGB')
    if k==1:   # photographs and a render: JPEG
        im.save(SUB+'Рисунок_%d.jpg'%k,quality=92,subsampling=0,dpi=(300,300)); im.save(J+nm+'_doc.jpg',quality=92,subsampling=0,dpi=(300,300))
    else:      # line art: 256-colour palette, lossless LZW TIFF
        q=im.quantize(colors=256,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE)
        q.save(SUB+'Рисунок_%d.tif'%k,compression='tiff_lzw',dpi=(300,300)); q.save(J+nm+'_doc.png',optimize=True,dpi=(300,300))
print('submission figures ok')
