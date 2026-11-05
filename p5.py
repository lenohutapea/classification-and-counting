import glob
import pickle
import pandas as pd
from cek_bagian1 import *

files, objs = pickle.load(open(os.path.join(BASE, "objs.pkl"), "rb"))
lab_dir = os.path.join(BASE, "converted", "labels")
img_dir = os.path.join(BASE, "converted", "images")
out = os.path.join(BASE, "check_label")
os.makedirs(out, exist_ok=True)


def baca(k):
    return pd.read_csv(os.path.join(lab_dir, "image_%04d.txt" % k)).to_numpy()


selisih, beda_jumlah = 0.0, []
for k in range(1, len(files) + 1):
    rows = baca(k)
    ref = objs.get(k, [])
    if len(rows) != len(ref):
        beda_jumlah.append(k)
        continue
    for r, o in zip(rows, ref):
        selisih = max(selisih, max(abs(r[i] - o[i]) for i in range(5)))
print("frame jumlah objek txt != XML:", beda_jumlah[:20], len(beda_jumlah))
print("selisih terbesar x,y,w,h,l (txt vs XML): %.2e" % selisih)

ks = [int(a) for a in sys.argv[1:]] or [1, 1591, 2651]
for k in ks:
    cand = glob.glob(os.path.join(img_dir, "image_%04d.*" % k))
    img = cv2.imread(cand[0]) if cand else None
    if img is None:
        print("gagal baca gambar", k)
        continue
    img = cv2.resize(img, (1280, 720))
    for x, y, w, h, l in baca(k):
        P = get_position_ground(x, y, K, T, img.shape[0])
        img = Box(P[0], P[2], w, h, l).project(img, T, K)
        cv2.circle(img, (int(x), int(y)), 3, (0, 255, 255), -1)
    nama = os.path.join(out, "image_%04d.png" % k)
    cv2.imwrite(nama, img)
    print("tersimpan:", nama)
