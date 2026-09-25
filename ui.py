import random
import pygame
import settings as cfg

_fonts = {}

def get_font(size):
    if size not in _fonts:
        _fonts[size] = pygame.font.Font(None, size)
    return _fonts[size]

def draw_text(surface, text, size, color, **anchor):
    image = get_font(size).render(text, True, color)
    rect = image.get_rect(**anchor)
    surface.blit(image, rect)
    return rect

def lerp_color(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def format_time(seconds):
    seconds = int(seconds)
    return f"{seconds // 60:02d}:{seconds % 60:02d}"

def draw_overlay(surface, alpha=150):
    overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    overlay.fill((40, 25, 10, alpha))
    surface.blit(overlay, (0, 0))

def draw_panel(surface, rect):
    pygame.draw.rect(surface, cfg.PANEL_BORDER, rect.move(0, 6), border_radius=22)
    pygame.draw.rect(surface, cfg.PANEL, rect, border_radius=22)
    pygame.draw.rect(surface, cfg.PANEL_BORDER, rect, width=4, border_radius=22)

class Button:
    def __init__(self, text, rect, size=36):
        self.text = text
        self.rect = pygame.Rect(rect)
        self.size = size

    def hit(self, pos):
        return self.rect.collidepoint(pos)

    def draw(self, surface):
        hovered = self.rect.collidepoint(pygame.mouse.get_pos())
        color = cfg.BUTTON_HOVER if hovered else cfg.BUTTON
        pygame.draw.rect(surface, cfg.BUTTON_SHADOW, self.rect.move(0, 5), border_radius=14)
        pygame.draw.rect(surface, color, self.rect, border_radius=14)
        pygame.draw.rect(surface, cfg.BUTTON_SHADOW, self.rect, width=3, border_radius=14)
        draw_text(surface, self.text, self.size, cfg.BUTTON_TEXT, center=self.rect.center)

class Confetti:
    def __init__(self):
        self.particles = []

    def burst(self, count=100):
        for _ in range(count):
            self.particles.append({
                "x": random.uniform(0, cfg.SCREEN_WIDTH),
                "y": random.uniform(-300, -10),
                "vx": random.uniform(-40, 40),
                "vy": random.uniform(80, 260),
                "size": random.randint(6, 11),
                "color": random.choice(cfg.CONFETTI_COLORS),
            })

    def update(self, dt):
        for p in self.particles:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
        self.particles = [p for p in self.particles if p["y"] < cfg.SCREEN_HEIGHT + 20]

    def draw(self, surface):
        for p in self.particles:
            pygame.draw.rect(surface, p["color"], (int(p["x"]), int(p["y"]), p["size"], p["size"] + 3))

    def clear(self):
        self.particles.clear()
