"""
Widgets
=======
Custom UI widgets for the Vidatron application.
"""

from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Ellipse, Line, Rectangle
from kivy.metrics import dp
from math import sin, pi


class Face(Widget):
    """
    Animated robot face widget.
    Displays eyes and mouth with various moods and expressions.
    """
    
    def __init__(self, **kwargs):
        """Initialize the face widget with animation."""
        super().__init__(**kwargs)
        self.t = 0.0  # Animation time counter
        self.accent = (0.10, 0.90, 1.00, 1.0)  # Accent color (RGBA)
        self.mood = "happy"  # Current mood/expression
        self.selected_eyes = None  # Custom eyes selection (nullable)
        self.selected_mouth = None  # Custom mouth selection (nullable)
        Clock.schedule_interval(self._tick, 1/30)  # 30 FPS animation

    def set_style(self, accent, mood):
        """
        Update face style with accent color and mood.
        
        Args:
            accent: Tuple of (r, g, b, a) values for accent color
            mood: happy, calm, wink, focused, listening, thinking, speaking
        """
        self.accent = accent
        self.mood = mood

    def set_customization(self, eyes=None, mouth=None):
        """
        Set custom eyes and mouth selections.
        
        Args:
            eyes: Optional string identifier for eyes style (nullable)
            mouth: Optional string identifier for mouth style (nullable)
        """
        self.selected_eyes = eyes
        self.selected_mouth = mouth

    def _tick(self, dt):
        """Animation tick - called every frame."""
        self.t += dt
        self._draw()

    def _draw(self):
        """Draw the face with current style and animation state."""
        self.canvas.clear()
        x, y = self.pos
        w, h = self.size

        r, g, b, a = self.accent
        # Pulsing effect for accent color (faster when listening, slower when thinking)
        pulse_base = (self.t % 3.0) / 3.0
        if self.mood == "listening":
            pulse_base = (self.t % 1.6) / 1.6
        elif self.mood == "thinking":
            pulse_base = (self.t % 4.2) / 4.2
        elif self.mood == "speaking":
            pulse_base = (self.t % 0.55) / 0.55
        pulse = 0.55 + 0.45 * sin(2 * pi * pulse_base)

        pad = 16
        cx, cy = x + pad, y + pad
        cw, ch = w - 2*pad, h - 2*pad

        # Base color derived from accent
        base = (0.07 + r*0.70, 0.07 + g*0.70, 0.07 + b*0.70, 1.0)

        # Eye positioning
        eye_y = cy + ch*0.60
        eye_r = min(cw, ch)*0.095
        lx = cx + cw*0.35 - eye_r
        rx = cx + cw*0.65 - eye_r

        # Pupil wandering animation
        wander = 0.10*sin(2*pi*(self.t % 4.5)/4.5)
        pupil_dx = eye_r*(0.18*wander)
        pupil_dy = eye_r*(0.10*sin(2*pi*(self.t % 5.5)/5.5))

        # Mood-based pupil adjustments
        if self.mood == "focused":
            pupil_dx -= eye_r*0.25
        if self.mood == "happy":
            pupil_dx += eye_r*0.08
        if self.mood == "listening":
            listen_sweep = sin(2 * pi * self.t * 2.0)
            pupil_dx += eye_r * 0.38 * listen_sweep
            pupil_dy *= 0.4
        elif self.mood == "thinking":
            pupil_dx += eye_r * 0.1 * sin(2 * pi * self.t * 0.85)
            pupil_dy += eye_r * 0.32
        elif self.mood == "speaking":
            pupil_dy += eye_r * 0.06 * sin(2 * pi * self.t * 6.0)

        # Blink animation
        blink = 0.0
        phase = (self.t % 4.0)
        if 3.82 <= phase <= 4.0:
            p = (phase - 3.82)/0.18
            blink = sin(p*pi)
        if self.mood == "listening":
            blink *= 0.35
        elif self.mood == "thinking":
            blink *= 0.45

        # Wink animation (for wink mood)
        wink = 0.0
        if self.mood == "wink":
            p2 = (self.t % 2.4)
            if 2.05 <= p2 <= 2.4:
                q = (p2 - 2.05)/0.35
                wink = sin(q*pi)

        # Mouth positioning
        mouth_w = cw*0.40
        mouth_h = ch*0.12
        mx = cx + (cw-mouth_w)/2
        my = cy + ch*0.25

        with self.canvas:
            # Background
            Color(0.02, 0.02, 0.04, 1.0)
            RoundedRectangle(pos=(x, y), size=(w, h), radius=[22])

            # Accent glow
            Color(r, g, b, 0.30 + 0.35*pulse)
            RoundedRectangle(pos=(cx-10, cy-10), size=(cw+20, ch+20), radius=[26])

            # Face base
            Color(*base)
            RoundedRectangle(pos=(cx, cy), size=(cw, ch), radius=[26])

            # Face border
            Color(1, 1, 1, 0.18)
            Line(rounded_rectangle=(cx, cy, cw, ch, 26), width=2)

            # Eyes (white sclera) - apply customization
            # Only draw eyes if not None
            if self.selected_eyes is not None:
                eye_scale = 1.0
                eye_offset_y = 0.0
                
                # Apply eye style customization (at least 3 options)
                if self.selected_eyes == "Round":
                    eye_scale = 1.0  # Default round
                elif self.selected_eyes == "Oval":
                    eye_scale = 1.2  # Wider oval
                    eye_offset_y = -eye_r * 0.1
                elif self.selected_eyes == "Narrow":
                    eye_scale = 0.85  # Narrower
                elif self.selected_eyes == "Wide":
                    eye_scale = 1.3  # Very wide
                    eye_offset_y = -eye_r * 0.15
                elif self.selected_eyes == "Big":
                    # Treat "Big" as the same direction as "Wide", but tuned slightly.
                    eye_scale = 1.35
                    eye_offset_y = -eye_r * 0.15
                elif self.selected_eyes == "Small":
                    eye_scale = 0.7  # Smaller eyes
                if self.mood == "listening":
                    eye_scale *= 1.12
                elif self.mood == "thinking":
                    eye_scale *= 0.94

                Color(1, 1, 1, 0.96)
                eye_w = eye_r * 2 * eye_scale
                eye_h = eye_r * 2
                Ellipse(pos=(lx + (eye_r*2 - eye_w)/2, eye_y-eye_r + eye_offset_y), size=(eye_w, eye_h))
                Ellipse(pos=(rx + (eye_r*2 - eye_w)/2, eye_y-eye_r + eye_offset_y), size=(eye_w, eye_h))

                # Pupils
                pr = eye_r*0.35
                Color(0.05, 0.06, 0.08, 1.0)
                Ellipse(pos=(lx+eye_r-pr+pupil_dx, eye_y-pr+pupil_dy), size=(pr*2, pr*2))
                Ellipse(pos=(rx+eye_r-pr+pupil_dx, eye_y-pr+pupil_dy), size=(pr*2, pr*2))

            # Eyelids for blink/wink (only if eyes are drawn)
            if self.selected_eyes is not None and (blink > 0.0 or wink > 0.0):
                Color(*base)
                eh_l = (eye_r*2)*(max(blink, wink)*0.95)
                RoundedRectangle(pos=(lx-2, eye_y-eh_l/2), size=(eye_r*2+4, eh_l), radius=[10])
                if blink > 0.0:
                    eh_r = (eye_r*2)*(blink*0.95)
                    RoundedRectangle(pos=(rx-2, eye_y-eh_r/2), size=(eye_r*2+4, eh_r), radius=[10])

            # Mouth: custom shape (Happy/Sad/Neutral/Shocked)
            # We keep "speaking" as a special animated state; all other moods use the
            # user-selected mouth shape so saved customizations are always visible.
            if self.selected_mouth is not None:
                Color(1, 1, 1, 0.90)
                
                mouth_style = self.selected_mouth
                # New mouth options
                if mouth_style in ("Happy", "Curved", "Smile"):
                    mouth_shape = "Happy"
                elif mouth_style == "Sad":
                    mouth_shape = "Sad"
                elif mouth_style == "Neutral":
                    mouth_shape = "Neutral"
                elif mouth_style == "Shocked":
                    mouth_shape = "Shocked"
                else:
                    # Legacy/compat: map unknown styles to Happy.
                    mouth_shape = "Happy"

                # Width tuning (helps preserve older stored options too)
                if mouth_style == "Wide":
                    mouth_w = cw * 0.50
                elif mouth_style == "Small":
                    mouth_w = cw * 0.30
                elif mouth_style == "Expressive":
                    mouth_w = cw * 0.45
                elif mouth_shape == "Happy":
                    mouth_w = cw * 0.42
                elif mouth_shape == "Sad":
                    mouth_w = cw * 0.42
                elif mouth_shape == "Neutral":
                    mouth_w = cw * 0.38
                elif mouth_shape == "Shocked":
                    mouth_w = cw * 0.36
                else:
                    mouth_w = cw * 0.40
                
                mx = cx + (cw-mouth_w)/2
                
                # speaking animation keeps its dynamic open/close
                if self.mood == "speaking":
                    talk = 0.5 + 0.5 * sin(2 * pi * self.t * 7.5)
                    open_h = mouth_h * (0.2 + 0.45 * talk)
                    ow = mouth_w * (0.35 + 0.12 * talk)
                    Ellipse(pos=(mx + (mouth_w - ow) * 0.5, my + mouth_h * 0.18), size=(ow, open_h))
                else:
                    # Custom static shape (used for listening/thinking/happy/etc)
                    if mouth_shape == "Happy":
                        # U shape (smile)
                        Line(
                            bezier=[
                                mx, my + mouth_h * 0.42,
                                mx + mouth_w * 0.25, my,
                                mx + mouth_w * 0.75, my,
                                mx + mouth_w, my + mouth_h * 0.42,
                            ],
                            width=7,
                            cap="round",
                        )
                    elif mouth_shape == "Sad":
                        # Upside-down U shape (frown)
                        Line(
                            bezier=[
                                mx, my,
                                mx + mouth_w * 0.25, my + mouth_h * 0.42,
                                mx + mouth_w * 0.75, my + mouth_h * 0.42,
                                mx + mouth_w, my,
                            ],
                            width=7,
                            cap="round",
                        )
                    elif mouth_shape == "Neutral":
                        # Flat line
                        Line(
                            points=[mx, my + mouth_h * 0.25, mx + mouth_w, my + mouth_h * 0.25],
                            width=7,
                            cap="round",
                        )
                    elif mouth_shape == "Shocked":
                        # Circle
                        circle_d = max(dp(10), min(mouth_w * 0.35, mouth_h * 2.0))
                        Ellipse(
                            pos=(mx + (mouth_w - circle_d) * 0.5, my + mouth_h * 0.05),
                            size=(circle_d, circle_d),
                        )
                    else:
                        # Fallback: neutral-ish smile
                        Line(
                            bezier=[
                                mx, my + mouth_h * 0.42,
                                mx + mouth_w * 0.25, my,
                                mx + mouth_w * 0.75, my,
                                mx + mouth_w, my + mouth_h * 0.42,
                            ],
                            width=7,
                            cap="round",
                        )

            # Extra motion cues for voice AI states
            if self.mood == "listening" and self.selected_eyes is not None:
                Color(0.72, 0.94, 1.0, 0.4 + 0.35 * sin(2 * pi * self.t * 2.5))
                bx = cx + cw * 0.74
                by = cy + ch * 0.46
                for i in range(3):
                    amp = 0.3 + 0.7 * sin(2 * pi * self.t * 2.3 - i * 0.55)
                    Line(
                        points=[bx + i * dp(6), by, bx + i * dp(6) + dp(16) * amp, by - dp(4) - i * dp(3)],
                        width=max(1.5, dp(2)),
                        cap="round",
                    )
            elif self.mood == "thinking" and self.selected_eyes is not None:
                Color(1, 1, 1, 0.4)
                ty = cy + ch * 0.82
                for i in range(3):
                    bob = dp(3) * sin(2 * pi * self.t * 1.15 - i * 0.9)
                    Ellipse(
                        pos=(cx + cw * (0.2 + i * 0.11) + bob, ty + i * dp(5)),
                        size=(dp(5 + i), dp(5 + i)),
                    )


class StickFigureIcon(Widget):
    """
    Kivy-drawn stick figure icon representing an action (e.g. drink, stretch).
    Uses the same colored background as the Face (accent-derived) so the area is not black.
    """
    def __init__(self, action="stretch", accent=(0.10, 0.90, 1.00, 1.0), **kwargs):
        super().__init__(**kwargs)
        self._action = action
        self._accent = accent if isinstance(accent, (tuple, list)) and len(accent) >= 4 else (0.10, 0.90, 1.00, 1.0)
        self.t = 0.0
        self.bind(size=self._draw, pos=self._draw)
        Clock.schedule_interval(self._tick, 1 / 30.0)

    def _tick(self, dt):
        self.t += dt
        self._draw()

    @property
    def action(self):
        return self._action

    @action.setter
    def action(self, value):
        if value != self._action:
            self._action = value
            self._draw()

    @property
    def accent(self):
        return self._accent

    @accent.setter
    def accent(self, value):
        if value != self._accent:
            self._accent = value if isinstance(value, (tuple, list)) and len(value) >= 4 else (0.10, 0.90, 1.00, 1.0)
            self._draw()

    def _draw(self, *args):
        self.canvas.clear()
        x, y = self.pos
        w, h = self.size
        if w <= 0 or h <= 0:
            return
        r, g, b, a = self._accent
        pad = 16
        cx, cy = x + pad, y + pad
        cw, ch = w - 2 * pad, h - 2 * pad
        base = (0.07 + r * 0.70, 0.07 + g * 0.70, 0.07 + b * 0.70, 1.0)
        pulse = 0.55 + 0.45 * sin(2 * pi * (self.t % 2.2) / 2.2)
        shimmer = 0.45 + 0.55 * sin(2 * pi * (self.t % 1.6) / 1.6)
        # Same background as Face so it's a color, not black
        with self.canvas:
            Color(0.02, 0.02, 0.04, 1.0)
            RoundedRectangle(pos=(x, y), size=(w, h), radius=[22])
            Color(r, g, b, 0.35 + 0.40 * pulse)
            RoundedRectangle(pos=(cx - 10, cy - 10), size=(cw + 20, ch + 20), radius=[26])
            Color(1, 1, 1, 0.05 + 0.09 * shimmer)
            RoundedRectangle(pos=(cx + cw * 0.06, cy + ch * 0.62), size=(cw * 0.88, ch * 0.26), radius=[18])
            Color(*base)
            RoundedRectangle(pos=(cx, cy), size=(cw, ch), radius=[26])
            Color(1, 1, 1, 0.18)
            Line(rounded_rectangle=(cx, cy, cw, ch, 26), width=2)
        # Stick figure on top
        def px(nx, ny):
            return (x + nx * w, y + ny * h)
        line_w = max(2, dp(4))
        if self._action == "drink":
            self._draw_drink(px, w, h, line_w)
        elif self._action == "exercise":
            self._draw_exercise(px, w, h, line_w)
        else:
            self._draw_stretch(px, w, h, line_w)

    def _draw_drink(self, px, w, h, line_w):
        """Stick figure drinking — cup tilts to mouth, swallow bob, water stream."""
        bob = 0.022 * sin(2 * pi * (self.t % 1.6) / 1.6)
        sip = 0.05 * sin(2 * pi * (self.t % 1.0) / 1.0)
        head_tilt = 0.04 * max(0, sin(2 * pi * (self.t % 1.0) / 1.0))
        cx, cy = 0.5, 0.52 + bob
        head_r = 0.085
        # Head (slight lean toward cup when sipping)
        self.canvas.add(Color(1, 1, 1, 0.95))
        self.canvas.add(Ellipse(pos=px(cx - head_r + head_tilt, cy + 0.26 - head_r), size=(2*head_r*w, 2*head_r*h)))
        # Body
        self.canvas.add(Line(points=px(cx, cy + 0.18) + px(cx, cy - 0.10), width=line_w, cap="round"))
        # Drinking arm + large cup/bottle
        self.canvas.add(Line(points=px(cx, cy + 0.12) + px(cx + 0.10, cy + 0.16 + sip * 0.5) + px(cx + 0.16, cy + 0.20 + sip), width=line_w, cap="round"))
        cup_w, cup_h = 0.055 * w, 0.11 * h
        cup_x, cup_y = px(cx + 0.11, cy + 0.14 + sip)
        self.canvas.add(Color(0.92, 0.96, 1.0, 0.92))
        self.canvas.add(RoundedRectangle(pos=(cup_x, cup_y), size=(cup_w, cup_h), radius=[4]))
        self.canvas.add(Color(0.45, 0.78, 1.0, 0.85))
        self.canvas.add(Rectangle(pos=(cup_x + cup_w * 0.15, cup_y + cup_h * 0.25), size=(cup_w * 0.7, cup_h * 0.45)))
        # Water stream into mouth when sipping high
        if sip > 0.02:
            self.canvas.add(Color(0.6, 0.9, 1.0, 0.7))
            sx, sy = px(cx + 0.08, cy + 0.22)
            ex, ey = px(cx + 0.02, cy + 0.26)
            self.canvas.add(Line(points=[sx, sy, ex, ey], width=max(1.5, line_w * 0.5), cap="round"))
        # Droplets
        self.canvas.add(Color(0.75, 0.95, 1.0, 0.7))
        drip_y = 0.1 * sin(2 * pi * (self.t % 0.65) / 0.65)
        self.canvas.add(Ellipse(pos=px(cx + 0.22, cy + 0.12 + drip_y), size=(0.014 * w, 0.022 * h)))
        self.canvas.add(Ellipse(pos=px(cx + 0.26, cy + 0.10 - drip_y), size=(0.011 * w, 0.018 * h)))
        # Free arm
        self.canvas.add(Color(1, 1, 1, 0.95))
        self.canvas.add(Line(points=px(cx, cy + 0.12) + px(cx - 0.09, cy - 0.02), width=line_w, cap="round"))
        # Legs
        self.canvas.add(Line(points=px(cx, cy - 0.10) + px(cx - 0.09, cy - 0.36), width=line_w, cap="round"))
        self.canvas.add(Line(points=px(cx, cy - 0.10) + px(cx + 0.09, cy - 0.36), width=line_w, cap="round"))

    def _draw_stretch(self, px, w, h, line_w):
        """Side reach stretch — torso side-bends, arm reaches up and across, big arc sweep."""
        phase = 2 * pi * (self.t % 2.0) / 2.0
        sway = 0.045 * sin(phase)
        reach = 0.08 * (0.5 + 0.5 * sin(phase))
        bend = 0.04 * sin(phase + 0.4)
        cx, cy = 0.48 + sway * 0.3, 0.52 + bend
        head_r = 0.082
        self.canvas.add(Color(1, 1, 1, 0.95))
        self.canvas.add(Ellipse(pos=px(cx - head_r + bend, cy + 0.24 - head_r), size=(2*head_r*w, 2*head_r*h)))
        # Torso: lean and bend
        self.canvas.add(Line(points=px(cx, cy + 0.16) + px(cx - 0.05 - bend, cy + 0.04), width=line_w, cap="round"))
        self.canvas.add(Line(points=px(cx - 0.05 - bend, cy + 0.04) + px(cx - 0.02, cy - 0.12), width=line_w, cap="round"))
        # Reaching arm — long sweep overhead
        ax = 0.18 + reach
        ay = 0.26 + reach * 0.4
        self.canvas.add(Line(points=px(cx, cy + 0.14) + px(cx + 0.06, cy + 0.22 + sway) + px(cx + ax, cy + ay), width=line_w, cap="round"))
        # Supporting arm
        self.canvas.add(Line(points=px(cx - 0.05 - bend, cy + 0.04) + px(cx - 0.17, cy - 0.06), width=line_w, cap="round"))
        # Legs (wide stance for balance)
        self.canvas.add(Line(points=px(cx - 0.02, cy - 0.12) + px(cx - 0.12, cy - 0.38), width=line_w, cap="round"))
        self.canvas.add(Line(points=px(cx - 0.02, cy - 0.12) + px(cx + 0.12, cy - 0.36), width=line_w, cap="round"))
        # Motion arc — follows reach
        self.canvas.add(Color(1, 1, 1, 0.22 + 0.12 * sin(phase)))
        arc_x, arc_y = px(cx + 0.08, cy + 0.22)
        self.canvas.add(Line(circle=(arc_x, arc_y, (0.11 + reach * 0.8) * w, 5, 125), width=max(1.2, line_w * 0.5)))

    def _draw_exercise(self, px, w, h, line_w):
        """Jumping-jack style motion — legs and arms open/close in sync."""
        T = 0.85
        ph = 2 * pi * (self.t % T) / T
        # 0 = closed, 1 = open
        open_amt = 0.5 * (1.0 + sin(ph))
        cx, cy = 0.5, 0.48 + 0.015 * sin(ph * 2)
        head_r = 0.08
        self.canvas.add(Color(1, 1, 1, 0.95))
        self.canvas.add(Ellipse(pos=px(cx - head_r, cy + 0.26 - head_r), size=(2 * head_r * w, 2 * head_r * h)))
        # Body
        self.canvas.add(Line(points=px(cx, cy + 0.18) + px(cx, cy - 0.08), width=line_w, cap="round"))
        # Arms: down at sides -> up diagonal when open
        arm_spread = 0.16 * open_amt
        self.canvas.add(
            Line(
                points=px(cx, cy + 0.12)
                + px(cx - 0.06 - arm_spread * 0.5, cy + 0.06 - arm_spread * 0.3)
                + px(cx - 0.12 - arm_spread, cy - 0.02 - arm_spread * 0.5),
                width=line_w,
                cap="round",
            )
        )
        self.canvas.add(
            Line(
                points=px(cx, cy + 0.12)
                + px(cx + 0.06 + arm_spread * 0.5, cy + 0.06 - arm_spread * 0.3)
                + px(cx + 0.12 + arm_spread, cy - 0.02 - arm_spread * 0.5),
                width=line_w,
                cap="round",
            )
        )
        # Legs: together -> apart
        leg_spread = 0.11 * open_amt
        self.canvas.add(Line(points=px(cx, cy - 0.08) + px(cx - leg_spread, cy - 0.36), width=line_w, cap="round"))
        self.canvas.add(Line(points=px(cx, cy - 0.08) + px(cx + leg_spread, cy - 0.36), width=line_w, cap="round"))
        # Pulse ring when open
        if open_amt > 0.6:
            bx, by = px(cx, cy + 0.06)
            rr = (0.10 + 0.06 * open_amt) * w
            self.canvas.add(Color(1, 1, 1, 0.18 * open_amt))
            self.canvas.add(Line(ellipse=(bx - rr, by - rr * 0.9, 2 * rr, 1.8 * rr), width=1.8))
