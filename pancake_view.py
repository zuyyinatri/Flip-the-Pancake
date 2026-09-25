import math
import pygame
import settings as cfg
from ui import draw_text, lerp_color

def _smoothstep(t):
    return t * t * (3 - 2 * t)

class StackView:
    def __init__(self, center_x, base_y, max_width=380, min_width=70, stack_height=330, max_spacing=54):
        self.center_x = center_x
        self.base_y = base_y
        self.max_width = max_width
        self.min_width = min_width
        self.stack_height = stack_height
        self.max_spacing = max_spacing

        self.stack = []
        self.spacing = max_spacing
        self.anims = {}

    def slot_y(self, index):
        n = len(self.stack)
        return self.base_y - (n - 1 - index) * self.spacing

    def width_of(self, value):
        n = len(self.stack)
        return self.min_width + (self.max_width - self.min_width) * value / n

    def index_at(self, pos):
        x, y = pos
        if not self.stack or abs(x - self.center_x) > self.max_width / 2 + 20:
            return None
        for i in range(len(self.stack)):
            if abs(y - self.slot_y(i)) <= self.spacing / 2:
                return i
        return None

    def set_stack(self, stack, animate=True):
        self.stack = list(stack)
        n = len(self.stack)
        if n == 0:
            self.anims = {}
            return
        self.spacing = min(self.max_spacing, self.stack_height / n)

        if not animate or set(self.anims) != set(self.stack):
            self.anims = {}

        for i, value in enumerate(self.stack):
            target = self.slot_y(i)
            anim = self.anims.get(value)
            if anim is None:
                self.anims[value] = {"y": target, "start": target, "target": target,
                                     "t": 1.0, "moving": False}
            else:
                anim["start"] = anim["y"]
                anim["target"] = target
                anim["t"] = 0.0
                anim["moving"] = abs(anim["y"] - target) > 1

    @property
    def is_animating(self):
        return any(a["t"] < 1.0 for a in self.anims.values())

    def update(self, dt):
        for a in self.anims.values():
            if a["t"] < 1.0:
                a["t"] = min(1.0, a["t"] + dt / cfg.FLIP_DURATION)
                eased = _smoothstep(a["t"])
                a["y"] = a["start"] + (a["target"] - a["start"]) * eased

    def draw(self, surface, hover_index=None):
        if not self.stack:
            return
        self._draw_plate(surface)

        n = len(self.stack)
        index_of = {value: i for i, value in enumerate(self.stack)}
        height = min(self.spacing * 0.92, 58)

        for value, a in sorted(self.anims.items(), key=lambda item: -item[1]["y"]):
            t = (value - 1) / (n - 1) if n > 1 else 0
            color = lerp_color(cfg.PANCAKE_LIGHT, cfg.PANCAKE_DARK, t)
            highlighted = hover_index is not None and index_of[value] <= hover_index
            if highlighted:
                color = lerp_color(color, (255, 255, 255), 0.35)

            arc = math.sin(math.pi * a["t"]) * cfg.FLIP_ARC if a["moving"] else 0
            self._draw_pancake(surface, self.center_x + arc, a["y"],
                               self.width_of(value), height, value, color, highlighted)

    def _draw_plate(self, surface):
        cx = self.center_x
        cy = self.base_y + self.spacing * 0.55 + 8
        w = self.max_width + 80
        for rect_args, color in (
            ((w, 46, cx, cy + 10), cfg.PLATE_SHADOW),
            ((w, 40, cx, cy), cfg.PLATE),
            ((w * 0.78, 26, cx, cy - 2), cfg.PLATE_INNER),
        ):
            width, height, x, y = rect_args
            rect = pygame.Rect(0, 0, int(width), int(height))
            rect.center = (int(x), int(y))
            pygame.draw.ellipse(surface, color, rect)

    def _draw_pancake(self, surface, cx, cy, width, height, value, color, highlighted):
        top = pygame.Rect(0, 0, int(width), int(height))
        top.center = (int(cx), int(cy))

        side = top.move(0, int(height * 0.2))
        pygame.draw.ellipse(surface, lerp_color(color, (0, 0, 0), 0.28), side)

        pygame.draw.ellipse(surface, color, top)
        inner = top.inflate(-int(width * 0.16), -int(height * 0.38))
        inner.center = (int(cx), int(cy - height * 0.04))
        pygame.draw.ellipse(surface, lerp_color(color, (255, 255, 255), 0.18), inner)

        if highlighted:
            pygame.draw.ellipse(surface, cfg.HIGHLIGHT, top, 4)
        else:
            pygame.draw.ellipse(surface, cfg.PANCAKE_OUTLINE, top, 2)

        draw_text(surface, str(value), int(height * 0.68), cfg.PANCAKE_TEXT,
                  center=(int(cx), int(cy)))
