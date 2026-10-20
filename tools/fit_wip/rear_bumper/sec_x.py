import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from slicer import *
W = os.path.dirname(os.path.abspath(__file__))
ch = transformed("chassis-super-1"); rb = transformed("chassis-super-1-rear-bumper")
chr_ = ch[(ch[:, :, 1] > 80).any(1)]
args = sys.argv[1:]
for xs in args:
    x = float(xs)
    s1 = section(chr_, "x", x); s2 = section(rb, "x", x)
    draw([(s1, (90, 90, 90)), (s2, (230, 100, 0))], "x", x, ((85, 137), (2, 23)), 22, os.path.join(W, "renders", f"secX_{x:05.2f}.png"), title="gray=chassis orange=rear-bumper(file pos)")
