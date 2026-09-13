# 📖 Panduan Akses Remote & Pengujian Ekspresi BRONE

Dokumentasi ini menjelaskan prosedur standar untuk menghubungkan perangkat lokal ke Jetson Nano melalui jaringan, menavigasi direktori proyek, dan menguji modul ekspresi wajah.

## 1. Persiapan Koneksi Jaringan (Tailscale & VPN)
Sebelum melakukan akses remote, pastikan perangkat berada dalam jaringan privat yang sama dengan Jetson Nano.

* **Aplikasi:** Gunakan **Tailscale**.
* **Prosedur:**
    1. Buka aplikasi Tailscale di laptop.
    2. Pastikan sudah *Log In* menggunakan akun yang terdaftar (misal: `dicodingcnub@gmail.com`).
    3. Pastikan status koneksi adalah **Active/Connected**.
    4. Cek daftar *Machines*. Pastikan unit **`ubuntu`** (Jetson Nano) dengan IP **`100.124.254.69`** berstatus *Online*.

## 2. Akses Terminal Jarak Jauh (SSH)
Setelah koneksi VPN aktif, gunakan terminal (PowerShell di Windows atau Terminal di macOS/Linux) untuk masuk ke sistem robot.

* **Perintah Utama:**
```bash
ssh brone@100.124.254.69
```
* **Autentikasi:** Masukkan *password* akun `brone` . *(Catatan: Karakter password tidak akan muncul di layar saat diketik).*

## 3. Navigasi Direktori & Akses File Ekspresi (Python)
Setelah berhasil masuk ke dalam Jetson via SSH, posisi awalmu berada di direktori utama (home). Berikut adalah panduan navigasi menuju file-file sistem.

### A. Perintah Dasar Linux
Gunakan perintah berikut untuk bernavigasi di dalam terminal:

| Perintah | Fungsi |
| :--- | :--- |
| `ls` | Melihat daftar file dan folder (Folder = Biru, File = Putih). |
| `cd [nama_folder]` | Masuk ke folder yang dituju. |
| `cd ..` | Kembali ke folder sebelumnya (mundur satu tingkat). |
| `history` | Melihat riwayat perintah yang pernah diketik sebelumnya. |

### B. Menuju Direktori Cetak Biru Ekspresi
Kumpulan file Python (sebagai referensi/cetak biru desain ekspresi) disimpan secara khusus di dalam sub-folder `REFINEMENT/`. Berikut urutan perintahnya:

1. **Masuk ke folder utama proyek BRONE:**
```bash
cd main-program-brone/
```
2. **Masuk ke folder sistem ekspresi:**
```bash
cd IntegrateSpeechExpression/
```
3. **Masuk ke folder arsip ekspresi:**
```bash
cd expression/
```
4. **Masuk ke folder referensi desain wajah:**
```bash
cd REFINEMENT/
```

> **💡 Tips Cepat:** sekaligus dengan satu perintah: 
> `cd main-program-brone/IntegrateSpeechExpression/expression/REFINEMENT/`

### C. Mengecek dan Mengedit Kodingan Ekspresi
Setelah berada di dalam folder `REFINEMENT/`, ketik perintah `ls` untuk melihat daftar file Python yang tersedia:
* `rcry.py` (Menangis)
* `rhappier.py` (Sangat Senang)
* `rhappy.py` (Senyum/Senang)
* `rload.py` (Loading/Mikir)
* `rsad.py` (Sedih)
* `rshock.py` (Terkejut)
* `rshy.py` (Malu/Kawaii)
* `rtalkingState.py` (Berbicara)

Jika ingin mengecek isi kodenya langsung di terminal, gunakan perintah `nano` (contoh: `nano rsad.py`). 
*(Tekan `Ctrl + X` lalu ketik `N` untuk keluar dari editor nano tanpa menyimpan).*

## 4. Menjalankan & Menguji Ekspresi di Browser
Sistem ekspresi utama BRONE berbasis web (HTML5 Canvas). Berikut urutan untuk menampilkannya di layar:

### A. Membuka Tampilan Wajah
Untuk melihat visualisasi wajah, buka browser (Chrome/Chromium) di Jetson Nano:
1. Akses lokasi file: `main-program-brone/IntegrateSpeechExpression/index.html`.
2. Buka file tersebut menggunakan **Chromium Browser**.
3. Gunakan *Kiosk Mode* agar tampilan memenuhi layar secara *Full Screen*.

### B. Kontrol Ekspresi (Keyboard Shortcuts)
Saat browser aktif, ekspresi dapat diubah secara manual menggunakan *keyboard shortcut*:
* **[S]**: Mode *Speaking* (Mulut bergerak).
* **[1] - [5]**: Berganti ekspresi (Sad, Shock, Cry, Shy, Happier).
* **[I] atau [0]**: Kembali ke mode *Idle* (Normal).
* **[D]**: Membuka/menutup *Debug Panel* (untuk melihat status *tracking*).

## 5. Alur Integrasi Data (MQTT)
Untuk pengujian otomatis, sistem menggunakan protokol MQTT. Data dikirim dalam format JSON ke topik yang telah ditentukan:

* **Topik:** `robot/expression`
* **Payload Contoh:**
```json
{
  "expression": "happy",
  "duration": 0
}
```
* **Ekspresi Pupil:** Pergerakan pupil dikontrol secara otomatis melalui deteksi wajah (MediaPipe) atau input koordinat eksternal melalui variabel `D_percent` dan `H_percent` yang sudah dibatasi secara sistem agar tidak keluar dari diameter anatomi mata.

---

### Tips Troubleshooting
* **Connection Timed Out:** Pastikan unit Jetson menyala dan Tailscale di unit tersebut berstatus *Active*. Lakukan perintah `ping 100.124.254.69` dari perangkat lokal untuk memastikan koneksi.
* **Permission Denied:** Gunakan awalan perintah `sudo` jika diperlukan akses administratif, namun berhati-hatilah saat mengubah file sistem konfigurasi.

---

*Dokumentasi ini dapat diperbarui seiring dengan perkembangan fitur Face Tracking dan integrasi hardware robot oleh tim.*
