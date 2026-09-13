# -*- coding: utf-8 -*-
"""
BRONE Dynamic Engine - Face State & Emotion Presets
===================================================
Mendefinisikan parameter wajah (DoF - Degrees of Freedom) dan bank emosi.
"""

from dataclasses import dataclass, field
from typing import Tuple

@dataclass
class FaceState:
    # 1. Transformasi Mata
    eye_scale_x: float = 1.0
    eye_scale_y: float = 1.0
    eye_rot_l: float = 0.0      # Derajat rotasi mata kiri
    eye_rot_r: float = 0.0      # Derajat rotasi mata kanan
    pupil_ox: float = 0.0       # Saccade / gaze horizontal offset (-50 s/d 50)
    pupil_oy: float = 0.0       # Saccade / gaze vertical offset (-30 s/d 30)
    eyelid_progress: float = 0.0 # 0.0 (terbuka penuh) s/d 1.0 (tertutup rapat)
    
    # 2. Efek & Warna Mata
    eye_water_alpha: float = 0.0  # 0.0 (normal) s/d 1.0 (penuh gelombang air)
    tear_intensity: float = 0.0   # 0.0 (kering) s/d 1.0 (aliran air mata aktif)
    eye_top_color: Tuple[int, int, int] = (80, 70, 150)
    eye_bot_color: Tuple[int, int, int] = (0, 0, 0)
    
    # 3. Mulut
    mouth_w: float = 220.0
    mouth_h: float = 60.0
    mouth_curve: float = 0.0     # +1.0 (senyum lebar), -1.0 (sedih/menangis), 0.0 (oval/flat)
    mouth_openness: float = 0.0  # 0.0 (diam) s/d 1.0 (artikulasi bicara / talking)
    mouth_style: str = "neutral" # "neutral", "smile", "oval", "sad"

    def copy(self):
        return FaceState(
            eye_scale_x=self.eye_scale_x,
            eye_scale_y=self.eye_scale_y,
            eye_rot_l=self.eye_rot_l,
            eye_rot_r=self.eye_rot_r,
            pupil_ox=self.pupil_ox,
            pupil_oy=self.pupil_oy,
            eyelid_progress=self.eyelid_progress,
            eye_water_alpha=self.eye_water_alpha,
            tear_intensity=self.tear_intensity,
            eye_top_color=self.eye_top_color,
            eye_bot_color=self.eye_bot_color,
            mouth_w=self.mouth_w,
            mouth_h=self.mouth_h,
            mouth_curve=self.mouth_curve,
            mouth_openness=self.mouth_openness,
            mouth_style=self.mouth_style
        )

# --- EMOTION BANK (Preset Target Berdasarkan Jurnal Xpress) ---
EMOTION_BANK = {
    "NEUTRAL": FaceState(
        eye_scale_x=1.0,
        eye_scale_y=1.0,
        eye_rot_l=0.0,
        eye_rot_r=0.0,
        pupil_ox=0.0,
        pupil_oy=0.0,
        eye_water_alpha=0.0,
        tear_intensity=0.0,
        eye_top_color=(80, 70, 150),
        eye_bot_color=(0, 0, 0),
        mouth_w=200.0,
        mouth_h=24.0,
        mouth_curve=0.0,
        mouth_style="neutral"
    ),
    "HAPPY": FaceState(
        eye_scale_x=1.0,
        eye_scale_y=1.0,
        eye_rot_l=0.0,
        eye_rot_r=0.0,
        pupil_ox=0.0,
        pupil_oy=0.0,
        eye_water_alpha=0.0,
        tear_intensity=0.0,
        eye_top_color=(80, 70, 150),
        eye_bot_color=(0, 0, 0),
        mouth_w=320.0,
        mouth_h=140.0,
        mouth_curve=1.0,
        mouth_style="smile"
    ),
    "SHOCK": FaceState(
        eye_scale_x=1.15,
        eye_scale_y=1.15,
        eye_rot_l=0.0,
        eye_rot_r=0.0,
        pupil_ox=0.0,
        pupil_oy=0.0,
        eye_water_alpha=0.0,
        tear_intensity=0.0,
        eye_top_color=(80, 70, 150),
        eye_bot_color=(0, 0, 0),
        mouth_w=220.0,
        mouth_h=160.0,
        mouth_curve=0.0,
        mouth_style="oval"
    ),
    "CRY": FaceState(
        eye_scale_x=1.0,
        eye_scale_y=1.0,
        eye_rot_l=0.0,
        eye_rot_r=0.0,
        pupil_ox=0.0,
        pupil_oy=0.0,
        eye_water_alpha=1.0,
        tear_intensity=1.0,
        eye_top_color=(40, 30, 70),
        eye_bot_color=(40, 30, 70),
        mouth_w=200.0,
        mouth_h=100.0,
        mouth_curve=-1.0,
        mouth_style="sad"
    ),
    "LOAD": FaceState(
        eye_scale_x=1.0,
        eye_scale_y=1.0,
        eye_rot_l=0.0,
        eye_rot_r=10.0,
        pupil_ox=-25.0,
        pupil_oy=-5.0,
        eye_water_alpha=0.0,
        tear_intensity=0.0,
        eye_top_color=(80, 70, 150),
        eye_bot_color=(10, 10, 30),
        mouth_w=220.0,
        mouth_h=110.0,
        mouth_curve=0.0,
        mouth_style="oval"
    )
}
