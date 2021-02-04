import pygame
import sys
import ctypes
import time

from Classes import *
from worldFunctions import *
from common import *


class PyGame(object):
    def __init__(self, width, height, fps):
        pygame.init()
        pygame.font.init()
        ctypes.windll.user32.SetProcessDPIAware()
        self.ad = AudioController('./static/sound/menu_music.wav')
        self.base_music_volume = 0.25
        self.base_sfx_volume = 0.4
        self.master_volume_multiplier = 1
        self.music_volume_multiplier = 1
        self.sfx_volume_multiplier = 1
        self.myfont = pygame.font.Font(
            './static/fonts/dogicapixelbold.ttf', 18)
        self.bigfont = pygame.font.Font(
            './static/fonts/dogicapixelbold.ttf', 38)
        self.text = [self.bigfont.render(
            "", True, (255, 255, 255), (0, 0, 0)), (0, 0)]
        self.resolution = (width, height)
        self.screen = pygame.display.set_mode(
            self.resolution, pygame.DOUBLEBUF)
        self.SpriteSheet = SpriteSheet(
            "./static/sprite_sheet/sprite_sheet.png", (2, 218, 216))
        self.UiSheet = SpriteSheet(
            "./static/sprite_sheet/ui_elements.png", (2, 218, 216))
        self.JSONs = JSON_base(
            "./elements/levels.json", "./elements/states.json", "./elements/entities.json", "./elements/bbs.json", "./elements/elements.json", "./elements/ui.json", "save.json")
        self.level = self.JSONs.getLevelFromJSON("spawn", self.SpriteSheet)
        
        self.user_selection = "mage"
        self.player = self.JSONs.getPlayerFromJSON(
            self.user_selection, self.level.spawn_point[3])
        self.elements = self.JSONs.getElementsFromJSON(self.SpriteSheet)
        self.coin = self.elements["coin"].image.copy()
        self.key = self.elements["key"].image.copy()
        self.fps = fps
        self.clock = pygame.time.Clock()
        self.movement = {"w": False, "d": False,
                         "s": False, "a": False, "dodge_que": False, "teleport": False}
        self.text_timer = [0, 4]

    def pre_run(self):
        running = True
        button_size = (256, 82, 28)
        self.master_volume_multiplier = self.JSONs.save["master"]
        self.sfx_volume_multiplier = self.JSONs.save["sfx"]
        self.music_volume_multiplier = self.JSONs.save["music"]
        self.ad.setMusicVolume(
            self.base_music_volume * self.master_volume_multiplier * self.music_volume_multiplier)
        self.ad.playLoop()
        while running:
            self.screen.fill((0, 0, 0))
            self.screen.blit(self.UiSheet.imageAt(
                self.JSONs.ui["menu_bg"]), (0, 60))

            self.screen.blit(pygame.transform.scale(self.UiSheet.imageAt(
                self.JSONs.ui["menu_buttons"]), (256, 400)), (192, 256))

            self.text = [self.bigfont.render(
                "CHASING SPRINGS", True, (255, 255, 255), (0, 0, 0)), (56, 12)]
            self.screen.blit(self.text[0], self.text[1])

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    self.quit_without_saving()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.quit_without_saving()

                left, wheel, right = pygame.mouse.get_pressed()
                (x, y) = pygame.mouse.get_pos()

                button = getMouseOverButton(x, y, 192, 256, button_size, 4)

                if left:
                    if button == 0:
                        running = False

                    elif button == 1:
                        self.settings()

                    elif button == 2:
                        pass

                    elif button == 3:
                        self.quit_with_saving()

            pygame.display.update()
            self.clock.tick(self.fps)
        
        self.level = self.JSONs.getLevelFromJSON("spawn", self.SpriteSheet)
        self.completed_levels = []
        self.where_player_moved = []
        if self.JSONs.save["status"]:
            self.load_from_save()
            self.screen.fill(pygame.Color("black"))
            self.text = [self.bigfont.render(
                "", True, (255, 255, 255), (0, 0, 0)), (0, 0)]
            time.sleep(0.2)
            self.ad.switchAudio('./static/sound/theme.wav')
            self.ad.setAssetChannels(
                self.level.assets, self.base_sfx_volume * self.master_volume_multiplier * self.sfx_volume_multiplier)
            self.run()
        else:
            self.character_selection()

    def character_selection(self):
        running = True
        button_size = (256, 82, 28)
        frame_size = (200, 304, 8)
        selected = ""
        frames = [self.JSONs.ui["unselected_frame"],
                  self.JSONs.ui["unselected_frame"], self.JSONs.ui["unselected_frame"]]
        while running:
            self.screen.fill((0, 0, 0))
            self.screen.blit(self.UiSheet.imageAt(
                self.JSONs.ui["menu_bg"]), (0, 60))

            self.screen.blit(pygame.transform.scale(self.UiSheet.imageAt(
                frames[0]), (240, 344)), (0, 130))

            self.screen.blit(pygame.transform.scale(self.UiSheet.imageAt(
                frames[1]), (240, 344)), (210, 130))

            self.screen.blit(pygame.transform.scale(self.UiSheet.imageAt(
                frames[2]), (240, 344)), (420, 130))

            self.screen.blit(pygame.transform.scale(self.UiSheet.imageAt(
                self.JSONs.ui["warrior"]), (170, 180)), (25, 200))

            self.screen.blit(pygame.transform.scale(self.UiSheet.imageAt(
                self.JSONs.ui["mage"]), (170, 180)), (235, 200))

            self.screen.blit(pygame.transform.scale(self.UiSheet.imageAt(
                self.JSONs.ui["archer"]), (170, 180)), (445, 200))

            self.screen.blit(pygame.transform.scale(self.UiSheet.imageAt(
                self.JSONs.ui["play_button"]), (256, 96)), (192, 460))

            self.screen.blit(pygame.transform.scale(self.UiSheet.imageAt(
                self.JSONs.ui["back_button"]), (256, 96)), (192, 560))

            self.text = [self.bigfont.render(
                "CHASING SPRINGS", True, (255, 255, 255), (0, 0, 0)), (56, 12)]
            self.screen.blit(self.text[0], self.text[1])

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    self.quit_without_saving()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.quit_without_saving()

                left, wheel, right = pygame.mouse.get_pressed()
                (x, y) = pygame.mouse.get_pos()

                frame = getMouseOverFrame(x, y, 0, 130, frame_size, 3)
                button = getMouseOverButton(x, y, 192, 460, button_size, 2)

                if left:
                    if button == 0 and not selected == "":
                        running = False

                    if button == 1:
                        self.pre_run()

                    if frame == 0:
                        frames[0] = self.JSONs.ui["selected_frame"]
                        selected = "warrior"
                        frames[1] = frames[2] = self.JSONs.ui["unselected_frame"]

                    if frame == 1:
                        frames[1] = self.JSONs.ui["selected_frame"]
                        selected = "mage"
                        frames[0] = frames[2] = self.JSONs.ui["unselected_frame"]

                    if frame == 2:
                        frames[2] = self.JSONs.ui["selected_frame"]
                        selected = "archer"
                        frames[0] = frames[1] = self.JSONs.ui["unselected_frame"]

            pygame.display.update()
            self.clock.tick(self.fps)

        self.user_selection = selected
        self.player = self.JSONs.getPlayerFromJSON(
            self.user_selection, self.level.spawn_point[3])
        self.player.set_state("idle")
        time.sleep(0.2)
        self.screen.fill(pygame.Color("black"))
        self.text = [self.bigfont.render(
            "", True, (255, 255, 255), (0, 0, 0)), (0, 0)]
        time.sleep(0.2)
        self.ad.switchAudio('./static/sound/theme.wav')
        self.level.load(self.SpriteSheet, AssetPrototype(
            self.player.body, self.level.spawn_point[3], self.player).convert(self.SpriteSheet), self.JSONs)
        self.ad.setAssetChannels(
            self.level.assets, self.base_sfx_volume * self.master_volume_multiplier * self.sfx_volume_multiplier)
        self.run()

    def settings(self):
        running = True
        button_size = (256, 82, 28)
        slider_size = (50, 50)
        sliders = [{"min_x": 164, "x_diff": 272, "y": 164}, {
            "min_x": 164, "x_diff": 272, "y": 288}, {"min_x": 164, "x_diff": 272, "y": 410}]
        while running:
            self.screen.fill((0, 0, 0))
            self.screen.blit(self.UiSheet.imageAt(
                self.JSONs.ui["menu_bg"]), (0, 60))

            self.screen.blit(pygame.transform.scale(self.UiSheet.imageAt(
                self.JSONs.ui["volume_bars"]), (362, 368)), (144, 130))

            self.screen.blit(pygame.transform.scale(self.UiSheet.imageAt(
                self.JSONs.ui["back_button"]), (256, 96)), (192, 512))

            self.screen.blit(pygame.transform.scale(self.UiSheet.imageAt(
                self.JSONs.ui["slider"]), (54, 54)), (sliders[0]["min_x"] + sliders[0]["x_diff"] * self.master_volume_multiplier, sliders[0]["y"]))

            self.screen.blit(pygame.transform.scale(self.UiSheet.imageAt(
                self.JSONs.ui["slider"]), (54, 54)), (sliders[1]["min_x"] + sliders[1]["x_diff"] * self.sfx_volume_multiplier, sliders[1]["y"]))

            self.screen.blit(pygame.transform.scale(self.UiSheet.imageAt(
                self.JSONs.ui["slider"]), (54, 54)), (sliders[2]["min_x"] + sliders[2]["x_diff"] * self.music_volume_multiplier, sliders[2]["y"]))

            self.text = [self.bigfont.render(
                "CHASING SPRINGS", True, (255, 255, 255), (0, 0, 0)), (56, 12)]
            self.screen.blit(self.text[0], self.text[1])

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    self.quit_without_saving()

                left, wheel, right = pygame.mouse.get_pressed()
                (x, y) = pygame.mouse.get_pos()

                button = getMouseOverButton(x, y, 192, 512, button_size, 1)
                slider = getMouseOverSlider(x, y, [sliders[0]["min_x"] + sliders[0]["x_diff"] * self.master_volume_multiplier, sliders[1]["min_x"] + sliders[1]["x_diff"] *
                                                   self.sfx_volume_multiplier, sliders[2]["min_x"] + sliders[2]["x_diff"] * self.music_volume_multiplier], [sliders[0]["y"], sliders[1]["y"], sliders[2]["y"]], slider_size)

                if left:
                    if button == 0:
                        running = False

                    if slider == 0:
                        self.master_volume_multiplier = (
                            x - sliders[0]["min_x"] - slider_size[0]/2)/(sliders[0]["x_diff"])
                        if self.master_volume_multiplier < 0:
                            self.master_volume_multiplier = 0
                        elif self.master_volume_multiplier > 1:
                            self.master_volume_multiplier = 1
                        self.ad.setMusicVolume(
                            self.base_music_volume * self.master_volume_multiplier * self.music_volume_multiplier)

                    if slider == 1:
                        self.sfx_volume_multiplier = (
                            x - sliders[1]["min_x"] - slider_size[0]/2)/(sliders[1]["x_diff"])
                        if self.sfx_volume_multiplier < 0:
                            self.sfx_volume_multiplier = 0
                        elif self.sfx_volume_multiplier > 1:
                            self.sfx_volume_multiplier = 1
                        self.ad.setAssetChannels(
                            self.level.assets, self.base_sfx_volume * self.master_volume_multiplier * self.sfx_volume_multiplier)

                    if slider == 2:
                        self.music_volume_multiplier = (
                            x - sliders[2]["min_x"] - slider_size[0]/2)/(sliders[0]["x_diff"])
                        if self.music_volume_multiplier < 0:
                            self.music_volume_multiplier = 0
                        elif self.music_volume_multiplier > 1:
                            self.music_volume_multiplier = 1
                        self.ad.setMusicVolume(
                            self.base_music_volume * self.master_volume_multiplier * self.music_volume_multiplier)

            pygame.display.update()
            self.clock.tick(self.fps)

    def pause_menu(self):
        running = True
        pygame.mouse.set_cursor(*pygame.cursors.arrow)
        pygame.mouse.set_visible(True)
        button_size = (256, 82, 28)
        while running:

            self.screen.blit(self.level.world, (0, 0))
            for asset in self.level.assets[::-1]:
                if isinstance(asset.aType, Element):
                    if asset.aType.type == "arrow":
                        if time.time() - asset.aType.toi >= asset.aType.ttl:
                            self.level.assets.remove(asset)
                            self.player.fired = False
                        asset.location = getMovement(
                            asset.location, asset.aType.angle, 5.5)
                        if asset.location[1] <= 600:
                            self.screen.blit(pygame.transform.rotate(
                                asset.image, asset.aType.angle), asset.location)
                    elif asset.aType.type == "poison":
                        if time.time() - asset.aType.toi >= asset.aType.ttl:
                            self.level.assets.remove(asset)
                        self.screen.blit(asset.image, asset.location)
                    else:
                        self.screen.blit(asset.image, asset.location)
                else:
                    self.screen.blit(asset.image, asset.location)

            self.screen.blit(pygame.transform.scale(self.UiSheet.imageAt(
                self.JSONs.ui["pause_menu"]), (256, 400)), (192, 180))

            self.text = [self.bigfont.render(
                "Game Paused", True, (255, 255, 255), (0, 0, 0)), (112, 12)]
            self.screen.blit(self.text[0], self.text[1])

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    self.quit_without_saving()

                left, wheel, right = pygame.mouse.get_pressed()
                (x, y) = pygame.mouse.get_pos()

                button = getMouseOverButton(x, y, 192, 180, button_size, 4)

                if left:
                    if button == 0:
                        running = False

                    elif button == 1:
                        self.settings()

                    elif button == 2:
                        self.quit_with_saving()

                    elif button == 3:
                        self.ad.switchAudio('./static/sound/menu_music.wav')
                        data = {"status": False, "health": 0, "max_hp": 0, "mvs": 0, "dmg": 0,
                                "coins": 0, "keys": 0, "travel": [], "completed": [], "selection": "warrior",
                                "upgrades": [], "music": self.music_volume_multiplier, "sfx": self.sfx_volume_multiplier, "master": self.master_volume_multiplier}
                        with open('save.json', 'w') as fp:
                            json.dump(data, fp)
                        self.pre_run()

            pygame.display.update()
            self.clock.tick(self.fps)

        self.text = [self.bigfont.render(
            "", True, (255, 255, 255), (0, 0, 0)), (0, 0)]
        pygame.mouse.set_cursor(*pygame.cursors.diamond)
        if not self.user_selection == "archer":
            pygame.mouse.set_visible(False)

    def run(self):
        running = True
        pygame.mouse.set_cursor(*pygame.cursors.diamond)
        if not self.user_selection == "archer":
            pygame.mouse.set_visible(False)
        while running:
            self.screen.fill((0, 0, 0))

            for asset in self.level.assets:

                if isinstance(asset.aType, Character) and self.player.is_alive:

                    for event in pygame.event.get():

                        if event.type == pygame.QUIT:
                            self.quit_without_saving()

                        elif event.type == pygame.KEYUP and not self.player.current == "teleport" and not self.player.current == "dodge":
                            if event.key == pygame.K_w:
                                self.movement["w"] = False

                            if event.key == pygame.K_d:
                                self.movement["d"] = False

                            if event.key == pygame.K_s:
                                self.movement["s"] = False

                            if event.key == pygame.K_a:
                                self.movement["a"] = False

                            if not self.player.in_action and not any(list(self.movement.values())[0:4]):
                                asset.revert()

                        elif event.type == pygame.KEYDOWN and not self.player.current == "teleport":
                            if event.key == pygame.K_w:
                                self.movement["w"] = True
                                self.movement["s"] = False

                            if event.key == pygame.K_d:
                                self.movement["d"] = True
                                self.movement["a"] = False
                                if self.player.direction:
                                    asset = self.player.flipPlayer(
                                        asset, self.JSONs)

                            if event.key == pygame.K_s:
                                self.movement["s"] = True
                                self.movement["w"] = False

                            if event.key == pygame.K_a:
                                self.movement["a"] = True
                                self.movement["d"] = False
                                if not self.player.direction:
                                    asset = self.player.flipPlayer(
                                        asset, self.JSONs)

                            if event.key == pygame.K_LSHIFT and any((self.movement["w"], self.movement["a"], self.movement["s"], self.movement["d"])):
                                if not self.player.in_action:
                                    if self.user_selection != "mage":
                                        asset.revert()
                                        self.player.set_state("dodge")
                                        self.movement["dodge_que"] = False
                                    else:
                                        asset.revert()
                                        self.player.set_state("teleport")
                                        self.movement["teleport"] = True

                                else:
                                    self.movement["dodge_que"] = True

                            if event.key == pygame.K_ESCAPE:
                                self.pause_menu()

                    keys = pygame.key.get_pressed()

                    if not any((keys[pygame.K_w], keys[pygame.K_a], keys[pygame.K_s], keys[pygame.K_d])) and not self.player.current == "teleport" and not self.player.current == "dodge":
                        self.movement["w"] = False
                        self.movement["a"] = False
                        self.movement["s"] = False
                        self.movement["d"] = False
                        self.movement["dodge_que"] = False

                left, wheel, right = pygame.mouse.get_pressed()
                (mx, my) = pygame.mouse.get_pos()

                player_loc = getLocation(self.level.assets[0])

                enemy_loc = None
                if isinstance(asset.aType, Enemy):
                    enemy_loc = getLocation(asset)

                if isinstance(asset.aType, Character) and self.player.is_alive:

                    if not self.player.current == "teleport" and self.movement["teleport"] and not self.player.in_action:
                        self.movement["teleport"] = False
                        if keys[pygame.K_w]:
                            self.movement["w"] = True
                        else:
                            self.movement["w"] = False
                        if keys[pygame.K_a]:
                            self.movement["a"] = True
                            if not self.player.direction:
                                asset = self.player.flipPlayer(
                                    asset, self.JSONs)
                        else:
                            self.movement["a"] = False
                        if keys[pygame.K_s]:
                            self.movement["s"] = True
                        else:
                            self.movement["s"] = False
                        if keys[pygame.K_d]:
                            self.movement["d"] = True
                            if self.player.direction:
                                asset = self.player.flipPlayer(
                                    asset, self.JSONs)
                        else:
                            self.movement["d"] = False

                    if left and not self.player.in_action and not self.player.current == "dodge" and not self.player.current == "teleport" and not self.player.fired:
                        asset.revert(0)
                        self.player.set_state("attack")
                        self.player.in_action = True
                        if not self.player.sound == None:
                            self.ad.playSound(
                                asset.audio_key, asset.aType.sound)

                    conditions = playerCanMove(
                        asset.aType, self.movement, self.player.mvs, self.level.orientation, any([x.aType.current != "death" for x in self.level.assets if isinstance(x.aType, Enemy)]))

                    if self.user_selection == "archer" and self.player.current == "attack" and not self.player.fired:
                        arrow = copy.deepcopy(self.elements["arrow"].aType)
                        arrow_asset = Asset(self.SpriteSheet.imageAt(arrow.body).convert(
                        ), arrow, updateVector(self.level.assets[0].location, self.player.centroid))
                        if arrow.toi == 0:
                            arrow.toi = time.time()
                            arrow.angle = angle_between(
                                arrow_asset.location, (mx, my))
                        self.level.assets.append(arrow_asset)
                        self.player.fired = True

                    if any(list(self.movement.values())) and not self.player.in_action:
                        if self.movement["dodge_que"]:
                            asset.revert()
                            if not self.user_selection == "mage":
                                self.player.set_state("dodge")
                            else:
                                self.player.set_state("teleport")
                                self.movement["teleport"] = True
                            self.movement["dodge_que"] = False
                        move = getPlayerMovement(
                            self.movement, conditions, self.player.mvs)
                        collision, collision_dmg = self.player.bbox.checkEnviromentCollisions(
                            self.level.bboxes, move)
                        c_collision = False

                        for object in closeEnoughAssets(player_loc, self.level.assets[1:], 125):
                            if not isinstance(object.aType, Element):
                                if not object.aType.current == "death" and not self.player.current == "teleport" and not object.aType.name == "worm":
                                    e_collision, e_collision_block = self.player.bbox.checkCollison(
                                        object.aType.bbox, move)
                                    if e_collision:
                                        collision_dmg = e_collision_block
                                        collision = e_collision

                            else:
                                if object.aType.type == "merchant":
                                    if self.player.money >= object.aType.amount:
                                        object.aType.set_state(
                                            "default", self.JSONs)
                                    elif self.player.money < object.aType.amount:
                                        object.aType.set_state(
                                            "not_selling", self.JSONs)
                                c_collision, _ = self.player.bbox.checkCollison(
                                    object.aType.bbox, move)
                                if c_collision:
                                    if object.aType.type == "coin":
                                        self.player.money += object.aType.amount
                                        self.level.assets.remove(object)
                                    elif object.aType.type == "key":
                                        self.player.keys += object.aType.amount
                                        self.level.assets.remove(object)
                                    elif object.aType.type == "normal_chest":
                                        if object.aType.state == "default":
                                            self.player.money += object.aType.amount
                                            object.aType.set_state(
                                                "opened", self.JSONs)
                                    elif object.aType.type == "locked_chest":
                                        if object.aType.state == "default" and self.player.keys > 0:
                                            self.player.keys -= 1
                                            self.player.money += object.aType.amount
                                            object.aType.set_state(
                                                "opened", self.JSONs)
                                            self.get_random_upgrade()
                                    elif object.aType.type == "merchant":
                                        if object.aType.state == "default" and self.text_timer[0] == 0:
                                            self.player.money -= object.aType.amount
                                            self.get_random_upgrade()
                                    elif object.aType.type == "poison":
                                        if not self.player.hit and not self.player.current == "dodge" and not self.player.current == "teleport":
                                            self.player.recieveHit(
                                                object.aType.amount)
                                            if self.player.health <= 0:
                                                asset.revert()
                                                self.player.kill()
                                                self.trigger_game_over()

                        if not collision:
                            if not self.player.current == "dodge" and not self.player.current == "move" and not self.player.current == "teleport" and self.player.is_alive:
                                asset.revert()
                                self.player.set_state("move")
                            if not self.player.sound == None:
                                self.ad.playSound(
                                    asset.audio_key, asset.aType.sound)

                            asset.updateLocation(move=move)

                        elif collision and not self.player.hit and self.player.current == "move":
                            asset.revert()
                            asset.aType.recieveHit(collision_dmg.hurtful)
                            if self.player.health <= 0:
                                asset.revert()
                                self.player.kill()
                                self.trigger_game_over()

                    if isinstance(conditions[1], int):
                        if self.level.name not in self.completed_levels and self.level.name != "merchant":
                            self.completed_levels.append(self.level.name)
                        self.where_player_moved.append(conditions[1])
                        self.level.assets = [self.level.assets[0]]
                        self.level = self.level.switchLevel(
                            conditions[1], self.SpriteSheet, self.JSONs)
                        if self.level.name == "merchant":
                            self.ad.switchAudio('./static/sound/merchant.wav')
                        else:
                            self.ad.switchAudio('./static/sound/theme.wav')
                        if self.level.name in self.completed_levels:
                            self.level.assets = [self.level.assets[0]]
                        asset.location = self.level.spawn_point[conditions[1]]
                        asset.aType.resetBounds(
                            self.JSONs, asset.location, self.user_selection)
                        self.ad.setAssetChannels(
                            self.level.assets, self.base_sfx_volume * self.master_volume_multiplier * self.sfx_volume_multiplier)

                    elif not any([x.aType.current != "death" for x in self.level.assets if isinstance(x.aType, Enemy)]):
                        if self.level.name not in self.completed_levels and self.level.name != "merchant":
                            self.completed_levels.append(self.level.name)

                elif isinstance(asset.aType, Enemy) and self.player.is_alive:
                    enemy_to_player_dist = 10000
                    if not enemy_loc is None:
                        enemy_to_player_dist = distBetweenLocations(
                            player_loc, enemy_loc)

                    if not asset.aType.name == "BULL":

                        if not asset.aType.current == "death":
                            for element in self.level.assets:
                                if isinstance(element.aType, Element) and element.aType.type == "arrow":
                                    detection = asset.aType.bbox.bl[0] <= element.location[0] <= asset.aType.bbox.ur[
                                        0] and asset.aType.bbox.ur[1] <= element.location[1] <= asset.aType.bbox.bl[1]
                                    if detection and not asset.aType.hit:
                                        asset.aType.recieveHit(self.player.dmg)
                                        if asset.aType.health <= 0:
                                            asset.revert()
                                            asset.aType.kill()
                                            if getDropChance() <= asset.aType.drop_chance:
                                                if getDropChance() <= asset.aType.drop_chance/4:
                                                    coin = copy.deepcopy(
                                                        self.elements["shiny_coin"].aType)
                                                else:
                                                    coin = copy.deepcopy(
                                                        self.elements["coin"].aType)
                                                coin_asset = Asset(self.SpriteSheet.imageAt(coin.body).convert(
                                                ), coin, updateVector(enemy_loc, [-coin.centroid[0], -coin.centroid[1]]))
                                                self.level.assets.append(
                                                    coin_asset)
                                                coin_asset.aType.updateBBox(
                                                    coin_asset.location)

                            if self.player.current == "attack" and self.player.anim.animation.frames * 0.40 <= self.level.assets[0].anim_num <= self.player.anim.animation.frames * 0.80:
                                if registerHit(asset, self.level.assets[0]) and not asset.aType.hit:
                                    asset.aType.recieveHit(self.player.dmg)
                                    if asset.aType.health <= 0:
                                        asset.revert()
                                        asset.aType.kill()
                                        if getDropChance() <= asset.aType.drop_chance:
                                            if getDropChance() <= asset.aType.drop_chance/4:
                                                coin = copy.deepcopy(
                                                    self.elements["shiny_coin"].aType)
                                            else:
                                                coin = copy.deepcopy(
                                                    self.elements["coin"].aType)
                                            coin_asset = Asset(self.SpriteSheet.imageAt(coin.body).convert(
                                            ), coin, updateVector(enemy_loc, [-coin.centroid[0], -coin.centroid[1]]))
                                            self.level.assets.append(
                                                coin_asset)
                                            coin_asset.aType.updateBBox(
                                                coin_asset.location)

                            if asset.aType.current == "attack" and asset.aType.anim.animation.frames * 0.40 <= asset.anim_num <= asset.aType.anim.animation.frames * 0.80:
                                if registerHit(self.level.assets[0], asset) and not self.player.hit and not self.player.current == "dodge" and not self.player.current == "teleport":
                                    self.player.recieveHit(asset.aType.dmg)
                                    if self.player.health <= 0:
                                        self.level.assets[0].revert()
                                        self.player.kill()
                                        self.trigger_game_over()

                            if (enemy_to_player_dist <= 300 or not isinstance(asset.aType.moveAlgo, DirectPath)) and not asset.aType.current == "death":
                                if enemy_to_player_dist <= asset.aType.range:
                                    if not asset.aType.current == "attack" and not asset.aType.name == "worm":
                                        asset.revert()
                                        asset.aType.set_state("attack")
                                        if not asset.aType.sound == None:
                                            self.ad.playSound(
                                                asset.audio_key, asset.aType.sound)

                                elif not asset.aType.current == "attack":
                                    if not asset.aType.name == "worm":
                                        if not asset.aType.current == "move":
                                            asset.revert()
                                            asset.aType.set_state("move")
                                        if asset.aType.name == "cobra":
                                            asset.aType.moveAlgo.update(
                                                enemy_loc, player_loc)
                                        else:
                                            asset.aType.moveAlgo.update(
                                                asset.location, player_loc)
                                        move, algo = asset.aType.moveAlgo.get_move()
                                        collision = asset.aType.bbox.checkEnviromentCollisions(
                                            self.level.bboxes,  move)[0]
                                        e_collision = asset.aType.bbox.checkCollison(
                                            self.player.bbox, move)[0]
                                        collision = collision or e_collision

                                        if not collision:
                                            if not algo:
                                                asset.updateLocation(move=move)
                                            else:
                                                asset.updateLocation(
                                                    location=move, json=self.JSONs)
                                            new_direction = getEnemyDirection(
                                                player_loc, enemy_loc)
                                            if asset.aType.direction != new_direction:
                                                asset = asset.aType.flipPlayer(
                                                    asset, self.JSONs)
                                                asset.aType.direction = new_direction

                                    elif asset.aType.name == "worm":
                                        if asset.anim_num == 0 and not asset.moved:
                                            move, algo = asset.aType.moveAlgo.get_move()
                                            asset.updateLocation(
                                                location=move, json=self.JSONs)
                                            asset.moved = True
                                            poison = copy.deepcopy(
                                                self.elements["poison"].aType)
                                            poison_asset = Asset(self.SpriteSheet.imageAt(poison.body).convert(
                                            ), poison, updateVector(asset.location, [0, asset.aType.centroid[1] * 2]))
                                            if poison.toi == 0:
                                                poison.toi = time.time()
                                                poison.ttl = 7
                                            poison_asset.aType.updateBBox(
                                                poison_asset.location)
                                            self.level.assets.append(
                                                poison_asset)
                                        elif asset.anim_num > 0:
                                            asset.moved = False

                            elif not asset.aType.current == "idle" and not asset.aType.current == "death":
                                asset.revert()

                        elif asset.aType.current == "death":
                            if time.time() - asset.aType.tod >= asset.aType.timer and asset in self.level.assets:
                                self.level.assets.remove(asset)

                    elif asset.aType.name == "BULL":

                        if not asset.aType.current == "death":
                            for element in self.level.assets:
                                if isinstance(element.aType, Element) and element.aType.type == "arrow":
                                    detection = asset.aType.bbox.bl[0] <= element.location[0] <= asset.aType.bbox.ur[
                                        0] and asset.aType.bbox.ur[1] <= element.location[1] <= asset.aType.bbox.bl[1]
                                    if detection and not asset.aType.hit:
                                        asset.aType.recieveHit(self.player.dmg)
                                        if asset.aType.health <= 0:
                                            asset.revert()
                                            asset.aType.kill()
                                            self.trigger_victory()

                            if self.player.current == "attack" and self.player.anim.animation.frames * 0.40 <= self.level.assets[0].anim_num <= self.player.anim.animation.frames * 0.80:
                                if registerHit(asset, self.level.assets[0]) and not asset.aType.hit:
                                    asset.aType.recieveHit(self.player.dmg)
                                    if asset.aType.health <= 0:
                                        asset.revert()
                                        asset.aType.kill()
                                        self.trigger_victory()

                            if asset.aType.current == "attack" and asset.aType.anim.animation.frames * 0.40 <= asset.anim_num <= asset.aType.anim.animation.frames * 0.80:
                                if registerHit(self.level.assets[0], asset) and not self.player.hit and not self.player.current == "dodge" and not self.player.current == "teleport":
                                    self.player.recieveHit(asset.aType.dmg)
                                    if self.player.health <= 0:
                                        self.level.assets[0].revert()
                                        self.player.kill()
                                        self.trigger_game_over()

                            if not asset.aType.current == "death":
                                if enemy_to_player_dist <= asset.aType.range:
                                    if not asset.aType.current == "attack":
                                        asset.revert()
                                        asset.aType.set_state("attack")
                                        if not asset.aType.sound == None:
                                            self.ad.playSound(
                                                asset.audio_key, asset.aType.sound)

                                value = getDropChance()
                                if value <= 0.07 and not asset.aType.current == "attack" and asset.aType.bull_buff == 0:
                                    asset.revert()
                                    asset.aType.set_state("buff")
                                    asset.aType.dmg += asset.aType.dmg * 0.1
                                    asset.aType.health += asset.aType.health * 0.2
                                    asset.aType.bull_buff = time.time()

                                if time.time() - asset.aType.bull_buff >= asset.aType.bull_cd:
                                    asset.aType.bull_buff = 0

                                elif not asset.aType.current == "attack" and not asset.aType.current == "buff":
                                    if not asset.aType.current == "move":
                                        asset.revert()
                                        asset.aType.set_state("move")
                                    asset.aType.moveAlgo.update(
                                        asset.location, player_loc)
                                    move, _ = asset.aType.moveAlgo.get_move()
                                    asset.updateLocation(
                                        location=move, json=self.JSONs)
                                    new_direction = getEnemyDirection(
                                        player_loc, enemy_loc)
                                    if asset.aType.direction != new_direction:
                                        asset = asset.aType.flipPlayer(
                                            asset, self.JSONs)
                                        asset.aType.direction = new_direction

                        elif self.elements["Water"] not in self.level.assets:
                            self.elements["Water"].location = [100, 500]
                            self.level.assets.append(self.elements["Water"])

                if not isinstance(asset.aType, Element) and asset.aType.hit:
                    asset.image.set_colorkey((190, 0, 0))
                    asset.image.fill((190, 0, 0))
                    if time.time() - asset.aType.toh >= asset.aType.hit_recovery and asset.aType.hit:
                        asset.aType.enableDmg()

                asset.update(self.SpriteSheet)
                pygame.draw.rect(self.screen, (210, 210, 218),
                                 (30, 650, 320, 40))
                health = self.player.health/self.player.max_hp if self.player.health / \
                    self.player.max_hp > 0 else 0
                pygame.draw.rect(self.screen, (255, 57, 46), (35, 655,
                                                              310*(health), 30))
                self.screen.blit(self.coin, (380, 620))
                textsurface = self.myfont.render(
                    str(self.player.money) + "$", True, (255, 255, 255), (0, 0, 0))
                self.screen.blit(textsurface, (420, 660))
                self.screen.blit(self.key, (475, 620))
                textsurface = self.myfont.render(
                    str(self.player.keys), True, (255, 255, 255), (0, 0, 0))
                self.screen.blit(textsurface, (540, 660))

            self.screen.blit(self.level.world, (0, 0))
            for asset in self.level.assets[::-1]:
                if isinstance(asset.aType, Element):
                    if asset.aType.type == "arrow":
                        if time.time() - asset.aType.toi >= asset.aType.ttl:
                            self.level.assets.remove(asset)
                            self.player.fired = False
                        asset.location = getMovement(
                            asset.location, asset.aType.angle, 5.5)
                        if asset.location[1] <= 600:
                            self.screen.blit(pygame.transform.rotate(
                                asset.image, asset.aType.angle), asset.location)
                    elif asset.aType.type == "poison":
                        if time.time() - asset.aType.toi >= asset.aType.ttl:
                            self.level.assets.remove(asset)
                        self.screen.blit(asset.image, asset.location)
                    else:
                        self.screen.blit(asset.image, asset.location)
                else:
                    self.screen.blit(asset.image, asset.location)
            if time.time() - self.text_timer[0] >= self.text_timer[1] and self.text_timer[0] != 0:
                self.text_timer[0] = 0
                self.text = [self.myfont.render(
                    "", True, (255, 255, 255), (0, 0, 0, 255)), (166, 300)]
            self.screen.blit(self.text[0], self.text[1])
            # self.screen.fill((255, 0, 0), (self.player.bbox.bl, (2, 2)))
            # self.screen.fill((0, 0, 255), (self.player.bbox.ur, (2, 2)))
            self.level.assets[0].aType.resetBounds(
                self.JSONs, self.level.assets[0].location, self.user_selection)
            if not self.player.is_alive and time.time() - self.player.tod >= 5:
                self.text = [self.bigfont.render(
                    "", True, (255, 255, 255), (0, 0, 0, 255)), (166, 300)]
                self.ad.switchAudio('./static/sound/menu_music.wav')
                pygame.mouse.set_cursor(*pygame.cursors.arrow)
                pygame.mouse.set_visible(True)
                self.pre_run()
            pygame.display.update()
            self.clock.tick(self.fps)

    def get_random_upgrade(self):
        value = getDropChance()
        self.text_timer[0] = time.time()
        if 0 <= value <= 0.4:
            self.text = [self.myfont.render(
                "Got 25% health upgrade!", True, (255, 255, 255), (0, 0, 0, 255)), (20, 100)]
            new_hp = self.player.max_hp + self.player.max_hp * 0.25
            diff = new_hp - self.player.max_hp
            self.player.max_hp = new_hp
            self.player.health += diff
        elif 0.4 < value <= 0.75:
            self.text = [self.myfont.render(
                "Got 20% movement speed upgrade!", True, (255, 255, 255), (0, 0, 0, 255)), (20, 100)]
            self.player.mvs += self.player.mvs * 0.2
        elif 0.75 < value <= 1:
            self.text = [self.myfont.render(
                "Got 15% damage upgrade!", True, (255, 255, 255), (0, 0, 0, 255)), (20, 100)]
            self.player.dmg += self.player.dmg * 0.15

    def trigger_game_over(self):
        self.text = [self.bigfont.render(
            "GAME OVER", True, (255, 255, 255), (0, 0, 0, 255)), (166, 300)]

    def trigger_victory(self):
        self.text = [self.myfont.render(
            "VICTORY!! ...but is it...", True, (255, 255, 255), (0, 0, 0, 255)), (166, 300)]
        self.player.kill()

    def quit_without_saving(self):
        data = {"status": False, "health": 0, "max_hp": 0, "mvs": 0, "dmg": 0,
                "coins": 0, "keys": 0, "travel": [], "completed": [], "selection": "warrior",
                "upgrades": [], "music": self.music_volume_multiplier, "sfx": self.sfx_volume_multiplier, "master": self.master_volume_multiplier}
        with open('save.json', 'w') as fp:
            json.dump(data, fp)
        pygame.quit()

    def quit_with_saving(self):
        self.save()
        pygame.quit()

    def save(self):
        data = {"status": True, "health": self.player.health, "max_hp": self.player.max_hp, "mvs": self.player.mvs, "dmg": self.player.dmg, "coins": self.player.money, "keys": self.player.keys,
                "travel": self.where_player_moved, "completed": self.completed_levels, "selection": self.user_selection,
                "upgrades": [], "music": self.music_volume_multiplier, "sfx": self.sfx_volume_multiplier, "master": self.master_volume_multiplier}
        with open('save.json', 'w') as fp:
            json.dump(data, fp)

    def load_from_save(self):
        self.JSONs.save = self.JSONs.readFromFile("save.json")
        self.user_selection = self.JSONs.save["selection"]
        self.player = self.JSONs.getPlayerFromJSON(
            self.user_selection, self.level.spawn_point[3])
        self.completed_levels = self.JSONs.save["completed"]
        self.player.health = self.JSONs.save["health"]
        self.player.max_hp = self.JSONs.save["max_hp"]
        self.player.mvs = self.JSONs.save["mvs"]
        self.player.dmg = self.JSONs.save["dmg"]
        self.player.money = self.JSONs.save["coins"]
        self.player.keys = self.JSONs.save["keys"]
        self.level.load(self.SpriteSheet, AssetPrototype(
            self.player.body, self.level.spawn_point[3], self.player).convert(self.SpriteSheet), self.JSONs)
        for pt in self.JSONs.save["travel"]:
            self.where_player_moved.append(pt)
            self.level = self.level.switchLevel(
                pt, self.SpriteSheet, self.JSONs)
            if self.level.name == "merchant":
                self.ad.switchAudio('./static/sound/merchant.wav')
            else:
                self.ad.switchAudio('./static/sound/theme.wav')
            if self.level.name in self.completed_levels:
                self.level.assets = [self.level.assets[0]]
            self.level.assets[0].location = self.level.spawn_point[pt]
            self.level.assets[0].aType.resetBounds(
                self.JSONs, self.level.assets[0].location, self.user_selection)
            self.ad.setAssetChannels(
                self.level.assets, self.base_sfx_volume * self.master_volume_multiplier * self.sfx_volume_multiplier)


PyGame(640, 700, 60).pre_run()
