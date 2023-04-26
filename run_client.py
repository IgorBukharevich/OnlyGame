import pygame
from client.client import GameClient


def main():

    run_client = True
    player = GameClient()
    try:
        player.create_pl_sock()
        player.send_resp_serv_cli()
        player.create_window()
    except:
        return print("Server Offline!")

    while run_client:
        try:
            # event handling
            if player.event_handling() == False:
                run_client = False
                pygame.quit()

            # we read the position of the player's mouse
            player.read_mouse_pos()

            # we send the received command to the server
            player.send_pl_command()

            # we receive a new state of the playing field from the server
            player.response_nst_game_map()

            # draw a new state of the playing field
            player.draw_nst_game_map()
            player.draw()
        except:
            run_client = False


if __name__ == "__main__":
    main()
