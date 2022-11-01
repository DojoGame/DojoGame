# dojogame.py
# This file contains the base of the engine.
# This file acts as a link between all submodules

from dojogame.physics import *
from dojogame.graphics import *
from dojogame.data import *
from dojogame import constants


def init():
    pygame.init()
    RealTime.init()
    Input.update()
