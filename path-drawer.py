# path-drawer.py
# Draws your mouse movements on the window, and detects "breakpoints" (sudden direction changes) and stoppages.
# Messier program than its sibling path-loader.py. Probably more active development.
# Lots of old scraps of code from moot tests and ideas. 
# Author: Connor Hickton
import pygame
from pygame.locals import *
import json
import time

# BREAKVAL is the distance in pixels which quantifies "enough movement" after a direction change,
# according to the paper, "Real Time Break Point Detection Technique (RBPD) in Computer Mouse Trajectory".
# The values for "m" (equal to BREAKVAL in this code) are 2, 3, 4, 7, 10 - with 4 being for "medial levels of tremor"
BREAKVAL = 4        
# LISTLEN is how many coordinates are stored, in order to calculate breakpoints, mean filters, etc.
# Correlates with time, but I don't know the exact translation at the moment. According to the paper, this should be half a second's worth of coordinates.
# My main monitor is 144 hz (and so hopefully 144 fps), so this might be set to 72? or 30 for my side monitor?
LISTLEN = 20

# https://stackoverflow.com/questions/67963353/how-to-set-framerate-in-pygame
FPS = 60

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
    with open("Assistive_Tremor_Algorithms/test.json", "w") as outfile:
        json.dump(output, outfile)



pygame.init()
info = pygame.display.Info()
screen = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))   # setting to 0,0 will default to the screen's resolution. Windows scaling can make that wonky though.
                                                # add , pygame.NOFRAME after coords for borderless
done = False

clock = pygame.time.Clock()


pygame.display.set_caption('Pygame Mouse Tracking Prototype')

# Create layered window
# hwnd = pygame.display.get_wm_info()["window"]
# win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
#                        win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)


# https://pythonprogramming.altervista.org/how-to-make-a-fully-transparent-window-with-pygame/?doing_wp_cron=1674556950.6755940914154052734375

direction = ""
lastdir = ""
prev = [None] * (LISTLEN + 1)
# i = 0
counter = 0

while not done: # main game loop
    
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == QUIT:
            export(output)
            done = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                export(output)
                done = True
    
    # print("Coord to Remove: ", prev[LISTLEN])
    
    # print("LastElementTest: ", prev[-1])

    popped = prev.pop()
    #print(popped)
    

    # This whole "redrawing over the line after a certain amount of updates" isn't important and will be removed eventually.
    # The linked list it relies on is definitely important for later, though! That'll store the coordinates that filtering
    # will be based on.
    if (popped is not None):
        #prev.remove(popped)
        #screen.set_at(popped, "black")  #"black" is just because it's the background colour. Ideally, change this to transparency
        pygame.draw.line(screen, "blue", prev[-2], popped, 3)
        
        
    
    coords = pygame.mouse.get_pos()
    
    prev.insert(0, coords)
    # print("Inserted coords: ", prev[0])
    
    #print("All coords: ", prev)

    #screen.set_at(coords, "green") # - replaced with the line draw, it's just better
    
    if (prev[1] is not None):
        pygame.draw.line(screen, "green", prev[1], prev[0], 1)
    # print(pygame.mouse.get_pos())
    # print(pyautogui.position())
    # i += 1
    # print("Tick #: ", i)

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
    # Rambling to myself, ensuring breakpoints weren't bugged:
    # you were having issues knowing what timeframes you were supposed to compare. Are you comparing to last frame,
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
                                        # v - I already tried changing this to popped instead of coords, but neither put the breakpoints right where I expect them.
        pygame.draw.circle(screen, "red", coords, 5, 2)


    # draws a gray circle if the direction is stopped
    elif (direction == "stop"):
        pygame.draw.circle(screen, "gray", coords, 5, 2)
        
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

    # print("\n")

    counter += 1

    pygame.display.update()

pygame.quit()


