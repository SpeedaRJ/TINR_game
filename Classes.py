import pygame
import json
import copy

from worldFunctions import *
from common import *


class JSON_base(object):
    def __init__(self, levels, states, entities, bboxes, elements, ui, save):
        self.levels = self.readFromFile(levels)
        self.states = self.readFromFile(states)
        self.entities = self.readFromFile(entities)
        self.bboxes = self.readFromFile(bboxes)
        self.elements = self.readFromFile(elements)
        self.ui = self.readFromFile(ui)
        self.save = self.readFromFile(save)

    def readFromFile(self, filename):
        with open(filename, 'r') as jsonFile:
            return json.load(jsonFile)

    def getAssetsFromJSON(self, enemies):
        array = []
        for enemy in enemies:
            asset = self.entities["enemies"][enemy[1]]
            array.append(AssetPrototype(
                asset["image"], enemy[0], self.getEnemyFromJSON(asset, enemy[1], enemy[0])))
        return array

    def getBBoxesFromJSON(self, multiple):
        array = []
        for bbox in self.levels[multiple]["bounding_boxes"]:
            ur = [bbox["loc"][0] + self.bboxes[bbox["name"]][0],
                  bbox["loc"][1] - self.bboxes[bbox["name"]][1]]
            bl = bbox["loc"]
            array.append(BoundingBox(bl, ur, self.bboxes[bbox["name"]][2]))
        return array

    def getEntityBBoxFromJSON(self, centroid, name):
        bl = [centroid[0], centroid[1]+self.bboxes[name][1]]
        ur = [centroid[0]+self.bboxes[name][0],
              centroid[1]-self.bboxes[name][1]]
        return BoundingBox(bl, ur, self.bboxes[name][2])

    def getPlayerFromJSON(self, selection, loc):
        char = self.entities["characters"][selection]
        centroid = updateVector(loc, char["centroid"])
        anim = char["animation"]
        return Character(char["image"], char["centroid"], Animator(Animation(char["delimiter"], anim[0], anim[1], anim[2])), char["hp"], char["max_hp"], char["mana"], char["damage"], char["speed"], char["range"], char["direction"], char["state"], self.states[selection], self.getEntityBBoxFromJSON(centroid, selection))

    def getEnemyFromJSON(self, enemy, name, loc):
        centroid = updateVector(loc, enemy["centroid"])
        anim = enemy["animation"]
        return Enemy(enemy["image"], enemy["centroid"], Animator(Animation(enemy["delimiter"], anim[0], anim[1], anim[2])), enemy["hp"], enemy["damage"], enemy["speed"], enemy["range"], enemy["direction"], enemy["state"], self.states[name], self.getEntityBBoxFromJSON(centroid, name), name, enemy["drop_chance"])

    def getLevelFromJSON(self, name, sprite_sheet):
        image = sprite_sheet.imageAt(self.levels[name]["image"])
        prototypes = self.getAssetsFromJSON(
            self.levels[name]["enemies"])
        return Level(image, prototypes, self.levels[name]["elements"], name, self.levels[name]["progression"], self.levels[name]["next_levels"], self.levels[name]["spawn_point"], self.getBBoxesFromJSON(multiple=name))

    def getElementsFromJSON(self, sprite_sheet):
        array = {}
        for name, values in self.elements.items():
            anim = values["anim"]
            array[name] = AssetPrototype(values["image"], [-10, -10], Element(values["image"], values["type"], values["amount"],
                                                                              values["centroid"], self.getEntityBBoxFromJSON(values["centroid"], values["type"]), Animator(Animation(values["delimiter"], anim[0], anim[1], anim[2])), self.states[name] if name in self.states else None)).convert(sprite_sheet)
        return array


class SpriteSheet(object):
    def __init__(self, filename, colorKey=None):
        self.sheet = pygame.image.load(filename).convert()
        self.colorKey = colorKey

    def imageAt(self, rectangle):
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        image.set_colorkey(self.colorKey)
        return image


class Asset(object):
    def __init__(self, image, aType, location):
        self.image = image
        self.aType = aType
        self.location = location
        self.anim_num = 0
        self.audio_key = 0
        self.moved = False

    def update(self, sprite_sheet):
        if not isinstance(self.aType, Element):
            update = self.aType.anim.getUpdate(
                self.aType.body, self.anim_num, self.aType.states[self.aType.current][0])
            if update:
                self.image = sprite_sheet.imageAt((
                    update[0], update[1], update[2], update[3])).convert()
                if self.aType.direction:
                    self.image = pygame.transform.flip(self.image, True, False)
                self.anim_num += 1

                if self.aType.current == "death" and self.anim_num >= self.aType.anim.animation.frames:
                    self.anim_num = self.aType.anim.animation.frames - 1

                elif self.anim_num >= self.aType.anim.animation.frames:
                    if not self.aType.anim.animation.repeatable:
                        self.revert()
                    self.anim_num = 0

        else:
            update = self.aType.anim.getUpdate(
                self.aType.body, self.anim_num, self.aType.states[self.aType.state][0] if self.aType.states != None else 0)
            if update:
                self.image = sprite_sheet.imageAt((
                    update[0], update[1], update[2], update[3])).convert()
            self.anim_num += 1
            if self.anim_num >= self.aType.anim.animation.frames:
                self.anim_num = 0

    def updateLocation(self, move=[], location=(), json=None):
        if len(move) != 0:
            self.location = updateVector(self.location, move)
            self.aType.bbox.update(move)
        else:
            self.location = location
            self.aType.resetBounds(json, location, self.aType.name)

    def revert(self, num=None):
        self.aType.set_state("idle")
        self.aType.in_action = False
        self.anim_num = 0
        if not num == None:
            pygame.mixer.Channel(num).stop()


class AssetPrototype(object):
    def __init__(self, image_xy, location, aType):
        self.image_xy = image_xy
        self.location = location
        self.aType = aType

    def convert(self, sprite_sheet):
        return Asset(sprite_sheet.imageAt((self.image_xy[0], self.image_xy[1], self.image_xy[2], self.image_xy[3])).convert(), self.aType, self.location)


class Level(object):
    def __init__(self, world, prototypes, elements, name, orientation, nextLevel, spawn_point, bboxes, loaded=False, assets=[], cleared=False):
        self.world = world
        self.name = name
        self.prototypes = prototypes
        self.elements = elements
        self.assets = assets
        self.orientation = orientation
        self.nextLevel = nextLevel
        self.loaded = loaded
        self.spawn_point = spawn_point
        self.bboxes = bboxes

    def load(self, sprite_sheet, player, json):
        conv_assets = []
        conv_assets.append(player)
        for prototype in self.prototypes:
            asset = prototype.convert(sprite_sheet)
            if not isinstance(asset.aType, Character):
                ma = json.entities["enemies"][asset.aType.name]["move"]
                if ma == "dirct":
                    asset.aType.moveAlgo = DirectPath(
                        asset.location, player.location, getLevelMaze(self.bboxes, asset.aType.mvs), asset.aType.mvs)
                if ma == "a1":
                    asset.aType.moveAlgo = A1(
                        asset.location, player.location, getLevelMaze(self.bboxes, asset.aType.mvs), asset.aType.mvs)
                if ma == "random":
                    asset.aType.moveAlgo = RandomMove(
                        asset.location, player.location, getLevelMaze(self.bboxes, asset.aType.mvs))
            conv_assets.append(asset)
        json_elements = json.getElementsFromJSON(sprite_sheet)
        for element in self.elements:
            element_asset = json_elements[element[1]]
            element_asset.location = element[0]
            element_asset.aType.updateBBox(element[0])
            conv_assets.append(element_asset)
        self.assets = conv_assets
        self.loaded = True

    def switchLevel(self, index, sprite_sheet, json):
        next = json.getLevelFromJSON(self.nextLevel[index], sprite_sheet)
        next.load(sprite_sheet, self.assets[0], json)
        return next


class BoundingBox(object):
    def __init__(self, bl, ur, hurt):
        self.bl = bl
        self.ur = ur
        self.hurtful = hurt

    def update(self, move):
        self.bl = updateVector(self.bl, move)
        self.ur = updateVector(self.ur, move)

    def checkCollison(self, enemy, move):
        new_bl = updateVector(self.bl, move)
        new_ur = updateVector(self.ur, move)
        collision = new_ur[0] >= enemy.bl[0] and new_bl[0] <= enemy.ur[0] and new_bl[1] >= enemy.ur[1] and new_ur[1] <= enemy.bl[1]
        return (collision, enemy)

    def checkEnviromentCollisions(self, boxes, move):
        new_bl = updateVector(self.bl, move)
        new_ur = updateVector(self.ur, move)
        collision = False
        box = None
        for box in boxes:
            if new_ur[0] >= box.bl[0] and new_bl[0] <= box.ur[0] and new_bl[1] >= box.ur[1] and new_ur[1] <= box.bl[1]:
                collision = True
                break

        return (collision, box if not box == None else "")


class Entity(object):
    def __init__(self, body, centroid, anim, health, dmg, mvs, range, direction, current, states, bbox, sound=None, in_action=False,  hit=False, hit_recovery=0.75):
        self.body = body
        self.centroid = centroid
        self.anim = anim
        self.health = health
        self.dmg = dmg
        self.mvs = mvs
        self.range = range
        self.direction = direction
        self.current = current
        self.states = states
        self.bbox = bbox
        self.hit = hit
        self.hit_recovery = hit_recovery

        self.idle = copy.deepcopy(self.anim)
        self.in_action = in_action
        self.sound = sound

        self.tod = 0
        self.toh = 0

    def set_state(self, state):
        self.current = state
        anima = self.states[self.current][1]
        self.anim = Animator(
            Animation(self.anim.animation.delimiter, anima[0], anima[1], anima[2]))
        if len(anima) == 4:
            self.sound = pygame.mixer.Sound(anima[3])
        else:
            self.sound = None

    def resetBounds(self, json, loc, name):
        self.bbox = json.getEntityBBoxFromJSON(
            updateVector(loc, self.centroid), name)

    def recieveHit(self, dmg):
        self.health -= dmg
        self.hit = True
        self.toh = time.time()

    def enableDmg(self):
        self.hit = False
        self.hit_recovery = 0.75
        self.toh = 0

    def flipPlayer(self, asset, json):
        self.direction = not self.direction
        if self.direction:
            asset.location = updateVector(
                asset.location, [-self.anim.animation.delimiter/4, 0])
            self.centroid[0] += self.anim.animation.delimiter/4

        else:
            asset.location = updateVector(
                asset.location, [self.anim.animation.delimiter/4, 0])
            self.centroid[0] -= self.anim.animation.delimiter/4
        return asset


class Character(Entity):
    def __init__(self,  body, centroid, anim, health, max_hp, mana, dmg, mvs, range, direction, current, states, bbox, in_action=False, hit=False, hit_recovery=0.75, money=0, is_alive=True, keys=0):
        self.max_hp = max_hp
        self.mana = mana
        self.money = money
        self.is_alive = is_alive
        self.fired = False
        self.keys = keys
        super().__init__(body, centroid, anim, health, dmg, mvs, range,
                         direction, current, states, bbox, in_action=False, hit=False, hit_recovery=0.75)

    def kill(self):
        self.is_alive = False
        self.set_state("death")
        self.tod = time.time() if self.tod == 0 else None


class Enemy(Entity):
    def __init__(self,  body, centroid, anim, health, dmg, mvs, range, direction, current, states, bbox, name, drop_chance, in_action=False,  hit=False, hit_recovery=0.75, timer=4, moveAlgo=None):
        self.name = name
        self.drop_chance = drop_chance
        self.timer = timer
        self.moveAlgo = moveAlgo

        self.bull_buff = 0
        self.bull_cd = 20

        super().__init__(body, centroid, anim, health, dmg, mvs, range,
                         direction, current, states, bbox, in_action=False, hit=False, hit_recovery=0.75)

    def kill(self):
        self.set_state("death")
        self.tod = time.time() if self.tod == 0 else self.tod


class Element(object):
    def __init__(self, body, type, amount, centroid, bbox, anim, states, dropped=False, state="default"):
        self.body = body
        self.default = copy.deepcopy(body)
        self.type = type
        self.amount = amount
        self.anim = anim
        self.states = states
        self.centroid = centroid
        self.bbox = bbox
        self.dropped = dropped
        self.state = state
        self.toi = 0
        self.ttl = 1.6

    def set_state(self, state, json):
        if not self.states == None:
            self.state = state
            anima = self.states[self.state][1]
            self.anim = Animator(
                Animation(self.anim.animation.delimiter, anima[0], anima[1], anima[2]))

    def updateBBox(self, location):
        self.bbox.ur[0] = location[0] + self.centroid[0]
        self.bbox.ur[1] = location[1] + self.centroid[1]
        self.bbox.bl[0] = location[0]
        self.bbox.bl[1] = location[1] + self.centroid[1]
