from config import *
from screens import *


class Controller:
    def __init__(self):
        self.display = pg.display.get_surface()
        self.window = pg.Surface(Config.UNSCALED_SIZE)
        self.game_running = True
        self.clock = pg.time.Clock()
        self.frame_rate = Config.FRAME_RATE
        self.screen = None

    def blit_fps(self):
        self.window.blit(*centred_text(str(round(self.clock.get_fps(), 1)),
                                       Config.FONTS['dmg_notification'], (20, 20), (255, 255, 255)))

    def switch_state(self, state, other=None):
        if state == 'game':
            if other is True:
                SCREENS[state] = GameScreen()
            pg.mouse.set_visible(False)
        else:
            SCREENS[state].screen = self.window
            pg.mouse.set_visible(True)
        self.screen = SCREENS[state]
        self.screen.pre_switch(other)

    def get_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.game_running = False
            elif event.type == pg.KEYUP:
                self.screen.check_event(event)
            else:
                self.screen.check_event(event)

    def main_loop(self):
        self.screen = SCREENS['main menu']
        while self.game_running:
            self.clock.tick(self.frame_rate)
            self.get_events()
            state = self.screen.update()
            match state:
                case None:
                    pass
                case [s, other]:
                    self.switch_state(s, other)
                case s:
                    self.switch_state(s)
            self.screen.draw(self.window)
            if Config.BLIT_FPS:
                self.blit_fps()
            self.display.blit(pg.transform.scale(self.window, Config.SCALED_SIZE), (0, 0))
            pg.display.update()
        pg.quit()


if __name__ == '__main__':
    os.environ["SDL_VIDEO_CENTERED"] = "True"
    pg.display.set_caption(Config.GAME_CAPTION)
    display_info = pg.display.Info()
    SCREEN_SIZE = (display_info.current_w, display_info.current_h)
    pg.display.set_mode(Config.SCALED_SIZE)
    controller = Controller()
    SCREENS = {'game': GameScreen(), 'pause': PauseScreen(), 'upgrade': UpgradeScreen(),
               'main menu': MenuScreen()}
    controller.main_loop()
