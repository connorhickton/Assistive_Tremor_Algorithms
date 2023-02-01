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


# BREAKVAL is the distance in pixels which quantifies "enough movement" after a direction change,
# according to the paper, "Real Time Break Point Detection Technique (RBPD) in Computer Mouse Trajectory".
# The values for "m" (equal to BREAKVAL in this code) are 2, 3, 4, 7, 10 - with 4 being for "medial levels of tremor"
BREAKVAL = 4        

# LISTLEN is how many coordinates are stored, in order to calculate breakpoints.
# Correlates with time, but I don't know the exact translation at the moment. According to the paper, this should be half a second's worth of coordinates.
# The datasets being loaded do not have a consistent framerate. It's likely the recorded data is event-based. This messes with the data and breakpoint algorithm. 
# My base assumption is that most people's screens are 60fps. So 30 would be half a second's worth.
LISTLEN = 30


# load json file
# User 258 is identified in the data as able-bodied and skilled enough with a mouse. Good subject to use to sanity-check that targets are appearing in the right place
# New: tkinter opens a file explorer box, and you can choose which file to open.
Tk().withdraw()
filename = askopenfilename(initialdir='mouseandtouchinput-master/alldata')
f = open(filename)
data = json.load(f)


# Open a window that's the same size as the working area of the participant's window.
# My monitors are very high-res, so the boxes have always been small enough to see the entirety of.
# Needs the JSON file to find out what the user's window's width/height were.
screenAvailWidth = data["screenAvailWidth"]
screenAvailHeight = data["screenAvailHeight"]


""" # this is supposed to be "commented out" - remove if it causes any issues at all. Not used.
# turns a centerpoint and width/height measurements of a square or rectangle, into a Rect with the given dimensions.
# Not actually useful, since the targets are circles...
def rectify(center_x, center_y, width, height):
    half_width = width / 2
    half_height = height / 2
    left = center_x - half_width
    top = center_y - half_height

    return Rect(left, top, width, height)
"""

pygame.init()
screen = pygame.display.set_mode((screenAvailWidth, screenAvailHeight))   # setting to 0,0 will default to the screen's resolution
                                                # add , pygame.NOFRAME after coords for borderless



pygame.display.set_caption('Pygame Mouse Replaying Prototype')

# Create layered window
# hwnd = pygame.display.get_wm_info()["window"]
# win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
#                        win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)

# https://pythonprogramming.altervista.org/how-to-make-a-fully-transparent-window-with-pygame/?doing_wp_cron=1674556950.6755940914154052734375




direction = ""
lastdir = ""
# "prev" is a linked list of the last LISTLEN + 1 coordinates that the mouse has been at.
prev = [None] * (LISTLEN + 1)

# tracks the time that the previous mouse event happened at (in ms). Starts at the time the trial began, in ms since epoch
last = data['startTime']

# Main game loop. Iterates through each of the "trials" stored in the JSON files.
for h in range(len(data["trials"])):

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
    for j in data['trials'][h]['mouseEvents']:
        
        # bad but working way to space out the events to show the proper timing when the data was recorded
        time.sleep((j["t"] - last)/1000)
        last = j["t"]

        # press ESC to exit the window at any time
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
        
        # pop the last element of the linked list. Used for direction/breakpoint detection, and to draw over the line with a different colour.
        popped = prev.pop()
        #print(popped)
        

        # This whole "redrawing over the line after a certain amount of updates" isn't important and will be removed eventually.
        # The linked list it relies on is definitely important for later, though! That'll store the coordinates that filtering
        # will be based on.
        if (popped is not None):
            #prev.remove(popped)
            #screen.set_at(popped, "black")  #"black" is just because it's the background colour. Ideally, change this to transparency
            pygame.draw.line(screen, "blue", prev[-2], popped, 3)
            
            
        # get next set of mouse coords from JSON
        coords = (j["p"]["X"], j["p"]["Y"])
        
        # insert the new coords at the front of the linked list
        prev.insert(0, coords)

        #draw a line from the last coord to the current one
        if (prev[1] is not None):
            pygame.draw.line(screen, "green", prev[1], prev[0], 1)


        # When comparing x,y coordinates, [0] is the X value and [1] is the Y value.
        # From the breakpoint paper - b is the current coordinate, a is the one from the past.
        # So coords is b, and popped is a.
        
        lastdir = direction

        # this next if statement is a verbatim port of the direction algorithm described in the paper mentioned earlier (Banihashem et al, 2013)
        if (coords is not None and popped is not None):
            
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


        # print(direction)

        # Breakpoint Detection
        # Jan 27 2023: You were having issues knowing what timeframes you were supposed to compare. Are you comparing to last frame,
        # or a half-second ago? (also you wouldn't be measuring by seconds, but frames instead. Nothing time-related programmed yet)
        #
        # Breakpoints aren't quite appearing where you want them to. Probably a math bug, at least as my guess.
        # Final update - if you try to make wave-like movements but slowly, the breakpoints appear right where you'd expect them!
        # Might be a matter of tweaking, rather than debugging
        #
        # Idea: To fix the "resonant frequency" problem (breakpoints detected best only with certain "frequencies" of tremor),
        # maybe if there was a breakpoint less than the half second ago, check against the last breakpoint rather than the 0.5 second coord?

        if (direction != lastdir and (abs(coords[0] - popped[0])> BREAKVAL or abs(coords[1] - popped[1]) > BREAKVAL)):
            # print("BREAKPOINT DETECTED!!!")
            #                                   v - I already tried changing this to popped instead of coords, but neither put the breakpoints right where I expect them.
            pygame.draw.circle(screen, "red", coords, 5, 2) # It might be good enough, really - I'll evaluate other methods and tweaks shortly

        # draw a white circle if the mouse is clicked
        elif (j["e"] == "mouseclick"):
            pygame.draw.circle(screen, "white", coords, 8, 4)
        
        # print("\n")

        pygame.display.update()

pygame.quit()


