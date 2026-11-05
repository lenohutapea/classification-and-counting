import os, re, sys
import xml.etree.ElementTree as ET
import numpy as np, cv2
sys.dont_write_bytecode = True
REPO = os.path.expanduser("~/projects/3d_bbox_highway")
sys.path.insert(0, REPO)
from utils import Box, get_position_ground, project

BASE = os.path.expanduser("~/projects/data_session0_right")
S = 2.0 / 3.0
NUM = r"-?\d+(?:\.\d+)?(?:e[+-]?\d+)?"

cal = ET.parse(os.path.join(BASE, "calib", "session0_right_calibParams.xml")).getroot()
f_full = float(cal.findtext("f"))
h_m = float(cal.findtext("h")) / 1000.0
v = [float(t) for t in cal.findtext("vanishPoints").split()]
Kf = np.array([[f_full, 0, 960.], [0, f_full, 540.], [0, 0, 1.]])

def direction(vp):
    d = np.linalg.inv(Kf) @ np.array([vp[0], vp[1], 1.0])
    return d / np.linalg.norm(d)

d1, d2 = direction(v[0:2]), direction(v[2:4])
if d1[2] < 0: d1 = -d1
if d2[0] < 0: d2 = -d2
X = d2 - (d2 @ d1) * d1
X /= np.linalg.norm(X)
Z = np.cross(X, d1)
if Z[1] > 0: Z = -Z
flip = np.array([1, -1, 1])
R_wc = np.stack([X * flip, Z * flip, d1 * flip], axis=0)
T = np.identity(4)
T[:3, :3] = R_wc
T[:3, 3] = [0, h_m, 0]
f = f_full * S
K = np.array([[f, 0, 640.], [0, f, 360.], [0, 0, 1.]])
print("f(720p)=%.2f  h=%.3f m  det(R)=%.6f" % (f, h_m, np.linalg.det(R_wc)))

def cross(a, b):
    return a[0] * b[1] - a[1] * b[0]

def base_center(p):
    d1_ = (p[2][0] - p[0][0], p[2][1] - p[0][1])
    d2_ = (p[3][0] - p[1][0], p[3][1] - p[1][1])
    t = cross((p[1][0] - p[0][0], p[1][1] - p[0][1]), d2_) / cross(d1_, d2_)
    return p[0][0] + t * d1_[0], p[0][1] + t * d1_[1]
