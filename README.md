# classification-and-counting

Konversi dan validasi label 3D bounding box dataset **session0_right** untuk melatih CenterNet pada [antoinekeller/3d_bbox_highway](https://github.com/antoinekeller/3d_bbox_highway), sebagai dasar klasifikasi dan penghitungan kendaraan.

## Gambaran 

Repo ini berisi skrip kerja yang:

1. Membaca anotasi XML dan kalibrasi kamera (`calibParams.xml`: fokus `f`, tinggi kamera `h`, dan vanishing point).
2. Membentuk model kamera (matriks intrinsik `K` dan ekstrinsik `T`) dari kalibrasi tersebut.
3. Mengonversi anotasi ke label `.txt` format 3d_bbox_highway: `x, y, w, h, l`.
4. Memeriksa hasilnya: konsistensi `.txt` dengan XML, IoU kotak model kamera terhadap kotak dataset, dan overlay visual.

## Catatan teknis

| Hal | Nilai |
|---|---|
| Resolusi asli | 1920x1080 |
| Resolusi latih | 1280x720 (skala 2/3) |
| Fokus (720p) | `f_full * 2/3` |
| Titik utama (720p) | (640, 360) |
| Tinggi kamera | `h` dari `calibParams.xml` (mm ke m) |

Karena gambar diperkecil, fokus dan titik utama diskalakan dengan faktor yang sama. Nilai 720 dipakai untuk membalik sumbu y saat proyeksi.

## Struktur

```
.
├── cek_bagian1.py   # model kamera (K, T) dan fungsi bantu
├── cek_bagian4.py   # IoU kotak model kamera vs kotak dataset
├── p5.py            # overlay label .txt ke gambar
├── .gitignore
└── README.md
```

Data tidak disertakan di repo (`images/`, `converted/`, `annotations/`, `calib/`, `*.pkl`).

## Persiapan

Prasyarat: Python 3, dan repo acuan `3d_bbox_highway` di `~/projects/3d_bbox_highway` (skrip mengimpor `utils.py` darinya).

```bash
source ~/projects/venv_3dbbox/bin/activate
pip install numpy opencv-python pandas
```

Susunan folder data yang diharapkan di `~/projects/data_session0_right`:

```
calib/        # session0_right_calibParams.xml
converted/
├── images/   # image_NNNN.jpg
└── labels/   # image_NNNN.txt
objs.pkl      # hasil baca XML
```

## Penggunaan

Periksa label dan gambar overlay:

```bash
cd ~/projects/data_session0_right
python p5.py              # frame 1, 1591, 2651
python p5.py 100 500 2000 # frame pilihan
```

Hasil disimpan di `check_label/`:

- Kotak magenta: kotak 3D dari model kamera.
- Titik kuning: titik (x, y) dari label.

Skrip juga mencetak jumlah frame yang objeknya tidak sama dengan XML dan selisih terbesar nilai `x, y, w, h, l`. Pada konversi yang benar, keduanya mendekati nol.

## Pelatihan

Pelatihan memakai notebook `centernet-3d-bbox.ipynb` dari repo acuan. Path data pada notebook perlu diarahkan ke folder data ini.

## Status

- [x] Konversi session0_right (3.182 frame, 8.664 objek)
- [x] Pemeriksaan model kamera dan overlay label
- [ ] Pelatihan CenterNet pada data hasil konversi
- [ ] Klasifikasi dan penghitungan kendaraan

## Referensi

- [antoinekeller/3d_bbox_highway](https://github.com/antoinekeller/3d_bbox_highway): kode dan format label acuan
- CenterNet: Zhou et al., *Objects as Points*, 2019