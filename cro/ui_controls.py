# ui_controls.py
"""
Beginner-friendly Pygame UI controls (no type hints, no typing module, no future imports).
Controls:
- ControlBase: shared color & interaction state (hovering, pressed)
- Button: rectangular clickable button with on_click and centered text
- RadioGroup: manages a set of RadioButton instances (mutual exclusivity)
- RadioButton: circular option with optional right-side label
- Slider: horizontal/vertical slider (orientation) with live-updating value in label
- ToggleSwitch: simple on/off switch with on_change
- TextInput: labeled text box; Enter triggers on_submit(text)
- DisplayBox: draw multiple lines of read-only text inside a box (auto-shrinks text to fit)
Author: Mr. Sharick and M365 Copilot
"""
import pygame
# -------------------------------
# ControlBase
# -------------------------------
class ControlBase:
    """Common base for simple pygame UI controls.
    Provides color derivation and basic interaction state flags so concrete
    controls can share a consistent look-and-feel and interaction semantics.
    """
    def __init__(self, color="red"):
        base = pygame.Color(color)
        self.base = base
        self.darker = (
            max(base.r - 50, 0),
            max(base.g - 50, 0),
            max(base.b - 50, 0),
        )
        self.lighter = (
            min(base.r + 50, 255),
            min(base.g + 50, 255),
            min(base.b + 50, 255),
        )
        # Interaction states
        self.hovering = False
        self.pressed = False
    def _state_color(self, hovering=None, pressed=None):
        """Return the color that matches the current (or provided) state.
        Mirrors the simple button logic:
          - pressed & hovering -> darker
          - hovering -> lighter
          - else -> base
        """
        if hovering is None:
            hovering = self.hovering
        if pressed is None:
            pressed = self.pressed
        if pressed and hovering:
            return self.darker
        elif hovering:
            return self.lighter
        else:
            return self.base
    def set_color(self, color):
        """Change the base color and recompute lighter/darker variants."""
        base = pygame.Color(color)
        self.base = base
        self.darker = (
            max(base.r - 50, 0),
            max(base.g - 50, 0),
            max(base.b - 50, 0),
        )
        self.lighter = (
            min(base.r + 50, 255),
            min(base.g + 50, 255),
            min(base.b + 50, 255),
        )
    def handle_event(self, event):
        """Default event handler (does nothing). Subclasses may override."""
        pass
    def draw(self, surface):
        """Default draw (does nothing). Subclasses may override."""
        pass
# -------------------------------
# Button
# -------------------------------
class Button(ControlBase):
    def __init__(self, x, y, w, h, color="red", on_click=None, text=None, font=None, text_color=(240, 240, 240)):
        super().__init__(color=color)
        self.rect = pygame.Rect(x, y, w, h)
        self.on_click = on_click
        # Text settings
        self.text = text
        # A "good" default font size for a button: ~50% of height, at least 12
        default_size = max(12, int(h * 0.5))
        self.font = font or pygame.font.SysFont(None, default_size)
        self.text_color = text_color
    def set_text(self, text):
        self.text = text
    def set_font(self, font):
        self.font = font
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.pressed and self.rect.collidepoint(event.pos):
                if self.on_click is not None:
                    self.on_click()
            self.pressed = False
        elif event.type == pygame.MOUSEMOTION:
            self.hovering = self.rect.collidepoint(event.pos)
    def draw(self, surface):
        color = self._state_color()
        pygame.draw.rect(surface, color, self.rect)
        # Draw centered text if present
        if self.text is not None:
            text_surf = self.font.render(self.text, True, self.text_color)
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)
# -------------------------------
# Radio Group
# -------------------------------
class RadioGroup:
    """Manages a set of RadioButton instances; ensures only one is selected."""
    def __init__(self, on_change=None):
        self.buttons = []
        self.on_change = on_change
    def add(self, radio_button):
        if radio_button not in self.buttons:
            self.buttons.append(radio_button)
            radio_button.group = self
    def select(self, radio_button):
        changed = False
        for rb in self.buttons:
            was = rb.selected
            rb.selected = (rb is radio_button)
            if rb.selected != was:
                changed = True
        if changed and self.on_change is not None:
            self.on_change(radio_button)
# -------------------------------
# Radio Button
# -------------------------------
class RadioButton(ControlBase):
    def __init__(self, x, y, radius, color="red", selected=False, label=None, font=None, on_click=None, group=None, text_color=(230, 230, 230)):
        super().__init__(color=color)
        self.center = (x, y)
        self.radius = radius
        self.rect = pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)
        self.selected = selected
        self.label = label
        self.font = font or pygame.font.SysFont(None, 18)
        self.text_color = text_color
        self.on_click = on_click
        self.group = group
        if self.group is not None:
            self.group.add(self)
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self._collide_circle(event.pos):
                self.pressed = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.pressed and self._collide_circle(event.pos):
                if self.group is not None:
                    self.group.select(self)
                else:
                    self.selected = True  # radios usually don't toggle off on click
                if self.on_click is not None:
                    self.on_click(self)
            self.pressed = False
        elif event.type == pygame.MOUSEMOTION:
            self.hovering = self._collide_circle(event.pos)
    def draw(self, surface):
        ring_color = self._state_color()
        # Outer ring
        pygame.draw.circle(surface, ring_color, self.center, self.radius, width=2)
        # Inner dot when selected
        if self.selected:
            inner_r = max(self.radius - 5, 2)
            pygame.draw.circle(surface, ring_color, self.center, inner_r)
        # Optional label
        if self.label is not None:
            text_surf = self.font.render(self.label, True, self.text_color)
            text_rect = text_surf.get_rect()
            text_rect.midleft = (self.center[0] + self.radius + 8, self.center[1])
            surface.blit(text_surf, text_rect)
    # --- Helpers ---
    def _collide_circle(self, pos):
        dx = pos[0] - self.center[0]
        dy = pos[1] - self.center[1]
        return (dx * dx + dy * dy) <= (self.radius * self.radius)
# -------------------------------
# Slider (horizontal or vertical)
# -------------------------------
class Slider(ControlBase):
    def __init__(
        self,
        x, y, w, h,
        min_value=0.0,
        max_value=1.0,
        value=None,
        color="red",
        on_change=None,
        continuous=False,
        text=None,
        font=None,
        text_color=(240, 240, 240),
        text_margin=6,
        orientation="horizontal",  # "horizontal" or "vertical"
        show_value=True,
        value_digits=0,
    ):
        super().__init__(color=color)
        self.rect = pygame.Rect(x, y, w, h)
        self.min_value = float(min_value)
        self.max_value = float(max_value)
        if value is None:
            self.value = self.min_value
        else:
            self.value = self._clamp_value(value)
        self.on_change = on_change
        self.continuous = continuous
        # Visual sizing
        self.track_height = max(4, (h if orientation == "horizontal" else w) // 4)
        self.knob_radius = max(6, (h if orientation == "horizontal" else w) // 2)
        # Label settings (centered above the slider)
        self.text = text
        default_size = max(12, int((h if orientation == "horizontal" else w) * 0.7))
        self.font = font or pygame.font.SysFont(None, default_size)
        self.text_color = text_color
        self.text_margin = text_margin
        # Orientation and display options
        self.orientation = orientation  # 'horizontal' or 'vertical'
        self.show_value = show_value
        self.value_digits = value_digits
    # --- Public API ---
    def set_value(self, v, fire_callback=True):
        v = self._clamp_value(v)
        if v != self.value:
            self.value = v
            if fire_callback and self.on_change is not None:
                self.on_change(self.value)
    def get_value(self):
        return self.value
    def set_text(self, text):
        self.text = text
    def set_font(self, font):
        self.font = font
    def handle_event(self, event):
        knob_rect = self._knob_rect()  # compute using current value
        if event.type == pygame.MOUSEBUTTONDOWN:
            if knob_rect.collidepoint(event.pos) or self.rect.collidepoint(event.pos):
                self.pressed = True
                # If clicking on the track (but not knob), jump to that position
                if not knob_rect.collidepoint(event.pos):
                    self._update_value_from_pos(event.pos, fire=self.continuous)
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.pressed:
                if (not self.continuous) and (self.on_change is not None):
                    self.on_change(self.value)
                self.pressed = False
        elif event.type == pygame.MOUSEMOTION:
            # Hover considers knob hover
            self.hovering = knob_rect.collidepoint(event.pos)
            if self.pressed:
                self._update_value_from_pos(event.pos, fire=self.continuous)
    def draw(self, surface):
        # Label text with live value (if requested)
        if self.text is not None or self.show_value:
            label = self.text if self.text is not None else ""
            if self.show_value:
                val_str = str(round(self.value, self.value_digits))
                if label:
                    label = f"{label}: {val_str}"
                else:
                    label = val_str
            text_surf = self.font.render(label, True, self.text_color)
            text_rect = text_surf.get_rect()
            text_rect.midbottom = (self.rect.centerx, self.rect.top - self.text_margin)
            surface.blit(text_surf, text_rect)
        # Color based on state
        active_color = self._state_color(hovering=self.hovering, pressed=self.pressed)
        track_color = (80, 80, 80)
        if self.orientation == "horizontal":
            # Track
            cx = self.rect.x
            cy = self.rect.centery
            track_w = self.rect.w
            pygame.draw.rect(
                surface,
                track_color,
                pygame.Rect(cx, cy - self.track_height // 2, track_w, self.track_height),
                border_radius=self.track_height // 2,
            )
            # Filled portion up to knob
            knob_x = self._value_to_pos(self.value)
            filled_w = max(0, knob_x - cx)
            pygame.draw.rect(
                surface,
                active_color,
                pygame.Rect(cx, cy - self.track_height // 2, filled_w, self.track_height),
                border_radius=self.track_height // 2,
            )
            # Knob
            knob_center = (knob_x, cy)
            pygame.draw.circle(surface, active_color, knob_center, self.knob_radius)
            pygame.draw.circle(surface, (20, 20, 20), knob_center, self.knob_radius, width=2)
        else:  # vertical
            # Track (vertical): aligned centered x, spanning height
            cx = self.rect.centerx
            cy = self.rect.y
            track_h = self.rect.h
            pygame.draw.rect(
                surface,
                track_color,
                pygame.Rect(cx - self.track_height // 2, cy, self.track_height, track_h),
                border_radius=self.track_height // 2,
            )
            # Filled portion: from bottom (min) up to knob
            knob_y = self._value_to_pos(self.value)
            bottom = self.rect.bottom
            top = knob_y
            if top < bottom:
                pygame.draw.rect(
                    surface,
                    active_color,
                    pygame.Rect(cx - self.track_height // 2, top, self.track_height, bottom - top),
                    border_radius=self.track_height // 2,
                )
            # Knob
            knob_center = (cx, knob_y)
            pygame.draw.circle(surface, active_color, knob_center, self.knob_radius)
            pygame.draw.circle(surface, (20, 20, 20), knob_center, self.knob_radius, width=2)
    # --- Helpers ---
    def _clamp_value(self, v):
        v = float(v)
        if v < self.min_value:
            return self.min_value
        if v > self.max_value:
            return self.max_value
        return v
    def _value_to_pos(self, v):
        # Map value -> pixel coordinate along the main axis depending on orientation
        if self.orientation == "horizontal":
            if self.max_value == self.min_value:
                return self.rect.x
            t = (v - self.min_value) / (self.max_value - self.min_value)
            return int(self.rect.x + t * self.rect.w)
        else:  # vertical (higher value -> higher up: smaller y)
            if self.max_value == self.min_value:
                return self.rect.y
            t = (v - self.min_value) / (self.max_value - self.min_value)
            return int(self.rect.bottom - t * self.rect.h)
    def _pos_to_value(self, pos):
        if self.orientation == "horizontal":
            x = pos[0]
            t = (x - self.rect.x) / max(1, self.rect.w)
            return self.min_value + t * (self.max_value - self.min_value)
        else:
            y = pos[1]
            t = (self.rect.bottom - y) / max(1, self.rect.h)
            return self.min_value + t * (self.max_value - self.min_value)
    def _update_value_from_pos(self, mouse_pos, fire=False):
        v = self._clamp_value(self._pos_to_value(mouse_pos))
        if v != self.value:
            self.value = v
            if fire and self.on_change is not None:
                self.on_change(self.value)
    def _knob_rect(self):
        if self.orientation == "horizontal":
            cx = self._value_to_pos(self.value)
            cy = self.rect.centery
        else:
            cx = self.rect.centerx
            cy = self._value_to_pos(self.value)
        r = self.knob_radius
        return pygame.Rect(cx - r, cy - r, r * 2, r * 2)
# -------------------------------
# Toggle Switch (on/off)
# -------------------------------
class ToggleSwitch(ControlBase):
    def __init__(self, x, y, w, h, color="seagreen", value=False, on_change=None, label=None, font=None, text_color=(240, 240, 240), label_margin=8):
        super().__init__(color=color)
        self.rect = pygame.Rect(x, y, w, h)
        self.value = bool(value)
        self.on_change = on_change
        self.label = label
        default_size = max(12, int(h * 0.6))
        self.font = font or pygame.font.SysFont(None, default_size)
        self.text_color = text_color
        self.label_margin = label_margin
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.pressed and self.rect.collidepoint(event.pos):
                self.value = not self.value
                if self.on_change is not None:
                    self.on_change(self.value)
            self.pressed = False
        elif event.type == pygame.MOUSEMOTION:
            self.hovering = self.rect.collidepoint(event.pos)
    def draw(self, surface):
        # Track color: active uses state color; inactive uses gray
        if self.value:
            track_color = self._state_color()
        else:
            track_color = (100, 100, 100)
        # Track
        pygame.draw.rect(surface, track_color, self.rect, border_radius=self.rect.h // 2)
        # Knob position
        r = self.rect.h // 2 - 2
        if self.value:
            knob_center = (self.rect.right - r - 2, self.rect.centery)
        else:
            knob_center = (self.rect.left + r + 2, self.rect.centery)
        pygame.draw.circle(surface, (240, 240, 240), knob_center, r)
        pygame.draw.circle(surface, (40, 40, 40), knob_center, r, width=2)
        # Optional label to the left of the switch
        if self.label is not None:
            text_surf = self.font.render(self.label, True, self.text_color)
            text_rect = text_surf.get_rect()
            text_rect.midright = (self.rect.left - self.label_margin, self.rect.centery)
            surface.blit(text_surf, text_rect)
# -------------------------------
# Display Box (read-only multi-line text)
# -------------------------------
class DisplayBox(ControlBase):
    """Displays a list of strings inside a box.
    - Accepts a list of text lines.
    - Draws a filled box with optional border.
    - Auto-sizes font down (never up) to make text fit within the box, constrained by max_font_size.
    - Left aligned with padding; vertically centered block.
    """
    def __init__(self, x, y, w, h, lines=None, bg_color=(32, 32, 32), text_color=(240, 240, 240), font=None, max_font_size=None, min_font_size=8, padding=8, line_spacing=2, border_color=(40, 40, 40), border_width=2):
        super().__init__(color="red")  # base color unused here; keep for consistency
        self.rect = pygame.Rect(x, y, w, h)
        self.bg_color = bg_color
        self.text_color = text_color
        self.border_color = border_color
        self.border_width = border_width
        self.padding = padding
        self.line_spacing = line_spacing
        self.min_font_size = int(min_font_size)
        self.max_font_size = int(max_font_size) if max_font_size is not None else None
        # If a concrete font is provided, we'll use it as-is and not auto-fit larger.
        self.font = font
        self.lines = lines[:] if isinstance(lines, list) else []
        self._computed_font = None
        self._computed_size = None
        self._dirty = True  # recalc needed
    def set_lines(self, lines):
        self.lines = lines[:] if isinstance(lines, list) else []
        self._dirty = True
    def set_bg_color(self, color):
        self.bg_color = color
    def set_text_color(self, color):
        self.text_color = color
    def _measure_lines(self, font):
        widths = []
        heights = []
        for s in self.lines:
            surf = font.render(s, True, self.text_color)
            widths.append(surf.get_width())
            heights.append(surf.get_height())
        max_w = max(widths) if widths else 0
        line_h = max(heights) if heights else (font.get_height() if font else 0)
        total_h = 0
        if heights:
            total_h = sum(heights) + self.line_spacing * max(0, len(heights) - 1)
        return max_w, line_h, total_h
    def _ensure_font(self):
        # If a font was explicitly provided, use it and don't change it.
        if self.font is not None:
            self._computed_font = self.font
            self._computed_size = self.font.get_height()
            self._dirty = False
            return
        if not self._dirty and self._computed_font is not None:
            return
        # Determine a starting size: if max_font_size is provided, start there; else estimate based on height & lines
        if self.max_font_size is not None:
            size = int(self.max_font_size)
        else:
            # heuristic: if we have N lines, target about (available_height / N) * 0.9
            content_h = max(1, self.rect.h - 2 * self.padding)
            n = max(1, len(self.lines))
            size = int((content_h / n) * 0.9)
            size = max(size, 12)
        size = max(self.min_font_size, size)
        # Shrink-to-fit loop
        avail_w = max(1, self.rect.w - 2 * self.padding)
        avail_h = max(1, self.rect.h - 2 * self.padding)
        while size >= self.min_font_size:
            test_font = pygame.font.SysFont(None, size)
            max_w, line_h, total_h = self._measure_lines(test_font)
            if max_w <= avail_w and total_h <= avail_h:
                self._computed_font = test_font
                self._computed_size = size
                self._dirty = False
                return
            size -= 1
        # Fallback to min size even if it doesn't fit completely
        self._computed_font = pygame.font.SysFont(None, self.min_font_size)
        self._computed_size = self.min_font_size
        self._dirty = False
    def draw(self, surface):
        # Box background and border
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=6)
        if self.border_width > 0:
            pygame.draw.rect(surface, self.border_color, self.rect, width=self.border_width, border_radius=6)
        # Compute font to fit current content
        self._ensure_font()
        font = self._computed_font
        # Measure total content height for vertical centering
        max_w, line_h, total_h = self._measure_lines(font)
        content_h = total_h
        start_y = self.rect.centery - content_h // 2
        y = start_y
        x = self.rect.left + self.padding
        # Render each line left-aligned; clip is naturally handled by pygame if it overflows
        for s in self.lines:
            surf = font.render(s, True, self.text_color)
            surf_rect = surf.get_rect()
            surf_rect.topleft = (x, y)
            surface.blit(surf, surf_rect)
            y += surf.get_height() + self.line_spacing
# -------------------------------
# Text Input (labeled)
# -------------------------------
class TextInput(ControlBase):
    def __init__(self, x, y, w, h, color="royalblue", label=None, font=None, text_color=(240, 240, 240), box_text_color=(20, 20, 20), placeholder=None, on_submit=None, label_margin=8, max_length=64, clear_on_submit=True):
        super().__init__(color=color)
        # The input box area
        self.rect = pygame.Rect(x, y, w, h)
        self.on_submit = on_submit
        self.text = ""
        self.placeholder = placeholder
        self.active = False
        self.max_length = max_length
        self.clear_on_submit = clear_on_submit
        # Label settings (to the left of the box)
        self.label = label
        default_size = max(12, int(h * 0.6))
        self.font = font or pygame.font.SysFont(None, default_size)
        self.text_color = text_color
        self.box_text_color = box_text_color
        self.label_margin = label_margin
    def set_text(self, s):
        self.text = s or ""
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            if self.active:
                self.pressed = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.pressed = False
        elif event.type == pygame.MOUSEMOTION:
            self.hovering = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                if self.on_submit is not None:
                    self.on_submit(self.text)
                    if self.clear_on_submit:
                        self.text = ""
                # keep focus but you could set active=False if desired
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_ESCAPE:
                self.active = False
            else:
                # Append typed character if within max length
                if event.unicode and len(self.text) < self.max_length:
                    self.text += event.unicode
    def draw(self, surface):
        # Optional label to the left: "Label: |input|"
        if self.label is not None:
            label_surf = self.font.render(self.label + ":", True, self.text_color)
            label_rect = label_surf.get_rect()
            label_rect.midright = (self.rect.left - self.label_margin, self.rect.centery)
            surface.blit(label_surf, label_rect)
        # Box background color reacts to state
        if self.active:
            box_color = self._state_color(hovering=True, pressed=self.pressed)
        elif self.hovering:
            box_color = self._state_color(hovering=True, pressed=False)
        else:
            box_color = self.base
        pygame.draw.rect(surface, box_color, self.rect, border_radius=6)
        pygame.draw.rect(surface, (40, 40, 40), self.rect, width=2, border_radius=6)
        # Text (or placeholder)
        display_text = self.text
        text_color = self.box_text_color
        if not self.active and self.text == "" and self.placeholder is not None:
            display_text = self.placeholder
            text_color = (120, 120, 120)
        text_surf = self.font.render(display_text, True, text_color)
        text_rect = text_surf.get_rect()
        text_rect.midleft = (self.rect.left + 8, self.rect.centery)
        surface.blit(text_surf, text_rect)
        # Caret (simple: show when active, at end of text)
        if self.active:
            caret_x = text_rect.right + 2
            caret_y1 = self.rect.top + 6
            caret_y2 = self.rect.bottom - 6
            pygame.draw.line(surface, (20, 20, 20), (caret_x, caret_y1), (caret_x, caret_y2), 2)
__all__ = [
    "ControlBase",
    "Button",
    "RadioGroup",
    "RadioButton",
    "Slider",
    "ToggleSwitch",
    "DisplayBox",
    "TextInput",
]
