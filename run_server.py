import pygame.time
from server.server import GameServer

WORK_ON_SERVER = True


def main():
    """"""
    clock = pygame.time.Clock()
    FPS = 100

    serv_run = True
    serv = GameServer()
    serv.create_serv_sock()
    if not WORK_ON_SERVER:
        serv.create_win_serv()
    tick = -1
    while serv_run:
        tick += 1
        try:
            clock.tick(FPS)

            # checking if there are people willing to enter the game
            if tick == 200:
                tick = 0
                serv.check_new_conn()

            # we read the teams of all players
            serv.read_pl_command(tick)

            # we determine what each player sees
            serv.visible_players()

            # sending a new state of the playing field
            serv.nst_game_map()

            # we clean the list of fallen off players
            serv.clean_list_off_pl()

            # cleaning the list of fallen off mobs
            serv.clean_list_eat()
            if not WORK_ON_SERVER:
                # рисуем новое состояние карты
                serv.draw_nst_map()

                # drawing the state of the map
                if serv.event_map() == False:
                    serv_run = False
                    serv.serv_sock.close()
        except:
            serv_run = False


if __name__ == "__main__":
    main()
