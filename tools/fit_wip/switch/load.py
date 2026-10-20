import struct, sys
from pathlib import Path
import numpy as np
SRC = Path(r"D:\coding\tamiya-garage\models\source\super1-printables")
CACHE = Path(__file__).resolve().parent / "cache"
def tris(name):
    c = CACHE / (name + ".npy")
    if c.exists():
        return np.load(c)
    data = (SRC / name).read_bytes()
    n = struct.unpack("<I", data[80:84])[0]
    t = np.frombuffer(data[84:84 + n * 50], dtype=np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")]))
    v = np.ascontiguousarray(t["v"]).astype(np.float32)
    np.save(c, v)
    return v
if __name__ == "__main__":
    for nm in sys.argv[1:]:
        v = tris(nm)
        p = v.reshape(-1,3)
        print(nm, len(v), p.min(0).round(3), p.max(0).round(3), ((p.min(0)+p.max(0))/2).round(3))
