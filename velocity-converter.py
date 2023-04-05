# velocity-converter.py
# NOTE: this file was used like a Jupyter notebook - running parts of it, until I got the desired output.
# Much of the code that was used once, was commented out for another task.

# Converts the dataset from being absolute coordinate-based, to relative "velocity"-based.
# i.e. each recorded coordinate is the distance from the previous coordinate.
# Only changes the "pointing" tasks, and a commented-out section of the code deleted all files that used a "TOUCH" device.
# Author: Connor Hickton
# 

import json
import time
import math
import os
import shutil

from tkinter import Tk
from tkinter.filedialog import askopenfilename
from tkinter import filedialog

from sharedfunctions import *


# open file in read mode
useridfile = open("mouseandtouchinput-velocity-modified/userid_mouse_tremor_pointing.txt", "r")

userids = useridfile.read()

useridlist = userids.split("\n")

useridlist.sort()

print(useridlist)

# load json file
# User 258 is identified in the data as able-bodied and skilled enough with a mouse. Good subject to use to sanity-check that targets are appearing in the right place
# New: tkinter opens a file explorer box, and you can choose which file to open.
foldername = filedialog.askdirectory()

pointingTasks = 0

for root, dirs, files in os.walk(foldername):
    

    """
    for dirname in dirs:
        
        if (dirname[6:] not in useridlist):
            print(dirname, " does not fit the criteria")
            source = (os.path.join(root, dirname))
            shutil.rmtree(source)
        else:
            print(dirname, " FITS THE CRITERIA!")
    """
    
    for filename in files:
        source = (os.path.join(root, filename))
        f = open(source, "r+")
        data = json.load(f)

        if("DESKTOP" in filename):

            if (data["taskName"] == "Pointing"):
                pointingTasks += 1
                print("Pointing Tasks Found: ", pointingTasks)

                # tracks the time that the previous mouse event happened at (in ms). Starts at the time the trial began, in ms since epoch
                last = data['startTime']
                #print(last)

                # Main game loop. Iterates through each of the "trials" stored in the JSON files.
                for h in range(len(data["trials"])):

                    lastCoords = (None, None)


                """   
                    # This section translates the absolute coordinates into the relative velocities.
                    for j in data['trials'][h]['mouseEvents']:

                        
                        # get next set of mouse coords from JSON
                        coords = (j["p"]["X"], j["p"]["Y"])
                        coordTime = (j["t"])

                        if (lastCoords[0] != None):
                            velocity = (coords[0] - lastCoords[0], coords[1] - lastCoords[1])
                        else:
                            velocity = (0,0)

                        print("VELOCITIES: ", velocity)
                        j["p"]["X"] = velocity[0]
                        j["p"]["Y"] = velocity[1]

                        lastCoords = coords
                        
                f.seek(0)
                json.dump(data, f)
                """
            else:
                f.close()
                os.remove(source)

        """
        elif ("TOUCH" in filename):
            f.close()
            os.remove(source)
        """










        
