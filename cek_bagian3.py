import pickle
from cek_bagian1 import *

files, objs_by_frame = pickle.load(open(os.path.join(BASE, "objs.pkl"), "rb"))
edges = [
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 0),
    (4, 5),
    (5, 6),
    (6, 7),
    (7, 4),
    (0, 4),
    (1, 5),
    (2, 6),
    (3, 7),
]
n = len(files)
out = os.path.join(BASE, "check")
os.makedirs(out, exist_ok=True)
for k in [1, n // 6, 2 * n // 6, 3 * n // 6, 4 * n // 6, 5 * n // 6]:
    k = max(k, 1)
    while k <= n and k not in objs_by_frame:
        k += 1
    if k > n:
        continue
    path = os.path.join(BASE, "converted", "images", "image_%04d.jpg" % k)
    img = cv2.imread(path)
    if img is None:
        print("gagal baca:", path)
        continue
    img = cv2.resize(img, (1280, 720))
    for x, y, W, H, L, p2 in objs_by_frame[k]:
        pts = [(int(a * S), int(b * S)) for a, b in p2]
        for a, b in edges:
            cv2.line(img, pts[a], pts[b], (0, 255, 0), 1)
        P = get_position_ground(x, y, K, T, 720)
        img = Box(P[0], P[2], W, H, L).project(img, T, K)
        cv2.circle(img, (int(x), int(y)), 3, (0, 255, 255), -1)
    name = os.path.join(out, "image_%04d.png" % k)
    cv2.imwrite(name, img)
    print("tersimpan:", name, "(%d objek)" % len(objs_by_frame[k]))
