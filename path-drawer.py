# path-drawer.py
# Draws your mouse movements on the window, and detects "breakpoints" (sudden direction changes) and stoppages.
# Messier program than its sibling path-loader.py. Probably more active development.
# Lots of old scraps of code from moot tests and ideas. 
# Author: Connor Hickton
import pygame
from pygame.locals import *
import json
import time
import numpy as np
from scipy.interpolate import BSpline, splrep, splev
import matplotlib.pyplot as plt
from breakpointtests import *

# BREAKVAL is the distance in pixels which quantifies "enough movement" after a direction change,
# according to the paper, "Real Time Break Point Detection Technique (RBPD) in Computer Mouse Trajectory".
# The values for "m" (equal to BREAKVAL in this code) are 2, 3, 4, 7, 10 - with 4 being for "medial levels of tremor"
BREAKVAL = 4        

# The closest recorded coordinate that was X seconds ago
TIME_COMPARE_SECONDS = 0.1


SCREENWIDTH = 1920
SCREENHEIGHT = 1080


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
    
    coordList.insert(0, (coords, int(time.time() * 1000)))

    if (len(coordList) > 2):
        for i in range(len(coordList)-1):
            pygame.draw.line(screen, "green", coordList[i][0], coordList[i+1][0], 1)

    
    lastdir = direction

    oldElement = getOldElement(coordList, TIME_COMPARE_SECONDS)

    direction = getDirection(coordList[0][0], oldElement)

    if (breakpoint1(direction, lastdir, coordList[0][0], oldElement, BREAKVAL)):
        # print("BREAKPOINT DETECTED!!!")
        breakpoints.insert(0, coords)
        
        
    
    if (len(breakpoints) > 2):
        for i in range(len(breakpoints)):
            pygame.draw.circle(screen, "red", breakpoints[i], 5, 2)
        

    

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

    # first, very naive attempt at making splines. Didn't work (yet?)
    """
    if (event.type == pygame.MOUSEBUTTONUP):
        # print("Click!")
        print(breakpoints)
        bpx = (list(zip(*breakpoints))[0])
        bpy = (list(zip(*breakpoints))[1])

        tck = splrep(bpx, bpy, t=bpx[2:-2], k=3)
        ys_interp = splev(bpx, tck)

        plt.figure(figsize=(12, 6))
        plt.plot(bpx, bpy, '.c')
        plt.plot(bpx, ys_interp, '-m')
        plt.show()
    """

    output["trials"][0]["mouseEvents"].update(addCoord)

    # print("\n")

    counter += 1

    pygame.display.update()

pygame.quit()
    

    

