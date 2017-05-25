class Room:
  # init, base class sets up room's entity list
  def __init__(self):
    self.entities = []
  # update loop, base class calls update() of each entity in room
  def update(self):
    for entity in self.entities:
      entity.update()
  # draw event, base class calls draw() of each entity in room
  def draw(self):
    for entity in self.entities:
      entity.draw()
  # called when room starts, typically create initial entities here
  def roomStart(self):
    pass
  # called when room ends, base class clears room's entity list
  def roomEnd(self):
    self.entities = []

class Entity:
  # init, base class stores entity's coordinates
  def __init__(self, x=0, y=0):
    self.x = x
    self.y = y
  # create event, called when instance makes it out of the instance creation queue
  def create(self):
    pass
  # update loop
  def update(self):
    pass
  # destroy event, called when instance makes it out of the instance removal queue
  def destroy(self):
    pass
  # draw event
  def draw(self):
    pass