exec(open('slice.py').read().split('res=[]')[0])
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_EDGE, TopAbs_FACE
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Curve, BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Circle, GeomAbs_Plane, GeomAbs_Cone, GeomAbs_Cylinder
done=set()
for path,nm,shp in parts:
    key=None
    for t in ['Пружина','пластина фрикционная','захват)','241(шток)','243(гайка)','242(прижим)','111(корпус)']:
        if t in nm: key=t
    if key is None or key in done: continue
    if len(path)>1 and 'тормоз фрикционный)' not in path[1] and 'тормоз фрикционный)-' not in path[1]: continue
    done.add(key)
    print('=====', nm, path[1] if len(path)>1 else '')
    circ=set()
    ex=TopExp_Explorer(shp,TopAbs_EDGE)
    while ex.More():
        c=BRepAdaptor_Curve(TopoDS.Edge(ex.Current()))
        if c.GetType()==GeomAbs_Circle:
            ci=c.Circle(); l=ci.Location()
            circ.add((round(ci.Radius()*2,2), round(l.X(),2), round(l.Y(),2), round(l.Z(),2)))
        ex.Next()
    for c in sorted(circ)[:40]: print('  circle D=%.2f at (%.2f,%.2f,%.2f)'%c)
    fx=TopExp_Explorer(shp,TopAbs_FACE); planes=[]
    while fx.More():
        f=TopoDS.Face(fx.Current()); s=BRepAdaptor_Surface(f)
        gg=GProp_GProps(); BRepGProp.SurfaceProperties_s(f,gg)
        if s.GetType()==GeomAbs_Plane:
            pl=s.Plane(); n=pl.Axis().Direction(); o=pl.Location()
            planes.append((round(gg.Mass(),1), round(n.X(),3),round(n.Y(),3),round(n.Z(),3), round(o.X(),2),round(o.Y(),2),round(o.Z(),2)))
        elif s.GetType()==GeomAbs_Cone:
            co=s.Cone(); print('  cone semiangle(deg)=%.3f refR=%.3f area=%.1f'%(co.SemiAngle()*57.29578, co.RefRadius(), gg.Mass()))
        fx.Next()
    for p in sorted(planes, reverse=True)[:12]: print('  plane A=%.1f n=(%.3f,%.3f,%.3f) o=(%.2f,%.2f,%.2f)'%p)
