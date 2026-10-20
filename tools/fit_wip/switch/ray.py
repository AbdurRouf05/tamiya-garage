import numpy as np, sys
from load import tris
def zray(t, x, y):
    a, b, c = t[:, 0].astype(float), t[:, 1].astype(float), t[:, 2].astype(float)
    m = (np.minimum(np.minimum(a[:,0],b[:,0]),c[:,0]) <= x) & (np.maximum(np.maximum(a[:,0],b[:,0]),c[:,0]) >= x) & \
        (np.minimum(np.minimum(a[:,1],b[:,1]),c[:,1]) <= y) & (np.maximum(np.maximum(a[:,1],b[:,1]),c[:,1]) >= y)
    a, b, c = a[m], b[m], c[m]
    d = (b[:,0]-a[:,0])*(c[:,1]-a[:,1]) - (b[:,1]-a[:,1])*(c[:,0]-a[:,0])
    wa = ((b[:,0]-x)*(c[:,1]-y) - (b[:,1]-y)*(c[:,0]-x)) / d
    wb = ((c[:,0]-x)*(a[:,1]-y) - (c[:,1]-y)*(a[:,0]-x)) / d
    wc = 1 - wa - wb
    ins = (wa >= 0) & (wb >= 0) & (wc >= 0)
    z = (wa*a[:,2] + wb*b[:,2] + wc*c[:,2])[ins]
    s = np.sign(d[ins])
    o = np.argsort(z)
    return [(round(float(zz), 3), int(ss)) for zz, ss in zip(z[o], s[o])]
t = tris(sys.argv[1])
for xy in sys.argv[2:]:
    x, y = map(float, xy.split(","))
    print(sys.argv[1], (x, y), zray(t, x + 0.0013, y + 0.0017))
