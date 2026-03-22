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
from kivy.uix.spinner import Spinner
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.metrics import dp
import os

from config import (
    config_manager,
    REMINDER_PRESETS,
    REMINDER_PRESET_ORDER,
    create_preset_reminder,
)
from widgets import Face, StickFigureIcon

# Bright panel colours for reminder setup (label → RGBA)
REMINDER_COLOR_SWATCHES = (
    ("Cyan", [0.20, 0.78, 1.00, 1.0]),
    ("Pink", [1.00, 0.35, 0.72, 1.0]),
    ("Yellow", [1.00, 0.72, 0.12, 1.0]),
    ("Purple", [0.62, 0.38, 0.98, 1.0]),
    ("Orange", [1.00, 0.55, 0.30, 1.0]),
    ("Green", [0.20, 0.95, 0.45, 1.0]),
    ("Red", [0.95, 0.22, 0.28, 1.0]),
    ("Lime", [0.55, 1.00, 0.35, 1.0]),
)


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
            Color(0.05, 0.05, 0.10, 1.0)
            Rectangle(pos=main_layout.pos, size=Window.size)
            Color(0.10, 0.15, 0.25, 0.3)
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
            color=(0.8, 0.8, 1, 1),
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
            background_color=(0.2, 0.7, 0.4, 1.0),
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
            background_color=(0.3, 0.5, 0.9, 1.0),
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
            background_color=(0.7, 0.4, 0.2, 1.0),
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
            background_color=(0.8, 0.3, 0.6, 1.0),
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
        config_manager.set("face_customization.selected_mouth", "Curved")
        config_manager.set("default_colors.primary", [0.10, 0.90, 1.00, 1.0])
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
        self.selected_eyes = None
        self.selected_mouth = None
        self.setup_ui()
    
    def setup_ui(self):
        """Build the UI for face customization."""
        layout = FloatLayout()
        
        # Background
        with layout.canvas.before:
            Color(0.05, 0.05, 0.10, 1.0)
            Rectangle(pos=layout.pos, size=Window.size)
        
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
            text="Customize your robot's face (optional)",
            font_size="22sp",
            color=(0.8, 0.8, 1, 1),
            halign="center",
            size_hint=(1, 0.08),
            pos_hint={"x": 0, "y": 0.75}
        )
        layout.add_widget(instructions)
        
        # Eyes selection with better spacing
        eyes_label = Label(
            text="Eyes (optional):",
            font_size="24sp",
            color=(0.9, 0.9, 1, 1),
            halign="left",
            size_hint=(0.4, 0.08),
            pos_hint={"x": 0.1, "y": 0.62}
        )
        layout.add_widget(eyes_label)
        
        self.eyes_dropdown = DropDown()
        eyes_btn = Button(
            text="Select Eyes",
            size_hint=(0.35, 0.08),
            pos_hint={"x": 0.5, "y": 0.62},
            background_color=(0.3, 0.5, 0.8, 1.0),
            background_normal='',
            background_down=''
        )
        # At least 3 options for eyes (including None)
        for option in ["None", "Round", "Oval", "Narrow", "Wide", "Small"]:
            btn = Button(text=option, size_hint_y=None, height=dp(50))
            btn.bind(on_release=lambda b, opt=option: self.select_eyes(opt, eyes_btn))
            self.eyes_dropdown.add_widget(btn)
        eyes_btn.bind(on_release=self.eyes_dropdown.open)
        layout.add_widget(eyes_btn)
        
        # Mouth selection with better spacing
        mouth_label = Label(
            text="Mouth (optional):",
            font_size="24sp",
            color=(0.9, 0.9, 1, 1),
            halign="left",
            size_hint=(0.4, 0.08),
            pos_hint={"x": 0.1, "y": 0.50}
        )
        layout.add_widget(mouth_label)
        
        self.mouth_dropdown = DropDown()
        mouth_btn = Button(
            text="Select Mouth",
            size_hint=(0.35, 0.08),
            pos_hint={"x": 0.5, "y": 0.50},
            background_color=(0.3, 0.5, 0.8, 1.0),
            background_normal='',
            background_down=''
        )
        # At least 3 options for mouth (including None)
        for option in ["None", "Wide", "Small", "Expressive", "Neutral", "Curved", "Smile"]:
            btn = Button(text=option, size_hint_y=None, height=dp(50))
            btn.bind(on_release=lambda b, opt=option: self.select_mouth(opt, mouth_btn))
            self.mouth_dropdown.add_widget(btn)
        mouth_btn.bind(on_release=self.mouth_dropdown.open)
        layout.add_widget(mouth_btn)
        
        # Navigation buttons with better styling
        back_btn = Button(
            text="← Back",
            size_hint=(0.2, 0.10),
            pos_hint={"x": 0.1, "y": 0.15},
            background_color=(0.4, 0.4, 0.4, 1.0),
            background_normal='',
            background_down=''
        )
        back_btn.bind(on_release=lambda *_: setattr(self.manager, "current", "welcome"))
        layout.add_widget(back_btn)
        
        next_btn = Button(
            text="Next →",
            size_hint=(0.25, 0.10),
            pos_hint={"x": 0.65, "y": 0.15},
            background_color=(0.2, 0.7, 0.4, 1.0),
            background_normal='',
            background_down=''
        )
        next_btn.bind(on_release=self.next_page)
        layout.add_widget(next_btn)
        
        self.add_widget(layout)
    
    def select_eyes(self, option, btn):
        """Handle eyes selection (nullable - can be None)."""
        self.eyes_dropdown.dismiss()
        if option == "None":
            self.selected_eyes = None
            btn.text = "Eyes: None"
        else:
            self.selected_eyes = option
            btn.text = f"Eyes: {option}"
        # Save immediately when selected
        config_manager.set("face_customization.selected_eyes", self.selected_eyes)
    
    def select_mouth(self, option, btn):
        """Handle mouth selection (nullable - can be None)."""
        self.mouth_dropdown.dismiss()
        if option == "None":
            self.selected_mouth = None
            btn.text = "Mouth: None"
        else:
            self.selected_mouth = option
            btn.text = f"Mouth: {option}"
        # Save immediately when selected
        config_manager.set("face_customization.selected_mouth", self.selected_mouth)
    
    def next_page(self, instance):
        """Save face customization and navigate to color selection."""
        # Ensure values are saved (they're already saved on selection, but double-check)
        config_manager.set("face_customization.selected_eyes", self.selected_eyes)
        config_manager.set("face_customization.selected_mouth", self.selected_mouth)
        self.manager.current = "setup_colors"


class SetupColorsScreen(Screen):
    """
    First-time setup - Page 2: Default Colors Selection
    Allows user to choose default accent color.
    """
    
    def __init__(self, **kwargs):
        """Initialize the color selection setup screen."""
        super().__init__(**kwargs)
        color_presets = [
            ("Blue", (0.10, 0.90, 1.00, 1.0)),
            ("Purple", (0.80, 0.35, 1.00, 1.0)),
            ("Pink", (1.00, 0.41, 0.71, 1.0)),
            ("Orange", (1.00, 0.45, 0.10, 1.0)),
            ("Green", (0.15, 1.00, 0.55, 1.0)),
        ]
        self.selected_color = color_presets[0][1]
        self.setup_ui()
    
    def setup_ui(self):
        """Build the UI for color selection."""
        layout = FloatLayout()
        
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
            color=(0.8, 0.8, 1, 1),
            halign="center",
            size_hint=(1, 0.08),
            pos_hint={"x": 0, "y": 0.75}
        )
        layout.add_widget(instructions)
        
        # Color presets (5: Blue, Purple, Pink, Orange, Green) - two rows to fit 800px
        color_presets = [
            ("Blue", (0.10, 0.90, 1.00, 1.0)),
            ("Purple", (0.80, 0.35, 1.00, 1.0)),
            ("Pink", (1.00, 0.41, 0.71, 1.0)),
            ("Orange", (1.00, 0.45, 0.10, 1.0)),
            ("Green", (0.15, 1.00, 0.55, 1.0)),
        ]
        for i, (name, color) in enumerate(color_presets):
            row, col = i // 3, i % 3
            btn = Button(
                text=name,
                size_hint=(0.28, 0.12),
                pos_hint={"x": 0.08 + col * 0.32, "y": 0.58 - row * 0.14},
                background_color=(*color[:3], 0.8),
                font_size="18sp"
            )
            btn.bind(on_release=lambda b, c=color: self.select_color(c))
            layout.add_widget(btn)
        
        # Navigation buttons
        back_btn = Button(
            text="← Back",
            size_hint=(0.2, 0.10),
            pos_hint={"x": 0.1, "y": 0.15},
            background_color=(0.5, 0.5, 0.5, 1.0)
        )
        back_btn.bind(on_release=lambda *_: setattr(self.manager, "current", "setup_face"))
        layout.add_widget(back_btn)
        
        # Complete Setup Button
        complete_btn = Button(
            text="Complete Setup",
            size_hint=(0.35, 0.10),
            pos_hint={"x": 0.55, "y": 0.15},
            background_color=(0.2, 0.8, 0.4, 1.0)
        )
        complete_btn.bind(on_release=self.complete_setup)
        layout.add_widget(complete_btn)
        
        self.add_widget(layout)
    
    def select_color(self, color):
        """Handle default color selection."""
        self.selected_color = color
        # Save immediately when selected
        config_manager.set("default_colors.primary", list(self.selected_color))
    
    def complete_setup(self, instance):
        """Save color settings, mark setup complete, and navigate to homescreen."""
        # Ensure color is saved (already saved on selection, but double-check)
        config_manager.set("default_colors.primary", list(self.selected_color))
        config_manager.set("first_time_setup_complete", True)
        self.manager.current = "homescreen"


class Homescreen(Screen):
    """
    Main homescreen displayed after first-time setup.
    Shows active reminders and provides navigation to settings.
    """
    _HOME_FONT = "Roboto"
    _HOME_TITLE_SP = 32
    _HOME_LINE_SP = 24

    def __init__(self, **kwargs):
        """Initialize the homescreen."""
        super().__init__(**kwargs)
        self.idx = 0  # Current reminder index
        # Ensure default reminders are added if needed
        config_manager.ensure_default_reminders()
        self.setup_ui()
        self.load_reminders()
    
    def setup_ui(self):
        """Build the homescreen UI."""
        layout = FloatLayout()
        
        # Face area (top 72%) - shown by default
        self.face = Face(size_hint=(1, 0.72), pos_hint={"x": 0, "y": 0.28})
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
        self.face.set_cute_default(True)
        layout.add_widget(self.face)
        
        # Icon image widget (stick figure from file) - replaces face when reminder has icon_path
        self.icon_image = Image(
            source="",
            size_hint=(1, 0.72),  # Same size as face area
            pos_hint={"x": 0, "y": 0.28},  # Same position as face
            allow_stretch=True,
            keep_ratio=True
        )
        self.icon_image.opacity = 0  # Hidden by default (face shows instead)
        layout.add_widget(self.icon_image)
        # Kivy-drawn stick figure icon (when reminder has action: drink / stretch)
        self.stick_figure_icon = StickFigureIcon(
            action="stretch",
            size_hint=(1, 0.72),
            pos_hint={"x": 0, "y": 0.28}
        )
        self.stick_figure_icon.opacity = 0  # Hidden by default
        layout.add_widget(self.stick_figure_icon)
        
        # Bottom bar
        self.bar = Widget(size_hint=(1, 0.28), pos_hint={"x": 0, "y": 0})
        layout.add_widget(self.bar)
        
        # Title label (fixed typography — font customization removed)
        self.title = Label(
            text="",
            markup=True,
            font_size=f"{self._HOME_TITLE_SP}sp",
            font_name=self._HOME_FONT,
            bold=True,
            halign="left",
            valign="top",
            color=(0.98, 0.99, 1, 1),
            size_hint=(1, 0.28),
            pos_hint={"x": 0, "y": 0},
            padding=(dp(26), dp(20))
        )
        self.title.bind(size=lambda lbl, *_: setattr(lbl, "text_size", (lbl.width-40, lbl.height)))
        layout.add_widget(self.title)
        
        # Line label (reminder text)
        self.line = Label(
            text="",
            font_size=f"{self._HOME_LINE_SP}sp",
            font_name=self._HOME_FONT,
            halign="left",
            valign="middle",
            color=(0.82, 0.88, 0.98, 1),
            size_hint=(1, 0.28),
            pos_hint={"x": 0, "y": -0.02},
            padding=(dp(26), dp(18))
        )
        self.line.bind(size=lambda lbl, *_: setattr(lbl, "text_size", (lbl.width-40, lbl.height)))
        layout.add_widget(self.line)
        
        home_btn = Button(
            text="Home",
            font_name=self._HOME_FONT,
            font_size="16sp",
            bold=True,
            size_hint=(0.16, 0.085),
            pos_hint={"x": 0.805, "y": 0.175},
            background_color=(0.38, 0.48, 0.72, 0.95),
            background_normal='',
            background_down='',
            color=(1, 1, 1, 1)
        )
        home_btn.bind(on_release=lambda *_: setattr(self.manager, "current", "welcome"))
        layout.add_widget(home_btn)

        rem_btn = Button(
            text="Reminders",
            font_name=self._HOME_FONT,
            font_size="16sp",
            bold=True,
            size_hint=(0.18, 0.085),
            pos_hint={"x": 0.62, "y": 0.175},
            background_color=(0.32, 0.55, 0.42, 0.95),
            background_normal='',
            background_down='',
            color=(1, 1, 1, 1)
        )
        rem_btn.bind(on_release=lambda *_: setattr(self.manager, "current", "reminders"))
        layout.add_widget(rem_btn)
        
        self.add_widget(layout)
        
        # Time in a separate overlay so it is always above face/bar/colour (drawn on top of everything)
        time_overlay = FloatLayout(size_hint=(1, 1))
        self.time_label = Label(
            text="",
            font_size="19sp",
            font_name=self._HOME_FONT,
            color=(0.88, 0.92, 1, 1),
            halign="right",
            valign="top",
            size_hint=(0.32, 0.08),
            pos_hint={"right": 1, "top": 1},
            padding=(dp(16), dp(8))
        )
        self.time_label.bind(size=lambda lbl, size: setattr(lbl, "text_size", (max(1, size[0] - dp(24)), max(1, size[1] - dp(16)))))
        time_overlay.add_widget(self.time_label)

        # Dismiss: bottom bar strip, left side — avoids face/stick area (y >= 0.28) and right nav cluster
        self.dismiss_btn = Button(
            text="Dismiss",
            font_name=self._HOME_FONT,
            font_size="15sp",
            bold=True,
            size_hint=(0.2, 0.055),
            pos_hint={"x": 0.02, "y": 0.025},
            background_color=(0.85, 0.35, 0.38, 0.95),
            background_normal='',
            background_down='',
            color=(1, 1, 1, 1),
            opacity=0,
            disabled=True,
        )
        self.dismiss_btn.bind(on_release=self.dismiss)
        time_overlay.add_widget(self.dismiss_btn)

        self._reminder_timer_cb = None
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
    
    def on_pre_enter(self, *args):
        """Refresh reminders and ALL customizations when screen becomes visible."""
        # Update face customization from config (reload to ensure latest values)
        eyes = config_manager.get("face_customization.selected_eyes")
        mouth = config_manager.get("face_customization.selected_mouth")
        # Convert string "None" to actual None, ensure proper None handling
        eyes = None if eyes == "None" or eyes is None else eyes
        mouth = None if mouth == "None" or mouth is None else mouth
        self.face.set_customization(eyes, mouth)
        
        # Update default color (apply to face if no reminder showing)
        default_color = config_manager.get("default_colors.primary", [0.10, 0.90, 1.00, 1.0])
        if isinstance(default_color, list):
            default_color = tuple(default_color)
        if not hasattr(self, 'active_reminders') or not self.active_reminders:
            self.face.set_style(default_color, "happy")
            self.draw_bar(default_color)
        
        # Refresh reminders (always show default view with count; never auto-show a reminder card)
        self.load_reminders()
    
    def show_default_view(self):
        """Show the default homescreen: user's face, default color, and reminder count (no reminder card).
        Per-reminder face customizations are never applied here; they only apply when a reminder is triggered (apply_card).
        """
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
            self.face.set_interaction_state("idle")
            self.face.set_cute_default(True)
        n = len(getattr(self, "active_reminders", []))
        if hasattr(self, "dismiss_btn"):
            self.dismiss_btn.opacity = 0
            self.dismiss_btn.disabled = True
        if n == 0:
            self.title.text = "[b]Hi there![/b]"
            self.line.text = "Tap Reminders (button below) to set up your schedules."
        elif n == 1:
            self.title.text = "[b]You're all set[/b]"
            self.line.text = "1 reminder is active — open Reminders to change timing."
        else:
            self.title.text = "[b]You're all set[/b]"
            self.line.text = f"{n} reminders active — open Reminders to edit."
    
    def load_reminders(self):
        """Load reminders and show default view (count only). Never auto-show a reminder card until its time."""
        reminders = config_manager.get("reminders", [])
        self.active_reminders = [r for r in reminders if r.get("is_active", True)]
        self.show_default_view()
    
    def draw_bar(self, accent):
        """Draw the bottom bar with accent color."""
        self.bar.canvas.before.clear()
        r, g, b, a = accent
        with self.bar.canvas.before:
            Color(r, g, b, 0.95)
            RoundedRectangle(
                pos=(10, 10),
                size=(Window.width-20, Window.height*0.28-20),
                radius=[18]
            )
            Color(0.04, 0.05, 0.09, 0.94)
            RoundedRectangle(
                pos=(16, 16),
                size=(Window.width-32, Window.height*0.28-32),
                radius=[14]
            )
    
    def apply_card(self, reminder):
        """
        Apply a reminder card to the display. Only called when a reminder is actually shown
        (time-triggered, test-in-10, or manual next). Per-reminder face customizations
        are applied here only, not on the default view.
        """
        self.face.set_cute_default(False)
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
        action = reminder.get("action")
        if reminder.get("reminder_template") == "focus":
            action = "focus"
        if not action and reminder.get("text"):
            # Infer action from text for reminders saved before "action" existed
            t = reminder["text"].lower().strip()
            if t == "focus":
                action = "focus"
            elif "drink" in t or "water" in t or "hydrat" in t:
                action = "drink"
            elif "stretch" in t or "exercise" in t:
                action = "stretch"
            elif "move" in t or "walk" in t or "movement" in t:
                action = "move"
        icon_path = reminder.get("icon_path")
        icon_text = reminder.get("icon", "")
        
        icon_shown = False
        # Focus: show robot face (no stick figure)
        if action == "focus":
            if hasattr(self, "stick_figure_icon"):
                self.stick_figure_icon.opacity = 0.0
            self.icon_image.opacity = 0.0
            self.face.opacity = 1.0
            icon_shown = True
        # Prefer Kivy-drawn stick figure when reminder has action (no image file needed)
        elif action in ("drink", "stretch", "move") and hasattr(self, "stick_figure_icon"):
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
        self.title.text = f"[b]{icon_text} {title}[/b]" if icon_text else f"[b]{title}[/b]"
        # Use description if available, otherwise use text as line
        description = reminder.get("description")
        if description:
            self.line.text = description
        else:
            # Fallback: show text in line if no description
            self.line.text = reminder.get("text", "")
    
    def dismiss(self, *args):
        """End the on-screen reminder early (same as waiting for the timer)."""
        cb = getattr(self, "_reminder_timer_cb", None)
        if cb is not None:
            Clock.unschedule(cb)
            self._reminder_timer_cb = None
        if hasattr(self, "dismiss_btn"):
            self.dismiss_btn.opacity = 0
            self.dismiss_btn.disabled = True
        self.triggered_reminder_showing = False
        self.cycling_paused_until = None
        return_to = getattr(self, "_return_screen", "homescreen")
        if return_to != "homescreen":
            self.manager.current = return_to
        else:
            self.load_reminders()
    
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
    
    REMINDER_DISPLAY_SECONDS = 30  # Show reminder 30s unless user taps Dismiss

    def trigger_reminder(self, reminder, is_real_trigger=False):
        """
        Trigger a reminder - display on homescreen for REMINDER_DISPLAY_SECONDS or until Dismiss.
        """
        old_cb = getattr(self, "_reminder_timer_cb", None)
        if old_cb is not None:
            Clock.unschedule(old_cb)
            self._reminder_timer_cb = None

        if not is_real_trigger and not hasattr(self, "_return_screen"):
            self._return_screen = self.manager.current

        self.apply_card(reminder)
        self.triggered_reminder_showing = True
        self.cycling_paused_until = datetime.now().timestamp() + float(self.REMINDER_DISPLAY_SECONDS)

        if hasattr(self, "dismiss_btn"):
            self.dismiss_btn.opacity = 1.0
            self.dismiss_btn.disabled = False

        def _after_reminder_duration(dt):
            self._reminder_timer_cb = None
            if hasattr(self, "dismiss_btn"):
                self.dismiss_btn.opacity = 0
                self.dismiss_btn.disabled = True
            self.triggered_reminder_showing = False
            self.cycling_paused_until = None
            return_to = getattr(self, "_return_screen", "homescreen")
            if return_to != "homescreen":
                self.manager.current = return_to
            else:
                self.load_reminders()

        self._reminder_timer_cb = _after_reminder_duration
        Clock.schedule_once(self._reminder_timer_cb, self.REMINDER_DISPLAY_SECONDS)
    
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
        if getattr(self, "triggered_reminder_showing", False):
            return
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
    
    def setup_ui(self):
        """Build the simplified settings UI."""
        layout = FloatLayout()
        
        # Background
        with layout.canvas.before:
            Color(0.05, 0.05, 0.10, 1.0)
            Rectangle(pos=layout.pos, size=Window.size)
        
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

        # Short icon / emoji label (optional; used in reminder title)
        icon_text_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(50), spacing=dp(10))
        icon_text_label = Label(
            text="Icon tag:",
            font_size="20sp",
            color=(0.9, 0.9, 1, 1),
            halign="left",
            size_hint_x=0.25,
            text_size=(None, None)
        )
        self.icon_input = TextInput(
            text="",
            multiline=False,
            size_hint_x=0.75,
            font_size="18sp",
            background_color=(0.15, 0.15, 0.20, 1.0),
            foreground_color=(1, 1, 1, 1),
            padding=dp(10),
            hint_text="e.g. emoji or short label (optional)"
        )
        icon_text_row.add_widget(icon_text_label)
        icon_text_row.add_widget(self.icon_input)
        form_layout.add_widget(icon_text_row)
        
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
        self.trigger_type_btn.text = "Specific Time"
        self.time_input.text = "12:00"
        self.am_pm_btn.text = "PM"
        self.time_input.disabled = False
        self.interval_input.text = "5"
        self.interval_input.disabled = True
        self.repeat_btn.text = "daily"
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
        
        text_stripped = self.text_input.text.strip() or ""
        tx = text_stripped.lower()
        inferred_action = None
        if "drink" in tx or "water" in tx or "hydrat" in tx:
            inferred_action = "drink"
        elif "stretch" in tx or "exercise" in tx:
            inferred_action = "stretch"
        elif "move" in tx or "walk" in tx or "movement" in tx:
            inferred_action = "move"
        elif tx.strip() == "focus":
            inferred_action = "focus"
        elif "break" in tx:
            inferred_action = "stretch"

        rem_template = None
        for pid, pdata in REMINDER_PRESETS.items():
            if pdata["text"].lower() == tx.strip():
                rem_template = pid
                break
        if rem_template is None and self.reminder_index is not None and 0 <= self.reminder_index < len(reminders):
            rem_template = reminders[self.reminder_index].get("reminder_template")

        accent = list(config_manager.get("default_colors.primary", [0.10, 0.90, 1.00, 1.0]))
        mood = self.mood_btn.text
        if rem_template in REMINDER_PRESETS:
            accent = list(REMINDER_PRESETS[rem_template]["accent"])
            mood = REMINDER_PRESETS[rem_template]["mood"]
        if face_expression and isinstance(face_expression, dict):
            mood = face_expression.get("mood", mood)

        # Create reminder object with all fields
        reminder = {
            "id": reminder_id,  # Stable UUID
            "text": text_stripped or None,  # nullable
            "icon": self.icon_input.text.strip() or None,  # nullable (text icon for backward compatibility)
            "icon_path": icon_path,  # nullable (image file path)
            "action": inferred_action,
            "reminder_template": rem_template,
            "face_expression": face_expression,  # nullable (dict with eyes, mouth, mood)
            "trigger_type": trigger_type,  # "Specific Time" or "Every X Minutes"
            "trigger_time": trigger_time,  # Time string (HH:MM) or None for interval
            "interval_minutes": interval_minutes,  # Minutes interval or None for time-based
            "repeat_settings": self.repeat_btn.text,  # Required
            "is_active": self.is_active_toggle.state == "down",  # Required
            "accent": accent,
            "mood": mood,
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
        
        text_stripped = self.text_input.text.strip() or "Test reminder"
        tx = text_stripped.lower()
        inferred_action = None
        if "drink" in tx or "water" in tx or "hydrat" in tx:
            inferred_action = "drink"
        elif "stretch" in tx or "exercise" in tx:
            inferred_action = "stretch"
        elif "move" in tx or "walk" in tx or "movement" in tx:
            inferred_action = "move"
        elif tx.strip() == "focus":
            inferred_action = "focus"
        elif "break" in tx:
            inferred_action = "stretch"

        test_template = None
        for pid, pdata in REMINDER_PRESETS.items():
            if pdata["text"].lower() == tx.strip():
                test_template = pid
                break

        accent = list(config_manager.get("default_colors.primary", [0.10, 0.90, 1.00, 1.0]))
        mood = self.mood_btn.text
        if test_template in REMINDER_PRESETS:
            accent = list(REMINDER_PRESETS[test_template]["accent"])
            mood = REMINDER_PRESETS[test_template]["mood"]

        return {
            "id": str(uuid.uuid4()),
            "text": text_stripped,
            "icon": self.icon_input.text.strip() if hasattr(self, 'icon_input') else None,
            "icon_path": icon_path,
            "action": inferred_action,
            "reminder_template": test_template,
            "face_expression": face_expression,
            "trigger_type": trigger_type,
            "trigger_time": trigger_time,
            "interval_minutes": interval_minutes,
            "repeat_settings": self.repeat_btn.text,
            "is_active": True,
            "accent": accent,
            "mood": mood,
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


class RemindersScreen(Screen):
    """
    1) List of reminders (with On/Off). 2) Sequential form: type → schedule → colour → Save.
    Drink / move / focus / break still use animated stick figure or face via reminder action.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._mute_preset_load = False
        self.setup_ui()

    def on_pre_enter(self, *args):
        config_manager.ensure_default_reminders()
        self.load_reminders()
        self._load_preset_into_form()

    @staticmethod
    def _accent_from_swatch_label(label):
        for name, c in REMINDER_COLOR_SWATCHES:
            if name == label:
                return list(c)
        return list(REMINDER_COLOR_SWATCHES[0][1])

    @staticmethod
    def _swatch_label_for_accent(accent):
        if not accent or len(accent) < 4:
            return REMINDER_COLOR_SWATCHES[0][0]
        best = REMINDER_COLOR_SWATCHES[0][0]
        best_d = 1e9
        try:
            for name, c in REMINDER_COLOR_SWATCHES:
                d = sum((float(accent[i]) - c[i]) ** 2 for i in range(3))
                if d < best_d:
                    best_d, best = d, name
        except (TypeError, ValueError, IndexError):
            pass
        return best

    def _preset_id_from_label(self, label):
        for pid in REMINDER_PRESET_ORDER:
            if REMINDER_PRESETS[pid]["label"] == label:
                return pid
        return REMINDER_PRESET_ORDER[0]

    def _index_for_template(self, tid):
        for i, r in enumerate(config_manager.get("reminders", [])):
            if r.get("reminder_template") == tid:
                return i
        return None

    def _ensure_reminder_for_template(self, tid):
        reminders = list(config_manager.get("reminders", []))
        idx = self._index_for_template(tid)
        if idx is not None:
            return idx
        reminders.append(create_preset_reminder(tid))
        config_manager.set("reminders", reminders)
        return len(reminders) - 1

    def _time_12h_to_24h_local(self, time_str_12h, am_pm):
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

    def _time_24h_to_12h_display_local(self, time_str_24h):
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

    def _format_summary(self, r):
        tt = r.get("trigger_type", "Specific Time")
        if tt == "Every X Minutes" and r.get("interval_minutes") is not None:
            return f"Every {r['interval_minutes']} min · {r.get('repeat_settings', 'daily')}"
        return f"{r.get('trigger_time', '')} · {r.get('repeat_settings', 'daily')}"

    def setup_ui(self):
        root = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(5))
        with root.canvas.before:
            Color(0.05, 0.05, 0.10, 1.0)
            bg_rect = Rectangle(pos=root.pos, size=root.size)

        def sync_bg(*_):
            bg_rect.pos = root.pos
            bg_rect.size = root.size

        root.bind(pos=sync_bg, size=sync_bg)

        root.add_widget(
            Label(
                text="Reminders",
                font_size="26sp",
                bold=True,
                color=(1, 1, 1, 1),
                size_hint_y=None,
                height=dp(34),
                halign="center",
            )
        )

        root.add_widget(
            Label(
                text="Your reminders",
                font_size="15sp",
                bold=True,
                color=(0.75, 0.8, 0.95, 1),
                size_hint_y=None,
                height=dp(22),
                halign="left",
            )
        )

        scroll = ScrollView(
            size_hint_y=None,
            height=dp(158),
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=dp(6),
            scroll_type=["bars", "content"],
            scroll_timeout=280,
            scroll_distance=dp(12),
        )
        self.reminder_list = BoxLayout(
            orientation="vertical",
            spacing=dp(5),
            padding=dp(4),
            size_hint_y=None,
            size_hint_x=1,
        )
        self.reminder_list.bind(minimum_height=self.reminder_list.setter("height"))
        scroll.add_widget(self.reminder_list)
        root.add_widget(scroll)

        root.add_widget(
            Label(
                text="—",
                font_size="11sp",
                color=(0.35, 0.38, 0.5, 1),
                size_hint_y=None,
                height=dp(10),
            )
        )

        root.add_widget(
            Label(
                text="Set up a reminder",
                font_size="15sp",
                bold=True,
                color=(0.82, 0.88, 1, 1),
                size_hint_y=None,
                height=dp(22),
                halign="left",
            )
        )

        root.add_widget(
            Label(
                text="1. Reminder type",
                font_size="12sp",
                color=(0.65, 0.72, 0.88, 1),
                size_hint_y=None,
                height=dp(18),
                halign="left",
            )
        )
        self.preset_spinner = Spinner(
            text=REMINDER_PRESETS[REMINDER_PRESET_ORDER[0]]["label"],
            values=tuple(REMINDER_PRESETS[k]["label"] for k in REMINDER_PRESET_ORDER),
            size_hint_y=None,
            height=dp(36),
            background_color=(0.18, 0.22, 0.34, 1),
            color=(1, 1, 1, 1),
        )
        self.preset_spinner.bind(text=self._on_preset_changed)
        root.add_widget(self.preset_spinner)

        root.add_widget(
            Label(
                text="2. When & how often",
                font_size="12sp",
                color=(0.65, 0.72, 0.88, 1),
                size_hint_y=None,
                height=dp(18),
                halign="left",
            )
        )

        row_when = BoxLayout(size_hint_y=None, height=dp(34), spacing=dp(6))
        row_when.add_widget(
            Label(text="Mode", size_hint_x=0.22, font_size="13sp", color=(0.8, 0.84, 0.95, 1))
        )
        self.trigger_spinner = Spinner(
            text="Every X Minutes",
            values=("Every X Minutes", "Specific Time"),
            size_hint_x=0.78,
            background_color=(0.18, 0.22, 0.34, 1),
            color=(1, 1, 1, 1),
        )
        self.trigger_spinner.bind(text=self._on_trigger_changed)
        row_when.add_widget(self.trigger_spinner)
        root.add_widget(row_when)

        row_vals = BoxLayout(size_hint_y=None, height=dp(34), spacing=dp(4))
        self.time_input = TextInput(
            hint_text="2:30",
            multiline=False,
            size_hint_x=0.26,
            font_size="14sp",
            padding=[dp(5), dp(5), 0, 0],
            background_color=(0.11, 0.13, 0.18, 1),
            foreground_color=(1, 1, 1, 1),
        )
        self.am_pm_spinner = Spinner(
            text="PM",
            values=("AM", "PM"),
            size_hint_x=0.16,
            background_color=(0.18, 0.22, 0.34, 1),
            color=(1, 1, 1, 1),
        )
        self.interval_input = TextInput(
            hint_text="min",
            multiline=False,
            size_hint_x=0.5,
            font_size="14sp",
            padding=[dp(5), dp(5), 0, 0],
            background_color=(0.11, 0.13, 0.18, 1),
            foreground_color=(1, 1, 1, 1),
        )
        row_vals.add_widget(
            Label(text="Time", size_hint_x=0.12, font_size="10sp", color=(0.55, 0.6, 0.75, 1))
        )
        row_vals.add_widget(self.time_input)
        row_vals.add_widget(self.am_pm_spinner)
        row_vals.add_widget(
            Label(text="Every", size_hint_x=0.1, font_size="10sp", color=(0.55, 0.6, 0.75, 1))
        )
        row_vals.add_widget(self.interval_input)
        root.add_widget(row_vals)

        row_rep = BoxLayout(size_hint_y=None, height=dp(34), spacing=dp(6))
        row_rep.add_widget(
            Label(text="Repeat", size_hint_x=0.22, font_size="13sp", color=(0.8, 0.84, 0.95, 1))
        )
        self.repeat_spinner = Spinner(
            text="daily",
            values=("daily", "once", "weekdays", "weekends", "weekly"),
            size_hint_x=0.78,
            background_color=(0.18, 0.22, 0.34, 1),
            color=(1, 1, 1, 1),
        )
        row_rep.add_widget(self.repeat_spinner)
        root.add_widget(row_rep)

        root.add_widget(
            Label(
                text="3. Colour (when it pops up)",
                font_size="12sp",
                color=(0.65, 0.72, 0.88, 1),
                size_hint_y=None,
                height=dp(18),
                halign="left",
            )
        )
        self.color_spinner = Spinner(
            text=REMINDER_COLOR_SWATCHES[0][0],
            values=tuple(n for n, _ in REMINDER_COLOR_SWATCHES),
            size_hint_y=None,
            height=dp(36),
            background_color=(0.18, 0.22, 0.34, 1),
            color=(1, 1, 1, 1),
        )
        root.add_widget(self.color_spinner)

        btn_row = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(8))
        save_btn = Button(
            text="Save",
            font_size="15sp",
            bold=True,
            background_color=(0.2, 0.68, 0.42, 1),
            background_normal="",
            color=(1, 1, 1, 1),
        )
        test_btn = Button(
            text="Test in 10 sec",
            font_size="13sp",
            bold=True,
            background_color=(0.52, 0.32, 0.82, 1),
            background_normal="",
            color=(1, 1, 1, 1),
        )
        save_btn.bind(on_release=self._quick_save)
        test_btn.bind(on_release=self._quick_test_10)
        btn_row.add_widget(save_btn)
        btn_row.add_widget(test_btn)
        root.add_widget(btn_row)

        adv = Button(
            text="More options (full editor)",
            font_size="11sp",
            background_color=(0.28, 0.38, 0.55, 1),
            background_normal="",
            color=(0.92, 0.94, 1, 1),
            size_hint_y=None,
            height=dp(30),
        )
        adv.bind(on_release=self._open_full_editor)
        root.add_widget(adv)

        self.status_label = Label(
            text="",
            font_size="11sp",
            color=(1, 0.45, 0.45, 1),
            halign="center",
            size_hint_y=None,
            height=dp(18),
        )
        root.add_widget(self.status_label)

        bottom = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(44),
            spacing=dp(10),
        )
        add_btn = Button(
            text="+ Custom reminder",
            font_size="14sp",
            bold=True,
            background_color=(0.22, 0.52, 0.36, 1),
            background_normal="",
            color=(1, 1, 1, 1),
        )
        add_btn.bind(on_release=self.show_add_dialog)
        home_btn = Button(
            text="Home",
            font_size="14sp",
            bold=True,
            background_color=(0.32, 0.48, 0.78, 1),
            background_normal="",
            color=(1, 1, 1, 1),
        )
        home_btn.bind(on_release=self.return_home)
        bottom.add_widget(add_btn)
        bottom.add_widget(home_btn)
        root.add_widget(bottom)

        self.add_widget(root)
        self._sync_trigger_inputs_disabled_state()

    def _on_preset_changed(self, spinner, text):
        if getattr(self, "_mute_preset_load", False):
            return
        self._load_preset_into_form()
        self.status_label.text = ""

    def _on_trigger_changed(self, spinner, text):
        self._sync_trigger_inputs_disabled_state()

    def _sync_trigger_inputs_disabled_state(self):
        spec = self.trigger_spinner.text == "Specific Time"
        self.time_input.disabled = not spec
        self.am_pm_spinner.disabled = not spec
        self.interval_input.disabled = spec

    def _load_preset_into_form(self):
        config_manager.ensure_default_reminders()
        tid = self._preset_id_from_label(self.preset_spinner.text)
        idx = self._ensure_reminder_for_template(tid)
        r = config_manager.get("reminders", [])[idx]
        self._mute_preset_load = True
        self.trigger_spinner.text = r.get("trigger_type", "Every X Minutes")
        if r.get("trigger_type") == "Specific Time":
            t24 = r.get("trigger_time") or "12:00"
            disp, ap = self._time_24h_to_12h_display_local(t24)
            self.time_input.text = disp
            self.am_pm_spinner.text = ap
        else:
            self.time_input.text = "12:00"
            self.am_pm_spinner.text = "PM"
        im = r.get("interval_minutes")
        self.interval_input.text = str(im if im is not None else REMINDER_PRESETS[tid]["default_interval"])
        self.repeat_spinner.text = r.get("repeat_settings", "daily")
        self.color_spinner.text = self._swatch_label_for_accent(r.get("accent"))
        self._mute_preset_load = False
        self._sync_trigger_inputs_disabled_state()

    def _quick_save(self, instance):
        tid = self._preset_id_from_label(self.preset_spinner.text)
        config_manager.ensure_default_reminders()
        idx = self._ensure_reminder_for_template(tid)
        reminders = list(config_manager.get("reminders", []))
        r = reminders[idx]
        p = REMINDER_PRESETS[tid]
        r["trigger_type"] = self.trigger_spinner.text
        if self.trigger_spinner.text == "Specific Time":
            tt = self._time_12h_to_24h_local(self.time_input.text.strip(), self.am_pm_spinner.text)
            if not tt:
                self.status_label.text = "Invalid time (e.g. 2:30)"
                self.status_label.color = (1, 0.45, 0.45, 1)
                return
            r["trigger_time"] = tt
            r["interval_minutes"] = None
        else:
            try:
                im = int(self.interval_input.text.strip())
                im = max(1, min(1440, im))
            except ValueError:
                self.status_label.text = "Interval: 1–1440 minutes"
                self.status_label.color = (1, 0.45, 0.45, 1)
                return
            r["interval_minutes"] = im
            r["trigger_time"] = None
        r["repeat_settings"] = self.repeat_spinner.text
        r["text"] = p["text"]
        r["action"] = p["action"]
        r["accent"] = self._accent_from_swatch_label(self.color_spinner.text)
        r["mood"] = p["mood"]
        r["description"] = p["description"]
        r["reminder_template"] = tid
        config_manager.set("reminders", reminders)
        self.status_label.text = "Saved."
        self.status_label.color = (0.4, 0.95, 0.55, 1)
        Clock.schedule_once(lambda dt: setattr(self.status_label, "text", ""), 2.5)
        self.load_reminders()

    def _build_preview_from_form(self):
        tid = self._preset_id_from_label(self.preset_spinner.text)
        p = REMINDER_PRESETS[tid]
        trigger_type = self.trigger_spinner.text
        trigger_time = None
        interval_minutes = None
        if trigger_type == "Specific Time":
            trigger_time = self._time_12h_to_24h_local(
                self.time_input.text.strip(), self.am_pm_spinner.text
            ) or "12:00"
        else:
            try:
                interval_minutes = max(1, min(1440, int(self.interval_input.text.strip())))
            except ValueError:
                interval_minutes = p["default_interval"]
        return {
            "id": str(uuid.uuid4()),
            "reminder_template": tid,
            "text": p["text"],
            "action": p["action"],
            "icon": None,
            "icon_path": None,
            "face_expression": None,
            "trigger_type": trigger_type,
            "trigger_time": trigger_time,
            "interval_minutes": interval_minutes,
            "repeat_settings": self.repeat_spinner.text,
            "is_active": True,
            "accent": self._accent_from_swatch_label(self.color_spinner.text),
            "mood": p["mood"],
            "description": p["description"],
        }

    def _quick_test_10(self, instance):
        self.status_label.text = "Home in 10 sec…"
        self.status_label.color = (0.85, 0.8, 1, 1)

        def _go(dt):
            self.status_label.text = ""
            preview = self._build_preview_from_form()
            hs = self.manager.get_screen("homescreen")
            hs._return_screen = "reminders"
            self.manager.current = "homescreen"
            hs.trigger_reminder(preview, is_real_trigger=False)

        Clock.schedule_once(_go, 10.0)

    def _open_full_editor(self, instance):
        tid = self._preset_id_from_label(self.preset_spinner.text)
        config_manager.ensure_default_reminders()
        idx = self._ensure_reminder_for_template(tid)
        self.edit_reminder(idx)

    def load_reminders(self):
        self.reminder_list.clear_widgets()
        config_manager.ensure_default_reminders()
        reminders = config_manager.get("reminders", [])
        for tid in REMINDER_PRESET_ORDER:
            idx = self._index_for_template(tid)
            if idx is None:
                continue
            r = reminders[idx]
            active = r.get("is_active", True)
            row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(6))
            lbl = Label(
                text=f"{REMINDER_PRESETS[tid]['label']}: {self._format_summary(r)}",
                font_size="14sp",
                halign="left",
                valign="middle",
                color=(0.92, 0.94, 1, 1),
                size_hint_x=0.78,
            )
            lbl.bind(size=lambda lb, s: setattr(lb, "text_size", (s[0] - dp(4), None)))
            tg = Button(
                text="On" if active else "Off",
                size_hint_x=0.22,
                font_size="13sp",
                bold=True,
                background_color=(0.22, 0.62, 0.4, 1) if active else (0.38, 0.4, 0.48, 1),
                background_normal="",
                color=(1, 1, 1, 1),
            )
            tg.bind(on_release=lambda b, i=idx: self.toggle_reminder(i))
            row.add_widget(lbl)
            row.add_widget(tg)
            self.reminder_list.add_widget(row)

        custom_header = False
        for i, r in enumerate(reminders):
            if r.get("reminder_template") in REMINDER_PRESET_ORDER:
                continue
            if not custom_header:
                custom_header = True
                self.reminder_list.add_widget(
                    Label(
                        text="Custom reminders",
                        font_size="13sp",
                        bold=True,
                        color=(0.65, 0.7, 0.85, 1),
                        size_hint_y=None,
                        height=dp(26),
                        halign="left",
                    )
                )
            row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(6))
            txt = (r.get("text") or "Untitled")[:36]
            lbl = Label(
                text=f"{txt}: {self._format_summary(r)}",
                font_size="13sp",
                halign="left",
                color=(0.88, 0.9, 1, 1),
                size_hint_x=0.62,
            )
            lbl.bind(size=lambda lb, s: setattr(lb, "text_size", (s[0] - dp(4), None)))
            ed = Button(
                text="Edit",
                size_hint_x=0.18,
                font_size="13sp",
                background_color=(0.3, 0.5, 0.85, 1),
                background_normal="",
                color=(1, 1, 1, 1),
            )
            ed.bind(on_release=lambda b, ii=i: self.edit_reminder(ii))
            del_btn = Button(
                text="Del",
                size_hint_x=0.18,
                font_size="11sp",
                background_color=(0.75, 0.28, 0.28, 1),
                background_normal="",
                color=(1, 1, 1, 1),
            )
            del_btn.bind(on_release=lambda b, ii=i: self.delete_reminder(ii))
            row.add_widget(lbl)
            row.add_widget(ed)
            row.add_widget(del_btn)
            self.reminder_list.add_widget(row)

    def show_add_dialog(self, instance):
        edit_screen = self.manager.get_screen("reminder_edit")
        edit_screen.setup_for_new()
        self.manager.current = "reminder_edit"

    def edit_reminder(self, index):
        edit_screen = self.manager.get_screen("reminder_edit")
        edit_screen.setup_for_edit(index)
        self.manager.current = "reminder_edit"

    def toggle_reminder(self, index):
        reminders = config_manager.get("reminders", [])
        if 0 <= index < len(reminders):
            reminders[index]["is_active"] = not reminders[index].get("is_active", True)
            config_manager.set("reminders", reminders)
            self.load_reminders()

    def delete_reminder(self, index):
        reminders = config_manager.get("reminders", [])
        if 0 <= index < len(reminders):
            reminders.pop(index)
            config_manager.set("reminders", reminders)
            self.load_reminders()

    def return_home(self, instance):
        self.manager.current = "homescreen"

# ============================================================================
# MAIN APPLICATION
# ============================================================================

