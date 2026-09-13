# BRONE v3 - Dynamic & Static Expression Engine

Repositori ini adalah iterasi bersih (clean architecture) untuk pengembangan sistem ekspresi robot BRONE 1024x600.

## 🗂️ Struktur Direktori

```
brone-v3/
├── static_expressions/          # Kumpulan cetak biru visual ekspresi statis
│   ├── rcry.py                  # Ekspresi menangis (sudah direvisi tanpa duplikasi render)
│   ├── rhappy.py                # Ekspresi senang
│   ├── rshock.py                # Ekspresi terkejut
│   └── rload.py                 # Ekspresi berpikir/loading
│
├── docs/                        # Dokumen riset, audit, dan panduan remote
│   ├── analisis_flaws_dan_roadmap_brone.md
│   ├── PANDUAN_REMOTE.md
│   └── Xpress A System For Dynamic.pdf
│
├── preview.py                   # Launcher interaktif untuk menguji ekspresi statis
└── .vscode/settings.json        # Konfigurasi Python 3.12 untuk editor
```

## 🚀 Cara Menjalankan
Jalankan preview launcher dengan Python 3.12:
```bash
py -3.12 preview.py
```
