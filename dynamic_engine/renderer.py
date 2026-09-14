# -*- coding: utf-8 -*-
"""
BRONE Dynamic Engine - Unified Renderer (1024x600)
==================================================
Renderer performa tinggi dengan:
- Zero alokasi memori berulang di dalam main loop (pre-allocated surfaces).
- Support transisi bentuk mulut, air mata bergelombang, dan mata bergradasi.
- Tampilan overlay HUD (Mode Statis vs Dinamis, status emosi, & panduan keyboard).
"""

import pygame
import math
from .state import FaceState

# Warna Universal BRONE
BG_COLOR    = (205, 215, 225)
BLACK       = (0, 0, 0)
HIGHLIGHT   = (240, 245, 255)
MOUTH_DARK  = (40, 40, 40)
TONGUE      = (230, 130, 100)
TEAR_COLOR  = (170, 230, 255)
EYE_WATER   = (130, 200, 255)

class FaceRenderer:
    def __init__(self, width=1024, height=600):
        self.width = width
        self.height = height
        self.center_x = width // 2
        
        # Parameter Anatomi Mata Native
        self.eye_y = 220
        self.base_eye_w = 130
        self.base_eye_h = 160
        self.dist_from_center = 170
        
        # Pre-allocated Surfaces (Mencegah Garbage Collector Lag di Jetson Nano)
        self.mouth_max_w = 400
        self.mouth_max_h = 250
        self.mouth_surf = pygame.Surface((self.mouth_max_w, self.mouth_max_h), pygame.SRCALPHA)
        self.tongue_surf = pygame.Surface((self.mouth_max_w, self.mouth_max_h), pygame.SRCALPHA)
        
        self.eye_surf = pygame.Surface((self.base_eye_w * 2, self.base_eye_h * 2), pygame.SRCALPHA)
        self.mask_surf = pygame.Surface((self.base_eye_w, self.base_eye_h), pygame.SRCALPHA)
        pygame.draw.ellipse(self.mask_surf, (255, 255, 255, 255), (0, 0, self.base_eye_w, self.base_eye_h))
        
        # Timer internal untuk animasi gelombang air mata
        self.anim_time = 0.0
        
        # Font untuk HUD Debug
        pygame.font.init()
        self.font = pygame.font.SysFont("Consolas", 16, bold=True)
        self.show_hud = True

    def draw(self, screen: pygame.Surface, state: FaceState, mode: str, emotion_name: str, is_talking: bool, fps: float, dt: float):
        self.anim_time += dt * 3.0
        screen.fill(BG_COLOR)
        
        # 1. Hitung Dimensi Mata Dinamis
        cur_eye_w = int(self.base_eye_w * state.eye_scale_x)
        cur_eye_h = int(self.base_eye_h * state.eye_scale_y)
        
        left_eye_rect = pygame.Rect(
            self.center_x - self.dist_from_center - cur_eye_w,
            self.eye_y - (cur_eye_h - self.base_eye_h) // 2,
            cur_eye_w, cur_eye_h
        )
        right_eye_rect = pygame.Rect(
            self.center_x + self.dist_from_center,
            self.eye_y - (cur_eye_h - self.base_eye_h) // 2,
            cur_eye_w, cur_eye_h
        )
        
        # 2. Gambar Kabel Robot (Statis Terhubung ke Mata)
        self._draw_cables(screen, left_eye_rect, right_eye_rect)
        
        # 3. Gambar Aliran Air Mata (Jika Tear Intensity > 0)
        if state.tear_intensity > 0.05:
            self._draw_tear_streams(screen, left_eye_rect, right_eye_rect, state.tear_intensity)
            
        # 4. Gambar Mata Kiri & Kanan (Gradasi + Gelombang Air + Saccade Glints)
        self._draw_eye(screen, left_eye_rect, state, state.eye_rot_l, is_left=True)
        self._draw_eye(screen, right_eye_rect, state, state.eye_rot_r, is_left=False)
        
        # 5. Gambar Kelopak Mata (Kedip Natural)
        if state.eyelid_progress > 0.01:
            self._draw_eyelids(screen, left_eye_rect, right_eye_rect, state.eyelid_progress)
            
        # 6. Gambar Mulut (Dinamis: Senyum, Oval Kaget, Sedih, atau Netral + Talking)
        self._draw_mouth(screen, state)
        
        # 7. Gambar HUD / Debug Info
        if self.show_hud:
            self._draw_hud(screen, mode, emotion_name, is_talking, fps)

    def _draw_cables(self, screen, left_rect, right_rect):
        elbow_y = left_rect.top - 50
        # Kabel kiri dari luar layar ke mata kiri
        pygame.draw.lines(screen, BLACK, False, [(-20, 60), (left_rect.centerx, elbow_y), (left_rect.centerx, left_rect.top)], 5)
        # Kabel kanan dari luar layar ke mata kanan
        pygame.draw.lines(screen, BLACK, False, [(self.width + 20, 60), (right_rect.centerx, elbow_y), (right_rect.centerx, right_rect.top)], 5)
        # Kabel jembatan tengah
        pygame.draw.lines(screen, BLACK, False, [
            (left_rect.right - 10, left_rect.centery),
            (self.center_x, left_rect.centery + 30),
            (right_rect.left + 10, right_rect.centery)
        ], 5)

    def _draw_tear_streams(self, screen, left_rect, right_rect, intensity):
        for center_x in (left_rect.centerx, right_rect.centerx):
            start_y = left_rect.bottom - 15
            width_top = int(35 * intensity)
            width_bot = int(48 * intensity)
            
            pts = []
            for y in range(start_y, self.height, 12):
                prog = (y - start_y) / max(1, self.height - start_y)
                cur_w = width_top + (width_bot - width_top) * prog
                wiggle = math.sin(y * 0.05 + self.anim_time) * 4
                pts.append((center_x - cur_w / 2 + wiggle, y))
            for y in range(self.height, start_y, -12):
                prog = (y - start_y) / max(1, self.height - start_y)
                cur_w = width_top + (width_bot - width_top) * prog
                wiggle = math.sin(y * 0.05 + self.anim_time) * 4
                pts.append((center_x + cur_w / 2 + wiggle, y))
                
            if len(pts) > 3:
                pygame.draw.polygon(screen, TEAR_COLOR, pts)
                
            # Tetesan kilau air jatuh
            for i in range(2):
                drop_y = start_y + int((self.anim_time * 80 + i * 200) % (self.height - start_y + 50))
                if drop_y < self.height:
                    drop_rect = pygame.Rect(center_x - 6, drop_y, 12, 28)
                    pygame.draw.ellipse(screen, HIGHLIGHT, drop_rect)

    def _draw_eye(self, screen, rect, state: FaceState, rotation: float, is_left: bool):
        # 1. Outline Luar
        pygame.draw.ellipse(screen, BLACK, rect.inflate(12, 12))
        
        # 2. Kanvas Mata
        w, h = rect.width, rect.height
        canvas = pygame.Surface((w, h), pygame.SRCALPHA)
        
        # Gradasi Warna
        for y in range(h):
            ratio = y / max(1, h)
            r = int(state.eye_top_color[0] * (1 - ratio) + state.eye_bot_color[0] * ratio)
            g = int(state.eye_top_color[1] * (1 - ratio) + state.eye_bot_color[1] * ratio)
            b = int(state.eye_top_color[2] * (1 - ratio) + state.eye_bot_color[2] * ratio)
            pygame.draw.line(canvas, (r, g, b), (0, y), (w, y))
            
        # Jika ada efek air mata di dalam mata (Cry mode)
        if state.eye_water_alpha > 0.05:
            water_pts = []
            water_lvl = h * (0.55 - 0.1 * state.eye_water_alpha)
            for x in range(w):
                wave = 5 * math.sin(0.15 * x + self.anim_time + (0 if is_left else 2))
                water_pts.append((x, water_lvl + wave + state.pupil_oy))
            water_pts.append((w, h))
            water_pts.append((0, h))
            pygame.draw.polygon(canvas, EYE_WATER, water_pts)
            
        # Masking Elips
        mask = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.ellipse(mask, (255, 255, 255, 255), (0, 0, w, h))
        canvas.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
        # Rotasi jika ada (misal di Load mode)
        if abs(rotation) > 0.5:
            canvas = pygame.transform.rotate(canvas, rotation)
            new_rect = canvas.get_rect(center=rect.center)
            screen.blit(canvas, new_rect.topleft)
        else:
            screen.blit(canvas, rect.topleft)
            
        # 3. Kilau Cahaya (Glints Saccade Ready)
        glint_x = rect.left + int(rect.width * 0.3) + int(state.pupil_ox)
        glint_y = rect.top + int(rect.height * 0.25) + int(state.pupil_oy)
        pygame.draw.circle(screen, HIGHLIGHT, (glint_x, glint_y), int(rect.width * 0.18))
        pygame.draw.circle(screen, state.eye_top_color, (glint_x + 8, glint_y + 8), int(rect.width * 0.08))
        
        small_glint_x = glint_x - 5
        small_glint_y = glint_y + int(rect.height * 0.3)
        pygame.draw.circle(screen, HIGHLIGHT, (small_glint_x, small_glint_y), int(rect.width * 0.05))

    def _draw_eyelids(self, screen, left_rect, right_rect, progress):
        for rect in (left_rect, right_rect):
            lid_h = int(rect.height * progress)
            if lid_h <= 0: continue
            
            cover_rect = pygame.Rect(rect.left - 6, rect.top - 6, rect.width + 12, lid_h + 6)
            pygame.draw.rect(screen, BG_COLOR, cover_rect)
            
            line_y = min(rect.bottom, rect.top + lid_h)
            pygame.draw.line(screen, BLACK, (rect.left - 6, line_y), (rect.right + 6, line_y), 6)

    def _draw_mouth(self, screen, state: FaceState):
        # Modulasi tinggi mulut saat Talking State aktif
        talk_extra_h = state.mouth_openness * 40.0
        cur_w = max(40, int(state.mouth_w))
        cur_h = max(10, int(state.mouth_h + talk_extra_h))
        
        mouth_rect = pygame.Rect(0, 0, cur_w, cur_h)
        mouth_rect.center = (self.center_x, 450)
        
        if state.mouth_style == "neutral":
            # Mulut datar / garis tenang
            pygame.draw.rect(screen, BLACK, (mouth_rect.left, mouth_rect.centery - 4, mouth_rect.width, 8), border_radius=4)
            if state.mouth_openness > 0.05:
                # Sedikit rongga saat berbicara
                inner_rect = mouth_rect.inflate(-40, int(talk_extra_h))
                pygame.draw.ellipse(screen, MOUTH_DARK, inner_rect)
                pygame.draw.ellipse(screen, BLACK, inner_rect, 4)
                
        elif state.mouth_style == "oval":
            # Mulut lonjong (Shock / Load) dengan Squash & Stretch Lidah
            pygame.draw.ellipse(screen, MOUTH_DARK, mouth_rect)
            
            # Lidah di dasar mulut
            clip_rect = pygame.Rect(mouth_rect.left, mouth_rect.centery, mouth_rect.width, mouth_rect.height // 2)
            screen.set_clip(clip_rect)
            pygame.draw.ellipse(screen, TONGUE, mouth_rect)
            screen.set_clip(None)
            
            pygame.draw.ellipse(screen, BLACK, mouth_rect, 6)
            
        elif state.mouth_style == "smile":
            # Mulut Kurva Tersenyum
            pts = []
            steps = 40
            top_y = mouth_rect.top
            sag = 25
            for i in range(steps + 1):
                t = i / steps
                px = mouth_rect.left + t * cur_w
                py = top_y + (sag * 4 * t * (1 - t))
                pts.append((px, py))
            for i in range(steps, -1, -1):
                t = i / steps
                px = mouth_rect.left + t * cur_w
                dx = px - mouth_rect.centerx
                a = cur_w / 2
                inside = max(0, 1 - (dx / max(1, a))**2)
                py = top_y + cur_h * math.sqrt(inside)
                pts.append((px, py))
                
            pygame.draw.polygon(screen, MOUTH_DARK, pts)
            
            # Gambar lidah dengan clipping rect aman
            clip_rect = pygame.Rect(mouth_rect.left, mouth_rect.centery + 10, mouth_rect.width, mouth_rect.height // 2)
            screen.set_clip(clip_rect)
            tongue_rect = pygame.Rect(mouth_rect.centerx - cur_w * 0.35, mouth_rect.centery, cur_w * 0.7, cur_h * 0.9)
            pygame.draw.ellipse(screen, TONGUE, tongue_rect)
            screen.set_clip(None)
            
            pygame.draw.polygon(screen, BLACK, pts, 6)
            
        elif state.mouth_style == "sad":
            # Mulut Kurva Menangis Terbalik (Sad Wail)
            pts = []
            steps = 40
            base_y = mouth_rect.bottom
            for i in range(steps + 1):
                t = i / steps
                px = mouth_rect.left + t * cur_w
                py = base_y - (cur_h * 4 * t * (1 - t))
                pts.append((px, py))
            for i in range(steps, -1, -1):
                t = i / steps
                px = mouth_rect.left + t * cur_w
                py = base_y - (18 * 4 * t * (1 - t))
                pts.append((px, py))
                
            pygame.draw.polygon(screen, MOUTH_DARK, pts)
            
            # Lidah di dasar mulut sedih
            tongue_rect = pygame.Rect(mouth_rect.centerx - cur_w * 0.25, base_y - 30, cur_w * 0.5, 35)
            clip_rect = pygame.Rect(mouth_rect.left, mouth_rect.top, mouth_rect.width, mouth_rect.height)
            screen.set_clip(clip_rect)
            pygame.draw.ellipse(screen, TONGUE, tongue_rect)
            screen.set_clip(None)
            
            pygame.draw.polygon(screen, BLACK, pts, 6)

    def _draw_hud(self, screen, mode: str, emotion: str, is_talking: bool, fps: float):
        # Background bar semi-transparan di bagian atas
        hud_surf = pygame.Surface((self.width, 36), pygame.SRCALPHA)
        hud_surf.fill((20, 25, 35, 180))
        screen.blit(hud_surf, (0, 0))
        
        mode_color = (100, 255, 150) if mode == "DYNAMIC" else (255, 200, 80)
        mode_text = f"MODE: [{mode}] (Tekan 'M' utk Toggle)"
        status_text = f"EMOTION: {emotion} | TALK: {'ON' if is_talking else 'OFF'} (Tekan 'T') | FPS: {fps:.0f}"
        guide_text = "[1] Happy  [2] Shock  [3] Cry  [4] Load  [0] Neutral  [D] HUD"
        
        t1 = self.font.render(mode_text, True, mode_color)
        t2 = self.font.render(status_text, True, (230, 240, 255))
        t3 = self.font.render(guide_text, True, (180, 200, 220))
        
        screen.blit(t1, (16, 9))
        screen.blit(t2, (340, 9))
        screen.blit(t3, (self.width - t3.get_width() - 16, 9))
