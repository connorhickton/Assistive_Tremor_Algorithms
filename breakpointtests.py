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
