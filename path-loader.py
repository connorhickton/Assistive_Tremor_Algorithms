# path-loader.py
# Choose a file from the dataset (right now: only one that's of the "pointing" task, and on the "DESKTOP" deviceType), and you can view a replay of the recorded data.
# Author: Connor Hickton
# 

import pygame
import json
import time

from pygame.locals import *
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from breakpointtests import *


# BREAKVAL is the distance in pixels which quantifies "enough movement" after a direction change,
# according to the paper, "Real Time Break Point Detection Technique (RBPD) in Computer Mouse Trajectory".
# The values for "m" (equal to BREAKVAL in this code) are 2, 3, 4, 7, 10 - with 4 being for "medial levels of tremor"
BREAKVAL = 4


# The closest recorded coordinate that was X seconds ago
TIME_COMPARE_SECONDS = 0.5


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


direction = ""
lastdir = ""


coordList = []
breakpoints = []

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

    # refresh display after each set of targets
    screen.fill("black")
    

    # if task is pointing, draw the targets
    if (data["taskName"] == "Pointing"):
        target_ctr = ((data["trials"][h]["target"]["center"]["X"]), (data["trials"][h]["target"]["center"]["Y"]))
        target_size = (data["trials"][h]["target"]["width"], data["trials"][h]["target"]["height"])

        start = (data["trials"][h]["target"]["start"]["X"], data["trials"][h]["target"]["start"]["Y"])

        # draw starting target in fuchsia
        pygame.draw.circle(screen, "fuchsia", start, target_size[0])

        # draw ending target in orange
        pygame.draw.circle(screen, "orange", target_ctr, target_size[0])

    
    # Secondary game loop. Iterates through mouse events stored in the opened JSON file.
    # TODO: time.sleep() is an improper way to use pygame. Change pygame to use pygame.time.get_ticks(), as per the top stackoverflow comment:
    # https://stackoverflow.com/questions/59888769/pygame-screen-not-updating-after-each-element-is-added
    count = 0
    for j in data['trials'][h]['mouseEvents']:
        
        if (keysAreStrings):
            j = data['trials'][h]['mouseEvents'][str(count)]
        
        #print("this is j: ",j, " and j is type: ", type(j))

        # bad but working way to space out the events to show the proper timing when the data was recorded
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

        count += 1

        pygame.display.update()

pygame.quit()



        
