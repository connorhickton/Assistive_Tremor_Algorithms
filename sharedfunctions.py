import math
import numpy as np


TIME_COMPARE_SECONDS = 0.2

BREAKVAL = 3

MAX_ANGLE = 90.0


# Filter Types:
# 0 means no filter
# 1 means B-spline and breakpoint filtering, a la Banihashem et al
# 2 means mean filtering/moving average
# 3 means Double Exponential Smoothing filter
FILTER_TYPE = 3

# If FILTER_TYPE is 1 (B-spline and breakpoint), then you can choose between two breakpoint algorithms
# 1 means Banihashem's breakpoint algorithm
# 2 means Connor's (my own)

BREAKPOINT_TYPE = 1





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

        if (type(path[i][0]) is tuple):
            #print("tuple")
            x3, y3 = path[i][0]
        else:
            #print("no tuple")
            x3, y3 = path[i]
        
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
"""
import math
tstPath = [[[1,10],100],[[3,8],102], [[6,6],104], [[8,2],106]]
print(eval1([0,10], [10,0], 5, tstPath))
"""


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
    
# returns the next coordinate for a mean filter (moving average) of the mouse path, over a specified time window timeCmp
def meanFilter(coordList, timeCmp):

    lastElement = getOldElement(coordList, timeCmp)

    if ((lastElement)) is not None:
        lastIndex = coordList.index(lastElement)
    
    else:
        return False

    window = coordList[:lastIndex]

    sumX = 0
    sumY = 0
    count = 0
    for i in window:
        #print(i)
        sumX += i[0][0]
        sumY += i[0][1]
        count += 1

    meanX = sumX / count
    meanY = sumY / count

    return (meanX, meanY)

# ("Efficient jitter compensation using double exponential smoothing", Chung and Kim (2012))
def alphaFunc(uk):

    min = 1
    max = 100

    if (uk < min):
        return 0
    elif (uk > max):
        return 1
    elif (uk <= max and uk >= min):
        return float(uk / max)

# alphaFunc and gammaFunc ended up being the same in the paper
def gammaFunc(uk):

    return alphaFunc(uk)
    
def vectorize(coords, lastCoords):

    vx = coords[0] - lastCoords[0]
    vy = coords[1] - lastCoords[1]

    return (vx, vy)


# returns the next coordinate for a Double Exponential Smoothing filter 
# ("Efficient jitter compensation using double exponential smoothing", Chung and Kim (2012))

def desFilter(coordList, desCoords, bTrend):

        #aFunc = 0
        #gFunc = 0
        #uk = 0

        # step 1: initialize s1 = z1 and b1 = z1 - z0. Then, iterate.
        if (len(desCoords) == 0 and len(coordList) > 2):
            desCoords.insert(0, vectorize(coordList[0][0], coordList[1][0]))
            #print(coordList[0][0])
            
            bTrend.insert(0, tuple(np.subtract(vectorize(coordList[0][0], coordList[1][0]), vectorize(coordList[1][0], coordList[2][0]))))
            print("this should be run exactly once")
            #print(bFunc)


        elif (len(desCoords) > 0):

            # step 2: obtain the new coord zk
            coord = vectorize(coordList[0][0], coordList[1][0])

            # determine the value uk = ||zk - s(k-1)||
            uk = math.hypot(coord[0] - desCoords[0][0], coord[1] - desCoords[0][1])

            #print("UK is ", uk)

            # Compute both alpha and gamma
            # the DES paper found that both should be linearly increasing functions
            aFunc = alphaFunc(uk)
            gFunc = gammaFunc(uk)

            #print(aFunc[0])
            #print("afunc is ", aFunc)
            #print(type(aFunc))

            #print(type(desCoords[0][0]))
            #print(bTrend)

            # Step 3: Compute Sk using alpha. The resulting vector denotes the smoothed value
            sCoordX = (aFunc * coord[0]) + ((1 - aFunc) * (desCoords[0][0] + bTrend[0][0]))
            sCoordY = (aFunc * coord[1]) + ((1 - aFunc) * (desCoords[0][1] + bTrend[0][1]))

            # print("sCoords: ", (sCoordX, sCoordY))

            desCoords.insert(0, (sCoordX, sCoordY))

            bTrendX = gFunc * (desCoords[0][0] - desCoords[1][0]) + (1 - gFunc)* bTrend[0][0]
            bTrendY = gFunc * (desCoords[0][1] - desCoords[1][1]) + (1 - gFunc)* bTrend[0][1]

            bTrend.insert(0, (bTrendX, bTrendY))
            # print("btrend: ", (bTrendX, bTrendY))

        return desCoords, bTrend




        #smooth = coord + desCoords[1]






