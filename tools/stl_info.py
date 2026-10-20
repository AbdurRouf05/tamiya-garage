"""Tampilkan jumlah segitiga tiap file STL. Pemakaian: python tools/stl_info.py <file.stl>..."""
import os
import struct
import sys

for f in sys.argv[1:]:
    size = os.path.getsize(f)
    with open(f, "rb") as fh:
        head = fh.read(84)
    n = struct.unpack("<I", head[80:84])[0]
    kind = "biner" if size == 84 + n * 50 else "ASCII"
    if kind == "ASCII":
        with open(f, "rb") as fh:
            n = sum(1 for line in fh if line.lstrip().startswith(b"facet"))
    print(f"{os.path.basename(f):45s} {n:>11,} segitiga  {kind:6s} {size / 1e6:8.1f} MB")
