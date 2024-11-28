from __future__ import division
from nodebox.graphics import *
import pymunk
import pymunk.pyglet_util
import random, math
import numpy as np

space = pymunk.Space()

def createBody(x, y, shape, *shapeArgs):
    body = pymunk.Body()
    body.position = x, y
    s = shape(body, *shapeArgs)
    s.mass = 1
    s.friction = 1
    space.add(body, s)
    return s

s0 = createBody(300, 300, pymunk.Poly, ((-20, -5), (-20, 5), (20, 15), (20, -15)))
s0.score = 0
s3 = createBody(200, 300, pymunk.Poly, ((-20, -5), (-20, 5), (20, 15), (20, -15)))
s3.color = (0, 255, 0, 255)
s3.score = 0
s3.body.Q = [[0, 0], [0, 0], [0, 0]]
s3.body.action = 0
s1 = createBody(300, 200, pymunk.Circle, 10, (0, 0))
S2 = [createBody(350, 250, pymunk.Circle, 10, (0, 0))]

def getAngle(x, y, x1, y1):
    return math.atan2(y1 - y, x1 - x)

def getDist(x, y, x1, y1):
    return math.sqrt((x - x1) ** 2 + (y - y1) ** 2)

def inCircle(x, y, cx, cy, R):
    return (x - cx) ** 2 + (y - cy) ** 2 < R ** 2

def inSector(x, y, cx, cy, R, a):
    angle = getAngle(cx, cy, x, y) % (2 * math.pi)
    a = a % (2 * math.pi)
    return inCircle(x, y, cx, cy, R) and a - 0.5 < angle < a + 0.5

def strategy(b=s3.body):
    v = 100
    a = b.angle
    b.velocity = v * math.cos(a), v * math.sin(a)
    x, y = b.position
    R = getDist(x, y, 350, 250)
    line(x, y, *s1.body.position, stroke=Color(0))
    if canvas.frame % 100 == 0:
        b.angle = getAngle(x, y, 350, 250) if R > 180 else getAngle(x, y, *s1.body.position)

def strategy2(b=s3.body):
    v = 100
    a = b.angle
    b.velocity = v * math.cos(a), v * math.sin(a)
    x, y = b.position
    R = getDist(x, y, 350, 250)
    ellipse(x, y, 200, 200, stroke=Color(0.5))
    line(x, y, x + 100 * math.cos(a + 0.5), y + 100 * math.sin(a + 0.5), stroke=Color(0.5))
    line(x, y, x + 100 * math.cos(a - 0.5), y + 100 * math.sin(a - 0.5), stroke=Color(0.5))

    if canvas.frame % 10 == 0:
        inS = inSector(s1.body.position[0], s1.body.position[1], x, y, 100, a)
        inS2 = inSector(S2[0].body.position[0], S2[0].body.position[1], x, y, 100, a)

        if inS:
            state = 1
            reward = 1 if b.action == 0 else -1
        elif inS2:
            state = 2
            reward = -1 if b.action == 0 else 1
        else:
            state = 0
            reward = 0
        b.Q[state][b.action] += reward

        act = b.Q[state][b.action]
        if random.random() < abs(1.0 / (act + 0.1)):
            b.action = random.choice([0, 1])
        else:
            b.action = np.argmax(b.Q[state])

        if b.action:
            b.angle = 2 * math.pi * random.random()

    if R > 180:
        b.angle = getAngle(x, y, 350, 250)

def scr(s, s0, s3, p=1):
    bx, by = s.body.position
    s0x, s0y = s0.body.position
    s3x, s3y = s3.body.position
    if not inCircle(bx, by, 350, 250, 180):
        if getDist(bx, by, s0x, s0y) < getDist(bx, by, s3x, s3y):
            s0.score += p
        else:
            s3.score += p
        s.body.position = random.randint(200, 400), random.randint(200, 300)

def score():
    scr(s1, s0, s3)
    for s in S2:
        scr(s, s0, s3, p=-1)

def manualControl():
    v = 10
    b = s0.body
    a = b.angle
    x, y = b.position
    vx, vy = b.velocity
    if canvas.keys.char == "a":
        b.angle -= 0.1
    if canvas.keys.char == "d":
        b.angle += 0.1
    if canvas.keys.char == "w":
        b.velocity = vx + v * math.cos(a), vy + v * math.sin(a)
    if canvas.mouse.button == LEFT:
        b.angle = getAngle(x, y, *canvas.mouse.xy)
        b.velocity = vx + v * math.cos(a), vy + v * math.sin(a)

def simFriction():
    for s in [s0, s1, s3] + S2:
        s.body.velocity = s.body.velocity[0] * 0.9, s.body.velocity[1] * 0.9
        s.body.angular_velocity *= 0.9

draw_options = pymunk.pyglet_util.DrawOptions()

def draw(canvas):
    canvas.clear()
    fill(0, 0, 0, 1)
    text("%i %i" % (s0.score, s3.score), 20, 20)
    nofill()
    ellipse(350, 250, 350, 350, stroke=Color(0))
    manualControl()
    strategy2()
    score()
    simFriction()
    space.step(0.02)
    space.debug_draw(draw_options)

canvas.size = 700, 500
canvas.run(draw)
