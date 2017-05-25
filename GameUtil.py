def collisionCircleLine(C, r, A, B):
  LAB = ((B[0] - A[0]) ** 2 + (B[1] - A[1]) ** 2) ** 0.5
  m0 = (B[0] - A[0])/LAB
  m1 = (B[1] - A[1])/LAB
  t = (C[0] - A[0]) * m0 + (C[1] - A[1]) * m1
  if t < 0 or t > LAB:
    return False
  return (C[0] - (A[0] + t * m0)) ** 2 + (C[1] - (A[1] + t * m1)) ** 2 <= r ** 2

def collisionCircleRectangle(C, r, RA, RB):
  return collisionCircleLine(C, r, (RA[0], RA[1]), (RB[0], RA[1])) or \
  collisionCircleLine(C, r, (RA[0], RA[1]), (RA[0], RB[1])) or \
  collisionCircleLine(C, r, (RB[0], RB[1]), (RB[0], RA[1])) or \
  collisionCircleLine(C, r, (RB[0], RB[1]), (RA[0], RB[1])) or \
  (C[0] > RA[0] and C[0] < RB[0] and C[1] > RA[1] and C[1] < RB[1])

def collisionCircleCircle(C1, r1, C2, r2):
  return (C2[0] - C1[0]) ** 2 + (C2[1] - C1[1]) ** 2 <= (r1 + r2) ** 2

def collisionLineLine(A1, B1, A2, B2):
  den = ((B1[0] - A1[0]) * (B2[1] - A2[1])) - ((B1[1] - A1[1]) * (B2[0] - A2[0]))
  r = ((A1[1] - A2[1]) * (B2[0] - A2[0])) - ((A1[0] - A2[0]) * (B2[1] - A2[1]))
  s = ((A1[1] - A2[1]) * (B1[0] - A1[0])) - ((A1[0] - A2[0]) * (B1[1] - A1[1]))
  if den == 0:
    if r == 0 and s == 0:
      c = (A2[0] - A1[0]) / (B1[0] - A1[0])
      d = (B2[0] - A1[0]) / (B1[0] - A1[0])
      return (c >= 0 and c <= 1) or (d >= 0 and d <= 1)
    else:
      return False
  r /= den
  s /= den
  return (r >= 0 and r <= 1) and (s >= 0 and s <= 1)

def collisionLineRectangle(A, B, RA, RB):
  return collisionLineLine(A, B, (RA[0], RA[1]), (RB[0], RA[1])) or \
  collisionLineLine(A, B, (RA[0], RA[1]), (RA[0], RB[1])) or \
  collisionLineLine(A, B, (RB[0], RB[1]), (RB[0], RA[1])) or \
  collisionLineLine(A, B, (RB[0], RB[1]), (RA[0], RB[1]))

def collisionPtLineLine(A1, B1, A2, B2):
  den = ((B1[0] - A1[0]) * (B2[1] - A2[1])) - ((B1[1] - A1[1]) * (B2[0] - A2[0]))
  r = ((A1[1] - A2[1]) * (B2[0] - A2[0])) - ((A1[0] - A2[0]) * (B2[1] - A2[1]))
  s = ((A1[1] - A2[1]) * (B1[0] - A1[0])) - ((A1[0] - A2[0]) * (B1[1] - A1[1]))
  if den == 0:
    if r == 0 and s == 0:
      c = (A2[0] - A1[0]) / (B1[0] - A1[0])
      d = (B2[0] - A1[0]) / (B1[0] - A1[0])
      if c >= 0 and c <= 1:
        return (A1[0] + c * (B1[0] - A1[0]), A1[1] + c * (B1[1] - A1[1]))
      elif d >= 0 and d <= 1:
        return (A1[0] + d * (B1[0] - A1[0]), A1[1] + d * (B1[1] - A1[1]))
      else:
        return None
    else:
      return None
  r /= den
  s /= den
  if (r >= 0 and r <= 1) and (s >= 0 and s <= 1):
    return (A1[0] + r * (B1[0] - A1[0]), A1[1] + r * (B1[1] - A1[1]))
  else:
    return None