# -*- coding: utf-8 -*-
"""
BRONE v3 - Expression Launcher
==============================
Menu pengujian terpadu untuk:
- Dynamic Engine (Mode Dinamis & Statis dengan transisi halus dan artikulasi bicara)
- Static Blueprints (Cetak biru ekspresi individual)
Usage: py -3.12 preview.py
"""

import subprocess
import sys
import os

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static_expressions")

# Otomatis cari Python yang punya pygame (utamakan .venv lokal atau Python 3.12)
def get_python_exe():
    candidates = [
        os.path.join(BASE_DIR, ".venv", "Scripts", "python.exe"),
        r"C:\Users\ASCARYA\AppData\Local\Python\pythoncore-3.12-64\python.exe",
        sys.executable
    ]
    for exe in candidates:
        if os.path.exists(exe):
            return exe
    return sys.executable

PYTHON_EXE = get_python_exe()

# Jika script dijalankan dengan Python yang salah (misal 3.14 tanpa pygame),
# otomatis alihkan ke PYTHON_EXE yang benar!
try:
    import pygame
except ImportError:
    if PYTHON_EXE != sys.executable:
        os.execv(PYTHON_EXE, [PYTHON_EXE] + sys.argv)

EXPRESSIONS = {
    "1": ("rshock.py", "[SHOCK]   Terkejut / Shocked (Blueprint)"),
    "2": ("rhappy.py", "[HAPPY]   Senang / Happy (Blueprint)"),
    "3": ("rcry.py",   "[CRY]     Menangis / Cry (Revised Blueprint)"),
    "4": ("rload.py",  "[LOAD]    Loading / Mikir (Blueprint)"),
}

# Pastikan proses anak juga mencetak UTF-8 (cegah UnicodeEncodeError emoji)
RUN_ENV = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}

# --- Debug trace (sementara untuk diagnosa) ---
TRACE_LOG = os.path.join(BASE_DIR, "debug_trace.log")
def trace(msg):
    import datetime as _dt
    try:
        with open(TRACE_LOG, "a", encoding="utf-8") as f:
            f.write(f"{_dt.datetime.now().strftime('%H:%M:%S.%f')}  {msg}\n")
    except Exception:
        pass

# --- Single-instance guard ---
# Cegah dua preview.py jalan barengan (penyebab ketikan nyasar antar 2 jendela)
_GUARD = None
def acquire_single_instance():
    global _GUARD
    try:
        import ctypes
        _GUARD = ctypes.windll.kernel32.CreateMutexW(
            None, False, "Local\\BRONE_preview_v3"
        )
        if ctypes.windll.kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
            return False
        return True
    except Exception:
        return True  # gagal guard -> biarkan berjalan

def draw_menu(status=None):
    # TUI layar penuh: selalu digambar ulang di posisi yang sama (tidak meloncat)
    os.system("cls" if os.name == "nt" else "clear")
    print("=" * 60)
    print("    🤖 BRONE v3 - Unified Expression Launcher")
    print("=" * 60)
    print(f"  [Interpreter]: {PYTHON_EXE}")
    print(f"  [Build]       preview.py v3.3 (TUI full-screen, tidak meloncat)")
    print()
    print("  ⭐ [D] RUN DYNAMIC ENGINE (Transisi Halus + Talking)")
    print("         (Dilengkapi saklar Mode Statis <-> Dinamis via tombol 'M')")
    print()
    print("  --- Cetak Biru Statis Individual ---")
    for key, (filename, label) in EXPRESSIONS.items():
        filepath = os.path.join(STATIC_DIR, filename)
        exists = "[OK]" if os.path.exists(filepath) and os.path.getsize(filepath) > 10 else "[MISSING]"
        print(f"  [{key}] {label:<42} {exists}")
    print()
    print("  [Q] Keluar")
    print()
    if status:
        print(f"  {status}")
    print("=" * 60)

def main():
    trace("main() mulai")
    draw_menu()
    while True:
        choice = input("  Pilih menu (D, 1-4, atau Q): ").strip().lower()
        trace(f"input menu: {choice!r}")
        if choice == "q":
            print("Sampai jumpa! 👋")
            trace("pilih q -> selesai")
            break

        if choice == "d":
            print("\n  >> Menjalankan: BRONE DYNAMIC ENGINE...")
            print("  (Gunakan tombol [M], [1-4], [0], [T], [B] di dalam jendela)")
            run_script = os.path.join(BASE_DIR, "run_dynamic.py")
            trace("sebelum subprocess run_dynamic")
            subprocess.run([PYTHON_EXE, run_script], env=RUN_ENV)
            trace("setelah subprocess run_dynamic")
            draw_menu("Selesai: BRONE DYNAMIC ENGINE")
            continue

        if choice in EXPRESSIONS:
            filename, label = EXPRESSIONS[choice]
            filepath = os.path.join(STATIC_DIR, filename)
            
            if not os.path.exists(filepath):
                draw_menu(f"[!] File '{filename}' tidak ditemukan di static_expressions/!")
                continue

            print(f"\n  >> Menjalankan: {label}")
            print("  (Tutup jendela pygame untuk kembali ke menu)\n")
            
            trace(f"sebelum subprocess {filename}")
            subprocess.run([PYTHON_EXE, filepath], env=RUN_ENV)
            trace(f"setelah subprocess {filename}")
            
            draw_menu(f"[OK] Selesai preview: {label}")
            continue
        else:
            draw_menu("[!] Pilihan tidak valid, coba lagi.")

if __name__ == "__main__":
    trace("main() mulai")
    if not acquire_single_instance():
        print("\n  [!] Sudah ada preview.py yang sedang berjalan.")
        print("  (Tombol Run mungkin ditekan 2x, atau ada jendela lain yang masih terbuka)")
        print("  Tutup jendela/instance yang lain, lalu jalankan ulang.")
        input("  Tekan Enter untuk menutup instance ini...")
        trace("instance ganda -> ditolak")
        sys.exit(0)
    try:
        main()
        trace("main() selesai normal")
    except (EOFError, KeyboardInterrupt):
        trace("EOFError / KeyboardInterrupt")
        print("\n  Sampai jumpa! 👋")
    except Exception as e:
        trace(f"EXCEPTION: {type(e).__name__}: {e}")
        import traceback
        print("\n  [ERROR] Terjadi kesalahan tidak terduga:")
        traceback.print_exc()
        input("\n  Tekan Enter untuk menutup jendela ini...")
