import sys, pygame
from GameObjects import *
from GameUtil import *
from math import *
import numpy as np
from random import random, randint

### main game class - edit settings

class Game:
  # settings
  _WINDOW_CAPTION = "Game"
  _FPS = 30
  _FPS_DISPLAY = False
  _WIDTH = 320
  _HEIGHT = 320
  _BGCOL = (255, 255, 255)

  # initialization
  _DIAG = (_WIDTH ** 2 + _HEIGHT ** 2) ** 0.5
  _DISPLAY = pygame.display.set_mode((_WIDTH, _HEIGHT), pygame.RESIZABLE)
  _GFX = pygame.Surface((_WIDTH, _HEIGHT), pygame.SRCALPHA)
  pygame.display.set_caption(_WINDOW_CAPTION)
  _CLOCK = pygame.time.Clock()

  _CREATION_QUEUE = []
  _DELETION_QUEUE = []

  _ROOMS = [Room()]
  _ACTIVE_ROOM = _ROOMS[0]

  @staticmethod
  def gameLoop():
    while True:
      # window closed
      for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
      # create queued instances
      for instance in Game._CREATION_QUEUE:
        instance.create()
        Game._ACTIVE_ROOM.entities.append(instance)
      Game._CREATION_QUEUE.clear()
      # update active room
      Game._ACTIVE_ROOM.update()
      # delete queued instances
      for instance in Game._DELETION_QUEUE:
        instance.destroy()
        Game._ACTIVE_ROOM.entities.remove(instance)
      Game._DELETION_QUEUE.clear()
      # draw
      Game._DISPLAY.fill(Game._BGCOL)
      Game._GFX.fill(Game._BGCOL)
      Game._ACTIVE_ROOM.draw()
      Game._DISPLAY.blit(Game._GFX, (0, 0))
      pygame.display.update()
      # manage framerate
      Game._CLOCK.tick(Game._FPS)
      if Game._FPS_DISPLAY: print('FPS:', Game._CLOCK.get_fps())

  @staticmethod
  def instanceCreate(instance):
    Game._CREATION_QUEUE.append(instance)
    return instance

  @staticmethod
  def instanceDestroy(instance):
    Game._DELETION_QUEUE.append(instance)
  
  @staticmethod
  def gotoRoom(roomNumber):
    Game._ACTIVE_ROOM.roomEnd()
    Game._ACTIVE_ROOM = Game._ROOMS[roomNumber]
    Game._ACTIVE_ROOM.roomStart()
  
  @staticmethod
  def entityExists(entity_class):
    for entity in Game._ACTIVE_ROOM.entities:
      if type(entity) == entity_class:
        return true
    return false
  
  @staticmethod
  def getEntities(entity_class):
    entities = []
    for entity in Game._ACTIVE_ROOM.entities:
      if type(entity) == entity_class:
        entities.append(entity)
    return entities
  
  @staticmethod
  def getEntitiesUnderParent(parent_class):
    entities = []
    for entity in Game._ACTIVE_ROOM.entities:
      if entity.__class__.__bases__[0] == parent_class or type(entity) == parent_class:
        entities.append(entity)
    return entities

### new rooms - inherit from base class (See GameObjects.py)

'''
class NewRoom(Room):
  def __init__(self): 
    super().__init__()
  def update(self):
    super().update()
  def draw(self):
    super().draw()
  def roomStart(self):
    super().roomStart()
  def roomEnd(self):
    super().roomEnd()
'''

class Environment(Room):
  def roomStart(self):
    super().roomStart()
    # build environment here - add obstacles, roombas, etc
    wallWidth = 32
    wallColorTop = [128, 128, 128]
    wallColorBottom = [128, 128, 128]
    wallColorLeft = [128, 128, 128]
    wallColorRight = [128, 128, 128]
    ballColor = [255, 128, 0]

    self.obstacles = []
    self.obstacles.append(Game.instanceCreate(ObstacleLine(wallWidth, wallWidth, Game._WIDTH - wallWidth, wallWidth, wallColorTop)))
    self.obstacles.append(Game.instanceCreate(ObstacleLine(wallWidth, wallWidth, wallWidth, Game._HEIGHT - wallWidth, wallColorLeft)))
    self.obstacles.append(Game.instanceCreate(ObstacleLine(Game._WIDTH - wallWidth, Game._HEIGHT - wallWidth, wallWidth, Game._HEIGHT - wallWidth, wallColorBottom)))
    self.obstacles.append(Game.instanceCreate(ObstacleLine(Game._WIDTH - wallWidth, Game._HEIGHT - wallWidth, Game._WIDTH - wallWidth, wallWidth, wallColorRight)))
    for i in range(3):
      self.obstacles.append(Game.instanceCreate(ObstacleCircle(1.5 * wallWidth + random() * (Game._WIDTH - 3 * wallWidth), 1.5 * wallWidth + random() * (Game._HEIGHT - 3 * wallWidth), wallWidth / 2, ballColor)))
    
    Game.instanceCreate(Roomba(160, 160, 16, 12, [32, 32, 32], random() * 2 * pi, 0.0, 0.5))


### new entities - inherit from base class (See GameObjects.py)

'''
class NewEntity(Entity):
  def __init__(self, x=0, y=0):
    super().__init__(x, y)
  def create(self):
    super().create()
  def update(self):
    super().update()
  def destroy(self):
    super().destroy()
  def draw(self):
    super().draw()
'''

class Roomba(Entity):
  sprFace = pygame.image.load('agent_face.png')

  ## events

  def __init__(self, x, y, r, rW, color, ang=0, lvel=0, rvel=0):
    super().__init__(x, y)
    self.r = r # roomba radius
    self.rW = rW # wheel distance from center
    self.color = color # [R, G, B]
    self.ang = ang # angle in radians
    self.lvel = lvel # linear velocity of left wheel
    self.rvel = rvel # linear velocity of right wheel
    self.xRem = 0 # x-remainder to account for rounding errors
    self.yRem = 0 # y-remainder ''
    self.bumpSensor = 0 # bump sensor
    # vision
    self.viewRays = 12 # number of rays
    self.viewRayDist = Game._DIAG # ray distance
    self.viewAngle = pi / 3 # field of view
    self.visRGB = [[0, 0, 0] for i in range(self.viewRays)] # vision RGB array
    self.visD = [0.0 for i in range(self.viewRays)] # vision depth array
    
    ### init RL stuff here ###
    self.S = np.zeros(3 * self.viewRays)
    self.wl = np.random.randn(3 * self.viewRays + 1) / np.sqrt(self.viewRays)
    self.wr = np.random.randn(3 * self.viewRays + 1) / np.sqrt(self.viewRays)
  
  def update(self):
    super().update()
    self.bumpSensor = 0 # reset bump sensor
    vel = (self.lvel + self.rvel) / 2 # compute linear velocity
    omega = (self.rvel - self.lvel) / self.rW # compute angular velocity
    self.ang += omega # increment angle
    self.ang = self.ang - 2 * pi if self.ang >= pi else self.ang + 2 * pi if self.ang < -pi else self.ang # wrap angle
    xvel = vel * cos(self.ang) # compute x-velocity
    yvel = vel * sin(self.ang) # compute y-velocity
    self.bumpSensor = self.moveX(xvel) or self.moveY(yvel) # adjust position and update bump sensor
    self.visRGB, self.visD = self.getVision(self.viewAngle, self.viewRays) # get RGBD information

    ### update RL stuff here ###
    ''' ignore this hacky genetic alg + backprop monster '''
    R = -2 * self.bumpSensor + abs(self.lvel + self.rvel)
    Sp = (np.array(self.visRGB) * (1 - np.array([self.visD]).T / Game._DIAG)).flatten() / 255
    phi = np.hstack((Sp, 1))
    self.lvel = tanh(np.dot(self.wl, phi))
    self.rvel = tanh(np.dot(self.wr, phi))
    self.S = Sp
    if R < 0.5:
      lvelTarget = 2 * randint(0, 1) - 1
      rvelTarget = 2 * randint(0, 1) - 1
      self.wl += 0.1 * (lvelTarget - self.lvel) * (1 - self.lvel ** 2) * phi
      self.wr += 0.1 * (rvelTarget - self.rvel) * (1 - self.rvel ** 2) * phi
  
  def draw(self):
    super().draw()
    pos = (int(self.x), int(self.y))
    self.drawVisionRays(self.viewAngle, self.viewRays) # draw vision rays
    pygame.draw.circle(Game._GFX, self.color, pos, self.r) # draw roomba color
    sprRotate = pygame.transform.rotate(Roomba.sprFace, self.ang * 180 / pi) # draw roomba face
    Game._GFX.blit(sprRotate, sprRotate.get_rect(center=pos))
    self.drawVision(8, 8, 8, self.visRGB, self.visD) # display vision RGB info
    self.drawBumpSensor(16 + 8 * self.viewRays, 8, 8) # display vision depth info
    self.drawState(8, 304, 8) # draw agent's state
  
  ## methods

  # set linear velocity of each wheel
  def setWheelVel(self, lvel, rvel):
    self.lvel = lvel
    self.rvel = rvel
  
  # set linear and angular velocity of roomba
  def setVel(self, vel, omega):
    self.lvel = vel - omega * self.rW / 2
    self.rvel = vel + omega * self.rW / 2
  
  # get vision RGB, D arrays
  def getVision(self, viewAngle, rays):
    vis = [[0, 0, 0] for i in range(rays)]
    depth = [Game._DIAG + 1 for i in range(rays)]
    if rays == 1:
      rayPts = [(self.x + self.viewRayDist + cos(self.ang), self.y - self.viewRayDist + sin(self.ang))]
    else:
      rayPts = [(self.x + self.viewRayDist * cos(self.ang + viewAngle * (0.5 - i / (rays - 1))), \
                 self.y - self.viewRayDist * sin(self.ang + viewAngle * (0.5 - i / (rays - 1)))) for i in range(rays)]
    for i, ray in enumerate(rayPts):
      for obstacle in Game._ACTIVE_ROOM.obstacles:
        if type(obstacle) == ObstacleRect:
          if collisionLineRectangle((self.x, self.y), ray, obstacle.rect.topleft, obstacle.rect.bottomright):
            dsqr = (obstacle.x - self.x) ** 2 + (obstacle.y - self.y) ** 2
            if dsqr < depth[i] ** 2:
              depth[i] = dsqr ** 0.5
              vis[i] = obstacle.color
        elif type(obstacle) == ObstacleCircle:
          if collisionCircleLine(obstacle.pos, obstacle.r, (self.x, self.y), ray):
            dsqr = (obstacle.x - self.x) ** 2 + (obstacle.y - self.y) ** 2
            if dsqr < depth[i] ** 2:
              depth[i] = dsqr ** 0.5
              vis[i] = obstacle.color
        elif type(obstacle) == ObstacleLine:
          pt = collisionPtLineLine(obstacle.A, obstacle.B, (self.x, self.y), ray)
          if pt != None:
            dsqr = (pt[0] - self.x) ** 2 + (pt[1] - self.y) ** 2
            if dsqr < depth[i] ** 2:
              depth[i] = dsqr ** 0.5
              vis[i] = obstacle.color
    return vis, depth
  
  # draw vision rays relative to roomba
  def drawVisionRays(self, viewAngle, rays):
    if rays == 1:
      rayPts = [(self.x + self.viewRayDist + cos(self.ang), self.y - self.viewRayDist + sin(self.ang))]
    else:
      rayPts = [(self.x + self.viewRayDist * cos(self.ang + viewAngle * (0.5 - i / (rays - 1))), \
                 self.y - self.viewRayDist * sin(self.ang + viewAngle * (0.5 - i / (rays - 1)))) for i in range(rays)]
    for ray in rayPts:
      pygame.draw.line(Game._GFX, [0, 0, 0], (self.x, self.y), ray)
  
  # draw RGBD visualization given coordinates and pixel width
  def drawVision(self, x, y, w, colors, depths):
    for i, color in enumerate(colors):
      pygame.draw.rect(Game._GFX, color, pygame.Rect(x + i * w, y, w, w))
    for i, depth in enumerate(depths):
      pygame.draw.rect(Game._GFX, [int(255 * (1 - min(1, depth / (Game._DIAG)))) for ray in range(3)], pygame.Rect(x + i * w, y + w, w, w))
  
  # draw bump sensor visualization given coordinates and pixel width
  def drawBumpSensor(self, x, y, w):
    pygame.draw.rect(Game._GFX, [(1 - self.bumpSensor) * 255, self.bumpSensor * 255, 0], pygame.Rect(x, y, w, w))
  
  # draw agent's state given coordinates and pixel width
  def drawState(self, x, y, w):
    for i, val in enumerate(self.S):
      pygame.draw.rect(Game._GFX, [val * 255 for ch in range(3)], pygame.Rect(x + i * w, y, w, w))
  
  # update roomba's x-position given x-velocity, return updated bump sensor
  def moveX(self, xvel):
    self.xRem += xvel
    amt = round(self.xRem)
    sgn = 1 if amt > 0 else -1 if amt < 0 else 0
    self.xRem -= amt
    for step in range(abs(amt)):
      if not self.collideObstacle(self.x + sgn, self.y):
        self.x += sgn
      else:
        self.xRem = 0
        return 1
    if amt == 0:
      sgn = 1 if self.xRem > 0 else -1 if self.xRem < 0 else 0
      if self.collideObstacle(self.x + sgn, self.y):
        self.xRem = 0
        return 1
    return 0

  # update roomba's y-position given y-velocity, return updated bump sensor
  def moveY(self, yvel):
    self.yRem += yvel
    amt = round(self.yRem)
    sgn = 1 if amt > 0 else -1 if amt < 0 else 0
    self.yRem -= amt
    for step in range(abs(amt)):
      if not self.collideObstacle(self.x, self.y - sgn):
        self.y -= sgn
      else:
        self.yRem = 0
        return 1
    if amt == 0:
      sgn = 1 if self.yRem > 0 else -1 if self.yRem < 0 else 0
      if self.collideObstacle(self.x, self.y - sgn):
        self.yRem = 0
        return 1
    return 0
  
  # check if roomba collided with an obstacle
  def collideObstacle(self, x, y):
    for obstacle in Game._ACTIVE_ROOM.obstacles:
      if type(obstacle) == ObstacleRect:
        if collisionCircleRectangle((x, y), self.r, obstacle.rect.topleft, obstacle.rect.bottomright):
          return True
      elif type(obstacle) == ObstacleCircle:
        if collisionCircleCircle((x, y), self.r, obstacle.pos, obstacle.r):
          return True
      elif type(obstacle) == ObstacleLine:
        if collisionCircleLine((x, y), self.r, obstacle.A, obstacle.B):
          return True
    return False
  
  # check if roomba collided with another roomba
  def collideRoomba(self, x, y):
    for roomba in Game.getEntities(Roomba):
      if self != roomba:
        if collisionCircle((x, y), self.r, (roomba.x, roomba.y), roomba.r):
          return True
    return False
  
  # bounce off of other roombas
  def bounceRoomba(self):
    for roomba in Game.getEntities(Roomba):
      if self != roomba:
        if collisionCircle((self.x, self.y), self.r, (roomba.x, roomba.y), roomba.r):
          self.x = self.x + 1 if self.x - roomba.x > 0 else self.x - 1 if self.x - roomba.x < 0 else self.x
          self.y = self.y + 1 if self.y - roomba.y > 0 else self.y - 1 if self.y - roomba.y < 0 else self.y
  
  # make the room wrap around 
  def wrapPos(self):
    self.x = self.x - Game._WIDTH if self.x >= Game._WIDTH else self.x + Game._WIDTH if self.x < 0 else self.x
    self.y = self.y - Game._HEIGHT if self.y >= Game._HEIGHT else self.y + Game._HEIGHT if self.y < 0 else self.y

# base obstacle entity
class Obstacle(Entity):
  def __init__(self, x=0, y=0):
    super().__init__(x, y)

# rectangle obstacle given top left coordinate, width, height
class ObstacleRect(Obstacle):
  def __init__(self, x1, y1, w, h, color=(0, 0, 0)):
    super().__init__(x1 + w/2, y1 + h/2)
    self.rect = pygame.Rect(int(x1), int(y1), int(w), int(h))
    self.color = color
  def draw(self):
    super().draw()
    pygame.draw.rect(Game._GFX, self.color, self.rect)

# circle obstacle given center coordinate and radius
class ObstacleCircle(Obstacle):
  def __init__(self, x1, y1, r, color=(0, 0, 0)):
    super().__init__(x1, y1)
    self.pos = (int(x1), int(y1))
    self.r = int(r)
    self.color = color
  def draw(self):
    super().draw()
    pygame.draw.circle(Game._GFX, self.color, self.pos, self.r)

# line segment obstacle given two end points
class ObstacleLine(Obstacle):
  def __init__(self, x1, y1, x2, y2, color=(0, 0, 0)):
    super().__init__((x1 + x2)/2, (y1 + y2)/2)
    self.A = (int(x1), int(y1))
    self.B = (int(x2), int(y2))
    self.color = color
  def draw(self):
    super().draw()
    pygame.draw.line(Game._GFX, self.color, self.A, self.B)

### entry point - add rooms here
if __name__ == '__main__':
  Game._ROOMS.clear()
  # add rooms
  Game._ROOMS.append(Environment())
  # set starting room
  Game.gotoRoom(0)
  # start game
  Game.gameLoop()
