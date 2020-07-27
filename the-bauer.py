from oxocard import *
from oxobutton import *
from oxoaccelerometer import *
from math import *

# implement enum
def Enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    reverse = dict((value, key) for key, value in enums.items())
    enums["string"] = reverse
    return type("Enum", (), enums)

# enums
Step = Enum("HELLO", "GROW", "MOW", "GATHER", "BYE")
Orientation = Enum("EAST", "SOUTH", "WEST", "NORTH")
Direction = Enum("STRAIGHT", "LEFT", "RIGHT")
Gear = Enum("FORWARD", "REVERSE")

# basic initializations
intervall = 0.5
acc = Accelerometer.create()
buttonR1 = Button(BUTTON_R1)

# classes
class Bauer():
    def __init__(self, step, intervall):
        self.step = step
        self.intervall = intervall

    def update(self):
        print("step: " + Step.string[self.step])
        if buttonR1.isPressed():
            self.bye()
        sleep(self.intervall)

    def hello(self):
        bigTextScroll("Welcome to: THE BAUER   ")
        self.update()

    def bye(self):
        bigTextScroll("Au revoir!   ")
        self.update()

    def grow(self):
        self.update()

    def mow(self):
        self.update()

    def gather(self):
        self.update()

class Tractor():
    def __init__(self, colorBack, colorFront, orientation, direction, gear):
        self.colorBack = colorBack
        self.colorFront = colorFront
        self.orientation = orientation
        self.direction = direction
        self.gear = gear

# game loop
bauer = Bauer(Step.HELLO, intervall)
repeat:
    # welcome
    if bauer.step == Step.HELLO:
        bauer.hello()
        bauer.step = Step.GROW
    # grow field
    elif bauer.step == Step.GROW:
        bauer.grow()
        bauer.step = Step.MOW
    # mow field
    elif bauer.step == Step.MOW:
        bauer.mow()
        bauer.step = Step.GATHER
    # gather hay balls
    elif bauer.step == Step.GATHER:
        bauer.gather()
        bauer.step = Step.GROW

