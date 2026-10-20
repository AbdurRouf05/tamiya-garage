import json, subprocess
from common import *
src = str(SRC)
objs = [
 {"kind":"stl","path":src+"/chassis-super-1.stl","color":[0.6,0.6,0.65]},
 {"kind":"stl","path":src+"/chassis-super-1-motor-bracket.stl","color":[0.9,0.25,0.2]},
 {"kind":"stl","path":src+"/chassis-super-1-gear-cover.stl","color":[0.2,0.4,0.95]},
 {"kind":"stl","path":src+"/chassis-super-1-rear-bumper.stl","color":[0.2,0.8,0.3]},
]
o = str(OUT)
tgt = [39, 95, 15]
cams = [
 {"out":o+"/iso_rear_left.png","loc":[-60, 170, 90],"target":tgt,"persp_lens":60,"res":[1400,1000]},
 {"out":o+"/iso_front_left.png","loc":[-60, 20, 90],"target":tgt,"persp_lens":60,"res":[1400,1000]},
 {"out":o+"/iso_rear_right.png","loc":[140, 170, 80],"target":tgt,"persp_lens":60,"res":[1400,1000]},
]
json.dump({"objects":objs,"cams":cams}, open("r1.json","w"))
subprocess.run([r"D:\setup\blender\blender.exe","-b","--factory-startup","--python","bl_render.py","--","r1.json"], check=True, capture_output=False)
