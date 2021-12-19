Universal LPC Spritesheet Character Generator
=============================================

Based on [Universal LPC Spritesheet](https://github.com/jrconway3/Universal-LPC-spritesheet).
Forked from [Universal LPC Spritesheet](https://github.com/sanderfrenken/Universal-LPC-spritesheet).

This project expands on prior work by adding classes for loading the sprites with pygame.

The Liberated Pixel Effort is a collaborative effort from a number of different great artists who helped produce sprites for the project.
**If you wish to use LPC sprites in your project, you will need to credit everyone who helped contribute to the LPC sprites you are using.** See below for how to do this.

### List of changes

- LPC Database class for loading sprites in Python
- PyGame Gui for visualizing the sprites
- scripts for manipulating the sprite sheets
- changed oversize slash animation from 6 to 9 sprites to allow for a back swing
This allows a chaining animation for 2 or more slashes in a row.
- new animation for axe
- new animation for pickaxe
- added new weapons for oversize layers slash and thrust

[Live Demo](https://sanderfrenken.github.io/Universal-LPC-Spritesheet-Character-Generator/)

### Licensing and Attribution (Credits)

All art distributed with this project (all images in the `spritesheets` subdirectory) is licensed under the [GNU GPL 3.0](http://www.gnu.org/licenses/gpl-3.0.html) ([text](gpl-3_0.txt)) and/or [Creative Commons Attribution-ShareAlike 3.0](http://creativecommons.org/licenses/by-sa/3.0/) ([text](cc-by-sa-3_0.txt)) license(s). Some art may be available under other licenses too.

The file `CREDITS.csv` lists the authors, license(s), and links to the original URL(s), for each image in `spritesheets`. **If you generate a sprite using this tool, you must credit all the authors**. You can do this one of two ways:

- Distribute the entire `CREDITS.csv` file along with your project.
- Based on the layers you use, copy the appropriate rows from `CREDITS.csv` into a new file and distribute that file with your project.

Either way, make sure this credits file is accessible from within your game or app and can be reasonably discovered by users (for instance, show the information on the "Credits" screen directly, or provide a visible link). If you don't want to *show* the entire credits file directly, should include a statement like this on your credits screen:

> Sprites by: David Conway Jr. (JaidynReiman), Nila122, Johannes Sjölund (wulax), Stephen Challener (Redshrike), Luke Mehl, Michael Whitlock (bigbeargames), Matthew Krohn (makrohn), Carlo Enrico Victoria (Nemisys), Thane Brimhall (pennomi), kheftel, Marcel van de Steeg (MadMarcel), Mark Weyer, Lanea Zimmerman (Sharm), Manuel Riecke (MrBeast), Charles Sanchez (CharlesGabriel), Zi Ye, Benjamin K. Smith (BenCreating), William.Thompsonj, Sander Frenken (castelonia), dalonedrau, ElizaWy, Evert, Daniel Eddeland (daneeklu), Durrani, MuffinElZangano, Pierre Vigier (pvigier), bluecarrot16, Rhimlock, laetissima, kirts, Joe White, Mandi Paugh, Barbara Riviera, cilekli, thecilekli, DarkwallLKE, Shaun Williams, Tuomo Untinen (reemax), Stafford McIntyre, PlatForge project, Tracy, Fabzy, Johannes Sjölund (wulax), drjamgo@hotmail.com, Lori Angela Nagel (jastiv), gr3yh47, pswerlang, XOR, tskaufma, Inboxninja, Dr. Jamgo, LordNeo
> Sprites contributed as part of the Liberated Pixel Cup project from OpenGameArt.org: http://opengameart.org/content/lpc-collection
> License: Creative Commons Attribution-ShareAlike 3.0 (CC-BY-SA 3.0) <http://creativecommons.org/licenses/by-sa/3.0/>
> Detailed credits: [LINK TO CREDITS.CSV FILE]

We are working on allowing the generator to build a customized credits file for you.

### Contributing

**Important: all art submitted to this project must be available under the [Creative Commons Attribution-ShareAlike 3.0](http://creativecommons.org/licenses/by-sa/3.0/) and/or the [GNU GPL 3.0](http://www.gnu.org/licenses/gpl-3.0.html) licenses**.
- **By contributing original work to this project, you agree to license any orginal contributions made by you under _both_ of these licenses.**
- If you are submitting art that was made by (or derived from work made by) someone else, please be sure that you have the rights to distribute that art under one of the two licenses.

When adding files to the project, please add a row to `CREDITS.csv` for each file you add. Note the entire list of authors for that image, a URL for each piece of art from which this image is derived, and a list of licenses under which the art is available.

To add sheets to an existing category, add the sheets to the correct folder(s) in `spritesheets/`.
In addition, locate the correct `sheet_definition` in `sheet_definitions/`, and add the name of your added sheet to the `variants` array.

To add a new category, add the sheets to the correct folder(s) in `spritesheets/`.
In addition, create a json file in `sheet_definitions/`, and define the required properties.
For example, you have created at this point:

`body_robot.json`

A category can exist of n-layers. For each layer, define the z-position the sheet needs to be drawn at.
For an example of a multi-layered definition, refer here [here](https://github.com/sanderfrenken/Universal-LPC-Spritesheet-Character-Generator/blob/master/sheet_definitions/body_wolfman.json).

To run this project, just clone the repo and open ``index.html`` in your browser of choice.

### Run

```bash
    python -m lpc_animator
```

