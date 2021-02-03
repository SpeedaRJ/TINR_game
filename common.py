import time
import pygame
import heapq
import copy
import random

from worldFunctions import *

# Ideja je da se lahko ta razred uporablja za vse igre, ki imajo sprite_sheet sestavljen na
#   tak način da si slike sledijo v zaporedju


class Animator(object):
    def __init__(self, animation):
        self.animation = animation
        self.start_time = time.time()
        self.stop_time = 0

    def getUpdate(self, body, num, state):
        self.stop_time = time.time()
        if self.stop_time - self.start_time >= self.animation.tpf:
            self.start_time = time.time()
            self.stop_time = 0
            return (body[0] + self.animation.delimiter * num, body[1] + state, body[2], body[3])
        else:
            return False


class Animation(object):
    def __init__(self, delimiter, frames, time, repeatable):
        self.frames = frames
        self.time = time
        self.delimiter = delimiter
        self.repeatable = repeatable
        self.tpf = self.time/self.frames


# Ideja tega razreda je da ga lahko uporabi katerakoli igrica napisana v pygame knjižnjici,
#   vse kar razred potrebuje je seznam objektov ki so v sceni, vsakemu pripne njegov zvočni ključ,
#   z samimi objekti pa ne operira in ne potrebuje znanje o nobenih njihovih lasnostih
class AudioController(object):
    def __init__(self, audio):
        pygame.mixer.music.load(audio)
        self.channels = []

    def playLoop(self):
        pygame.mixer.music.play(-1)

    def setMusicVolume(self, volume):
        pygame.mixer.music.set_volume(volume)

    def switchAudio(self, audio):
        pygame.mixer.music.stop()
        pygame.mixer.music.load(audio)
        self.playLoop()

    def setAssetChannels(self, assets, volume):
        self.channels = []
        for x in range(len(assets)):
            self.channels.append(pygame.mixer.Channel(x))
            assets[x].audio_key = x
            pygame.mixer.Channel(x).set_volume(volume)

    def setChannelVolume(self, id, volume):
        pygame.mixer.Channel(id).set_volume(volume)

    def playSound(self, id, audio):
        if not pygame.mixer.Channel(id).get_busy():
            pygame.mixer.Channel(id).stop()
            pygame.mixer.Channel(id).play(audio)

# Naslednji sklop razredov služi kontroli premikanja nasprotnikov. Glavni razred služi hranjenju ciljne lokacije
#   in začetne lokacije, nato pa posamezni podrazredi služijo kot različni algoritmi za računanje
#   poti, ki jo bo nasprotnik obral. Te so direktna pot, a* algoritem (ne najbolj optimalen), in naključno premikanje.


class MovementController(object):
    def __init__(self, location, target_location, maze):
        self.location = tuple([int(x) for x in location])
        self.target_location = tuple([int(x) for x in target_location])
        self.maze = maze

    def update(self, location, target_location):
        self.location = tuple([int(x) for x in location])
        self.target_location = tuple([int(x) for x in target_location])


class DirectPath(MovementController):
    def __init__(self, location, target_location, maze, move):
        super().__init__(location, target_location, maze)
        self.move = move

    def get_move(self):
        move = [0, 0]
        margin = 8
        vertical_dist = abs(self.target_location[1] - self.location[1])
        horizontal_dist = abs(self.target_location[0] - self.location[0])
        if self.location[0] < self.target_location[0] and horizontal_dist > margin:
            move[0] = self.move
        elif self.location[0] > self.target_location[0] and horizontal_dist > margin:
            move[0] = -self.move
        if self.location[1] < self.target_location[1] and vertical_dist > margin:
            move[1] = self.move
        elif self.location[1] > self.target_location[1] and vertical_dist > margin:
            move[1] = -self.move
        if all(move):
            cdf = getPitagoraCoeffiecinet(self.move)
            move[0] = move[0]*self.move/cdf
            move[1] = move[1]*self.move/cdf
        return (move, False)


class Node(object):
    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = tuple(position)

        self.g = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position

    def __lt__(self, other):
        return self.f + self.g < other.f + other.g

    def __gt__(self, other):
        return self.f + self.g > other.f + other.g

    def __hash__(self):
        return hash((int(self.position[0]), int(self.position[1])))


class A1(MovementController):
    def __init__(self, location, target_location, maze, move):
        super().__init__(location, target_location, maze)
        self.start = copy.deepcopy(location)
        self.move = move
        self.series = []

    def heuristic(self, pos):
        return self.maze[pos[0]][pos[1]]

    def astar(self):
        open, closed, nodes = [], set(), {}
        start = Node(position=self.location)
        end = Node(position=self.target_location)
        moves = ((-1, 0), (1, 0), (0, -1), (0, 1),
                 (1, 1), (-1, -1), (-1, 1), (1, -1))
        current = Node(position=self.location)
        heapq.heappush(open, current)
        max_iters = 700
        iters = 0
        while open:
            current = heapq.heappop(open)

            if current == end or iters >= max_iters:
                path = []
                while current != start:
                    path.append(current.position)
                    current = current.parent
                return list(reversed(path))

            iters += 1

            closed.add(current)
            neighbours = []
            for move in moves:
                child = Node(current, updateVector(current.position, move))
                if not is_between(child.position[0], int(self.location[0]), int(self.target_location[0])) or not is_between(child.position[1], int(self.location[1]), int(self.target_location[1])):
                    continue
                if child not in nodes.keys():
                    nodes[child] = child
                    neighbours.append(nodes[child])

            for n in neighbours:
                g = current.g
                if n in open and g < n.g:
                    open.remove(n)
                if g < n.g and n in closed:
                    closed.remove(n)
                if n not in open and n not in closed:
                    n.g = g + self.heuristic(n.position)
                    n.f = n.g + distBetweenLocations(self.start, n.position)
                    n.parent = current
                    heapq.heappush(open, n)
                heapq.heapify(open)
        return "fuck"

    def update(self, location, target_location):
        if len(self.series) <= 1:
            self.location = tuple([int(x) for x in location])
            self.target_location = tuple([int(x) for x in target_location])
            self.start = copy.deepcopy(self.location)
            self.series = self.astar()

    def get_move(self):
        if len(self.series) > 1:
            new_loc = self.series.pop(0)
            self.location = new_loc
            return (new_loc, True)


class RandomMove(MovementController):
    def __init__(self, location, target_location, maze):
        super().__init__(location, target_location, maze)

    def get_move(self):
        x = random.randint(100, 540)
        y = random.randint(100, 540)
        if self.validate_move((x, y)):
            return ((x, y), True)
        else:
            return self.get_move()

    def validate_move(self, location):
        return self.maze[location[0]][location[1]] == 1