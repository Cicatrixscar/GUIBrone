# -*- coding: utf-8 -*-
"""
BRONE v3 - Dynamic Engine Launcher
Jalankan langsung dengan:
    py -3.12 run_dynamic.py
"""
import sys
import os

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
                os.execv(exe, [exe] + sys.argv)

ensure_correct_python()

from dynamic_engine.main import run_engine

if __name__ == "__main__":
    run_engine()
