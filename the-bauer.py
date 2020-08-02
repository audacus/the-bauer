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
INTERVALL = 1.0
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
                270: Difference.LEFT,
                360: Difference.SAME
            }
            # calculate direction difference
            alpha = orientSwitcher.get(one, 0)
            beta = orientSwitcher.get(two, 0)
            phi = beta - alpha % 360
            phi = phi if phi > 0 else 360 + phi
            diff = diffSwitcher.get(phi, Difference.SAME)

        return diff

    def getOrientationFromDifference(self, orient, diff):
        orientSwitcher = {
            Orientation.NORTH: 0,
            Orientation.EAST: 90,
            Orientation.SOUTH: 180,
            Orientation.WEST: 270
        }
        diffSwitcher = {
            Difference.SAME: 0,
            Difference.RIGHT: 90,
            Difference.OPPOSITE: 180,
            Difference.LEFT: -90
        }
        degSwitcher = {
            0: Orientation.NORTH,
            90: Orientation.EAST,
            180: Orientation.SOUTH,
            270: Orientation.WEST,
            -90: Orientation.WEST
        }

        # get degree value of orientation
        degOrient = orientSwitcher.get(orient, 0)
        # get degree operand of difference
        degDiff = diffSwitcher.get(diff, 0)
        # calculate new degree value and get corresponding orientation
        phi = (degOrient + degDiff) % 360
        return degSwitcher.get(phi, Orientation.NONE)

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
        self.trac = Tractor(COL_TRAC_MOW_BACK, COL_TRAC_MOW_FRONT, Orientation.EAST, Direction.STRAIGHT, Gear.NEUTRAL)

    def update(self):
        print("step: " + Step.string[self.step])

        if self.oxo.R1.isPressed():
            self.step = Step.BYE

        self.trac.update()
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
            # back left
            if self.trac.elements[self.trac.iBL][self.trac.iX] == x and self.trac.elements[self.trac.iBL][self.trac.iY] == y:
                color = self.trac.colorBack
            # front left
            elif self.trac.elements[self.trac.iFL][self.trac.iX] == x and self.trac.elements[self.trac.iFL][self.trac.iY] == y:
                color = self.trac.colorFront
            # back right
            elif self.trac.elements[self.trac.iBR][self.trac.iX] == x and self.trac.elements[self.trac.iBR][self.trac.iY] == y:
                color = self.trac.colorBack
            # front right
            elif self.trac.elements[self.trac.iFR][self.trac.iX] == x and self.trac.elements[self.trac.iFR][self.trac.iY] == y:
                color = self.trac.colorFront
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
        # axis indices
        # [X, Y]
        self.iX = 0
        self.iY = 1
        # element indices
        # [BL][FL] -->
        # [BR][FR] -->
        self.iBL = 0
        self.iFL = 1
        self.iBR = 2
        self.iFR = 3
        # elements
        self.elements = [[0, 0], [1, 0], [0, 1], [1, 1]]
        # colors
        self.colorBack = colorBack
        self.colorFront = colorFront

        # difference between orientation of tractor and orientation of oxocard
        self.difference = Difference.SAME
        # driving state (forward, reverse, neutral)
        self.gear = gear
        self.invert = False
        # orientation of vehicle in the field (N, E, S, W)
        self.orientation = orientation
        # direction of travel (forward, right, left)
        self.direction = direction

        self.oxo = Oxocard(accelerometerThreshold)

        self.resetPosition()

    def lineUp(self):
        self.resetPosition()
        # TODO: drive onto field (staging)

    def resetPosition(self):
        # self.elements = [[-2, 0], [-1, 0], [-2, 1], [-1, 1]]
        self.elements = [[0, 0], [1, 0], [0, 1], [1, 1]]

    def update(self):
        self.updateDifference()
        self.updateGear()
        self.updateDirection()
        self.updateElements()

    def updateDifference(self):
        self.difference = self.oxo.getDifference(self.orientation, self.oxo.getOrientation())

    def updateGear(self):
        orientOxo = self.oxo.getOrientation()
        # if no oxocard orientation -> stop
        if orientOxo == Orientation.NONE:
            self.gear = Gear.NEUTRAL
            self.invert = False
        else:
            # forward
            if self.difference == Difference.SAME and not self.invert:
                # if reversing -> stop
                if self.gear == Gear.REVERSE:
                    self.gear = Gear.NEUTRAL
                # if already stopped -> forward
                elif self.gear == Gear.NEUTRAL:
                    self.gear = Gear.FORWARD
            # reverse
            elif self.difference == Difference.OPPOSITE:
                # if driving forward -> stop
                if self.gear == Gear.FORWARD:
                    self.gear = Gear.NEUTRAL
                # if already stopped -> revert
                elif self.gear == Gear.NEUTRAL:
                    self.gear = Gear.REVERSE

    def updateDirection(self):
        # change direction only when moving
        if self.gear == Gear.FORWARD or self.gear == Gear.REVERSE:
            if self.difference == Difference.SAME or self.difference == Difference.OPPOSITE:
                self.direction = Direction.STRAIGHT
            elif self.difference == Difference.RIGHT:
                self.direction = Direction.RIGHT
            elif self.difference == Difference.LEFT:
                self.direction = Direction.LEFT

    def updateElements(self):
        move = self.oxo.getOrientationFromDifference(self.orientation, self.difference)
        if self.gear == Gear.FORWARD:
            if self.direction == Direction.STRAIGHT:
                self.moveElements(move, 1)
                self.invert = False
            elif self.direction == Direction.LEFT:
                self.goLeft()
                self.orientation = move
            elif self.direction == Direction.RIGHT:
                self.goRight()
                self.orientation = move
        elif self.gear == Gear.REVERSE:
            # invert movement
            if self.direction == Direction.STRAIGHT:
                if self.invert:
                    move = self.oxo.getOrientationFromDifference(move, Difference.OPPOSITE)
                self.moveElements(move, 1)
            elif self.direction == Direction.LEFT:
                if self.invert:
                    self.goRight()
                    move = self.oxo.getOrientationFromDifference(move, Difference.OPPOSITE)
                else:
                    self.goLeft()
                self.orientation = move
                self.invert = True
            elif self.direction == Direction.RIGHT:
                if self.invert:
                    move = self.oxo.getOrientationFromDifference(move, Difference.OPPOSITE)
                    self.goLeft()
                else:
                    self.goRight()
                self.orientation = move
                self.invert = True

    def goLeft(self):
        elBL = self.elements[self.iBR]
        elFL = self.elements[self.iBL]
        elBR = self.elements[self.iFR]
        elFR = self.elements[self.iFL]
        self.elements[self.iBL] = elBL
        self.elements[self.iFL] = elFL
        self.elements[self.iBR] = elBR
        self.elements[self.iFR] = elFR

    def goRight(self):
        elBL = self.elements[self.iFL]
        elFL = self.elements[self.iFR]
        elBR = self.elements[self.iBL]
        elFR = self.elements[self.iBR]
        self.elements[self.iBL] = elBL
        self.elements[self.iFL] = elFL
        self.elements[self.iBR] = elBR
        self.elements[self.iFR] = elFR


    def moveElements(self, orient, amount):
        # define how to alter element values
        # [x, y]
        moveSwitcher = {
            Orientation.NORTH: [0, -amount],
            Orientation.EAST: [amount, 0],
            Orientation.SOUTH: [0, amount],
            Orientation.WEST: [-amount, 0]
        }
        movement = moveSwitcher.get(orient, [0, 0])
        # alter each element
        for el in self.elements:
            el[self.iX] = el[self.iX] + movement[self.iX]
            el[self.iY] = el[self.iY] + movement[self.iY]


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
