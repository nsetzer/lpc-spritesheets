import os
import sys
import time
import logging
import traceback
import threading

from .globals import g

import pygame
from pygame._sdl2.video import Window

class GameState(object):
    def __init__(self):
        super(GameState, self).__init__()

    def handle_message(self, msg):
        pass

    def handle_event(self, evt):
        pass

    def paint(self):
        pass

    def paintOverlay(self, window, scale):
        pass

    def resizeEvent(self, window_width, window_height):
        pass

    def update(self, delta_t):
        pass

class ExceptionState(GameState):
    def __init__(self):
        super(ExceptionState, self).__init__()
        self.exec_info = sys.exc_info()
        font = g.engine.getFont(size=72)
        self.text = font.render("Error", True, (255, 255, 255))
        self.acked = False

    def ack(self, *args):
        self.acked = True

    def update(self, delta_t):
        pass

    def paint(self):

        g.screen.fill((0,0,170))
        x = g.screen_width//2 - self.text.get_width()//2
        y = g.screen_height//2 - self.text.get_height()//2
        g.screen.blit(self.text, (x,y))

class Engine(object):
    def __init__(self):
        super(Engine, self).__init__()

        self.active = False
        self.state = None

        self.sdl_window = None

        self.deferred_text = []
        self._font_cache1 = {}
        self._font_cache2 = {}

        pygame.joystick.init()
        if pygame.joystick.get_count():
            g.joystick_index = 0
            g.joystick = pygame.joystick.Joystick(g.joystick_index)
            g.joystick.init()

        self.stats_fps = [60]*5*60
        self.last_fps_update_time = 0

    def init(self):

        pygame.init()
        pygame.display.init()
        pygame.font.init()
        pygame.mixer.init()

        g.engine = self

        infoObject = pygame.display.Info()
        w = infoObject.current_w
        h =infoObject.current_h
        self.resolution = (w, h)

        self.setWindowMode()

        g.clock = pygame.time.Clock()

    def run(self):

        try:
            self._run()

        except Exception as e:
            raise

        finally:
            pygame.display.quit()
            pygame.quit()

        print("run finished")

        return 0 # process exit code

    def _run(self):

        self.active = True


        if self.deferred_text:
            self.deferred_text = []

        accumulator = 0.0
        update_step = 1 / g.FPS

        while self.active:


            if g.next_state:
                self.state = self.getState(g.next_state)
                g.next_state = 0

            accumulator += g.clock.tick(g.FPS) / 1000
            g.frame_counter += 1

            try:
                for event in pygame.event.get():
                    if self.handle_event(event):
                        continue
            except Exception as e:
                logging.exception("error during event")
                self.state = ExceptionState()

            # ensure every update step uses the same delta_t
            # this means some frames will have 0 or more than 1 update
            try:
                t0 = int(time.time())
                if t0 != self.last_fps_update_time:
                    self.last_fps_update_time = t0
                    self.stats_fps.append(g.clock.get_fps())
                    while len(self.stats_fps) > 5 * 60:
                        self.stats_fps.pop(0)

                while accumulator > update_step:
                    self.state.update(update_step)
                    accumulator -= update_step

            except Exception as e:
                logging.exception("error during update")
                self.state = ExceptionState()

            try:

                self.state.paint()

            except Exception as e:
                logging.exception("error during paint")
                self.state = ExceptionState()

            try:

                if g.screen is not g.window:
                    # g.window.blit(pygame.transform.scale(g.screen, g.window_size), (0,0))
                    window = pygame.transform.smoothscale(g.screen, g.window_size)
                    self.state.paintOverlay(window, g.window_scale)
                    g.window.blit(window, (0,0))

                else:

                    self.state.paintOverlay(g.window, g.window_scale)

            except Exception as e:
                logging.exception("error during paint")
                self.state = ExceptionState()


            pygame.display.flip()
        print("activity exited")

    def setWindowMode(self):
        """
        the first time this is called the environment variables are
        used to suggest  how to display the window

        subsequent calls require changing the window to a bogus value
        before updating the sdl_window and changing the mode to the
        new correct value

        """

        if g.window_mode == "borderless":
            if self.sdl_window:
                g.window = pygame.display.set_mode((100, 100))
            os.environ['SDL_VIDEO_CENTERED'] = '1'
            os.environ['SDL_VIDEO_WINDOW_POS']='0, 0'
            if self.sdl_window:
                self.sdl_window.position = (0,0)
            g.window = pygame.display.set_mode(self.resolution, pygame.NOFRAME)
            g.window_size = self.resolution
            g.screen = pygame.Surface((g.screen_width, g.screen_height)).convert()

        elif g.window_mode == "fullscreen":
            if self.sdl_window:
                g.window = pygame.display.set_mode((100, 100))
            g.window = pygame.display.set_mode((0,0), pygame.FULLSCREEN|pygame.HWSURFACE|pygame.DOUBLEBUF)
            g.window_size = (g.window.get_width(), g.window.get_height())
            g.screen = pygame.Surface((g.screen_width, g.screen_height)).convert()
        else:
            if self.sdl_window:
                g.window = pygame.display.set_mode((100, 100))
            x=self.resolution[0]//2 - g.screen_width//2
            y=self.resolution[1]//2 - g.screen_height//2
            os.environ['SDL_VIDEO_WINDOW_POS']='%d, %d' % (x,y)
            if self.sdl_window:
                self.sdl_window.position = (x, y)
            g.window = pygame.display.set_mode((g.screen_width, g.screen_height))
            g.window_size = None
            g.screen = g.window

        g.window_scale = (g.window.get_width()/g.screen.get_width(), g.window.get_height()/g.screen.get_height())

        if self.sdl_window is None:
            self.sdl_window = Window.from_display_module()
        g.viewport = pygame.Surface((g.viewport_width, g.viewport_height))

        print("viewport: (%d,%d)" % (g.viewport.get_width(), g.viewport.get_height()))
        print("screen: (%d,%d)" % (g.screen.get_width(), g.screen.get_height()))
        print("window: (%d,%d)" % (g.window.get_width(), g.window.get_height()))
        print("SDL_VIDEO_WINDOW_POS: %s" % os.environ.get('SDL_VIDEO_WINDOW_POS'))
        print("SDL_VIDEO_CENTERED: %s" % os.environ.get('SDL_VIDEO_CENTERED'))
        print(g.window_scale)

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.setActive(False)

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_ESCAPE:
                self.setActive(False)

            if event.key == pygame.K_F1:
                g.window_mode = "borderless"
                self.setWindowMode()
                self.state.resizeEvent(g.window.get_width(), g.window.get_height())

            if event.key == pygame.K_F2:
                g.window_mode = "fullscreen"
                self.setWindowMode()
                self.state.resizeEvent(g.window.get_width(), g.window.get_height())

            if event.key == pygame.K_F3:
                g.window_mode = "windowed"
                self.setWindowMode()
                self.state.resizeEvent(g.window.get_width(), g.window.get_height())

        if event.type == pygame.MOUSEBUTTONDOWN:
            event.pos = g.engine.screenpos(event.pos)
        if event.type == pygame.MOUSEBUTTONUP:
            event.pos = g.engine.screenpos(event.pos)
        if event.type == pygame.MOUSEMOTION:
            event.pos = g.engine.screenpos(event.pos)

        self.state.handle_event(event)

    def handleDroppedConnection(self):
        raise NotImplementedError()

    def setActive(self, active):
        self.active = active

    def getState(self, state):

        raise NotImplementedError

    def screenpos(self, windowpos):
        if g.window is not g.screen:
            wx, wy = windowpos
            sx, sy = g.window_size
            x = int(wx * g.screen_width / sx)
            y = int(wy * g.screen_height / sy)
            return (x, y)
        return windowpos

    def getFont(self, family=None, size=12, bold=False, italic=False, underline=False):

        if not family:
            family = "arial"
        font_family = pygame.font.match_font(family)

        spec = (family, size, bold, italic, underline)
        if spec not in self._font_cache1:
            print("load font: %s" % (spec,))
            font = pygame.font.Font(font_family, size, bold=bold,italic=italic)
            self._font_cache1[spec] = font
        return self._font_cache1[spec]

    def renderText(self):

        for spec, rect, color, text, max_width in self.deferred_text:
            font = self._font_cache1[spec]
            surf = font.render(text, True, color)
            g.window.blit(surf, rect)
