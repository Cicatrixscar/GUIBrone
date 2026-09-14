# -*- coding: utf-8 -*-
"""
BRONE v3 - Dynamic Engine Launcher
Jalankan langsung dengan:
    py -3.12 run_dynamic.py
"""
import sys
import os

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Otomatis pastikan menggunakan Python yang memiliki pygame
def ensure_correct_python():
    try:
        import pygame
    except ImportError:
        candidates = [
            os.path.join(BASE_DIR, ".venv", "Scripts", "python.exe"),
            r"C:\Users\ASCARYA\AppData\Local\Python\pythoncore-3.12-64\python.exe",
        ]
        for exe in candidates:
            if os.path.exists(exe):
                try:
                    os.execv(exe, [exe] + sys.argv)
                except OSError as e:
                    print(f"[FATAL] Gagal restart dengan {exe}: {e}")
                    sys.exit(1)
        print("[FATAL] Tidak ada interpreter dengan pygame ditemukan.")
        print("Install pygame atau jalankan via preview.py / .venv.")
        sys.exit(1)

ensure_correct_python()

from dynamic_engine.main import run_engine

if __name__ == "__main__":
    run_engine()
