import sys, numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from load import tris
for nm in sys.argv[1:]:
    v = tris(nm)
    p = v.reshape(-1, 3).round(4)
    u, inv = np.unique(p, axis=0, return_inverse=True)
    inv = inv.reshape(-1, 3)
    a = np.concatenate([inv[:, 0], inv[:, 1]]); b = np.concatenate([inv[:, 1], inv[:, 2]])
    g = coo_matrix((np.ones(len(a)), (a, b)), shape=(len(u), len(u)))
    n, lab = connected_components(g, directed=False)
    tl = lab[inv[:, 0]]
    print(nm, "components:", n)
    # signed volume per component
    for c in range(n):
        t = v[tl == c]
        vol = np.einsum('ij,ij->i', t[:, 0], np.cross(t[:, 1], t[:, 2])).sum() / 6
        pp = t.reshape(-1, 3)
        print(f"  comp {c}: tris {len(t)} vol {vol:.2f} mm3 bbox min {pp.min(0).round(2)} max {pp.max(0).round(2)}")
    np.save(f"cache/{nm}.lab.npy", tl)
