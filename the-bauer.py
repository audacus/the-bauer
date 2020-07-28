from oxocard import *
from oxocardext import *
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
Orientation = Enum("EAST", "SOUTH", "WEST", "NORTH", "NONE")
Difference = Enum("SAME", "LEFT", "RIGHT", "OPPOSITE")
Direction = Enum("STRAIGHT", "LEFT", "RIGHT")
Gear = Enum("FORWARD", "NEUTRAL", "REVERSE")

# basic initializations
enableRepaint(False)
INTERVALL = 3.0
accelerometerThreshold = 9
FIELD_WIDTH = 8
FIELD_HEIGHT = 8
# colors
COL_BLACK = 0x000000
COL_WHITE = 0xffffff
COL_BLUE =  0x0000ff
COL_RED =   0xff0000
COL_BEIGE = 0xffee88
COL_BROWN = 0x85734d
# tractor colors
COL_TRAC_MOW_FRONT = COL_BLUE
COL_TRAC_MOW_BACK = COL_WHITE
COL_TRAC_GATHER_FRONT = COL_RED
COL_TRAC_GATHER_BACK = COL_WHITE
# field colors
COL_FIELD_GROWN = COL_BEIGE
COL_FIELD_MOWN = COL_BROWN

# classes
class Oxocard():
    def __init__(self, accelerometerThreshold):
        self.threshold = accelerometerThreshold
        self.acc = Accelerometer.create()
        self.R1 = Button(BUTTON_R1)

    def getOrientation(self):
        orientation = Orientation.NONE
        # west < 0 < east
        roll = self.acc.getRoll()
        rollAbs = abs(roll)
        # north < 0 < south
        pitch = self.acc.getPitch()
        pitchAbs = abs(pitch)
        # check west/east
        if rollAbs > pitchAbs and rollAbs > self.threshold:
            if roll < 0:
                orientation = Orientation.WEST
            else:
                orientation = Orientation.EAST
        # check north/south
        elif pitchAbs > rollAbs and pitchAbs > self.threshold:
            if pitch < 0:
                orientation = Orientation.NORTH
            else:
                orientation = Orientation.SOUTH

        return orientation

    def getDifference(self, one, two):
        diff = Difference.SAME

        if (one != Orientation.NONE and two != Orientation.NONE):
            # map orientations to degrees
            orientSwitcher = {
                Orientation.NORTH: 0,
                Orientation.EAST: 90,
                Orientation.SOUTH: 180,
                Orientation.WEST: 270
            }
            # map degree differences to direction differences
            diffSwitcher = {
                0: Difference.SAME,
                90: Difference.RIGHT,
                180: Difference.OPPOSITE,
                -180: Difference.OPPOSITE,
                -90: Difference.LEFT
            }
            # calculate direction difference
            alpha = orientSwitcher.get(one, 0)
            beta = orientSwitcher.get(two, 0)
            diff = diffSwitcher.get(beta - alpha % 360, Difference.SAME)

        return diff


class Field():
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.resetField()

    def resetField(self):
        # array with width * height zeroes (not mowed)
        self.field = [0] * (self.width * self.height)

class Bauer():
    def __init__(self, step, intervall):
        self.step = step
        self.intervall = intervall
        self.oxo = Oxocard(accelerometerThreshold)
        self.field = Field(FIELD_WIDTH, FIELD_HEIGHT)
        self.tractor = Tractor(COL_TRAC_MOW_BACK, COL_TRAC_MOW_FRONT, Orientation.EAST, Direction.STRAIGHT, Gear.NEUTRAL)

    def update(self):
        print("step: " + Step.string[self.step])

        if self.oxo.R1.isPressed():
            self.step = Step.BYE

        self.tractor.update()
        self.draw()

        # TODO: add condition for next step
        self.nextStep()
        sleep(self.intervall)

    # draw display
    def draw(self):
        width = self.field.width
        height = self.field.height

        dots = (width * height)
        matrix = [[COL_BLACK for i in range(width)] for j in range(height)]

        for i in range(dots):
            x = i % width
            y = int(i / width)

            # mowed field
            if self.field.field[i] == 1:
                color = COL_FIELD_MOWN
            # grown field
            else:
                color = COL_FIELD_GROWN

            # check if tractor
            # back 1
            if self.tractor.elements[0][0] == x and self.tractor.elements[0][1] == y:
                color = self.tractor.colorBack
            # front 1
            elif self.tractor.elements[1][0] == x and self.tractor.elements[1][1] == y:
                color = self.tractor.colorFront
            # back 2
            elif self.tractor.elements[2][0] == x and self.tractor.elements[2][1] == y:
                color = self.tractor.colorBack
            # front 2
            elif self.tractor.elements[3][0] == x and self.tractor.elements[3][1] == y:
                color = self.tractor.colorFront
            # set color
            matrix[y][x] = color
        # paint whole matrix
        image(matrix)
        repaint()

    def nextStep(self):
        # welcome
        if bauer.step == Step.HELLO:
            self.step = Step.GROW
        # grow field
        elif bauer.step == Step.GROW:
            self.step = Step.MOW
        # mow field
        elif bauer.step == Step.MOW:
            self.step = Step.GATHER
        # gather hay balls
        elif bauer.step == Step.GATHER:
            self.step = Step.GROW

    def hello(self):
        # bigTextScroll("Welcome to: THE BAUER   ")
        self.update()

    def bye(self):
        # bigTextScroll("Au revoir!   ")
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
        self.oxo = Oxocard(accelerometerThreshold)
        self.resetPosition()

    def lineUp(self):
        self.resetPosition()
        # TODO: drive onto field (staging)

    def resetPosition(self):
        # back/front
        # [0][1] -->
        # [2][3] -->
        # self.elements = [[-2, 0], [-1, 0], [-2, 1], [-1, 1]]
        self.elements = [[0, 0], [1, 0], [0, 1], [1, 1]]

    def update(self):
        self.updateGear()
        self.updateDirection()

    def updateGear(self):
        orientOxo = self.oxo.getOrientation()
        # if no oxocard orientation -> stop
        if orientOxo == Orientation.NONE:
            self.gear = Gear.NEUTRAL
        else:
            diff = self.oxo.getDifference(self.orientation, orientOxo)
            # forward
            if diff == Difference.SAME:
                # if reversing -> stop
                if self.gear == Gear.REVERSE:
                    self.gear = Gear.NEUTRAL
                # if already stopped -> forward
                elif self.gear == Gear.NEUTRAL:
                    self.gear = Gear.FORWARD
            # reverse
            elif diff == Difference.OPPOSITE:
                # if driving forward -> stop
                if self.gear == Gear.FORWARD:
                    self.gear = Gear.NEUTRAL
                # if already stopped -> revert
                elif self.gear == Gear.NEUTRAL:
                    self.gear = Gear.REVERSE
        print(Gear.string[self.gear])

    def updateDirection(self):
        orientOxo = self.oxo.getOrientation()
        # TODO:


# game loop
bauer = Bauer(Step.HELLO, INTERVALL)
repeat:
    # welcome
    if bauer.step == Step.HELLO:
        bauer.hello()
    # grow field
    elif bauer.step == Step.GROW:
        bauer.grow()
    # mow field
    elif bauer.step == Step.MOW:
        bauer.mow()
    # gather hay balls
    elif bauer.step == Step.GATHER:
        bauer.gather()
    # exit
    elif bauer.step == Step.BYE:
        bauer.bye()
        break
