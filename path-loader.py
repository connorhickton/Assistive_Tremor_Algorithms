# path-loader.py
# Choose a file from the dataset (right now: only one that's of the "pointing" task, and on the "DESKTOP" deviceType), and you can view a replay of the recorded data.
# Author: Connor Hickton
# 

import pygame
import json
import time
import math

from pygame.locals import *
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import numpy as np
import scipy.interpolate
from scipy.interpolate import BSpline, splrep, splev
# import matplotlib.pyplot as plt
from sharedfunctions import *


# BREAKVAL is the distance in pixels which quantifies "enough movement" after a direction change,
# according to the paper, "Real Time Break Point Detection Technique (RBPD) in Computer Mouse Trajectory".
# The values for "m" (equal to BREAKVAL in this code) are 2, 3, 4, 7, 10 - with 4 being for "medial levels of tremor"
BREAKVAL = getBreakVal()


# The closest recorded coordinate that was X seconds ago
TIME_COMPARE_SECONDS = getTimeCmp()


# load json file
# User 258 is identified in the data as able-bodied and skilled enough with a mouse. Good subject to use to sanity-check that targets are appearing in the right place
# New: tkinter opens a file explorer box, and you can choose which file to open.
Tk().withdraw()
filename = askopenfilename() #initialdir='mouseandtouchinput-master/alldata')
f = open(filename)
data = json.load(f)


# Open a window that's the same size as the working area of the participant's window.
# My monitors are very high-res, so the boxes have always been small enough to see the entirety of.
# Needs the JSON file to find out what the user's window's width/height were.
screenAvailWidth = data["screenAvailWidth"]
screenAvailHeight = data["screenAvailHeight"]


pygame.init()
screen = pygame.display.set_mode((screenAvailWidth, screenAvailHeight))   # setting to 0,0 will default to the screen's resolution
                                                # add , pygame.NOFRAME after coords for borderless


pygame.display.set_caption('Pygame Mouse Replaying Prototype')





coordList = []
currentTrialList = []

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
#sumOfVariability = 0

# tracks the time that the previous mouse event happened at (in ms). Starts at the time the trial began, in ms since epoch
last = data['startTime']
#print(last)

# AWFUL code that lets me put off understanding the awful mix of list/dicts/json that the original dataset is made of. So this program can just read both...
keysAreStrings = False
try:
    keys = list(data["trials"].keys())
    #print(keys)
    if (type(keys[0]) == str):
        keysAreStrings = True
        #print("KEY IS STRING")
except:
    pass



# Main game loop. Iterates through each of the "trials" stored in the JSON files.
for h in range(len(data["trials"])):

    if (keysAreStrings):
        h = str(h)

    # if task is pointing, get target details
    if (data["taskName"] == "Pointing"):
        target_ctr = ((data["trials"][h]["target"]["center"]["X"]), (data["trials"][h]["target"]["center"]["Y"]))
        target_size = (data["trials"][h]["target"]["width"], data["trials"][h]["target"]["height"])

        start = (data["trials"][h]["target"]["start"]["X"], data["trials"][h]["target"]["start"]["Y"])


    
        if(len(currentTrialList) > 1 and h > 0):

            last_target_ctr = ((data["trials"][h-1]["target"]["center"]["X"]), (data["trials"][h-1]["target"]["center"]["Y"]))
            last_target_size = (data["trials"][h-1]["target"]["width"], data["trials"][h-1]["target"]["height"])

            last_start = (data["trials"][h-1]["target"]["start"]["X"], data["trials"][h-1]["target"]["start"]["Y"])

            variability = eval1(last_start, last_target_ctr, last_target_size[0], currentTrialList)
            print("RUN #", h)
            print ("Movement Variability Evaluation: ", variability)
            print("First Target coord vs first element added to currentTrialList: ", last_start, " | ", currentTrialList[-1])
            print("Last Target coord vs last element added to currentTrialList: ", last_target_ctr, " | ", currentTrialList[0])
            currentTrialList = []


    
    # Secondary game loop. Iterates through mouse events stored in the opened JSON file.
    # Note: time.sleep() is an improper way to use pygame. Change pygame to use pygame.time.get_ticks(), as per the top stackoverflow comment:
    # https://stackoverflow.com/questions/59888769/pygame-screen-not-updating-after-each-element-is-added
    # However, for this part of the project, being truly real-time may not be an issue.
    count = 0
    for j in data['trials'][h]['mouseEvents']:
        
        
        # refresh display after each set of targets
        screen.fill("black")
        # if task is pointing, draw the targets
        if (data["taskName"] == "Pointing"):
            # draw starting target in fuchsia
            pygame.draw.circle(screen, "fuchsia", start, target_size[0])

            # draw ending target in orange
            pygame.draw.circle(screen, "orange", target_ctr, target_size[0])










        if (keysAreStrings):
            j = data['trials'][h]['mouseEvents'][str(count)]
        
        # else:
            #print("this is j: ",j, " and j is type: ", type(j))

        # bad but working way to space out the events to show the proper timing when the data was recorded   
        # If replaying data from path-drawer.py, then it appears slow. 
        # However, it should be accurate in terms of time-based data, as if it were full speed.
        time.sleep((j["t"] - last)/1000)
        last = j["t"]
        #print (j["t"], "     ", (j["t"] - last))



        # press ESC to exit the window at any time
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
        
        # get next set of mouse coords from JSON
        coords = (j["p"]["X"], j["p"]["Y"])
        coordTime = (j["t"])
        
        # Oops, I should be getting the time from the JSON for breakpoint detection! Or else a computer slowdown will affect results
        # coordList.insert(0, (coords, int(time.time() * 1000)))
        coordList.insert(0, (coords, coordTime))

        # if the task is "pointing" and the target has been activated:
        if data["taskName"] == "Pointing" and data['trials'][h]['taskEvents'][0]['t'] < coordTime:
            currentTrialList.insert(0, coordList[0])

        
        # if currentTrialList is used, only the current trial's raw mouse data will be shown in green.
        # if it's coordList, then the entire path will be shown for all trials.
        if (len(currentTrialList) > 2):
            for i in range(len(currentTrialList)-1):
                pygame.draw.line(screen, "green", currentTrialList[i][0], currentTrialList[i+1][0], 1)


        if (FILTER_TYPE == 1):
            lastdir = direction
            oldElement = getOldElement(coordList, TIME_COMPARE_SECONDS)
            direction = getDirection(coordList[0][0], oldElement)


            # breakpoint 1 code
            
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
                breakpoints.insert(0, checkBreakpoint)
            """
            # """"
            
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

                x = ctr[:,0]
                y = ctr[:,1]

                l=len(x)
                t=np.linspace(0,1,l-2,endpoint=True)
                t=np.append([0,0,0],t)
                t=np.append(t,[1,1,1])

                tck=[t,[x,y],3]
                u3=np.linspace(0,1,(max(l*2,70)),endpoint=True)
                out = scipy.interpolate.splev(u3,tck)


                for i in range(len(out[0]) - 1):
                    pygame.draw.line(screen, "white", (out[0][i],out[1][i]), (out[0][i+1],out[1][i+1]),  3)

        elif(FILTER_TYPE == 2):
            
            if (len(coordList) > 2):
                mean = meanFilter(coordList, TIME_COMPARE_SECONDS)
                if (mean is not False):
                    meanCoords.insert(0, mean)

            if (len (meanCoords) > 2):
                for i in range(len(meanCoords) - 1):
                    pygame.draw.line(screen, "orange", meanCoords[i], meanCoords[i+1], 1)

        elif (FILTER_TYPE == 3):
        
            if (beginningPos == (None, None) and len(currentTrialList) > 0):
                beginningPos = coords

            # coordList has another dimension, so to plug this into desFilter I need to add that dimension, or else I have to rewrite the whole thing
            currentTrialPad = [currentTrialList]

            desVels, bTrend = desFilter(currentTrialList, desVels, bTrend)

            if (len(desVels) > 0):
                #print(desVels[0])

                if (len(desCoords) > 0 ):
                    desX = desVels[0][0] + desCoords[0][0]
                    desY = desVels[0][1] + desCoords[0][1]
                else:
                    desX = desVels[0][0] + beginningPos[0]
                    desY = desVels[0][1] + beginningPos[1]

                desCoords.insert(0, (desX, desY))

                print("desCoords: ", desCoords[0])
                print("desVels:   ", desVels[0])


            #realLocY = sum(list(zip(*desCoords[1]))) + beginningPos[1]
            #print(realLocX, realLocY)

            if (len(desCoords)> 2):
                for i in range(len(desCoords) - 1):
                    pygame.draw.line(screen, "cyan", desCoords[i], desCoords[i+1], 1)


        count += 1

        pygame.display.update()

    # reset filters when trial is over, since trials shouldn't carry over through multiple
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
    


pygame.quit()



        
