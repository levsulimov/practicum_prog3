
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




    def reset_star(self, star, initial=False):
        
        star.z = random.uniform(self.NEAR, self.FAR) if initial else self.FAR
        star.x = random.uniform(-self.width / 2, self.width / 2) * star.z / self.focal
        star.y = random.uniform(-self.height / 2, self.height / 2) * star.z / self.focal
        star.size = random.uniform(0.8, 2.8)
        star.color = random.choice(self.COLORS)

    def resize(self, event):
        self.width, self.height = event.width, event.height
        self.focal = max(200.0, min(self.width, self.height) * 0.85)

    def mouse_move(self, event):
        
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
