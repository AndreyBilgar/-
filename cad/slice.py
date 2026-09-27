import json, sys, time, numpy as np
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString
from OCP.XCAFDoc import XCAFDoc_DocumentTool, XCAFDoc_ShapeTool
from OCP.TDF import TDF_Label
from OCP.collections import Sequence_TDF_Label as Seq
from OCP.TDataStd import TDataStd_Name
from OCP.TopLoc import TopLoc_Location
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
from OCP.gp import gp_Pln, gp_Pnt, gp_Dir
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
doc = TDocStd_Document(TCollection_ExtendedString("doc"))
r = STEPCAFControl_Reader(); r.SetNameMode(True); r.ReadFile('model.stp'); r.Transfer(doc)
stool = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
def name(lab):
    n = TDataStd_Name()
    return n.Get().ToExtString() if lab.FindAttribute(TDataStd_Name.GetID_s(), n) else ''
parts=[]
def walk(lab, loc, path):
    if XCAFDoc_ShapeTool.IsReference_s(lab):
        ref=TDF_Label(); XCAFDoc_ShapeTool.GetReferredShape_s(lab, ref)
        walk(ref, loc.Multiplied(XCAFDoc_ShapeTool.GetLocation_s(lab)), path+[name(lab)]); return
    if XCAFDoc_ShapeTool.IsAssembly_s(lab):
        c=Seq(); XCAFDoc_ShapeTool.GetComponents_s(lab, c)
        for i in range(1,c.Length()+1): walk(c.Value(i), loc, path)
        return
    parts.append((path, name(lab), XCAFDoc_ShapeTool.GetShape_s(lab).Moved(loc)))
roots=Seq(); stool.GetFreeShapes(roots)
for i in range(1,roots.Length()+1): walk(roots.Value(i), TopLoc_Location(), [])
res=[]
t0=time.time()
for idx,(path,nm,shp) in enumerate(parts):
    b=Bnd_Box(); BRepBndLib.Add_s(shp,b,True); p1=b.CornerMin(); p2=b.CornerMax()
    g=GProp_GProps(); BRepGProp.VolumeProperties_s(shp,g); V=g.Mass()
    if 'рельс' in nm: continue
    # coaxial load path candidates: centred on axis x=0,y=334, big enough
    cx=(p1.X()+p2.X())/2; cy=(p1.Y()+p2.Y())/2
    coax = abs(cx)<5 and abs(cy-334)<30 and (p2.X()-p1.X())>100 and V*7850e-9>1.0
    L=p2.Z()-p1.Z()
    step = 20.0
    zs = np.arange(p1.Z()+step/2, p2.Z(), step) if coax else []
    areas=[]
    for z in zs:
        f=BRepBuilderAPI_MakeFace(gp_Pln(gp_Pnt(0,0,z),gp_Dir(0,0,1)),-2000,2000,-2000,2000).Face()
        cm=BRepAlgoAPI_Common(shp,f); cm.Build()
        gg=GProp_GProps(); BRepGProp.SurfaceProperties_s(cm.Shape(),gg); areas.append(gg.Mass())
    res.append(dict(path=path,part=nm,V=V,z0=p1.Z(),z1=p2.Z(),x0=p1.X(),x1=p2.X(),y0=p1.Y(),y1=p2.Y(),coax=coax,zs=list(map(float,zs)),A=areas))
    if coax: print(idx, nm, len(zs), round(time.time()-t0,1), file=sys.stderr)
json.dump(res, open('slices.json','w'), ensure_ascii=False)
print('done', time.time()-t0, file=sys.stderr)
