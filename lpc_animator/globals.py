
class Namespace(object):
    def __init__(self):
        super(Namespace, self).__init__()

        self.FPS = 60
        self.engine = None


        self.window_mode = "window" # one of: borderless, windowed, fullscreen
        self.window_size = None
        self.window = None

        self.screen = None
        self.screen_width = 960
        self.screen_height = 540

        self.viewport = None
        self.viewport_x = 0
        self.viewport_y = 0

        self.viewport_width = 640
        self.viewport_height = 352 # 384

        self.frame_counter = 0

        self.next_state = 0

g = Namespace()