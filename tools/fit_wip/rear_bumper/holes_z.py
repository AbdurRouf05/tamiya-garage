import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from slicer import *
W = os.path.dirname(os.path.abspath(__file__))
ch = transformed("chassis-super-1"); rb = transformed("chassis-super-1-rear-bumper")
chr_ = ch[(ch[:, :, 1] > 85).any(1)]
for z in np.arange(5.5, 21.0, 0.5):
    s1 = section(chr_, "z", z); s2 = section(rb, "z", z)
    c1 = circles(s1, "z"); c2 = circles(s2, "z")
    print(f"Z={z:5.2f}  chassis: " + "; ".join(f"({a:.2f},{b:.2f}) r{r:.2f}" for a, b, r, e, n in c1))
    print(f"         bumper : " + "; ".join(f"({a:.2f},{b:.2f}) r{r:.2f}" for a, b, r, e, n in c2))
    if z in (6.0, 8.0, 10.0, 12.0, 14.0, 16.0, 18.0, 19.0, 20.0):
        draw([(s1, (90, 90, 90)), (s2, (230, 100, 0))], "z", z, ((5, 73), (88, 136)), 18, os.path.join(W, "renders", f"secZ_{z:04.1f}.png"), title="gray=chassis orange=rear-bumper(file pos)")
