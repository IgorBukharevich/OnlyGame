import os
import socket
import pygame
import random
from dotenv import load_dotenv
from player.player import Player, colours
from eat.eat import Eat

load_dotenv()

pygame.init()

COUNT_MOBS = 25


def new_size(SIZE, size):
    """
    changing the size when eating a player or mob
    @param SIZE: big player
    @param size: small player
    @return: new player or mob size
    """
    return (SIZE ** 2 + size ** 2) ** 0.5


def find(s):
    """
    search for the necessary objects that the server has received
    @param s: the data that came to the server "Data"
    @return: res
    """
    start = None
    for i in range(len(s)):
        if s[i] == "<":
            start = i
        if s[i] == ">" and start is not None:
            end = i
            res = s[start + 1: end]
            res = list(map(int, res.split(",")))
            return res
    return ""


class GameServer:
    START_PL_SIZE = 50

    def __init__(self):
        self.visible_enemy = None
        self.responses = None
        self.screen = None
        self.serv_sock = None
        self.HOST = os.getenv("HOST")
        self.PORT = int(os.getenv("PORT"))
        self.WIDTH_MAP = int(os.getenv("WIDTH_MAP"))
        self.HEIGHT_MAP = int(os.getenv("HEIGHT_MAP"))

        # map window parameters
        self.small_WIDTH = int(os.getenv("small_WIDTH"))
        self.small_HEIGHT = int(os.getenv("small_HEIGHT"))

        # create mob
        self.players = [
            Player(
                None, None,
                random.randint(0, self.WIDTH_MAP),
                random.randint(0, self.HEIGHT_MAP),
                random.randint(10, 100),
                str(random.randint(0, 4))
            )
            for i in range(COUNT_MOBS)
        ]

        # create eat
        self.SIZE_EAT = 15
        self.COUNT_EAT = (self.WIDTH_MAP * self.HEIGHT_MAP) // 80000
        self.eat = [
            Eat(
                random.randint(0, self.WIDTH_MAP),
                random.randint(0, self.HEIGHT_MAP),
                self.SIZE_EAT,
                str(random.randint(0, 4))
            )
            for i in range(self.COUNT_EAT)
        ]

    def create_serv_sock(self):
        # creates a server socket
        self.serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # disabling the Nagle algorithm
        self.serv_sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.serv_sock.bind((self.HOST, self.PORT))
        self.serv_sock.setblocking(False)
        self.serv_sock.listen(5)
        print("Created Socket!")

    def check_new_conn(self):
        # checking connected players
        try:
            player_sock, addr = self.serv_sock.accept()
            print("Connected: ", addr)
            player_sock.setblocking(False)
            spawn = random.choice(self.eat)
            new_players = Player(
                player_sock,
                addr,
                spawn.x,
                spawn.y,
                self.START_PL_SIZE,
                str(random.randint(0, 4))
            )
            self.players.append(new_players)
        except:
            pass
        # add eat
        for i in range(COUNT_MOBS - len(self.players)):
            if len(self.eat) != 0:
                spawn = random.choice(self.eat)
                self.players.append(
                    Player(
                        None, None,
                        spawn.x,
                        spawn.y,
                        random.randint(10, 100),
                        str(random.randint(0, 4))
                    )
                )
                self.eat.remove(spawn)

        # add list eat
        new_eat = [
            Eat(
                random.randint(0, self.WIDTH_MAP),
                random.randint(0, self.HEIGHT_MAP),
                self.SIZE_EAT,
                str(random.randint(0, 4))
            )
            for i in range(self.COUNT_EAT - len(self.eat))
        ]
        self.eat = self.eat + new_eat

    def read_pl_command(self, tick):
        # reads commands from players
        for player in self.players:
            if player.conn is not None:
                try:
                    data = player.conn.recv(2048)
                    data = data.decode()
                    if data[0] == "!":  # a message has arrived
                        player.ready = True
                    else:
                        # message has arrived name and size window
                        if data[0] == "." and data[-1] == ".":
                            player.set_options(data)
                            player.conn.send(
                                (
                                        str(self.START_PL_SIZE) +
                                        " " + player.colour).encode()
                            )
                        else:  # kursor
                            data = find(data)
                            player.change_speed(data)
                except:
                    pass
            else:
                if tick == 100:
                    tick = 0
                    # random move mob
                    data = [
                        random.randint(-100, 100),
                        random.randint(-100, 100)
                    ]
                    player.change_speed(data)

            player.update()

    def visible_players(self):
        # displaying visible objects and players on the map
        self.visible_enemy = [[] for i in range(len(self.players))]
        for i in range(len(self.players)):
            # what kind of food does he see
            for k in range(len(self.eat)):
                dist_x = self.eat[k].x - self.players[i].x
                dist_y = self.eat[k].y - self.players[i].y
                # i see k
                if (
                        (abs(dist_x) <= (self.players[i].w_vision) // 2 +
                         self.eat[k].size)
                        and
                        (abs(dist_y) <= (self.players[i].h_vision) // 2 +
                         self.eat[k].size)
                ):
                    # i can it eat k
                    if (dist_x ** 2 + dist_y ** 2) ** 0.5 <= self.players[
                        i].size:
                        # refresh size i players
                        self.players[i].size = new_size(
                            self.players[i].size,
                            self.eat[k].size
                        )
                        self.eat[k].size = 0

                    if (self.players[i].conn is not None) and (
                            self.eat[k].size != 0):
                        # add list visible i
                        x_ = str(round(dist_x / self.players[i].L))
                        y_ = str(round(dist_y / self.players[i].L))
                        r_ = str(round(self.eat[k].size / self.players[i].L))
                        c_ = self.eat[k].colour

                        self.visible_enemy[i].append(
                            x_ + " " + y_ + " " + r_ + " " + c_
                        )

            for j in range(i + 1, len(self.players)):
                # views couple i and j enemy
                dist_x = self.players[j].x - self.players[i].x
                dist_y = self.players[j].y - self.players[i].y

                # i see j
                if (
                        (abs(dist_x) <= (self.players[i].w_vision) // 2 +
                         self.players[j].size)
                        and
                        (abs(dist_y) <= (self.players[i].h_vision) // 2 +
                         self.players[j].size)

                ):
                    # i can it eat j
                    if ((dist_x ** 2 + dist_y ** 2) ** 0.5 <= self.players[
                        i].size and
                            self.players[i].size > 1.1 * self.players[j].size):
                        # refresh size player
                        self.players[i].size = new_size(
                            self.players[i].size,
                            self.players[j].size
                        )
                        self.players[j].size, self.players[j].speed_x, \
                            self.players[j].speed_y = 0, 0, 0

                    if self.players[i].conn is not None:
                        # data add in list visible enemy
                        x_ = str(round(dist_x / self.players[i].L))
                        y_ = str(round(dist_y / self.players[i].L))
                        r_ = str(
                            round(self.players[j].size / self.players[i].L))
                        c_ = self.players[j].colour
                        n_ = self.players[j].name

                        if self.players[j].size >= 30 * self.players[i].L:
                            self.visible_enemy[i].append(
                                x_ + " " + y_ + " " + r_ + " " + c_ + " " + n_
                            )
                        else:
                            self.visible_enemy[i].append(
                                x_ + " " + y_ + " " + r_ + " " + c_
                            )

                # j see i
                if (
                        (abs(dist_x) <= (self.players[j].w_vision) // 2 +
                         self.players[i].size)
                        and
                        (abs(dist_y) <= (self.players[j].h_vision) // 2 +
                         self.players[i].size)

                ):
                    # j can it eat i
                    if ((dist_x ** 2 + dist_y ** 2) ** 0.5 <= self.players[
                        j].size and
                            self.players[j].size > 1.1 * self.players[i].size):
                        # refresh size player
                        self.players[j].size = new_size(
                            self.players[j].size,
                            self.players[i].size
                        )
                        self.players[i].size, self.players[i].speed_x, \
                            self.players[i].speed_y = 0, 0, 0

                    if self.players[j].conn is not None:
                        # data add in list visible enemy
                        x_ = str(round(-dist_x / self.players[i].L))
                        y_ = str(round(-dist_y / self.players[i].L))
                        r_ = str(
                            round(self.players[i].size / self.players[i].L)
                        )
                        c_ = self.players[i].colour
                        n_ = self.players[i].name

                        if self.players[i].size >= 30 * self.players[j].L:
                            self.visible_enemy[j].append(
                                x_ + " " + y_ + " " + r_ + " " + c_ + " " + n_
                            )
                        else:
                            self.visible_enemy[j].append(
                                x_ + " " + y_ + " " + r_ + " " + c_
                            )
        self.response_any_pl(self.visible_enemy)

    def response_any_pl(self, visible_enemy):
        # response all players and accepts lists of visible objects
        self.responses = ["" for i in range(len(self.players))]
        for i in range(len(self.players)):
            new_size = str(round(self.players[i].size / self.players[i].L))
            visible_enemy[i] = [new_size] + visible_enemy[i]
            self.responses[i] = "<" + (",".join(visible_enemy[i])) + ">"

    def nst_game_map(self):
        # send new sate map
        for i in range(len(self.players)):
            if (self.players[i].conn is not None) and (self.players[i].ready):
                try:
                    self.players[i].conn.send(self.responses[i].encode())
                    self.players[i].errors = 0
                except:
                    self.players[i].errors += 1

    def clean_list_off_pl(self):
        # clean list offline players
        for player in self.players:
            if player.size == 0:
                if player.conn is not None:
                    player.dead += 1
                else:
                    player.dead += 300
            if (player.errors == 500) or (player.dead == 300):
                if player.conn is not None:
                    player.conn.close()
                self.players.remove(player)

    def clean_list_eat(self):
        # clean list eat
        for m in self.eat:
            if m.size == 0:
                self.eat.remove(m)

    def create_win_serv(self):
        # create window server and
        self.screen = pygame.display.set_mode(
            (self.small_WIDTH, self.small_HEIGHT)
        )

    @staticmethod
    def event_map() -> bool:
        # check event on map
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Server Offline!")
                return False

    def draw_nst_map(self):
        # draw new state map
        self.screen.fill("BLACK")
        for player in self.players:
            x = round(player.x * self.small_WIDTH / self.WIDTH_MAP)
            y = round(player.y * self.small_HEIGHT / self.HEIGHT_MAP)
            r = round(player.size * self.small_WIDTH / self.WIDTH_MAP)
            c = colours[player.colour]
            pygame.draw.circle(
                self.screen,
                c,
                (x, y),
                r
            )
        pygame.display.update()
