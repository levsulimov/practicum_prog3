
import math
import random
import time
import tkinter as tk
from dataclasses import dataclass


@dataclass
class Star:
    item: int
    x: float
    y: float
    z: float
    size: float
    color: tuple


class Starfield:
    STAR_COUNT = 650
    FAR = 1800.0
    NEAR = 15.0
    COLORS = ((255, 255, 255), (190, 215, 255),
              (255, 225, 170), (255, 185, 160))

    def __init__(self, root):
        self.root = root
        root.title("Звёздное поле")
        root.geometry("1000x700")
        root.minsize(400, 300)
        self.canvas = tk.Canvas(root, background="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.width, self.height = 1000, 700
        self.focal = 600.0
        self.speed = 350.0
        self.keys = set()
        self.target_x = self.target_y = 0.0
        self.heading_x = self.heading_y = 0.0
        self.stars = []
        for _ in range(self.STAR_COUNT):
            star = Star(self.canvas.create_oval(0, 0, 0, 0, outline=""),
                        0, 0, 0, 0, (255, 255, 255))
            self.reset_star(star, initial=True)
            self.stars.append(star)
        self.hud = self.canvas.create_text(
            16, 16, anchor="nw", fill="#b6c5da", font=("Arial", 12))
        self.canvas.bind("<Configure>", self.resize)
        self.canvas.bind("<Motion>", self.mouse_move)
        self.canvas.bind("<Leave>", self.center_direction)
        root.bind("<KeyPress>", self.key_down)
        root.bind("<KeyRelease>", self.key_up)
        root.bind("<FocusOut>", lambda event: self.keys.clear())
        root.bind("<Escape>", lambda event: root.destroy())
        self.last_time = time.perf_counter()
        self.animate()

    def reset_star(self, star, initial=False):
        # Выбираем положение на экране и переводим его в координаты 3D.
        star.z = random.uniform(self.NEAR, self.FAR) if initial else self.FAR
        star.x = random.uniform(-self.width / 2, self.width / 2) * star.z / self.focal
        star.y = random.uniform(-self.height / 2, self.height / 2) * star.z / self.focal
        star.size = random.uniform(0.8, 2.8)
        star.color = random.choice(self.COLORS)

    def resize(self, event):
        self.width, self.height = event.width, event.height
        self.focal = max(200.0, min(self.width, self.height) * 0.85)

    def mouse_move(self, event):
        # Направление полёта задаётся лучом из камеры к указателю мыши.
        self.target_x = (event.x - self.width / 2) / self.focal
        self.target_y = (event.y - self.height / 2) / self.focal

    def center_direction(self, event):
        self.target_x = self.target_y = 0.0

    def key_down(self, event):
        self.keys.add(event.keysym.lower())

    def key_up(self, event):
        self.keys.discard(event.keysym.lower())

    def animate(self):
        now = time.perf_counter()
        dt = min(now - self.last_time, 0.05)
        self.last_time = now
        faster = bool(self.keys & {"up", "w"})
        slower = bool(self.keys & {"down", "s"})
        self.speed = max(0.0, min(2000.0, self.speed + (faster - slower) * 500 * dt))

        # Плавное изменение направления; скорость не зависит от частоты кадров.
        smoothing = 1 - math.exp(-5 * dt)
        self.heading_x += (self.target_x - self.heading_x) * smoothing
        self.heading_y += (self.target_y - self.heading_y) * smoothing
        distance = self.speed * dt / math.sqrt(
            1 + self.heading_x ** 2 + self.heading_y ** 2)

        for star in self.stars:
            star.x -= self.heading_x * distance
            star.y -= self.heading_y * distance
            star.z -= distance
            if star.z <= self.NEAR:
                self.reset_star(star)

            # Перспективная проекция: чем ближе звезда, тем она крупнее.
            scale = self.focal / star.z
            x = self.width / 2 + star.x * scale
            y = self.height / 2 + star.y * scale
            radius = min(12.0, max(0.5, star.size * scale))
            if not (-radius <= x <= self.width + radius
                    and -radius <= y <= self.height + radius):
                self.reset_star(star)
                scale = self.focal / star.z
                x = self.width / 2 + star.x * scale
                y = self.height / 2 + star.y * scale
                radius = min(12.0, max(0.5, star.size * scale))

            brightness = 0.35 + 0.65 * (1 - star.z / self.FAR)
            color = "#{:02x}{:02x}{:02x}".format(
                *(int(channel * brightness) for channel in star.color))
            self.canvas.coords(star.item, x - radius, y - radius, x + radius, y + radius)
            self.canvas.itemconfigure(star.item, fill=color)

        self.canvas.itemconfigure(
            self.hud, text=f"Скорость: {self.speed:.0f}\n"
            "↑ / ↓ или W / S — скорость\nМышь — направление полёта\nEsc — выход")
        self.canvas.tag_raise(self.hud)
        self.root.after(16, self.animate)


if __name__ == "__main__":
    window = tk.Tk()
    Starfield(window)
    window.mainloop()
