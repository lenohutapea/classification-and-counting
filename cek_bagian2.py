import pickle
from cek_bagian1 import *

ann = os.path.join(BASE, "annotations")
files = sorted(
    n for n in os.listdir(ann) if n.startswith("session0_right_") and n.endswith(".xml")
)
Tcw = np.linalg.inv(T)
pat2 = rf"\(\s*({NUM})\s*,\s*({NUM})\s*\)"
pat3 = rf"\(\s*({NUM})\s*,\s*({NUM})\s*,\s*({NUM})\s*\)"
err_self, ratio, lat, true_z = [], [], [], []
objs_by_frame = {}
n_skip = 0
for i, fx in enumerate(files, start=1):
    root = ET.parse(os.path.join(ann, fx)).getroot()
    for ob in root.findall("object"):
        p2 = [
            (float(a), float(b)) for a, b in re.findall(pat2, ob.findtext("vertex2d"))
        ]
        p3 = [
            (float(a), float(b))
            for a, b, _ in re.findall(pat3, ob.findtext("vertex3d"))
        ]
        if len(p2) != 8 or len(p3) != 8:
            n_skip += 1
            continue
        L, W, H = [float(t) for t in ob.findtext("veh_size").split()]
        cx, cy = base_center(p2)
        x, y = cx * S, cy * S
        P = get_position_ground(x, y, K, T, 720)
        pix = project(P, Tcw, K)
        err_self.append(np.hypot(pix[0] - x, (720 - pix[1]) - y))
        tx = np.mean([q[0] for q in p3[:4]]) / 1000
        tz = np.mean([q[1] for q in p3[:4]]) / 1000
        ratio.append(P[2] / tz)
        lat.append(abs(P[0] - tx))
        true_z.append(tz)
        objs_by_frame.setdefault(i, []).append((x, y, W, H, L, p2))

ratio, lat, true_z = map(np.array, (ratio, lat, true_z))
print("frame: %d | objek dipakai: %d | dilewati: %d" % (len(files), len(ratio), n_skip))
print("[1] galat konsistensi (px): maks %.6f" % max(err_self))
print(
    "[2] kedalaman model/vertex3d: median %.3f | P5 %.3f | P95 %.3f"
    % (np.median(ratio), np.percentile(ratio, 5), np.percentile(ratio, 95))
)
print(
    "    galat lateral |dx| (m): median %.2f | P95 %.2f"
    % (np.median(lat), np.percentile(lat, 95))
)
for lo, hi in [(0, 60), (60, 80), (80, 100), (100, 1e9)]:
    m = (true_z >= lo) & (true_z < hi)
    if m.any():
        print(
            "    jarak %3d-%s m: n=%4d  rasio median %.3f"
            % (lo, "inf" if hi > 1e8 else str(hi), m.sum(), np.median(ratio[m]))
        )
pickle.dump((files, objs_by_frame), open(os.path.join(BASE, "objs.pkl"), "wb"))
print("tersimpan: objs.pkl")
