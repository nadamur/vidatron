"""
Configuration Management
=======================
Handles saving and loading application configuration.
"""

import json
import os
import uuid


def get_config_path():
    """
    Get absolute path to configuration file.
    Uses vidatron_config.json in the project directory.
    """
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, "vidatron_config.json")


CONFIG_FILE = get_config_path()

# Built-in wellness reminders (dropdown templates). Keys are stable IDs saved as reminder_template.
REMINDER_PRESET_ORDER = ("drink", "move", "focus", "break")
REMINDER_PRESETS = {
    "drink": {
        "label": "Drink water",
        "text": "Drink water",
        "action": "drink",
        "accent": [0.20, 0.78, 1.00, 1.0],
        "mood": "happy",
        "description": "Stay hydrated!",
        "default_interval": 45,
    },
    "move": {
        "label": "Move your body",
        "text": "Move your body",
        "action": "move",
        "accent": [1.00, 0.72, 0.12, 1.0],
        "mood": "happy",
        "description": "Walk, stretch, or change posture for a minute.",
        "default_interval": 60,
    },
    "focus": {
        "label": "Focus",
        "text": "Focus",
        "action": "focus",
        "accent": [0.58, 0.38, 0.98, 1.0],
        "mood": "focused",
        "description": "Deep work — minimize distractions for this block.",
        "default_interval": 25,
    },
    "break": {
        "label": "Take a break",
        "text": "Take a break",
        "action": "stretch",
        "accent": [1.00, 0.55, 0.30, 1.0],
        "mood": "calm",
        "description": "Rest your eyes and stretch. You earned it.",
        "default_interval": 50,
    },
}


def create_preset_reminder(preset_id):
    """New reminder dict for a built-in preset (caller saves into config)."""
    if preset_id not in REMINDER_PRESETS:
        preset_id = "drink"
    p = REMINDER_PRESETS[preset_id]
    return {
        "id": str(uuid.uuid4()),
        "reminder_template": preset_id,
        "text": p["text"],
        "action": p["action"],
        "icon": None,
        "icon_path": None,
        "face_expression": None,
        "trigger_type": "Every X Minutes",
        "trigger_time": None,
        "interval_minutes": p["default_interval"],
        "repeat_settings": "daily",
        "is_active": True,
        "accent": list(p["accent"]),
        "mood": p["mood"],
        "description": p["description"],
    }


def deep_merge(default, loaded):
    """
    Deep merge two dictionaries, preserving nested structure.
    Values from 'loaded' override 'default', but missing nested keys are preserved.
    """
    result = default.copy()
    for key, value in loaded.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


class ConfigManager:
    """
    Manages application configuration persistence.
    Handles saving and loading user preferences, setup state, and reminders.
    """
    
    def __init__(self):
        """Initialize the config manager and load existing configuration."""
        self.config = self.load_config()
    
    def load_config(self):
        """
        Load configuration from JSON file with deep merging.
        Returns default configuration if file doesn't exist.
        """
        default_config = {
            "first_time_setup_complete": False,
            "face_customization": {
                "selected_eyes": None,      # nullable - can be None or a string identifier
                "selected_mouth": None       # nullable - can be None or a string identifier
            },
            "default_colors": {
                "primary": [0.10, 0.90, 1.00, 1.0],    # default accent color
                "background": [0.02, 0.02, 0.04, 1.0]   # default background color
            },
            "reminders": [],                 # list of reminder objects
            "last_fired": {},                # reminder_id -> "YYYY-MM-DD HH:MM" for trigger tracking
            "default_reminders_added": False  # track if default reminders have been added
        }
        
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    loaded = json.load(f)
                    # Deep merge to preserve nested defaults
                    merged = deep_merge(default_config, loaded)
                    # Ensure None values are preserved (JSON null becomes None in Python)
                    # Convert string "None" to actual None if it exists
                    if isinstance(merged.get("face_customization", {}).get("selected_eyes"), str):
                        if merged["face_customization"]["selected_eyes"] == "None":
                            merged["face_customization"]["selected_eyes"] = None
                    if isinstance(merged.get("face_customization", {}).get("selected_mouth"), str):
                        if merged["face_customization"]["selected_mouth"] == "None":
                            merged["face_customization"]["selected_mouth"] = None
                    return merged
            except Exception as e:
                print(f"Error loading config: {e}")
                return default_config
        return default_config
    
    def save_config(self):
        """Save current configuration to JSON file."""
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key, default=None):
        """Get a configuration value by key path (supports nested keys)."""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key, value):
        """Set a configuration value by key path (supports nested keys)."""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self.save_config()
    
    def ensure_default_reminders(self):
        """Ensure four built-in presets exist (drink, move, focus, break) and assign reminder_template."""
        reminders = list(self.config.get("reminders", []))
        changed = False

        text_to_template = {
            "drink water": "drink",
            "move your body": "move",
            "focus": "focus",
            "take a break": "break",
            "get up and stretch": "break",
        }

        for reminder in reminders:
            if reminder.get("reminder_template") in REMINDER_PRESET_ORDER:
                continue
            key = (reminder.get("text") or "").strip().lower()
            if key in text_to_template:
                reminder["reminder_template"] = text_to_template[key]
                changed = True

        seen_templates = set()
        deduped = []
        for reminder in reminders:
            tid = reminder.get("reminder_template")
            if tid in REMINDER_PRESET_ORDER:
                if tid in seen_templates:
                    changed = True
                    continue
                seen_templates.add(tid)
            deduped.append(reminder)
        reminders = deduped

        for preset_id in REMINDER_PRESET_ORDER:
            if any(r.get("reminder_template") == preset_id for r in reminders):
                continue
            reminders.append(create_preset_reminder(preset_id))
            changed = True

        if changed:
            self.config["reminders"] = reminders
            self.config["default_reminders_added"] = True
            self.save_config()


# Global config manager instance
config_manager = ConfigManager()
