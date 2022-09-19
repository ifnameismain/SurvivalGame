from hud import *
from entities import *
from map import Map
from camera import *
from enemy import *
from wave import Wave


class GameScreen:
    def __init__(self):
        self.player = Player(0, 0)
        self.map = Map()
        self.hud = HUD()
        self.next_state = None
        self.wave = Wave()
        self.exp_points = []
        self.crosshair = Crosshair()
        self.camera = PlayerCamera()
        self.map.update_background(self.player.pos)
        self.notifications = []

    def pre_switch(self, upgrade):
        if upgrade is not None:
            self.player.register_upgrade(upgrade)
        self.next_state = None
        self.player.move_state = {control: False for control in self.player.controls.values()}

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
        self.player.update(self.camera)
        self.wave.update(self.player.pos)
        for e in self.wave.enemies.copy():
            e.update(self.player.pos)
            if e.stats['hp'] <= 0:
                self.exp_points.append(ExpPoint(e.pos.x, e.pos.y, e.exp))
                self.wave.enemies.remove(e)
                continue
        self.wave.converge()
        self.player.stats['hp'] -= len(self.player.rect.collidelistall([e.rect for e in self.wave.enemies]))
        for bullet in self.player.casts.copy():
            if abs(bullet.pos.x - self.player.pos.x) > config.WIDTH // 2 or \
                    abs(bullet.pos.y - self.player.pos.y) > config.HEIGHT // 2:
                self.player.casts.remove(bullet)
                continue
            for e in self.wave.enemies:
                if isinstance(bullet, Bullet):
                    if bullet.rect.colliderect(e.rect):
                        e.add_dmg(bullet.get_dmg())
                        self.player.casts.remove(bullet)
                        break
                elif isinstance(bullet, StatusBomb):
                    if bullet.state == 1:
                        if bullet.rect.colliderect(e.rect):
                            e.add_dmg(bullet.get_dmg())
                    elif bullet.state == 2:
                        self.player.casts.remove(bullet)
                        break
        for e in self.wave.enemies:
            e.calculate_status()
            if nots := e.get_notification():
                for n in nots[1]:
                    self.notifications.append([30, n])
            e.status_inflicted['normal'] = 0
            for key in e.status_inflicted:
                if key == "normal":
                    continue
                else:
                    if e.status_tick_timers[key] == e.status_tick_rate:
                        if e.status_inflicted[key] != 0:
                            e.status_inflicted[key] -= 1
        for exp in self.exp_points.copy():
            if abs(self.player.pos.x - exp.pos.x) < config.WIDTH // 2 and \
                    abs(self.player.pos.y - exp.pos.y) < config.HEIGHT // 2:
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
                        self.wave.num, self.wave.wave_time, [])
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
        for exp in self.exp_points:
            if exp.drawable:
                exp.draw(surface, self.camera)
        for e in self.wave.enemies:
            e.draw(surface, self.camera)
        self.player.draw(surface, self.camera)
        self.hud.draw(surface)
        self.crosshair.draw(surface)
        for notification in self.notifications.copy():
            if notification[0] == 0:
                self.notifications.remove(notification)
            else:
                surface.blit(notification[1][0], self.camera.object_pos(*notification[1][1]))
                notification[0] -= 1


class PauseScreen:
    def __init__(self):
        self.screen = None
        self.next_state = None
        self.pause_text, self.pause_pos = centred_text("paused...", config.FONTS['upgrade'],
                                                       (config.WIDTH // 2, config.HEIGHT // 2),
                                                       (255, 248, 220))

    def pre_switch(self, other):
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
        surface.blit(self.pause_text, self.pause_pos)


class UpgradeScreen:
    def __init__(self):
        self.screen = None
        self.upgrade_cards = []
        self.get_upgrade_cards()
        self.next_state = None
        self.upgrade_text, self.upgrade_pos = centred_text("Choose Upgrade...", config.FONTS['upgrade'],
                                                           (config.WIDTH//2, 50), (255, 248, 220))

    def pre_switch(self, other):
        self.next_state = None
        self.get_upgrade_cards()

    def get_upgrade_cards(self):
        # do something here. probably random
        self.upgrade_cards = [UpgradeCard((x * config.WIDTH//6) - UpgradeCard.width // 2, 100) for x in [2, 3, 4]]

    def check_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                x, y = get_mouse()
                for card in self.upgrade_cards:
                    if card.x < x < card.x + card.width and card.y < y < card.y + card.height:
                        self.next_state = ["game", card.info_key]

    def update(self):
        for event in pg.event.get():
            self.check_event(event)
        return self.next_state

    def draw(self, surface):
        surface.blit(self.screen, (0, 0))
        for card in self.upgrade_cards:
            card.draw(surface)
        surface.blit(self.upgrade_text, self.upgrade_pos)


class SettingsScreen:
    def __init__(self, game):
        self.next_state = None
        self.game = game

    def pre_switch(self, other):
        self.next_state = None

    def check_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.next_state = ['main menu', True]
        elif event.type == pg.KEYUP:
            pass

    def update(self):
        for event in pg.event.get():
            self.check_event(event)
        self.game.update()
        return self.next_state

    def draw(self, surface):
        self.game.draw(surface)
        surface.blit(self.title_card, (config.WIDTH//2-300, 125))
        surface.blit(self.title_text, self.title_pos)
        surface.blit(self.space_text, self.space_pos)


class MenuScreen:
    def __init__(self):
        self.next_state = None
        self.game = SimGame()
        self.title_card = create_card(600, 150, 15)
        self.title_text, self.title_pos = centred_text("Survival", config.FONTS['title'],
                                                       (config.WIDTH//2, 200), (255, 248, 220))
        self.space_text, self.space_pos = centred_text("Press Space to Start", config.FONTS['upgrade'],
                                                       (config.WIDTH // 2, 400), (255, 248, 220))

    def pre_switch(self, other):
        self.next_state = None
        self.game = SimGame()

    def check_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE:
                self.next_state = ['game', True]
        elif event.type == pg.KEYUP:
            pass

    def update(self):
        for event in pg.event.get():
            self.check_event(event)
        self.game.update()
        return self.next_state

    def draw(self, surface):
        self.game.draw(surface)
        surface.blit(self.title_card, (config.WIDTH//2-300, 125))
        surface.blit(self.title_text, self.title_pos)
        surface.blit(self.space_text, self.space_pos)


class SimGame:
    def __init__(self):
        self.player = Player(0, 0)
        self.map = Map()
        self.hud = HUD()
        self.next_state = None
        self.wave = Wave()
        self.exp_points = []
        self.crosshair = Crosshair()
        self.camera = PlayerCamera()
        self.map.update_background(self.player.pos)
        self.notifications = []

    def pre_switch(self, upgrade):
        if upgrade is not None:
            self.player.register_upgrade(upgrade)
        self.next_state = None
        self.player.move_state = {control: False for control in self.player.controls.values()}

    def check_event(self, event):
        pass

    def update(self):
        for event in pg.event.get():
            self.check_event(event)
        self.wave.update(self.player.pos)
        for e in self.wave.enemies.copy():
            e.update(self.player.pos)
            if e.stats['hp'] == 0:
                self.exp_points.append(ExpPoint(e.pos.x, e.pos.y, e.exp))
                self.wave.enemies.remove(e)
                continue
        self.wave.converge()
        self.player.stats['hp'] -= len(self.player.rect.collidelistall([e.rect for e in self.wave.enemies]))
        for bullet in self.player.casts.copy():
            if abs(bullet.pos.x - self.player.pos.x) > config.WIDTH // 2 or \
                    abs(bullet.pos.y - self.player.pos.y) > config.HEIGHT // 2:
                self.player.casts.remove(bullet)
                continue
            for e in self.wave.enemies.copy():
                if bullet.rect.colliderect(e.rect):
                    e.add_dmg(bullet.get_dmg())
                    self.player.casts.remove(bullet)
                    break
        for exp in self.exp_points.copy():
            if abs(self.player.pos.x - exp.pos.x) < config.WIDTH // 2 and \
                    abs(self.player.pos.y - exp.pos.y) < config.HEIGHT // 2:
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
                        self.wave.num, self.wave.wave_time, [])
        self.crosshair.update()
        self.map.update_background(self.player.pos)
        if self.player.stats['hp'] <= 0:
            self.next_state = "main menu"
        return self.next_state

    def draw(self, surface):
        self.map.draw(surface)
        self.camera.update_player(self.player.pos.x, self.player.pos.y)
        self.camera.update_camera()
        for exp in self.exp_points:
            if exp.drawable:
                exp.draw(surface, self.camera)
        for e in self.wave.enemies:
            e.draw(surface, self.camera)
        self.player.draw(surface, self.camera)
        self.hud.draw(surface)
        self.crosshair.draw(surface)
        for notification in self.notifications.copy():
            if notification[0] == 0:
                self.notifications.remove(notification)
            else:
                surface.blit(notification[1][0], self.camera.object_pos(*notification[1][1]))
                notification[0] -= 1