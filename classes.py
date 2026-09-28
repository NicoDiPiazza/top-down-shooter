import math
import pygame
import copy
from random import random

class Coordinates:
    row: int
    column: int

    def __init__(self, row: int, column: int) -> None:
        self.column = column
        self.row = row

class Camera():
    location: Coordinates

    def __init__(self, location: Coordinates) -> None:
        self.location = location


class Entity:
    location: Coordinates
    hp_max: float
    hp: float
    facing_direction: list[float]
    radius: float
    name: float
    sprite: str

    def __init__(self, location: Coordinates, hp_max: float, radius: float, name: str) -> None:
        self.location = location
        self.hp_max = hp_max
        self.hp = self.hp_max
        self.facing_direction = [0, 0]
        self.radius = radius
        self.name = name

    def move(self, direction: list[float]) -> None:
        self.location.column += self.speed * direction[0]
        self.location.row += self.speed * direction[1]

    def collide(self, collideables: list['Entity']) -> None:
        # collideables must have a size and an ability to move # TODO
        for collideable in collideables:
            if (entity_distance(self, collideable)) < self.radius + collideable.radius and entity_distance(self, collideable) != 0:
                move_distance = self.radius + collideable.radius - (entity_distance(self, collideable)) + 1
                direction = get_direction(self.location, collideable.location)
                collideable.location.column += move_distance * direction[0]
                collideable.location.row += move_distance * direction[1]


    def generate_sprite(self, image_file: str, scale_factor) -> None:
        sprite_image = pygame.image.load(image_file).convert_alpha()

        sprite_width = sprite_image.get_width()
        sprite_height = sprite_image.get_height()

        sprite_area = sprite_width * sprite_height

        # my thought is, the scale factor should first divide by the smaller of the width and height, to bring that one to one, and then
        # both will be multipled by the diameter (2 * the radius)

        scale_factor = 2* self.radius / sprite_height


        sprite_image = pygame.transform.scale(sprite_image, (sprite_width * scale_factor, sprite_height * scale_factor))
        self.sprite = pygame.transform.rotate(sprite_image, 90)

    def draw_sprite(self, screen, camera: Camera, show_hitbox: bool) -> None:
        if show_hitbox:
            pygame.draw.circle(screen, 'red', ((rel_loc(self.location, camera))[0], (rel_loc(self.location, camera))[1]), self.radius, 2)
        sprite_image = pygame.transform.rotate(self.sprite, angle_to_face(self.facing_direction))
        sprite_image_rect = sprite_image.get_rect(center=((rel_loc(self.location, camera))[0],\
                                                            (rel_loc(self.location, camera))[1]))
        screen.blit(sprite_image, sprite_image_rect)

#------------------------------------------------------------------------------------------------------



class Inanimate(Entity):
    
    pass


class Character(Entity):
    strength: float
    speed: float
    cooldown_timer: int
    cooldown: int
    def __init__(self, location: Coordinates, hp_max: float, radius: float, name: str,\
                 strength: float, speed: float, cooldown: int) -> None:
            self.strength = strength
            self.speed = speed
            self.cooldown = cooldown
            self.cooldown_timer = cooldown
            
            super().__init__(location, hp_max, radius, name)


#----------------------------------------------------------------------------------------------------


class Supply(Entity):
    name: str
    weight: float
    location: Coordinates
    facing_direction: list[float]
    size: float

    def __init__(self, location: Coordinates, radius: float, name: str,\
                 weight: float) -> None:
        self.weight = weight
        super().__init__(location, 100, radius, name)

        self.generate_sprite('crate.jpg', 0.04)

class Respawn_tank(Entity):
    def __init__(self, location: Coordinates, radius: float):
        super().__init__(location, 100, radius, 'respawn tank')
        self.generate_sprite('respawn_tank.jpg', 0.1)



class Player(Character):
    magic_max: float
    magic: float
    armor: float
    tumors: int
    pickup_range: float

    def __init__(self, location: Coordinates, hp_max: float, radius: float, name: str,\
                 strength: float, speed: float,\
                 magic_max: float, armor: float, tumors: int, pickup_range: float, cooldown: int) -> None:
        self.magic_max = magic_max
        self.magic = self.magic_max
        self.armor = armor
        self.tumors = tumors
        self.pickup_range = pickup_range
        super().__init__(location, hp_max, radius, name, strength, speed, cooldown)

        self.generate_sprite('space_marine.png', 0.15)

    def attack(self, enemy: Entity, player_attack_range: float) -> None:
        # note that an enemy argument can be type Siren or Bastion
        close_enough = player_attack_range >= distance(self.location.column, enemy.location.column, self.location.row, enemy.location.row)
        if close_enough:
            enemy.hp -= self.strength
            # TODO cooldown stuff

    def carry(self, supply: Supply) -> None:
        close_enough = self.pickup_range >= distance(self.location.column, supply.location.column, self.location.row, supply.location.row)
        
        if self.strength >= supply.weight and close_enough:
            supply.facing_direction = self.facing_direction
            carrying_offset = 75
            supply.location.column = copy.deepcopy(self.location).column + carrying_offset*self.facing_direction[0]
            supply.location.row = copy.deepcopy(self.location).row + carrying_offset*self.facing_direction[1]
        else: # TODO
            pass # let the player know they can't pick anything up right now

    def move_player(self, keys) -> None:
        direction = [0, 0]

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            direction[1] -= 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            direction[0] -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            direction[1] += 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            direction[0] += 1

        direction_magnitude = ((direction[0]) **2 + (direction[1]) **2) ** 0.5

        if direction_magnitude != 0:
            direction = [direction[0] / direction_magnitude, direction[1] / direction_magnitude]
            self.facing_direction = direction
            self.move(direction)

    def death(self, respawn_tank: Entity) -> None:
        self.location = copy.deepcopy(respawn_tank.location)
        self.hp = self.hp_max




class Siren(Character):

    def __init__(self, location: Coordinates, hp_max: float, radius: float, name: str,\
                 strength: float, speed: float, cooldown: int) -> None:
        super().__init__(location, hp_max, radius, name,\
                         strength, speed, cooldown)
        self.generate_sprite('monster.png', 0.4)

    def attack(self, player: Player, siren_attack_range) -> None:
        armor_damage_factor = 0.1
        close_enough = siren_attack_range >= distance(player.location.column, self.location.column, player.location.row, self.location.row)
        if self.cooldown_timer > 0:
            self.cooldown_timer -= 1
        else:
            if close_enough:
                player.hp -= max((self.strength - player.armor), 0)
                player.armor -= (self.strength * armor_damage_factor)
                if player.armor < 0:
                    player.armor = 0
                self.cooldown_timer = self.cooldown

    def seek_player(self, player: Player) -> None:
        push_range = 50
        direction = get_direction(self.location, player.location)

        if self.speed < distance(self.location.column, player.location.column, self.location.row, player.location.row):
            self.move(direction)
            self.facing_direction = direction
        self.attack(player, push_range)


class Bastion:
    spawn_rate: float
    hp: float
    location: Coordinates

    def __init__(self, location: Coordinates, hp: float, spawn_rate: float) -> None:
        self.hp = hp
        self.location = location
        self.spawn_rate = spawn_rate


# helper functions ------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------

def distance(x1: int, x2: int, y1: int, y2: int) -> float:
    return((((x1 -x2)**2) + ((y1 - y2) **2)) ** 0.5)

def entity_distance(entity1: Entity, entity2: Entity):
    x1 = entity1.location.column
    x2 = entity2.location.column
    y1 = entity1.location.row
    y2 = entity2.location.row
    return distance(x1, x2, y1, y2)

def get_direction(loc1: Coordinates, loc2: Coordinates) -> list[float]:
    # this function returns a unit vector that points from the first argument to the second argument
    vector = []
    magnitude = distance(loc1.column, loc2.column, loc1.row, loc2.row)
    if magnitude > 0:
        vector.append(-(loc1.column - loc2.column) / magnitude)
        vector.append(-(loc1.row - loc2.row) / magnitude)
        return vector
    else:
        return [0, 1]

def rel_loc(location: Coordinates, camera: Camera) -> list[float]:
    # this returns the location of an object relative to the camera
    relative_loc = []
    relative_loc.append(location.column - camera.location.column)
    relative_loc.append(location.row - camera.location.row)

    return relative_loc

def random_loc(spawn_diameter) -> Coordinates:
    new_loc = Coordinates(int(random() * spawn_diameter - spawn_diameter/2), int(random() * spawn_diameter - spawn_diameter/2))
    return new_loc

def closest_one(group: list, looker):
    # this provides the closest object, distance-wise
    # it is assumed that everything in the group has a location
    closest_one = group[0]
    nearest_distance = 10 ** 100
    for thing in group:
        distance_to_thing = distance(thing.location.column, looker.location.column, thing.location.row, looker.location.row)
        if distance_to_thing <= nearest_distance and distance_to_thing > 0: # make sure that things pretty much always have unique locations
            closest_one = thing
            nearest_distance = distance(thing.location.column, looker.location.column, thing.location.row, looker.location.row)
    return closest_one

def angle_to_face(unit_vector: list[float]) -> float:
    if math.asin(unit_vector[1]) <=0:
        return math.degrees(math.acos(unit_vector[0])) 
    else:
        return math.degrees(-math.acos(unit_vector[0]))
    
def hud(screen, current_hp: float, hp_max: float) -> None:
    hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height = 20, 50, 200, 30
    hp_bar_border = 5
    pygame.draw.rect(screen, 'gray', (hp_bar_x - hp_bar_border, hp_bar_y - hp_bar_border,\
                                      hp_bar_width + 2*hp_bar_border, hp_bar_height + 2*hp_bar_border))
    pygame.draw.rect(screen, 'red', (hp_bar_x, hp_bar_y, hp_bar_width * current_hp / hp_max, hp_bar_height))
