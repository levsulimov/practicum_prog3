
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




   

if __name__ == "__main__":
    window = tk.Tk()
    Starfield(window)
    window.mainloop()
