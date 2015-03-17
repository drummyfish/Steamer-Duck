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
    self.tile_variant = 0
    self.enemy_id = 0

  def __str__(self):
    if self.object_type == MapGridObject.OBJECT_TILE:
      return "T"
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
    return

#-----------------------------------------------------------------------

class Level:

  ## Loads the level from given file.
  #

  def load_from_file(self,filename):
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
      elif content[line_number].rstrip() == "map:":
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
            self.map_array[pos_x][pos_y] = MapGridObject.get_instance_from_string(helper_list[pos_x])

          pos_y += 1

      line_number += 1

  def __init_attributes(self):
    ## the level name
    self.name = ""
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

  def __init__(self):
    self.__init_attributes()

#-----------------------------------------------------------------------

class Movable:
  def __init__(self):
    return

#-----------------------------------------------------------------------

class Player(Movable):
  def __init__(self):
    return

#-----------------------------------------------------------------------

class Enemy(Movable):
  def __init__(self):
    return

#-----------------------------------------------------------------------

class Game:
  def __init__(self):
    return

#-----------------------------------------------------------------------

class Renderer:
  TILE_WIDTH = 200
  TILE_HEIGHT = 200

  def __init_attributes(self):
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
    ## camera top left x offset from the origin in pixels
    self._camera_x = 0
    ## camera top left y offset from the origin in pixels
    self._camera_y = 0
    ## contains images of tiles indexed by tile id, each item is a list
    #  where each item contains an image of one tile variant starting
    #  from 1, index 0 contains an image for the tile top
    self.tile_images = {}
    ## Contains the level background image
    self.background_image = None
    ## How many times the background should be repeated in x direction
    self.background_repeat_times = 1
    ## Says which part of the map array is visible in format
    #  (x1,y1,x2,y2)
    self.visible_tile_area = (0,0,0,0)

  ## Sets the level to be rendered.
  #
  #  @param level Level object

  def set_level(self,level):
    self._level = level

    # load the level background image:
    self.background_image = prepare_image(pygame.image.load(("resources/background_" + self._level.background_name + ".bmp")))

    self.background_repeat_times = int(math.ceil(self.screen_width / float(self.background_image.get_width())))

    print(self.screen_width)
    print(self.background_image.get_width())
    print(self.screen_width / self.background_image.get_width())

    # load the tile images:
    for tile in level.tiles:
      self.tile_images[tile[0]] = []

      top_mask = pygame.image.load(("resources/tile_" + tile[1] + "_top_mask.bmp"))

      self.tile_images[tile[0]].append(prepare_image(pygame.image.load(("resources/tile_" + tile[1] + "_top.bmp")),transparency_mask = top_mask)) # tile top

      for variant_number in range(tile[2]):  # tile variants
        self.tile_images[tile[0]].append(prepare_image(pygame.image.load("resources/tile_" + tile[1] + "_" + str(variant_number + 1) + ".bmp")))

  ## Renders the level (without GUI).
  #
  #  @return image with rendered level (pygame.Surface)

  def render_level(self):
    result = pygame.Surface((self.screen_width,self.screen_height))
    result.fill(self._level.background_color)

    # draw the background image:

    for i in range(self.background_repeat_times):
      result.blit(self.background_image,(i * self.background_image.get_width() * i,0))

    # draw the tiles and map object:
    for j in range(self.visible_tile_area[1],self.visible_tile_area[3]):  # render only visible area
      for i in range(self.visible_tile_area[0],self.visible_tile_area[2]):
        map_grid_object = self._level.map_array[i][j]

        if map_grid_object == None:
          continue
        elif map_grid_object.object_type == MapGridObject.OBJECT_TILE:
          result.blit(self.tile_images[map_grid_object.tile_id][1],(i * Renderer.TILE_WIDTH - self._camera_x, j * Renderer.TILE_HEIGHT - self._camera_y))

    return result

  ## Sets the camera top left corner position.
  #
  #  @param camera_x x coordinate in pixels
  #  @param camera_y y coordinate in pixels

  def set_camera_position(self, camera_x, camera_y):
    self._camera_x = camera_x
    self._camera_y = camera_y

    helper_x = int(camera_x / Renderer.TILE_WIDTH)
    helper_y = int(camera_y / Renderer.TILE_HEIGHT)

    self.visible_tile_area = (max(helper_x,0),max(helper_y,0),min(helper_x + self.screen_width_tiles,self._level.width),min(helper_y + self.screen_height_tiles,self._level.height))

    print(self.visible_tile_area)

  def __init__(self, screen_width, screen_height):
    self.__init_attributes()
    self.screen_width = screen_width
    self.screen_height = screen_height
    self.screen_width_tiles = int(math.ceil(self.screen_width / Renderer.TILE_WIDTH)) + 2
    self.screen_height_tiles = int(math.ceil(self.screen_height / Renderer.TILE_HEIGHT)) + 2
    return

#-----------------------------------------------------------------------

l = Level()
l.load_from_file("resources/level1.lvl")

screen_width = 1024
screen_height = 768

screen = pygame.display.set_mode((screen_width,screen_height))
renderer = Renderer(screen_width,screen_height)

renderer.set_level(l)

cam_x = 0;
cam_y = 0;

while 1:
  for event in pygame.event.get():
    if event.type == pygame.QUIT: sys.exit()

    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_RIGHT:
        cam_x += 10
        print("r")
      elif event.key == pygame.K_LEFT:
        print("l")
        cam_x -= 10
      elif event.key == pygame.K_UP:
        print("u")
        cam_y -= 10
      elif event.key == pygame.K_DOWN:
        print("d")
        cam_y += 10

      print(str(cam_x) + " " + str(cam_y))
      renderer.set_camera_position(cam_x,cam_y)

  screen.blit(renderer.render_level(),(0,0))
  pygame.display.flip()
