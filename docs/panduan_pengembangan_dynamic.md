#  Panduan Arsitektur & Pengembangan BRONE Dynamic Engine (v3)

Folder `dynamic_engine/` adalah implementasi sistem ekspresi robot berbasis prinsip jurnal **Xpress** (*Antony et al., Johns Hopkins University*).

---

##  Arsitektur Sistem

Sistem ini memisahkan antara **State/Parameter**, **Motion Interpolator**, dan **Renderer**:

```
+---------------------------------------------------------------------------------+
|                                 INPUT TRIGGER                                   |
|   Keyboard ([1-4], [0], [T], [M]) / Kelak: MQTT Subscriber / MediaPipe Socket   |
+---------------------------------------------------------------------------------+
                                        │
                                        ▼
+---------------------------------------------------------------------------------+
|                    dynamic_engine/interpolator.py                               |
|   - Menghitung pergeseran nilai parameter secara halus (lerp)                   |
|   - Mode Dinamis: Transisi ~300ms berbasis exponential smoothing (dt)           |
|   - Mode Statis: Transisi 0ms (snap langsung ke target)                         |
|   - Modulasi bukaan mulut bicara (Talking State oscilator)                      |
|   - Finite State Machine kedip mata (closing -> opening -> idle)                |
+---------------------------------------------------------------------------------+
                                        │
                                        ▼
+---------------------------------------------------------------------------------+
|                    dynamic_engine/renderer.py                                   |
|   - Merender kanvas 1024x600 setiap frame                                       |
|   - ZERO alokasi Surface di main loop (pre-allocated & memory safe)             |
|   - Menampilkan HUD status interaktif                                           |
+---------------------------------------------------------------------------------+
```

---

##  Kontrol Keyboard di Dynamic Engine

| Tombol | Fungsi | Keterangan |
|---|---|---|
| **[M]** | **Toggle Mode** | Beralih antara **MODE DINAMIS** (transisi halus) dan **MODE STATIS** (snap langsung). |
| **[1]** | Emosi **HAPPY** | Mulut melengkung senyum, mata normal. |
| **[2]** | Emosi **SHOCK** | Mata membesar (skala 1.15x), mulut oval lonjong terbuka. |
| **[3]** | Emosi **CRY** | Warna mata ungu tua, gelombang air mata aktif, aliran air mata jatuh mengalir. |
| **[4]** | Emosi **LOAD** | Mata kanan miring 10°, pupil melirik ke kiri (`pupil_ox = -25`). |
| **[0]** atau **[I]** | Emosi **NEUTRAL** | Wajah posisi diam/netral. |
| **[T]** | **Toggle Talking** | Mengaktifkan/mematikan artikulasi bukaan mulut bicara (*viseme flutter*). Bisa digabung dengan emosi apa pun! |
| **[B]** | **Blink Manual** | Memicu kedipan mata manual di luar kedipan otomatis. |
| **[D]** | **Toggle HUD** | Menampilkan atau menyembunyikan panel bar informasi di atas layar. |
| **[ESC]** | **Keluar** | Menutup jendela Pygame dengan aman. |

---

##  Cara Menambah Emosi Baru

Untuk menambah emosi baru (misal: `SAD`, `SHY`, atau `ANGRY`):
1. Buka `dynamic_engine/state.py`.
2. Tambahkan preset baru di dalam `EMOTION_BANK`:
```python
"ANGRY": FaceState(
    eye_scale_x=1.0,
    eye_scale_y=0.85,
    eye_rot_l=-12.0,       # Mata kiri miring ke dalam
    eye_rot_r=12.0,        # Mata kanan miring ke dalam
    eye_top_color=(180, 40, 40), # Warna mata kemerahan
    mouth_w=180.0,
    mouth_h=40.0,
    mouth_curve=-0.6,
    mouth_style="sad"
)
```
3. Daftarkan tombol pemicunya di `dynamic_engine/main.py`.
