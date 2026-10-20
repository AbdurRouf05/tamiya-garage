"""Exact ray-interval measurements of chassis bay features and the retainer (STL mm)."""
import numpy as np
import stlcore
T = stlcore.tris("chassis-super-1.stl")
# restrict to region for speed
v = T.reshape(-1, 9)
m = (T[:, :, 1].max(1) > 30) & (T[:, :, 1].min(1) < 98)
T = T[m]
R = stlcore.tris("chassis-super-1-battery-retainer.stl")
ci = stlcore.column_intervals
print("== chassis: X-rays (intervals along X) ==")
for (y, z) in [(68.2, 15.5), (68.2, 14.0), (68.2, 16.5), (68.2, 17.5), (54.0, 14.0), (54.0, 9.5), (45.0, 9.5), (60.0, 9.5), (45.0, 14.2), (68.2, 12.0), (54.0, 7.5), (45.0, 7.5), (45, 6.0), (60, 6.0)]:
    print(f"Y={y} Z={z}:", ci(T, 0, y, z))
print("== chassis: Y-rays (intervals along Y) ==")
for (x, z) in [(22.0, 16.0), (22.8, 17.0), (56.0, 16.0), (55.2, 17.0), (22.7, 14.5), (32.47, 7.5), (32.47, 9.0), (32.47, 12.0), (47.72, 7.5), (47.72, 9.0), (47.72, 12.0), (26.0, 10.0), (26.0, 12.0), (53.0, 10.0), (36.0, 8.0), (44.0, 8.0), (28.0, 9.0), (51.0, 9.0)]:
    print(f"X={x} Z={z}:", ci(T, 1, x, z))
print("== chassis: Z-rays ==")
for (x, y) in [(32.47, 45), (32.47, 60), (32.47, 85), (47.72, 45), (47.72, 60), (47.72, 85), (39.0, 45), (40.1, 45), (32.47, 54.0), (47.72, 54.0), (32.47, 70), (47.72, 70), (22.7, 68.2), (21.5, 68.2), (55.3, 68.2), (56.5, 68.2), (22.7, 54), (55.4, 54)]:
    print(f"X={x} Y={y}:", ci(T, 2, x, y))
print("== retainer ==")
for (y, z) in [(54.1, 14.4), (54.1, 19.0), (51.0, 15.5), (57.4, 15.5), (51.0, 17.5)]:
    print(f"ret X-ray Y={y} Z={z}:", ci(R, 0, y, z))
for (x, z) in [(20.9, 14.4), (20.9, 15.5), (20.9, 15.2), (55.2, 15.5), (55.2, 14.4), (38.0, 19.0), (25, 19.0)]:
    print(f"ret Y-ray X={x} Z={z}:", ci(R, 1, x, z))
for (x, y) in [(20.9, 54.1), (20.9, 51.0), (38.0, 54.1), (38.0, 51.0), (30, 52), (55.2, 54.1), (22.5, 51)]:
    print(f"ret Z-ray X={x} Y={y}:", ci(R, 2, x, y))
