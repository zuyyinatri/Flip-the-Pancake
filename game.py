import math
import random
from enum import Enum, auto
import pygame

import settings as cfg
from pancake_view import StackView
from puzzle import create_level, flip, is_sorted
from ui import (Button, Confetti, draw_overlay, draw_panel, draw_text, lerp_color)

W, H = cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT

HOW_TO_PLAY_LINES = [
    ("GOAL", True),
    ("Sort the pancakes: smallest on top, biggest at the bottom.", False),
    ("", False),
    ("HOW TO FLIP", True),
    ("Click a pancake. It and every pancake above it get flipped.", False),
    ("Example: [3, 1, 5, 2, 4] -> click the 3rd pancake -> [5, 1, 3, 2, 4]", False),
    ("", False),
    ("LIMITS", True),
    ("Every flip uses one of your limited flips. Run out and you lose.", False),
    ("Higher levels add more pancakes and give you fewer spare flips.", False),
    ("", False),
    ("CONTROLS", True),
    ("Mouse click: flip     R: restart level     ESC: back to menu", False),
]

class State(Enum):
    MENU = auto()
    HOW_TO_PLAY = auto()
    GAMEPLAY = auto()
    LEVEL_COMPLETE = auto()
    GAME_OVER = auto()
    VICTORY = auto()

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(cfg.TITLE)
        self.screen = pygame.display.set_mode((W, H))
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = State.MENU

        self.level = None
        self.stack = []
        self.flips_used = 0
        self.pending = None
        self.pending_delay = 0.0

        self.view = StackView(center_x=W // 2, base_y=470)
        self.menu_view = StackView(center_x=690, base_y=430, max_width=300,
                                   min_width=80, stack_height=280, max_spacing=48)
        self.menu_view.set_stack([3, 1, 5, 2, 4], animate=False)
        self.menu_timer = 0.0
        self.confetti = Confetti()

        self._build_buttons()

    def _build_buttons(self):
        to_menu = lambda: self.set_state(State.MENU)
        left, right = (215, 440, 230, 56), (455, 440, 230, 56)

        self.buttons = {
            State.MENU: [
                (Button("Play", (60, 290, 260, 60)), self.start_new_game),
                (Button("How to Play", (60, 370, 260, 60)),
                 lambda: self.set_state(State.HOW_TO_PLAY)),
                (Button("Exit", (60, 450, 260, 60)), self.quit),
            ],
            State.HOW_TO_PLAY: [
                (Button("Back", (W // 2 - 100, 545, 200, 56)), to_menu),
            ],
            State.GAMEPLAY: [
                (Button("Restart", (W // 2 - 175, 572, 160, 48), 32), self.restart_level),
                (Button("Menu", (W // 2 + 15, 572, 160, 48), 32), to_menu),
            ],
            State.LEVEL_COMPLETE: [
                (Button("Next Level", left), self.next_level),
                (Button("Menu", right), to_menu),
            ],
            State.GAME_OVER: [
                (Button("Try Again", left), self.retry_level),
                (Button("Menu", right), to_menu),
            ],
            State.VICTORY: [
                (Button("Play Again", left), self.start_new_game),
                (Button("Menu", right), to_menu),
            ],
        }

    def quit(self):
        self.running = False

    def set_state(self, state):
        self.state = state
        self.pending = None
        self.confetti.clear()
        if state == State.LEVEL_COMPLETE:
            self.confetti.burst(80)
        elif state == State.VICTORY:
            self.confetti.burst(220)

    def start_new_game(self):
        self.load_level(1)
        self.set_state(State.GAMEPLAY)

    def load_level(self, number):
        self.level = create_level(number)
        self.stack = list(self.level.stack)
        self.flips_used = 0
        self.view.set_stack(self.stack, animate=False)

    def next_level(self):
        self.load_level(self.level.number + 1)
        self.set_state(State.GAMEPLAY)

    def restart_level(self):
        if self.pending:
            return
        self.stack = list(self.level.stack)
        self.flips_used = 0
        self.view.set_stack(self.stack)

    def retry_level(self):
        self.restart_level()
        self.set_state(State.GAMEPLAY)

    def do_flip(self, k):
        if k < 2 or self.pending:
            return
        self.stack = flip(self.stack, k)
        self.flips_used += 1
        self.view.set_stack(self.stack)

        if is_sorted(self.stack):
            self.finish_level()
        elif self.flips_used >= self.level.max_flips:
            self.schedule(State.GAME_OVER)

    def finish_level(self):
        last = self.level.number >= cfg.MAX_LEVEL
        self.schedule(State.VICTORY if last else State.LEVEL_COMPLETE)

    def schedule(self, state):
        self.pending = state
        self.pending_delay = cfg.RESULT_DELAY

    def run(self):
        while self.running:
            dt = min(self.clock.tick(cfg.FPS) / 1000, 0.05)
            self.handle_events()
            self.update(dt)
            self.draw()
        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            elif event.type == pygame.KEYDOWN:
                self.on_key(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.on_click(event.pos)

    def on_key(self, key):
        if key == pygame.K_ESCAPE:
            if self.state != State.MENU:
                self.set_state(State.MENU)
        elif key == pygame.K_r:
            if self.state == State.GAMEPLAY:
                self.restart_level()
            elif self.state == State.GAME_OVER:
                self.retry_level()

    def on_click(self, pos):
        for button, action in self.buttons.get(self.state, []):
            if button.hit(pos):
                action()
                return

        if self.state == State.GAMEPLAY and not self.pending:
            index = self.view.index_at(pos)
            if index is not None:
                self.do_flip(index + 1)

    def update(self, dt):
        self.view.update(dt)
        self.confetti.update(dt)

        if self.state == State.MENU:
            self.menu_view.update(dt)
            self.menu_timer += dt
            if self.menu_timer > 1.5:
                self.menu_timer = 0.0
                demo = flip(self.menu_view.stack, random.randint(2, 5))
                self.menu_view.set_stack(demo)

        elif self.state == State.GAMEPLAY:
            if self.pending:
                self.pending_delay -= dt
                if self.pending_delay <= 0:
                    self.set_state(self.pending)

    def draw(self):
        self.screen.fill(cfg.BG)

        if self.state == State.MENU:
            self.draw_menu()
        elif self.state == State.HOW_TO_PLAY:
            self.draw_how_to_play()
        else:
            self.draw_gameplay()
            if self.state == State.LEVEL_COMPLETE:
                self.draw_level_complete()
            elif self.state == State.GAME_OVER:
                self.draw_game_over()
            elif self.state == State.VICTORY:
                self.draw_victory()

        self.confetti.draw(self.screen)
        pygame.display.flip()

    def draw_buttons(self):
        for button, _ in self.buttons[self.state]:
            button.draw(self.screen)

    def draw_menu(self):
        s = self.screen
        draw_text(s, "Flip the", 104, cfg.TEXT, topleft=(60, 60))
        draw_text(s, "Pancake", 104, cfg.ACCENT, topleft=(60, 140))
        draw_text(s, "Sort the stack. Flip smart.", 30, cfg.TEXT_LIGHT, topleft=(64, 225))
        self.menu_view.draw(s)
        self.draw_buttons()

    def draw_how_to_play(self):
        s = self.screen
        draw_text(s, "How to Play", 70, cfg.ACCENT, center=(W // 2, 60))
        y = 120
        for text, is_heading in HOW_TO_PLAY_LINES:
            if is_heading:
                draw_text(s, text, 34, cfg.ACCENT, topleft=(90, y))
                y += 32
            else:
                draw_text(s, text, 29, cfg.TEXT, topleft=(90, y))
                y += 28 if text else 8
        self.draw_buttons()

    def draw_gameplay(self):
        s = self.screen
        level = self.level
        remaining = level.max_flips - self.flips_used
        active = self.state == State.GAMEPLAY and not self.pending

        draw_text(s, "FLIP THE PANCAKE", 44, cfg.TEXT, center=(W // 2, 38))
        draw_text(s, f"Level: {level.number}", 38, cfg.TEXT, midleft=(60, 100))

        flips_color = cfg.TEXT
        if active and remaining <= cfg.WARNING_REMAINING:
            pulse = (math.sin(pygame.time.get_ticks() / 130) + 1) / 2
            flips_color = lerp_color(cfg.TEXT, cfg.WARNING, pulse)
        draw_text(s, f"Flips: {self.flips_used} / {level.max_flips}", 42, flips_color, center=(W // 2, 100))

        hover = None
        if active:
            index = self.view.index_at(pygame.mouse.get_pos())
            if index is not None and index >= 1:
                hover = index
        self.view.draw(s, hover)

        draw_text(s, "Click a pancake to flip it and everything above it", 26,
                  cfg.TEXT_LIGHT, center=(W // 2, 545))
        for button, _ in self.buttons[State.GAMEPLAY]:
            button.draw(s)

    def _result_panel(self, title, title_color, lines):
        draw_overlay(self.screen)
        panel = pygame.Rect(0, 0, 520, 340)
        panel.center = (W // 2, H // 2)
        draw_panel(self.screen, panel)

        draw_text(self.screen, title, 64, title_color, center=(panel.centerx, panel.top + 70))
        y = panel.top + 150
        for text, color in lines:
            draw_text(self.screen, text, 32, color, center=(panel.centerx, y))
            y += 40
        self.draw_buttons()

    def draw_level_complete(self):
        lines = [(f"Level {self.level.number} complete!", cfg.TEXT)]
        self._result_panel("Victory!", cfg.ACCENT, lines)

    def draw_game_over(self):
        level = self.level
        lines = [
            (f"Level {level.number}", cfg.TEXT),
            (f"You used all {level.max_flips} flips.", cfg.TEXT),
            ("Same puzzle - give it another try!", cfg.TEXT_LIGHT),
        ]
        self._result_panel("Game Over", cfg.WARNING, lines)

    def draw_victory(self):
        lines = [(f"You cleared all {cfg.MAX_LEVEL} levels!", cfg.TEXT)]
        self._result_panel("Victory!", cfg.GOLD, lines)
