#! cd .. && python3 -m lpc_animator

"""
todo: save/load config
      presets
"""
import os
import sys
import math
import json
from typing import List, Dict
import pygame

from collections import defaultdict

from .engine import Engine, GameState
from .globals import g

from lpcdb.sprites import SpriteSheetBuilder
from lpcdb.lpcdb import LPCDB, SpritePreset, SpritePresetVariant

class Sound(object):

    CLICK1 = "./data/sfx/gui/clicksound1.wav"
    CLICK2 = "./data/sfx/gui/clicksound2.wav"
    CLICK3 = "./data/sfx/gui/clicksound3.wav"

    sounds = {}

    @staticmethod
    def load(sid):
        if not os.path.exists(sid):
            return None

        if sid not in Sound.sounds:
            Sound.sounds[sid] = pygame.mixer.Sound(sid)
        return Sound.sounds[sid]

    @staticmethod
    def play(sid):

        snd = Sound.load(sid)
        if snd:
            snd.play()

class CharEntity(object):
    """docstring for CharEntity"""
    def __init__(self):
        super(CharEntity, self).__init__()

        self.xpos = 32
        self.ypos = 32
        self.sprites = None
        self.image_index = 0
        self.timer = 0
        self.timeout = .1
        self.paused = False

    def handle_event(self, evt):

        if evt.type == pygame.KEYDOWN:
            if evt.key == pygame.K_SPACE:
                self.paused = not self.paused

            if evt.key == pygame.K_LEFT:
                self.image_index -= 1

            if evt.key == pygame.K_RIGHT:
                self.image_index += 1

            if evt.key == pygame.K_DOWN:
                self.image_index = 0

    def update(self, delta_t):

        if not self.paused:
            self.timer += delta_t
            if self.timer > self.timeout:
                self.timer -= self.timeout
                self.image_index += 1

    def paint(self, surface):

        self.ypos = 0
            #for zPos, size, sprites in self.sprites:
        j = 0
        for grp, info in self.sprites.items():

            size = 72

            i = 0
            for direction in ['north', 'east', 'south', 'west']:
                i += size
                if direction in info:
                    frames = info[direction]
                    count = len(frames)
                    frame = frames[self.image_index % count]

                    #pygame.draw.rect(surface, (200,0,0), (self.xpos + i, self.ypos + j, 64, 64))

                    if frame.get_width() == 192:
                        surface.blit(frame, (self.xpos + i - 64, self.ypos + j - 64))
                    else:
                        surface.blit(frame, (self.xpos + i, self.ypos + j))
            j += size

    def setSprites(self, sprites):

        animations = defaultdict(dict)

        for direction in ['north', 'east', 'south', 'west']:

            if direction in sprites['walk']:
                animations["walk"][direction] = sprites['walk'][direction]

            slashp = "slash3"
            if direction in sprites[slashp]:

                animation = []
                animation.append(sprites[slashp][direction][0])
                animation.append(sprites[slashp][direction][0])
                animation.append(sprites[slashp][direction][0])
                animation.append(sprites[slashp][direction][0])
                animation.extend(sprites[slashp][direction])
                animations[slashp][direction] = animation

                animations[slashp][direction] = animation
            else:
                animations[slashp][direction] = []

            if direction in sprites['thrust1']:
                animation = []
                animation.append(sprites['thrust1'][direction][0])
                animation.append(sprites['thrust1'][direction][0])
                animation.append(sprites['thrust1'][direction][0])
                animation.append(sprites['thrust1'][direction][0])
                animation.extend(sprites['thrust1'][direction])
                animations["thrust1"][direction] = animation

            if direction in sprites['shoot1_begin']:
                animation = []
                animation.append(sprites["shoot1_begin"][direction][0])
                animation.append(sprites["shoot1_begin"][direction][0])
                animation.append(sprites["shoot1_begin"][direction][0])
                animation.append(sprites["shoot1_begin"][direction][0])
                animation.extend(sprites["shoot1_begin"][direction])
                animation.extend(sprites["shoot1_hold"][direction])
                animation.extend(sprites["shoot1_hold"][direction])
                animation.extend(sprites["shoot1_hold"][direction])
                animation.extend(sprites["shoot1_hold"][direction])
                animation.extend(sprites["shoot1_end"][direction])
                animations["shoot1"][direction] = animation

            if direction in sprites['cast1_begin']:
                animation = []
                animation.append(sprites["cast1_begin"][direction][0])
                animation.append(sprites["cast1_begin"][direction][0])
                animation.append(sprites["cast1_begin"][direction][0])
                animation.append(sprites["cast1_begin"][direction][0])
                animation.append(sprites["cast1_begin"][direction][0])
                animation.extend(sprites["cast1_begin"][direction])
                animation.extend(sprites["cast1_hold"][direction])
                animation.extend(sprites["cast1_hold"][direction])
                animation.extend(sprites["cast1_hold"][direction])
                animation.extend(sprites["cast1_hold"][direction])
                animation.extend(sprites["cast1_end"][direction])
                animations["cast1"][direction] = animation

                animation = []
                animation.append(sprites["cast2_begin"][direction][0])
                animation.append(sprites["cast2_begin"][direction][0])
                animation.append(sprites["cast2_begin"][direction][0])
                animation.append(sprites["cast2_begin"][direction][0])
                animation.append(sprites["cast2_begin"][direction][0])
                animation.extend(sprites["cast2_begin"][direction])
                animation.extend(sprites["cast2_hold"][direction])
                animation.extend(sprites["cast2_hold"][direction])
                animation.extend(sprites["cast2_hold"][direction])
                animation.extend(sprites["cast2_hold"][direction])
                animation.extend(sprites["cast2_hold"][direction])
                animation.extend(sprites["cast2_hold"][direction])
                animation.extend(sprites["cast2_hold"][direction])
                animation.extend(sprites["cast2_hold"][direction])
                animation.extend(sprites["cast2_end"][direction])
                animations["cast2"][direction] = animation

                #animations["stagger"][direction] = sprites['stagger'][direction]

            if direction in sprites['hurt']:

                animation = []
                animation.append(sprites["hurt"][direction][0])
                animation.append(sprites["hurt"][direction][0])
                animation.append(sprites["hurt"][direction][0])
                animation.append(sprites["hurt"][direction][0])
                animation.extend(sprites["hurt"][direction])
                animation.extend(sprites["down"][direction])
                animation.extend(sprites["down"][direction])
                animation.extend(sprites["down"][direction])
                animation.extend(sprites["down"][direction])
                animation.extend(sprites["down"][direction])
                animations["hurt"][direction] = animation

        self.sprites = animations
        self.timer = 0

class Widget():
    def __init__(self):
        super(Widget, self).__init__()

        self.visible = True

    def handle_event(self, evt):
        pass
    def update(self, delta_t):
        pass
    def paint(self, surface):
        pass

class TextInput(Widget):
    def __init__(self, parent, x=0, y=0, w=32, h=32):
        super(TextInput, self).__init__()
        self.parent = parent
        self.resize(x, y, w, h)

        self.font = g.engine.getFont('arial', size=11)
        self.text = ""
        self.insert_index = 0
        self.enabled = False
        self.error = False

        self.show_cursor = True
        self.timer_cursor = 0
        self.timout_cursor = 0.5

    def update(self, delta_t):

        self.timer_cursor += delta_t
        if self.timer_cursor > self.timout_cursor:
            self.timer_cursor -= self.timout_cursor
            self.show_cursor = not self.show_cursor

    def resize(self, x, y, w, h):
        self.xpos = x
        self.ypos = y
        self.width = w
        self.height = h
        self.rect = pygame.Rect(self.xpos, self.ypos, self.width, self.height)

    def setText(self, text):
        self.text = text

    def handle_event(self, evt):

        if evt.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(evt.pos):
                Sound.play(Sound.CLICK2)
                self.parent.focus(self)
                self.enabled = True
            elif self.parent.hasFocus(self):
                self.enabled = False
                self.parent.focus(None)

        if self.parent.hasFocus(self):

            if evt.type == pygame.KEYDOWN:
                if evt.key == pygame.K_LEFT:
                    if self.insert_index < len(self.text):
                        self.insert_index += 1

                elif evt.key == pygame.K_RIGHT:
                    if self.insert_index > 0:
                        self.insert_index -= 1

                elif evt.key == pygame.K_HOME:
                    self.insert_index = len(self.text)

                elif evt.key == pygame.K_END:
                    self.insert_index = 0

                elif evt.key == pygame.K_DELETE:
                    self.onKeyDelete()

                elif evt.key == pygame.K_BACKSPACE:
                    self.onKeyBackspace()

                elif evt.key == pygame.K_KP_ENTER or evt.key == pygame.K_RETURN:
                    self.submit()

                elif evt.unicode:
                    self.onKeyAppend(evt)

    def onKeyBackspace(self):
        if self.insert_index == 0:
            self.text = self.text[:-1]
        else:
            self.text = self.text[:-self.insert_index - 1] + \
                        self.text[-self.insert_index:]
            if self.insert_index > len(self.text):
                self.insert_index = len(self.text)

    def onKeyDelete(self):
        if self.insert_index == 0:
            return
        else:
            a = len(self.text) - self.insert_index
            self.text = self.text[:a] + self.text[a+1:]
            self.insert_index -= 1
            if self.insert_index > len(self.text):
                self.insert_index = len(self.text)

    def onKeyAppend(self, evt):
        if self.insert_index == 0:
            self.text += evt.unicode
        else:
            self.text = self.text[:-self.insert_index] + \
                        evt.unicode + \
                        self.text[-self.insert_index:]

    def submit(self):
        pass

    def paint(self, surface):

        fh = self.font.get_height()
        x = self.xpos
        y = self.ypos
        xoff = 4
        col = (200, 200, 200)

        if self.error:
            pygame.draw.rect(surface, (100,60,60), (x,y,self.width,self.height))
        else:
            pygame.draw.rect(surface, (60,60,60), (x,y,self.width,self.height))
        y2 = y + self.height
        pygame.draw.line(surface, (90,90,90), (x,y2), (x+self.width,y2), width=2)
        pygame.draw.line(surface, (90,90,90), (x+self.width,y), (x+self.width,y2), width=2)


        y = y + self.height//2 - fh//2
        if self.text:
            # TODO: truncate the text view port if the text would overflow
            # blit on to a sub surface
            # then use
            #   surface.blit(sub, pos, area)
            # where area is a centerd view of the sub surface
            # center around the insert index
            if self.insert_index == 0:
                text = self.font.render(self.text, True, col)
                surface.blit(text, (x + xoff, y))
                if self.show_cursor and self.enabled:
                    pygame.draw.rect(surface, col, (x + xoff + text.get_width() + 1, y, 2, fh))
            else:
                text1 = self.text[:-self.insert_index]
                text2 = self.text[-self.insert_index:]

                xt = x + xoff
                if text1:
                    surf1 = self.font.render(text1, True, col)
                    surface.blit(surf1, (x + xoff, y))
                    xt += surf1.get_width()

                if self.show_cursor and self.enabled:
                    pygame.draw.rect(surface, col, (xt + 1, y, 2, fh))

                if text2:
                    surf2 = self.font.render(text2, True, col)
                    surface.blit(surf2, (xt + 4, y))
        elif self.show_cursor and self.enabled:
            pygame.draw.rect(surface, col, (x + xoff + 1, y, 2, fh))

class IconButton(Widget):
    def __init__(self, parent, icon, callback, xpos, ypos, width, height):
        super(IconButton, self).__init__()
        self.parent = parent
        self.icon = icon
        self.callback = callback
        self.resize(xpos, ypos, width, height)



    def resize(self, x, y, w, h):
        self.xpos = x
        self.ypos = y
        self.width = w
        self.height = h
        self.rect = pygame.Rect(self.xpos, self.ypos, self.width, self.height)

        self.xoff = self.xpos + self.width//2 - self.icon.get_width()//2
        self.yoff = self.ypos + self.height//2 - self.icon.get_height()//2

    def handle_event(self, evt):

        if evt.type == pygame.MOUSEBUTTONDOWN:
            pass
        if evt.type == pygame.MOUSEMOTION:
            pass
        if evt.type == pygame.MOUSEBUTTONUP:
            if evt.button == 1:
                if self.rect.collidepoint(evt.pos):
                    Sound.play(Sound.CLICK1)
                    if self.callback:
                        self.callback()

    def paint(self, surface):

        pygame.draw.rect(surface, (60,60,60), self.rect)
        surface.blit(self.icon, (self.xoff,self.yoff))

class ScrollItem(Widget):
    def __init__(self, parent, text):
        super(ScrollItem, self).__init__()
        self.parent = parent
        self.xpos = 0
        self.ypos = 0
        self.width = 0
        self.height = 0
        self.has_focus = False

        self.font = g.engine.getFont(size=11)
        fh = self.font.get_height()
        lh = int(fh * 1.5)
        self.height = lh

        self.text = text
        self.label1 = self.font.render(text, True, (200, 200, 200))
        self.label2 = self.font.render(text, True, (200, 200, 0))

    def resize(self, x, y, w, h):
        self.xpos = x
        self.ypos = y
        self.width = w
        self.height = h

    def update(self, delta_t):

        pass

    def paint(self, surface):
        fh = self.font.get_height()

        c = (60,60,60)
        if self.parent.widgets[self.parent.selected_index] is self:
            c = (90,90,200)
        area = (self.xpos, self.ypos, self.width, self.height)
        pygame.draw.rect(surface, c, area, width=0)

        if self.parent.altColor(self.text):
            surface.blit(self.label2, (self.xpos + 2, self.ypos + self.height//2 - fh//2))
        else:
            surface.blit(self.label1, (self.xpos + 2, self.ypos + self.height//2 - fh//2))

class ScrollMenu(Widget):
    """
    ScrollMenu is a layout item which allows scrolling
    through other widgets.

    child widgets must implement the resize api

        properties:
            xpos
            ypos
            width
            height
        methods:
            resize(x,y,w,h)
    """
    def __init__(self, parent, xpos, ypos, width, height, callback):
        super(ScrollMenu, self).__init__()
        self.parent = parent
        self.xpos = xpos
        self.ypos = ypos
        self.width = width
        self.height = height
        self.callback = callback
        self.altColor = lambda text: False

        self.scroll_index = 0
        self.display_count = 4
        self.selected_index = 0
        self.selected_widget = None

        self.widgets = []
        self.font = g.engine.getFont(size=16)

        self.onSelectionChanged = callback
        self.onMenuCancel = lambda: None

        self.style = lambda: None
        self.style.min_items = 4

        self.page_size = 5

    def handle_event(self, evt):

        if not self.visible:
            return

        fh = self.font.get_height()
        lh = int(fh * 1.5)

        r1x = self.xpos + self.width - 2 - lh//2
        r1y = self.ypos + 8
        r1w = lh // 2
        r1h = lh // 2

        r2x = r1x
        r2y = self.ypos + self.height - 8 - lh//2
        r2w = r1w
        r2h = r1h

        if evt.type == pygame.MOUSEBUTTONDOWN:
            if evt.button == 4:
                x,y = evt.pos
                if self.xpos <= x <= r1x and \
                   self.ypos <= y <= self.ypos + self.height:
                    self.scrollUp()
            elif evt.button == 5:
                x,y = evt.pos
                if self.xpos <= x <= r1x and \
                   self.ypos <= y <= self.ypos + self.height:
                    self.scrollDown()

        if evt.type == pygame.MOUSEBUTTONUP:
            if evt.button == 1:
                x,y = evt.pos

                if self.xpos <= x <= r1x and \
                   self.ypos <= y <= self.ypos + self.height:

                   self.onClick(evt)

                elif r1x <= x <= r1x+r1w and \
                     r1y <= y <= r1y+r1h:
                    self.scrollUp()


                elif r2x <= x <= r2x+r2w and \
                     r2y <= y <= r2y+r2h:
                    self.scrollDown()
        for wgt in self.widgets:
            if wgt.visible:
                wgt.handle_event(evt)

    def onScrollIndexChanged(self):
        """  update the layout of the widgets
        """

        fh = self.font.get_height()
        lh = int(fh * 1.5)

        rx = self.xpos + 2
        ry = self.ypos + 8
        rw = self.width - 2 - lh//2 - 2 - 2

        i = 0
        self.display_count = 0
        while i < len(self.widgets):
            wgt = self.widgets[i]

            if i < self.scroll_index:
                wgt.visible = False

            elif ry + wgt.height < self.ypos + self.height - 8:
                wgt.visible = True
                self.display_count += 1
                wgt.resize(rx, ry, rw, wgt.height)
                ry += wgt.height + 2
            else:
                break

            i += 1

        while i < len(self.widgets):
            wgt = self.widgets[i]

            wgt.visible = False

            i += 1

    def scrollTo(self, index):
        if self.selected_index < self.scroll_index:
            self.scroll_index = self.selected_index

        minv = len(self.widgets) - self.style.min_items
        if self.selected_index >= self.scroll_index + self.display_count:
            self.scroll_index = min(minv, self.selected_index)

        self.onScrollIndexChanged()

    def scrollUp(self):
        if self.scroll_index > 0:
            self.scroll_index = max(
                0,
                self.scroll_index - self.page_size
            )
            self.onScrollIndexChanged()
            Sound.play(Sound.CLICK2)
        else:
            Sound.play(Sound.CLICK3)

    def scrollDown(self):
        if len(self.widgets) > self.style.min_items:
            minv = len(self.widgets) - self.style.min_items
            if self.scroll_index  < minv:
                self.scroll_index = min(
                    minv,
                    self.scroll_index + self.page_size
                )
                self.onScrollIndexChanged()
                Sound.play(Sound.CLICK2)
            else:
                Sound.play(Sound.CLICK3)
        else:
            Sound.play(Sound.CLICK3)

    def onClick(self, evt):

        x,y = evt.pos
        fh = self.font.get_height()
        lh = int(fh * 1.5)

        for idx, wgt in enumerate(self.widgets):
            if wgt.visible:
                rect = pygame.Rect(wgt.xpos, wgt.ypos, wgt.width, wgt.height)
                if rect.collidepoint(evt.pos):
                    Sound.play(Sound.CLICK2)
                    self.selected_index = idx
                    self.onSelectionChanged(self.selected_index)
                    break
        else:
            Sound.play(Sound.CLICK3)

    def update(self, delta_t):

        for wgt in self.widgets:
            if wgt.visible:
                wgt.update(delta_t)

    def paint(self, surface):
        fh = self.font.get_height()
        lh = int(fh * 1.5)
        lw = self.width - 16 - 16
        area = (self.xpos, self.ypos, self.width, self.height)
        pygame.draw.rect(surface, (100,100,100), area)
        #pygame.draw.rect(surface, (100,100,0), area, width=3)

        x = self.xpos + 8
        y = self.ypos + 8

        # draw the up arrow button
        rw = lh // 2
        rh = lh // 2
        rx = self.xpos + self.width - 2 - rw
        ry = y
        pygame.draw.rect(surface, (200, 200, 200), (rx, ry, rw, rh))
        pygame.draw.polygon(surface, (0, 0, 0),
            [(rx+rw//2,ry+3), (rx+3, ry+rh-3), (rx+rw-3, ry+rw-3)])

        for wgt in self.widgets:
            if wgt.visible:
                wgt.paint(surface)

        # paint each visible item in the list
        #idx = self.scroll_index
        #while y + fh < self.ypos + self.height:
        #    if idx < len(self.items):
        #        if idx == self.selected_index:
        #            pygame.draw.rect(surface, (0, 200, 240), (x - 4, y - 2, lw, fh + 4))
        #            surf = self.font.render(self.items[idx], True, (255,255,255))
        #        else:
        #            surf = self.font.render(self.items[idx], True, (0,0,0))
        #        surface.blit(surf, (x, y))
        #    y += lh
        #    idx += 1

        # draw the down arrow button
        ry = self.ypos + self.height - 8 - rh
        pygame.draw.rect(surface, (200, 200, 200), (rx, ry, rw, rh))
        pygame.draw.polygon(surface, (0, 0, 0),
            [(rx+rw//2,ry+rh-4), (rx+3, ry+3), (rx+rw-4, ry+3)])

        # draw the scroll bar
        ryb = ry - 2
        ryt = (self.ypos + 8) + rh + 2
        rh = ryb - ryt
        if len(self.widgets) <= self.style.min_items:
            pygame.draw.rect(surface, (200, 200, 200), (rx, ryt, rw, rh))
        else:
            rh = rh - 12
            rn = max(1, len(self.widgets) - self.style.min_items)
            ryt += int(self.scroll_index/rn * rh)
            pygame.draw.rect(surface, (200, 200, 200), (rx, ryt, rw, 12))

#presets = [
#    {
#        "name": "lizardman",
#        "body_type": "male",
#        "layers": {
#            'body': {"name": 'Reptile', "variant": 'lightgreen unwinged'},
#            'cape': {"name": 'Solid', "variant": 'maroon'},
#            'shoulders': {"name": 'Legion', "variant": 'bronze'},
#            'armour': {"name": 'Legion', "variant": 'bronze'},
#            'bracers': {"name": 'Bracers', "variant": '3'},
#            'legs': {"name": 'Armour', "variant": '8'},
#        }
#    },
#]

class MainState(GameState):
    def __init__(self):
        super(MainState, self).__init__()
        self.widgets = []

        self.focus_widget = None

        self.db = LPCDB("./")

        builder = SpriteSheetBuilder() \
            .colorkey((0, 255, 0)) \
            .offset(0, 0) \
            .spacing(0, 0) \
            .dimensions(24, 24) \
            .layout(-1, -1)

        self.ui = builder.build("./lpc_animator/ui.bmp")

        self.ent = CharEntity()
        self.ent.xpos = 256
        self.ent.ypos = 0

        self.scroll_body = ScrollMenu(self, 4, 4, 128, 128, self.onBodyTypeIndexChanged)
        for name in self.db.getBodyTypes():
            self.scroll_body.widgets.append(ScrollItem(self.scroll_body, name))
        self.scroll_body.onScrollIndexChanged()
        self.widgets.append(self.scroll_body)

        self.scroll_types = ScrollMenu(self, 4, 128 + 4 + 4, 128, g.screen_height-128 - 4 - 4 - 4, self.onTypeIndexChanged)
        self.scroll_types.altColor = lambda text: text in self.selection
        for name in sorted(self.db.getTypes()):
            self.scroll_types.widgets.append(ScrollItem(self.scroll_types, name))
        self.scroll_types.onScrollIndexChanged()
        self.widgets.append(self.scroll_types)

        hh = g.screen_height//2
        self.scroll_names = ScrollMenu(self, 128 + 4 + 4, 4, 128, hh - 4 - 4, self.onTypeNameIndexChanged)
        self.scroll_names.onScrollIndexChanged()
        self.widgets.append(self.scroll_names)

        self.scroll_variants = ScrollMenu(self, 128 + 4 + 4, hh, 128, hh - 4, self.onVariantIndexChanged)
        self.scroll_variants.onScrollIndexChanged()
        self.widgets.append(self.scroll_variants)

        self.edit_preset_name = TextInput(self, g.screen_width - 128 - 4, 4, 96, 32)
        self.widgets.append(self.edit_preset_name)

        self.btn_save = IconButton(self, self.ui[0], self.onSaveClicked, g.screen_width - 32 - 4, 4, 32, 32)
        self.widgets.append(self.btn_save)

        self.scroll_preset = ScrollMenu(self, g.screen_width - 128 - 4, 32 + 4, 128, hh, self.onPresetIndexChanged)
        self.widgets.append(self.scroll_preset)

        self.selection = {}
        self.selected_body_type = "male"
        self.selected_body_type_both = False
        self.selected_type = "body"
        self.selected_name = "Humanlike"
        self.selected_variant = "white"

        self.selection["body"] = ("Humanlike", "white")
        self.setBodyType("male")
        self._update()

        self._fixPreset()

    def handle_event(self, evt):

        self.ent.handle_event(evt)
        for widget in self.widgets:
            widget.handle_event(evt)

    def focus(self, widget):
        self.focus_widget = widget

    def hasFocus(self, widget):
        return self.focus_widget is widget

    def onSaveClicked(self):

        preset = SpritePreset()

        if not self.edit_preset_name.text:

            print("error")
            return

        preset.name = self.edit_preset_name.text
        preset.body_type = self.selected_body_type
        preset.layers = {}

        sprites = []
        for type_name, (name, variant) in self.selection.items():
            if self.db.hasDefinition(type_name, name):
                preset.layers[type_name] = SpritePresetVariant(name=name, variant=variant)


        self.db.savePreset(preset)

        self._fixPreset()

    def onBodyTypeIndexChanged(self, index):

        body_type = self.scroll_body.widgets[index].text

        if body_type == "male&female":
            body_type = "male"
            self.selected_body_type_both = True
        else:
            self.selected_body_type_both = False
        self.setBodyType(body_type)
        self._update()

    def onTypeIndexChanged(self, index):

        type_name = self.scroll_types.widgets[index].text
        self.setType(type_name)
        self._update()

    def onTypeNameIndexChanged(self, index):

        name = self.scroll_names.widgets[index].text
        self.setTypeName(name)
        self._update()

    def onVariantIndexChanged(self, index):

        variant = self.scroll_variants.widgets[index].text
        self.setVariant(variant)
        self._update()

    def onPresetIndexChanged(self, index):

        preset_name = self.scroll_preset.widgets[index].text
        preset = self.db.presets[preset_name]

        self.selection = {}
        for category, info in preset.layers.items():
            self.selection[category] = (info.name, info.variant)

        self.selected_body_type = preset.body_type
        self.selected_type = 'body'

        if 'body' in preset.layers:
            self.selected_name = preset.layers['body'].name
            self.selected_variant = preset.layers['body'].variant
        else:
            self.selected_name = "none"
            self.selected_variant = "none"

        self.edit_preset_name.setText(preset.name)

        self._fixCategory(self.selected_type)
        self._fixNames(self.selected_name)
        self._fixVariants(self.selected_variant)

        self._update()

    def _fixPreset(self):

        self.scroll_preset.widgets = []
        for preset_name in sorted(self.db.presets.keys()):
            self.scroll_preset.widgets.append(ScrollItem(self.scroll_preset, preset_name))
        self.scroll_preset.onScrollIndexChanged()

    def _fixCategory(self, selected_category=None):
        for idx, wgt in enumerate(self.scroll_types.widgets):
            if wgt.text == selected_category:
                self.scroll_types.selected_index = idx
                break
        else:
            self.scroll_types.selected_index = 0

        self.scroll_types.scrollTo(self.scroll_types.selected_index)

    def _fixNames(self, selected_name=None):
        self.scroll_names.widgets = []

        self.scroll_names.widgets.append(ScrollItem(self.scroll_names, "none"))
        self.scroll_names.selected_index = 0

        for  name in sorted(self.db.getTypeNames(self.selected_type)):
            if self.db.hasDefinition(self.selected_type, name):
                jsdef = self.db.getDefinition(self.selected_type, name)

                if self.selected_body_type_both:
                    attr1 = getattr(jsdef.layer_1, "male")
                    attr2 = getattr(jsdef.layer_1, "female")
                    valid = bool(attr1 and attr2)
                else:
                    attr = getattr(jsdef.layer_1, self.selected_body_type)
                    valid = bool(attr)

                if valid:
                    self.scroll_names.widgets.append(ScrollItem(self.scroll_names, name))

                    if selected_name and selected_name == name:
                        self.scroll_names.selected_index = len(self.scroll_names.widgets) - 1
        self.scroll_names.onScrollIndexChanged()
        self.scroll_names.scrollTo(self.scroll_names.selected_index)

    def _fixVariants(self, selected_variant):

        self.scroll_variants.widgets = []

        self.scroll_variants.widgets.append(ScrollItem(self.scroll_names, "none"))
        self.scroll_variants.selected_index = 0

        if self.db.hasDefinition(self.selected_type, self.selected_name):
            jsdef = self.db.getDefinition(self.selected_type, self.selected_name)
            for variant in sorted(jsdef.variants):
                self.scroll_variants.widgets.append(ScrollItem(self.scroll_variants, variant))

                if selected_variant and selected_variant == variant:
                    self.scroll_variants.selected_index = len(self.scroll_variants.widgets) - 1

        self.scroll_variants.onScrollIndexChanged()
        self.scroll_variants.scrollTo(self.scroll_variants.selected_index)

    def setBodyType(self, body_type):
        self.selected_body_type = body_type

        self.selected_type = "body"
        if self.selected_type in self.selection:
            self.selected_name, self.selected_variant = self.selection[self.selected_type]
            del self.selection[self.selected_type]

        type_names = self.db.getTypeNames(self.selected_type)
        if type_names:
            if self.selected_name not in type_names:
                self.selected_name = type_names[0]
        else:
            self.selected_name = "none"

        if self.db.hasDefinition(self.selected_type, self.selected_name):
            jsdef = self.db.getDefinition(self.selected_type, self.selected_name)

            if jsdef.variants:
                if self.selected_variant not in jsdef.variants:
                     self.selected_variant = jsdef.variants[0]
            else:
                self.selected_variant = "none"

            self.selection['body'] = [self.selected_name, self.selected_variant]

        self._fixCategory(self.selected_type)
        self._fixNames(self.selected_name)
        self._fixVariants(self.selected_variant)

    def setType(self, type_name):
        self.selected_type = type_name

        if self.selected_type in self.selection:
            name, variant = self.selection[self.selected_type]
            self.selected_name = name
            self.selected_variant = variant
        else:
            self.selected_name = "none"
            self.selected_variant = "none"

        self._fixNames(self.selected_name)
        self._fixVariants(self.selected_variant)

    def setTypeName(self, type_name):
        self.selected_name = type_name
        self._fixNames(self.selected_name)

        self.selected_variant = "none"
        if self.selected_type in self.selection:
            _, self.selected_variant = self.selection[self.selected_type]

        if self.db.hasDefinition(self.selected_type, self.selected_name):
            jsdef = self.db.getDefinition(self.selected_type, self.selected_name)
            if self.selected_variant not in jsdef.variants:
                self.selected_variant = jsdef.variants[0]

        self._fixVariants(self.selected_variant)

        self.selection[self.selected_type] = (self.selected_name, self.selected_variant)

    def setVariant(self, variant):
        self.selected_variant = variant
        self.selection[self.selected_type] = (self.selected_name, self.selected_variant)
        self._fixVariants(self.selected_variant)

    def _update(self):

        sprites = []
        self.icons = []
        for type_name, (name, variant) in self.selection.items():
            if self.db.hasDefinition(type_name, name):

                cat_sprites = self.db.getSprites(self.selected_body_type, type_name, name, variant)
                sprites.extend(cat_sprites)

                for zPos, _, t in cat_sprites:
                    if 'walk' in t:
                        print(zPos, type_name)
                        self.icons.append((zPos, t['walk']['south'][0]))

        self.icons.sort(key=lambda x: x[0])
        sprites = self.db.flatten(sprites)
        # sprites.sort(key = lambda x: x[0])
        self.ent.setSprites(sprites)

    def update(self, delta_t):

        self.ent.update(delta_t)

        for widget in self.widgets:
            widget.update(delta_t)

    def paint(self):
        g.screen.fill("#CCCCCCFF")

        self.ent.paint(g.screen)

        for widget in self.widgets:
            widget.paint(g.screen)

        for idx, (_, icon) in enumerate(self.icons):
            i = idx%2
            j = idx//2
            g.screen.blit(icon, (g.screen_width-256 + (i*32), 64 + j*64))
            g.screen.blit(icon, (g.screen_width-256, 0))

def main():

    engine = Engine()

    engine.init()
    engine.state = MainState()
    engine.run()

if __name__ == '__main__':
    main()
