# BRONE Dynamic Engine

Mesin wajah robot BRONE yang dapat berganti ekspresi secara **dinamis** (transisi halus antar emosi), dengan opsi mode **statis** (berganti instan), artikulasi bicara (talking), dan kedip mata natural.

Dibangun untuk resolusi **1024×600** dengan arsitektur terpisah: **data / logika transisi / rendering / loop**.

## Cakupan Modul

```
dynamic_engine/
├── __init__.py        # Penanda paket
├── state.py           # Model data ekspresi (FaceState + EMOTION_BANK)
├── interpolator.py    # Transisi halus, kedip FSM, artikulasi bicara
├── renderer.py        # Penggambar semua visual ke layar 1024×600
└── main.py            # Entry point: init pygame, game loop, kontrol keyboard
```

| File | Peran |
|---|---|
| `state.py` | Mendefinisikan `FaceState` (kumpulan DoF wajah: ukuran/rotasi mata, pupil/gaze, kedip, warna & air mata, ukuran/gaya mulut, bukaan bicara) dan `EMOTION_BANK` berisi 5 preset: `NEUTRAL`, `HAPPY`, `SHOCK`, `CRY`, `LOAD`. |
| `interpolator.py` | `FaceInterpolator` menggeser state aktif mendekati state target secara halus (exponential smoothing, independen FPS), menghidupkan FSM kedip natural (`idle → closing → opening`), serta osilasi buka-tutup mulut saat talking aktif. Mendukung 2 mode: `DYNAMIC` (halus) dan `STATIC` (instan). |
| `renderer.py` | `FaceRenderer` menggambar mata gradasi + kilau glint, kabel robot, aliran air mata, kelopak kedip, 4 gaya mulut (`neutral`, `oval`, `smile`, `sad`) + lidah, dan HUD. Menggunakan surface pre-allocated untuk mencegah lag akibat alokasi berulang (antisipasi Jetson Nano). |
| `main.py` | Membuka jendela pygame, menjalankan loop 60 FPS berbasis delta-time, memetakan input keyboard ke aksi, lalu merangkai `interpolator.update(dt)` → `FaceRenderer.draw(...)` → `pygame.display.flip()`. |

## Alur Data

```
Input keyboard (main.py)
        │  set_emotion(), toggle_mode(), toggle_talking()
        ▼
FaceInterpolator ── target ──► EMOTION_BANK (state.py)
   update(dt) menggeser current ─► target (DYNAMIC) / snap (STATIC)
        │
        ▼  FaceState (current)
FaceRenderer.draw(screen, state, mode, emotion, is_talking, fps, dt)
        │
        ▼
Jendela 1024×600
```

Ringkasnya:

- **`state.py`** = library koordinat ekspresi → tiap emosi hanyalah kumpulan angka.
- **`interpolator.py`** = transisi pergantian antar kumpulan angka tersebut (plus kedip & bicara).
- **`renderer.py`** = menampilkan angka tersebut menjadi gambar.
- **`main.py`** = loop yang menyambungkan dan menggerakkan semuanya.

## Cara Menjalankan

### 1. Langsung dari folder `dynamic_engine`

```bash
# Wajib Python yang memiliki pygame (lokal .venv atau Python 3.12)
py -3.12 -m dynamic_engine.main
```

### 2. Via launcher paket `run_dynamic.py` (direkomendasikan)

```bash
py -3.12 run_dynamic.py
```

Launcher ini otomatis memastikan interpreter yang dipakai memiliki pygame, lalu menjalankan `dynamic_engine.main`.

### 3. Via menu launcher utama `preview.py`

Buka `preview.py` lalu pilih opsi **`D`** (RUN DYNAMIC ENGINE).

## Kontrol Keyboard

| Tombol | Fungsi |
|---|---|
| `M` | Toggle MODE: `DYNAMIC` (transisi halus) ↔ `STATIC` (berganti instan) |
| `1` | Ekspresi HAPPY (senang) |
| `2` | Ekspresi SHOCK (terkejut) |
| `3` | Ekspresi CRY (menangis) |
| `4` | Ekspresi LOAD (berpikir/loading) |
| `0` | Ekspresi NEUTRAL |
| `T` | Toggle talking: artikulasi buka-tutup mulut |
| `B` | Trigger kedip manual |
| `D` | Tampilkan / sembunyikan HUD |
| `ESC` | Keluar |

## Menambah Ekspresi Baru

Tambahkan preset baru ke `EMOTION_BANK` di `state.py`, contoh:

```python
"SLEEPY": FaceState(
    eye_scale_y=0.6,
    eyelid_progress=0.6,
    pupil_ox=0.0,
    pupil_oy=-5.0,
    mouth_w=140.0,
    mouth_h=10.0,
    mouth_style="neutral",
)
```

Lalu panggil dari `main.py` (misal tombol `5`): `interpolator.set_emotion("SLEEPY")`.

## Catatan

- Mesin ini merupakan paket dari repositori BRONE v3; struktur antar modul menggunakan relative import (`from .state import ...`) sehingga harus dijalankan sebagai paket (`-m`) atau melalui launcher agar `sys.path` terisi benar.
- Jika menjalankan `main.py` secara langsung tetapi interpreter tidak memiliki pygame, gunakan `.venv` atau Python 3.12 (lihat `run_dynamic.py`).