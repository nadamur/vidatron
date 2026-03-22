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
        # Assistant interaction: idle | thinking | listening | talking
        self.interaction_state = "idle"
        # Softer, friendlier look on homescreen idle (cheeks, bigger smile)
        self.cute_default = False
        Clock.schedule_interval(self._tick, 1/30)  # 30 FPS animation

    def set_cute_default(self, active):
        """When True (homescreen idle), draw a warmer, cuter friendly face."""
        self.cute_default = bool(active)

    def set_interaction_state(self, state):
        """idle, thinking, listening, or talking — overrides idle expression until cleared."""
        if state not in ("idle", "thinking", "listening", "talking"):
            state = "idle"
        self.interaction_state = state

    def set_style(self, accent, mood):
        """
        Update face style with accent color and mood.
        
        Args:
            accent: Tuple of (r, g, b, a) values for accent color
            mood: String mood identifier (happy, calm, wink, focused)
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
        # Pulsing effect for accent color (gentler when cute_default)
        pulse_period = 4.2 if self.cute_default else 3.0
        pulse = 0.55 + 0.45*sin(2*pi*(self.t % pulse_period)/pulse_period)

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

        # Mood-based pupil adjustments (idle only; interaction states override below)
        if self.interaction_state == "idle":
            if self.mood == "focused":
                pupil_dx -= eye_r*0.25
            if self.mood == "happy":
                pupil_dx += eye_r*0.08
            if self.cute_default:
                pupil_dy += eye_r*0.06*sin(2*pi*(self.t % 5.0)/5.0)

        # Interaction-state pupil / attention
        if self.interaction_state == "thinking":
            pupil_dx += eye_r * 0.12 * sin(2 * pi * (self.t % 5.0) / 5.0)
            pupil_dy += eye_r * 0.42
        elif self.interaction_state == "listening":
            pupil_dx += eye_r * 0.18 * sin(2 * pi * (self.t % 2.8) / 2.8)
            pupil_dy -= eye_r * 0.06
        elif self.interaction_state == "talking":
            pupil_dy -= eye_r * 0.05

        # Blink animation
        blink = 0.0
        phase = (self.t % 4.0)
        if 3.82 <= phase <= 4.0:
            p = (phase - 3.82)/0.18
            blink = sin(p*pi)

        # Wink animation (for wink mood); disabled during listening/talking for clarity
        wink = 0.0
        if self.mood == "wink" and self.interaction_state == "idle":
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
            glow_a = 0.30 + 0.35 * pulse
            if self.cute_default and self.interaction_state == "idle":
                glow_a = 0.34 + 0.28 * pulse
            if self.interaction_state == "listening":
                glow_a = 0.45 + 0.35 * sin(2 * pi * (self.t % 1.6) / 1.6)
            Color(r, g, b, glow_a)
            RoundedRectangle(pos=(cx-10, cy-10), size=(cw+20, ch+20), radius=[26])

            # Face base
            Color(*base)
            RoundedRectangle(pos=(cx, cy), size=(cw, ch), radius=[26])

            # Face border
            Color(1, 1, 1, 0.22 if self.cute_default else 0.18)
            Line(rounded_rectangle=(cx, cy, cw, ch, 26), width=2)

            # Rosy cheeks when idle + cute homescreen look
            if self.cute_default and self.interaction_state == "idle":
                cheek_r = min(cw, ch) * 0.065
                bob = 0.92 + 0.08 * sin(2 * pi * (self.t % 3.3) / 3.3)
                Color(1.0, 0.55, 0.62, 0.22 * bob)
                Ellipse(pos=(cx + cw * 0.12 - cheek_r, cy + ch * 0.38 - cheek_r), size=(cheek_r * 2, cheek_r * 2))
                Ellipse(pos=(cx + cw * 0.78 - cheek_r, cy + ch * 0.38 - cheek_r), size=(cheek_r * 2, cheek_r * 2))

            # Thinking: soft thought dots above head
            if self.interaction_state == "thinking":
                for i, phase in enumerate((0.0, 0.45, 0.9)):
                    bob = 0.5 + 0.5 * sin(2 * pi * ((self.t + phase) % 2.2) / 2.2)
                    bx = cx + cw * (0.62 + i * 0.07)
                    by = cy + ch * (0.88 + 0.06 * bob)
                    br = dp(4 + i * 2) * bob
                    Color(1, 1, 1, 0.35 + 0.25 * bob)
                    Ellipse(pos=(bx - br, by - br), size=(br * 2, br * 2))

            # Listening: sound arcs toward the face
            if self.interaction_state == "listening":
                wave = 0.5 + 0.5 * sin(2 * pi * (self.t % 1.2) / 1.2)
                Color(1, 1, 1, 0.22 + 0.2 * wave)
                ax = cx - cw * 0.02
                ay = cy + ch * 0.55
                for k, scale in enumerate((0.85, 1.0, 1.15)):
                    rk = (0.12 + k * 0.05) * cw * scale
                    Line(
                        points=[
                            ax - rk * 0.2, ay,
                            ax - rk * 0.5, ay + rk * 0.35,
                            ax - rk * 0.85, ay,
                        ],
                        width=2 + k,
                        cap="round",
                    )

            # Eyes (white sclera) - apply customization
            # Only draw eyes if not None
            if self.selected_eyes is not None:
                eye_scale = 1.0
                eye_offset_y = 0.0
                if self.interaction_state == "listening":
                    eye_scale = 1.12
                    eye_offset_y = -eye_r * 0.06
                elif self.interaction_state == "thinking":
                    eye_scale = 1.05

                # Apply eye style customization (at least 3 options)
                if self.selected_eyes == "Round":
                    pass  # base scale
                elif self.selected_eyes == "Oval":
                    eye_scale *= 1.2
                    eye_offset_y -= eye_r * 0.1
                elif self.selected_eyes == "Narrow":
                    eye_scale *= 0.85
                elif self.selected_eyes == "Wide":
                    eye_scale *= 1.3
                    eye_offset_y -= eye_r * 0.15
                elif self.selected_eyes == "Small":
                    eye_scale *= 0.7

                if self.cute_default and self.interaction_state == "idle":
                    eye_scale *= 1.08
                    eye_offset_y -= eye_r * 0.04

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

                if self.cute_default and self.interaction_state == "idle":
                    sp = pr * 0.35
                    Color(1, 1, 1, 0.85)
                    Ellipse(
                        pos=(lx + eye_r - pr * 1.1 + pupil_dx, eye_y - pr * 1.05 + pupil_dy),
                        size=(sp, sp),
                    )
                    Ellipse(
                        pos=(rx + eye_r - pr * 1.1 + pupil_dx, eye_y - pr * 1.05 + pupil_dy),
                        size=(sp, sp),
                    )

            # Eyelids for blink/wink (only if eyes are drawn)
            if self.selected_eyes is not None and (blink > 0.0 or wink > 0.0):
                Color(*base)
                eh_l = (eye_r*2)*(max(blink, wink)*0.95)
                RoundedRectangle(pos=(lx-2, eye_y-eh_l/2), size=(eye_r*2+4, eh_l), radius=[10])
                if blink > 0.0:
                    eh_r = (eye_r*2)*(blink*0.95)
                    RoundedRectangle(pos=(rx-2, eye_y-eh_r/2), size=(eye_r*2+4, eh_r), radius=[10])

            # Mouth (varies by mood, customization, and talking state)
            # Only draw mouth if not None
            if self.selected_mouth is not None:
                Color(1, 1, 1, 0.90)
                
                # Apply mouth style customization if set (at least 3 options)
                mouth_style = self.selected_mouth
                
                if mouth_style == "Wide":
                    mouth_w = cw * 0.50  # Wider mouth
                elif mouth_style == "Small":
                    mouth_w = cw * 0.30  # Smaller mouth
                elif mouth_style == "Expressive":
                    mouth_w = cw * 0.45  # Slightly wider
                elif mouth_style == "Neutral":
                    mouth_w = cw * 0.35  # Neutral size
                elif mouth_style in ("Curved", "Smile"):
                    mouth_w = cw * 0.42  # Curved / smile style
                else:
                    mouth_w = cw * 0.40  # Default (Round or unknown)

                if self.cute_default and self.interaction_state == "idle" and self.mood in ("happy", "wink"):
                    mouth_w *= 1.14
                    mouth_h *= 1.12

                mx = cx + (cw-mouth_w)/2

                if self.interaction_state == "talking":
                    # Animated speaking mouth (open amount follows a smooth wave)
                    talk = 0.35 + 0.65 * abs(sin(2 * pi * (self.t % 0.35) / 0.35))
                    ow = mouth_w * 0.38
                    oh = max(dp(6), mouth_h * 1.1 * talk)
                    ox = mx + (mouth_w - ow) / 2
                    oy = my + mouth_h * 0.15 - oh * 0.35
                    Color(0.12, 0.12, 0.16, 1.0)
                    Ellipse(pos=(ox, oy), size=(ow, oh))
                    Color(1, 1, 1, 0.92)
                    Line(ellipse=(ox, oy, ow, oh), width=3)
                elif self.interaction_state == "thinking":
                    # Small pondering curve
                    Line(
                        bezier=[
                            mx,
                            my + mouth_h * 0.35,
                            mx + mouth_w * 0.35,
                            my + mouth_h * 0.12,
                            mx + mouth_w,
                            my + mouth_h * 0.38,
                        ],
                        width=6,
                        cap="round",
                    )
                else:
                    # Draw mouth based on mood (or use default if no customization)
                    if self.mood in ("happy", "wink"):
                        # Smile (slightly thicker curve when cute_default)
                        mw = 8 if self.cute_default else 7
                        dip = 0.02 * sin(2 * pi * (self.t % 4.0) / 4.0) if self.cute_default else 0.0
                        Line(
                            bezier=[
                                mx,
                                my + mouth_h * (0.42 + dip),
                                mx + mouth_w * 0.25,
                                my - mouth_h * 0.02,
                                mx + mouth_w * 0.75,
                                my - mouth_h * 0.02,
                                mx + mouth_w,
                                my + mouth_h * (0.42 + dip),
                            ],
                            width=mw,
                            cap="round",
                        )
                    elif self.mood == "calm":
                        # Neutral line
                        Line(points=[mx, my+mouth_h*0.25, mx+mouth_w, my+mouth_h*0.25], width=7, cap="round")
                    else:
                        # Focused (slight curve)
                        Line(points=[mx+mouth_w*0.10, my+mouth_h*0.28, mx+mouth_w*0.92, my+mouth_h*0.34], width=7, cap="round")


class StickFigureIcon(Widget):
    """
    Kivy-drawn stick figure icon representing an action (e.g. drink, stretch, move).
    Uses a bright accent-filled panel so each reminder type reads clearly at a glance.
    """
    def __init__(self, action="stretch", accent=(0.10, 0.90, 1.00, 1.0), **kwargs):
        super().__init__(**kwargs)
        self._action = action
        self._accent = accent if isinstance(accent, (tuple, list)) and len(accent) >= 4 else (0.10, 0.90, 1.00, 1.0)
        self._t = 0.0
        Clock.schedule_interval(self._tick_icon, 1 / 30)
        self.bind(size=self._draw, pos=self._draw)

    def _tick_icon(self, dt):
        self._t += dt
        if self._action in ("move", "drink", "stretch"):
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
        # Saturated outer frame (bright reminder backdrop)
        bright_outer = (min(1.0, r * 0.92 + 0.08), min(1.0, g * 0.92 + 0.08), min(1.0, b * 0.92 + 0.08), 1.0)
        inner_tint = (
            0.12 + r * 0.55,
            0.12 + g * 0.55,
            0.12 + b * 0.55,
            1.0,
        )
        breathe = 0.88 + 0.12 * sin(2 * pi * (self._t % 3.4) / 3.4)
        with self.canvas:
            Color(*bright_outer)
            RoundedRectangle(pos=(x, y), size=(w, h), radius=[22])
            Color(r, g, b, 0.55 + 0.28 * breathe)
            RoundedRectangle(pos=(cx - 10, cy - 10), size=(cw + 20, ch + 20), radius=[26])
            Color(inner_tint[0], inner_tint[1], inner_tint[2], min(1.0, inner_tint[3] * (0.92 + 0.08 * breathe)))
            RoundedRectangle(pos=(cx, cy), size=(cw, ch), radius=[26])
            Color(1, 1, 1, 0.26 + 0.08 * breathe)
            Line(rounded_rectangle=(cx, cy, cw, ch, 26), width=2)
        # Stick figure on top
        def px(nx, ny):
            return (x + nx * w, y + ny * h)
        line_w = max(2, dp(4))
        if self._action == "drink":
            self._draw_drink(px, w, h, line_w)
        elif self._action == "move":
            self._draw_move(px, w, h, line_w)
        else:
            self._draw_stretch(px, w, h, line_w)

    def _draw_drink(self, px, w, h, line_w):
        """Animated sip: cup travels to mouth, slight head tilt, gentle sway."""
        u = 0.5 + 0.5 * sin(2 * pi * (self._t % 2.4) / 2.4)
        sway = 0.012 * sin(2 * pi * (self._t % 1.7) / 1.7)
        cx, cy = 0.5 + sway, 0.5
        head_r = 0.08
        # Head (nudges toward cup as it rises)
        self.canvas.add(Color(1, 1, 1, 0.95))
        self.canvas.add(
            Ellipse(
                pos=px(cx - head_r + 0.02 * u, cy + 0.28 - head_r + 0.015 * u),
                size=(2 * head_r * w, 2 * head_r * h),
            )
        )
        # Tiny sip arc at mouth (optional motion line)
        self.canvas.add(Color(1, 1, 1, 0.18 * u))
        mx_mouth, my_mouth = px(cx + 0.07 + 0.01 * u, cy + 0.26 + 0.02 * u)
        self.canvas.add(
            Line(
                points=[mx_mouth, my_mouth, mx_mouth + 0.02 * w, my_mouth + 0.015 * h],
                width=max(1, line_w - 1),
                cap="round",
            )
        )

        self.canvas.add(Color(1, 1, 1, 0.95))
        # Body
        self.canvas.add(Line(points=px(cx, cy + 0.20) + px(cx, cy - 0.12), width=line_w, cap="round"))
        # Drinking arm: shoulder -> animated elbow -> hand/cup height tracks u
        sx, sy = cx, cy + 0.14
        ex = cx + 0.14 - 0.10 * u
        ey = cy + 0.06 + 0.16 * u
        hx = cx + 0.05 + 0.03 * (1 - u)
        hy = cy + 0.10 + 0.18 * u
        self.canvas.add(Line(points=px(sx, sy) + px(ex, ey) + px(hx, hy), width=line_w, cap="round"))
        # Cup at hand (tilts slightly when drinking)
        cup_w = (0.05 + 0.015 * u) * w
        cup_h = (0.065 + 0.02 * u) * h
        cup_x, cup_y = px(hx - 0.02, hy - 0.02)
        self.canvas.add(Color(0.92, 0.96, 1.0, 0.95))
        self.canvas.add(Rectangle(pos=(cup_x, cup_y), size=(cup_w, cup_h)))
        self.canvas.add(Color(1, 1, 1, 0.95))
        self.canvas.add(Line(rectangle=(cup_x, cup_y, cup_w, cup_h), width=2))
        # Other arm (relaxed sway)
        sway_arm = 0.025 * sin(2 * pi * (self._t % 2.0) / 2.0)
        self.canvas.add(
            Line(
                points=px(sx, sy) + px(cx - 0.09, cy - 0.02 + sway_arm) + px(cx - 0.11, cy - 0.12),
                width=line_w,
                cap="round",
            )
        )
        # Legs (subtle weight shift)
        shift = 0.02 * sin(2 * pi * (self._t % 3.1) / 3.1)
        self.canvas.add(
            Line(
                points=px(cx, cy - 0.12) + px(cx - 0.10 + shift, cy - 0.38),
                width=line_w,
                cap="round",
            )
        )
        self.canvas.add(
            Line(
                points=px(cx, cy - 0.12) + px(cx + 0.10 - shift, cy - 0.38),
                width=line_w,
                cap="round",
            )
        )

    def _draw_move(self, px, w, h, line_w):
        """Walking / movement pose with subtle stride animation."""
        phase = sin(2 * pi * (self._t % 0.9) / 0.9)
        cx, cy = 0.5, 0.5
        head_r = 0.08
        lean = 0.04 * phase
        self.canvas.add(Color(1, 1, 1, 0.95))
        self.canvas.add(
            Ellipse(
                pos=px(cx - head_r + lean * 0.3, cy + 0.24 - head_r),
                size=(2 * head_r * w, 2 * head_r * h),
            )
        )
        # Torso
        self.canvas.add(
            Line(
                points=px(cx + lean * 0.2, cy + 0.16) + px(cx + lean, cy - 0.10),
                width=line_w,
                cap="round",
            )
        )
        # Arms swing
        arm_s = 0.06 * phase
        self.canvas.add(
            Line(
                points=px(cx + lean * 0.2, cy + 0.12)
                + px(cx - 0.10 - arm_s, cy + 0.02)
                + px(cx - 0.14 - arm_s, cy - 0.08),
                width=line_w,
                cap="round",
            )
        )
        self.canvas.add(
            Line(
                points=px(cx + lean * 0.2, cy + 0.12)
                + px(cx + 0.12 + arm_s, cy + 0.04)
                + px(cx + 0.16 + arm_s, cy - 0.06),
                width=line_w,
                cap="round",
            )
        )
        # Legs stepping
        leg = 0.05 * phase
        self.canvas.add(
            Line(
                points=px(cx + lean, cy - 0.10)
                + px(cx - 0.08 - leg, cy - 0.22)
                + px(cx - 0.12 - leg, cy - 0.36),
                width=line_w,
                cap="round",
            )
        )
        self.canvas.add(
            Line(
                points=px(cx + lean, cy - 0.10)
                + px(cx + 0.10 + leg, cy - 0.24)
                + px(cx + 0.14 + leg, cy - 0.38),
                width=line_w,
                cap="round",
            )
        )

    def _draw_stretch(self, px, w, h, line_w):
        """Side reach cycles up/down; torso leans; alternates lead side over time."""
        phase = 2 * pi * (self._t % 5.5) / 5.5
        reach = 0.55 + 0.45 * sin(phase)
        lean = 0.08 * sin(phase * 1.3)
        side = 1.0 if int(self._t // 2.75) % 2 == 0 else -1.0
        cx, cy = 0.5 + 0.015 * sin(phase * 2), 0.5
        head_r = 0.08
        bx = cx - 0.06 * side * reach
        by = cy + 0.02 + 0.02 * sin(phase * 2)

        self.canvas.add(Color(1, 1, 1, 0.95))
        self.canvas.add(
            Ellipse(
                pos=px(cx - head_r + lean * w * 0.05, cy + 0.22 - head_r + 0.03 * reach * h / h),
                size=(2 * head_r * w, 2 * head_r * h),
            )
        )
        # Torso: upper + lower with animated bend
        self.canvas.add(
            Line(
                points=px(cx, cy + 0.14) + px(bx, by),
                width=line_w,
                cap="round",
            )
        )
        self.canvas.add(
            Line(
                points=px(bx, by) + px(cx - 0.04 * side * reach, cy - 0.14 - 0.02 * reach),
                width=line_w,
                cap="round",
            )
        )
        # Stretching arm: reaches up and lengthens with reach
        tip_x = cx + side * (0.10 + 0.12 * reach)
        tip_y = cy + 0.18 + 0.14 * reach
        self.canvas.add(
            Line(
                points=px(cx, cy + 0.14) + px(cx + side * 0.04, cy + 0.20 + 0.04 * reach) + px(tip_x, tip_y),
                width=line_w,
                cap="round",
            )
        )
        # Supporting arm
        self.canvas.add(
            Line(
                points=px(bx, by) + px(cx - side * 0.16, cy - 0.01) + px(cx - side * 0.19, cy - 0.10),
                width=line_w,
                cap="round",
            )
        )
        # Legs (widen base on big reach)
        foot = 0.04 * reach
        self.canvas.add(
            Line(
                points=px(cx - 0.04 * side * reach, cy - 0.14 - 0.02 * reach)
                + px(cx - 0.14 * side - foot, cy - 0.38),
                width=line_w,
                cap="round",
            )
        )
        self.canvas.add(
            Line(
                points=px(cx - 0.04 * side * reach, cy - 0.14 - 0.02 * reach)
                + px(cx + 0.10 * side + foot * 0.5, cy - 0.36),
                width=line_w,
                cap="round",
            )
        )
