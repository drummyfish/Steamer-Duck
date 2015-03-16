##
#
#
# For Python 2.7.

import pygame

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

class Level:
  def __init__():
    return

class Movable:
  def __init__():
    return

class Player(Movable):
  def __init__():
    return

class Game:
  def __init__():
    return

class Renderer:
  def __init__():
    return

screen = pygame.display.set_mode((800,600))

duck = pygame.image.load("resources/duck_right_jump_up_1.bmp")
duck_mask = pygame.image.load("resources/duck_right_jump_up_1_mask.bmp")

duck = prepare_image(duck,transparency_mask = duck_mask)

while 1:
  for event in pygame.event.get():
    if event.type == pygame.QUIT: sys.exit()

  screen.fill(pygame.Color("black"))
  screen.blit(duck,(0,0))
  pygame.display.flip()
