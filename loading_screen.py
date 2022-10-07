from config import *
from pg_funcs import centred_text
from status_icons import StatusBar
import threading


def import_functions(stage):
    match stage:
        case 0:
            import attacks
        case 1:
            import hud
        case 2:
            import map
        case 3:
            import entities
        case 4:
            import enemy


class LoadingScreen:
    def __init__(self):
        self.display = pg.display.get_surface()
        self.window = pg.Surface(Config.UNSCALED_SIZE)
        self.stage = 0
        self.text = "Loading"
        self.text_surface = self.create_text_surface()
        self.box = StatusBar(400, 380, 400, 60, (255, 255, 255))
        self.thread = None
        self.clock = pg.time.Clock()

    def create_text_surface(self):
        return centred_text(self.text, Config.FONTS['title'], tuple(c//2 for c in Config.UNSCALED_SIZE), (255,255,255))

    def update(self):
        self.box.update(self.stage / 4)
        match self.stage:
            case 0:
                self.text = "Loading: attacks"
            case 1:
                self.text = "Loading: hud"
            case 2:
                self.text = "Loading: map"
            case 3:
                self.text = "Loading: player"
            case 4:
                self.text = "Loading: enemies"
        self.text_surface = self.create_text_surface()

    def draw(self):
        self.window.blit(self.text_surface[0], self.text_surface[1])
        self.box.draw(self.window)
        self.display.blit(pg.transform.scale(self.window, Config.SCALED_SIZE), (0, 0))

    def main_loop(self):
        self.clock.tick(30)
        self.update()
        self.draw()
        pg.display.update()
        while self.stage != 5:
            self.clock.tick(30)
            self.window.fill((0,0,0))
            if self.thread is None:
                self.thread = threading.Thread(target=import_functions, args=(self.stage,))
                self.thread.start()
            if not self.thread.is_alive():
                self.stage += 1
                self.thread = threading.Thread(target=import_functions, args=(self.stage,))
                self.thread.start()
            self.update()
            self.draw()
            pg.display.update()


