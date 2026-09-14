#  Dokumen Analisis Flaw, Keterbatasan Kode, & Blueprint Pengembangan BRONE Expression v2

> Dokumen ini disusun sebagai panduan audit menyeluruh terhadap kode pada repositori `brone-expression-v2` serta penyelarasan dengan paradigma sistem ekspresi dinamis yang diadaptasi dari jurnal riset **Xpress** (*Antony et al., Johns Hopkins University*).

---

##  Daftar Isi
1. [Executive Summary: Masalah Utama Sistem Saat Ini](#1-executive-summary-masalah-utama-sistem-saat-ini)
2. [Audit Kode & Flaw Kritis per File](#2-audit-kode--flaw-kritis-per-file)
   - [A. rcry.py (Ekspresi Menangis)](#a-rcrypy)
   - [B. rshock.py (Ekspresi Terkejut)](#b-rshockpy)
   - [C. rhappy.py (Ekspresi Senang)](#c-rhappypy)
   - [D. rload.py (Ekspresi Loading / Berpikir)](#d-rloadpy)
   - [E. File 0-Byte / Incomplete Stubs](#e-file-0-byte--stub-kosong)
   - [F. preview.py (Launcher)](#f-previewpy)
3. [Flaw Arsitektural Menyeluruh (Systemic Architectural Flaws)](#3-flaw-arsitektural-menyeluruh)
4. [Korelasi dengan Jurnal Xpress: Mengapa Wajah Belum Bisa Dinamis?](#4-korelasi-dengan-jurnal-xpress)
5. [Roadmap & Blueprint Solusi untuk Pengembangan Kedepan](#5-roadmap--blueprint-solusi-pengembangan)
6. [Rangkuman Lengkap Seluruh Flaw Kode (Daftar Poin / Checklist Ringkas)](#6-rangkuman-lengkap-seluruh-flaw-kode-daftar-poin--checklist-ringkas)

---

## 1. Executive Summary: Masalah Utama Sistem Saat Ini

Saat ini repositori masih berupa **skrip visual statis yang terisolasi**, bukan sebuah **sistem runtime ekspresi robot terpadu**:

| Aspek | Kondisi Saat Ini | Dampak |
|---|---|---|
| **Pola Eksekusi** | Tiap ekspresi adalah skrip Python independen dengan `while True` loop & `pygame.init()` sendiri. | Tidak bisa berganti ekspresi secara instan/halus (*seamless*). Mengganti ekspresi mengharuskan mematikan proses dan membuka proses baru (*window flicker*, lag). |
| **Transisi Wajah** | Statis, tidak ada fungsi interpolasi (*lerp*) atau kurva *easing*. | Ekspresi tidak memiliki fase transisi (misal: Netral $\to$ Senang secara halus). |
| **Manajemen Memori** | Alokasi `pygame.Surface` baru terjadi setiap frame (60 kali/detik) di dalam loop utama. | Tekanan besar pada Garbage Collector Python; memicu *micro-stuttering* pada hardware terbatas seperti Jetson Nano. |
| **Kelengkapan Fitur** | 50% file ekspresi (`rhappier`, `rsad`, `rshy`, `rtalkingState`) adalah stub 0-byte. | Fitur bicara (*lip-sync* / artikulasi mulut), sedih, malu, dan senang gembira belum diimplementasi di Python. |
| **Konektivitas Robot** | Belum ada integrasi MQTT (`robot/expression`) dan MediaPipe (*face tracking*). | Nilai `pup_ox` dan `pup_oy` hanya di-hardcode `0`; robot belum bisa merespons data sensor. |

---

## 2. Audit Kode & Flaw Kritis per File

### A. `rcry.py`
1. **Critical Bug: Duplikasi Kode Rendering Mulut (Baris 219–253)**
   - Di dalam main loop, bagian rendering mulut digambar **dua kali berturut-turut** dengan parameter dimensi yang berbeda:
     ```python
     # Blok 1 (Baris 221-232): Digambar dan diblit
     mouth_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
     ...
     screen.blit(mouth_surf, (box_x, box_y))
     
     # Blok 2 (Baris 238-249): Langsung digambar ulang dan menimpa Blok 1!
     mouth_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
     ...
     screen.blit(mouth_surf, (box_x, box_y))
     ```
   - **Dampak:** Terjadi pemborosan 4 alokasi surface transparan per frame (240 alokasi/detik) dan CPU cycle terbuang sia-sia untuk menggambar elemen yang langsung ditimpa.
2. **Kalkulasi Gelombang Air Mata Berat (CPU-Bound)**
   - Fungsi `draw_purple_eye_with_wave` melakukan perulangan `for x in range(rect.width)` (130 iterasi $\times$ 2 mata $\times$ 60 FPS = 15.600 pemanggilan `math.sin` per detik).
   - Pada Jetson Nano (ARM Cortex-A57), kalkulasi trigonometri per pixel di CPU tanpa SIMD/NumPy menurunkan kestabilan frame rate.
3. **Artifact Visual Layering Eyelid & Aliran Air Mata**
   - Stream air mata (`draw_cartoon_stream_slow`) digambar sebelum kelopak mata (`draw_eyelid`).
   - Kelopak mata digambar dengan `pygame.draw.rect(surface, BG_COLOR, cover_rect)` yang memotong area persegi di atas mata. Saat mata berkedip, persegi abu-abu ini memotong aliran air mata dan garis kabel secara kasar, meninggalkan patahan visual.

---

### B. `rshock.py`
1. **Flaw Logika Gerakan: Mulut "Kejang" Saat Berkedip (Blink-Coupled Mouth)**
   - Baris 154–155:
     ```python
     current_mouth_h = base_mouth_h * (1.0 - blink_progress)
     current_mouth_w = base_mouth_w + (blink_progress * 40)
     ```
   - **Masalah:** Bentuk mulut oval yang terkejut dipaksa mengecil dan memipih mengikuti kedipan mata. Akibatnya, setiap kali robot berkedip (tiap 2–5 detik), mulutnya ikut menciut lalu membesar kembali. Ini tidak natural dan menyerupai kejang visual, kecuali jika diniatkan sebagai animasi kaget sekali lewat (*flinch*), bukan *idle loop*.
2. **Memory Allocation inside Loop pada Mata**
   - Fungsi `draw_eye_gradient()` membuat `eye_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)` dua kali setiap frame (untuk mata kiri dan kanan).
   - Meskipun gradasinya sudah di-pre-render (`PRE_RENDERED_EYE_GRADIENT`), surface penampungnya tetap dibuat ulang setiap frame alih-alih di-reuse.

---

### C. `rhappy.py`
1. **Alokasi Masking Lidah Berulang**
   - Baris 166–170:
     ```python
     mouth_surf = pygame.Surface((mouth_w, mouth_box_h), pygame.SRCALPHA)
     tongue_surf = pygame.Surface((mouth_w, mouth_box_h), pygame.SRCALPHA)
     ```
   - Bentuk mulut senang bersifat statis (`STATIC_MOUTH_POINTS` tidak berubah). Seharusnya seluruh mulut (rongga gelap + lidah) cukup di-render **1 kali** ke sebuah `Surface` di awal program, lalu di-`blit` saja. Menggambar ulang poligon dan elips lidah setiap frame adalah operasi redundan.
2. **Ketiadaan Animasi Senyum**
   - Berbeda dengan `rshock` yang memiliki modulasi dinamis, `rhappy` murni statis kecuali kelopak matanya yang berkedip. Tidak ada getaran napas (*breathing idle*), modulasi kurva senyum, maupun mikro-ekspresi.

---

### D. `rload.py`
1. **Operasi Rotasi Software yang Boros (`pygame.transform.rotate`)**
   - Baris 97:
     ```python
     if angle != 0:
         canvas = pygame.transform.rotate(canvas, angle)
     ```
   - Fungsi `draw_rotated_layered_eye` melakukan alokasi 3 surface (`canvas`, `content`, `mask`) ditambah operasi rotasi software setiap frame untuk mata kanan. Rotasi raster di CPU Pygame tanpa akselerasi hardware sangat membebani GPU/CPU Jetson.
2. **Inkonsistensi Posisi Kabel**
   - Di `rload.py` baris 150, sambungan kabel ke mata kanan diberi offset vertikal `+ 20` (`left_eye_rect.top + 20`), sedangkan di `rshock.py` dan `rhappy.py` kabel menyambung tepat di `left_eye_rect.top`. Variasi koordinat antar file menunjukkan ketiadaan konstanta global bersama.

---

### E. File 0-Byte / Stub Kosong
File-file berikut terdaftar di repositori namun berukuran **0 byte**:
1. `rhappier.py` (Variasi senang dengan mata menyipit / bintang)
2. `rsad.py` (Ekspresi sedih dengan alis murung)
3. `rshy.py` (Ekspresi malu / kawaii dengan semburat pipi / blush)
4. `rtalkingState.py` (State berbicara dengan modulasi buka-tutup mulut)

> **Kekurangan Krusial:** `rtalkingState.py` adalah elemen vital bagi robot sosial seperti BRONE. Tanpa artikulasi mulut saat berbicara, robot akan terdengar berbicara dari speaker sementara mulutnya mematung atau terus berada di ekspresi shock/happy.

---

### F. `preview.py`
1. **Blocking Subprocess Execution**
   - Menu menjalankan skrip via `subprocess.run([sys.executable, filename])`.
   - Ini memblokir proses launcher sampai jendela pygame ditutup.
   - Tidak memungkinkan pergantian ekspresi secara langsung melalui keyboard tanpa menutup jendela tampilan.

---

## 3. Flaw Arsitektural Menyeluruh

### 1. Ketiadaan Delta Time ($dt$) untuk Animasi
Semua animasi saat ini mengandalkan penambahan inkremental konstan:
```python
blink_progress += blink_speed  # blink_speed = 0.15 per frame
time_counter += 0.1           # per frame
clock.tick(60)
```
- **Masalah:** Jika beban kerja Jetson Nano meningkat (misal saat kalkulasi AI / speech recognition aktif) dan frame rate turun ke 30 FPS, kecepatan animasi akan menjadi setengah kali lebih lambat (*slow motion*).
- **Solusi:** Seluruh pergerakan harus dikalikan dengan waktu nyata: `dt = clock.tick(60) / 1000.0`.

### 2. Pendekatan "Per-Script" alih-alih "Data-Driven / Component-Based"
Setiap file mendefinisikan ulang warna, inisialisasi display, event loop, dan fungsi gambar. Jika ingin mengubah warna latar belakang robot atau ukuran mata, pengembang harus menyunting seluruh file satu per satu.

### 3. Ketiadaan Integrasi I/O Robot (Headless & Network)
- Parameter `pup_ox` dan `pup_oy` sudah disiapkan, tetapi tidak ada modul pembaca pesan (MQTT subscriber atau socket listener) untuk menerima sinyal koordinat wajah manusia dari MediaPipe.
- Tidak ada mekanisme penanganan event keyboard/gamepad global untuk beralih mode.

---

## 4. Korelasi dengan Jurnal Xpress: Mengapa Wajah Belum Bisa Dinamis?

Jurnal **Xpress** (*Antony et al.*) merancang sistem ekspresi robot yang dinamis dan sadar konteks (*context-aware*). Mari kita bandingkan arsitektur Xpress dengan kode BRONE saat ini:

```
+-----------------------------------------------------------------------------------+
|                            PARADIGMA JURNAL XPRESS                                |
|                                                                                   |
|  [Input Konteks/Teks] ---> [Phase 1: Temporal Flow] ---> [Phase 2: Context zC]    |
|                                                                  |                |
|                                                                  v                |
|  [Wajah Robot: 28-DoF] <--- [Interpolator/Easing Engine] <--- [Phase 3: Trajectory|
|   (Mata, Alis, Mulut,        (Transisi halus parameter)       tau_face / Emosi]   |
|    Warna berubah smooth)                                                          |
+-----------------------------------------------------------------------------------+
                                        VS
+-----------------------------------------------------------------------------------+
|                            KODE BRONE SAAT INI                                    |
|                                                                                   |
|  [File rshock.py]  ---> While loop kaku 60 FPS (Bentuk Mulut Terkunci)            |
|  [File rhappy.py]  ---> While loop kaku 60 FPS (Kurva Mulut Terkunci)            |
|  [File rcry.py]    ---> While loop kaku 60 FPS (Air Mata Terkunci)                |
|                                                                                   |
|  * Tidak ada parameter bersama (DoF)                                              |
|  * Tidak ada transisi/interpolasi antar file                                      |
+-----------------------------------------------------------------------------------+
```

### Gap Kunci Antara BRONE dan Xpress:
1. **Degrees of Freedom (DoF) Parameterization**
   - **Xpress:** Memetakan wajah ke 28 derajat kebebasan (posisi mata, kelengkungan mulut, tinggi kelopak, rotasi alis, skala pupil, warna).
   - **BRONE:** Menggambar bentuk statis dengan poligon terpisah di masing-masing file tanpa variabel penentu bentuk yang bisa di-tween.
2. **Trajectory & State Interpolation ($\tau_{\text{face}}$)**
   - **Xpress:** Setiap emosi adalah target parameter nilai numerik. Sistem menghitung lintasan dari status saat ini ke status target menggunakan kurva easing (misal: *ease-in-out*).
   - **BRONE:** Pergantian ekspresi bersifat biner: matikan file A, jalankan file B. Tidak ada jembatan visual.
3. **Pemisahan Logika Emosi vs Rendering Engine**
   - **Xpress:** Ada pemisahan tegas antara *Decision Maker* (LLM/Rule-based/Bank Emosi) dan *Display Renderer*.
   - **BRONE:** Logika emosi, timing, dan rendering tercampur baur dalam satu file monolithic.

---

## 5. Roadmap & Blueprint Solusi untuk Pengembangan Kedepan

Berikut rekomendasi langkah demi langkah untuk mereformasi kode BRONE menjadi sistem dinamis berkualitas tinggi:

### Tahap 1: Unifikasi Rendering Engine (Single Display Window)
- Hentikan pemisahan file `r*.py` sebagai skrip terpisah yang berdiri sendiri.
- Buat modul inti: `brone_engine.py` yang memiliki:
  1. Satu `screen` Pygame yang tidak pernah ditutup.
  2. Canvas renderer yang mengambil parameter wajah dari state saat ini.
  3. Menggunakan **Delta Time** (`dt`) untuk kestabilan 60 FPS.
  4. Cache surface transparan (tidak membuat `pygame.Surface` baru dalam loop).

### Tahap 2: Definisi Parameter Wajah (Face State Representation)
Definisikan wajah BRONE sebagai kumpulan parameter numerik (DoF):
```python
class FaceState:
    eye_scale_x: float = 1.0
    eye_scale_y: float = 1.0
    eye_rotation: float = 0.0
    pupil_offset_x: float = 0.0
    pupil_offset_y: float = 0.0
    eyelid_top: float = 0.0      # 0.0 (terbuka) s/d 1.0 (tertutup)
    mouth_width: float = 220.0
    mouth_height: float = 80.0
    mouth_curvature: float = 0.0 # +1.0 (senyum), 0.0 (datar), -1.0 (sedih)
    mouth_openness: float = 0.0  # untuk artikulasi bicara (talking)
    tear_intensity: float = 0.0  # 0.0 s/d 1.0
    bg_color: tuple = (205, 215, 225)
```

### Tahap 3: Modul Interpolasi (Tweening / Easing Engine)
Buat fungsi transisi yang secara bertahap memindahkan parameter dari `CurrentState` ke `TargetState`:
$$\text{Current} = \text{Current} + (\text{Target} - \text{Current}) \times \text{easing}(t)$$
Dengan cara ini:
- Robot bisa beralih dari **Happy** ke **Surprised** dengan mata yang membesar secara bertahap (misal 300 ms).
- Mode berbicara (`rtalkingState`) cukup mengosilasikan parameter `mouth_openness` antara 0.2 dan 1.0 dengan kurva sinus, di atas ekspresi apa pun yang sedang aktif.

### Tahap 4: Implementasi Bank Emosi (Emotion Bank) Sesuai Jurnal Xpress
Buat kamus target state untuk emosi dasar:
- `NEUTRAL`: Mata oval tegak, mulut datar, kelopak rileks.
- `HAPPY`: Mata sedikit menyipit dari bawah, mulut melengkung ke atas (`mouth_curvature = 1.0`).
- `SHOCK`: Mata membesar (`eye_scale = 1.3`), mulut membuka lonjong vertikal.
- `SAD`: Sudut mata miring keluar, mulut melengkung ke bawah (`mouth_curvature = -1.0`).
- `CRY`: Sad state + `tear_intensity = 1.0`.
- `TALKING`: Layer osilasi mulut yang aktif berdampingan dengan emosi apa pun.

### Tahap 5: Integrasi Komunikasi Eksternal (MQTT & MediaPipe)
- Tambahkan thread background ringan (misal menggunakan modul `threading` + `paho-mqtt`) untuk menangkap topik `robot/expression`.
- Update `pupil_offset_x` dan `pupil_offset_y` secara real-time dari data MediaPipe untuk pelacakan kontak mata (*saccades* & *gaze tracking*).

---

## 6. Rangkuman Lengkap Seluruh Flaw Kode (Daftar Poin / Checklist Ringkas)

Berikut adalah rekapitulasi poin-demi-poin seluruh cacat kode (*code flaws*) dan kelemahan sistem yang ditemukan pada repositori ini:

###  Kategori 1: Bug Kritis & Masalah Performa (Rendering & Memory)
- [ ] **Duplikasi Render Mulut (`rcry.py:L219-L253`):** Poligon dan lidah mulut digambar dan di-blit dua kali berturut-turut di tiap frame, menimpa gambar sebelumnya dan menggandakan beban draw call.
- [ ] **Alokasi Surface Berulang di Main Loop (Semua File):** `pygame.Surface((w, h), pygame.SRCALPHA)` dialokasikan berulang kali setiap frame (60 kali/detik) untuk mata dan mulut, memicu lonjakan Garbage Collector dan *micro-stuttering* di Jetson Nano.
- [ ] **Kalkulasi Trigonometri CPU Berat (`rcry.py:L94`):** Pemanggilan fungsi sinus sebanyak 15.600 kali per detik di CPU untuk membuat gelombang air mata per pixel tanpa vektorisasi/caching.
- [ ] **Rotasi Raster Software Berat (`rload.py:L97`):** Menggunakan `pygame.transform.rotate()` pada surface bertingkat setiap frame di CPU tanpa akselerasi grafis hardware.
- [ ] **Redundansi Komputasi Mulut Senang (`rhappy.py:L166`):** Bentuk mulut bersifat statis 100%, tetapi pembuatan surface kanvas dan masking elips lidah tetap diulang 60 kali per detik alih-alih di-cache satu kali.

###  Kategori 2: Flaw Logika Animasi & Visual Glitch
- [ ] **Anomali Mulut Kejang saat Kedip (`rshock.py:L154-L157`):** Tinggi dan lebar mulut dikaitkan langsung ke `blink_progress`. Mulut kaget menciut dan gepeng setiap kali robot berkedip, tampak seperti kejang/spasme visual.
- [ ] **Animasi Terikat Frame Rate (Tanpa Delta Time / $dt$):** Progres animasi dihitung dengan penambahan nilai konstan (`+= 0.15`). Jika beban CPU naik dan FPS turun ke 30, pergerakan wajah robot otomatis menjadi *slow motion*.
- [ ] **Clipping Kasar Eyelid (`draw_eyelid`):** Penutup kelopak mata menggunakan balok persegi (`pygame.draw.rect`) dengan warna background, memotong garis kabel atas mata dan aliran air mata secara tidak rapi saat menutup.
- [ ] **Inkonsistensi Geometri Kabel Antar-File:** Posisi ujung sambungan kabel atas berbeda antar file (contoh: di `rload.py` diberi offset `+ 20`, sedangkan di `rhappy.py` tepat di `top`).

###  Kategori 3: Flaw Arsitektur (Penyebab Wajah Tidak Bisa Berganti Dinamis)
- [ ] **Arsitektur Skrip Terisolasi (Silo Execution):** Setiap file `r*.py` memiliki inisialisasi display, clock, dan while-loop mandiri. Tidak ada satu engine terpusat.
- [ ] **Ketiadaan Engine Transisi / Interpolasi (Lerp/Tweening):** Tidak ada fungsi transisi parameter dari ekspresi A ke ekspresi B; wajah terkunci kaku pada satu bentuk poligon permanen.
- [ ] **Pergantian Ekspresi via Subprocess Mematikan:** Di `preview.py`, ekspresi dijalankan via `subprocess.run()`. Untuk mengganti ekspresi, proses Pygame harus di-kill dan dihidupkan ulang, menimbulkan *screen flicker* dan jeda waktu lama.
- [ ] **Ketiadaan Parameterisasi Terpadu (Degrees of Freedom):** Komponen wajah (mata, alis, bukaan mulut, kurva senyum) tidak dimodelkan sebagai variabel angka yang bisa diubah-ubah, melainkan koordinat hardcoded.

###  Kategori 4: File Kosong & Fitur Esensial Belum Terwujud
- [ ] **Stub Kosong 0-Byte:** File `rhappier.py`, `rsad.py`, `rshy.py`, dan `rtalkingState.py` masih berukuran 0 byte.
- [ ] **Ketiadaan Artikulasi Mulut Bicara (`rtalkingState`):** Belum ada modul artikulasi rahang/mulut (*viseme modulation*) saat robot memutar suara atau berbicara.
- [ ] **Ketiadaan Input Sensor / Jaringan:** Variabel `pup_ox` dan `pup_oy` hanya bernilai `0`. Belum ada listener MQTT (`robot/expression`) atau socket MediaPipe untuk membaca pergerakan pupil secara nyata dari kamera.

