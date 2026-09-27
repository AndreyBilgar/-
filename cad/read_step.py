import json, sys, time
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString
from OCP.XCAFDoc import XCAFDoc_DocumentTool, XCAFDoc_ShapeTool
from OCP.TDF import TDF_Label
from OCP.collections import Sequence_TDF_Label as TDF_LabelSequence
from OCP.TDataStd import TDataStd_Name
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
from OCP.TopLoc import TopLoc_Location
from OCP.IFSelect import IFSelect_RetDone
t0=time.time()
doc = TDocStd_Document(TCollection_ExtendedString("doc"))
r = STEPCAFControl_Reader(); r.SetNameMode(True)
st = r.ReadFile('model.stp'); assert st==IFSelect_RetDone, st
r.Transfer(doc)
print('read', time.time()-t0, file=sys.stderr)
stool = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
def name(lab):
    n = TDataStd_Name()
    if lab.FindAttribute(TDataStd_Name.GetID_s(), n):
        return n.Get().ToExtString()
    return ''
out=[]
def walk(lab, loc, path, depth):
    ref = TDF_Label()
    nm = name(lab)
    if XCAFDoc_ShapeTool.IsReference_s(lab):
        XCAFDoc_ShapeTool.GetReferredShape_s(lab, ref)
        l2 = loc.Multiplied(XCAFDoc_ShapeTool.GetLocation_s(lab))
        walk(ref, l2, path+[nm], depth)
        return
    if XCAFDoc_ShapeTool.IsAssembly_s(lab):
        comps = TDF_LabelSequence()
        XCAFDoc_ShapeTool.GetComponents_s(lab, comps)
        for i in range(1, comps.Length()+1):
            walk(comps.Value(i), loc, path, depth+1)
        return
    shp = XCAFDoc_ShapeTool.GetShape_s(lab).Moved(loc)
    g = GProp_GProps(); BRepGProp.VolumeProperties_s(shp, g)
    V = g.Mass(); c = g.CentreOfMass()
    M = g.MatrixOfInertia()
    b = Bnd_Box(); BRepBndLib.Add_s(shp, b, True)
    p1=b.CornerMin(); p2=b.CornerMax(); xmin,ymin,zmin,xmax,ymax,zmax = p1.X(),p1.Y(),p1.Z(),p2.X(),p2.Y(),p2.Z()
    out.append(dict(path=path, part=nm, V=V, c=[c.X(),c.Y(),c.Z()],
       I=[[M.Value(i,j) for j in (1,2,3)] for i in (1,2,3)],
       bb=[xmin,ymin,zmin,xmax,ymax,zmax]))
roots = TDF_LabelSequence(); stool.GetFreeShapes(roots)
for i in range(1, roots.Length()+1):
    walk(roots.Value(i), TopLoc_Location(), [], 0)
json.dump(out, open('parts.json','w'), ensure_ascii=False)
print('parts', len(out), time.time()-t0, file=sys.stderr)
