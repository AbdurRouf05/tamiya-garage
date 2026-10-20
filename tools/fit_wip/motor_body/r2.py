import json, subprocess
from common import *
src = str(SRC)
objs = [{"kind":"stl","path":src+"/chassis-super-1-motor-bracket.stl","color":[0.9,0.25,0.2]}]
o = str(OUT)
c = [40.5, 90.1, 18.0]
cams = [
 {"out":o+"/br_iso1.png","loc":[c[0]-70, c[1]-60, c[2]+50],"target":c,"persp_lens":50,"res":[1000,800]},
 {"out":o+"/br_iso2.png","loc":[c[0]+70, c[1]+60, c[2]+50],"target":c,"persp_lens":50,"res":[1000,800]},
 {"out":o+"/br_iso3_below.png","loc":[c[0]-50, c[1]+70, c[2]-60],"target":c,"persp_lens":50,"res":[1000,800]},
 {"out":o+"/br_iso4_below.png","loc":[c[0]+60, c[1]-70, c[2]-50],"target":c,"persp_lens":50,"res":[1000,800]},
 {"out":o+"/br_sideX.png","loc":[c[0]+100, c[1], c[2]],"rot_deg":[90,0,90],"ortho":45,"res":[900,900]},
]
json.dump({"objects":objs,"cams":cams}, open("r2.json","w"))
subprocess.run([r"D:\setup\blender\blender.exe","-b","--factory-startup","--python","bl_render.py","--","r2.json"], check=True)
