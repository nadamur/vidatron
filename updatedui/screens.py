"""
Screens
=======
All screen classes for the Vidatron application.
"""

import uuid
from datetime import datetime
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput
from kivy.uix.dropdown import DropDown
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.graphics import Color, RoundedRectangle, Rectangle, Line
from kivy.metrics import dp
from kivy.animation import Animation
import os

from config import config_manager
from widgets import Face, StickFigureIcon

UI = {
    "BG": (0.045, 0.055, 0.085, 1.0),
    "PANEL": (0.09, 0.10, 0.14, 0.96),
    "PANEL_2": (0.11, 0.12, 0.18, 0.96),
    "TEXT": (0.94, 0.96, 1.0, 1.0),
    "TEXT_DIM": (0.72, 0.78, 0.92, 1.0),
    "ACCENT_BLUE": (0.20, 0.62, 1.0, 1.0),
    "ACCENT_PINK": (1.00, 0.41, 0.71, 1.0),
    "ACCENT_GREEN": (0.18, 0.82, 0.44, 1.0),
    "ACCENT_ORANGE": (1.00, 0.55, 0.18, 1.0),
    "NEUTRAL": (0.42, 0.46, 0.58, 1.0),
    "DANGER": (0.85, 0.28, 0.28, 1.0),
}


class WelcomeScreen(Screen):
    """
    Welcome/Home screen with navigation options.
    Allows user to choose: Go with Default, Customize, or View Settings.
    """
    
    def __init__(self, **kwargs):
        """Initialize the welcome screen."""
        super().__init__(**kwargs)
        self.setup_ui()
    
    def setup_ui(self):
        """Build the welcome screen UI with navigation icons."""
        # Main layout with background
        main_layout = FloatLayout()
        
        # Background gradient effect
        with main_layout.canvas.before:
            Color(*UI["BG"])
            Rectangle(pos=main_layout.pos, size=Window.size)
            Color(0.12, 0.18, 0.30, 0.28)
            RoundedRectangle(pos=(dp(20), dp(20)), size=(Window.width-dp(40), Window.height-dp(40)), radius=[dp(30)])
        
        # Title
        title = Label(
            text="Vidatron",
            font_size="48sp",
            bold=True,
            color=(1, 1, 1, 1),
            halign="center",
            valign="top",
            size_hint=(1, 0.2),
            pos_hint={"x": 0, "y": 0.80}
        )
        main_layout.add_widget(title)
        
        subtitle = Label(
            text="Your Personal Robot Assistant",
            font_size="24sp",
            color=UI["TEXT_DIM"],
            halign="center",
            size_hint=(1, 0.1),
            pos_hint={"x": 0, "y": 0.70}
        )
        main_layout.add_widget(subtitle)
        
        # Navigation buttons in a grid
        nav_grid = GridLayout(
            cols=2,
            spacing=dp(20),
            padding=dp(30),
            size_hint=(0.9, 0.5),
            pos_hint={"center_x": 0.5, "center_y": 0.45}
        )
        
        # Go with Default button
        default_btn = Button(
            text="Go with Default",
            font_size="20sp",
            bold=True,
            size_hint_y=None,
            height=dp(120),
            background_color=UI["ACCENT_GREEN"],
            background_normal='',
            background_down=''
        )
        default_btn.bind(on_release=self.go_default)
        nav_grid.add_widget(default_btn)
        
        # Customize button
        customize_btn = Button(
            text="Customize",
            font_size="20sp",
            bold=True,
            size_hint_y=None,
            height=dp(120),
            background_color=UI["ACCENT_BLUE"],
            background_normal='',
            background_down=''
        )
        customize_btn.bind(on_release=self.start_customization)
        nav_grid.add_widget(customize_btn)
        
        # Settings button
        settings_btn = Button(
            text="Settings",
            font_size="20sp",
            bold=True,
            size_hint_y=None,
            height=dp(120),
            background_color=UI["ACCENT_ORANGE"],
            background_normal='',
            background_down=''
        )
        settings_btn.bind(on_release=self.open_settings)
        nav_grid.add_widget(settings_btn)
        
        # Reminders button
        reminders_btn = Button(
            text="Reminders",
            font_size="20sp",
            bold=True,
            size_hint_y=None,
            height=dp(120),
            background_color=UI["ACCENT_PINK"],
            background_normal='',
            background_down=''
        )
        reminders_btn.bind(on_release=self.open_reminders)
        nav_grid.add_widget(reminders_btn)
        
        main_layout.add_widget(nav_grid)
        
        self.add_widget(main_layout)
        
        # Time in a separate overlay so it is always above background/colour (drawn on top of everything)
        welcome_time_overlay = FloatLayout(size_hint=(1, 1))
        self._welcome_time_label = Label(
            text="",
            font_size="20sp",
            color=(0.9, 0.9, 1, 1),
            halign="right",
            valign="top",
            size_hint=(0.32, 0.08),
            pos_hint={"right": 1, "top": 1},
            padding=(dp(16), dp(8))
        )
        self._welcome_time_label.bind(size=lambda lbl, size: setattr(lbl, "text_size", (max(1, size[0] - dp(24)), max(1, size[1] - dp(16)))))
        welcome_time_overlay.add_widget(self._welcome_time_label)
        self.add_widget(welcome_time_overlay)
        self._update_welcome_time()
        Clock.schedule_interval(lambda dt: self._update_welcome_time(), 1.0)
    
    def _update_welcome_time(self):
        """Update time in top right (12-hour with AM/PM)."""
        if hasattr(self, '_welcome_time_label'):
            now = datetime.now()
            h = now.hour % 12 or 12
            m = now.minute
            ampm = "AM" if now.hour < 12 else "PM"
            self._welcome_time_label.text = f"{h}:{m:02d} {ampm}"
    
    def go_default(self, instance):
        """Revert to default settings (blue screen, round eyes, smile) and go to homescreen."""
        # Default: blue accent, Round eyes, Curved mouth (smile)
        config_manager.set("face_customization.selected_eyes", "Round")
        config_manager.set("face_customization.selected_mouth", "Happy")
        config_manager.set("default_colors.primary", [0.10, 0.90, 1.00, 1.0])
        config_manager.set("font_settings.style", "Roboto")
        config_manager.set("font_settings.size", 30)
        config_manager.set("first_time_setup_complete", True)
        self.manager.current = "homescreen"
    
    def start_customization(self, instance):
        """Start the customization setup process."""
        self.manager.current = "setup_face"
    
    def open_settings(self, instance):
        """Open settings screen."""
        self.manager.current = "settings"
    
    def open_reminders(self, instance):
        """Open reminders screen."""
        self.manager.current = "reminders"


class SetupFaceScreen(Screen):
    """
    First-time setup - Page 1: Face Customization
    Allows user to configure eyes and mouth (both nullable).
    """
    
    def __init__(self, **kwargs):
        """Initialize the face customization setup screen."""
        super().__init__(**kwargs)
        # Defaults ensure the mouth/eyes are always visible after "Complete Setup".
        self.selected_eyes = "Round"
        self.selected_mouth = "Happy"
        self.setup_ui()

    def on_pre_enter(self, *args):
        # Load current saved values so changes reliably persist.
        eyes = config_manager.get("face_customization.selected_eyes") or "Round"
        mouth = config_manager.get("face_customization.selected_mouth") or "Happy"
        allowed_eyes = {"Round", "Narrow", "Big", "Small"}
        allowed_mouth = {"Happy", "Sad", "Neutral", "Shocked"}
        self.selected_eyes = eyes if eyes in allowed_eyes else "Round"
        self.selected_mouth = mouth if mouth in allowed_mouth else "Happy"
        if hasattr(self, "eyes_btn"):
            self.eyes_btn.text = f"Eyes: {self.selected_eyes}"
        if hasattr(self, "mouth_btn"):
            self.mouth_btn.text = f"Mouth: {self.selected_mouth}"
    
    def setup_ui(self):
        """Build the UI for face customization."""
        layout = FloatLayout()
        
        # Background
        with layout.canvas.before:
            Color(*UI["BG"])
            Rectangle(pos=layout.pos, size=Window.size)
            Color(*UI["PANEL"])
            RoundedRectangle(
                pos=(dp(18), dp(18)),
                size=(Window.width - dp(36), Window.height - dp(36)),
                radius=[dp(26)],
            )
        
        # Title
        title = Label(
            text="Welcome to Vidatron!\nStep 1/2: Face Customization",
            font_size="36sp",
            bold=True,
            color=(1, 1, 1, 1),
            halign="center",
            valign="top",
            size_hint=(1, 0.15),
            pos_hint={"x": 0, "y": 0.85}
        )
        layout.add_widget(title)
        
        # Instructions
        instructions = Label(
            text="Choose eyes + mouth (tap Save on next screen)",
            font_size="22sp",
            color=UI["TEXT_DIM"],
            halign="center",
            size_hint=(1, 0.08),
            pos_hint={"x": 0, "y": 0.75}
        )
        layout.add_widget(instructions)
        
        # Eyes selection with better spacing
        eyes_label = Label(
            text="Eyes (optional):",
            font_size="24sp",
            color=UI["TEXT"],
            halign="left",
            size_hint=(0.4, 0.08),
            pos_hint={"x": 0.1, "y": 0.62}
        )
        layout.add_widget(eyes_label)
        
        self.eyes_dropdown = DropDown()
        self.eyes_btn = Button(
            text=f"Eyes: {self.selected_eyes}",
            size_hint=(0.35, 0.08),
            pos_hint={"x": 0.5, "y": 0.62},
            background_color=UI["ACCENT_BLUE"],
            background_normal='',
            background_down=''
        )
        # Keep options limited to shapes Kivy depicts cleanly.
        for option in ["Round", "Narrow", "Big", "Small"]:
            btn = Button(text=option, size_hint_y=None, height=dp(50))
            btn.bind(on_release=lambda b, opt=option: self.select_eyes(opt, self.eyes_btn))
            self.eyes_dropdown.add_widget(btn)
        self.eyes_btn.bind(on_release=self.eyes_dropdown.open)
        layout.add_widget(self.eyes_btn)
        
        # Mouth selection with better spacing
        mouth_label = Label(
            text="Mouth (optional):",
            font_size="24sp",
            color=UI["TEXT"],
            halign="left",
            size_hint=(0.4, 0.08),
            pos_hint={"x": 0.1, "y": 0.50}
        )
        layout.add_widget(mouth_label)
        
        self.mouth_dropdown = DropDown()
        self.mouth_btn = Button(
            text=f"Mouth: {self.selected_mouth}",
            size_hint=(0.35, 0.08),
            pos_hint={"x": 0.5, "y": 0.50},
            background_color=UI["ACCENT_BLUE"],
            background_normal='',
            background_down=''
        )
        # At least 3 options for mouth (including None)
        for option in ["Happy", "Sad", "Neutral", "Shocked"]:
            btn = Button(text=option, size_hint_y=None, height=dp(50))
            btn.bind(on_release=lambda b, opt=option: self.select_mouth(opt, self.mouth_btn))
            self.mouth_dropdown.add_widget(btn)
        self.mouth_btn.bind(on_release=self.mouth_dropdown.open)
        layout.add_widget(self.mouth_btn)
        
        # Navigation buttons with better styling
        back_btn = Button(
            text="← Back",
            size_hint=(0.2, 0.10),
            pos_hint={"x": 0.1, "y": 0.15},
            background_color=UI["NEUTRAL"],
            background_normal='',
            background_down=''
        )
        back_btn.bind(on_release=lambda *_: setattr(self.manager, "current", "welcome"))
        layout.add_widget(back_btn)
        
        next_btn = Button(
            text="Next →",
            size_hint=(0.25, 0.10),
            pos_hint={"x": 0.65, "y": 0.15},
            background_color=UI["ACCENT_GREEN"],
            background_normal='',
            background_down=''
        )
        next_btn.bind(on_release=self.next_page)
        layout.add_widget(next_btn)
        
        self.add_widget(layout)
    
    def select_eyes(self, option, btn):
        """Handle eyes selection (nullable - can be None)."""
        self.eyes_dropdown.dismiss()
        self.selected_eyes = option
        btn.text = f"Eyes: {option}"
    
    def select_mouth(self, option, btn):
        """Handle mouth selection (nullable - can be None)."""
        self.mouth_dropdown.dismiss()
        self.selected_mouth = option
        btn.text = f"Mouth: {option}"
    
    def next_page(self, instance):
        """Navigate to color selection (values are saved on Complete Setup)."""
        self.manager.current = "setup_colors"


class SetupFontScreen(Screen):
    """
    First-time setup - Page 2: Font Selection
    Allows user to choose font style and size.
    """
    
    def __init__(self, **kwargs):
        """Initialize the font selection setup screen."""
        super().__init__(**kwargs)
        self.selected_style = "Roboto"
        self.setup_ui()
    
    def setup_ui(self):
        """Build the UI for font selection."""
        layout = FloatLayout()
        
        # Title
        title = Label(
            text="Step 2/3: Font Selection",
            font_size="32sp",
            bold=True,
            color=(1, 1, 1, 1),
            halign="center",
            valign="top",
            size_hint=(1, 0.15),
            pos_hint={"x": 0, "y": 0.85}
        )
        layout.add_widget(title)
        
        # Font style
        style_label = Label(
            text="Font Style:",
            font_size="22sp",
            color=(0.9, 0.9, 1, 1),
            halign="left",
            size_hint=(0.3, 0.08),
            pos_hint={"x": 0.1, "y": 0.60}
        )
        layout.add_widget(style_label)
        
        self.style_dropdown = DropDown()
        style_btn = Button(
            text="Roboto",
            size_hint=(0.3, 0.08),
            pos_hint={"x": 0.35, "y": 0.60}
        )
        # Only use fonts that Kivy reliably supports
        for option in ["Roboto", "DejaVuSans"]:
            btn = Button(text=option, size_hint_y=None, height=50)
            btn.bind(on_release=lambda b, opt=option: self.select_style(opt, style_btn))
            self.style_dropdown.add_widget(btn)
        style_btn.bind(on_release=self.style_dropdown.open)
        layout.add_widget(style_btn)
        
        # Font size
        size_label = Label(
            text="Font Size:",
            font_size="22sp",
            color=(0.9, 0.9, 1, 1),
            halign="left",
            size_hint=(0.3, 0.08),
            pos_hint={"x": 0.1, "y": 0.48}
        )
        layout.add_widget(size_label)
        
        self.size_input = TextInput(
            text="30",
            multiline=False,
            size_hint=(0.2, 0.08),
            pos_hint={"x": 0.35, "y": 0.48}
        )
        layout.add_widget(self.size_input)
        
        # Navigation buttons
        back_btn = Button(
            text="← Back",
            size_hint=(0.2, 0.10),
            pos_hint={"x": 0.1, "y": 0.15},
            background_color=(0.5, 0.5, 0.5, 1.0)
        )
        back_btn.bind(on_release=lambda *_: setattr(self.manager, "current", "setup_face"))
        layout.add_widget(back_btn)
        
        next_btn = Button(
            text="Next →",
            size_hint=(0.25, 0.10),
            pos_hint={"x": 0.7, "y": 0.15},
            background_color=(0.2, 0.6, 0.8, 1.0)
        )
        next_btn.bind(on_release=self.next_page)
        layout.add_widget(next_btn)
        
        self.add_widget(layout)
    
    def select_style(self, option, btn):
        """Handle font style selection."""
        self.style_dropdown.dismiss()
        self.selected_style = option
        btn.text = option
        # Save immediately when selected
        config_manager.set("font_settings.style", self.selected_style)
    
    def next_page(self, instance):
        """Save font settings and navigate to color selection."""
        # Ensure style is saved (already saved on selection, but double-check)
        config_manager.set("font_settings.style", self.selected_style)
        try:
            font_size = int(self.size_input.text)
            config_manager.set("font_settings.size", font_size)
        except ValueError:
            config_manager.set("font_settings.size", 30)
        self.manager.current = "setup_colors"


class SetupColorsScreen(Screen):
    """
    First-time setup - Page 3: Default Colors Selection
    Allows user to choose default accent color.
    """
    
    def __init__(self, **kwargs):
        """Initialize the color selection setup screen."""
        super().__init__(**kwargs)
        color_presets = [
            ("Blue", (0.10, 0.90, 1.00, 1.0)),
            ("Red", (1.00, 0.25, 0.25, 1.0)),
            ("Yellow", (1.00, 0.93, 0.20, 1.0)),
            ("Green", (0.15, 1.00, 0.55, 1.0)),
            ("Orange", (1.00, 0.45, 0.10, 1.0)),
            ("Purple", (0.80, 0.35, 1.00, 1.0)),
            ("Pink", (1.00, 0.41, 0.71, 1.0)),
        ]
        self.selected_color = color_presets[0][1]
        self.setup_ui()
    
    def setup_ui(self):
        """Build the UI for color selection."""
        layout = FloatLayout()

        with layout.canvas.before:
            Color(*UI["BG"])
            Rectangle(pos=layout.pos, size=Window.size)
            Color(*UI["PANEL"])
            RoundedRectangle(
                pos=(dp(18), dp(18)),
                size=(Window.width - dp(36), Window.height - dp(36)),
                radius=[dp(26)],
            )
        
        # Title
        title = Label(
            text="Step 2/2: Default Colors",
            font_size="32sp",
            bold=True,
            color=(1, 1, 1, 1),
            halign="center",
            valign="top",
            size_hint=(1, 0.15),
            pos_hint={"x": 0, "y": 0.85}
        )
        layout.add_widget(title)
        
        # Instructions
        instructions = Label(
            text="Choose your default accent color",
            font_size="20sp",
            color=UI["TEXT_DIM"],
            halign="center",
            size_hint=(1, 0.08),
            pos_hint={"x": 0, "y": 0.75}
        )
        layout.add_widget(instructions)
        
        # Color presets (7: pink, blue, red, yellow, green, orange, purple)
        color_presets = [
            ("Blue", (0.10, 0.90, 1.00, 1.0)),
            ("Red", (1.00, 0.25, 0.25, 1.0)),
            ("Yellow", (1.00, 0.93, 0.20, 1.0)),
            ("Green", (0.15, 1.00, 0.55, 1.0)),
            ("Orange", (1.00, 0.45, 0.10, 1.0)),
            ("Purple", (0.80, 0.35, 1.00, 1.0)),
            ("Pink", (1.00, 0.41, 0.71, 1.0)),
        ]
        for i, (name, color) in enumerate(color_presets):
            row, col = i // 3, i % 3
            btn = Button(
                text=name,
                size_hint=(0.28, 0.12),
                pos_hint={"x": 0.08 + col * 0.32, "y": 0.58 - row * 0.14},
                background_color=(*color[:3], 0.8),
                font_size="18sp",
                background_normal="",
                background_down="",
            )
            btn.bind(on_release=lambda b, c=color: self.select_color(c))
            layout.add_widget(btn)
        
        # Navigation buttons
        back_btn = Button(
            text="← Back",
            size_hint=(0.2, 0.10),
            pos_hint={"x": 0.1, "y": 0.15},
            background_color=UI["NEUTRAL"],
            background_normal="",
            background_down="",
        )
        back_btn.bind(on_release=lambda *_: setattr(self.manager, "current", "setup_face"))
        layout.add_widget(back_btn)
        
        # Complete Setup Button
        complete_btn = Button(
            text="Complete Setup",
            size_hint=(0.35, 0.10),
            pos_hint={"x": 0.55, "y": 0.15},
            background_color=UI["ACCENT_GREEN"],
            background_normal="",
            background_down="",
        )
        complete_btn.bind(on_release=self.complete_setup)
        layout.add_widget(complete_btn)
        
        self.add_widget(layout)
    
    def select_color(self, color):
        """Handle default color selection."""
        self.selected_color = color
        # Defer saving until Complete Setup (keeps "click save" semantics).
    
    def complete_setup(self, instance):
        """Save color settings, mark setup complete, and navigate to homescreen."""
        # Save eyes + mouth chosen on SetupFaceScreen
        try:
            face_screen = self.manager.get_screen("setup_face")
            config_manager.set("face_customization.selected_eyes", getattr(face_screen, "selected_eyes", "Round"))
            config_manager.set("face_customization.selected_mouth", getattr(face_screen, "selected_mouth", "Happy"))
        except Exception:
            # Fall back to whatever is already in config
            pass

        # Save selected accent color
        config_manager.set("default_colors.primary", list(self.selected_color))
        config_manager.set("first_time_setup_complete", True)
        self.manager.current = "homescreen"


class Homescreen(Screen):
    """
    Main homescreen displayed after first-time setup.
    Shows active reminders and provides navigation to settings.
    """
    # Fraction of window height for text + controls (rest is face / habit animation)
    BOTTOM_PANEL_FRAC = 0.38
    VISUAL_FRAC = 1.0 - BOTTOM_PANEL_FRAC  # 0.62

    def __init__(self, **kwargs):
        """Initialize the homescreen."""
        super().__init__(**kwargs)
        self.idx = 0  # Current reminder index
        self._default_text_mode = True  # False while a reminder card is shown (title/line)
        self.ai_service = None
        self._ai_listener_active = False
        self._ai_conversation_active = False
        self._ai_previous_conversation_active = False
        self._ai_starting = False
        self._ai_shutting_down = False
        self._ai_state_anim = None
        self._deferred_reminder_keys = set()
        self._deferred_reminder_queue = []
        # Ensure default reminders are added if needed
        config_manager.ensure_default_reminders()
        self.setup_ui()
        self.load_reminders()
    
    def setup_ui(self):
        """Build the homescreen UI."""
        layout = FloatLayout()
        vf = Homescreen.VISUAL_FRAC
        bf = Homescreen.BOTTOM_PANEL_FRAC

        # Face / animation area (top ~62%)
        self.face = Face(size_hint=(1, vf), pos_hint={"x": 0, "y": bf})
        # Apply saved face customization (ensure None is properly handled)
        eyes = config_manager.get("face_customization.selected_eyes")
        mouth = config_manager.get("face_customization.selected_mouth")
        # Convert string "None" to actual None if needed
        eyes = None if eyes == "None" or eyes is None else eyes
        mouth = None if mouth == "None" or mouth is None else mouth
        self.face.set_customization(eyes, mouth)
        
        # Apply saved default color to face
        default_color = config_manager.get("default_colors.primary", [0.10, 0.90, 1.00, 1.0])
        if isinstance(default_color, list):
            default_color = tuple(default_color)
        self.face.set_style(default_color, "happy")
        layout.add_widget(self.face)
        
        # Icon image widget (stick figure from file) - replaces face when reminder has icon_path
        self.icon_image = Image(
            source="",
            size_hint=(1, vf),
            pos_hint={"x": 0, "y": bf},
            allow_stretch=True,
            keep_ratio=True,
        )
        if hasattr(self.icon_image, "fit_mode"):
            self.icon_image.fit_mode = "contain"
        self.icon_image.opacity = 0  # Hidden by default (face shows instead)
        layout.add_widget(self.icon_image)
        # Kivy-drawn stick figure icon (when reminder has action: drink / stretch)
        self.stick_figure_icon = StickFigureIcon(
            action="stretch",
            size_hint=(1, vf),
            pos_hint={"x": 0, "y": bf},
        )
        self.stick_figure_icon.opacity = 0  # Hidden by default
        layout.add_widget(self.stick_figure_icon)
        
        # Bottom bar (canvas behind text panel)
        self.bar = Widget(size_hint=(1, bf), pos_hint={"x": 0, "y": 0})
        layout.add_widget(self.bar)

        font_size = config_manager.get("font_settings.size", 30)
        font_style = config_manager.get("font_settings.style", "Roboto")

        # Bottom text stack: status row (wake hint) | title | body — no overlap
        self.bottom_panel = BoxLayout(
            orientation="vertical",
            size_hint=(1, bf),
            pos_hint={"x": 0, "y": 0},
            padding=(dp(16), dp(8), dp(16), dp(10)),
            spacing=dp(6),
        )
        # Home stays visible; wake hint row hides during reminder cards (no overlap with title)
        self._home_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(36),
            spacing=dp(8),
        )
        self._home_row.add_widget(Widget(size_hint_x=1))
        self.home_btn = Button(
            text="Home",
            size_hint=(None, None),
            size=(dp(96), dp(36)),
            background_color=(0.35, 0.42, 0.55, 0.95),
            background_normal="",
            background_down="",
        )
        self.home_btn.bind(on_release=lambda *_: setattr(self.manager, "current", "welcome"))
        self._home_row.add_widget(self.home_btn)

        self._status_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(36),
            spacing=dp(10),
        )
        self.ai_status = Label(
            text="",
            font_size="11sp",
            color=(0.78, 0.86, 1.0, 1),
            halign="left",
            valign="middle",
            size_hint_x=1,
        )
        self.ai_status.bind(
            size=lambda lb, s: setattr(lb, "text_size", (max(1, s[0] - dp(6)), max(1, s[1] - dp(4))))
        )
        self._status_row.add_widget(self.ai_status)

        self.title = Label(
            text="",
            markup=True,
            font_size=f"{int(font_size * 1.02)}sp",
            font_name=font_style,
            bold=True,
            halign="left",
            valign="top",
            color=(1, 1, 1, 1),
            size_hint_y=None,
            padding=(0, 2, 0, 0),
        )
        self.title.bind(size=lambda lbl, sz: setattr(lbl, "text_size", (max(1, sz[0] - dp(8)), None)))
        self.title.bind(
            texture_size=lambda lbl, ts: setattr(lbl, "height", max(ts[1] + dp(10), dp(40)))
        )

        self.line = Label(
            text="",
            markup=True,
            font_size=f"{int(font_size * 0.78)}sp",
            font_name=font_style,
            halign="left",
            valign="top",
            color=(0.92, 0.95, 1, 1),
            size_hint_y=1,
            padding=(0, 0, 0, dp(4)),
        )
        self.line.bind(size=lambda lbl, sz: setattr(lbl, "text_size", (max(1, sz[0] - dp(8)), None)))

        self.bottom_panel.add_widget(self._home_row)
        self.bottom_panel.add_widget(self._status_row)
        self.bottom_panel.add_widget(self.title)
        self.bottom_panel.add_widget(self.line)
        layout.add_widget(self.bottom_panel)

        # Voice conversation overlay (hidden unless a wake-triggered session is active)
        self.ai_conv_box = BoxLayout(
            orientation="vertical",
            size_hint=(0.96, 0.17),
            pos_hint={"x": 0.02, "y": 0.02},
            padding=(dp(12), dp(8), dp(12), dp(8)),
            spacing=dp(4),
            opacity=0,
            disabled=True,
        )
        with self.ai_conv_box.canvas.before:
            Color(0.06, 0.10, 0.16, 0.95)
            self._ai_panel_bg = RoundedRectangle(pos=self.ai_conv_box.pos, size=self.ai_conv_box.size, radius=[16])
            Color(0.40, 0.74, 1.0, 0.26)
            self._ai_panel_glow = RoundedRectangle(pos=self.ai_conv_box.pos, size=self.ai_conv_box.size, radius=[16])
            Color(1, 1, 1, 0.10)
            self._ai_panel_border = Line(rounded_rectangle=(self.ai_conv_box.x, self.ai_conv_box.y, self.ai_conv_box.width, self.ai_conv_box.height, 16), width=1.3)
        self.ai_conv_box.bind(pos=self._update_ai_panel_rect, size=self._update_ai_panel_rect)
        self.ai_mode_title = Label(
            text="[b]AI Voice Mode[/b]",
            markup=True,
            font_size=f"{int(font_size * 0.5)}sp",
            font_name=font_style,
            halign="left",
            valign="middle",
            color=(0.92, 0.97, 1, 1),
            size_hint_y=None,
            height=dp(22),
        )
        self.ai_mode_title.bind(
            size=lambda lbl, sz: setattr(lbl, "text_size", (max(1, sz[0] - dp(6)), max(1, sz[1] - dp(4))))
        )
        self.ai_phase_label = Label(
            text="",
            markup=True,
            font_size=f"{int(font_size * 0.45)}sp",
            font_name=font_style,
            bold=True,
            halign="left",
            valign="middle",
            color=(0.92, 0.97, 1, 1),
            size_hint_y=None,
            height=dp(20),
        )
        self.ai_phase_label.bind(
            size=lambda lbl, sz: setattr(lbl, "text_size", (max(1, sz[0] - dp(6)), max(1, sz[1] - dp(6))))
        )
        self.ai_chat_scroll = ScrollView(
            size_hint_y=1,
            do_scroll_x=False,
            bar_width=dp(8),
            bar_color=(0.4, 0.65, 0.9, 0.75),
            bar_inactive_color=(0.22, 0.3, 0.42, 0.35),
            scroll_type=["bars", "content"],
        )
        self.ai_chat_label = Label(
            text="",
            markup=True,
            font_size=f"{int(font_size * 0.40)}sp",
            font_name=font_style,
            halign="left",
            valign="top",
            color=(0.86, 0.91, 0.98, 1),
            size_hint_y=None,
            padding=(dp(4), dp(4)),
        )
        self.ai_chat_scroll.bind(
            width=lambda *_: setattr(self.ai_chat_label, "text_size", (max(1, self.ai_chat_scroll.width - dp(18)), None))
        )
        self.ai_chat_label.bind(
            texture_size=lambda lb, sz: setattr(lb, "height", max(sz[1] + dp(24), self.ai_chat_scroll.height + dp(6)))
        )
        self.ai_chat_scroll.add_widget(self.ai_chat_label)
        self.ai_conv_box.add_widget(self.ai_mode_title)
        self.ai_conv_box.add_widget(self.ai_phase_label)
        self.ai_conv_box.add_widget(self.ai_chat_scroll)
        layout.add_widget(self.ai_conv_box)

        self.add_widget(layout)

        # Time overlay — inset from top so it is never clipped by the window
        time_overlay = FloatLayout(size_hint=(1, 1))
        self.time_label = Label(
            text="",
            font_size="18sp",
            color=(0.95, 0.96, 1, 1),
            halign="right",
            valign="top",
            size_hint=(0.44, 0.11),
            pos_hint={"right": 0.99, "top": 0.99},
            padding=(dp(20), dp(14), dp(20), dp(6)),
        )
        self.time_label.bind(
            size=lambda lbl, size: setattr(
                lbl, "text_size", (max(1, size[0] - dp(28)), max(1, size[1] - dp(10)))
            )
        )
        time_overlay.add_widget(self.time_label)
        self.add_widget(time_overlay)
        self._update_time_label()
        Clock.schedule_interval(lambda dt: self._update_time_label(), 1.0)
        
        # Track if a triggered reminder is currently showing (pause cycling)
        self.triggered_reminder_showing = False
        self.cycling_paused_until = None
        
        # Start reminder scheduler (checks every second for time-triggered reminders)
        Clock.schedule_interval(self.check_reminders, 1.0)
        # No automatic cycling: reminders only show when their set time triggers
    
    def _update_time_label(self):
        """Update the time display in top right (12-hour with AM/PM)."""
        if hasattr(self, 'time_label'):
            now = datetime.now()
            h = now.hour % 12 or 12
            m = now.minute
            ampm = "AM" if now.hour < 12 else "PM"
            self.time_label.text = f"{h}:{m:02d} {ampm}"

    def _update_ai_panel_rect(self, *_):
        if not hasattr(self, "_ai_panel_bg"):
            return
        self._ai_panel_bg.pos = self.ai_conv_box.pos
        self._ai_panel_bg.size = self.ai_conv_box.size
        self._ai_panel_glow.pos = self.ai_conv_box.pos
        self._ai_panel_glow.size = self.ai_conv_box.size
        self._ai_panel_border.rounded_rectangle = (
            self.ai_conv_box.x,
            self.ai_conv_box.y,
            self.ai_conv_box.width,
            self.ai_conv_box.height,
            16,
        )

    def _set_status_row_visible(self, show: bool):
        """Wake-hint row only; Home stays in _home_row."""
        if not hasattr(self, "_status_row"):
            return
        if show:
            self._status_row.height = dp(36)
            self._status_row.opacity = 1
            self._status_row.disabled = False
        else:
            self._status_row.height = 0
            self._status_row.opacity = 0
            self._status_row.disabled = True

    def _refresh_status_row_visibility(self):
        if getattr(self, "_ai_conversation_active", False):
            self._set_status_row_visible(False)
            return
        if getattr(self, "_default_text_mode", True):
            self._set_status_row_visible(True)
        else:
            self._set_status_row_visible(False)

    def on_leave(self, *args):
        self._ai_shutting_down = True
        if self._ai_state_anim is not None:
            self._ai_state_anim.cancel(self.face)
            self._ai_state_anim = None
        if getattr(self, "ai_service", None):
            self.ai_service.stop(quiet=True)
            self.ai_service = None
        self._ai_listener_active = False
        self._ai_conversation_active = False
        self._set_voice_panel_mode(False)
        if hasattr(self, "ai_status"):
            self.ai_status.text = ""
        self._ai_shutting_down = False

    def _set_voice_panel_mode(self, conv: bool):
        self.ai_conv_box.opacity = 1 if conv else 0
        self.ai_conv_box.disabled = not bool(conv)
        self.title.opacity = 0 if conv else 1
        self.line.opacity = 0 if conv else 1
        if hasattr(self, "home_btn"):
            self.home_btn.opacity = 0.88 if conv else 1.0
        self._refresh_status_row_visibility()

    def _animate_ai_state(self, state):
        from ai_voice_service import AIState

        if self._ai_state_anim is not None:
            self._ai_state_anim.cancel(self.face)
            self._ai_state_anim = None
        self.face.opacity = 1.0
        # Light outer pulse only — face widget handles listening/thinking/speaking motion
        if state == AIState.LISTENING:
            self._ai_state_anim = Animation(opacity=0.88, d=0.28) + Animation(opacity=1.0, d=0.28)
            self._ai_state_anim.repeat = True
            self._ai_state_anim.start(self.face)
        elif state == AIState.THINKING:
            self._ai_state_anim = Animation(opacity=0.9, d=0.45) + Animation(opacity=1.0, d=0.45)
            self._ai_state_anim.repeat = True
            self._ai_state_anim.start(self.face)
        elif state == AIState.SPEAKING:
            self._ai_state_anim = Animation(opacity=0.82, d=0.12) + Animation(opacity=1.0, d=0.12)
            self._ai_state_anim.repeat = True
            self._ai_state_anim.start(self.face)

    def _start_voice_ai_if_needed(self):
        if getattr(self, "_ai_shutting_down", False):
            return
        if getattr(self, "ai_service", None) and getattr(self.ai_service, "_running", False):
            return
        if getattr(self, "_ai_starting", False):
            return
        self._ai_starting = True
        try:
            from ai_voice_service import AIVoiceService

            self.ai_service = AIVoiceService(ui_callback=self._ai_dispatch_from_any_thread)
            self.ai_service.start()
            self._ai_listener_active = True
            self.ai_status.text = "Starting voice assistant…"
        except Exception as e:
            self._ai_listener_active = False
            self.line.text = ("Voice assistant: " + str(e))[:220]
            self.ai_status.text = "Voice unavailable"
        finally:
            self._ai_starting = False

    def _ai_dispatch_from_any_thread(self, **kwargs):
        Clock.schedule_once(lambda dt: self._ai_apply_ai_ui(**kwargs), 0)

    def _ai_apply_ai_ui(
        self,
        state=None,
        title=None,
        line=None,
        wake_confidence=None,
        conversation_active=None,
        conversation_ended=False,
        phase=None,
    ):
        from ai_voice_service import AIState

        if not getattr(self, "_ai_listener_active", False):
            return

        if conversation_ended:
            self._ai_conversation_active = False
            self._ai_previous_conversation_active = False
            self._set_voice_panel_mode(False)
            self.ai_chat_label.text = ""
            self.ai_phase_label.text = ""
            if self._ai_state_anim is not None:
                self._ai_state_anim.cancel(self.face)
                self._ai_state_anim = None
            self.load_reminders()
            pending = list(self._deferred_reminder_queue)
            self._deferred_reminder_queue = []
            self._deferred_reminder_keys.clear()
            if pending:
                first = pending[0]
                Clock.schedule_once(lambda dt: self.trigger_reminder(first, is_real_trigger=True), 0.15)
        elif conversation_active is not None:
            self._ai_conversation_active = bool(conversation_active)

        conv = self._ai_conversation_active
        cur = getattr(self.ai_service, "state", None) if self.ai_service else None
        effective = state if state is not None else cur
        phrase = getattr(self.ai_service, "wake_phrase", "wake phrase") if self.ai_service else "wake phrase"

        if state == AIState.OFF and line:
            self._set_voice_panel_mode(False)
            self.title.text = "[b]Voice assistant[/b]"
            self.line.text = (line or "")[:900]
            self.ai_status.text = ""
            return

        if not conv:
            self._set_voice_panel_mode(False)
            self._ai_previous_conversation_active = False
            if effective == AIState.WAITING and wake_confidence is not None:
                self.ai_status.text = f"Say '{phrase}' to chat  ·  Wake {wake_confidence:.0%}"
            elif effective == AIState.WAITING:
                self.ai_status.text = f"Say '{phrase}' to chat with Vidatron"
            else:
                self.ai_status.text = ""
            return

        self._set_voice_panel_mode(True)
        if not self._ai_previous_conversation_active:
            # Keep this generic so the user never needs to type their name.
            self.ai_chat_label.text = "[b]Vidatron[/b]\nI'm listening."
        self._ai_previous_conversation_active = True
        self.ai_status.text = ""
        if state == AIState.LISTENING:
            mood = "listening"
        elif state == AIState.FOLLOW_UP:
            mood = "listening"
        elif state == AIState.THINKING:
            mood = "thinking"
        elif state == AIState.SPEAKING:
            mood = "speaking"
        else:
            mood = "happy"
        accent = config_manager.get("default_colors.primary", [0.10, 0.90, 1.00, 1.0])
        if isinstance(accent, list):
            accent = tuple(accent)
        self.face.set_style(accent, mood)
        self.draw_bar(accent)
        self.icon_image.opacity = 0
        self.stick_figure_icon.opacity = 0
        self.face.opacity = 1.0
        self._animate_ai_state(effective)

        if phase:
            dot = "#3dd6ff" if effective in (AIState.LISTENING, AIState.FOLLOW_UP) else "#b388ff"
            if effective == AIState.SPEAKING:
                dot = "#5ef5a8"
            self.ai_phase_label.text = f"[b][color={dot}]●[/color]  {phase}[/b]"
        if title and line:
            existing = self.ai_chat_label.text.strip()
            speaker_color = "#7DD3FC" if str(title).lower().startswith("you") else "#86EFAC"
            block = f"[b][color={speaker_color}]{title}[/color][/b]\n[color=#EAF4FF]{line}[/color]"
            self.ai_chat_label.text = (existing + "\n\n" + block).strip() if existing else block
            self.ai_chat_scroll.scroll_y = 0
    
    def on_pre_enter(self, *args):
        """Refresh reminders and ALL customizations when screen becomes visible."""
        # Update face customization from config (reload to ensure latest values)
        eyes = config_manager.get("face_customization.selected_eyes")
        mouth = config_manager.get("face_customization.selected_mouth")
        # Convert string "None" to actual None, ensure proper None handling
        eyes = None if eyes == "None" or eyes is None else eyes
        mouth = None if mouth == "None" or mouth is None else mouth
        self.face.set_customization(eyes, mouth)
        
        # Update font settings - CRITICAL: Must update font_size property
        font_size = config_manager.get("font_settings.size", 30)
        font_style = config_manager.get("font_settings.style", "Roboto")
        if hasattr(self, 'title'):
            self.title.font_size = f"{int(font_size * 1.02)}sp"
            self.title.font_name = font_style
        if hasattr(self, 'line'):
            self.line.font_size = f"{int(font_size * 0.78)}sp"
            self.line.font_name = font_style
        
        # Update default color (apply to face if no reminder showing)
        default_color = config_manager.get("default_colors.primary", [0.10, 0.90, 1.00, 1.0])
        if isinstance(default_color, list):
            default_color = tuple(default_color)
        if not hasattr(self, 'active_reminders') or not self.active_reminders:
            self.face.set_style(default_color, "happy")
            self.draw_bar(default_color)

        self._start_voice_ai_if_needed()
        # Refresh reminders (always show default view with count; never auto-show a reminder card)
        self.load_reminders()
    
    def show_default_view(self):
        """Show the default homescreen: user's face, default color, and reminder count (no reminder card).
        Per-reminder face customizations are never applied here; they only apply when a reminder is triggered (apply_card).
        """
        self._default_text_mode = True
        eyes = config_manager.get("face_customization.selected_eyes")
        mouth = config_manager.get("face_customization.selected_mouth")
        eyes = None if eyes == "None" or eyes is None else eyes
        mouth = None if mouth == "None" or mouth is None else mouth
        self.face.set_customization(eyes, mouth)
        default_color = config_manager.get("default_colors.primary", [0.10, 0.90, 1.00, 1.0])
        if isinstance(default_color, list):
            default_color = tuple(default_color)
        self.face.set_style(default_color, "happy")
        self.draw_bar(default_color)
        # Hide icon image and stick figure; show robot face in default view
        if hasattr(self, 'icon_image'):
            self.icon_image.opacity = 0
        if hasattr(self, 'stick_figure_icon'):
            self.stick_figure_icon.opacity = 0
        if hasattr(self, 'face'):
            self.face.opacity = 1.0  # Show robot face (stick figure hidden)
        n = len(getattr(self, "active_reminders", []))
        if n == 0:
            self.title.text = "[b]No Reminders[/b]"
            self.line.text = "Add reminders in the Tools section"
        elif n == 1:
            self.title.text = "[b]Reminders[/b]"
            self.line.text = "1 reminder"
        else:
            self.title.text = "[b]Reminders[/b]"
            self.line.text = f"{n} reminders"
        self._refresh_status_row_visibility()

    def load_reminders(self):
        """Load reminders and show default view (count only). Never auto-show a reminder card until its time."""
        reminders = config_manager.get("reminders", [])
        self.active_reminders = [r for r in reminders if r.get("is_active", True)]
        if getattr(self, "_ai_conversation_active", False):
            return
        self.show_default_view()
    
    def draw_bar(self, accent):
        """Draw the bottom bar with accent color."""
        self.bar.canvas.before.clear()
        r, g, b, a = accent
        bh = Window.height * Homescreen.BOTTOM_PANEL_FRAC
        with self.bar.canvas.before:
            # Outer glow shell
            Color(r, g, b, 0.95)
            RoundedRectangle(
                pos=(10, 10),
                size=(Window.width - 20, bh - 20),
                radius=[18],
            )
            # Inner dark panel
            Color(0.02, 0.02, 0.04, 0.92)
            RoundedRectangle(
                pos=(16, 16),
                size=(Window.width - 32, bh - 32),
                radius=[14],
            )
            # Accent highlight stripe
            Color(min(1, r * 1.25 + 0.1), min(1, g * 1.25 + 0.1), min(1, b * 1.25 + 0.1), 0.36)
            RoundedRectangle(
                pos=(20, bh - 20),
                size=(Window.width - 40, 8),
                radius=[6],
            )
    
    def apply_card(self, reminder):
        """
        Apply a reminder card to the display. Only called when a reminder is actually shown
        (time-triggered, test-in-10, or manual next). Per-reminder face customizations
        are applied here only, not on the default view.
        """
        self._default_text_mode = False
        # Get accent color from reminder or use default
        accent = reminder.get("accent", config_manager.get("default_colors.primary", [0.10, 0.90, 1.00, 1.0]))
        if isinstance(accent, list):
            accent = tuple(accent)
        
        # Get face expression from reminder (nullable)
        # Constraint: face_expression must have eyes and/or mouth defined within it
        face_expression = reminder.get("face_expression")
        if face_expression and isinstance(face_expression, dict):
            # Check constraint: face_expression must have eyes OR mouth defined
            expr_eyes = face_expression.get("eyes")
            expr_mouth = face_expression.get("mouth")
            if expr_eyes is None and expr_mouth is None:
                # Constraint violation - face_expression requires eyes or mouth
                face_expression = None
        
        # Use face expression mood if valid, otherwise use reminder mood
        if face_expression and isinstance(face_expression, dict):
            mood = face_expression.get("mood", reminder.get("mood", "happy"))
            # Apply face expression customization to face widget
            expr_eyes = face_expression.get("eyes")
            expr_mouth = face_expression.get("mouth")
            # Ensure None values are properly passed (not string "None")
            expr_eyes = None if expr_eyes == "None" or expr_eyes is None else expr_eyes
            expr_mouth = None if expr_mouth == "None" or expr_mouth is None else expr_mouth
            self.face.set_customization(expr_eyes, expr_mouth)
        else:
            mood = reminder.get("mood", "happy")
            # Use global customization - always refresh from config
            eyes = config_manager.get("face_customization.selected_eyes")
            mouth = config_manager.get("face_customization.selected_mouth")
            # Ensure None values are properly passed (not string "None")
            eyes = None if eyes == "None" or eyes is None else eyes
            mouth = None if mouth == "None" or mouth is None else mouth
            self.face.set_customization(eyes, mouth)
        
        # Display reminder icon (stick figure modeling the action) - replaces face when shown
        action = reminder.get("action")  # "drink" | "stretch" | "exercise"
        if not action and reminder.get("text"):
            # Infer action from text for default reminders saved before "action" existed
            t = reminder["text"].lower()
            if "drink" in t or "water" in t or "hydrat" in t:
                action = "drink"
            elif any(k in t for k in ("exercise", "workout", "cardio", "jog", "run", "jump", "active")):
                action = "exercise"
            elif "stretch" in t or "walk" in t or "move" in t:
                action = "stretch"
        icon_path = reminder.get("icon_path")
        icon_text = reminder.get("icon", "")
        
        icon_shown = False
        # Prefer Kivy-drawn stick figure when reminder has action (no image file needed)
        if action in ("drink", "stretch", "exercise") and hasattr(self, "stick_figure_icon"):
            self.stick_figure_icon.accent = tuple(accent) if isinstance(accent, (list, tuple)) else (0.10, 0.90, 1.00, 1.0)
            self.stick_figure_icon.action = action
            self.stick_figure_icon.opacity = 1.0
            self.icon_image.opacity = 0.0
            self.face.opacity = 0.0
            icon_shown = True
        elif icon_path:
            if not os.path.isabs(icon_path):
                script_dir = os.path.dirname(os.path.abspath(__file__))
                icon_path_abs = os.path.join(script_dir, icon_path)
            else:
                icon_path_abs = icon_path
            
            if os.path.exists(icon_path_abs):
                try:
                    self.icon_image.source = icon_path_abs
                    self.icon_image.opacity = 1.0
                    if hasattr(self, "stick_figure_icon"):
                        self.stick_figure_icon.opacity = 0.0
                    self.face.opacity = 0.0
                    icon_shown = True
                except Exception as e:
                    print(f"Error loading icon {icon_path_abs}: {e}")
                    self.icon_image.opacity = 0.0
                    if hasattr(self, "stick_figure_icon"):
                        self.stick_figure_icon.opacity = 0.0
                    self.face.opacity = 1.0
                    icon_text = icon_text or ""
            else:
                if hasattr(self, "stick_figure_icon"):
                    self.stick_figure_icon.opacity = 0.0
                self.icon_image.opacity = 0.0
                self.face.opacity = 1.0
                if not icon_text:
                    icon_text = ""
        else:
            if hasattr(self, "stick_figure_icon"):
                self.stick_figure_icon.opacity = 0.0
            self.icon_image.opacity = 0.0
            self.face.opacity = 1.0
            if not icon_text:
                icon_text = ""
        
        # Apply face style and bar (even if face is hidden, bar still shows)
        self.face.set_style(accent, mood)
        self.draw_bar(accent)
        
        # Display reminder text (nullable)
        title = reminder.get("text", "Reminder")
        self.title.text = f"[b][color=#9BE7FF]{icon_text} {title}[/color][/b]" if icon_text else f"[b][color=#9BE7FF]{title}[/color][/b]"
        # Use description if available, otherwise use text as line
        description = reminder.get("description")
        if description:
            self.line.text = f"[color=#E6F4FF]{description}[/color]"
        else:
            # Fallback: show text in line if no description
            self.line.text = f"[color=#E6F4FF]{reminder.get('text', '')}[/color]"
        self._refresh_status_row_visibility()
    
    def dismiss(self):
        """Dismiss current reminder overlay."""
        self.line.text = "Dismissed!"
    
    def _normalize_trigger_time(self, time_str):
        """Normalize stored trigger time to HH:MM for reliable comparison."""
        if not time_str or not isinstance(time_str, str):
            return ""
        parts = time_str.strip().split(":")
        if len(parts) != 2:
            return ""
        try:
            h, m = int(parts[0]), int(parts[1])
            if h < 0 or h > 23 or m < 0 or m > 59:
                return ""
            return f"{h:02d}:{m:02d}"
        except (ValueError, TypeError):
            return ""

    def check_reminders(self, dt):
        """
        Reminder scheduler engine.
        Checks every second if any active reminder should trigger based on trigger_time or interval.
        """
        now = datetime.now()
        current_time = now.strftime("%H:%M")  # Always "HH:MM" (e.g. 09:00, 12:58)
        current_date = now.strftime("%Y-%m-%d")
        current_minute = f"{current_date} {current_time}"
        current_timestamp = now.timestamp()
        
        reminders = config_manager.get("reminders", [])
        last_fired = config_manager.get("last_fired", {})
        
        for reminder in reminders:
            if not reminder.get("is_active", True):
                continue
            
            # Get stable reminder ID (must exist, generated on creation)
            reminder_id = reminder.get("id")
            if not reminder_id:
                # Legacy reminder without ID - generate one and save it
                reminder_id = str(uuid.uuid4())
                reminder["id"] = reminder_id
                config_manager.set("reminders", reminders)
            
            trigger_type = reminder.get("trigger_type", "Specific Time")
            should_trigger = False
            
            if trigger_type == "Every X Minutes":
                # Interval-based reminder
                interval_minutes = reminder.get("interval_minutes", 5)
                last_fired_time = last_fired.get(reminder_id)
                
                if last_fired_time is None:
                    # Never fired - trigger immediately
                    should_trigger = True
                else:
                    # Check if enough time has passed
                    try:
                        # Parse last fired timestamp
                        if isinstance(last_fired_time, str):
                            # Old format: "YYYY-MM-DD HH:MM"
                            last_dt = datetime.strptime(last_fired_time, "%Y-%m-%d %H:%M")
                        else:
                            # New format: timestamp
                            last_dt = datetime.fromtimestamp(last_fired_time)
                        
                        minutes_passed = (now - last_dt).total_seconds() / 60.0
                        if minutes_passed >= interval_minutes:
                            should_trigger = True
                    except (ValueError, TypeError):
                        # Invalid format - trigger anyway
                        should_trigger = True
            else:
                # Time-based reminder: compare normalized HH:MM
                raw_trigger = reminder.get("trigger_time", "")
                trigger_time = self._normalize_trigger_time(raw_trigger)
                if not trigger_time or trigger_time != current_time:
                    continue
                
                # Check if already fired this minute (prevent repeated triggers)
                if last_fired.get(reminder_id) == current_minute:
                    continue
                
                should_trigger = True
            
            if not should_trigger:
                continue
            
            # Check repeat settings (for time-based reminders)
            if trigger_type == "Specific Time":
                repeat_settings = reminder.get("repeat_settings", "once")
                if not self.repeat_allows_today(repeat_settings, now):
                    continue

            if getattr(self, "_ai_conversation_active", False):
                if trigger_type == "Every X Minutes":
                    dkey = (reminder_id, f"iv_{int(current_timestamp)}")
                    last_fired[reminder_id] = current_timestamp
                else:
                    dkey = (reminder_id, current_minute)
                    last_fired[reminder_id] = current_minute
                if dkey not in self._deferred_reminder_keys:
                    self._deferred_reminder_keys.add(dkey)
                    self._deferred_reminder_queue.append(reminder)
                config_manager.set("last_fired", last_fired)
                if trigger_type == "Specific Time" and reminder.get("repeat_settings") == "once":
                    reminder["is_active"] = False
                    config_manager.set("reminders", reminders)
                continue
            
            # Remember where to return after 1 minute
            self._return_screen = self.manager.current
            self.manager.current = "homescreen"
            self.trigger_reminder(reminder, is_real_trigger=True)
            
            # Mark as fired (use timestamp for interval, minute string for time-based)
            if trigger_type == "Every X Minutes":
                last_fired[reminder_id] = current_timestamp
            else:
                last_fired[reminder_id] = current_minute
            config_manager.set("last_fired", last_fired)
            
            # If "once" repeat (time-based only), disable the reminder after firing
            if trigger_type == "Specific Time" and reminder.get("repeat_settings") == "once":
                reminder["is_active"] = False
                config_manager.set("reminders", reminders)
                # Reload active reminders
                self.load_reminders()
    
    def repeat_allows_today(self, repeat_settings, now):
        """
        Check if repeat settings allow reminder to fire today.
        
        Args:
            repeat_settings: String like "daily", "weekly", "once", "weekdays", etc.
            now: datetime object for current time
        
        Returns:
            bool: True if reminder should fire today
        """
        if repeat_settings == "once":
            # "once" is handled by disabling after firing, so always allow if active
            return True
        elif repeat_settings == "daily":
            return True
        elif repeat_settings == "weekdays":
            return now.weekday() < 5  # Monday=0, Friday=4
        elif repeat_settings == "weekends":
            return now.weekday() >= 5  # Saturday=5, Sunday=6
        elif repeat_settings == "weekly":
            # Fire once per week (check last_fired for same weekday)
            return True  # Simplified - could check last week's date
        else:
            return True  # Default: allow
    
    REMINDER_DISPLAY_SECONDS = 60  # Show reminder for 1 minute then return

    def trigger_reminder(self, reminder, is_real_trigger=False):
        """
        Trigger a reminder - display it on the homescreen for 1 minute, then return to previous screen.
        
        Args:
            reminder: Dictionary containing reminder data
            is_real_trigger: If True, we have already set _return_screen in check_reminders.
        """
        if not is_real_trigger and not hasattr(self, '_return_screen'):
            # Test-in-10 or other call: remember current screen for return (if not already set by caller)
            self._return_screen = self.manager.current
        # For is_real_trigger, _return_screen was set in check_reminders before switching
        
        self.apply_card(reminder)
        self.triggered_reminder_showing = True
        self.cycling_paused_until = datetime.now().timestamp() + float(self.REMINDER_DISPLAY_SECONDS)

        def _after_reminder_duration(dt):
            self.triggered_reminder_showing = False
            self.cycling_paused_until = None
            return_to = getattr(self, '_return_screen', 'homescreen')
            if return_to != 'homescreen':
                self.manager.current = return_to
            else:
                # Stay on homescreen; show default view (reminder count only)
                self.load_reminders()

        Clock.schedule_once(_after_reminder_duration, self.REMINDER_DISPLAY_SECONDS)
    
    def cycle_if_allowed(self, dt):
        """Cycle to next reminder only if no triggered reminder is showing."""
        # Don't cycle if a triggered reminder is currently displayed
        if self.triggered_reminder_showing:
            return
        
        # Don't cycle if still in pause period
        if self.cycling_paused_until and datetime.now().timestamp() < self.cycling_paused_until:
            return
        
        self.next_card()
    
    def next_card(self):
        """Cycle to the next active reminder."""
        if self.active_reminders:
            self.idx = (self.idx + 1) % len(self.active_reminders)
            self.apply_card(self.active_reminders[self.idx])
    
    # Removed open_settings - homescreen only has Home button now


class SettingsScreen(Screen):
    """
    Settings screen - simplified to only provide access to Tools.
    Face customization is handled in the 3-page setup flow.
    """
    
    def __init__(self, **kwargs):
        """Initialize the settings screen."""
        super().__init__(**kwargs)
        self.setup_ui()

    def on_pre_enter(self, *args):
        # No name entry required; greeting is generic.
        return
    
    def setup_ui(self):
        """Build the simplified settings UI."""
        layout = FloatLayout()
        
        # Background
        with layout.canvas.before:
            Color(*UI["BG"])
            Rectangle(pos=layout.pos, size=Window.size)
            Color(0.12, 0.18, 0.30, 0.20)
            RoundedRectangle(pos=(dp(14), dp(14)), size=(Window.width - dp(28), Window.height - dp(28)), radius=[dp(22)])
        
        # Title
        title = Label(
            text="Settings",
            font_size="36sp",
            bold=True,
            color=(1, 1, 1, 1),
            halign="center",
            valign="top",
            size_hint=(1, 0.15),
            pos_hint={"x": 0, "y": 0.85}
        )
        layout.add_widget(title)
        
        # Info message
        info_label = Label(
            text="To customize your robot's face,\nuse the Customize option from Home.",
            font_size="20sp",
            color=(0.8, 0.8, 1, 1),
            halign="center",
            size_hint=(1, 0.15),
            pos_hint={"x": 0, "y": 0.65}
        )
        layout.add_widget(info_label)

        # (Name entry removed intentionally)
        
        # Tools → Reminders button
        tools_btn = Button(
            text="Tools: Reminders",
            size_hint=(0.4, 0.12),
            pos_hint={"center_x": 0.5, "center_y": 0.45},
            font_size="24sp",
            bold=True,
            background_color=(0.6, 0.4, 0.8, 1.0),
            background_normal='',
            background_down='',
            color=(1, 1, 1, 1)
        )
        tools_btn.bind(on_release=lambda *_: setattr(self.manager, "current", "reminders"))
        layout.add_widget(tools_btn)
        
        # Return to Homescreen button
        home_btn = Button(
            text="← Return to Homescreen",
            size_hint=(0.4, 0.10),
            pos_hint={"center_x": 0.5, "y": 0.20},
            font_size="20sp",
            background_color=(0.3, 0.7, 0.4, 1.0),
            background_normal='',
            background_down='',
            color=(1, 1, 1, 1)
        )
        home_btn.bind(on_release=self.return_home)
        layout.add_widget(home_btn)
        
        self.add_widget(layout)
    
    def return_home(self, instance):
        """Navigate back to homescreen."""
        self.manager.current = "homescreen"


class ReminderEditScreen(Screen):
    """
    Screen for editing/creating reminders with all fields:
    - Text (nullable)
    - Icon (nullable)
    - Face expression (nullable, but requires eyes/mouth to be defined)
    - Trigger Time
    - Repeat Settings
    - is_active flag
    """
    REMINDER_TEMPLATES = {
        "Drink Water": {
            "text": "Drink water",
            "description": "Stay hydrated.",
            "action": "drink",
            "icon_path": "assets/icons/drink_water.png",
            "mood": "happy",
        },
        "Exercise": {
            "text": "Exercise break",
            "description": "Move your body for a few minutes.",
            "action": "exercise",
            "icon_path": "assets/icons/stretch.png",
            "mood": "focused",
        },
        "Stretch": {
            "text": "Get up and stretch",
            "description": "Stand, stretch shoulders and back.",
            "action": "stretch",
            "icon_path": "assets/icons/stretch.png",
            "mood": "calm",
        },
        "Mindful Breathing": {
            "text": "Take a mindful breath",
            "description": "Pause and take 5 deep breaths.",
            "action": None,
            "icon_path": None,
            "mood": "calm",
        },
        "Take a short walk": {
            "text": "Take a short walk",
            "description": "Move around for 3-5 minutes.",
            "action": "stretch",
            "icon_path": "assets/icons/stretch.png",
            "mood": "happy",
        },
        "Healthy Snack": {
            "text": "Grab a healthy snack",
            "description": "Choose fruit, nuts, or yogurt.",
            "action": None,
            "icon_path": None,
            "mood": "happy",
        },
        "Custom": None,
    }
    COLOR_PRESETS = [
        ("Blue", [0.10, 0.90, 1.00, 1.0]),
        ("Green", [0.15, 1.00, 0.55, 1.0]),
        ("Purple", [0.65, 0.52, 1.00, 1.0]),
        ("Orange", [1.00, 0.72, 0.35, 1.0]),
        ("Pink", [1.00, 0.55, 0.80, 1.0]),
    ]
    
    def __init__(self, reminder_index=None, **kwargs):
        """Initialize the reminder edit screen."""
        super().__init__(**kwargs)
        self.reminder_index = reminder_index
        self.setup_ui()
    
    def setup_ui(self):
        """Build the reminder edit UI with proper spacing and ScrollView."""
        # Main container
        main_layout = FloatLayout()
        
        # Background
        with main_layout.canvas.before:
            Color(0.05, 0.05, 0.10, 1.0)
            Rectangle(pos=main_layout.pos, size=Window.size)
        
        # Title (fixed at top)
        self.title_label = Label(
            text="Edit Reminder",
            font_size="36sp",
            bold=True,
            color=(1, 1, 1, 1),
            halign="center",
            valign="top",
            size_hint=(1, 0.10),
            pos_hint={"x": 0, "y": 0.90}
        )
        main_layout.add_widget(self.title_label)
        
        # Scrollable form area
        self.scroll = ScrollView(
            size_hint=(1, 0.75),
            pos_hint={"x": 0, "y": 0.15},
            do_scroll_x=False,
            do_scroll_y=True
        )
        
        # Form container with proper spacing
        form_layout = BoxLayout(
            orientation="vertical",
            spacing=dp(15),
            padding=dp(20),
            size_hint_y=None
        )
        form_layout.bind(minimum_height=form_layout.setter('height'))
        
        # Text input section
        text_container = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(50), spacing=dp(10))
        text_label = Label(
            text="Text:",
            font_size="20sp",
            color=(0.9, 0.9, 1, 1),
            halign="left",
            size_hint_x=0.25,
            text_size=(None, None)
        )
        self.text_input = TextInput(
            text="",
            multiline=False,
            size_hint_x=0.75,
            font_size="18sp",
            background_color=(0.15, 0.15, 0.20, 1.0),
            foreground_color=(1, 1, 1, 1),
            padding=dp(10)
        )
        text_container.add_widget(text_label)
        text_container.add_widget(self.text_input)
        form_layout.add_widget(text_container)

        # Reminder type presets
        type_container = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(50), spacing=dp(10))
        type_label = Label(
            text="Reminder Type:",
            font_size="20sp",
            color=(0.9, 0.9, 1, 1),
            halign="left",
            size_hint_x=0.3,
            text_size=(None, None),
        )
        self.template_dropdown = DropDown()
        self.template_btn = Button(
            text="Custom",
            size_hint_x=0.45,
            font_size="16sp",
            background_color=(0.3, 0.5, 0.8, 1.0),
            background_normal='',
            background_down='',
            color=(1, 1, 1, 1),
        )
        for option in self.REMINDER_TEMPLATES.keys():
            btn = Button(text=option, size_hint_y=None, height=dp(45), font_size="16sp")
            btn.bind(on_release=lambda b, opt=option: self.select_template(opt))
            self.template_dropdown.add_widget(btn)
        self.template_btn.bind(on_release=self.template_dropdown.open)
        type_container.add_widget(type_label)
        type_container.add_widget(self.template_btn)
        type_container.add_widget(Widget())
        form_layout.add_widget(type_container)
        
        # Icon selection section (image file path)
        icon_container = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(80), spacing=dp(5))
        icon_label = Label(
            text="Icon (image file):",
            font_size="20sp",
            color=(0.9, 0.9, 1, 1),
            halign="left",
            size_hint_y=0.4,
            text_size=(None, None)
        )
        icon_row = BoxLayout(orientation="horizontal", size_hint_y=0.6, spacing=dp(8))
        
        # Icon dropdown with predefined options (using relative paths)
        self.icon_dropdown = DropDown()
        icon_options = [
            ("None", None),
            ("Drink Water", "assets/icons/drink_water.png"),
            ("Stretch", "assets/icons/stretch.png"),
            ("Custom Path", "CUSTOM")
        ]
        self.icon_btn = Button(
            text="None",
            size_hint_x=0.35,
            font_size="16sp",
            background_color=(0.3, 0.5, 0.8, 1.0),
            background_normal='',
            background_down='',
            color=(1, 1, 1, 1)
        )
        for label, path in icon_options:
            btn = Button(text=label, size_hint_y=None, height=dp(40), font_size="16sp")
            btn.bind(on_release=lambda b, p=path, lbl=label: self._select_icon(p, lbl))
            self.icon_dropdown.add_widget(btn)
        self.icon_btn.bind(on_release=self.icon_dropdown.open)
        
        # Custom path input (shown when "Custom Path" selected)
        self.icon_path_input = TextInput(
            text="",
            multiline=False,
            size_hint_x=0.6,
            font_size="14sp",
            background_color=(0.15, 0.15, 0.20, 1.0),
            foreground_color=(1, 1, 1, 1),
            padding=dp(8),
            hint_text="assets/icons/icon.png",
            disabled=True
        )
        icon_row.add_widget(self.icon_btn)
        icon_row.add_widget(self.icon_path_input)
        icon_container.add_widget(icon_label)
        icon_container.add_widget(icon_row)
        self.icon_input = TextInput(
            text="",
            multiline=False,
            size_hint_y=None,
            height=dp(34),
            font_size="14sp",
            background_color=(0.12, 0.12, 0.18, 1.0),
            foreground_color=(0.9, 0.95, 1, 1),
            padding=dp(8),
            hint_text="Optional short icon text (e.g., water)",
        )
        icon_container.add_widget(self.icon_input)
        form_layout.add_widget(icon_container)
        
        # Description input section
        desc_container = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(100), spacing=dp(5))
        desc_label = Label(
            text="Description:",
            font_size="20sp",
            color=(0.9, 0.9, 1, 1),
            halign="left",
            size_hint_y=0.3,
            text_size=(None, None)
        )
        self.description_input = TextInput(
            text="",
            multiline=True,
            size_hint_y=0.7,
            font_size="16sp",
            background_color=(0.15, 0.15, 0.20, 1.0),
            foreground_color=(1, 1, 1, 1),
            padding=dp(10)
        )
        desc_container.add_widget(desc_label)
        desc_container.add_widget(self.description_input)
        form_layout.add_widget(desc_container)
        
        # Trigger Type section (Time or Interval)
        trigger_type_container = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(50), spacing=dp(10))
        trigger_type_label = Label(
            text="Trigger Type:",
            font_size="20sp",
            color=(0.9, 0.9, 1, 1),
            halign="left",
            size_hint_x=0.3,
            text_size=(None, None)
        )
        self.trigger_type_dropdown = DropDown()
        self.trigger_type_btn = Button(
            text="Specific Time",
            size_hint_x=0.35,
            font_size="16sp",
            background_color=(0.3, 0.5, 0.8, 1.0),
            background_normal='',
            background_down='',
            color=(1, 1, 1, 1)
        )
        for option in ["Specific Time", "Every X Minutes"]:
            btn = Button(text=option, size_hint_y=None, height=dp(45), font_size="16sp")
            btn.bind(on_release=lambda b, opt=option: self.select_trigger_type(opt))
            self.trigger_type_dropdown.add_widget(btn)
        self.trigger_type_btn.bind(on_release=self.trigger_type_dropdown.open)
        trigger_type_container.add_widget(trigger_type_label)
        trigger_type_container.add_widget(self.trigger_type_btn)
        trigger_type_container.add_widget(Widget())  # Spacer
        form_layout.add_widget(trigger_type_container)
        
        # Trigger Time section (shown when "Specific Time" is selected)
        time_container = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(50), spacing=dp(10))
        time_label = Label(
            text="Time (e.g. 2:30):",
            font_size="20sp",
            color=(0.9, 0.9, 1, 1),
            halign="left",
            size_hint_x=0.25,
            text_size=(None, None)
        )
        self.time_input = TextInput(
            text="12:00",
            multiline=False,
            size_hint_x=0.2,
            font_size="18sp",
            background_color=(0.15, 0.15, 0.20, 1.0),
            foreground_color=(1, 1, 1, 1),
            padding=dp(10)
        )
        # AM/PM selector
        self.am_pm_dropdown = DropDown()
        self.am_pm_btn = Button(
            text="PM",
            size_hint_x=0.15,
            font_size="18sp",
            background_color=(0.3, 0.5, 0.8, 1.0),
            background_normal='',
            background_down='',
            color=(1, 1, 1, 1)
        )
        for option in ["AM", "PM"]:
            btn = Button(text=option, size_hint_y=None, height=dp(45), font_size="16sp")
            btn.bind(on_release=lambda b, opt=option: self._select_am_pm(opt))
            self.am_pm_dropdown.add_widget(btn)
        self.am_pm_btn.bind(on_release=self.am_pm_dropdown.open)
        time_container.add_widget(time_label)
        time_container.add_widget(self.time_input)
        time_container.add_widget(self.am_pm_btn)
        time_container.add_widget(Widget())  # Spacer
        form_layout.add_widget(time_container)
        
        # Interval Minutes section (shown when "Every X Minutes" is selected)
        interval_container = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(50), spacing=dp(10))
        interval_label = Label(
            text="Every (minutes):",
            font_size="20sp",
            color=(0.9, 0.9, 1, 1),
            halign="left",
            size_hint_x=0.3,
            text_size=(None, None)
        )
        self.interval_input = TextInput(
            text="5",
            multiline=False,
            size_hint_x=0.3,
            font_size="18sp",
            background_color=(0.15, 0.15, 0.20, 1.0),
            foreground_color=(1, 1, 1, 1),
            padding=dp(10),
            disabled=True  # Disabled by default (only enabled for interval type)
        )
        interval_container.add_widget(interval_label)
        interval_container.add_widget(self.interval_input)
        interval_container.add_widget(Widget())  # Spacer
        form_layout.add_widget(interval_container)
        
        # Repeat Settings section
        repeat_container = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(50), spacing=dp(10))
        repeat_label = Label(
            text="Repeat:",
            font_size="20sp",
            color=(0.9, 0.9, 1, 1),
            halign="left",
            size_hint_x=0.25,
            text_size=(None, None)
        )
        self.repeat_dropdown = DropDown()
        self.repeat_btn = Button(
            text="daily",
            size_hint_x=0.35,
            font_size="18sp",
            background_color=(0.3, 0.5, 0.8, 1.0),
            background_normal='',
            background_down='',
            color=(1, 1, 1, 1)
        )
        for option in ["once", "daily", "weekdays", "weekends", "weekly"]:
            btn = Button(text=option, size_hint_y=None, height=dp(45), font_size="16sp")
            btn.bind(on_release=lambda b, opt=option: self.select_repeat(opt))
            self.repeat_dropdown.add_widget(btn)
        self.repeat_btn.bind(on_release=self.repeat_dropdown.open)
        repeat_container.add_widget(repeat_label)
        repeat_container.add_widget(self.repeat_btn)
        repeat_container.add_widget(Widget())  # Spacer
        form_layout.add_widget(repeat_container)

        # Per-reminder accent color
        color_container = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(50), spacing=dp(10))
        color_label = Label(
            text="Reminder Color:",
            font_size="20sp",
            color=(0.9, 0.9, 1, 1),
            halign="left",
            size_hint_x=0.3,
            text_size=(None, None),
        )
        self.accent_dropdown = DropDown()
        self.accent_btn = Button(
            text="Default",
            size_hint_x=0.35,
            font_size="16sp",
            background_color=(0.3, 0.5, 0.8, 1.0),
            background_normal='',
            background_down='',
            color=(1, 1, 1, 1),
        )
        for label, color in self.COLOR_PRESETS:
            btn = Button(text=label, size_hint_y=None, height=dp(45), font_size="16sp")
            btn.bind(on_release=lambda b, lbl=label, c=color: self.select_accent(lbl, c))
            self.accent_dropdown.add_widget(btn)
        self.accent_btn.bind(on_release=self.accent_dropdown.open)
        self.selected_accent = list(config_manager.get("default_colors.primary", [0.10, 0.90, 1.00, 1.0]))
        color_container.add_widget(color_label)
        color_container.add_widget(self.accent_btn)
        color_container.add_widget(Widget())
        form_layout.add_widget(color_container)
        
        # Face Expression toggle section
        face_expr_container = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(50), spacing=dp(10))
        face_label = Label(
            text="Face Expression:",
            font_size="20sp",
            color=(0.9, 0.9, 1, 1),
            halign="left",
            size_hint_x=0.4,
            text_size=(None, None)
        )
        self.use_face_expr = ToggleButton(
            text="Use Face Expression",
            size_hint_x=0.5,
            font_size="16sp",
            background_color=(0.5, 0.3, 0.7, 1.0),
            background_normal='',
            background_down='',
            color=(1, 1, 1, 1)
        )
        self.use_face_expr.bind(state=self.on_face_expr_toggle)
        face_expr_container.add_widget(face_label)
        face_expr_container.add_widget(self.use_face_expr)
        face_expr_container.add_widget(Widget())  # Spacer
        form_layout.add_widget(face_expr_container)
        
        # Face expression options (only shown when toggle is on)
        fe_options_container = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(180), spacing=dp(10))
        
        # FE Eyes
        fe_eyes_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(50), spacing=dp(10))
        fe_eyes_label = Label(
            text="FE Eyes:",
            font_size="18sp",
            color=(0.8, 0.8, 1, 1),
            halign="left",
            size_hint_x=0.3,
            text_size=(None, None)
        )
        self.fe_eyes_dropdown = DropDown()
        self.fe_eyes_btn = Button(
            text="None",
            size_hint_x=0.4,
            font_size="16sp",
            disabled=True,
            background_color=(0.4, 0.4, 0.5, 0.5),
            background_normal='',
            background_down='',
            color=(0.7, 0.7, 0.7, 1.0)
        )
        for option in ["None", "Round", "Oval", "Narrow", "Wide", "Small"]:
            btn = Button(text=option, size_hint_y=None, height=dp(40), font_size="16sp")
            btn.bind(on_release=lambda b, opt=option: self.select_fe_eyes(opt))
            self.fe_eyes_dropdown.add_widget(btn)
        self.fe_eyes_btn.bind(on_release=self.fe_eyes_dropdown.open)
        fe_eyes_row.add_widget(fe_eyes_label)
        fe_eyes_row.add_widget(self.fe_eyes_btn)
        fe_eyes_row.add_widget(Widget())  # Spacer
        fe_options_container.add_widget(fe_eyes_row)
        
        # FE Mouth
        fe_mouth_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(50), spacing=dp(10))
        fe_mouth_label = Label(
            text="FE Mouth:",
            font_size="18sp",
            color=(0.8, 0.8, 1, 1),
            halign="left",
            size_hint_x=0.3,
            text_size=(None, None)
        )
        self.fe_mouth_dropdown = DropDown()
        self.fe_mouth_btn = Button(
            text="None",
            size_hint_x=0.4,
            font_size="16sp",
            disabled=True,
            background_color=(0.4, 0.4, 0.5, 0.5),
            background_normal='',
            background_down='',
            color=(0.7, 0.7, 0.7, 1.0)
        )
        for option in ["None", "Wide", "Small", "Expressive", "Neutral", "Curved", "Smile"]:
            btn = Button(text=option, size_hint_y=None, height=dp(40), font_size="16sp")
            btn.bind(on_release=lambda b, opt=option: self.select_fe_mouth(opt))
            self.fe_mouth_dropdown.add_widget(btn)
        self.fe_mouth_btn.bind(on_release=self.fe_mouth_dropdown.open)
        fe_mouth_row.add_widget(fe_mouth_label)
        fe_mouth_row.add_widget(self.fe_mouth_btn)
        fe_mouth_row.add_widget(Widget())  # Spacer
        fe_options_container.add_widget(fe_mouth_row)
        
        # Mood
        mood_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(50), spacing=dp(10))
        mood_label = Label(
            text="Mood:",
            font_size="18sp",
            color=(0.8, 0.8, 1, 1),
            halign="left",
            size_hint_x=0.3,
            text_size=(None, None)
        )
        self.mood_dropdown = DropDown()
        self.mood_btn = Button(
            text="happy",
            size_hint_x=0.4,
            font_size="16sp",
            disabled=True,
            background_color=(0.4, 0.4, 0.5, 0.5),
            background_normal='',
            background_down='',
            color=(0.7, 0.7, 0.7, 1.0)
        )
        for option in ["happy", "calm", "wink", "focused"]:
            btn = Button(text=option, size_hint_y=None, height=dp(40), font_size="16sp")
            btn.bind(on_release=lambda b, opt=option: self.select_mood(opt))
            self.mood_dropdown.add_widget(btn)
        self.mood_btn.bind(on_release=self.mood_dropdown.open)
        mood_row.add_widget(mood_label)
        mood_row.add_widget(self.mood_btn)
        mood_row.add_widget(Widget())  # Spacer
        fe_options_container.add_widget(mood_row)
        
        form_layout.add_widget(fe_options_container)
        
        # Active toggle section (must be ON for reminder to trigger at set time)
        active_container = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(50), spacing=dp(10))
        active_label = Label(
            text="Active (ON = shows at set time):",
            font_size="20sp",
            color=(0.9, 0.9, 1, 1),
            halign="left",
            size_hint_x=0.45,
            text_size=(None, None)
        )
        self.is_active_toggle = ToggleButton(
            text="Active",
            state="down",
            size_hint_x=0.25,
            font_size="18sp",
            background_color=(0.2, 0.7, 0.3, 1.0),
            background_normal='',
            background_down='',
            color=(1, 1, 1, 1)
        )
        active_container.add_widget(active_label)
        active_container.add_widget(self.is_active_toggle)
        active_container.add_widget(Widget())  # Spacer
        form_layout.add_widget(active_container)
        
        # Error message
        self.error_label = Label(
            text="",
            font_size="16sp",
            color=(1, 0.3, 0.3, 1),
            halign="center",
            size_hint_y=None,
            height=dp(30),
            text_size=(None, None)
        )
        form_layout.add_widget(self.error_label)
        
        # Add form to scroll view
        self.scroll.add_widget(form_layout)
        main_layout.add_widget(self.scroll)
        
        # Fixed bottom buttons with better styling
        button_container = BoxLayout(
            orientation="horizontal",
            spacing=dp(15),
            padding=dp(15),
            size_hint=(1, 0.12),
            pos_hint={"x": 0, "y": 0}
        )
        
        cancel_btn = Button(
            text="Cancel",
            size_hint_x=0.28,
            font_size="18sp",
            bold=True,
            background_color=(0.5, 0.5, 0.5, 1.0),
            background_normal='',
            background_down='',
            color=(1, 1, 1, 1)
        )
        cancel_btn.bind(on_release=self.cancel)
        button_container.add_widget(cancel_btn)
        
        test_btn = Button(
            text="Test in 10 sec",
            size_hint_x=0.28,
            font_size="18sp",
            bold=True,
            background_color=(0.6, 0.4, 0.9, 1.0),
            background_normal='',
            background_down='',
            color=(1, 1, 1, 1)
        )
        test_btn.bind(on_release=self.test_in_10_seconds)
        button_container.add_widget(test_btn)
        
        save_btn = Button(
            text="Save",
            size_hint_x=0.28,
            font_size="18sp",
            bold=True,
            background_color=(0.2, 0.8, 0.4, 1.0),
            background_normal='',
            background_down='',
            color=(1, 1, 1, 1)
        )
        save_btn.bind(on_release=self.save)
        button_container.add_widget(save_btn)
        
        main_layout.add_widget(button_container)
        
        self.add_widget(main_layout)
    
    def on_face_expr_toggle(self, instance, value):
        """Enable/disable face expression controls based on toggle state."""
        enabled = value == "down"
        self.fe_eyes_btn.disabled = not enabled
        self.fe_mouth_btn.disabled = not enabled
        self.mood_btn.disabled = not enabled
        
        # Update button appearance
        if enabled:
            self.fe_eyes_btn.background_color = (0.4, 0.5, 0.7, 1.0)
            self.fe_eyes_btn.color = (1, 1, 1, 1)
            self.fe_mouth_btn.background_color = (0.4, 0.5, 0.7, 1.0)
            self.fe_mouth_btn.color = (1, 1, 1, 1)
            self.mood_btn.background_color = (0.4, 0.5, 0.7, 1.0)
            self.mood_btn.color = (1, 1, 1, 1)
        else:
            self.fe_eyes_btn.background_color = (0.4, 0.4, 0.5, 0.5)
            self.fe_eyes_btn.color = (0.7, 0.7, 0.7, 1.0)
            self.fe_mouth_btn.background_color = (0.4, 0.4, 0.5, 0.5)
            self.fe_mouth_btn.color = (0.7, 0.7, 0.7, 1.0)
            self.mood_btn.background_color = (0.4, 0.4, 0.5, 0.5)
            self.mood_btn.color = (0.7, 0.7, 0.7, 1.0)
    
    def setup_for_new(self):
        """Setup screen for creating a new reminder."""
        self.title_label.text = "New Reminder"
        self.reminder_index = None
        self.text_input.text = ""
        self.description_input.text = ""
        self.icon_input.text = ""
        self.icon_btn.text = "None"
        self.icon_path_input.text = ""
        self.icon_path_input.disabled = True
        self.template_btn.text = "Custom"
        self.trigger_type_btn.text = "Specific Time"
        self.time_input.text = "12:00"
        self.am_pm_btn.text = "PM"
        self.time_input.disabled = False
        self.interval_input.text = "5"
        self.interval_input.disabled = True
        self.repeat_btn.text = "daily"
        self.selected_accent = list(config_manager.get("default_colors.primary", [0.10, 0.90, 1.00, 1.0]))
        self.accent_btn.text = "Default"
        self.use_face_expr.state = "normal"
        self.fe_eyes_btn.text = "None"
        self.fe_mouth_btn.text = "None"
        self.mood_btn.text = "happy"
        self.is_active_toggle.state = "down"
        self.error_label.text = ""
        # Update disabled state and appearance
        self.on_face_expr_toggle(self.use_face_expr, "normal")
    
    def setup_for_edit(self, index):
        """Setup screen for editing an existing reminder."""
        self.title_label.text = "Edit Reminder"
        self.reminder_index = index
        reminders = config_manager.get("reminders", [])
        if 0 <= index < len(reminders):
            reminder = reminders[index]
            self.text_input.text = reminder.get("text", "")
            self.description_input.text = reminder.get("description", "")
            self.template_btn.text = "Custom"
            current_text = (self.text_input.text or "").strip().lower()
            for option, preset in self.REMINDER_TEMPLATES.items():
                if not preset:
                    continue
                if (preset.get("text", "").strip().lower() == current_text):
                    self.template_btn.text = option
                    break
            self.icon_input.text = reminder.get("icon", "")
            # Load icon_path (handle both relative and absolute paths)
            icon_path = reminder.get("icon_path")
            if icon_path:
                # Normalize to relative path for comparison
                script_dir = os.path.dirname(os.path.abspath(__file__))
                if os.path.isabs(icon_path):
                    # Convert absolute to relative if in project
                    if icon_path.startswith(script_dir):
                        icon_path_rel = os.path.relpath(icon_path, script_dir)
                    else:
                        icon_path_rel = icon_path  # Keep absolute if outside project
                else:
                    icon_path_rel = icon_path
                
                if icon_path_rel == "assets/icons/drink_water.png":
                    self.icon_btn.text = "Drink Water"
                    self.icon_path_input.text = icon_path_rel
                    self.icon_path_input.disabled = True
                elif icon_path_rel == "assets/icons/stretch.png":
                    self.icon_btn.text = "Stretch"
                    self.icon_path_input.text = icon_path_rel
                    self.icon_path_input.disabled = True
                else:
                    self.icon_btn.text = "Custom Path"
                    self.icon_path_input.text = icon_path_rel
                    self.icon_path_input.disabled = False
            else:
                self.icon_btn.text = "None"
                self.icon_path_input.text = ""
                self.icon_path_input.disabled = True
            
            # Load trigger type and values
            trigger_type = reminder.get("trigger_type", "Specific Time")
            self.trigger_type_btn.text = trigger_type
            if trigger_type == "Every X Minutes":
                self.time_input.disabled = True
                self.interval_input.disabled = False
                self.interval_input.text = str(reminder.get("interval_minutes", 5))
            else:
                self.time_input.disabled = False
                self.interval_input.disabled = True
                # Load 24h time and show as 12h + AM/PM
                stored_time = reminder.get("trigger_time", "12:00")
                display_12h, display_am_pm = self._time_24h_to_12h_display(stored_time)
                self.time_input.text = display_12h
                self.am_pm_btn.text = display_am_pm
            
            self.repeat_btn.text = reminder.get("repeat_settings", "daily")
            saved_accent = reminder.get("accent", config_manager.get("default_colors.primary", [0.10, 0.90, 1.00, 1.0]))
            self.selected_accent = list(saved_accent) if isinstance(saved_accent, (list, tuple)) else list(config_manager.get("default_colors.primary", [0.10, 0.90, 1.00, 1.0]))
            self.accent_btn.text = "Custom"
            for label, color in self.COLOR_PRESETS:
                if list(color) == self.selected_accent:
                    self.accent_btn.text = label
                    break
            
            face_expr = reminder.get("face_expression")
            if face_expr and isinstance(face_expr, dict):
                self.use_face_expr.state = "down"
                self.fe_eyes_btn.text = face_expr.get("eyes") or "None"
                self.fe_mouth_btn.text = face_expr.get("mouth") or "None"
                self.mood_btn.text = face_expr.get("mood", "happy")
            else:
                self.use_face_expr.state = "normal"
                self.fe_eyes_btn.text = "None"
                self.fe_mouth_btn.text = "None"
                self.mood_btn.text = reminder.get("mood", "happy")
            
            self.is_active_toggle.state = "down" if reminder.get("is_active", True) else "normal"
            # Update disabled state and appearance
            self.on_face_expr_toggle(self.use_face_expr, self.use_face_expr.state)
        self.error_label.text = ""
        
        # Scroll to top when editing
        if hasattr(self, 'scroll'):
            Clock.schedule_once(lambda dt: setattr(self.scroll, 'scroll_y', 1.0), 0.1)
    
    def _select_am_pm(self, option):
        """Handle AM/PM selection."""
        self.am_pm_dropdown.dismiss()
        self.am_pm_btn.text = option

    def _time_12h_to_24h(self, time_str_12h, am_pm):
        """Convert 12-hour time string + AM/PM to 24-hour HH:MM string."""
        try:
            parts = time_str_12h.strip().split(":")
            if len(parts) != 2:
                return None
            hour, minute = int(parts[0]), int(parts[1])
            if not (1 <= hour <= 12 and 0 <= minute < 60):
                return None
            if am_pm == "PM":
                hour = 12 if hour == 12 else hour + 12
            else:  # AM
                hour = 0 if hour == 12 else hour
            return f"{hour:02d}:{minute:02d}"
        except (ValueError, IndexError):
            return None

    def _time_24h_to_12h_display(self, time_str_24h):
        """Convert 24-hour HH:MM string to (12h_display, AM_or_PM)."""
        try:
            parts = time_str_24h.strip().split(":")
            if len(parts) != 2:
                return "12:00", "PM"
            hour, minute = int(parts[0]), int(parts[1])
            hour = hour % 24
            if hour == 0:
                return f"12:{minute:02d}", "AM"
            if hour == 12:
                return f"12:{minute:02d}", "PM"
            if hour < 12:
                return f"{hour}:{minute:02d}", "AM"
            return f"{hour - 12}:{minute:02d}", "PM"
        except (ValueError, IndexError):
            return "12:00", "PM"

    def select_trigger_type(self, option):
        """Handle trigger type selection (Time vs Interval)."""
        self.trigger_type_dropdown.dismiss()
        self.trigger_type_btn.text = option
        # Enable/disable inputs based on type
        if option == "Every X Minutes":
            self.time_input.disabled = True
            self.interval_input.disabled = False
        else:
            self.time_input.disabled = False
            self.interval_input.disabled = True
    
    def select_repeat(self, option):
        """Handle repeat selection."""
        self.repeat_dropdown.dismiss()
        self.repeat_btn.text = option

    def select_template(self, option):
        """Apply a preset reminder template."""
        self.template_dropdown.dismiss()
        self.template_btn.text = option
        preset = self.REMINDER_TEMPLATES.get(option)
        if not preset:
            return
        self.text_input.text = preset.get("text", "")
        self.description_input.text = preset.get("description", "")
        self.mood_btn.text = preset.get("mood", "happy")
        icon_path = preset.get("icon_path")
        if icon_path == "assets/icons/drink_water.png":
            self.icon_btn.text = "Drink Water"
            self.icon_path_input.text = icon_path
            self.icon_path_input.disabled = True
        elif icon_path == "assets/icons/stretch.png":
            self.icon_btn.text = "Stretch"
            self.icon_path_input.text = icon_path
            self.icon_path_input.disabled = True
        else:
            self.icon_btn.text = "None"
            self.icon_path_input.text = ""
            self.icon_path_input.disabled = True

    def select_accent(self, label, color):
        self.accent_dropdown.dismiss()
        self.accent_btn.text = label
        self.selected_accent = list(color)

    def _infer_action(self):
        preset = self.REMINDER_TEMPLATES.get(self.template_btn.text)
        if preset and preset.get("action") in ("drink", "stretch", "exercise"):
            return preset.get("action")
        text = (self.text_input.text or "").lower()
        if "drink" in text or "water" in text or "hydrat" in text:
            return "drink"
        if any(k in text for k in ("exercise", "workout", "cardio", "jog", "jumping", "active")):
            return "exercise"
        if "stretch" in text or "walk" in text or "move" in text:
            return "stretch"
        return None
    
    def _select_icon(self, icon_path, label):
        """Handle icon selection from dropdown."""
        self.icon_dropdown.dismiss()
        self.icon_btn.text = label
        if icon_path == "CUSTOM":
            # Enable custom path input
            self.icon_path_input.disabled = False
            self.icon_path_input.text = ""
        elif icon_path is None:
            # None selected
            self.icon_path_input.disabled = True
            self.icon_path_input.text = ""
        else:
            # Predefined icon selected - use relative path
            self.icon_path_input.disabled = True
            # icon_path is already relative from the dropdown options
            self.icon_path_input.text = icon_path
    
    def select_fe_eyes(self, option):
        """Handle face expression eyes selection."""
        self.fe_eyes_dropdown.dismiss()
        self.fe_eyes_btn.text = option
    
    def select_fe_mouth(self, option):
        """Handle face expression mouth selection."""
        self.fe_mouth_dropdown.dismiss()
        self.fe_mouth_btn.text = option
    
    def select_mood(self, option):
        """Handle mood selection."""
        self.mood_dropdown.dismiss()
        self.mood_btn.text = option
    
    def save(self, instance):
        """Save the reminder with validation."""
        trigger_type = self.trigger_type_btn.text
        
        # Validate based on trigger type
        if trigger_type == "Every X Minutes":
            # Validate interval
            try:
                interval_minutes = int(self.interval_input.text.strip())
                if interval_minutes < 1 or interval_minutes > 1440:  # Max 24 hours
                    raise ValueError
                trigger_time = None  # Not used for interval reminders
            except ValueError:
                self.error_label.text = "Invalid interval (1-1440 minutes)"
                return
        else:
            # Validate trigger time (12-hour + AM/PM) and convert to 24-hour for storage
            time_str = self.time_input.text.strip()
            am_pm = self.am_pm_btn.text  # "AM" or "PM"
            if not time_str:
                self.error_label.text = "Trigger time is required"
                return
            trigger_time = self._time_12h_to_24h(time_str, am_pm)
            if trigger_time is None:
                self.error_label.text = "Invalid time (use e.g. 2:30 with AM/PM)"
                return
            interval_minutes = None  # Not used for time-based reminders
        
        # Validate face expression constraint
        face_expression = None
        if self.use_face_expr.state == "down":
            fe_eyes = None if self.fe_eyes_btn.text == "None" else self.fe_eyes_btn.text
            fe_mouth = None if self.fe_mouth_btn.text == "None" else self.fe_mouth_btn.text
            
            # Constraint: face_expression requires eyes OR mouth
            if fe_eyes is None and fe_mouth is None:
                self.error_label.text = "Face expression requires eyes or mouth"
                return
            
            face_expression = {
                "eyes": fe_eyes,
                "mouth": fe_mouth,
                "mood": self.mood_btn.text
            }
        
        # Get or create stable reminder ID
        reminders = config_manager.get("reminders", [])
        reminder_id = None
        
        if self.reminder_index is not None and 0 <= self.reminder_index < len(reminders):
            # Editing existing reminder - preserve ID
            existing_reminder = reminders[self.reminder_index]
            reminder_id = existing_reminder.get("id")
            if not reminder_id:
                # Legacy reminder without ID - generate one
                reminder_id = str(uuid.uuid4())
        else:
            # Creating new reminder - generate new UUID
            reminder_id = str(uuid.uuid4())
        
        # Get icon_path from icon_path_input or from icon_btn selection (store as relative path)
        icon_path = None
        if self.icon_path_input.text.strip():
            path = self.icon_path_input.text.strip()
            # Convert absolute path to relative if it's in the project
            script_dir = os.path.dirname(os.path.abspath(__file__))
            if os.path.isabs(path) and path.startswith(script_dir):
                icon_path = os.path.relpath(path, script_dir)
            else:
                icon_path = path  # Already relative or custom absolute
        elif self.icon_btn.text not in ("None", "Custom Path"):
            # Predefined icon selected - use relative path
            if self.icon_btn.text == "Drink Water":
                icon_path = "assets/icons/drink_water.png"
            elif self.icon_btn.text == "Stretch":
                icon_path = "assets/icons/stretch.png"
        
        # Create reminder object with all fields
        reminder = {
            "id": reminder_id,  # Stable UUID
            "text": self.text_input.text.strip() or None,  # nullable
            "icon": self.icon_input.text.strip() or None,  # nullable (text icon for backward compatibility)
            "icon_path": icon_path,  # nullable (image file path)
            "action": self._infer_action(),
            "face_expression": face_expression,  # nullable (dict with eyes, mouth, mood)
            "trigger_type": trigger_type,  # "Specific Time" or "Every X Minutes"
            "trigger_time": trigger_time,  # Time string (HH:MM) or None for interval
            "interval_minutes": interval_minutes,  # Minutes interval or None for time-based
            "repeat_settings": self.repeat_btn.text,  # Required
            "is_active": self.is_active_toggle.state == "down",  # Required
            "accent": list(getattr(self, "selected_accent", config_manager.get("default_colors.primary", [0.10, 0.90, 1.00, 1.0]))),
            "mood": self.mood_btn.text,  # Default mood (used if no face_expression)
            "description": self.description_input.text.strip() or ""  # Separate description field
        }
        
        # Save to config
        if self.reminder_index is not None and 0 <= self.reminder_index < len(reminders):
            reminders[self.reminder_index] = reminder
        else:
            reminders.append(reminder)
        config_manager.set("reminders", reminders)
        
        # Clear error message
        self.error_label.text = ""
        
        # Return to reminders screen (will refresh automatically via on_pre_enter)
        self.manager.current = "reminders"
    
    def _build_reminder_dict_for_test(self):
        """Build a reminder dict from current form for 'Test in 10 sec' (no save)."""
        face_expression = None
        if self.use_face_expr.state == "down":
            fe_eyes = None if self.fe_eyes_btn.text == "None" else self.fe_eyes_btn.text
            fe_mouth = None if self.fe_mouth_btn.text == "None" else self.fe_mouth_btn.text
            if fe_eyes is not None or fe_mouth is not None:
                face_expression = {
                    "eyes": fe_eyes,
                    "mouth": fe_mouth,
                    "mood": self.mood_btn.text
                }
        trigger_type = self.trigger_type_btn.text
        trigger_time = None
        interval_minutes = None
        if trigger_type == "Every X Minutes":
            try:
                interval_minutes = int(self.interval_input.text.strip())
                interval_minutes = max(1, min(1440, interval_minutes))
            except ValueError:
                interval_minutes = 5
        else:
            time_str = self.time_input.text.strip()
            am_pm = self.am_pm_btn.text
            trigger_time = self._time_12h_to_24h(time_str, am_pm) if time_str else "12:00"
        accent = list(getattr(self, "selected_accent", config_manager.get("default_colors.primary", [0.10, 0.90, 1.00, 1.0])))
        # Get icon_path for test reminder (use relative paths)
        icon_path = None
        if hasattr(self, 'icon_path_input') and self.icon_path_input.text.strip():
            path = self.icon_path_input.text.strip()
            script_dir = os.path.dirname(os.path.abspath(__file__))
            if os.path.isabs(path) and path.startswith(script_dir):
                icon_path = os.path.relpath(path, script_dir)
            else:
                icon_path = path
        elif hasattr(self, 'icon_btn') and self.icon_btn.text not in ("None", "Custom Path"):
            if self.icon_btn.text == "Drink Water":
                icon_path = "assets/icons/drink_water.png"
            elif self.icon_btn.text == "Stretch":
                icon_path = "assets/icons/stretch.png"
        
        return {
            "id": str(uuid.uuid4()),
            "text": self.text_input.text.strip() or "Test reminder",
            "icon": self.icon_input.text.strip() if hasattr(self, 'icon_input') else None,
            "icon_path": icon_path,
            "action": self._infer_action(),
            "face_expression": face_expression,
            "trigger_type": trigger_type,
            "trigger_time": trigger_time,
            "interval_minutes": interval_minutes,
            "repeat_settings": self.repeat_btn.text,
            "is_active": True,
            "accent": accent,
            "mood": self.mood_btn.text,
            "description": self.description_input.text.strip() or ""
        }

    def test_in_10_seconds(self, instance):
        """Schedule this reminder to appear on the homescreen in 10 seconds (for testing)."""
        reminder = self._build_reminder_dict_for_test()
        from_screen = self.manager.current  # Return here after 1 minute
        self.error_label.text = "Switching to Home in 10 sec..."
        def _show_test_reminder(dt):
            self.error_label.text = ""
            homescreen = self.manager.get_screen("homescreen")
            homescreen._return_screen = from_screen
            # If a real reminder is set for current time, show that instead of the test reminder
            now = datetime.now()
            current_time = now.strftime("%H:%M")
            reminders = config_manager.get("reminders", [])
            real_reminder = None
            for r in reminders:
                if not r.get("is_active", True):
                    continue
                if r.get("trigger_type") != "Specific Time":
                    continue
                raw = r.get("trigger_time", "")
                normalized = homescreen._normalize_trigger_time(raw) if hasattr(homescreen, "_normalize_trigger_time") else raw
                if normalized == current_time:
                    real_reminder = r
                    break
            display_reminder = real_reminder if real_reminder else reminder
            self.manager.current = "homescreen"
            if hasattr(homescreen, "trigger_reminder"):
                homescreen.trigger_reminder(display_reminder, is_real_trigger=False)
        Clock.schedule_once(_show_test_reminder, 10.0)

    def cancel(self, instance):
        """Cancel editing and return to reminders screen."""
        self.manager.current = "reminders"


class ReminderQuickEditScreen(Screen):
    """
    Simplified reminder creation/edit screen:
    - Reminder type dropdown (no typing)
    - Color dropdown (palette)
    - Either every 15 minutes OR a specific time
    """

    REMINDER_TEMPLATES = ReminderEditScreen.REMINDER_TEMPLATES
    COLOR_PRESETS = [
        ("Pink", [1.00, 0.55, 0.80, 1.0]),
        ("Blue", [0.10, 0.90, 1.00, 1.0]),
        ("Red", [1.00, 0.25, 0.25, 1.0]),
        ("Yellow", [1.00, 0.93, 0.20, 1.0]),
        ("Green", [0.15, 1.00, 0.55, 1.0]),
        ("Orange", [1.00, 0.45, 0.10, 1.0]),
        ("Purple", [0.80, 0.35, 1.00, 1.0]),
    ]

    def __init__(self, reminder_index=None, **kwargs):
        super().__init__(**kwargs)
        self.reminder_index = reminder_index
        self._editing_is_active = True
        self.setup_ui()

    def setup_ui(self):
        main_layout = FloatLayout()
        with main_layout.canvas.before:
            Color(*UI["BG"])
            Rectangle(pos=main_layout.pos, size=Window.size)
            Color(*UI["PANEL"])
            RoundedRectangle(pos=(dp(18), dp(18)), size=(Window.width - dp(36), Window.height - dp(36)), radius=[dp(26)])

        self.title_label = Label(
            text="New Reminder",
            font_size="36sp",
            bold=True,
            color=(1, 1, 1, 1),
            halign="center",
            valign="top",
            size_hint=(1, 0.10),
            pos_hint={"x": 0, "y": 0.90},
        )
        main_layout.add_widget(self.title_label)

        self.scroll = ScrollView(
            size_hint=(1, 0.75),
            pos_hint={"x": 0, "y": 0.15},
            do_scroll_x=False,
            do_scroll_y=True,
        )

        form_layout = BoxLayout(
            orientation="vertical",
            spacing=dp(15),
            padding=dp(20),
            size_hint_y=None,
        )
        form_layout.bind(minimum_height=form_layout.setter("height"))

        # Reminder type dropdown
        type_container = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(50), spacing=dp(10))
        type_label = Label(
            text="Reminder Type:",
            font_size="20sp",
            color=UI["TEXT"],
            halign="left",
            size_hint_x=0.35,
            text_size=(None, None),
        )
        self.template_dropdown = DropDown()
        self.template_btn = Button(
            text="Drink Water",
            size_hint_x=0.55,
            font_size="16sp",
            background_color=UI["ACCENT_BLUE"],
            background_normal="",
            background_down="",
            color=(1, 1, 1, 1),
        )
        for option in [k for k in self.REMINDER_TEMPLATES.keys() if k != "Custom"]:
            btn = Button(text=option, size_hint_y=None, height=dp(45), font_size="16sp")
            btn.bind(on_release=lambda b, opt=option: self.select_template(opt))
            self.template_dropdown.add_widget(btn)
        self.template_btn.bind(on_release=self.template_dropdown.open)
        type_container.add_widget(type_label)
        type_container.add_widget(self.template_btn)
        type_container.add_widget(Widget())
        form_layout.add_widget(type_container)

        # Reminder color dropdown
        color_container = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(50), spacing=dp(10))
        color_label = Label(
            text="Reminder Color:",
            font_size="20sp",
            color=UI["TEXT"],
            halign="left",
            size_hint_x=0.35,
            text_size=(None, None),
        )
        self.accent_dropdown = DropDown()
        self.accent_btn = Button(
            text="Blue",
            size_hint_x=0.55,
            font_size="16sp",
            background_color=UI["ACCENT_BLUE"],
            background_normal="",
            background_down="",
            color=(1, 1, 1, 1),
        )
        for label, color in self.COLOR_PRESETS:
            btn = Button(text=label, size_hint_y=None, height=dp(45), font_size="16sp")
            btn.bind(on_release=lambda b, lbl=label, c=color: self.select_accent(lbl, c))
            self.accent_dropdown.add_widget(btn)
        self.accent_btn.bind(on_release=self.accent_dropdown.open)
        color_container.add_widget(color_label)
        color_container.add_widget(self.accent_btn)
        color_container.add_widget(Widget())
        form_layout.add_widget(color_container)

        # Trigger dropdown (every 15 minutes OR specific time)
        trigger_container = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(50), spacing=dp(10))
        trigger_label = Label(
            text="Trigger:",
            font_size="20sp",
            color=UI["TEXT"],
            halign="left",
            size_hint_x=0.20,
            text_size=(None, None),
        )
        self.trigger_type_dropdown = DropDown()
        self.trigger_type_btn = Button(
            text="Every 15 Minutes",
            size_hint_x=0.55,
            font_size="16sp",
            background_color=UI["ACCENT_BLUE"],
            background_normal="",
            background_down="",
            color=(1, 1, 1, 1),
        )
        for option in ["Every 15 Minutes", "Specific Time"]:
            btn = Button(text=option, size_hint_y=None, height=dp(45), font_size="16sp")
            btn.bind(on_release=lambda b, opt=option: self.select_trigger_type(opt))
            self.trigger_type_dropdown.add_widget(btn)
        self.trigger_type_btn.bind(on_release=self.trigger_type_dropdown.open)
        trigger_container.add_widget(trigger_label)
        trigger_container.add_widget(self.trigger_type_btn)
        trigger_container.add_widget(Widget())
        form_layout.add_widget(trigger_container)

        # Time input section (only visible for "Specific Time")
        self.time_container = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(50), spacing=dp(10))
        time_label = Label(
            text="Time (e.g. 2:30):",
            font_size="20sp",
            color=UI["TEXT"],
            halign="left",
            size_hint_x=0.30,
            text_size=(None, None),
        )
        self.time_input = TextInput(
            text="12:00",
            multiline=False,
            size_hint_x=0.20,
            font_size="18sp",
            background_color=(0.12, 0.12, 0.18, 1.0),
            foreground_color=(1, 1, 1, 1),
            padding=dp(10),
        )
        self.am_pm_dropdown = DropDown()
        self.am_pm_btn = Button(
            text="PM",
            size_hint_x=0.15,
            font_size="18sp",
            background_color=UI["ACCENT_BLUE"],
            background_normal="",
            background_down="",
            color=(1, 1, 1, 1),
        )
        for option in ["AM", "PM"]:
            btn = Button(text=option, size_hint_y=None, height=dp(45), font_size="16sp")
            btn.bind(on_release=lambda b, opt=option: self._select_am_pm(opt))
            self.am_pm_dropdown.add_widget(btn)
        self.am_pm_btn.bind(on_release=self.am_pm_dropdown.open)
        self.time_container.add_widget(time_label)
        self.time_container.add_widget(self.time_input)
        self.time_container.add_widget(self.am_pm_btn)
        self.time_container.add_widget(Widget())  # Spacer
        form_layout.add_widget(self.time_container)

        # Error message
        self.error_label = Label(
            text="",
            font_size="16sp",
            color=(1, 0.3, 0.3, 1),
            halign="center",
            size_hint_y=None,
            height=dp(30),
            text_size=(None, None),
        )
        form_layout.add_widget(self.error_label)

        self.scroll.add_widget(form_layout)
        main_layout.add_widget(self.scroll)

        # Fixed bottom buttons
        button_container = BoxLayout(
            orientation="horizontal",
            spacing=dp(15),
            padding=dp(15),
            size_hint=(1, 0.12),
            pos_hint={"x": 0, "y": 0},
        )

        cancel_btn = Button(
            text="Cancel",
            size_hint_x=0.28,
            font_size="18sp",
            bold=True,
            background_color=UI["NEUTRAL"],
            background_normal="",
            background_down="",
            color=(1, 1, 1, 1),
        )
        cancel_btn.bind(on_release=self.cancel)
        button_container.add_widget(cancel_btn)

        save_btn = Button(
            text="Save",
            size_hint_x=0.28,
            font_size="18sp",
            bold=True,
            background_color=UI["ACCENT_GREEN"],
            background_normal="",
            background_down="",
            color=(1, 1, 1, 1),
        )
        save_btn.bind(on_release=self.save)
        button_container.add_widget(save_btn)

        main_layout.add_widget(button_container)
        self.add_widget(main_layout)

    def setup_for_new(self):
        self.title_label.text = "New Reminder"
        self.reminder_index = None
        self._editing_is_active = True
        self.template_btn.text = "Drink Water" if "Drink Water" in self.REMINDER_TEMPLATES else next(
            (k for k in self.REMINDER_TEMPLATES.keys() if k != "Custom"), "Drink Water"
        )
        self.selected_accent = list(config_manager.get("default_colors.primary", [0.10, 0.90, 1.00, 1.0]))
        self.accent_btn.text = self._label_for_accent(self.selected_accent) or "Custom"
        self.trigger_type_btn.text = "Every 15 Minutes"
        self.time_input.text = "12:00"
        self.am_pm_btn.text = "PM"
        self.error_label.text = ""
        self._apply_time_visibility()

    def setup_for_edit(self, index):
        self.title_label.text = "Edit Reminder"
        self.reminder_index = index
        reminders = config_manager.get("reminders", [])
        if not (0 <= index < len(reminders)):
            self.setup_for_new()
            return

        reminder = reminders[index]
        self._editing_is_active = reminder.get("is_active", True)

        # Infer template selection from stored text/action
        stored_text = (reminder.get("text") or "").strip().lower()
        inferred_template = None
        for key, preset in self.REMINDER_TEMPLATES.items():
            if key == "Custom" or not preset:
                continue
            if (preset.get("text") or "").strip().lower() == stored_text and stored_text:
                inferred_template = key
                break
        if not inferred_template:
            inferred_action = reminder.get("action")
            if inferred_action:
                for key, preset in self.REMINDER_TEMPLATES.items():
                    if key == "Custom" or not preset:
                        continue
                    if preset.get("action") == inferred_action:
                        inferred_template = key
                        break
        if not inferred_template:
            inferred_template = "Drink Water"
        self.template_btn.text = inferred_template

        # Accent
        stored_accent = reminder.get("accent", config_manager.get("default_colors.primary", [0.10, 0.90, 1.00, 1.0]))
        self.selected_accent = list(stored_accent) if isinstance(stored_accent, (list, tuple)) else list(config_manager.get("default_colors.primary", [0.10, 0.90, 1.00, 1.0]))
        self.accent_btn.text = self._label_for_accent(self.selected_accent) or "Custom"

        # Trigger
        if reminder.get("trigger_type") == "Every X Minutes":
            self.trigger_type_btn.text = "Every 15 Minutes"
        else:
            self.trigger_type_btn.text = "Specific Time"
            stored_time = reminder.get("trigger_time", "12:00") or "12:00"
            display_12h, display_am_pm = self._time_24h_to_12h_display(stored_time)
            self.time_input.text = display_12h
            self.am_pm_btn.text = display_am_pm

        self.error_label.text = ""
        self._apply_time_visibility()

    def _apply_time_visibility(self):
        # Only show time widgets for "Specific Time"
        enabled = self.trigger_type_btn.text == "Specific Time"
        self.time_container.height = dp(50) if enabled else 0
        self.time_container.opacity = 1 if enabled else 0
        self.time_input.disabled = not enabled
        self.am_pm_btn.disabled = not enabled

    def _label_for_accent(self, accent_rgba):
        if not accent_rgba:
            return None
        for label, color in self.COLOR_PRESETS:
            if list(color) == list(accent_rgba):
                return label
        return None

    def _select_am_pm(self, option):
        self.am_pm_dropdown.dismiss()
        self.am_pm_btn.text = option

    def select_template(self, option):
        self.template_dropdown.dismiss()
        self.template_btn.text = option

    def select_accent(self, label, color):
        self.accent_dropdown.dismiss()
        self.accent_btn.text = label
        self.selected_accent = list(color)

    def select_trigger_type(self, option):
        self.trigger_type_dropdown.dismiss()
        self.trigger_type_btn.text = option
        self._apply_time_visibility()

    def _time_12h_to_24h(self, time_str_12h, am_pm):
        try:
            parts = time_str_12h.strip().split(":")
            if len(parts) != 2:
                return None
            hour, minute = int(parts[0]), int(parts[1])
            if not (1 <= hour <= 12 and 0 <= minute < 60):
                return None
            if am_pm == "PM":
                hour = 12 if hour == 12 else hour + 12
            else:
                hour = 0 if hour == 12 else hour
            return f"{hour:02d}:{minute:02d}"
        except (ValueError, IndexError):
            return None

    def _time_24h_to_12h_display(self, time_str_24h):
        try:
            parts = time_str_24h.strip().split(":")
            if len(parts) != 2:
                return "12:00", "PM"
            hour, minute = int(parts[0]), int(parts[1])
            hour = hour % 24
            if hour == 0:
                return f"12:{minute:02d}", "AM"
            if hour == 12:
                return f"12:{minute:02d}", "PM"
            if hour < 12:
                return f"{hour}:{minute:02d}", "AM"
            return f"{hour - 12}:{minute:02d}", "PM"
        except (ValueError, IndexError):
            return "12:00", "PM"

    def save(self, instance):
        self.error_label.text = ""
        preset = self.REMINDER_TEMPLATES.get(self.template_btn.text)
        if not preset:
            self.error_label.text = "Pick a reminder type."
            return

        # Trigger handling
        if self.trigger_type_btn.text == "Every 15 Minutes":
            trigger_type = "Every X Minutes"
            interval_minutes = 15
            trigger_time = None
        else:
            trigger_type = "Specific Time"
            interval_minutes = None
            time_str = (self.time_input.text or "").strip()
            am_pm = self.am_pm_btn.text  # "AM" or "PM"
            if not time_str:
                self.error_label.text = "Time is required."
                return
            trigger_time = self._time_12h_to_24h(time_str, am_pm)
            if trigger_time is None:
                self.error_label.text = "Invalid time. Use HH:MM (e.g. 2:30)."
                return

        reminders = config_manager.get("reminders", [])
        editing = self.reminder_index is not None and 0 <= self.reminder_index < len(reminders)
        # Stable reminder ID
        if editing:
            reminder_id = reminders[self.reminder_index].get("id") or str(uuid.uuid4())
        else:
            reminder_id = str(uuid.uuid4())

        # Build reminder object (no free-form typing)
        reminder_obj = {
            "id": reminder_id,
            "text": preset.get("text", "Reminder"),
            "icon": None,
            "icon_path": preset.get("icon_path"),
            "action": preset.get("action"),
            "face_expression": None,
            "trigger_type": trigger_type,
            "trigger_time": trigger_time,
            "interval_minutes": interval_minutes,
            "repeat_settings": "daily",
            "is_active": bool(self._editing_is_active),
            "accent": list(getattr(self, "selected_accent", config_manager.get("default_colors.primary", [0.10, 0.90, 1.00, 1.0]))),
            "mood": preset.get("mood", "happy"),
            "description": preset.get("description", ""),
        }

        if editing:
            reminders[self.reminder_index] = reminder_obj
        else:
            reminders.append(reminder_obj)

        config_manager.set("reminders", reminders)
        self.manager.current = "reminders"

    def cancel(self, instance):
        self.manager.current = "reminders"


class RemindersScreen(Screen):
    """
    Reminders tool screen.
    Allows users to create and manage reminders with:
    - Text (nullable)
    - Icon (nullable)
    - Face expression (nullable, but requires eyes/mouth to be defined)
    - Trigger Time
    - Repeat Settings
    - is_active flag
    """
    
    def __init__(self, **kwargs):
        """Initialize the reminders screen."""
        super().__init__(**kwargs)
        self.setup_ui()
        self.load_reminders()
    
    def on_pre_enter(self, *args):
        """Refresh reminders when screen becomes visible."""
        self.load_reminders()
    
    def setup_ui(self):
        """Build the reminders management UI."""
        layout = FloatLayout()
        
        # Background
        with layout.canvas.before:
            Color(0.05, 0.05, 0.10, 1.0)
            Rectangle(pos=layout.pos, size=Window.size)
        
        # Title
        title = Label(
            text="Reminders",
            font_size="32sp",
            bold=True,
            color=(1, 1, 1, 1),
            halign="center",
            valign="top",
            size_hint=(1, 0.10),
            pos_hint={"x": 0, "y": 0.90}
        )
        layout.add_widget(title)
        
        # ScrollView wrapping the reminder list (fits 800x480; scroll when many reminders)
        scroll = ScrollView(
            size_hint=(1, 0.58),
            pos_hint={"x": 0, "y": 0.32},
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=dp(8),
            scroll_type=["bars", "content"]
        )
        self.reminder_list = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=dp(12),
            size_hint_y=None,
            size_hint_x=1
        )
        self.reminder_list.bind(minimum_height=self.reminder_list.setter("height"))
        scroll.add_widget(self.reminder_list)
        layout.add_widget(scroll)
        
        # Bottom bar: Add + Home
        bottom = BoxLayout(
            orientation="horizontal",
            size_hint=(1, 0.14),
            pos_hint={"x": 0, "y": 0.06},
            padding=dp(20),
            spacing=dp(20)
        )
        add_btn = Button(
            text="+ Add New Reminder",
            size_hint_x=0.45,
            font_size="20sp",
            bold=True,
            background_color=UI["ACCENT_GREEN"],
            background_normal='',
            background_down='',
            color=(1, 1, 1, 1)
        )
        add_btn.bind(on_release=self.show_add_dialog)
        bottom.add_widget(add_btn)
        home_btn = Button(
            text="Return Home",
            size_hint_x=0.45,
            font_size="20sp",
            bold=True,
            background_color=UI["ACCENT_BLUE"],
            background_normal='',
            background_down='',
            color=(1, 1, 1, 1)
        )
        home_btn.bind(on_release=self.return_home)
        bottom.add_widget(home_btn)
        layout.add_widget(bottom)
        
        self.add_widget(layout)
    
    def load_reminders(self):
        """Load and display all reminders."""
        self.reminder_list.clear_widgets()
        reminders = config_manager.get("reminders", [])
        
        if not reminders:
            empty = Label(
                text="No reminders yet.\nTap '+ Add New Reminder' to create one.",
                font_size="20sp",
                color=UI["TEXT_DIM"],
                halign="center",
                size_hint_y=None,
                height=dp(80),
                text_size=(None, None)
            )
            self.reminder_list.add_widget(empty)
            return
        for i, reminder in enumerate(reminders):
            reminder_widget = self.create_reminder_widget(reminder, i)
            self.reminder_list.add_widget(reminder_widget)
    
    def create_reminder_widget(self, reminder, index):
        """Create a card-style widget for displaying a reminder."""
        is_active = reminder.get("is_active", True)
        text = reminder.get("text", "Untitled") or "Untitled"
        icon = reminder.get("icon", "") or ""
        trigger_type = reminder.get("trigger_type", "Specific Time")
        trigger_time = reminder.get("trigger_time", "")
        interval_min = reminder.get("interval_minutes")
        repeat = reminder.get("repeat_settings", "daily")
        accent = reminder.get("accent", [0.10, 0.90, 1.00, 1.0])
        if not isinstance(accent, (list, tuple)) or len(accent) < 3:
            accent = [0.10, 0.90, 1.00, 1.0]
        
        # Time/subtitle line
        if trigger_type == "Every X Minutes" and interval_min:
            time_str = f"Every {interval_min} min · {repeat}"
        else:
            time_str = f"{trigger_time} · {repeat}" if trigger_time else repeat
        status = "ON" if is_active else "OFF"
        status_color = (0.2, 0.8, 0.3, 1) if is_active else (0.5, 0.5, 0.5, 1)
        
        card = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            size_hint_x=1,
            height=dp(108),
            spacing=dp(4),
            padding=dp(10)
        )
        with card.canvas.before:
            Color(accent[0], accent[1], accent[2], 0.35)
            outer = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(10)])
            Color(0.12, 0.12, 0.18, 0.96)
            rect = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(10)])
        def _update_card_rect(w, *args):
            outer.pos = w.pos
            outer.size = w.size
            rect.pos = w.pos
            rect.size = w.size
        card.bind(pos=_update_card_rect, size=_update_card_rect)
        
        # Top row: title (wraps) + status
        row1 = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(40), spacing=dp(8))
        title_label = Label(
            text=(f"{icon} {text}".strip() or "Untitled")[:60],
            font_size="18sp",
            bold=True,
            color=(1, 1, 1, 1),
            halign="left",
            valign="middle",
            size_hint_x=0.68,
            text_size=(None, None)
        )
        def _set_title_text_size(lbl, size):
            if size[0] > 1 and size[1] > 1:
                lbl.text_size = (size[0] - dp(4), None)
        title_label.bind(size=_set_title_text_size)
        status_label = Label(
            text=status,
            font_size="14sp",
            bold=True,
            color=status_color,
            halign="right",
            size_hint_x=0.22,
            text_size=(None, None)
        )
        row1.add_widget(title_label)
        row1.add_widget(status_label)
        card.add_widget(row1)
        
        # Second row: time + repeat (single line, truncate if needed)
        row2 = Label(
            text=time_str[:45] + ("…" if len(time_str) > 45 else ""),
            font_size="13sp",
            color=(0.75, 0.78, 0.9, 1),
            halign="left",
            size_hint_y=None,
            height=dp(20),
            text_size=(None, None)
        )
        card.add_widget(row2)
        
        # Button row
        btn_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(38), spacing=dp(6))
        edit_btn = Button(
            text="Edit",
            size_hint_x=0.28,
            font_size="14sp",
            background_color=(0.3, 0.5, 0.85, 1.0),
            background_normal='',
            background_down='',
            color=(1, 1, 1, 1)
        )
        edit_btn.bind(on_release=lambda b, idx=index: self.edit_reminder(idx))
        toggle_btn = Button(
            text="Toggle",
            size_hint_x=0.28,
            font_size="14sp",
            background_color=(0.4, 0.45, 0.55, 1.0),
            background_normal='',
            background_down='',
            color=(1, 1, 1, 1)
        )
        toggle_btn.bind(on_release=lambda b, idx=index: self.toggle_reminder(idx))
        delete_btn = Button(
            text="Delete",
            size_hint_x=0.28,
            font_size="14sp",
            background_color=(0.75, 0.25, 0.25, 1.0),
            background_normal='',
            background_down='',
            color=(1, 1, 1, 1)
        )
        delete_btn.bind(on_release=lambda b, idx=index: self.delete_reminder(idx))
        btn_row.add_widget(edit_btn)
        btn_row.add_widget(toggle_btn)
        btn_row.add_widget(delete_btn)
        card.add_widget(btn_row)
        
        return card
    
    def show_add_dialog(self, instance):
        """Navigate to edit screen to add a new reminder."""
        # Create a new reminder screen
        screen_name = "reminder_quick_edit"
        if screen_name not in [s.name for s in self.manager.screens]:
            self.manager.add_widget(ReminderQuickEditScreen(name=screen_name, reminder_index=None))
        edit_screen = self.manager.get_screen(screen_name)
        edit_screen.setup_for_new()
        self.manager.current = screen_name
    
    def edit_reminder(self, index):
        """Navigate to edit screen to edit an existing reminder."""
        screen_name = "reminder_quick_edit"
        if screen_name not in [s.name for s in self.manager.screens]:
            self.manager.add_widget(ReminderQuickEditScreen(name=screen_name, reminder_index=index))
        edit_screen = self.manager.get_screen(screen_name)
        edit_screen.setup_for_edit(index)
        self.manager.current = screen_name
    
    def toggle_reminder(self, index):
        """Toggle the active state of a reminder."""
        reminders = config_manager.get("reminders", [])
        if 0 <= index < len(reminders):
            reminders[index]["is_active"] = not reminders[index].get("is_active", True)
            config_manager.set("reminders", reminders)
            self.load_reminders()
    
    def delete_reminder(self, index):
        """Delete a reminder."""
        reminders = config_manager.get("reminders", [])
        if 0 <= index < len(reminders):
            reminders.pop(index)
            config_manager.set("reminders", reminders)
            self.load_reminders()
    
    def return_home(self, instance):
        """Navigate back to homescreen."""
        self.manager.current = "homescreen"

# ============================================================================
# MAIN APPLICATION
# ============================================================================

