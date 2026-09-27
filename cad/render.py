import numpy as np, json
exec(open('slice.py').read().split('res=[]')[0])
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopoDS import TopoDS
from OCP.BRep import BRep_Tool
from OCP.TopLoc import TopLoc_Location
tris={}
def tess(shp, defl):
    BRepMesh_IncrementalMesh(shp, defl, False, 0.5, True)
    P=[];T=[]; off=0
    ex=TopExp_Explorer(shp,TopAbs_FACE)
    while ex.More():
        f=TopoDS.Face(ex.Current()); loc=TopLoc_Location()
        tri=BRep_Tool.Triangulation_s(f,loc)
        if tri is not None:
            tr=loc.Transformation()
            for i in range(1,tri.NbNodes()+1):
                p=tri.Node(i).Transformed(tr); P.append((p.X(),p.Y(),p.Z()))
            for i in range(1,tri.NbTriangles()+1):
                a,b,c=tri.Triangle(i).Get(); T.append((a-1+off,b-1+off,c-1+off))
            off+=tri.NbNodes()
        ex.Next()
    return np.array(P),np.array(T,dtype=int)
out=[]
for path,nm,shp in parts:
    b=Bnd_Box(); BRepBndLib.Add_s(shp,b,True); p1=b.CornerMin(); p2=b.CornerMax()
    size=max(p2.X()-p1.X(),p2.Y()-p1.Y(),p2.Z()-p1.Z())
    P,T=tess(shp, max(0.5,size/150))
    if len(T)==0: continue
    grp=path[1] if len(path)>1 else nm
    out.append(dict(grp=grp,nm=nm,P=P.astype(np.float32),T=T))
np.save('tess.npy', np.array(out,dtype=object), allow_pickle=True)
print('parts tessellated', len(out), 'triangles', sum(len(o['T']) for o in out))
