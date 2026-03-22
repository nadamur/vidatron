# Vidatron UI — Feature Summary

A concise list of everything implemented in the Vidatron UI (Kivy app).

---

## 1. Application shell

- **Window**: Fixed 800×480, minimum 800×480 (e.g. for embedded display).
- **Boot behavior**:
  - **First time**: `first_time_setup_complete` false → show **Welcome** screen.
  - **Returning**: `first_time_setup_complete` true → go straight to **Homescreen**.
- **Keyboard shortcuts** (when no `TextInput` is focused):
  - `h` → Homescreen  
  - `s` → Settings  
  - `r` → Reminders  
  - `d` → Dismiss current reminder (on Homescreen)  
  - `n` → Next reminder card (on Homescreen)

---

## 2. Configuration & persistence

- **File**: `vidatron_config.json` in the project directory.
- **Deep merge**: Loaded config is merged with defaults so new keys don’t wipe existing data.
- **Stored data**:
  - `first_time_setup_complete`
  - `face_customization`: `selected_eyes`, `selected_mouth` (nullable)
  - `font_settings`: `style` (e.g. Roboto, DejaVuSans), `size` (sp)
  - `default_colors`: `primary` (RGBA), `background` (RGBA)
  - `reminders`: list of reminder objects
  - `last_fired`: reminder id → `"YYYY-MM-DD HH:MM"` for trigger logic
  - `default_reminders_added`: ensures default reminders are added once

**ConfigManager** API: `get(key, default)`, `set(key, value)`, `load_config()`, `save_config()`, `ensure_default_reminders()`.

---

## 3. Welcome screen

- Title: “Vidatron”, subtitle: “Your Personal Robot Assistant”.
- **Current time** shown top-right (overlay).
- **Four actions**:
  - **Go with Default** — Saves default face (round eyes, smile), default color (blue), Roboto; marks setup complete; goes to Homescreen.
  - **Customize** — Starts 3-step setup: Face → Font → Colors.
  - **Settings** — Opens Settings screen.
  - **Reminders** — Opens Reminders screen.

---

## 4. First-time setup (3 steps)

### Step 1 — Setup Face

- Title: “Step 1/3: Customize your robot’s face”.
- **Eyes**: Round, Oval, Narrow, Wide, Small, or **None**.
- **Mouth**: Wide, Small, Expressive, Neutral, Curved/Smile, or **None**.
- **Next** → Step 2 (Font). Choices saved to `face_customization`.

### Step 2 — Setup Font

- Title: “Step 2/3: Font”.
- **Style**: Roboto, DejaVuSans.
- **Size**: Numeric input (sp). Saved to `font_settings`.
- **Next** → Step 3 (Colors).

### Step 3 — Setup Colors

- Title: “Step 3/3: Default Colors”.
- **Preset colors**: Blue, Purple, Pink, Orange, Green (saved as `default_colors.primary`).
- **Back** → Step 2.
- **Complete Setup** → Saves color, sets `first_time_setup_complete` true, goes to Homescreen.

---

## 5. Homescreen

- **Layout**:
  - **Top ~72%**: Robot **Face** (or reminder card when a reminder is showing).
  - **Bottom ~28%**: **Bar** with accent color; **title** and **line** text (reminder count or reminder content).
- **Current time** top-right (overlay).
- **Default view** (no reminder card): Robot face, default accent, title “Reminders”, line “No reminders” / “1 reminder” / “N reminders”.
- **Reminder card view** (when a reminder is triggered or cycled):
  - **Icon**: Either **StickFigureIcon** (action “drink” or “stretch”) with accent-colored background, or **Image** from `icon_path` if file exists; otherwise face stays visible.
  - **Face expression**: Per-reminder `face_expression` (eyes, mouth, mood) applied when showing that reminder; else global face customization + reminder mood.
  - **Bar** and **text**: Reminder accent, title (reminder text), line (description).
- **Reminder logic**:
  - **Time-based**: `check_reminders(dt)` every 1 s; “Every X Minutes” uses `interval_minutes`; “Specific Time” uses `trigger_time` + `repeat_settings` (once/daily/weekdays/weekends/weekly). `last_fired` used to avoid duplicate triggers; “once” disables reminder after firing.
  - **Display**: When a reminder triggers, app switches to Homescreen (if not already), shows that reminder’s card for **60 seconds**, then returns to previous screen or default Homescreen view. Manual **dismiss** or **next card** available.
- **Cycling**: `cycle_if_allowed(dt)` every 7 s cycles to next active reminder when no triggered reminder is on screen.
- **Navigation**: “Home” (or equivalent) can return to this default view; Settings/Reminders reached via Welcome or shortcuts.

---

## 6. Robot Face widget

- **Animated** (e.g. 30 FPS): blink, pupil movement, mood-based mouth.
- **Moods**: happy (smile), calm (neutral), wink, focused.
- **Customization**: `set_customization(eyes, mouth)` — eyes/mouth options as in Setup Face; supports None.
- **Style**: `set_style(accent, mood)` — accent color (RGBA), mood. Accent drives base and glow colors.

---

## 7. Stick-figure action icon

- **Actions**: “drink” (cup to mouth), “stretch” (side stretch).
- **Background**: Same style as Face (accent-derived), so reminder card is never plain black.
- **Usage**: When a reminder has `action` “drink” or “stretch” (or text implies it), this icon is shown instead of the face; otherwise `icon_path` image is used if present and file exists.

---

## 8. Settings screen

- Title “Settings”.
- Short text: To customize the robot’s face, use Customize from Home.
- **Tools: Reminders** — Opens Reminders screen.
- **← Return to Homescreen** — Goes to Homescreen.

---

## 9. Reminders screen

- **List** of all reminders (from config); each row: reminder text, toggle (active/inactive), Edit, Delete.
- **Add** — Opens Reminder Edit (new reminder).
- **Edit** — Opens Reminder Edit (existing reminder); ReminderEditScreen added to manager when needed.
- **Toggle** — Flips `is_active` and saves.
- **Delete** — Removes reminder from config and refreshes list.
- **← Return to Homescreen** — Back to Homescreen.
- **on_pre_enter**: Refreshes list from config.

---

## 10. Reminder Edit screen

- **Modes**: New reminder (`setup_for_new`) or edit by index (`setup_for_edit(index)`).
- **Fields**:
  - **Text**: Reminder title.
  - **Description**: Optional second line.
  - **Icon**: None, Drink Water, Stretch, or Custom path (`icon_path`); optional `action` for built-in stick figure.
  - **Face expression** (optional): Override eyes/mouth/mood for this reminder only; constraint: at least one of eyes or mouth set.
  - **Trigger type**: “Specific Time” or “Every X Minutes”.
  - **Specific time**: Time input + AM/PM; **Repeat**: once, daily, weekdays, weekends, weekly.
  - **Every X Minutes**: Interval (minutes).
  - **Mood**: happy, calm, wink, focused (for face when this reminder shows).
  - **Accent**: RGBA (default from config primary).
  - **Active**: Checkbox/toggle.
- **Test in 10 sec**: Builds a temporary reminder from current form, triggers it in 10 s (no save); useful for testing.
- **Save**: Creates or updates reminder in config (stable UUID on edit), then e.g. back to Reminders.
- **Cancel**: Discard and go back.

---

## 11. Default reminders

- **Ensure once**: `ensure_default_reminders()` adds (if missing):
  - **“Drink water”**: action “drink”, interval 1 min (for testing), accent blue, description “Stay hydrated!”.
  - **“Get up and stretch”**: action “stretch”, interval 2 min (for testing), accent green, description “Take a break and move around”.
- Both are **active** by default and can be edited or toggled like any other reminder.

---

## 12. Screens summary

| Screen            | Purpose                                              |
|-------------------|------------------------------------------------------|
| Welcome           | First entry; Go Default / Customize / Settings / Reminders |
| Setup Face        | Step 1: eyes, mouth                                  |
| Setup Font        | Step 2: font style, size                              |
| Setup Colors      | Step 3: default accent color; complete setup         |
| Homescreen        | Face or reminder card, time, bar, reminder count/logic |
| Settings          | Shortcut to Reminders; return home                    |
| Reminders         | List, add/edit/toggle/delete reminders               |
| Reminder Edit     | Create/edit reminder; all fields; Test in 10 s       |

---

## 13. Technical notes

- **Kivy**: ScreenManager, FloatLayout, BoxLayout, ScrollView, Buttons, Labels, TextInput, DropDown, Image, etc.
- **Clocks**: `check_reminders` every 1 s; `cycle_if_allowed` every 7 s; reminder display 60 s; “Test in 10 s” uses `schedule_once(..., 10.0)`.
- **Paths**: `icon_path` can be relative (e.g. `assets/icons/...`) or absolute; relative resolved from project root.
- **Inference**: If a reminder has no `action` but text contains “drink”/“water” or “stretch”, Homescreen infers “drink” or “stretch” for the stick-figure icon.

This document reflects the implementation as of the current codebase.
