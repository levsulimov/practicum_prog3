

import colorsys
import math
import random
import time
import tkinter as tk
from dataclasses import dataclass, field


def fade_color(color, opacity):
    opacity = max(0.0, min(1.0, opacity))
    return "#{:02x}{:02x}{:02x}".format(
        *(round(channel * opacity) for channel in color))


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    lifetime: float
    color: tuple
    size: float
    opacity: float
    item: int
    trail_item: int
    age: float = 0.0
    trail: list = field(default_factory=list)

    def advance(self, dt, gravity):
        self.age += dt
        self.x += self.vx * dt
        self.y += self.vy * dt + gravity * dt * dt / 2
        self.vy += gravity * dt
        self.trail.append((self.x, self.y))
        self.trail = self.trail[-8:]
        return self.age < self.lifetime


@dataclass
class Rocket:
    x: float
    y: float
    target_y: float
    speed: float
    color: tuple
    item: int
    age: float = 0.0


class Fireworks:
    COLORS = 12
    MAX_PARTICLES = 1800
    MAX_ROCKETS = 12

    def __init__(self, root):
        self.root = root
        root.title("Лабораторная работа 3.2 — Фейерверки")
        root.geometry("1000x720")
        root.minsize(640, 480)
        self.gravity = tk.DoubleVar(value=100.0)
        self.paused = False
        self.rockets = []
        self.particles = []
        self.width, self.height = 1000, 600
        self.spawn_in = 0.2

        controls = tk.Frame(root, padx=10, pady=5)
        controls.pack(fill="x")
        tk.Label(controls, text="Гравитация (пикс./с²):").pack(side="left")
        tk.Scale(controls, from_=-150, to=350, resolution=10,
                 orient="horizontal", variable=self.gravity,
                 length=260).pack(side="left")
        self.pause_button = tk.Button(controls, text="Пауза", command=self.toggle_pause)
        self.pause_button.pack(side="left", padx=10)
        tk.Button(controls, text="Сброс", command=self.reset).pack(side="left")
        tk.Label(root, text="Щелчок по небу — взрыв • Пробел — пауза • "
                 "R — сброс • Esc — выход").pack(fill="x")
        self.canvas = tk.Canvas(root, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.status = tk.Label(root, anchor="w")
        self.status.pack(fill="x", padx=10)

        self.canvas.bind("<Configure>", self.resize)
        self.canvas.bind("<Button-1>", self.click)
        root.bind("<space>", self.toggle_pause)
        root.bind("<KeyPress-r>", self.reset)
        root.bind("<KeyPress-R>", self.reset)
        root.bind("<Escape>", lambda event: root.destroy())
        self.last_time = time.perf_counter()
        self.after_id = None
        root.protocol("WM_DELETE_WINDOW", self.close)
        self.animate()

    def resize(self, event):
        self.width, self.height = event.width, event.height

    def random_color(self):
        hue = random.randrange(self.COLORS) / self.COLORS
        return tuple(round(c * 255) for c in colorsys.hsv_to_rgb(hue, 0.75, 1.0))

    def launch(self):
        if len(self.rockets) >= self.MAX_ROCKETS:
            return
        x = random.uniform(self.width * 0.1, self.width * 0.9)
        color = self.random_color()
        item = self.canvas.create_line(x, self.height, x, self.height + 15,
                                       fill=fade_color(color, 1), width=2)
        self.rockets.append(Rocket(
            x, self.height, random.uniform(self.height * 0.12, self.height * 0.6),
            random.uniform(280, 430), color, item))

    def explode(self, x, y, color=None):
        color = color if color is not None else self.random_color()
        count = min(random.randint(65, 100), self.MAX_PARTICLES - len(self.particles))
        for _ in range(count):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(45, 220)
            size = random.uniform(1.2, 3.0)
            trail_item = self.canvas.create_line(x, y, x, y, width=1)
            item = self.canvas.create_oval(x, y, x, y, outline="")
            self.particles.append(Particle(
                x, y, math.cos(angle) * speed, math.sin(angle) * speed,
                random.uniform(1.4, 3.0), color, size,
                random.uniform(0.65, 1.0), item, trail_item))

    def click(self, event):
        self.canvas.focus_set()
        if not self.paused:
            self.explode(event.x, event.y)

    def toggle_pause(self, event=None):
        self.paused = not self.paused
        self.pause_button.configure(text="Продолжить" if self.paused else "Пауза")
        return "break"

    def reset(self, event=None):
        self.canvas.delete("all")
        self.rockets.clear()
        self.particles.clear()
        self.gravity.set(100)
        self.paused = False
        self.pause_button.configure(text="Пауза")
        self.spawn_in = 0.2
        self.last_time = time.perf_counter()
        return "break"

    def update_scene(self, dt):
        self.spawn_in -= dt
        if self.spawn_in <= 0:
            self.launch()
            self.spawn_in = random.uniform(0.35, 0.85)

        living_rockets = []
        for rocket in self.rockets:
            rocket.age += dt
            rocket.y -= rocket.speed * dt
            if rocket.y <= rocket.target_y or rocket.age >= 3.0:
                self.canvas.delete(rocket.item)
                self.explode(rocket.x, rocket.y, rocket.color)
            else:
                self.canvas.coords(rocket.item, rocket.x, rocket.y,
                                   rocket.x, rocket.y + 18)
                living_rockets.append(rocket)
        self.rockets = living_rockets

        living_particles = []
        gravity = self.gravity.get()
        for particle in self.particles:
            if not particle.advance(dt, gravity):
                self.canvas.delete(particle.item, particle.trail_item)
                continue
            remaining = 1 - particle.age / particle.lifetime
            alpha = particle.opacity * remaining ** 1.4
            radius = particle.size * (0.4 + 0.6 * remaining)
            self.canvas.coords(particle.item,
                               particle.x - radius, particle.y - radius,
                               particle.x + radius, particle.y + radius)
            self.canvas.itemconfigure(particle.item, fill=fade_color(particle.color, alpha))
            if len(particle.trail) > 1:
                points = [value for point in particle.trail for value in point]
                self.canvas.coords(particle.trail_item, *points)
                self.canvas.itemconfigure(particle.trail_item,
                                          fill=fade_color(particle.color, alpha * 0.35))
            living_particles.append(particle)
        self.particles = living_particles

    def animate(self):
        now = time.perf_counter()
        dt = min(now - self.last_time, 0.05)
        self.last_time = now
        if not self.paused:
            self.update_scene(dt)
        mode = "Пауза" if self.paused else "Анимация"
        self.status.configure(text=f"{mode} | Ракет: {len(self.rockets)} | "
                              f"Частиц: {len(self.particles)} | "
                              f"Гравитация: {self.gravity.get():.0f} пикс./с²")
        self.after_id = self.root.after(16, self.animate)

    def close(self):
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
        self.root.destroy()


if __name__ == "__main__":
    window = tk.Tk()
    Fireworks(window)
    window.mainloop()
