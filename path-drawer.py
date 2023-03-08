# path-drawer.py
# Draws your mouse movements on the window, and detects "breakpoints" (sudden direction changes) and stoppages.
# Messier program than its sibling path-loader.py. Probably more active development.
# Lots of old scraps of code from moot tests and ideas. 
# Author: Connor Hickton
import pygame
from pygame.locals import *
import json
import time
import math

import numpy as np
import scipy.interpolate
from scipy.interpolate import BSpline, splrep, splev
# import matplotlib.pyplot as plt
from sharedfunctions import *
# from bsplinetest4 import *

# BREAKVAL is the distance in pixels which quantifies "enough movement" after a direction change,
# according to the paper, "Real Time Break Point Detection Technique (RBPD) in Computer Mouse Trajectory".
# The values for "m" (equal to BREAKVAL in this code) are 2, 3, 4, 7, 10 - with 4 being for "medial levels of tremor"
BREAKVAL = getBreakVal()

# The closest recorded coordinate that was X seconds ago
TIME_COMPARE_SECONDS = getTimeCmp()


SCREENWIDTH = 1280
SCREENHEIGHT = 720


output = {
    "taskName": "Drawing",
    "trials": {
        0: {
            "mouseEvents": {

            }
        }
    },
    "screenAvailWidth": SCREENWIDTH,
    "screenAvailHeight": SCREENHEIGHT,
    "startTime": (int)(time.time() * 1000)
    
}

# exports the program's recorded mouse movements to a json file when the program is closed.
def export(output):
    endTimeAdd = {"endTime": (int)(time.time() * 1000)}
    output.update(endTimeAdd)
    with open("test.json", "w") as outfile:
        json.dump(output, outfile)



pygame.init()
info = pygame.display.Info()
screen = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))   # setting to 0,0 will default to the screen's resolution. Windows scaling can make that wonky though.
                                                # add , pygame.NOFRAME after coords for borderless
done = False

clock = pygame.time.Clock()


pygame.display.set_caption('Pygame Mouse Tracking Prototype')


direction = ""
lastdir = ""

coordList = []
breakpoints = []
meanBreakpoints = []

counter = 0

while not done: # main game loop
    
    # clock.tick(FPS)
    screen.fill("black")
    
    for event in pygame.event.get():
        if event.type == QUIT:
            export(output)
            done = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                export(output)
                done = True



    
    coords = pygame.mouse.get_pos()

    # Don't add repeated coordinates
    if len(coordList) == 0 or coordList[0][0] != coords:
        coordList.insert(0, (coords, int(time.time() * 1000)))


    if (len(coordList) > 2):
        for i in range(len(coordList)-1):
            
            #if i < 50:
            pygame.draw.line(screen, "green", coordList[i][0], coordList[i+1][0], 1)
            #else:
                #pygame.draw.line(screen, "blue", coordList[i][0], coordList[i+1][0], 1)

    
    lastdir = direction

    oldElement = getOldElement(coordList, TIME_COMPARE_SECONDS)

    direction = getDirection(coordList[0][0], oldElement)

    # breakpoint1 code
    
    if (breakpoint1(direction, lastdir, coordList[0][0], oldElement, BREAKVAL)):
        # print("BREAKPOINT DETECTED!!!")
        breakpoints.insert(0, coords)

        # mean filtering
        if(len(breakpoints) > 1):
            bx = int((breakpoints[0][0] + breakpoints[1][0])/2)
            by = int((breakpoints[0][1] + breakpoints[1][1])/2)
            
            meanBreakpoints.insert(0, (bx, by))
    
    """

    # breakpoint2 code
    checkBreakpoint = breakpoint2(coordList, BREAKVAL, TIME_COMPARE_SECONDS)
    if (checkBreakpoint is not False):
        # pinpoint accurate, but places the point in the past. Not acceptable
        # breakpoints.insert(0, checkBreakpoint)

        # Real-time, but slight delay in point location
        breakpoints.insert(0, coords)
              
        # mean filtering
        if(len(breakpoints) > 1):
            bx = int((breakpoints[0][0] + breakpoints[1][0])/2)
            by = int((breakpoints[0][1] + breakpoints[1][1])/2)
            
            meanBreakpoints.insert(0, (bx, by))
    """  

    
    if (len(breakpoints) > 2):
        for i in range(len(breakpoints)):
            pygame.draw.circle(screen, "red", breakpoints[i], 3, 2)

    
    if (len(meanBreakpoints) > 2):
        for i in range(len(meanBreakpoints)):
            pygame.draw.circle(screen, "purple", meanBreakpoints[i], 5, 2)

    

    mouseAction = "mousemove"

    if (counter == 0):
        mouseAction = "mouseenter"
    
    addCoord = {
        counter: {
            "e": mouseAction,
            "t": (int)(time.time() * 1000),
            "p": {
                "X": coords[0],
                "Y": coords[1]
            }
        }
        
    }
    """
    # second attempt at b splines
    # it kinda works!!!
    if (event.type == pygame.MOUSEBUTTONUP or len(breakpoints) > 3):
        ctr = np.array(breakpoints)

        x = ctr[:,0]
        y = ctr[:,1]

        l=len(x)
        t=np.linspace(0,1,l-2,endpoint=True)
        t=np.append([0,0,0],t)
        t=np.append(t,[1,1,1])

        tck=[t,[x,y],3]
        u3=np.linspace(0,1,(max(l*2,70)),endpoint=True)
        out = scipy.interpolate.splev(u3,tck)

        #print(" HERE HERE: ", out[0][0])

        for i in range(len(out[0]) - 1):
            pygame.draw.line(screen, "yellow", (out[0][i],out[1][i]), (out[0][i+1],out[1][i+1]),  1)
    """

    # second attempt at b splines
    # it kinda works!!!
    if (event.type == pygame.MOUSEBUTTONUP or len(meanBreakpoints) > 3):
        ctr = np.array(meanBreakpoints)

        x = ctr[:,0] # get all values from column 0 (the x values)
        y = ctr[:,1] # get all values from column 1 (the y values)


        #x = x[::-1]
        #y = y[::-1]

        l=len(x)
        # print(l)
   
        
        t=np.linspace(0,1,l-2,endpoint=True)
        t=np.append([0,0,0],t)
        t=np.append(t,[1,1,1])

        tck=[t,[x,y],3]
        u3=np.linspace(0,1,(max(l*2,70)),endpoint=True)
        out = scipy.interpolate.splev(u3,tck)
        
        for i in range(len(out[0]) - 1):
            pygame.draw.line(screen, "white", (out[0][i],out[1][i]), (out[0][i+1],out[1][i+1]),  3)
        
        """
        #print(" HERE HERE: ", out[0][0])

        print(np.array([x,y]), "\nIs of type: ", type(np.array([x,y])))

        newOut = bspline(np.array([x,y]), max(l*2,70), periodic=False)
        print(newOut)

        for i in range(len(newOut[0]) - 1):
            pygame.draw.line(screen, "white", (newOut[0][i],newOut[1][i]), (newOut[0][i+1],newOut[1][i+1]),  3)
        """


    output["trials"][0]["mouseEvents"].update(addCoord)

    # print("\n")

    counter += 1

    pygame.display.update()

pygame.quit()
    

    

