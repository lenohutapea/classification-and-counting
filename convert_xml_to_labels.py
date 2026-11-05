"""
Konversi anotasi XML dataset (session0_right) ke format label repo 3d_bbox_highway.
Rujukan format: CarlaDataset.__getitem__ di centernet-3d-bbox.ipynb (CSV "x,y,w,h,l",
satu file per gambar, nama label = nama gambar tanpa ekstensi 3 huruf; gambar di-resize
ke 1280x720 saat dimuat, jadi x,y diskalakan 2/3).
Titik (x,y) = perpotongan diagonal 4 titik alas vertex2d (pusat alas setelah proyeksi).
y diukur dari ATAS gambar (terbukti dari label Carla dan get_position_ground).
w,h,l = veh_size ke-2, ke-3, ke-1 (terbukti dari selisih vertex3d).
"""

import os, re, sys, csv
import xml.etree.ElementTree as ET
from collections import Counter

BASE = os.path.expanduser(
    sys.argv[1] if len(sys.argv) > 1 else "~/projects/data_session0_right"
)
ANN = os.path.join(BASE, "annotations")
IMG = os.path.join(BASE, "images")
OUT = os.path.join(BASE, "converted")
SCALE = 2.0 / 3.0
NUM = r"-?\d+(?:\.\d+)?"


def cross(a, b):
    return a[0] * b[1] - a[1] * b[0]


def base_center(pts):
    p0, p1, p2, p3 = pts[:4]
    d1 = (p2[0] - p0[0], p2[1] - p0[1])
    d2 = (p3[0] - p1[0], p3[1] - p1[1])
    den = cross(d1, d2)
    if abs(den) < 1e-9:
        return None
    t = cross((p1[0] - p0[0], p1[1] - p0[1]), d2) / den
    return p0[0] + t * d1[0], p0[1] + t * d1[1]


os.makedirs(os.path.join(OUT, "images"), exist_ok=True)
os.makedirs(os.path.join(OUT, "labels"), exist_ok=True)

files = sorted(
    f for f in os.listdir(ANN) if f.startswith("session0_right_") and f.endswith(".xml")
)
types, skipped, no_img = Counter(), Counter(), 0
ys, xs, n_obj, n_y150, n_out = [], [], 0, 0, 0

with open(os.path.join(OUT, "mapping.csv"), "w", newline="") as fm, open(
    os.path.join(OUT, "objects.csv"), "w", newline=""
) as fo:
    wm, wo = csv.writer(fm), csv.writer(fo)
    wm.writerow(["image", "original"])
    wo.writerow(["image", "row", "type", "perspective", "x", "y", "w", "h", "l"])
    for i, fx in enumerate(files, start=1):
        name = f"image_{i:04d}"
        orig = fx[:-4]
        src_img = os.path.join(IMG, orig + ".jpg")
        if not os.path.exists(src_img):
            no_img += 1
        link = os.path.join(OUT, "images", name + ".jpg")
        if os.path.lexists(link):
            os.remove(link)
        os.symlink(os.path.abspath(src_img), link)
        wm.writerow([name, orig])

        rows = []
        for ob in ET.parse(os.path.join(ANN, fx)).getroot().findall("object"):
            pts = [
                (float(a), float(b))
                for a, b in re.findall(
                    rf"\(\s*({NUM})\s*,\s*({NUM})\s*\)", ob.findtext("vertex2d", "")
                )
            ]
            sz = [float(v) for v in ob.findtext("veh_size", "").split()]
            if len(pts) < 4 or len(sz) != 3:
                skipped["data tidak lengkap"] += 1
                continue
            c = base_center(pts)
            if c is None:
                skipped["diagonal sejajar"] += 1
                continue
            x, y = c[0] * SCALE, c[1] * SCALE
            L, W, H = sz
            if not (0 <= x < 1280 and 0 <= y < 720):
                n_out += 1
            if y < 150:
                n_y150 += 1
            rows.append((x, y, W, H, L))
            typ = ob.findtext("type", "?").strip()
            types[typ] += 1
            wo.writerow(
                [
                    name,
                    len(rows) - 1,
                    typ,
                    ob.findtext("perspective", "").strip(),
                    f"{x:.3f}",
                    f"{y:.3f}",
                    W,
                    H,
                    L,
                ]
            )
            xs.append(x)
            ys.append(y)
            n_obj += 1
        with open(os.path.join(OUT, "labels", name + ".txt"), "w") as fl:
            fl.write("x,y,w,h,l\n")
            for r in rows:
                fl.write(",".join(repr(v) for v in r) + "\n")

print("frame:", len(files), "| objek:", n_obj, "| gambar tidak ditemukan:", no_img)
print("kelas:", dict(types))
print("dilewati:", dict(skipped))
if ys:
    print(
        f"x (720p): min {min(xs):.1f} maks {max(xs):.1f} | y (720p): min {min(ys):.1f} maks {max(ys):.1f}"
    )
print(
    "objek di luar gambar 1280x720:",
    n_out,
    "| objek dengan y<150 (tanpa target ukuran di notebook):",
    n_y150,
)
print("keluaran:", OUT)
