

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




    

if __name__ == "__main__":
    window = tk.Tk()
    Fireworks(window)
    window.mainloop()
