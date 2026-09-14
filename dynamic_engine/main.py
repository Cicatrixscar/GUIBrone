# -*- coding: utf-8 -*-
"""
BRONE Dynamic Engine - Main Controller
======================================
Eksekusi utama sistem wajah robot BRONE (1024x600).
Dapat dijalankan langsung dengan:
    py -3.12 -m dynamic_engine.main
atau via run_dynamic.py
"""

import pygame
import sys
import os

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Pastikan path modul terdeteksi
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dynamic_engine.interpolator import FaceInterpolator
from dynamic_engine.renderer import FaceRenderer

def run_engine():
    pygame.init()
    WIDTH, HEIGHT = 1024, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("BRONE Robot Face Engine - Dynamic & Static Mode")
    
    clock = pygame.time.Clock()
    interpolator = FaceInterpolator()
    renderer = FaceRenderer(WIDTH, HEIGHT)
    
    running = True
    print("=" * 60)
    print("   BRONE Face Engine Berjalan!")
    print("=" * 60)
    print("  [M] Toggle MODE (DYNAMIC <--> STATIC)")
    print("  [1] Happy   [2] Shock   [3] Cry   [4] Load   [0] Neutral")
    print("  [T] Toggle Talking (Artikulasi Bicara)")
    print("  [B] Trigger Kedip Manual")
    print("  [D] Sembunyikan / Tampilkan HUD")
    print("  [ESC] Keluar")
    print("=" * 60)
    
    while running:
        # Delta time dalam detik (mencegah animasi melambat jika FPS drop di Jetson)
        dt = clock.tick(60) / 1000.0
        
        # --- Handle Event Keyboard ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_m:
                    new_mode = interpolator.toggle_mode()
                    print(f"  >> Mode beralih ke: [{new_mode}]")
                elif event.key == pygame.K_t:
                    talking = interpolator.toggle_talking()
                    print(f"  >> Talking State: {'ON' if talking else 'OFF'}")
                elif event.key == pygame.K_d:
                    renderer.show_hud = not renderer.show_hud
                elif event.key == pygame.K_b:
                    interpolator.blink_state = "closing"
                elif event.key in (pygame.K_0, pygame.K_i):
                    interpolator.set_emotion("NEUTRAL")
                elif event.key == pygame.K_1:
                    interpolator.set_emotion("HAPPY")
                elif event.key == pygame.K_2:
                    interpolator.set_emotion("SHOCK")
                elif event.key == pygame.K_3:
                    interpolator.set_emotion("CRY")
                elif event.key == pygame.K_4:
                    interpolator.set_emotion("LOAD")

        # --- Update Interpolasi State ---
        current_state = interpolator.update(dt)
        
        # --- Render ke Layar ---
        renderer.draw(
            screen=screen,
            state=current_state,
            mode=interpolator.mode,
            emotion_name=interpolator.current_emotion,
            is_talking=interpolator.is_talking,
            fps=clock.get_fps(),
            dt=dt
        )
        
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    run_engine()
