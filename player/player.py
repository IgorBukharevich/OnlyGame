import os
from dotenv import load_dotenv

load_dotenv()

# COLOURS
colours = {
    "0": (255, 255, 0),
    "1": (255, 0, 0),
    "2": (0, 255, 0),
    "3": (0, 255, 255),
    "4": (128, 0, 128)
}


class Player:
    def __init__(self, conn, addr, x, y, size, colours):
        self.conn = conn
        self.addr = addr
        self.name = "Mob"
        self.x = x
        self.y = y
        self.size = size
        self.colour = colours

        # parameters games window
        self.L = 1  # player scale proportions
        self.width_window = int(os.getenv("WIN_WIDTH"))
        self.height_window = int(os.getenv("WIN_HEIGHT"))

        # width and height game-map
        self.WIDTH_MAP = int(os.getenv("WIDTH_MAP"))
        self.HEIGHT_MAP = int(os.getenv("HEIGHT_MAP"))

        # field to view
        self.w_vision = int(os.getenv("WIN_WIDTH"))
        self.h_vision = int(os.getenv("WIN_HEIGHT"))

        self.ready = False
        # count errors
        self.errors = 0
        self.dead = 0
        # control speed
        self.abs_speed = 30 / (self.size ** 0.5)
        self.speed_x = 0
        self.speed_y = 0

    def set_options(self, data):
        data = data[1: -1].split(" ")
        self.name = data[0]
        # field to view
        self.width_window = int(data[1])
        self.height_window = int(data[2])

        # field to view
        self.w_vision = int(data[1])
        self.h_vision = int(data[2])
        print(self.name)

    def change_speed(self, vector):
        # speed calculation
        if (vector[0] == 0) and (vector[1] == 0):
            self.speed_x = 0
            self.speed_y = 0
        else:
            len_vector = (vector[0] ** 2 + vector[1] ** 2) ** 0.5
            vector = (vector[0] / len_vector, vector[1] / len_vector)
            vector = (vector[0] * self.abs_speed, vector[1] * self.abs_speed)
            self.speed_x, self.speed_y = vector[0], vector[1]

    def update(self):
        # x coordinate
        if self.x - self.size <= 0:
            if self.speed_x >= 0:
                self.x += self.speed_x
        else:
            if self.x + self.size >= self.WIDTH_MAP:
                if self.speed_x <= 0:
                    self.x += self.speed_x
            else:
                self.x += self.speed_x

        # y coordinate
        if self.y - self.size <= 0:
            if self.speed_y >= 0:
                self.y += self.speed_y
        else:
            if self.y + self.size >= self.HEIGHT_MAP:
                if self.speed_y <= 0:
                    self.y += self.speed_y
            else:
                self.y += self.speed_y

        # absolute player speed
        if self.size != 0:
            self.abs_speed = 30 / (self.size ** 0.5)
        else:
            self.abs_speed = 0
        # new size
        if self.size >= 100:
            self.size -= self.size / 20000

        # player scale proportions
        if (self.size >= self.w_vision / 4) or (
                self.size >= self.h_vision / 4):
            if (self.w_vision <= self.WIDTH_MAP) or (
                    self.h_vision <= self.HEIGHT_MAP):
                self.L *= 2
                self.w_vision = self.width_window * self.L
                self.h_vision = self.height_window * self.L

        if (self.size <= self.w_vision / 8) and (
                self.size < self.h_vision / 8):
            if self.L > 1:
                self.L = self.L // 2
                self.w_vision = self.width_window * self.L
                self.h_vision = self.height_window * self.L
