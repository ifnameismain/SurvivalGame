from hud import *
from entities import *
from map import Map
from camera import *
from wave import Wave
from icons import GrowingIcon
from menu import Menu
from abc import ABCMeta, abstractmethod


class BaseScreen(metaclass=ABCMeta):
    def __init__(self):
        self.next_state = None

    @abstractmethod
    def pre_switch(self, other):
        pass

    @abstractmethod
    def check_event(self, event):
        pass

    @abstractmethod
    def update(self):
        return self.next_state

    @abstractmethod
    def draw(self, surface):
        pass


class GameScreen(BaseScreen):
    def __init__(self):
        super().__init__()
        self.player = Player(0, 0)
        self.map = Map()
        self.hud = HUD()
        self.wave = Wave()
        self.exp_points = {}
        self.crosshair = Crosshair()
        self.camera = PlayerCamera()
        self.map.update_background(self.player.pos)
        self.notifications = []
        self.death_animations = []

    def pre_switch(self, upgrade):
        if upgrade not in [None, True]:
            self.player.register_upgrade(upgrade)
        self.next_state = None
        self.player.move_state = {control: False for control in self.player.controls.values()}
        pg.mouse.set_visible(False)

    def check_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.next_state = 'pause'
            elif event.key in self.player.controls.values():
                self.player.handle_key_press(event.key, True)
        elif event.type == pg.KEYUP:
            if event.key in self.player.controls.values():
                self.player.handle_key_press(event.key, False)

    def update(self):
        self.player.update(self.camera)
        self.wave.update(self.player.pos)
        delete_dict = {sector: [] for sector in self.wave.enemies.keys()}
        append_dict = {sector: [] for sector in self.wave.enemies.keys()}
        prev_lvl = self.player.stats['lvl']
        for sector, enemies in self.wave.enemies.items():
            for i, e in enumerate(enemies):
                e.update(self.player.pos, sector)
                e.calculate_status()
                if nots := e.notification:
                    for n in nots:
                        self.notifications.append([0.5, n])
                e.set_inflicted()
                if e.stats['hp'] <= 0 or (e.type == 'kamikaze' and not e.attack_ready):
                    if sector not in self.exp_points.keys():
                        self.exp_points[sector] = [ExpPoint(e.pos.x, e.pos.y, e.exp)]
                    else:
                        self.exp_points[sector].append(ExpPoint(e.pos.x, e.pos.y, e.exp))
                    self.death_animations.append([0, *e.death_animation])
                    delete_dict[sector].append(i)
                else:
                    if (sec := (int(e.pos.x//Config.CHUNK_SIZE), int(e.pos.y//Config.CHUNK_SIZE))) != sector:

                        if sec not in append_dict.keys():
                            append_dict[sec] = [e]
                        else:
                            append_dict[sec] = [e]
                        delete_dict[sector].append(i)
        for sector, indexs in delete_dict.items():
            for i in indexs[::-1]:
                self.wave.enemies[sector].pop(i)
        for sector, enemies in append_dict.items():
            for e in enemies[::-1]:
                if sector not in self.wave.enemies.keys():
                    self.wave.enemies[sector] = [e]
                else:
                    self.wave.enemies[sector].append(e)
        for sector in delete_dict.keys():
            if len(self.wave.enemies[sector]) == 0:
                self.wave.enemies.pop(sector)
        self.wave.converge()
        # self.player.stats['hp'] -= len(self.player.rect.collidelistall([e.rect for e in self.wave.enemies]))
        for sector in get_sector_range(tuple(self.player.sector)):
            for e in self.wave.enemies.get(sector, []):
                if self.player.mask.overlap(e.mask, (e.pos.x - self.player.pos.x, e.pos.y - self.player.pos.y)):
                    self.player.stats['hp'] -= e.dmg * Config.DT
                    e.attack_ready = False
            # probably add to delete dict
            for i, exp in enumerate(self.exp_points.get(sector, []).copy()[::-1]):
                if self.player.mask.overlap(exp.mask, (exp.pos.x - self.player.pos.x, exp.pos.y - self.player.pos.y)):
                    self.player.add_exp(exp.value)
                    self.exp_points[sector].pop(i)
        delete_list = []
        for i, bullet in enumerate(self.player.casts):
            if abs(bullet.pos.x - self.player.pos.x) > Config.WIDTH // 2 or \
                    abs(bullet.pos.y - self.player.pos.y) > Config.HEIGHT // 2:
                delete_list.append(i)
                continue
            elif bullet.state == bullet.final_state:
                self.player.casts.remove(bullet)
                continue
            for sector in get_sector_range(tuple(bullet.sector), *bullet.sector_range):
                for e in self.wave.enemies.get(sector, []):
                    if isinstance(bullet, Bullet):
                        if bullet.pos.distance_to(e.pos) < e.radius + bullet.radius:
                            e.add_dmg(bullet.get_dmg())
                            bullet.state = 1
                            break
                    elif isinstance(bullet, StatusBomb):
                        if bullet.state == 1:
                            if bullet.pos.distance_to(e.pos) < e.radius + bullet.radius:
                                e.add_dmg(bullet.get_dmg())
                    elif isinstance(bullet, Beam):
                        if bullet.state == 1:
                            if bullet.check_collision(self.camera.player_relative(e.pos.x, e.pos.y), e.radius):
                                e.add_dmg(bullet.get_dmg())
            if isinstance(bullet, StatusBomb):
                if bullet.dmg_tick > 0.5:
                    bullet.dmg_tick -= 0.5
        for i in delete_list[::-1]:
            self.player.casts.pop(i)
        if self.player.stats['lvl'] != prev_lvl:
            self.next_state = ['upgrade', self.player.stats['lvl'] - prev_lvl]
        self.hud.update(self.player.stats['hp'] / self.player.stats['max hp'],
                        self.player.exp_percentage, self.player.dash_status,
                        self.wave.num, self.player.attacks)
        self.crosshair.update()
        self.map.update_background(self.player.pos)
        if self.player.stats['hp'] <= 0:
            self.next_state = "main menu"
        return self.next_state

    def draw(self, surface):
        self.map.draw(surface)
        self.camera.update_player(self.player.pos.x, self.player.pos.y)
        self.camera.update_camera()
        self.player.draw_casts(surface, self.camera)
        for points in self.exp_points.values():
            for exp in points:
                if abs(self.player.pos.x - exp.pos.x) < Config.WIDTH // 2 and \
                        abs(self.player.pos.y - exp.pos.y) < Config.HEIGHT // 2:
                    exp.draw(surface, self.camera)
        for enemies in self.wave.enemies.values():
            for e in enemies:
                if e.drawable:
                    e.draw(surface, self.camera)
        self.player.draw(surface, self.camera)
        self.hud.draw(surface)
        self.crosshair.draw(surface)
        delete_list = []
        for i, notification in enumerate(self.notifications):
            if notification[0] <= 0:
                delete_list.append(i)
            else:
                surface.blit(notification[1][0], self.camera.object_pos(*notification[1][1]))
                notification[0] -= Config.DT
        for i in delete_list[::-1]:
            del self.notifications[i]
        finished_animations = []
        for count, (time, animation, pos, size) in enumerate(self.death_animations):
            t = int(60 * time)
            if t >= len(animation) - 1:
                finished_animations.append(count)
            else:
                surface.blit(animation[t], self.camera.object_pos(pos.x - size[0]//2, pos.y - size[0]//2))
                self.death_animations[count][0] += Config.DT
        finished_animations.reverse()
        for i in finished_animations:
            del self.death_animations[i]


class PauseScreen(BaseScreen):
    def __init__(self):
        super().__init__()
        self.screen = None
        self.drawn = False
        self.pause_text, self.pause_pos = centred_text("Paused", Config.FONTS['title'],
                                                       (Config.WIDTH // 2, Config.HEIGHT // 2 - 100),
                                                       (255, 248, 220))

    def pre_switch(self, other):
        self.next_state = None
        self.drawn = False
        pg.mouse.set_visible(True)

    def check_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.next_state = 'game'
        elif event.type == pg.KEYUP:
            pass

    def update(self):
        return self.next_state

    def draw(self, surface):
        if not self.drawn:
            surface.blit(self.pause_text, self.pause_pos)
            self.drawn = True


class UpgradeScreen(BaseScreen):
    def __init__(self):
        super().__init__()
        self.screen = None
        self.upgrade_cards = []
        self.lvl_amount = 0
        self.upgrade_text, self.upgrade_pos = centred_text("Choose Upgrade...", Config.FONTS['upgrade'],
                                                           (Config.WIDTH//2, 50), (255, 248, 220))
        self.chosen_cards = []

    def pre_switch(self, lvl_amount):
        self.next_state = None
        self.lvl_amount = lvl_amount
        self.get_upgrade_cards()
        pg.mouse.set_visible(True)

    def get_upgrade_cards(self):
        # do something here. probably random
        self.upgrade_cards = [UpgradeCard((x * Config.WIDTH//6) - UpgradeCard.width // 2, 100) for x in [2, 3, 4]]

    def check_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                x, y = get_mouse()
                for card in self.upgrade_cards:
                    if card.x < x < card.x + card.width and card.y < y < card.y + card.height:
                        self.lvl_amount -= 1
                        self.chosen_cards.append(card.info_key)
                        self.get_upgrade_cards()
                        if self.lvl_amount == 0:
                            self.next_state = ["game", self.chosen_cards]

    def update(self):
        return self.next_state

    def draw(self, surface):
        surface.blit(self.screen, (0, 0))
        for card in self.upgrade_cards:
            card.draw(surface)
        surface.blit(self.upgrade_text, self.upgrade_pos)


class SettingsScreen(BaseScreen):
    def __init__(self):
        super().__init__()
        self.title_card = create_card(400, 100, 10)
        self.title_text, self.title_pos = centred_text("Settings", Config.FONTS['upgrade'],
                                                       (Config.WIDTH // 2, 100), (255, 248, 220))
        self.menu = Menu(Config.WIDTH//2-400, 175, 800, 450, (255, 235, 205))
        self.game = None

    def pre_switch(self, game):
        self.next_state = None
        self.game = game
        pg.mouse.set_visible(True)

    def check_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.next_state = ['main menu', self.game]
            else:
                self.menu.check_event(event)
        elif event.type == pg.MOUSEWHEEL:
            self.menu.set_scroller_offset(- event.y)
        elif event.type == pg.MOUSEBUTTONDOWN:
            if event.button not in [4, 5]:
                self.menu.check_event(event)

    def update(self):
        self.game.update()
        return self.next_state

    def draw(self, surface):
        self.game.draw(surface)
        surface.blit(self.title_card, (Config.WIDTH//2-200, 50))
        surface.blit(self.title_text, self.title_pos)
        self.menu.draw(surface)


class MenuScreen(BaseScreen):
    def __init__(self):
        super().__init__()
        self.game = SimGame()
        self.title_card = create_card(600, 150, 15)
        self.title_text, self.title_pos = centred_text("Survival", Config.FONTS['title'],
                                                       (Config.WIDTH//2, 200), (255, 248, 220))
        self.space_text, self.space_pos = centred_text("Press Space to Start", Config.FONTS['upgrade'],
                                                       (Config.WIDTH // 2, 400), (255, 248, 220))
        self.fonts = {t: centred_text(t, Config.FONTS['upgrade'], (75, 25), (255, 255, 255), True) for t in ['Play', "Options"]}
        self.icons = [GrowingIcon(360, 400, 200, 50, Config.COLORS['poison'], self.fonts['Play']),
                      GrowingIcon(640, 400, 200, 50, Config.COLORS['slow'], self.fonts['Options'])]

    def pre_switch(self, game):
        self.next_state = None
        if game is None:
            self.game = SimGame()
        else:
            self.game = game
        pg.mouse.set_visible(True)

    def check_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                for i, icon in enumerate(self.icons):
                    if icon.is_hovered(*get_mouse()):
                        if i == 0:
                            self.next_state = ['game', True]
                        elif i == 1:
                            self.next_state = ['settings', self.game]

    def update(self):
        self.game.update()
        for icon in self.icons:
            icon.is_hovered(*get_mouse())
            icon.update()
        return self.next_state

    def draw(self, surface):
        self.game.draw(surface)
        surface.blit(self.title_card, (Config.WIDTH//2-300, 125))
        surface.blit(self.title_text, self.title_pos)
        for icon in self.icons:
            icon.draw(surface)


class SimGame(BaseScreen):
    def __init__(self):
        super().__init__()
        self.player = Player(0, 0)
        self.map = Map()
        self.wave = Wave()
        self.exp_points = []
        self.camera = PlayerCamera()
        self.map.update_background(self.player.pos)
        self.notifications = []

    def pre_switch(self, upgrade):
        if upgrade is not None:
            self.player.register_upgrade(upgrade)
        self.next_state = None
        self.player.move_state = {control: False for control in self.player.controls.values()}
        pg.mouse.set_visible(True)

    def check_event(self, event):
        pass

    def update(self):
        self.wave.update(self.player.pos)
        self.wave.converge()
        self.map.update_background(self.player.pos)
        if self.player.stats['hp'] <= 0:
            self.next_state = "main menu"
        return self.next_state

    def draw(self, surface):
        self.map.draw(surface)
        self.camera.update_player(self.player.pos.x, self.player.pos.y)
        self.camera.update_camera()
        for enemies in self.wave.enemies.values():
            for e in enemies:
                e.draw(surface, self.camera)
        self.player.draw(surface, self.camera)
        for notification in self.notifications.copy():
            if notification[0] == 0:
                self.notifications.remove(notification)
            else:
                surface.blit(notification[1][0], self.camera.object_pos(*notification[1][1]))
                notification[0] -= 1