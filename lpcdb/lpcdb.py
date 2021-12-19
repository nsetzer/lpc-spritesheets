#! cd .. && python3 -m lpc_db.lpcdb


import os
import sys
import math
import json
from typing import List, Dict, get_origin
import pygame

from collections import defaultdict

from .sprites import SpriteSheetBuilder
from .ser import Serializable

"""
TODO: create a new set of child sprites automatically
    given: sprites[group][direction] => frames
    scale each frame from 64x64 to 48x48
    Then paste the images back into 64x64 tile sheets and
    save as child variants

    smooth scaling wont even need to be fixed

    for grp, info in sprites.items():
        for direction, frames in info.items():
            for i, frame in enumerate(frames):
                frames[i] = pygame.transform.smoothscale(frame, (48, 48))

    + dwarf_male    <- scale 64x64 to 48x48
    + dwarf_female
    + giant_male    <-- scale 64x64 to 80x80  
    + giant_female

TODO:

    goblin
    orc
    cyclcopes
    dwarf     <- child lumberjack
    lizardman
    zombie



"""
class SpriteLayerDef(Serializable):
    zPos: int = 0
    oversize: str = None # is oversize, "thrust" or "slash"
    male: str = ""
    female: str = ""
    child: str = ""
    pregnant: str = ""
    muscular: str = ""

class SpriteDef(Serializable):

    name: str = ""
    type_name: str = ""
    layer_1: SpriteLayerDef = None
    layer_2: SpriteLayerDef = None
    layer_3: SpriteLayerDef = None
    variants: List[str] = []

class SpritePresetVariant(Serializable):
    name: str = ""
    variant: str = ""

class SpritePreset(Serializable):

    name: str = ""
    body_type: str = ""
    layers: Dict[str, SpritePresetVariant] = None

class LPCDB(object):
    def __init__(self, path):
        super(LPCDB, self).__init__()

        self.preset_dir = os.path.join(path, "presets")
        self.preset_items_dir = os.path.join(path, "preset_items")
        self.definitions_dir = os.path.join(path, "sheet_definitions")
        self.spritesheets_dir = os.path.join(path, "spritesheets")

        if not os.path.exists(self.spritesheets_dir):
            raise FileNotFoundError(self.spritesheets_dir)

        self.types = defaultdict(dict)
        self.item_presets = defaultdict(dict)
        self.presets = dict()

        for jsname in os.listdir(self.definitions_dir):
            jspath = os.path.join(self.definitions_dir, jsname)

            with open(jspath, "r") as rf:
                text = rf.read()
                js = SpriteDef.fromJson(json.loads(text))
                self.types[js.type_name][js.name] = js

        if os.path.exists(self.preset_dir):
            for jsname in os.listdir(self.preset_dir):
                jspath = os.path.join(self.preset_dir, jsname)
                if jspath.endswith(".json"):
                    with open(jspath, "r") as rf:
                        text = rf.read()
                        preset = SpritePreset.fromJson(json.loads(text))
                        self.presets[preset.name] = preset


        if os.path.exists(self.preset_items_dir):

            for catname in os.listdir(self.preset_items_dir):
                catpath = os.path.join(self.preset_items_dir, catname)
                if not os.path.isdir(catpath):
                    continue

                for jsname in os.listdir(catpath):
                    jspath = os.path.join(catpath, jsname)
                    if jspath.endswith(".json"):
                        with open(jspath, "r") as rf:
                            text = rf.read()
                            try:
                                preset = SpritePreset.fromJson(json.loads(text))
                                self.item_presets[catname][preset.name] = preset
                            except json.decoder.JSONDecodeError:
                                print("skip: %s" % jspath)


        self.frame_counts = {
            "cast": 7,
            "thrust": 8,
            "walk": 9,
            "slash": 6,
            "shoot": 13,
            "hurt": 6,
        }

        self.animation_row = {
            "cast": {
                "north": 0,
                "west":  1,
                "south": 2,
                "east":  3,
            },
            "thrust": {
                "north": 4,
                "west":  5,
                "south": 6,
                "east":  7,
            },
            "walk": {
                "north": 8,
                "west":  9,
                "south": 10,
                "east":  11,
            },
            "slash": {
                "north": 12,
                "west":  13,
                "south": 14,
                "east":  15,
            },
            "shoot": {
                "north": 16,
                "west":  17,
                "south": 18,
                "east":  19,
            },
            "hurt": {
                "south": 20,
            }
        }

        self.oversize_thrust = {
            "thrust": {
                "north": 0,
                "west":  1,
                "south": 2,
                "east":  3,
            },
        }

        self.oversize_slash = {
            "slash": {
                "north": 0,
                "west":  1,
                "south": 2,
                "east":  3,
            },
        }

        self.cache = {}
        #self.images = self.getSprites("Humanlike", "male")

    def getBodyTypes(self):
        return ["male", "female", "male&female", "child", "pregnant", "muscular"]

    def getTypes(self):
        return list(self.types.keys())

    def getTypeNames(self, type_name):
        return list(self.types[type_name].keys())

    def hasDefinition(self, type_name, name):

        if type_name not in self.types:
            return False
        if name not in self.types[type_name]:
            return False
        return True

    def getDefinition(self, type_name, name):
        return self.types[type_name][name]

    def _getSpriteLayer(self, layer, body_type, variant):
        path = getattr(layer, body_type)
        sheet_dir = os.path.join(self.spritesheets_dir, path)
        sheet_path = os.path.join(sheet_dir, variant + ".png")
        if not os.path.exists(sheet_path):
            print("***")
            print(os.listdir(sheet_dir))
            print(variant)
            print(sheet_path)
            print("***")
            return 0, 0, {}

        size = 64
        row_data = self.animation_row
        if layer.oversize == "slash":
            size = 192
            row_data = self.oversize_slash
        elif layer.oversize == "thrust":
            size = 192
            row_data = self.oversize_thrust

        if sheet_path in self.cache:
            n_cols, n_rows, sheet = self.cache[sheet_path]
        else:
            builder = SpriteSheetBuilder() \
                .colorkey(None) \
                .offset(0, 0) \
                .spacing(0, 0) \
                .dimensions(size, size) \
                .layout(-1, -1)

            sheet = builder.build(sheet_path)
            n_cols = builder.cols
            n_rows = builder.rows
            self.cache[sheet_path] = (builder.cols, builder.rows, sheet)

        sprites = defaultdict(dict)
        for grp, info in row_data.items():
            count = self.frame_counts[grp]
            if grp == "slash" and n_cols == 9:
                count = 9

            for direction, row in info.items():
                s = row*n_cols
                e = row*n_cols + count
                frames = sheet[s:e]
                #print(grp, direction, count, "s", s, "e", e)

                if frames:

                    if len(frames) != count:
                        continue

                    if grp == "shoot":

                        sprites['shoot1_begin'][direction] = [frames[i] for i in [0, 1, 2, 3, 4, 5, 6, 7]]
                        sprites['shoot1_hold'][direction] = [frames[i] for i in [7]]
                        sprites['shoot1_end'][direction] = [frames[i] for i in [7, 8, 9, 10, 12, 2, 1, 0,]]

                    elif grp == "cast":
                        sprites['cast1_begin'][direction] = [frames[i] for i in [0, 1, 2, 3, 4, 5, 5]]
                        sprites['cast1_hold'][direction] = [frames[i] for i in [4, 4, 5, 5]]
                        sprites['cast1_end'][direction] = [frames[i] for i in [6, 2, 1, 0]]

                        sprites['cast2_begin'][direction] = [frames[i] for i in [0, 1, 2]]
                        sprites['cast2_hold'][direction] = [frames[i] for i in [2]]
                        sprites['cast2_end'][direction] = [frames[i] for i in [3, 0]]

                        sprites['stagger'][direction] = [frames[i] for i in [0, 1, 3, 6]]

                    elif grp == "thrust":
                        sprites["thrust1"][direction] = [frames[i] for i in [0, 1, 2, 3, 4, 5, 5, 4, 3, 2, 1, 0]]

                        sprites["thrust3"][direction] = [frames[i] for i in [0, 1, 2, 3, 4, 5, 5, 6, 7, 6, 5, 5, 4, 3, 2, 1, 0]]

                    elif grp == "slash":

                        # slash with 3 hits on 5 and middle 2
                        # requires an alt animation sequence for the oversize layer
                        # frames 2, 3, 4, 5 need to have a back swing
                        # to support this, the oversize file should have 6 or 10 frames
                        # 10 frame files can then generate this animation sequence


                        if n_cols == 6 or n_cols == 13:
                            # old style / original LPC slash animation sequence

                            sprites["slash1"][direction] = [frames[i] for i in [0, 1, 2, 3, 4, 5, 5, ]]

                            sprites["slash3"][direction] = [frames[i] for i in [0, 1, 2, 3, 4, 5, 4, 3, 2, 2, 3, 4, 5]]

                        elif n_cols == 9:
                            # new 'triple slash' animation

                            sprites["slash1"][direction] = [frames[i] for i in [0, 1, 2, 3, 4, 5, 5, 5, 3, 2, 1, 0]]

                            sprites["slash3"][direction] = [frames[i] for i in [0, 1, 2, 3, 4, 5, 6, 7, 8, 2, 3, 4, 5]]
                        else:
                            raise ValueError(n_rows)

                        # experimental 'thrust'
                        #frames = [frames[i] for i in [0, 1, 3, 4, 4, 3, 1, 0]]
                        #sprites["slash3"][direction] = frames

                    elif grp == "hurt":
                        sprites["hurt"][direction] = [frames[i] for i in [0, 1, 2, 3, 4, 5]]
                        sprites["down"][direction] = [frames[i] for i in [5,]]
                    else:

                        sprites[grp][direction] = frames

        return (layer.zPos, size, sprites)

    def getSprites(self, body_type, type_name, name, variant):

        #type_name = "body"
        #name = "Humanlike"
        # body_type = "male"
        body = self.types[type_name][name]
        #variant = body.variants[variant]

        variant = variant.replace(" ", "_")

        sprites = []

        if variant != "none":

            if body.layer_1:
                sprites.append(self._getSpriteLayer(body.layer_1, body_type, variant))

            if body.layer_2:
                sprites.append(self._getSpriteLayer(body.layer_2, body_type, variant))

            if body.layer_3:
                sprites.append(self._getSpriteLayer(body.layer_3, body_type, variant))

        return sprites

    def savePreset(self, preset):

        name = preset.name.replace(" ", "_") + ".json"
        path = os.path.join(self.preset_dir, name)

        if not os.path.exists(self.preset_dir):
            os.makedirs(self.preset_dir)

        with open(path, "w") as wf:
            wf.write(json.dumps(preset.toJson(), indent=2))
            wf.write("\n")

        self.presets[preset.name] = preset

    def loadPreset(self, preset):
        sprites = []
        for category, info in preset.layers.items():
            if self.hasDefinition(category, info.name):
                sprites.extend(self.getSprites(preset.body_type, category, info.name, info.variant))
        return self.flatten(sprites)

    def _getSpriteLayerPath(self, layer, body_type, variant):
        path = getattr(layer, body_type)
        sheet_dir = os.path.join(self.spritesheets_dir, path)
        sheet_path = os.path.join(sheet_dir, variant + ".png")
        return sheet_path

    def _getSpritePaths(self, body_type, type_name, name, variant):

        body = self.types[type_name][name]

        variant = variant.replace(" ", "_")



        sprites = set()

        if variant != "none":

            if body.layer_1:
                sprites.add(self._getSpriteLayerPath(body.layer_1, body_type, variant))

            if body.layer_2:
                sprites.add(self._getSpriteLayerPath(body.layer_2, body_type, variant))

            if body.layer_3:
                sprites.add(self._getSpriteLayerPath(body.layer_3, body_type, variant))

        return sprites

    def getPresetSpritePaths(self, preset):
        sprites = set()
        for category, info in preset.layers.items():
            if self.hasDefinition(category, info.name):
                sprites |= self._getSpritePaths(preset.body_type, category, info.name, info.variant)
        return sprites

    def loadPresetByName(self, preset_name):

        preset = self.presets[preset_name]

        return self.loadPreset(preset)

    def flatten(self, seq):

        # sort the sequence bu increasing z index
        seq.sort(key = lambda x: x[0])

        groups = [
            'walk',
            'thrust1',
            'thrust2',
            'thrust3',
            'slash1',
            'slash2',
            'slash3',
            'shoot1_begin', 'shoot1_hold', 'shoot1_end',
            'cast1_begin', 'cast1_hold', 'cast1_end',
            'cast2_begin', 'cast2_hold', 'cast2_end',
            'hurt',
            'down',
        ]

        # [group][direction] => animation cycle
        output = defaultdict(dict)

        for grp in groups:
            # determine largest frame size
            frame_size = 64
            for _, size, sprites in seq:
                if grp not in sprites:
                    continue
                frame_size = max(frame_size, size)
            for _, _, sprites in seq:
                if grp not in sprites:
                    continue

                for direction in ['north', 'east', 'south', 'west']:

                    if direction not in sprites[grp]:
                        continue

                    # create a blank image for each frame
                    if direction not in output[grp]:
                        temp = []
                        for i in range(len(sprites[grp][direction])):
                            s = pygame.Surface((size, size)).convert_alpha()
                            s.fill((0,0,0,0))
                            temp.append(s)
                        output[grp][direction] = temp

                    # paste frames one after another
                    for base, frame in zip(output[grp][direction], sprites[grp][direction]):
                        x = base.get_width()//2 - frame.get_width()//2
                        y = base.get_height()//2 - frame.get_height()//2
                        base.blit(frame, (x, y))



        return output

    def getItemPreset(self, category, name):
        info = self.item_presets[category][name]
        return info

    def getItemIcon(self, category, name):

        info = self.item_presets[category][name]

        png = name.replace(" ", "_") + ".png"
        path = os.path.join(self.preset_items_dir, category, png)

        sprites = SpriteSheetBuilder() \
            .offset(0,0) \
            .spacing(0,0) \
            .dimensions(48, 48) \
            .layout(1, 1) \
            .colorkey((0,255,0)) \
            .build(path)

        return sprites[0]

    def getBodyTypes(self):
        return ["male", "female"]

    def getBodyColors(self):
        body_colors = [
            'light', 'olive', 'dark', 'dark_2', 'brown', 'black',
            'darkelf_2', 'darkelf', 'zombie',
        ]
        return body_colors

    def getHairStyles(self):
        # assuming body type = male or female
        # then Hair can be one of these styles
        styles = [
            'Bangs', 'Bangs long', 'Bangs longer', 'Bangs short',
            'Bedhead', 'Bunches', 'Jewfro', 'Plain', 'Longhawk',
            'Longknot', 'Loose', 'Messy', 'Messy 2', 'Mohawk',
            'Page', 'Parted', 'Pixie', 'Ponytail', 'Ponytail 2',
            'Princess', 'Shorthawk', 'Shortknot', 'Shoulder left',
            'Shoulder right', 'Swoop', 'Unkempt', 'Extra long',
            'Extra longknot'
        ]
        return styles

    def getHairColors(self):
        # assuming body type = male or female
        # and a style form getHairStyles is used
        # then the color can be one of these
        colors = [
            'black', 'blonde', 'blonde 2', 'blue', 'blue 2', 'brown',
            'brown 2', 'brunette', 'brunette 2', 'dark blonde',
            'gold', 'gray', 'gray 2', 'green', 'green 2', 'light blonde',
            'light blonde 2', 'pink', 'pink 2', 'purple', 'raven',
            'raven 2', 'redhead', 'redhead 2', 'rubyred',
            'white blonde', 'white blonde 2', 'white cyan', 'white'
        ]
        return colors

    def getShirtColors(self):
        """
        assuming the cothing style is "Sleeved2"
        then the color can be one of these
        """
        # 'bluegray',
        colors = [
            'black', 'blue',  'forest', 'gray', 'green',
            'lavender', 'leather', 'maroon', 'navy', 'orange', 'pink',
            'purple', 'red', 'sky', 'tan', 'teal', 'walnut', 'white', 'yellow',
        ]
        return colors

    def getPantsColors(self):
        """
        assuming the cothing style is "Sleeved2"
        then the color can be one of these
        """
        colors = [
            'black', 'blue', 'bluegray', 'brown', 'charcoal', 'forest',
            'gray', 'green', 'lavender', 'leather', 'magenta', 'maroon',
            'navy', 'orange', 'pink', 'purple', 'red', 'rose', 'sky',
            'slate', 'tan', 'teal', 'walnut', 'white', 'yellow',
        ]
        return colors

    def getShoeColors(self):
        # Shoes
        colors = ["brown"]
        return colors

    def export(self):
        # return just the list of paths that are actually used.

        sprite_paths = set()

        # get all sprite sheets used by presets

        for name, preset in self.presets.items():
            sprite_paths |= self.getPresetSpritePaths(preset)

        # get all sprite sheets used by items
        for _, data in self.item_presets.items():
            for name, preset in data.items():
                for body_type in self.getBodyTypes():
                    for type_name, info in preset.layers.items():
                        variant = info.variant.replace(" ", "_")
                        if variant == "none":
                            continue
                        sprite_paths |= self._getSpritePaths(body_type, type_name, info.name, variant)

        # the default player character pulls from these variants.

        for body_type in self.getBodyTypes():

            type_name = "body"
            name = "Humanlike"
            for variant in self.getBodyColors():
                variant = variant.replace(" ", "_")
                sprite_paths |= self._getSpritePaths(body_type, type_name, name, variant)

            type_name = "hair"
            for name in self.getHairStyles():
                for variant in self.getHairColors():
                    variant = variant.replace(" ", "_")
                    sprite_paths |= self._getSpritePaths(body_type, type_name, name, variant)

            type_name = "clothes"
            name = "Sleeved2"
            for variant in self.getShirtColors():
                variant = variant.replace(" ", "_")
                sprite_paths |= self._getSpritePaths(body_type, type_name, name, variant)

            type_name = "legs"
            name = "Pants"
            for variant in self.getPantsColors():
                variant = variant.replace(" ", "_")
                sprite_paths |= self._getSpritePaths(body_type, type_name, name, variant)

            type_name = "shoes"
            name = "Shoes"
            for variant in self.getShoeColors():
                variant = variant.replace(" ", "_")
                sprite_paths |= self._getSpritePaths(body_type, type_name, name, variant)

        out = {}
        for path in sorted(sprite_paths):
            dirpath, filename = os.path.split(path)
            if dirpath not in out:
                out[dirpath] = []
            out[dirpath].append(path)

        return out


def update_items():

    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.init()
    pygame.display.init()
    screen = pygame.display.set_mode((1,1))

    db = LPCDB("LPC/Universal-LPC-Spritesheet-Character-Generator/")

    for category, grp in db.item_presets.items():
        for name, info in grp.items():
            print(category, name)
            sprites = db.loadPreset(info)

            name = name.replace(" ", "_")
            path = os.path.join(db.preset_items_dir, category, name + ".png")
            if not os.path.exists(path):
                # TODO: different categories should use different frames
                # by default and use different crop rects
                if category == "head":
                    frame = sprites['walk']['east'][0]
                    frame = frame.subsurface(pygame.Rect(8, 0, 48, 48))
                elif category == "body":
                    frame = sprites['walk']['south'][0]
                    frame = frame.subsurface(pygame.Rect(8,16, 48, 48))
                elif category == "legs":
                    frame = sprites['walk']['south'][0]
                    frame = frame.subsurface(pygame.Rect(8,16, 48, 48))
                elif category == "shoes":
                    frame = sprites['walk']['south'][0]
                    frame = frame.subsurface(pygame.Rect(8,16, 48, 48))
                else:
                    frame = sprites['walk']['south'][0]
                    frame = frame.subsurface(pygame.Rect(8, 8, 48, 48))

                print(path)
                pygame.image.save(frame, path)


def get_hair():

    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.init()
    pygame.display.init()
    screen = pygame.display.set_mode((1,1))

    db = LPCDB("./")

    # first get a rough idea of available styles and available colors
    styles = []
    variant_counts = defaultdict(int)
    for name, info in db.types['hair'].items():

        if not info.layer_1.male or not info.layer_1.female:
            print("x", name)
        elif len(info.variants) < 20:
            print("v", name, len(info.variants))
        elif name in ['Curly', 'Single', 'Braid']:
            print("s", name, len(info.variants))
        else:
            print(" ", name, len(info.variants))
            styles.append(name)
            for variant in info.variants:
                variant_counts[variant] += 1


    # colors = [variant for variant, count in variant_counts.items() if count > 20]

    # check that for a given style all colors are valid
    # this list was manually paired down until any combination would be valid
    styles = ['Bangs', 'Bangs long', 'Bangs longer', 'Bangs short', 'Bedhead', 'Bunches', 'Jewfro', 'Plain', 'Longhawk', 'Longknot', 'Loose', 'Messy', 'Messy 2', 'Mohawk', 'Page', 'Parted', 'Pixie', 'Ponytail', 'Ponytail 2', 'Princess', 'Shorthawk', 'Shortknot', 'Shoulder left', 'Shoulder right', 'Swoop', 'Unkempt', 'Extra long', 'Extra longknot']
    colors = ['black', 'blonde', 'blonde 2', 'blue', 'blue 2', 'brown', 'brown 2', 'brunette', 'brunette 2', 'dark blonde', 'gold', 'gray', 'gray 2', 'green', 'green 2', 'light blonde', 'light blonde 2', 'pink', 'pink 2', 'purple', 'raven', 'raven 2', 'redhead', 'redhead 2', 'rubyred', 'white blonde', 'white blonde 2', 'white cyan', 'white']
    print(styles)
    print("------------")
    for name, info in db.types['hair'].items():
        if not info.layer_1.male or not info.layer_1.female:
            pass
        elif len(info.variants) < 20:
            pass
        elif name in ['Curly', 'Single', 'Braid']:
            pass
        else:
            for color in colors:
                if color not in info.variants:
                    print(info.name, color)



    print()

def main():
    #update_items()
    get_hair()



if __name__ == '__main__':
    main()
