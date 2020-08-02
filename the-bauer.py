from oxocard import *
from oxocardext import *
from oxobutton import *
from oxoaccelerometer import *
from math import *
from random import randrange

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
COL_BLACK =   0x000000
COL_WHITE =   0xffffff
COL_RED =     0xff0000
COL_GREEN =   0x198a00
COL_BLUE =    0x003e8a
COL_YELLOW =  0xffeb36
COL_BROWN =   0x695a3c
COL_GROW_01 = 0x756644
COL_GROW_02 = 0x82734c
COL_GROW_03 = 0x8e7f54
COL_GROW_04 = 0x9b8c5c
COL_GROW_05 = 0xa79864
COL_GROW_06 = 0xb4a56d
COL_GROW_07 = 0xc0b275
COL_GROW_08 = 0xcdbe7d
COL_GROW_09 = 0xd9cb85
COL_GROW_10 = 0xe6d78d
COL_GROW_11 = 0xf2e495
COL_BEIGE =   0xfff19e
COL_HAYBALL = COL_YELLOW
# tractor colors
COL_TRAC_MOW_FRONT = COL_BLUE
COL_TRAC_MOW_BACK = COL_WHITE
COL_TRAC_GATHER_FRONT = COL_GREEN
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
        self.orientation = Orientation.NONE

    def update(self):
        self.orientation = self.getOrientation()

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

class Color():

    def __init__(self):
        # indices
        self.R = 0
        self.G = 1
        self.B = 2

    def getRgbArray(self, h):
        return [
            int(str(hex(h))[2:4], 16),
            int(str(hex(h))[4:6], 16),
            int(str(hex(h))[6:9], 16)
        ]

    def getRgbStepSizes(self, start, target, steps):
        # get rgb values of start and target color
        intStart = self.getRgbArray(start)
        intTarget = self.getRgbArray(target)

        # get difference between start and target color
        diff = [
            intTarget[self.R] - intStart[self.R],
            intTarget[self.G] - intStart[self.G],
            intTarget[self.B] - intStart[self.B]
        ]

        # calculate steps
        return [
            diff[self.R] / steps,
            diff[self.G] / steps,
            diff[self.B] / steps
        ]

class Field():
    def __init__(self, width, height, colorMown, colorGrown):
        # flags
        self.MOWN = 0
        self.MAX_MOWN = 3
        self.GROWN = 10
        self.MAX_GROWN = 12
        self.HAYBALL = 15

        self.width = width
        self.height = height

        self.colMown = colorMown
        self.colGrown = colorGrown

        self.dots = []

        self.color = Color()
        self.colorSteps = self.color.getRgbStepSizes(self.colMown, self.colGrown, self.MAX_GROWN)

        self.reset()

    def reset(self):
        # array with width * height times a number between 0 and 3
        for i in range(self.width * self.height):
            self.dots.append(randrange(self.MAX_MOWN))

    def grow(self):
        for i in range(len(self.dots)):
            # grow all dots that are not yet growed
            if self.dots[i] < self.GROWN:
                self.dots[i] = self.dots[i] + randrange(3)
        return True

    def isGrown(self):
        for i in range(len(self.dots)):
            # check if all dots are grown
            if self.dots[i] < self.GROWN:
                return False
        return True

    def isMown(self):
        for i in range(len(self.dots)):
            # check all dots if mowed or hayball
            if self.dots[i] > self.MAX_MOWN and self.dots[i] != self.HAYBALL:
                return False
        return True

    def isGathered(self):
        for i in range(len(self.dots)):
            # check all dots if mowed (no hayball)
            if self.dots[i] <= self.MAX_MOWN:
                return
        return True

    def getColorComplex(self, dot):
        mownInt = self.color.getRgbArray(self.colMown)

        # calculate target hex values
        targetHex = [
            str(hex(int(mownInt[self.color.R] + (self.colorSteps[self.color.R] * dot))))[2:],
            str(hex(int(mownInt[self.color.G] + (self.colorSteps[self.color.G] * dot))))[2:],
            str(hex(int(mownInt[self.color.B] + (self.colorSteps[self.color.B] * dot))))[2:]
        ]

        # double hex value if just single symbol
        for i in (self.color.R, self.color.G, self.color.B):
            if len(targetHex[i]) < 2:
                targetHex[i] = targetHex[i] + targetHex[i]

        targetString = "0x" + targetHex[self.color.R] + targetHex[self.color.G] + targetHex[self.color.B]
        target = hex(int(targetString, 16))

        return target

    def getColor(self, dot):
        colors = [
            COL_BROWN,
            COL_GROW_01,
            COL_GROW_02,
            COL_GROW_03,
            COL_GROW_04,
            COL_GROW_05,
            COL_GROW_06,
            COL_GROW_07,
            COL_GROW_08,
            COL_GROW_09,
            COL_GROW_10,
            COL_GROW_11,
            COL_BEIGE
        ]
        return colors[dot]

class Bauer():
    def __init__(self, step, intervall):
        self.step = step
        self.intervall = intervall
        self.oxo = Oxocard(accelerometerThreshold)
        self.field = Field(FIELD_WIDTH, FIELD_HEIGHT, COL_FIELD_MOWN, COL_FIELD_GROWN)
        self.trac = Tractor(COL_TRAC_MOW_BACK, COL_TRAC_MOW_FRONT, Orientation.EAST, Direction.STRAIGHT, Gear.NEUTRAL)
        self.offsetIsGrown = 3
        self.offsetIsMown = 3
        self.offsetIsGathered = 3
        self.matrix = [[COL_BLACK for i in range(self.field.width)] for j in range(self.field.height)]

    def update(self):
        print("step: " + Step.string[self.step])

        if self.oxo.R1.isPressed():
            self.step = Step.BYE

        if self.step == Step.GROW:
            self.field.grow()
        elif self.step == Step.MOW or self.step == Step.GATHER:
            # stage tractor
            if self.trac.staging:
                self.trac.stage()
            else:
                self.trac.update()

        self.draw()

        self.nextStep()

        sleep(self.intervall)

    # draw display
    def draw(self):
        width = self.field.width
        height = self.field.height

        for i in range(len(self.field.dots)):
            color = COL_FIELD_MOWN

            dot = self.field.dots[i]
            # flag if dot ist mown
            mowed = False
            x = i % width
            y = int(i / width)

            # hayball dot
            if dot == self.field.HAYBALL:
                color = COL_HAYBALL
            # grown / mowed dot
            else:
                color = self.field.getColor(dot)

            # check if tractor
            # back left
            if self.trac.elements[self.trac.iBL][self.trac.iX] == x and self.trac.elements[self.trac.iBL][self.trac.iY] == y:
                color = self.trac.colorBack
                if self.step == Step.MOW:
                    mowed = True
            # front left
            elif self.trac.elements[self.trac.iFL][self.trac.iX] == x and self.trac.elements[self.trac.iFL][self.trac.iY] == y:
                color = self.trac.colorFront
                if self.step == Step.MOW:
                    mowed = True
            # back right
            elif self.trac.elements[self.trac.iBR][self.trac.iX] == x and self.trac.elements[self.trac.iBR][self.trac.iY] == y:
                color = self.trac.colorBack
                if self.step == Step.MOW:
                    mowed = True
            # front right
            elif self.trac.elements[self.trac.iFR][self.trac.iX] == x and self.trac.elements[self.trac.iFR][self.trac.iY] == y:
                color = self.trac.colorFront
                if self.step == Step.MOW:
                    mowed = True
            # set color
            self.matrix[y][x] = color

            # check if dot got mowed
            if self.step == Step.MOW and dot != self.field.HAYBALL and mowed:
                if i >= 9 and self.isHayball(x, y):
                    dot = self.field.HAYBALL
                else:
                    dot = randrange(self.field.MAX_MOWN)

            self.field.dots[i] = dot


        # paint whole matrix
        image(self.matrix)
        repaint()

    def isHayball(self, x, y):
        hayball = False
        # counter for mowed neighbours
        counter = 0
        # verify hayball
        # [x-1/y-1][x+0/y-1][x+1/y-1]
        # [x-1/y-0][x+0/y+0][x+1/y+0]
        # [x-1/y+1][x+0/y+1][x+1/y+1]
        for iY in range(-1, 2):
            for iX in range(-1, 2):
                factorY = y+iY
                factorX = x+iX
                if factorX >= 0 and factorX < self.field.width and factorY >= 0 and factorY < self.field.height:
                    i = (factorY * self.field.width) + (factorX)
                    if i >= 0 and i < self.field.width * self.field.height:
                        # there must not by any hayball in the sourrounding dots
                        if self.field.dots[i] == self.field.HAYBALL:
                            return False
                        # count sourrounding mowed dots
                        elif self.field.dots[i] <= self.field.MAX_MOWN:
                            counter = counter + 1
                        # if 3 sourrounding dots are mowed -> is hayball (if no hayball is in sourroundings)
                        if counter == 3:
                            hayball = True
        return hayball

    def nextStep(self):
        # welcome
        if bauer.step == Step.HELLO:
            self.step = Step.GROW
        # grow field
        elif bauer.step == Step.GROW:
            if self.field.isGrown():
                if self.offsetIsGrown > 0:
                    self.offsetIsGrown = self.offsetIsGrown - 1
                else:
                    self.step = Step.MOW
                    bigTextScroll("  Mow!   ")
                    self.trac.reset()
        # mow field
        elif bauer.step == Step.MOW:
            if self.field.isMown():
                if self.offsetIsMown > 0:
                    self.offsetIsMown = self.offsetIsMown - 1
                else:
                    self.step = Step.GATHER
                    bigTextScroll("  Gather!   ")
                    self.trac = Tractor(COL_TRAC_GATHER_BACK, COL_TRAC_GATHER_FRONT, Orientation.EAST, Direction.STRAIGHT, Gear.NEUTRAL)
        # gather hay balls
        elif bauer.step == Step.GATHER:
            if self.field.isGathered():
                if self.offsetIsGathered > 0:
                    self.offsetIsGathered = self.offsetIsGathered - 1
                else:
                    self.step = Step.GROW
                    self.field.reset()

    def hello(self):
        # bigTextScroll("  Welcome to: THE BAUER   ")
        self.update()

    def bye(self):
        bigTextScroll("  Au revoir!   ")
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
        self.elements = []
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

        self.staging = True
        self.reset()

    def reset(self):
        self.elements = [[-3, 0], [-2, 0], [-3, 1], [-2, 1]]
        self.staging = True
        # self.elements = [[0, 0], [1, 0], [0, 1], [1, 1]]

    # drive onto field
    def stage(self):
        if self.elements[self.iBL][self.iX] <= 0:
            self.moveElements(Orientation.EAST, 1)
        else:
            self.staging = False

    def update(self):
        self.updateOxocard()
        self.updateDifference()
        self.updateGear()
        self.updateDirection()
        self.updateElements()

    def updateOxocard(self):
        self.oxo.update()

    def updateDifference(self):
        self.difference = self.oxo.getDifference(self.orientation, self.oxo.orientation)

    def updateGear(self):
        orientOxo = self.oxo.orientation
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
