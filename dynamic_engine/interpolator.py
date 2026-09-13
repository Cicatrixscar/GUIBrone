# -*- coding: utf-8 -*-
"""
BRONE Dynamic Engine - Interpolator & Motion Controller
======================================================
Menghitung transisi halus antar parameter wajah (lerp/easing) berdasarkan Delta Time (dt),
mengatur sistem kedip natural FSM, serta modulasi artikulasi bicara (talking state).
"""

import math
import random
from .state import FaceState, EMOTION_BANK

def lerp(a: float, b: float, factor: float) -> float:
    return a + (b - a) * factor

def lerp_color(c1: tuple, c2: tuple, factor: float) -> tuple:
    return (
        int(lerp(c1[0], c2[0], factor)),
        int(lerp(c1[1], c2[1], factor)),
        int(lerp(c1[2], c2[2], factor)),
    )

class FaceInterpolator:
    def __init__(self):
        # Mode: "DYNAMIC" (transisi halus 300-500ms) atau "STATIC" (transisi instan)
        self.mode = "DYNAMIC"
        
        # State aktif dan state target
        self.current_emotion = "NEUTRAL"
        self.target_emotion = "NEUTRAL"
        self.current = EMOTION_BANK["NEUTRAL"].copy()
        self.target = EMOTION_BANK["NEUTRAL"].copy()
        
        # Kecepatan transisi dinamis (damping factor)
        self.dynamic_speed = 8.0  # Menghasilkan transisi halus ~300ms
        
        # FSM Kedip (Blink Controller)
        self.blink_state = "idle" # "closing", "opening", "idle"
        self.blink_progress = 0.0
        self.blink_speed = 6.0    # Kecepatan kedip per detik (real-time)
        self.blink_timer = random.uniform(2.0, 5.0)
        
        # Fitur Bicara (Talking State Controller)
        self.is_talking = False
        self.talking_time = 0.0
        self.talking_speed = 14.0  # Frekuensi osilasi buka-tutup rahang
        
        # Debug / Info
        self.transition_progress = 1.0

    def toggle_mode(self):
        self.mode = "STATIC" if self.mode == "DYNAMIC" else "DYNAMIC"
        return self.mode

    def toggle_talking(self):
        self.is_talking = not self.is_talking
        return self.is_talking

    def set_emotion(self, emotion_name: str):
        if emotion_name in EMOTION_BANK:
            self.target_emotion = emotion_name
            self.target = EMOTION_BANK[emotion_name].copy()
            
            # Jika dalam Mode Statis, langsung kunci parameter seketika (snap)
            if self.mode == "STATIC":
                self.current = self.target.copy()
                self.current_emotion = emotion_name
                self.transition_progress = 1.0

    def update(self, dt: float):
        # --- 1. PROSES KEDIP NATURAL (Blink FSM berbasis dt) ---
        if self.blink_state == "closing":
            self.blink_progress += self.blink_speed * dt
            if self.blink_progress >= 1.0:
                self.blink_progress = 1.0
                self.blink_state = "opening"
        elif self.blink_state == "opening":
            self.blink_progress -= self.blink_speed * dt
            if self.blink_progress <= 0.0:
                self.blink_progress = 0.0
                self.blink_state = "idle"
                self.blink_timer = random.uniform(2.0, 5.5)
        elif self.blink_state == "idle":
            self.blink_timer -= dt
            if self.blink_timer <= 0:
                self.blink_state = "closing"

        # --- 2. PROSES ARTIKULASI BICARA (Talking Viseme) ---
        if self.is_talking:
            self.talking_time += dt * self.talking_speed
            # Gelombang sinus buka-tutup mulut natural (rentang 0.1 s/d 1.0)
            talking_wave = (math.sin(self.talking_time) + 1.0) * 0.5
            target_openness = 0.1 + talking_wave * 0.9
        else:
            target_openness = 0.0
            self.talking_time = 0.0

        # --- 3. PROSES INTERPOLASI (Mode Dinamis vs Mode Statis) ---
        if self.mode == "DYNAMIC":
            # Exponential smoothing independent dari frame rate
            factor = 1.0 - math.exp(-self.dynamic_speed * dt)
            
            self.current.eye_scale_x = lerp(self.current.eye_scale_x, self.target.eye_scale_x, factor)
            self.current.eye_scale_y = lerp(self.current.eye_scale_y, self.target.eye_scale_y, factor)
            self.current.eye_rot_l   = lerp(self.current.eye_rot_l, self.target.eye_rot_l, factor)
            self.current.eye_rot_r   = lerp(self.current.eye_rot_r, self.target.eye_rot_r, factor)
            self.current.pupil_ox    = lerp(self.current.pupil_ox, self.target.pupil_ox, factor)
            self.current.pupil_oy    = lerp(self.current.pupil_oy, self.target.pupil_oy, factor)
            
            self.current.eye_water_alpha = lerp(self.current.eye_water_alpha, self.target.eye_water_alpha, factor)
            self.current.tear_intensity  = lerp(self.current.tear_intensity, self.target.tear_intensity, factor)
            
            self.current.eye_top_color = lerp_color(self.current.eye_top_color, self.target.eye_top_color, factor)
            self.current.eye_bot_color = lerp_color(self.current.eye_bot_color, self.target.eye_bot_color, factor)
            
            self.current.mouth_w     = lerp(self.current.mouth_w, self.target.mouth_w, factor)
            self.current.mouth_h     = lerp(self.current.mouth_h, self.target.mouth_h, factor)
            self.current.mouth_curve = lerp(self.current.mouth_curve, self.target.mouth_curve, factor)
            self.current.mouth_openness = lerp(self.current.mouth_openness, target_openness, factor * 2.0)
            
            # Ganti gaya mulut jika sudah mendekati target
            if factor > 0.5:
                self.current.mouth_style = self.target.mouth_style
                self.current_emotion = self.target_emotion
        else:
            # MODE STATIS: Kunci nilai seketika (Zero Transition Delay)
            self.current = self.target.copy()
            self.current.mouth_openness = target_openness
            self.current_emotion = self.target_emotion

        # Kelopak mata selalu mengikuti progress kedip
        self.current.eyelid_progress = self.blink_progress
        return self.current
