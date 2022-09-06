import config
import random
from pg_funcs import *
from hud import *
from entities import *
from map import Map
from camera import *
from enemy import *


class GameScreen:
    def __init__(self):
        self.player = Player(0, 0)
        self.map = Map()
        self.hud = HUD()
        self.next_state = None
        self.wave = 1
        self.spawn_rate = 0.001 * self.wave + 0.01
        self.wave_timer = 60
        self.enemies = []
        self.exp_points = []
        self.crosshair = Crosshair()
        self.flames = []
        self.offset = 0
        self.timer = 0
        self.camera = PlayerCamera()

    def reset(self):
        self.next_state = None
        self.player.move_state = {control: False for control in self.player.controls.values()}

    def spawn(self):
        if random.uniform(0, 1) < self.spawn_rate:
            self.enemies.append(BaseEnemy(self.player.pos.x + random.randint(0, config.UNSCALED_SIZE[0]),
                                          self.player.pos.y + random.choice([-config.UNSCALED_SIZE[1] - 10,
                                                                             config.UNSCALED_SIZE[1] + 10]),
                                          10, 50, 10, 1, (210, 105, 30)))

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
        for event in pg.event.get():
            self.check_event(event)
        self.spawn()
        self.player.update()
        for e in self.enemies.copy():
            e.update(self.player.pos)
            for ee in self.enemies.copy():
                if e != ee and e.type == ee.type:
                    if e.pos.distance_to(ee.pos) < e.radius:
                        e.converge(ee)
                        self.enemies.remove(ee)
        for bullet in self.player.casts.copy():
            if abs(bullet.pos.x - self.player.pos.x) > config.UNSCALED_SIZE[0] // 2 or \
                    abs(bullet.pos.y - self.player.pos.y) > config.UNSCALED_SIZE[1] // 2:
                self.player.casts.remove(bullet)
                continue
            for e in self.enemies.copy():
                if bullet.rect.colliderect(e.rect):
                    e.calculate_dmg(bullet.dmg * self.player.stats['m-dmg'])
                    if e.hp == 0:
                        self.exp_points.append(ExpPoint(e.pos.x, e.pos.y, e.exp))
                        self.enemies.remove(e)
                    self.player.casts.remove(bullet)
                    break
        for exp in self.exp_points.copy():
            if abs(self.player.pos.x - exp.pos.x) < config.UNSCALED_SIZE[0] // 2 and \
                    abs(self.player.pos.y - exp.pos.y) < config.UNSCALED_SIZE[1] // 2:
                exp.drawable = True
                if exp.rect.colliderect(self.player.rect):
                    if self.player.add_exp(exp.value):
                        self.next_state = 'upgrade'
                    self.exp_points.remove(exp)
                    continue
            else:
                exp.drawable = False
        self.hud.update(self.player.stats['hp'] / self.player.stats['max hp'],
                        self.player.exp_percentage, self.player.get_dash_status(),
                        self.wave, self.wave_timer, [])
        self.crosshair.update()
        return self.next_state

    def draw(self, surface):
        self.map.draw(surface)
        self.camera.update_player(self.player.pos.x, self.player.pos.y)
        self.camera.update_camera()
        for exp in self.exp_points:
            if exp.drawable:
                exp.draw(surface, self.camera)
        for e in self.enemies:
            e.draw(surface, self.camera)
        self.player.draw(surface, self.camera)
        self.hud.draw(surface)
        self.crosshair.draw(surface)


class PauseScreen:
    def __init__(self):
        self.screen = None
        self.next_state = None

    def reset(self):
        self.next_state = None

    def check_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.next_state = 'game'
        elif event.type == pg.KEYUP:
            pass

    def update(self):
        for event in pg.event.get():
            self.check_event(event)
        return self.next_state

    def draw(self, surface):
        surface.blit(self.screen, (0, 0))


class UpgradeScreen:
    def __init__(self):
        self.screen = None
        self.upgrade_cards = []
        self.get_upgrade_cards()
        self.next_state = None
        self.upgrade_text, self.upgrade_pos = centred_text("Choose Upgrade...", config.FONTS['upgrade'],
                                                           (config.UNSCALED_SIZE[0]//2, 50), (255, 248, 220))

    def reset(self):
        self.next_state = None
        self.get_upgrade_cards()

    def get_upgrade_cards(self):
        # do something here. probably random
        self.upgrade_cards = [UpgradeCard((x * config.UNSCALED_SIZE[0]//6) - UpgradeCard.card_width//2, 100,
                                          "upgrades/bullet.json") for x in [2, 3, 4]]

    def check_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                x, y = get_mouse()
                for card in self.upgrade_cards:
                    if card.x < x < card.x + card.card_width and card.y < y < card.y + card.card_height:
                        self.next_state = "game"

    def update(self):
        for event in pg.event.get():
            self.check_event(event)
        return self.next_state

    def draw(self, surface):
        surface.blit(self.screen, (0, 0))
        for card in self.upgrade_cards:
            card.draw(surface)
        surface.blit(self.upgrade_text, self.upgrade_pos)
