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


SCREENWIDTH = 1600
SCREENHEIGHT = 900


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


# create a sine wave
# https://www.mkdynamics.net/current_projects/sine_wv_50Hz.html
sRate = 60
sFreq = 6
sAmp = 50
numPeriods = 5
numSamples = sRate * numPeriods

sin = np.linspace (0, numPeriods, numSamples) + np.random.normal(size=300, scale=0.005)

f1 = lambda x: sAmp*np.sin(sFreq*2*np.pi*x)

sampled_f1 = [f1(i) for i in sin]
#print(sampled_f1)

sinList = [[sin[i], sampled_f1[i]] for i in range(0, len(sin))]

for i in sinList:

    # move the X coordinate 100 pixels right, and spread the points apart by 500x
    i[0] = (i[0]*500) + 100

    # add 500 to each Y so that the sine wave is closer to the middle of the screen
    i[1] = i[1] + 500

#print(sinList)

sinLineStart = (100, 500)
sinLineEnd = (10000, 500)

coordList = []

if (FILTER_TYPE == 1):
    direction = ""
    lastdir = ""
    breakpoints = []
    meanBreakpoints = []

if (FILTER_TYPE == 2):
    meanCoords = []

if (FILTER_TYPE == 3):
    desVels = []
    desCoords = []
    bTrend = []
    beginningPos = (None, None)

counter = 0

for g in sinList: # main game loop
    
    # clock.tick(FPS)
    screen.fill("black")

    pygame.draw.line(screen, "gray", sinLineStart, sinLineEnd, 1)
    
    for event in pygame.event.get():
        if event.type == QUIT:
            export(output)
            done = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                export(output)
                done = True


    # don't just spew out the plot all at once, especially since some of the functions rely on time
    time.sleep(0.01)
    coords = g
    skipped = False

    # Don't add repeated coordinates
    if len(coordList) == 0 or coordList[0][0] != coords:
        coordList.insert(0, (coords, int(time.time() * 1000)))
    else:
        skipped = True


    if (len(coordList) > 2):
        for i in range(len(coordList)-1):
            
            #if i < 50:
            pygame.draw.line(screen, "green", coordList[i][0], coordList[i+1][0], 1)
            #else:
                #pygame.draw.line(screen, "blue", coordList[i][0], coordList[i+1][0], 1)

    
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

    output["trials"][0]["mouseEvents"].update(addCoord)


    if(FILTER_TYPE == 1):
        lastdir = direction
        oldElement = getOldElement(coordList, TIME_COMPARE_SECONDS)
        direction = getDirection(coordList[0][0], oldElement)
        if(len(meanBreakpoints) == 0):
            meanBreakpoints.insert(0, coords)
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


        # second attempt at b splines
        # it kinda works!!!
        if (event.type == pygame.MOUSEBUTTONUP or len(meanBreakpoints) > 3):
            ctr = np.array(meanBreakpoints)

            x = ctr[:,0] # get all values from column 0 (the x values)
            y = ctr[:,1] # get all values from column 1 (the y values)

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
    

    # Mean Filter Code
    elif(FILTER_TYPE == 2):

        if (len(coordList) > 2):
            mean = meanFilter(coordList, TIME_COMPARE_SECONDS)
            if (mean is not False):
                meanCoords.insert(0, mean)
            else:
                meanCoords.insert(0, coordList[-1][0])

        if (len (meanCoords) > 2):
            for i in range(len(meanCoords) - 1):
                pygame.draw.line(screen, "cyan", meanCoords[i], meanCoords[i+1], 1)


    elif (FILTER_TYPE == 3 ):
        
        if (beginningPos == (None, None)):
            beginningPos = coords

        if (skipped == False):
            desVels, bTrend = desFilter(coordList, desVels, bTrend)


            if (len(desVels) > 0):
                #print(desVels[0])

                if (len(desCoords) > 0 ):
                    desX = desVels[0][0] + desCoords[0][0]
                    desY = desVels[0][1] + desCoords[0][1]
                else:
                    desX = desVels[0][0] + beginningPos[0]
                    desY = desVels[0][1] + beginningPos[1]

                desCoords.insert(0, (desX, desY))

                #print("descoords: ", desCoords[0])
                #print("desvels: ", desVels[0])
                #print("btrend: ", bTrend[0])


        #realLocY = sum(list(zip(*desCoords[1]))) + beginningPos[1]
        #print(realLocX, realLocY)

        if (len(desCoords)> 2):
            for i in range(len(desCoords) - 1):
                pygame.draw.line(screen, "cyan", desCoords[i], desCoords[i+1], 1)
                

        



    

    # print("\n")

    counter += 1

    pygame.display.update()

pygame.quit()
    

    

