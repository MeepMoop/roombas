class Room:
  def __init__(self):
    self.entities = []
  def update(self):
    for entity in self.entities:
      entity.update()
  def draw(self):
    for entity in self.entities:
      entity.draw()
  def roomStart(self):
    pass
  def roomEnd(self):
    for entity in self.entities:
      entity.destroy()
    self.entities = []

class Entity:
  def __init__(self, x=0, y=0):
    self.x = x
    self.y = y
  def create(self):
    pass
  def update(self):
    pass
  def destroy(self):
    pass
  def draw(self):
    pass