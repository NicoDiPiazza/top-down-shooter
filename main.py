import pygame
import copy
from random import random
import math
from classes import *


# TODO make a csv containing the dialogue
# TODO make a dialogue function
# TODO make a shooting system
# TODO make a csv save/load save system
# TODO make an animation system




def game() -> None:
    pygame.init()
    screenWidth = 1000
    screenHeight = 600
    dt = 200      #in milliseconds
    screen_size = [ screenWidth, screenHeight]
    screen = pygame.display.set_mode(screen_size)
    camera = Camera(Coordinates(0, 0))
    pygame.event.get()
    keys = pygame.key.get_pressed()
    clock = pygame.time.Clock()
    current_fps = 200

    show_hitbox = True

    player_speed = 3
    player = Player(Coordinates(0, 0), 50, 20, 'Endepimus', 4, player_speed, 0, 5, 0, 100, 20)


    respawn_tank = Respawn_tank(random_loc(1000), 30)

    n_sirens = 10
    # when framerate is half of intended, speed should double to compensate
    siren_speed = 1
    all_sirens = []
    for i in range(n_sirens):
        all_sirens.append(Siren(random_loc(1000), 2, 40, 'Siren', 1, siren_speed, 30))

    all_crates = []
    n_crates = 10
    for i in range(n_crates):
        all_crates.append(Supply(random_loc(1000), 50, 'Crate', 2))



    keep_playing = True
    while keep_playing:
        pygame.event.get()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            keep_playing = False
            break
        screen.fill([255, 255, 255])

        if player.hp <= 0:
            player.death(respawn_tank)

        camera.location.column = player.location.column - screenWidth/2
        camera.location.row = player.location.row - screenHeight/2

        player.move_player(keys)
        if keys[pygame.K_SPACE] and len(all_sirens) > 0:
            closest_siren_to_player = closest_one(all_sirens, player)
            player.attack(closest_siren_to_player, 20)
        
        if keys[pygame.K_e] and len(all_crates) > 0:
            closest_crate_to_player = closest_one(all_crates, player)
            player.carry(closest_crate_to_player)

        player.draw_sprite(screen, camera, show_hitbox)
        player.speed = player_speed  * 200 / current_fps

        respawn_tank_image = pygame.transform.rotate(respawn_tank.sprite, -90)
        respawn_tank_rect = respawn_tank_image.get_rect(center = (rel_loc(respawn_tank.location, camera)[0],\
                                                                rel_loc(respawn_tank.location, camera)[1]))
        screen.blit(respawn_tank_image, respawn_tank_rect)

        sirens_to_kill = []
        for i in range(len(all_sirens)):
            siren = all_sirens[i]
            if siren.hp <= 0:
                sirens_to_kill.append(i)
                continue
            siren.speed = siren_speed * 200/current_fps
            siren.seek_player(player)
            siren.collide(all_sirens)

            siren.draw_sprite(screen, camera, show_hitbox)
        for i in sirens_to_kill:
            all_sirens.pop(i)
        sirens_to_kill = []


        for i in range(len(all_crates)):
            crate = all_crates[i]


            crate.draw_sprite(screen, camera, show_hitbox)
            crate.collide(all_crates)
            crate.collide(all_sirens)
            crate.collide([player])



        hud(screen, player.hp, player.hp_max)
        pygame.display.update()
        clock.tick(200)
        current_fps = clock.get_fps()
        if current_fps == 0:
            current_fps = 100
    pygame.quit()



def main() -> None:
    game()

if __name__ == '__main__':
    main()