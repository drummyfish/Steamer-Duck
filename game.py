# -*- coding: utf-8 -*-

## A duck game.
#
#
#
#  Miloslav 'tastyfish' Číž, 2015, FIT VUT Brno
#  For Python 2.7.

import pygame
import sys
import math
import random
import os

# time of the last frame in milliseconds
frame_time = 0.0

# after how many frames the player state will be updated (this is
# only a graphics thing)

#-----------------------------------------------------------------------

def text_to_fixed_width(text, width):
  if len(text) > width:
    return text[:width]

  return text + " " * (width - len(text))

#-----------------------------------------------------------------------

## Prepares image after loading for its use.
#
#  @param image image to be prepared (pygame.Surface)
#  @param transparent_color color that should be transparent, if not
#         given, no color will be transparent (pygame.Color)
#  @param transparency_mask image to be used as a transparency map, it
#         should be the same size as the image and should be gray scale,
#         0 meaning fully transparent, 255 fully non-transparent
#         (pygame.Surface)
#  @return prepared image

def prepare_image(image, transparent_color = None, transparency_mask = None):
  result = pygame.Surface.convert(image)

  if transparency_mask != None:
    result = pygame.Surface.convert_alpha(result)

    for y in range(image.get_height()):
      for x in range(image.get_width()):
        color = image.get_at((x,y))
        alpha = transparency_mask.get_at((x,y))

        color.a = alpha.r
        result.set_at((x,y),color)

  elif transparent_color != None:
    result = pygame.Surface.convert_alpha(result)

    for y in range(image.get_height()):
      for x in range(image.get_width()):
        color = image.get_at((x,y))

        if color == transparent_color:
          color.a = 0
          result.set_at((x,y),color)

  return result

#-----------------------------------------------------------------------

class MapGridObject:
  OBJECT_TILE = 0
  OBJECT_FINISH = 1
  OBJECT_TRAMPOLINE = 2
  OBJECT_COIN = 3
  OBJECT_EGG = 4
  OBJECT_ENEMY_FLYING = 5
  OBJECT_ENEMY_GROUND = 6
  OBJECT_PLAYER = 7
  OBJECT_SPIKES = 8

  ## Checks if the argument is a tile.
  #
  #  @return True if what is a tile, False otherwise

  @staticmethod
  def is_tile(what):
    return what != None and (what.object_type == MapGridObject.OBJECT_TILE or what.object_type == MapGridObject.OBJECT_TRAMPOLINE)

  ## Makes an instance of MapGridObject based on provided string.
  #
  #  @param object_string string representing the object
  #  @return MapGridObject instance or None (if the string represented
  #          no object)

  @staticmethod
  def get_instance_from_string(object_string):
    if object_string == ".":
      return None

    result = MapGridObject()

    if object_string[0] == "X":
      result.object_type = MapGridObject.OBJECT_FINISH
    elif object_string[0] == "E":
      result.object_type = MapGridObject.OBJECT_EGG
    elif object_string[0] == "C":
      result.object_type = MapGridObject.OBJECT_COIN
    elif object_string[0] == "P":
      result.object_type = MapGridObject.OBJECT_PLAYER
    elif object_string[0] == "T":
      result.object_type = MapGridObject.OBJECT_TRAMPOLINE
    elif object_string[0] == "S":
      result.object_type = MapGridObject.OBJECT_SPIKES
    elif object_string[0] == "F":
      result.object_type = MapGridObject.OBJECT_ENEMY_FLYING
      result.enemy_id = int(object_string[2:])
    elif object_string[0] == "G":
      result.object_type = MapGridObject.OBJECT_ENEMY_GROUND
      result.enemy_id = int(object_string[2:])
    else:    # tile
      result.object_type = MapGridObject.OBJECT_TILE
      helper_list = object_string.split(";")
      result.tile_id = int(helper_list[0])
      result.tile_variant = int(helper_list[1])

    return result

  def __init_attributes(self):
    self.object_type = MapGridObject.OBJECT_TILE
    self.tile_id = 0
    self.tile_variant = 1
    self.enemy_id = 0

  def __str__(self):
    if self.object_type == MapGridObject.OBJECT_TILE:
      return "t"
    if self.object_type == MapGridObject.OBJECT_COIN:
      return "C"
    if self.object_type == MapGridObject.OBJECT_EGG:
      return "E"
    if self.object_type == MapGridObject.OBJECT_PLAYER:
      return "P"
    if self.object_type == MapGridObject.OBJECT_ENEMY_FLYING:
      return "F"
    if self.object_type == MapGridObject.OBJECT_ENEMY_GROUND:
      return "G"
    if self.object_type == MapGridObject.OBJECT_FINISH:
      return "F"
    return "?"

  def __init__(self):
    self.__init_attributes()
    return

#-----------------------------------------------------------------------

class Level:

  STATE_PLAYING = 0
  STATE_WON = 1
  STATE_LOST = 2

  ## Loads the level from given file.
  #
  #  @param filename file to be loaded

  def load_from_file(self,filename):
    self.filename = filename

    with open(filename) as input_file:
      content = input_file.readlines()

    for i in range(len(content)):    # get rid of newlines and spaces
      content[i] = ((content[i])[:-1]).rstrip()

    line_number = 0

    while line_number < len(content):
      if content[line_number] == "name:":
        line_number += 1
        self.name = content[line_number]
      elif content[line_number] == "background:":
        line_number += 1
        self.background_name = content[line_number]
        line_number += 1
        self.background_color = pygame.Color(content[line_number])
      elif content[line_number].rstrip() == "tiles:":
        while True:
          line_number += 1
          if line_number >= len(content) or len(content[line_number]) == 0:
            break

          helper_list = content[line_number].split()
          self.tiles.append((int(helper_list[0]),helper_list[1],int(helper_list[2])))

      elif content[line_number] == "outside:":
        line_number += 1
        self.outside_tile = MapGridObject()
        self.outside_tile.object_type = MapGridObject.OBJECT_TILE
        self.outside_tile.tile_id = int(content[line_number])
        self.outside_tile.tile_variant = 1

      elif content[line_number] == "scores:":
        line_number += 1

        while True:
          if line_number >= len(content):
            break

          split_line = content[line_number].split()

          if len(split_line) != 3:
            break

          self.scores.append((split_line[0],int(split_line[1]),int(split_line[2])))
          line_number += 1

        line_number -= 1

        self._sort_scores()

      elif content[line_number] == "map:":
        line_number += 1
        helper_list = content[line_number].split()  # map size
        self.width = int(helper_list[0])
        self.height = int(helper_list[1])
        self.map_array = [[None] * self.height for item in range(self.width)]
        pos_y = 0

        while True:              # load the map grid
          line_number += 1

          if line_number >= len(content) or len(content[line_number]) == 0:
            break

          helper_list = content[line_number].split()

          for pos_x in range(len(helper_list)):

            helper_object = MapGridObject.get_instance_from_string(helper_list[pos_x])

            if helper_object == None:
              self.map_array[pos_x][pos_y] = helper_object
            elif helper_object.object_type == MapGridObject.OBJECT_PLAYER:
              self.player = Player(self)
              self.player.position_x = pos_x + 0.5
              self.player.position_y = pos_y + 0.5
            elif helper_object.object_type == MapGridObject.OBJECT_ENEMY_FLYING:
              self.enemies.append(Enemy(self,Enemy.ENEMY_FLYING))
              self.enemies[-1].position_x = pos_x + 0.5
              self.enemies[-1].position_y = pos_y + 0.5
            elif helper_object.object_type == MapGridObject.OBJECT_ENEMY_GROUND:
              self.enemies.append(Enemy(self,Enemy.ENEMY_GROUND))
              self.enemies[-1].position_x = pos_x + 0.5
              self.enemies[-1].position_y = pos_y + 0.5
            else:
              if helper_object.object_type == MapGridObject.OBJECT_EGG:
                self.eggs_left += 1
              elif helper_object.object_type == MapGridObject.OBJECT_COIN:
                self.coins_total += 1

              self.map_array[pos_x][pos_y] = helper_object

          pos_y += 1

      line_number += 1

  ## Saves the scores into a file that's associated with the level
  #  (the one that's been passed to load_from_file method).

  def save_scores(self):
    if len(self.filename) == 0:
      return

    output_lines = []

    input_file = open(self.filename)

    for line in input_file:
      if line.lstrip().rstrip() == "scores:":
        break
      else:
        output_lines.append(line)

    input_file.close()

    output_file = open(self.filename,"w")

    for line in output_lines:
      output_file.write(line)

    output_file.write("scores:\n")

    for score in self.scores:
      output_file.write(score[0] + " " + str(score[1]) + " " + str(score[2]) + "\n")

    output_file.close()

  ## Says to add a new score entry. The entry will be added if it will
  #  be among the top scores.
  #
  #  @param name player name (string)
  #  @param time time in milliseconds (int)
  #  @param score player score

  def add_score(self, name, time, score):
    if len(self.scores) < 20:   # record 20 highest scores
      self.scores.append((name,score,time))
    else:
      minimum_index = 0
      i = 0

      while len(self.scores):
        if self.scores[i][1] < self.scores[minimum_index][1]:
          minimum_index = i

        i += 1

      if self.scores[minimum_index][1] < score:
        del self.scores[minimum_index]
        self.scores.append((name,score,time))
        self._sort_scores()

  def _sort_scores(self):
    self.scores.sort(key = lambda item: item[1],reverse = True)

  ## Checks the game state and updates it acoordingly, for example if
  #  a player is standing on an egg, they will take it.

  def update(self):
    player_tile_x = int(self.player.position_x)
    player_tile_y = int(self.player.position_y)

    self.time = pygame.time.get_ticks() - self._time_start

    object_at_player_tile = self.get_at(player_tile_x,player_tile_y)
    object_under_player_tile = self.get_at(player_tile_x,player_tile_y + 1)

    if object_at_player_tile != None:
      if object_at_player_tile.object_type == MapGridObject.OBJECT_COIN:
        self.sound_player.play_coin()
        self.map_array[player_tile_x][player_tile_y] = None
        self.coins_collected += 1
      elif object_at_player_tile.object_type == MapGridObject.OBJECT_EGG:
        self.sound_player.play_click()
        self.map_array[player_tile_x][player_tile_y] = None
        self.eggs_left -= 1
      elif object_at_player_tile.object_type == MapGridObject.OBJECT_FINISH:
        if self.eggs_left <= 0:
          self.state = Level.STATE_WON
          self.add_score(self.game.name,pygame.time.get_ticks() - self._time_start,self.score)
          self.save_scores()
          self.player.force_computer.velocity_vector[0] = 0
          self.sound_player.play_win()
      elif object_at_player_tile.object_type == MapGridObject.OBJECT_SPIKES:
        self.set_lost()
        return

    if object_under_player_tile != None and object_under_player_tile.object_type == MapGridObject.OBJECT_TRAMPOLINE and not self.player.is_in_air():
      self.player.force_computer.velocity_vector[1] = -10
      self.sound_player.play_trampoline()

    # compute the score:

    self.score = int(20000000.0 / (pygame.time.get_ticks() - self._time_start + 20000)) + self.coins_collected * 200

    # check colissions of player with enemies:

    for enemy in self.enemies:
      if self.player.collides(enemy):
        self.set_lost()

  ## Sets the game state to lost and takes appropriate actions.

  def set_lost(self):
    if self.state == Level.STATE_LOST:
      return

    self.player.last_quack_time = -99999 # to allow the player to make quack
    self.player.quack()

    self.state = Level.STATE_LOST
    self.player.solid = False
    self.player.force_computer.velocity_vector[0] = -1
    self.player.force_computer.velocity_vector[1] = -4
    self.player.force_computer.acceleration_vector[0] = 0
    self.player.force_computer.ground_friction = 0

  def __init_attributes(self):
    ## this will contain the name of the file associated with the level
    self.filename = ""
    ## game to which the level belongs
    self.game = None
    ## the level name
    self.name = ""
    ## current score
    self.score = 0
    ## holds the level scores, the items of the list are tuples
    #  (name, score, time in ms)
    self.scores = []
    ## state of the game
    self.state = Level.STATE_PLAYING
    ## total number of coins in the level, this doesn not decrease as
    #  the player takes them
    self.coins_total = 0
    ## how many coins the player has collected in the level so far
    self.coins_collected = 0
    ## how many eggs are there left in the level
    self.eggs_left = 0
    ## the level background name
    self.background_name = ""
    ## background color (pygame.Color)
    self.background_color = None
    ## list of tile types - dicts in format [id (int), name (str), number of variants (int)]
    self.tiles = []
    ## map width in tiles
    self.width = 0
    ## map height in tiles
    self.height = 0
    ## 2D list of map grid objects representing the map, each item can
    #  be None (representing nothing) or a MapGridObject
    self.map_array = None
    ## contains a MapGridObject representing a tile with which the area
    #  outside of the level is filled
    self.outside_tile = None
    ## the player object
    self.player = None
    ## contains enemies
    self.enemies = []
    ## plays the sounds in the game
    self.sound_player = None
    ## gravity force
    self.gravity = 4.7
    ## time from the level start in miliseconds
    self.time = 0
    ## time at which the level was created
    self._time_start = pygame.time.get_ticks()

  ## Gets the MapGridObject at given position in the map with map
  #  boundary check.
  #
  #  @param x x position
  #  @param y y position
  #  @return MapGridObject at given position (can be also None), if the
  #          position provided is outside the map area, the
  #          MapGridObject representing the outside tile is returned

  def get_at(self, x, y):
    if x < 0 or x >= self.width or y < 0 or y >= self.height:
      return self.outside_tile

    return self.map_array[x][y]

  def __init__(self, game):
    self.__init_attributes()
    self.sound_player = game.sound_player
    self.game = game

#-----------------------------------------------------------------------

## Represents an object that has a position and a rectangular shape. The
#  object can be moved with collision detections.

class Movable(object):
  def __init_attributes(self):
    ## x position of the center in tiles (float)
    self.position_x = 0.0
    ## y position of the center in tiles (float)
    self.position_y = 0.0
    ## object width in tiles (float)
    self.width = 0.4
    ## object height in tiles (float)
    self.height = 0.8
    ## reference to a level in which the object is placed (for colision
    #  detection)
    self.level = None
    ## says if collisions are applied when moving
    self.solid = True

  ## Check if the object collides with another object.
  #
  #  @param with_what object to check the collision with (Movable)
  #  @return True if the objects collide, otherwise False

  def collides(self, with_what):
    if ((self.position_x < with_what.position_x and
         self.position_x < with_what.position_x + with_what.width and
         self.position_x + self.width < with_what.position_x and
         self.position_x + self.width < with_what.position_x + with_what.width)
         or
         (self.position_x > with_what.position_x and
         self.position_x > with_what.position_x + with_what.width and
         self.position_x + self.width > with_what.position_x and
         self.position_x + self.width > with_what.position_x + with_what.width)):
      return False

    if ((self.position_y < with_what.position_y and
         self.position_y < with_what.position_y + with_what.height and
         self.position_y + self.height < with_what.position_y and
         self.position_y + self.height < with_what.position_y + with_what.height)
         or
         (self.position_y > with_what.position_y and
         self.position_y > with_what.position_y + with_what.height and
         self.position_y + self.height > with_what.position_y and
         self.position_y + self.height > with_what.position_y + with_what.height)):
      return False

    return True

  ## Checks if the object is in the air (i.e. there is no tile right
  #  below it)
  #
  #  @return True if the object is in the air, False otherwise

  def is_in_air(self):
    distance_to_ground = 99999

    lower_border = self.position_y + self.height / 2.0
    tile_y = int(lower_border) + 1

    if MapGridObject.is_tile(self.level.get_at(int(self.position_x),tile_y)):
      distance_to_ground = tile_y - lower_border

    return distance_to_ground > 0.1

  ## Moves the object by given position difference with colission
  #  detections.
  #
  #  @param dx position difference in x, in tiles (float)
  #  @param dy position difference in y, in tiles (float)

  def move_by(self, dx, dy):
    if not self.solid:
      self.position_x += dx
      self.position_y += dy
      return

    half_width = self.width / 2.0
    half_height = self.height / 2.0

    # occupied cells in format (x1,y1,x2,y2)
    occupied_cells = (int(self.position_x - half_width),int(self.position_y - half_height),int(self.position_x + half_width),int(self.position_y + half_height))

    # distances to nearest obstacles:
    distance_x = 0
    distance_y = 0

    if dx > 0:
      minimum = 65536

      for i in range(occupied_cells[1],occupied_cells[3] + 1):
        value = 65536

        for j in range(occupied_cells[2] + 1,occupied_cells[2] + 3):  # checks the following two cells
          if MapGridObject.is_tile(self.level.get_at(j,i)):
            value = j
            break

        if value < minimum:
          minimum = value

      distance_x = minimum - (self.position_x + half_width)
    elif dx < 0:
      maximum = -2048

      for i in range(occupied_cells[1],occupied_cells[3] + 1):
        value = -2048

        for j in range(occupied_cells[0] - 1,occupied_cells[0] - 3,-1):
          if MapGridObject.is_tile(self.level.get_at(j,i)):
            value = j
            break

        if value > maximum:
          maximum = value

      distance_x = (maximum + 1) - (self.position_x - half_width)

    if dy > 0:
      minimum = 65536

      for i in range(occupied_cells[0],occupied_cells[2] + 1):
        value = 65536

        for j in range(occupied_cells[3] + 1,occupied_cells[3] + 3):  # checks the following two cells
          if MapGridObject.is_tile(self.level.get_at(i,j)):
            value = j
            break

        if value < minimum:
          minimum = value

      distance_y = minimum - (self.position_y + half_height)
    elif dy < 0:
      maximum = -2048

      for i in range(occupied_cells[0],occupied_cells[2] + 1):
        value = -2048

        for j in range(occupied_cells[1] - 1,occupied_cells[1] - 3,-1):
          if MapGridObject.is_tile(self.level.get_at(i,j)):
            value = j
            break

        if value > maximum:
          maximum = value

      distance_y = (maximum + 1) - (self.position_y - half_height)

    if abs(distance_x) > abs(dx):
      self.position_x += dx

    if abs(distance_y) > abs(dy):
      self.position_y += dy

  def __init__(self, level):
    self.__init_attributes()
    self.level = level
    return

#-----------------------------------------------------------------------

class Player(Movable):
  PLAYER_STATE_STANDING = 0
  PLAYER_STATE_WALKING = 1
  PLAYER_STATE_JUMPING_UP = 2
  PLAYER_STATE_JUMPING_DOWN = 3
  QUACK_COOLDOWN = 5000       # quack cooldown time in milliseconds
  QUACK_DURATION = 2500       # for how long the quack immobilises the enemies

  def __init_attributes(self):
    ## basic player state
    self.state = Player.PLAYER_STATE_STANDING
    ## whether the player is facing right or left
    self.facing_right = True
    ## whether the player is flapping its wings
    self.flapping_wings = False
    self.last_quack_time = -999999
    ## force computer of the player
    self.force_computer = ForceComputer(self)

  def jump(self):
    self.force_computer.velocity_vector[1] = -3.7

  ## Makes the player quack and takes appropriate actions (tells the
  #  level about it etc).

  def quack(self):
    if pygame.time.get_ticks() < self.last_quack_time + Player.QUACK_COOLDOWN:
      return

    self.last_quack_time = pygame.time.get_ticks()
    self.level.sound_player.play_quack()

  def __init__(self, level):
    super(Player,self).__init__(level)
    self.__init_attributes()
    self.force_computer.acceleration_vector[0] = self.level.gravity     # set the gravity
    self.force_computer.acceleration_vector[1] = 0


#-----------------------------------------------------------------------

class Enemy(Movable):
  ENEMY_FLYING = 0
  ENEMY_GROUND = 1

  ## Makes the enemy move accoording to its AI. The step length is
  #  computed out of a global
  #  variable frame_time.

  def ai_move(self):
    self.force_computer.execute_step()

    if pygame.time.get_ticks() < self.level.player.last_quack_time + Player.QUACK_DURATION:  # quack is active => monsters don't move
      self.force_computer.velocity_vector[0] = 0

      if self.enemy_type == Enemy.ENEMY_FLYING:
        self.force_computer.velocity_vector[1] = 0

      return

    if pygame.time.get_ticks() >= self.next_direction_change:
      self.next_direction_change = pygame.time.get_ticks() + random.randint(500,2000)
      self.__recompute_direction()

  ## Private method, recomputes the direction of movement to a new
  #  direction and remembers it as a velocity vector in force computer.

  def __recompute_direction(self):
    self.force_computer.velocity_vector[0] = 1.0 - random.random() * 2.0
    self.force_computer.velocity_vector[1] = 1.0 - random.random() * 2.0

  def __init__(self, level, enemy_type = ENEMY_GROUND):
    super(Enemy,self).__init__(level)
    self.enemy_type = enemy_type

    self.force_computer = ForceComputer(self)

    if self.enemy_type == Enemy.ENEMY_GROUND:  # apply gravity to the ground robot
      self.force_computer.acceleration_vector[0] = 0
      self.force_computer.acceleration_vector[1] = level.gravity

    self.force_computer.ground_friction = 0

    ## time of next direction change
    self.next_direction_change = 0

    self.enemy_type = enemy_type
    return

#-----------------------------------------------------------------------

## Tile top layer image container.

class TileTopImageContainer:
  def __init__(self):
    ## full image
    self.image = None
    ## subimage - left
    self.left = None
    ## subimage - center
    self.center = None
    ## subimage - right
    self.right = None

#-----------------------------------------------------------------------

## Character (player, enemy, ...) image container.

class CharacterImageContainer:
  def __init__(self):
    self.standing = []
    self.moving_right = []
    self.moving_left = []
    self.jumping = []
    self.special = []

#-----------------------------------------------------------------------

class SoundPlayer:

  ## Initialises the sound player.
  #
  #  @param allow whether the sound is allowed or not (boolean)

  def __init__(self, allow):
    self.allowed = allow

    if not self.allowed:
      return

    pygame.mixer.init()

    if not pygame.mixer.get_init:
      return

    self.sound_quack = pygame.mixer.Sound("resources/quack.wav")
    self.sound_trampoline = pygame.mixer.Sound("resources/trampoline.wav")
    self.sound_coin = pygame.mixer.Sound("resources/coin.wav")
    self.sound_click = pygame.mixer.Sound("resources/click.wav")
    self.sound_flap = pygame.mixer.Sound("resources/flapping.wav")
    self.sound_win = pygame.mixer.Sound("resources/win.wav")

    pygame.mixer.music.load("resources/blue_dot_session.wav")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play()

  def play_quack(self):
    if self.allowed:
      self.sound_quack.play()

  def play_trampoline(self):
    if self.allowed:
      self.sound_trampoline.play()

  def play_coin(self):
    if self.allowed:
      self.sound_coin.play()

  def play_click(self):
    if self.allowed:
      self.sound_click.play()

  def play_flap(self):
    if self.allowed:
      self.sound_flap.play()

  def play_win(self):
    if self.allowed:
      self.sound_win.play()

#-----------------------------------------------------------------------

class Renderer:
  TILE_WIDTH = 200
  TILE_HEIGHT = 200
  TOP_LAYER_OFFSET = 10
  TOP_LAYER_LEFT_WIDTH = 23
  QUACK_LENGTH = 350

  def __init_attributes(self):
    ## normal sized font
    self.font_normal = pygame.font.Font("resources/Folktale.ttf",28)
    ## small sized font
    self.font_small = pygame.font.Font("resources/larabiefont.ttf",20)
    ## the text color
    self.font_color = (100,50,0)
    ## reference to a level being rendered
    self._level = None
    ## screen width in pixel
    self.screen_width = 640
    ## screen height in pixel
    self.screen_height = 480
    ## screen width in tiles (rounded up)
    self.screen_width_tiles = 1
    ## screen height in tiles (rounded up)
    self.screen_height_tiles = 1
    ## camera top left corner x offset from the origin in pixels
    self._camera_x = 0
    ## camera top left corner y offset from the origin in pixels
    self._camera_y = 0
    ## contains images of tiles indexed by tile id, each item is a list
    #  where each item contains an image of one tile variant starting
    #  from 1, index 0 contains a TileTopImageContainer
    self.tile_images = {}
    ## contains the level background image
    self.background_image = None
    ## contains prerendered image of high score text
    self.scores_image = None
    arrow_mask = pygame.image.load("resources/arrow_mask.bmp")
    self.arrow_image = prepare_image(pygame.image.load("resources/arrow.bmp"),transparency_mask = arrow_mask)
    ## contains flying enemy images
    self.enemy_flying_images = []
    enemy_flying_mask = pygame.image.load("resources/robot_flying_1_mask.bmp")
    self.enemy_flying_images.append(prepare_image(pygame.image.load("resources/robot_flying_1.bmp"),transparency_mask = enemy_flying_mask))
    enemy_flying_mask = pygame.image.load("resources/robot_flying_2_mask.bmp")
    self.enemy_flying_images.append(prepare_image(pygame.image.load("resources/robot_flying_2.bmp"),transparency_mask = enemy_flying_mask))
    enemy_flying_mask = pygame.image.load("resources/robot_flying_3_mask.bmp")
    self.enemy_flying_images.append(prepare_image(pygame.image.load("resources/robot_flying_3.bmp"),transparency_mask = enemy_flying_mask))
    ## contains ground enemy images
    self.enemy_ground_images = []
    enemy_ground_mask = pygame.image.load("resources/robot_ground_stand_mask.bmp")
    self.enemy_ground_images.append(prepare_image(pygame.image.load("resources/robot_ground_stand.bmp"),transparency_mask = enemy_ground_mask))
    enemy_ground_mask = pygame.image.load("resources/robot_ground_right_mask.bmp")
    self.enemy_ground_images.append(prepare_image(pygame.image.load("resources/robot_ground_right.bmp"),transparency_mask = enemy_ground_mask))
    enemy_ground_mask = pygame.image.load("resources/robot_ground_left_mask.bmp")
    self.enemy_ground_images.append(prepare_image(pygame.image.load("resources/robot_ground_left.bmp"),transparency_mask = enemy_ground_mask))
    ## contains teleport image
    teleport_mask = pygame.image.load("resources/teleport_mask.bmp")
    self.teleport_inactive_image = prepare_image(pygame.image.load("resources/teleport_1.bmp"),transparency_mask = teleport_mask)
    self.teleport_active_image = prepare_image(pygame.image.load("resources/teleport_2.bmp"),transparency_mask = teleport_mask)
    self.logo_image = prepare_image(pygame.image.load("resources/logo.bmp"))
    ## contains coin animation images
    self.coin_images = []

    score_bar_mask = pygame.image.load("resources/score_bar_mask.bmp")
    self.score_bar_image = prepare_image(pygame.image.load("resources/score_bar.bmp"),transparency_mask = score_bar_mask)

    for i in range(1,7):
      coin_mask = pygame.image.load("resources/coin_" + str(i) + "_mask.bmp")
      self.coin_images.append(prepare_image(pygame.image.load("resources/coin_" + str(i) + ".bmp"),transparency_mask = coin_mask))

    egg_mask = pygame.image.load("resources/egg_mask.bmp")
    ## contains egg image
    self.egg_image = prepare_image(pygame.image.load("resources/egg.bmp"),transparency_mask = egg_mask)

    ## how many times the background should be repeated in x direction
    self.background_repeat_times = 1
    ## Says which part of the map array is visible in format
    #  (x1,y1,x2,y2)
    self.visible_tile_area = (0,0,0,0)

    spikes_mask = pygame.image.load("resources/spikes_mask.bmp")
    ## contains the spikes image
    self.spikes_image = prepare_image(pygame.image.load("resources/spikes.bmp"),transparency_mask = spikes_mask)
    ## contains the trampoline image
    self.trampoline_image = prepare_image(pygame.image.load("resources/trampoline.bmp"))

    ## contains images of the player (the duck)
    self.player_images = CharacterImageContainer()

    self.player_images.standing.append(prepare_image(pygame.image.load("resources/duck_right_stand.bmp"),transparency_mask = pygame.image.load("resources/duck_right_stand_mask.bmp")))
    self.player_images.standing.append(pygame.transform.flip(self.player_images.standing[0],True,False))

    for i in range(1,7):
      self.player_images.moving_right.append(prepare_image(pygame.image.load("resources/duck_right_walk_" + str(i) + ".bmp"),transparency_mask = pygame.image.load("resources/duck_right_walk_" + str(i) + "_mask.bmp")))
      self.player_images.moving_left.append(pygame.transform.flip(self.player_images.moving_right[-1],True,False))

    self.player_images.jumping.append(prepare_image(pygame.image.load("resources/duck_right_jump_up_1.bmp"),transparency_mask = pygame.image.load("resources/duck_right_jump_up_1_mask.bmp")))
    self.player_images.jumping.append(prepare_image(pygame.image.load("resources/duck_right_jump_up_2.bmp"),transparency_mask = pygame.image.load("resources/duck_right_jump_up_2_mask.bmp")))
    self.player_images.jumping.append(prepare_image(pygame.image.load("resources/duck_right_jump_down_1.bmp"),transparency_mask = pygame.image.load("resources/duck_right_jump_down_1_mask.bmp")))
    self.player_images.jumping.append(prepare_image(pygame.image.load("resources/duck_right_jump_down_2.bmp"),transparency_mask = pygame.image.load("resources/duck_right_jump_down_2_mask.bmp")))
    self.player_images.jumping.append(pygame.transform.flip(self.player_images.jumping[0],True,False))
    self.player_images.jumping.append(pygame.transform.flip(self.player_images.jumping[1],True,False))
    self.player_images.jumping.append(pygame.transform.flip(self.player_images.jumping[2],True,False))
    self.player_images.jumping.append(pygame.transform.flip(self.player_images.jumping[3],True,False))

    self.player_images.special.append(prepare_image(pygame.image.load("resources/duck_right_quack.bmp"),transparency_mask = pygame.image.load("resources/duck_right_quack_mask.bmp")))
    self.player_images.special.append(pygame.transform.flip(self.player_images.special[0],True,False))

  ## Converts number of milliseconds to a string in format:
  #  ss:m.
  #
  #  @param value number of milliseconds
  #  @return string in format described above

  def __milliseconds_to_time(self, value):
    seconds = int(value / 1000)
    tenths = int((value % 1000) / 100)

    return str(seconds) + ":" + str(tenths)

  ## Sets the level to be rendered.
  #
  #  @param level Level object

  def set_level(self, level):
    self._level = level

    # load the level background image:
    self.background_image = prepare_image(pygame.image.load("resources/background_" + self._level.background_name + ".bmp"))

    self.background_repeat_times = int(math.ceil(self.screen_width / float(self.background_image.get_width())))

    # load the tile images:
    for tile in level.tiles:
      self.tile_images[tile[0]] = []

      # tile top:
      top_mask = pygame.image.load(("resources/tile_" + tile[1] + "_top_mask.bmp"))
      top_image = prepare_image(pygame.image.load(("resources/tile_" + tile[1] + "_top.bmp")),transparency_mask = top_mask)

      self.tile_images[tile[0]].append(TileTopImageContainer())

      self.tile_images[tile[0]][0].image = top_image
      self.tile_images[tile[0]][0].left = top_image.subsurface(pygame.Rect(0,0,23,56)) # left
      self.tile_images[tile[0]][0].center = top_image.subsurface(pygame.Rect(24,0,201,56)) # center
      self.tile_images[tile[0]][0].right = top_image.subsurface(pygame.Rect(225,0,21,56)) # right

      # tile variants:
      for variant_number in range(tile[2]):
        self.tile_images[tile[0]].append(prepare_image(pygame.image.load("resources/tile_" + tile[1] + "_" + str(variant_number + 1) + ".bmp")))

    # make the score image:

    self.scores_image = prepare_image(pygame.Surface((250,200)),pygame.Color(0,0,0))
    text_image = self.font_normal.render("top scores:",1,self.font_color)
    self.scores_image.blit(text_image,(0,0))

    for i in range(min(3,len(self._level.scores))):
      text_image = self.font_small.render(text_to_fixed_width(self._level.scores[i][0],10) + " " + text_to_fixed_width(str(self._level.scores[i][1]),6) + " " + text_to_fixed_width(self.__milliseconds_to_time(self._level.scores[i][2]),6),1,self.font_color)
      self.scores_image.blit(text_image,(0,30 + (i + 1) * 20))

  ## Private method, checks if the tile at given position in the level
  #  has a top layer (i.e. there is no other tile above it) and what
  #  type.
  #
  #  @param x x position of the tile
  #  @param y y position of the tile
  #  @return a tree item tuple with boolean values (left, center, right)

  def __get_top_layer(self, x, y):
    center = not MapGridObject.is_tile(self._level.get_at(x, y - 1))
    left = not MapGridObject.is_tile(self._level.get_at(x, y - 1)) and not MapGridObject.is_tile(self._level.get_at(x - 1, y)) and not MapGridObject.is_tile(self._level.get_at(x - 1, y - 1))
    right = not MapGridObject.is_tile(self._level.get_at(x, y - 1)) and not MapGridObject.is_tile(self._level.get_at(x + 1, y)) and not MapGridObject.is_tile(self._level.get_at(x + 1, y - 1))

    return (left,center,right)

  ## Private method, computes the screen pixel coordinates out of given
  #  map square coordinates (float) taking camera position into account.
  #
  #  @param x x map position in tiles (double)
  #  @param y y map position in tiles (double)
  #  @return (x,y) tuple of pixel screen coordinates

  def __map_position_to_screen_position(self, x, y):
    return (x * Renderer.TILE_WIDTH - self._camera_x,y * Renderer.TILE_HEIGHT - self._camera_y)

  ## Renders given menu.
  #
  #  @param menu menu screen to be rendered (Menu)
  #  @return image (Surface) with the menu rendered

  def render_menu(self, menu):
    result = pygame.Surface((self.screen_width,self.screen_height))
    result.fill((255,255,255))

    result.blit(self.logo_image,(self.screen_width / 2 - self.logo_image.get_width() / 2,self.screen_height / 2 - self.logo_image.get_height() / 2))

    i = 0

    while i < len(menu.items):
      text_image = self.font_normal.render(menu.items[i],1,(0,0,0))
      result.blit(text_image,(100,100 + i * 40))

      if i == menu.selected_item:
        result.blit(self.arrow_image,(50,95 + i * 40))

      i += 1

    i = 0

    while i < len(menu.text_lines):
      text_image = self.font_small.render(menu.text_lines[i],1,(0,0,0))
      result.blit(text_image,(100,self.screen_height / 2 + i * 30))
      i += 1

    return result

  ## Renders the level (without GUI).
  #
  #  @return image with rendered level (pygame.Surface)

  def render_level(self):
    result = pygame.Surface((self.screen_width,self.screen_height))
    result.fill(self._level.background_color)

    animation_frame = int(pygame.time.get_ticks() / 64)

    # draw the background image:

    for i in range(self.background_repeat_times):
      result.blit(self.background_image,(i * self.background_image.get_width(),0))

    # draw the tiles and map object:
    for j in range(self.visible_tile_area[1],self.visible_tile_area[3]):  # render only visible area
      for i in range(self.visible_tile_area[0],self.visible_tile_area[2]):
        map_grid_object = self._level.get_at(i,j)

        if map_grid_object == None:
          continue
        else:
          x = i * Renderer.TILE_WIDTH - self._camera_x
          y = j * Renderer.TILE_HEIGHT - self._camera_y

          if map_grid_object.object_type == MapGridObject.OBJECT_TILE:
            result.blit(self.tile_images[map_grid_object.tile_id][map_grid_object.tile_variant],(x,y))

            top_layer = self.__get_top_layer(i,j)

            if top_layer[0]:   # left
              result.blit(self.tile_images[map_grid_object.tile_id][0].left,(x - Renderer.TOP_LAYER_LEFT_WIDTH,y - Renderer.TOP_LAYER_OFFSET))

            if top_layer[1]:   # center
              result.blit(self.tile_images[map_grid_object.tile_id][0].center,(x,y - Renderer.TOP_LAYER_OFFSET))

            if top_layer[2]:   # right
              result.blit(self.tile_images[map_grid_object.tile_id][0].right,(x + Renderer.TILE_WIDTH,y - Renderer.TOP_LAYER_OFFSET))

          elif map_grid_object.object_type == MapGridObject.OBJECT_SPIKES:
            result.blit(self.spikes_image,(x,y))
          elif map_grid_object.object_type == MapGridObject.OBJECT_EGG:
            result.blit(self.egg_image,(x + 50,y + 50))
          elif map_grid_object.object_type == MapGridObject.OBJECT_COIN:
            result.blit(self.coin_images[animation_frame % len(self.coin_images)],(x + 20,y))
          elif map_grid_object.object_type == MapGridObject.OBJECT_TRAMPOLINE:
            result.blit(self.trampoline_image,(x,y))
          elif map_grid_object.object_type == MapGridObject.OBJECT_FINISH:
            if self._level.eggs_left > 0:
              result.blit(self.teleport_inactive_image,(x,y))
            else:
              result.blit(self.teleport_active_image,(x,y))

    # draw the player:

    player_position = self.__map_position_to_screen_position(self._level.player.position_x,self._level.player.position_y)

    player_image = self.player_images.standing[0]

    if self._level.player.flapping_wings:
      flapping_animation_frame = animation_frame % 2
    else:
      flapping_animation_frame = 0

    if pygame.time.get_ticks() < self._level.player.last_quack_time + Renderer.QUACK_LENGTH:
      if self._level.player.facing_right:
        player_image = self.player_images.special[0]
      else:
        player_image = self.player_images.special[1]
    elif self._level.player.state == Player.PLAYER_STATE_STANDING:
      if self._level.player.facing_right:
        player_image = self.player_images.standing[0]
      else:
        player_image = self.player_images.standing[1]
    elif self._level.player.state == Player.PLAYER_STATE_WALKING:
      if self._level.player.facing_right:
        player_image = self.player_images.moving_right[animation_frame % len(self.player_images.moving_right)]
      else:
        player_image = self.player_images.moving_left[animation_frame % len(self.player_images.moving_right)]
    elif self._level.player.state == Player.PLAYER_STATE_JUMPING_UP:
      if self._level.player.facing_right:
        player_image = self.player_images.jumping[flapping_animation_frame]
      else:
        player_image = self.player_images.jumping[4 + flapping_animation_frame]
    elif self._level.player.state == Player.PLAYER_STATE_JUMPING_DOWN:
      if self._level.player.facing_right:
        player_image = self.player_images.jumping[3 - flapping_animation_frame]
      else:
        player_image = self.player_images.jumping[7 - flapping_animation_frame]

    result.blit(player_image,(player_position[0] - player_image.get_width() / 2,player_position[1] - player_image.get_height() / 2))

    # draw the enemies:

    for enemy in self._level.enemies:
      enemy_position = self.__map_position_to_screen_position(enemy.position_x,enemy.position_y)

      if enemy.enemy_type == Enemy.ENEMY_GROUND:
        if enemy.force_computer.velocity_vector[0] > 0.5:
          enemy_image = self.enemy_ground_images[1]
        elif enemy.force_computer.velocity_vector[0] < -0.5:
          enemy_image = self.enemy_ground_images[2]
        else:
          enemy_image = self.enemy_ground_images[0]
      else:
        enemy_image = self.enemy_flying_images[animation_frame % 3]

      result.blit(enemy_image,(enemy_position[0] - enemy_image.get_width() / 2,enemy_position[1] - enemy_image.get_height() / 2))

    # draw the GUI:

    line_height = 30

   # result.blit(self.score_bar_image,(22,20))
    text_image = self.font_normal.render("time: " + self.__milliseconds_to_time(self._level.time),1,self.font_color)
    result.blit(text_image,(50,50))
    text_image = self.font_normal.render("score: " + str(self._level.score),1,self.font_color)
    result.blit(text_image,(50,50 + line_height))
    result.blit(self.scores_image,(self.screen_width - 300,50))

    if self._level.state == Level.STATE_LOST:
      text_image = self.font_normal.render("you lost",1,(255,0,0))
      result.blit(text_image,(self.screen_width / 2 - text_image.get_width() / 2,self.screen_height / 2 - text_image.get_height() / 2))
    elif self._level.state == Level.STATE_WON:
      text_image = self.font_normal.render("you won",1,(0,255,0))
      result.blit(text_image,(self.screen_width / 2 - text_image.get_width() / 2,self.screen_height / 2 - text_image.get_height() / 2))

    return result

  ## Sets the camera center position.
  #
  #  @param camera_x x coordinate in pixels
  #  @param camera_y y coordinate in pixels

  def set_camera_position(self, camera_x, camera_y):
    self._camera_x = camera_x - self.screen_width / 2
    self._camera_y = camera_y - self.screen_width / 2

    helper_x = int(self._camera_x / Renderer.TILE_WIDTH)
    helper_y = int(self._camera_y / Renderer.TILE_HEIGHT)

    self.visible_tile_area = (helper_x,helper_y,helper_x + self.screen_width_tiles,helper_y + self.screen_height_tiles)

  def __init__(self, screen_width, screen_height):
    self.__init_attributes()
    self.screen_width = screen_width
    self.screen_height = screen_height
    self.screen_width_tiles = int(math.ceil(self.screen_width / Renderer.TILE_WIDTH)) + 2
    self.screen_height_tiles = int(math.ceil(self.screen_height / Renderer.TILE_HEIGHT)) + 2
    return

#-----------------------------------------------------------------------

## A decorator that moves given movable object acoording to forces it
#  computes.

class ForceComputer:
  def __init_attributes(self):
    ## reference to decorated object (Movable)
    self.decorated_object = None

    ## velocity in tiles per second
    self.velocity_vector = [0,0]

    ## acceleration in tiles per second squared
    self.acceleration_vector = [0,0]

    ## maximum speed that will be assigned int horizontal direction
    self.maximum_horizontal_speed = 3


    ## says how much of the horizontal speed will be converted to
    #  acceleration in opposite direction
    self.ground_friction = 5

  ## Applies the forces to the decorated object and computes new forces.
  #

  def execute_step(self):
    if frame_time == 0:    # we don't want to be diving by zero
      return

    seconds = frame_time / 1000.0

    object_position = (self.decorated_object.position_x,self.decorated_object.position_y)
    self.decorated_object.move_by(self.velocity_vector[0] * seconds,self.velocity_vector[1] * seconds)
    object_position2 = (self.decorated_object.position_x,self.decorated_object.position_y)

    self.velocity_vector = [(object_position2[0] - object_position[0]) / seconds,(object_position2[1] - object_position[1]) / seconds]

    self.velocity_vector[0] += (self.acceleration_vector[0] - self.velocity_vector[0] * self.ground_friction) * seconds
    self.velocity_vector[1] += self.acceleration_vector[1] * seconds

  def __init__(self, decorated_object):
    self.__init_attributes()
    self.decorated_object = decorated_object

#-----------------------------------------------------------------------

## Represents a menu screen.

class Menu:
  def __init__(self):
    ## list of menu items
    self.items = []
    ## index of the selected item
    self.selected_item = 0
    ## optional text to be displayed in the menu
    self.text_lines = []

  def cursor_up(self):
    self.selected_item = max(self.selected_item - 1,0)

  def cursor_down(self):
    self.selected_item = min(self.selected_item + 1,len(self.items) - 1)

#-----------------------------------------------------------------------

class Config:
  def __init__(self, filename):
    self.sound = True
    self.fullscreen = False
    self.name = "player"

    try:
      lines = [line.strip() for line in open(filename)]

      for line in lines:
        line_split = line.split(":")
        line_split[0] = line_split[0].lstrip().rstrip()
        line_split[1] = line_split[1].lstrip().rstrip()

        if line_split[0] == "sound":
          self.sound = line_split[1] == "yes"
        elif line_split[0] == "fullscreen":
          self.fullscreen = line_split[1] == "yes"
        elif line_split[0] == "name":
          self.sound = line_split[1]

    except Exception:    # make a new config file
      output_file = open(filename,'w')
      output_file.write("name: player\nfullscreen: no\nsound: yes\n")
      output_file.close()

#-----------------------------------------------------------------------

## The main game class handling the inpu management, calling renderer,
#  the main game loop etc.

class Game:
  STATE_MENU_MAIN = 0
  STATE_MENU_ABOUT = 1
  STATE_MENU_PLAY = 2
  STATE_IN_GAME = 3
  VERSION = "1.1"

  FLYING_FORCE = 2    # what number is substracted from gravity when flapping the ducks wings

  UPDATE_STATE_AFTER_FRAMES = 7

  ## Initialises a new game.
  #
  #  @param name player name (string)
  #  @param fullscreen whether the game will be in fullscreen or not (boolean)
  #  @param sounds whether sounds and music will be played

  def __init__(self, name, fullscreen, sound):
    ## the player's name
    self.name = name
    self.fullscreen = fullscreen
    self.sound = sound
    self.state = Game.STATE_MENU_MAIN
    screen_width = 1024
    screen_height = 640

    if sound:
      pygame.mixer.pre_init(22050,-16,2,512)   # smaller size of the buffer (512) prevents the audio from lagging

    pygame.init()

    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (100,50)  # set the screen position

    if self.fullscreen:
      fullscreen_size = (pygame.display.list_modes())[0]

      if fullscreen_size != -1:
        screen_width = fullscreen_size[0]
        screen_height = fullscreen_size[1]

      self.screen = pygame.display.set_mode((screen_width,screen_height),pygame.FULLSCREEN)
    else:
      self.screen = pygame.display.set_mode((screen_width,screen_height))

    pygame.display.set_caption("steamer duck")
    pygame.mouse.set_visible(False)
    self.sound_player = SoundPlayer(sound)
    self.level = None
    self.renderer = Renderer(screen_width,screen_height)
    self.key_up = False
    self.key_down = False
    self.key_left = False
    self.key_right = False
    self.key_space = False
    self.key_ctrl = False
    self.key_return = False
    self.key_escape = False
    self.player_state_update_counter = 0    # the player state will be updated once every n frames,
                                            # this will prevent the "jerky" sprite changing
    self.menu_main = Menu()
    self.menu_main.items.append("new game")
    self.menu_main.items.append("about")
    self.menu_main.items.append("exit")

    self.menu_about = Menu()
    self.menu_about.items.append("back")
    self.menu_about.text_lines.append("Miloslav Ciz, 2015")
    self.menu_about.text_lines.append("version " + Game.VERSION)
    self.menu_about.text_lines.append("powered by Python + Pygame")
    self.menu_about.text_lines.append("your name is set to: " + self.name)

    self.menu_about.text_lines.append("")
    self.menu_about.text_lines.append("arrows = move")
    self.menu_about.text_lines.append("ctrl = quack")
    self.menu_about.text_lines.append("space = flap wings")
    self.menu_about.text_lines.append("get all eggs and get to the teleport")

    self.menu_play = Menu()
    self.menu_play.items.append("level 1")
    self.menu_play.items.append("level 2")
    self.menu_play.items.append("level 3")
    self.menu_play.items.append("level 4")
    self.menu_play.items.append("level 5")
    self.menu_play.items.append("level 6")
    self.menu_play.items.append("level 7")
    self.menu_play.items.append("level 8")
    self.menu_play.items.append("back")

  ## Runs the game.

  def run(self):
    global frame_time
    rendered_frame = None
    done = False
    wait = False     # whether the waiting is going on when the game is over
    flapping_player = False
    wait_until = 0
    cheat = False
    cheat_buffer = [0,0]

    while not done:
      time_start = pygame.time.get_ticks()

      for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

        if event.type == pygame.KEYDOWN:
          if event.key == pygame.K_RIGHT:
            self.key_right = True
          elif event.key == pygame.K_UP:
            self.key_up = True
          elif event.key == pygame.K_LEFT:
            self.key_left = True
          elif event.key == pygame.K_DOWN:
            self.key_down = True
          elif event.key == pygame.K_SPACE:
            self.key_space = True
          elif event.key == pygame.K_RCTRL or event.key == pygame.K_LCTRL:
            self.key_ctrl = True
          elif event.key == pygame.K_RETURN:
            self.key_return = True
          elif event.key == pygame.K_ESCAPE:
            self.key_escape = True
          elif event.key == pygame.K_KP4:
            cheat_buffer[0] = cheat_buffer[1]
            cheat_buffer[1] = 4
          elif event.key == pygame.K_KP2:
            cheat_buffer[0] = cheat_buffer[1]
            cheat_buffer[1] = 2
            if cheat_buffer[0] == 4 and cheat_buffer[1] == 2:
              self.sound_player.play_win()
              cheat = True
        elif event.type == pygame.KEYUP:
          if event.key == pygame.K_RIGHT:
            self.key_right = False
          elif event.key == pygame.K_LEFT:
            self.key_left = False
          elif event.key == pygame.K_UP:
            self.key_up = False
          elif event.key == pygame.K_DOWN:
            self.key_down = False
          elif event.key == pygame.K_SPACE:
            self.key_space = False
          elif event.key == pygame.K_RCTRL or event.key == pygame.K_LCTRL:
            self.key_ctrl = False
          elif event.key == pygame.K_RETURN:
            self.key_return = False
          elif event.key == pygame.K_ESCAPE:
            self.key_escape = False

      if self.state == Game.STATE_IN_GAME:
        if self.key_escape:
          self.state = Game.STATE_MENU_MAIN

        if self.level.state == Level.STATE_PLAYING:
          if self.key_up:
            if not self.level.player.state in [Player.PLAYER_STATE_JUMPING_UP, Player.PLAYER_STATE_JUMPING_DOWN] and not self.level.player.is_in_air():
              self.level.player.jump()

          if self.key_right and not self.key_left:
            self.level.player.force_computer.acceleration_vector[0] = 40 if cheat else 20.0
          elif self.key_left and not self.key_right:
            self.level.player.force_computer.acceleration_vector[0] = -40 if cheat else -20.0
          else:
            self.level.player.force_computer.acceleration_vector[0] = 0

          if self.key_ctrl:
            self.level.player.quack()

          if self.key_space:
            if not flapping_played:
              self.level.sound_player.play_flap()
              flapping_played = True

            self.level.player.flapping_wings = True
          else:
            flapping_played = False
            self.level.player.flapping_wings = False


          if self.level.player.flapping_wings:
            self.level.player.force_computer.acceleration_vector[1] = self.level.gravity - Game.FLYING_FORCE
          else:
            self.level.player.force_computer.acceleration_vector[1] = self.level.gravity

          self.level.update()
        else:
          if not wait:
            wait_until = pygame.time.get_ticks() + 3000 # wait 2 seconds
            wait = True
          elif pygame.time.get_ticks() >= wait_until:
            wait = False
            self.state = Game.STATE_MENU_MAIN

        for enemy in self.level.enemies:
          enemy.ai_move()

        self.level.player.force_computer.execute_step()

        if self.level.state != Level.STATE_LOST:     # follow the player only if he's not lost
          self.renderer.set_camera_position(int(self.level.player.position_x * Renderer.TILE_WIDTH),int(self.level.player.position_y * Renderer.TILE_HEIGHT) + 200)

        self.player_state_update_counter = (self.player_state_update_counter + 1) % Game.UPDATE_STATE_AFTER_FRAMES

        if self.player_state_update_counter == 0:
          if self.level.player.force_computer.velocity_vector[1] > 0.1:
            self.level.player.state = Player.PLAYER_STATE_JUMPING_DOWN
          elif self.level.player.force_computer.velocity_vector[1] < -0.1:
            self.level.player.state = Player.PLAYER_STATE_JUMPING_UP
          else:
            if self.level.player.force_computer.velocity_vector[0] > 0.1 or self.level.player.force_computer.velocity_vector[0] < -0.1:
              self.level.player.state = Player.PLAYER_STATE_WALKING
            else:
              self.level.player.state = Player.PLAYER_STATE_STANDING

          if self.level.player.force_computer.acceleration_vector[0] > 0.1:
            self.level.player.facing_right = True
          elif self.level.player.force_computer.acceleration_vector[0] < -0.1:
            self.level.player.facing_right = False

        self.screen.blit(self.renderer.render_level(),(0,0))
        pygame.display.flip()
      elif self.state == Game.STATE_MENU_MAIN:
        if self.key_up:
          self.menu_main.cursor_up()
          self.key_up = False

        if self.key_down:
          self.menu_main.cursor_down()
          self.key_down = False

        if self.key_return:
          if self.menu_main.selected_item == 0:
            self.state = Game.STATE_MENU_PLAY
          elif self.menu_main.selected_item == 1:
            self.state = Game.STATE_MENU_ABOUT
          elif self.menu_main.selected_item == 2:
            done = True

          self.key_return = False

        self.screen.blit(self.renderer.render_menu(self.menu_main),(0,0))
        pygame.display.flip()
      elif self.state == Game.STATE_MENU_ABOUT:
        if self.key_return:
          self.state = Game.STATE_MENU_MAIN
          self.key_return = False

        self.screen.blit(self.renderer.render_menu(self.menu_about),(0,0))
        pygame.display.flip()
      elif self.state == Game.STATE_MENU_PLAY:
        if self.key_up:
          self.menu_play.cursor_up()
          self.key_up = False

        if self.key_down:
          self.menu_play.cursor_down()
          self.key_down = False

        if self.key_return:
          if self.menu_play.selected_item == 8:
            self.state = Game.STATE_MENU_MAIN
          else:
            level_name = "level" + str(self.menu_play.selected_item + 1) + ".lvl"
            self.level = Level(self)
            self.level.load_from_file("resources/" + level_name)
            self.renderer.set_level(self.level)
            self.state = Game.STATE_IN_GAME

          self.key_return = False

        self.screen.blit(self.renderer.render_menu(self.menu_play),(0,0))
        pygame.display.flip()

      frame_time = pygame.time.get_ticks() - time_start

#-----------------------------------------------------------------------

config = Config("config.txt")
game = Game(config.name,config.fullscreen,config.sound)
game.run()












