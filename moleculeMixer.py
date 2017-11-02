#writtern by Gary Zeri, Part of Furche Group UCI NS2
#Script to take two Turbomole molecule files and combine the two molecules into one file
#Used to create multiple instances of one molecule within the coord file of another molecule

import argparse
import os
import math
from random import randint

nan = -1000000.01010101
space = "    "

#start argument parser
parser = argparse.ArgumentParser()

parser.add_argument("-c", "--coord", metavar="coord", type=str, default="coord")
parser.add_argument("-m", "--molecule", metavar="molecule", type=str, default="molecule")
#parser.add_argument("-r", "--random", metavar="random", type=bool, default=True)
parser.add_argument("-d", "--distance", metavar="distance", type=float, default=nan)
parser.add_argument("-mxd", "--maxDistance", metavar="maxDistance", type=float, default=100)
parser.add_argument("-mnd", "--minDistance", metavar="minDistance", type=float, default=0)
parser.add_argument("-i", "--instances", metavar="instances", type=int, default=1)

args = parser.parse_args()

#open main coordinate file
coord = open(args.coord,"r+")

#open molecule to append file
molecule = open(args.molecule, "r")

#Start function declarations###########################################
def parseCoord(File):
    #given coord file, parses out distance and midpoint data 
    #and returns dictionary of data

    #create dictionary for holding data
    data = {
            
            "midpoint":[0.0,0.0,0.0],
            "atomNumber": 0,
            "file":File

            }

    #iterate over each line in the file that contains atom data
    for line in File:

        #check for coord and end lines
        if(line == "$coord\n" or line == "$end\n"):
            continue

        line2 = line.split("\n")[0].split(space)
        print(line2)
        
        #increamnet atom count
        data["atomNumber"] += 1

        #increment midpoint
        for dim in range(3):
            data["midpoint"][dim] += float(line2[dim])

    #finish midpoint calculation by dividing by the total number of atoms
    data["midpoint"] = [ mp/data["atomNumber"] for mp in data["midpoint"] ]

    return data

############################################
def RSI(coordData, moleculeData, args):
    #uses a sphere to randomly integrate one molecule into another coord file
    
    #init variables for calculation
    if (args.distance == nan):
        hypotenuse = randint(args.minDistance,args.maxDistance)
    else:
        hypotenuse = args.distance

    theta = randint(0,359)

    #calculate final x, y coordinate of molecule
    X = (hypotenuse * math.cos(theta)) + coordData["midpoint"][0]
    Y = (hypotenuse * math.sin(theta)) + coordData["midpoint"][1]
    Z = (hypotenuse * math.sin(theta) * math.cos(theta)) + coordData["midpoint"][2]

    newLines = newPosition(moleculeData, [X,Y,Z])
    
    return newLines

############################################
def newPosition(data, newMidpoint):

    newLines = ""
    data["file"].seek(0)

    #calculate delta for each atom in molecule
    delta = [ newMidpoint[dim] - data["midpoint"][dim] for dim in range(3) ]
    print(0)
    #iterate overl all lines in coord file
    for line in data["file"]:
        print(1)
        #check for coord and end lines
        if(line == "$coord\n" or line == "$end\n"):
            continue
       
        line2 = line.split("\n")[0].split(space)
        print(line2[0])  
        #calculate new coord for each atom using delta
        newCoord = [ str(float(line2[dim]) + delta[dim]) for dim in range(3) ]
        
        print(newCoord)
        print("newCoord")

        #convert newCoord to TM coord friendly data
        newLines += "\n" + space + newCoord[0] + space + newCoord[1] + space + newCoord[2] + space + line2[3]
        
    return newLines[2:]

#Start of main code###########################################
#get coord and molecule data
coordData = parseCoord(coord)
moleculeData = parseCoord(molecule)

print(coordData["midpoint"])
print(moleculeData["midpoint"])

#init variable to hold strings to append to file
linesToAppend = ""

#place requested number of molecules in random positions at random distances using given constraints
#uses random spherical integration method
for i in range(args.instances):
    linesToAppend += RSI(coordData, moleculeData, args)
    linesToAppend += "\n"

#append new lines to new coord file
#delete last line in coord file
os.popen("head -n-1 " + args.coord + " > " + "new" + args.coord)

#append new lines to file
os.popen('echo "' + linesToAppend[:-1] + '" >> new' + args.coord)
os.popen("echo '$end\n' >> new" + args.coord)

#close open files
coordData["file"].close()
moleculeData["file"].close()

