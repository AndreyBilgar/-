exec(open('slice.py').read().split('res=[]')[0])
import numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'Liberation Serif','font.size':11})
from matplotlib.patches import Polygon
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopoDS import TopoDS
from OCP.BRep import BRep_Tool
from OCP.TopLoc import TopLoc_Location
zs=21794.8
fig,ax=plt.subplots(figsize=(6.2,5.2))
def colr(nm):
    if 'Пружина' in nm: return '#e8b81a'
    if 'пластина' in nm: return '#6b3d1f'
    if 'захват' in nm: return '#c0392b'
    if '111' in nm and 'корпус' in nm: return '#e07b6a'
    if 'рельс' in nm: return '#b5b5b5'
    if 'шток' in nm: return '#34495e'
    if 'гайка' in nm or 'прижим' in nm: return '#7f8c8d'
    if 'Болт' in nm or 'Шайба' in nm: return '#95a5a6'
    return '#bbbbbb'
for path,nm,shp in parts:
    b=Bnd_Box(); BRepBndLib.Add_s(shp,b,True); p1=b.CornerMin(); p2=b.CornerMax()
    if not (p1.Z()<=zs<=p2.Z()): continue
    if p1.X()<250 or p2.X()>480: continue
    if p2.Y()>300: continue
    f=BRepBuilderAPI_MakeFace(gp_Pln(gp_Pnt(0,0,zs),gp_Dir(0,0,1)),-2000,2000,-2000,2000).Face()
    cm=BRepAlgoAPI_Common(shp,f); cm.Build(); sec=cm.Shape()
    BRepMesh_IncrementalMesh(sec,0.2,False,0.3,True)
    ex=TopExp_Explorer(sec,TopAbs_FACE)
    while ex.More():
        fc=TopoDS.Face(ex.Current()); loc=TopLoc_Location(); tri=BRep_Tool.Triangulation_s(fc,loc)
        if tri is not None:
            tr=loc.Transformation()
            P=np.array([[tri.Node(i).Transformed(tr).X(),tri.Node(i).Transformed(tr).Y()] for i in range(1,tri.NbNodes()+1)])
            for i in range(1,tri.NbTriangles()+1):
                a,b_,c=tri.Triangle(i).Get()
                ax.add_patch(Polygon(P[[a-1,b_-1,c-1]],closed=True,fc=colr(nm),ec=colr(nm),lw=0.2))
        ex.Next()
ax.set_xlim(290,440); ax.set_ylim(95,262); ax.set_aspect('equal')
ax.set_xlabel('x, мм'); ax.set_ylabel('y, мм')
ann=[('головка\nрельса Р65',(362,160),(292,108)),('фрикционная\nпластина',(375,181),(408,165)),('пакет из 6\nтарельчатых\nпружин',(372,205),(405,238)),
     ('захват',(405,140),(415,115)),('корпус',(330,215),(292,242)),('шток,\nгайка',(362,186),(292,195))]
for t,xy,xyt in ann: ax.annotate(t,xy,xyt,fontsize=10,arrowprops=dict(arrowstyle='->',lw=0.8))
ax.grid(alpha=0.3)
plt.tight_layout(); plt.savefig('../figures/fig_brake_section.png',dpi=200); print('ok')
