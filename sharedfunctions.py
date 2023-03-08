import math


TIME_COMPARE_SECONDS = 0.5

BREAKVAL = 4

MAX_ANGLE = 90.0



def getTimeCmp():
    return TIME_COMPARE_SECONDS

def getBreakVal():
    return BREAKVAL

def getMaxAngle():
    return MAX_ANGLE


def getOldElement(coordList, timeCmp):
    nowTime = coordList[0][1]
    maxTime = int(nowTime - (timeCmp * 1000))

    popped = None
    for i in range(len(coordList)):
        if (coordList[i][1] <= maxTime):
            popped = coordList[i]
            break
    
    return popped




# Part of Banihashem et al's breakpoint detection - this gets the direction the mouse is moving, between now and X seconds ago.
# X is defined by TIME_COMPARE_SECONDS in the other program.
def getDirection(coords, oldElement):

    
    # When comparing x,y coordinates, [0] is the X value and [1] is the Y value.
    # From the breakpoint paper - b is the current coordinate, a is the one from the past.
    # So coords is b, and popped is a.

    direction = ""

    if oldElement is not None:
        popped = oldElement[0]
        if (coords[0] > popped[0]):
            if (coords[1] == popped[1]):
                direction = "right"
            elif (coords[1] < popped[1]):
                    direction = "up right"
            else:
                direction = "down right"
            
        if (coords[0] == popped[0]):
            if (coords[1] < popped[1]):
                direction = "up"
            elif (coords[1] > popped[1]):
                direction = "down"
            else:
                direction = "stop"

        if (coords[0] < popped[0]):
            if (coords[1] < popped[1]):
                direction = "up left"
            elif (coords[1] == popped[1]):
                direction = "left"
            else:
                direction = "down left"

    return direction

# Movement Variability evaluation.
# Takes the start and end target (1 and 2 respectively), the size of the targets (always the same), 
# and the mouse's path between them (list of tuples, first element containing coords in another tuple, second element containing time).
# From MacKenzie et al, "Accuracy Measures for Evaluating Computer Pointing Devices" (2001)
def eval1(tgt1, tgt2, radius, path):
    
    
    x1, y1 = tgt1
    x2, y2 = tgt2
    dx, dy = x2-x1, y2-y1

    yDistFromAxis = []

    for i in range(len(path)):
        
        # get closest distance from task axis
        # https://stackoverflow.com/questions/47177493/python-point-on-a-line-closest-to-third-point

        x3, y3 = path[i][0]
        
        det = dx * dx + dy * dy
        a = (dy*(y3-y1)+dx*(x3-x1))/det
        nearestOnLine = x1+a*dx, y1+a*dy

        yDistFromAxis.insert(0,math.hypot(nearestOnLine[0]-x3, nearestOnLine[1]-y3))

    meanDist = (sum(yDistFromAxis) / len(yDistFromAxis))

    summation = 0
    for j in range(len(yDistFromAxis)):
        summation += ((yDistFromAxis[j]-meanDist) ** 2)
    
    if (len(yDistFromAxis) - 1) == 0:
        return None
    
    equation = summation / (len(yDistFromAxis) - 1)

    equation = math.sqrt(equation)

    return equation

# Test of eval1
import math
tstPath = [[[1,10],100],[[3,8],102], [[6,6],104], [[8,2],106]]
print(eval1([0,10], [10,0], 5, tstPath))



# Banihashem et al's specific breakpoint logic.
# If the direction has changed from X seconds ago (X = 0.5 in the paper) and the mouse has moved more than BREAKVAL pixels, a breakpoint is registered.
def breakpoint1(direction, lastdir, coords, oldElement, BREAKVAL):

    popped = None

    if oldElement is not None:
        popped = oldElement[0]
    else:
        return False


    if (direction != lastdir and (abs(coords[0] - popped[0])> BREAKVAL or abs(coords[1] - popped[1]) > BREAKVAL)):
        return True
    else:
        return False




def getAngle(a, b, c):
    ang = math.degrees(math.atan2(c[1]-b[1], c[0]-b[0]) - math.atan2(a[1]-b[1], a[0]-b[0]))
    return ang + 360 if ang < 0 else ang
 
# print(getAngle((98, 50), (81, 66), (112, 71)))




# my own breakpoint algorithm. Looks at three coordinates: The current mouse position, the coordinates X seconds ago, and the coordinates X seconds again before that.
# It looks at the combined angle between these three points. If the angle is greater than 90 degrees, a breakpoint is registered.
def breakpoint2(coordList, BREAKVAL, timeCmp):
    coord1 = coordList[0][0]
    coord2 = getOldElement(coordList, timeCmp)
    
    
    if coord2 is None:
        return False
    
    index = coordList.index(coord2)

    
    if len(coordList) <= index * 2:
        return False
    
    
    
    coord3 = coordList[index * 2][0]

    coord2 = coord2[0]

    # print (coord3, " : ", type(coord3))

    # math.hypot gets the distance between two coords.
    # If the movement is less than BREAKVAL, the breakpoint doesn't count.
    if (math.hypot(coord2[0] - coord1[0], coord2[1] - coord1[1]) < BREAKVAL) or (math.hypot(coord3[0] - coord2[0], coord3[1] - coord2[1]) < BREAKVAL):
        return False

    angle = getAngle(coord1, coord2, coord3)
    
    if angle < MAX_ANGLE or angle > (360 - MAX_ANGLE):
        print("index: ", index)
        print(getAngle(coord1, coord2, coord3))
        return coord2
    else:
        return False