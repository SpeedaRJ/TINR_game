import numpy as np
import random
import math


def playerCanMove(asset, movement, speed, orientation, completed):
    xl = asset.bbox.ur[0]
    xh = asset.bbox.bl[0]
    yh = asset.bbox.ur[1]
    yl = asset.bbox.bl[1]

    context = [True, True, True, True]
    index = None

    if movement["w"]:
        if yl - speed < 60:
            if orientation[0] and not completed:
                index = 0

            else:
                context[0] = False

    if movement["d"]:
        if xh + speed > 600:
            if orientation[1] and not completed:
                index = 1

            else:
                context[1] = False

    if movement["s"]:
        if yh + speed > 560:
            if orientation[2] and not completed:
                index = 2

            else:
                context[2] = False

    if movement["a"]:
        if xl - speed < 40:
            if orientation[3] and not completed:
                index = 3

            else:
                context[3] = False

    if completed:
        index = None

    return (context, index)


def getPlayerMovement(movement, conditions, mvs):
    move = [0, 0]
    if movement["w"] and conditions[0][0]:
        move[1] -= mvs

    if movement["d"] and conditions[0][1]:
        move[0] += mvs

    if movement["s"] and conditions[0][2]:
        move[1] += mvs

    if movement["a"] and conditions[0][3]:
        move[0] -= mvs

    if not move[0] == 0 and not move[1] == 0:
        cdf = getPitagoraCoeffiecinet(mvs)
        move[0] = move[0]*mvs/cdf
        move[1] = move[1]*mvs/cdf

    return move


def distBetweenLocations(player_loc, enemy_loc):
    return np.linalg.norm(np.array([enemy_loc])-(np.array(player_loc)))


def closeEnoughAssets(loc, assets, dist):
    close = []
    for asset in assets:
        if distBetweenLocations(loc, getLocation(asset)) <= dist:
            close.append(asset)
    return close


def getEnemyDirection(player_loc, enemy_loc):
    margin = 8
    direct = False
    vertical_dist = abs(player_loc[1] - enemy_loc[1])
    horizontal_dist = abs(player_loc[0] - enemy_loc[0])
    if player_loc[0] < enemy_loc[0] and horizontal_dist > margin:
        direct = True

    if player_loc[0] > enemy_loc[0] and horizontal_dist > margin:
        direct = False
    return direct


def updateVector(location, move):
    return (np.array(location) + np.array(move)).tolist()


def getLocation(asset):
    return updateVector(asset.location, updateVector(asset.aType.centroid,
                                                     [-(asset.aType.bbox.bl[0] - asset.aType.bbox.ur[0])/2, 0]))


def registerHit(getting_hit, hitter):
    direction = hitter.aType.direction
    upper = hitter.aType.bbox.ur[1]
    lower = hitter.aType.bbox.bl[1]
    location = getLocation(hitter)
    range = hitter.aType.range
    box = [[location[0], upper - range/1.5],
           [location[0] - range if direction else location[0] + range, lower + range/1.5]]
    target = getLocation(getting_hit)
    if not direction:
        return (box[0][0] <= target[0] <= box[1][0]) and (box[0][1] <= target[1] <= box[1][1])
    return (box[1][0] <= target[0] <= box[0][0]) and (box[0][1] <= target[1] <= box[1][1])


def getDropChance():
    return random.random()


def getPitagoraCoeffiecinet(num):
    return np.sqrt(np.power(num, 2) + np.power(num, 2))


def angle_between(p2, p1):
    ang = math.degrees(math.atan2(p1[0] - p2[0], p1[1] - p2[1]))
    return int((ang + 360) % 360) - 90


def getMovement(loc, angle, n):
    x = loc[0] + n * math.cos(math.radians(angle))
    y = loc[1] - n * math.sin(math.radians(angle))
    return (x, y)


def getMouseOverButton(x, y, sx, sy, size, num):
    buttons = []
    for i in range(num):
        buttons.append((sx, sx + size[0], sy + size[1] * i +
                        size[2] * i, sy + size[1] * (i + 1) + size[2] * i))
    for button in buttons:
        if button[0] <= x <= button[1] and button[2] <= y <= button[3]:
            return buttons.index(button)
    return -1


def getMouseOverFrame(x, y, sx, sy, size, num):
    frames = []
    for i in range(num):
        frames.append((sx + size[0] * i + size[2] * i,
                       sx + sx + size[0] * (i + 1), sy, sy + size[1]))
    for frame in frames:
        if frame[0] <= x <= frame[1] and frame[2] <= y <= frame[3]:
            return frames.index(frame)
    return -1


def getMouseOverSlider(x, y, sx, sy, size):
    sliders = []
    for i in range(len(sx)):
        sliders.append((sx[i], sx[i] + size[0], sy[i], sy[i] + size[1]))
    for slider in sliders:
        if slider[0] <= x <= slider[1] and slider[2] <= y <= slider[3]:
            return sliders.index(slider)
    return -1


def getLevelMaze(bboxes, n):
    maze = np.ones((640, 640))
    for x in range(60, 580, int(n)):
        for y in range(60, 580, int(n)):
            value = 1
            for bbox in bboxes:
                xl = bbox.ur[0]
                xh = bbox.bl[0]
                yh = bbox.ur[1]
                yl = bbox.bl[1]
                if is_between(x, xl, xh) and is_between(y, yl, yh):
                    value = 10000
            maze[x][y] = value
    return maze


def is_between(x, p1, p2):
    if p1 < p2:
        return x in range(p1, p2 + 1)
    else:
        return x in range(p2, p1 + 1)
