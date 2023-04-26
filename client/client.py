import os
import socket
import pygame
from dotenv import load_dotenv
from player.player import colours

# initialization .env_file
load_dotenv()
# initialization pygame
pygame.init()


def find(s):
    """
    performs a search received from the server to the client
    @param s: the data that came to the client "Data"
    @return: res
    """
    start = None
    for i in range(len(s)):
        if s[i] == "<":
            start = i
        if s[i] == ">" and start != None:
            end = i
            res = s[start + 1: end]
            return res
    return ""


class GameClient:
    def __init__(self):
        self.my_name = str(os.getenv("PLAYER_NAME"))
        self.pl_size = 50
        self.pl_color = None
        self.data = None
        self.vector = (0, 0)
        self.old_message = (0, 0)
        self.screen = None
        self.pl_sock = None
        self.serv_HOST = os.getenv("HOST")
        self.serv_PORT = int(os.getenv("PORT"))
        self.WIN_WIDTH = int(os.getenv("WIN_WIDTH"))
        self.WIN_HEIGHT = int(os.getenv("WIN_HEIGHT"))
        self.GRID_COLOR = (150, 150, 150)

    def create_pl_sock(self):
        # creating a client socket
        self.pl_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.pl_sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.pl_sock.connect((self.serv_HOST, self.serv_PORT))

    def read_mouse_pos(self):
        # reading the vector, the desired direction of movement
        if pygame.mouse.get_focused():
            pos = pygame.mouse.get_pos()
            self.vector = (
                pos[0] - self.WIN_WIDTH // 2,
                pos[1] - self.WIN_HEIGHT // 2
            )
            if self.vector[0] ** 2 + self.vector[1] ** 2 <= 50 ** 2:
                self.vector = (0, 0)

    def send_pl_command(self):
        # we send the vector of the desired direction of movement, if it has
        # changed
        if self.vector != self.old_message:
            self.old_message = self.vector
            message = "<" + str(self.vector[0]) + "," + str(
                self.vector[1]) + ">"
            self.pl_sock.send(message.encode())

    def response_nst_game_map(self):
        # response from the server about the new map state
        self.data = self.pl_sock.recv(2048)
        self.data = self.data.decode()
        self.data = find(self.data)
        self.data = self.data.split(",")
        if self.data[0].isdigit():
            self.pl_size = int(self.data[0])
        self.data = self.data[1:]

    def create_window(self):
        # create window Client
        self.screen = pygame.display.set_mode(
            (self.WIN_WIDTH, self.WIN_HEIGHT))
        pygame.display.set_caption("PlanetWars")

    def draw_nst_game_map(self):
        # displaying the new map state
        self.screen.fill("black")

        if self.data != [""]:
            self.draw_opponents()

        pygame.draw.circle(
            self.screen,
            colours[self.pl_color],
            (self.WIN_WIDTH // 2, self.WIN_HEIGHT // 2),
            self.pl_size,
        )
        pygame.display.update()

    def event_handling(self) -> bool:
        # processing of window closing events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

    def draw_opponents(self):
        # displaying opponents on the client window
        for i in range(len(self.data)):
            j = self.data[i].split(" ")

            x = self.WIN_WIDTH // 2 + int(j[0])
            y = self.WIN_HEIGHT // 2 + int(j[1])
            r = int(j[2])
            c = colours[j[3]]
            pygame.draw.circle(
                self.screen,
                c,
                (x, y),
                r
            )
            if len(j) == 5:
                self.write_name(x, y, r, j[4])

    def send_resp_serv_cli(self):
        # sending primary data from the client to the server
        self.pl_sock.send(("." + str(self.my_name) + " " + str(
            self.WIN_WIDTH) + " " + str(self.WIN_HEIGHT) + ".").encode())
        color = self.pl_sock.recv(64).decode()
        self.pl_color = color[3]
        self.pl_sock.send("!".encode())

    def write_name(self, x, y, size, name):
        # displaying names on objects
        font = pygame.font.Font(None, size)
        text = font.render(name, True, (255, 255, 255))
        rect = text.get_rect(center=(x, y))
        self.screen.blit(text, rect)

    def draw(self):
        # displaying names on objects
        if self.pl_size != 0:
            pygame.draw.circle(
                self.screen,
                colours[self.pl_color],
                (self.WIN_WIDTH // 2, self.WIN_HEIGHT),
                self.pl_size
            )
            self.write_name(
                self.WIN_WIDTH // 2,
                self.WIN_HEIGHT,
                self.pl_size,
                self.my_name
            )
