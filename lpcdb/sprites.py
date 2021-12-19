
import os
import pygame
import time

class SpriteSheetBuilder(object):
    def __init__(self):
        super(SpriteSheetBuilder, self).__init__()

        self.colorkey_c = None
        self.colorkey_x = None
        self.colorkey_y = None
        self.offset_x = 0
        self.offset_y = 0
        self.spacing_x = 0
        self.spacing_y = 0
        self.rows = 0
        self.cols = 0
        self.width = 16
        self.height = 16

        self._images = []

    def colorkey(self, c_x, y=None):

        if y is None:
            self.colorkey_c = c_x
        else:
            self.colorkey_x = c_x
            self.colorkey_y = y
            self.colorkey_c = None

        return self

    def offset(self, x, y):
        # starting position of the tile sheet in the image
        self.offset_x = x;
        self.offset_y = y;
        return self

    def spacing(self, x, y):
        # space between each tile
        self.spacing_x = x;
        self.spacing_y = y;
        return self

    def dimensions(self, w, h):
        # size of each tile
        self.width = w;
        self.height = h;
        return self

    def layout(self, rows, cols):
        # number of rows and columns
        # TODO: allow 0 or negative to mean as many as possible
        self.rows = rows;
        self.cols = cols;
        return self

    def build(self, path):
        """
        it is faster to load a png with an alpha layer already set
        than to load an image and use a color key
        """

        #t0 = time.time()
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        if isinstance(path, str):
            sheet = pygame.image.load(path)
            if path.lower().endswith(".png"):
                sheet = sheet.convert_alpha()
        else:
            sheet = path

        if self.cols == -1:
            self.cols = sheet.get_width() // self.width

        if self.rows == -1:
            self.rows = sheet.get_height() // self.height

        images = []

        if self.colorkey_c is None:
            if self.colorkey_x is not None:
                self.colorkey_c = sheet.get_at((self.colorkey_x,self.colorkey_y))

        if self.colorkey_c is not None:
            sheet.set_colorkey(self.colorkey_c, pygame.RLEACCEL)

        for i in range(self.rows):
            for j in range(self.cols):

                x = self.offset_x + (self.width + self.spacing_x) * j
                y = self.offset_y + (self.height + self.spacing_y) * i

                rect = pygame.Rect(x,y,self.width, self.height)
                image = pygame.Surface(rect.size).convert_alpha()
                image.fill((0,0,0,0))
                image.blit(sheet, (0, 0), rect)

                images.append(image)

        #print("elapsed: %.2f" % (time.time() - t0))

        return images
