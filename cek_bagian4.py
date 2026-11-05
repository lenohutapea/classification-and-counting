import pickle
from cek_bagian1 import *

files, objs = pickle.load(open(os.path.join(BASE, "objs.pkl"), "rb"))
Tcw = np.linalg.inv(T)

def bbox(pts):
    a = np.array(pts, dtype=float)
    return a[:, 0].min(), a[:, 1].min(), a[:, 0].max(), a[:, 1].max()

def iou(a, b):
    w = min(a[2], b[2]) - max(a[0], b[0])
    h = min(a[3], b[3]) - max(a[1], b[1])
    if w <= 0 or h <= 0:
        return 0.0
    inter = w * h
    ua = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / ua

def corners(P, W, H, L):
    pts = []
    for sx in (-1, 1):
        for sy in (0, H):
            for sz in (-1, 1):
                q = project(np.array([P[0] + sx * W / 2, sy, P[2] + sz * L / 2]), Tcw, K)
                pts.append((q[0], 720 - q[1]))
    return pts

ious, rw, rh, dy, ys = [], [], [], [], []
for k, lst in objs.items():
    for (x, y, W, H, L, p2) in lst:
        P = get_position_ground(x, y, K, T, 720)
        m = bbox(corners(P, W, H, L))
        g = bbox([(a * S, b * S) for a, b in p2])
        ious.append(iou(m, g))
        rw.append((m[2] - m[0]) / (g[2] - g[0]))
        rh.append((m[3] - m[1]) / (g[3] - g[1]))
        dy.append(((m[1] + m[3]) - (g[1] + g[3])) / 2)
        ys.append(720 - y)
ious, rw, rh, dy, ys = map(np.array, (ious, rw, rh, dy, ys))

def ringkas(nama, a, fmt):
    print(("%-34s median " + fmt + " | P5 " + fmt + " | P95 " + fmt) %
          (nama, np.median(a), np.percentile(a, 5), np.percentile(a, 95)))

print("objek: %d" % len(ious))
ringkas("IoU 2D magenta vs hijau", ious, "%.3f")
ringkas("rasio lebar bbox (magenta/hijau)", rw, "%.3f")
ringkas("rasio tinggi bbox (magenta/hijau)", rh, "%.3f")
ringkas("selisih pusat vertikal (px,720p)", dy, "%.1f")
for nama, m in [("y<150 dari bawah", ys < 150), ("y>=150 dari bawah", ys >= 150)]:
    print("IoU median, %-18s n=%4d: %.3f" % (nama, m.sum(), np.median(ious[m])))
