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

EXPRESSIONS = {
    "1": ("rshock.py", "[SHOCK]   Terkejut / Shocked (Blueprint)"),
    "2": ("rhappy.py", "[HAPPY]   Senang / Happy (Blueprint)"),
    "3": ("rcry.py",   "[CRY]     Menangis / Cry (Revised Blueprint)"),
    "4": ("rload.py",  "[LOAD]    Loading / Mikir (Blueprint)"),
}

def main():
    os.system("cls" if os.name == "nt" else "clear")
    print("=" * 60)
    print("    🤖 BRONE v3 - Unified Expression Launcher")
    print("=" * 60)
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

    while True:
        choice = input("Pilih menu (D, 1-4, atau Q): ").strip().lower()
        if choice == "q":
            print("Sampai jumpa! 👋")
            break

        if choice == "d":
            print("\n  >> Menjalankan: BRONE DYNAMIC ENGINE...")
            print("  (Gunakan tombol [M], [1-4], [0], [T], [B] di dalam jendela)")
            run_script = os.path.join(BASE_DIR, "run_dynamic.py")
            subprocess.run([sys.executable, run_script])
            input("\n  Tekan Enter untuk kembali ke menu...")
            main()
            return

        if choice in EXPRESSIONS:
            filename, label = EXPRESSIONS[choice]
            filepath = os.path.join(STATIC_DIR, filename)
            
            if not os.path.exists(filepath):
                print(f"  [ERROR] File '{filename}' tidak ditemukan di static_expressions/!")
                continue

            print(f"\n  >> Menjalankan: {label}")
            print("  (Tutup jendela pygame untuk kembali ke menu)\n")
            
            subprocess.run([sys.executable, filepath])
            
            print(f"\n  [DONE] Selesai preview: {label}")
            input("  Tekan Enter untuk kembali ke menu...")
            main()
            return
        else:
            print("  [!] Pilihan tidak valid, coba lagi.")

if __name__ == "__main__":
    main()
