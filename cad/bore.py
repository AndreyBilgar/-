import sys
exec(open('slice.py').read().split('res=[]')[0])
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_EDGE, TopAbs_VERTEX
from OCP.BRep import BRep_Tool
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Curve
import math
targets=['труба поршневая','труба баллистическая','форкамера)','камера зарядная)','муфта)']
for path,nm,shp in parts:
    if not any(t in nm for t in targets): continue
    b=Bnd_Box(); BRepBndLib.Add_s(shp,b,True); z0=b.CornerMin().Z(); z1=b.CornerMax().Z()
    zz = [z0+(z1-z0)*f for f in (0.1,0.3,0.5,0.7,0.9)]
    out=[]
    for z in zz:
        f=BRepBuilderAPI_MakeFace(gp_Pln(gp_Pnt(0,0,z),gp_Dir(0,0,1)),-2000,2000,-2000,2000).Face()
        cm=BRepAlgoAPI_Common(shp,f); cm.Build()
        rs=[]
        ex=TopExp_Explorer(cm.Shape(),TopAbs_EDGE)
        while ex.More():
            e=TopoDS.Edge(ex.Current()); c=BRepAdaptor_Curve(e)
            for t in [c.FirstParameter()+(c.LastParameter()-c.FirstParameter())*k/4 for k in range(5)]:
                p=c.Value(t); rs.append(math.hypot(p.X(),p.Y()-334.0))
            ex.Next()
        gg=GProp_GProps(); BRepGProp.SurfaceProperties_s(cm.Shape(),gg)
        if rs: out.append((round(z), round(2*min(rs),1), round(2*max(rs),1), round(gg.Mass()/100,1)))
    print(nm, out)
