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
parser.add_argument("-f", "--fileType", metavar="fileType", type=str, default="tm")

args = parser.parse_args()

#open main coordinate file
coord = open(args.coord,"r+")

#open molecule to append to file
molecule = open(args.molecule, "r")

#Start function declarations###########################################
def tmParser(line):
    #prase turbomole file lines

    #check for coord and end lines
    if(line == "$coord\n" or line == "$end\n"):
        return "NAN"

    line2 = line.split("\n")[0].split(space)
    print(line2)
    
    #check for stray spaces
    if(len(line2) > 4):
        line2.pop(0)

    return line2

#####################################################################
def xyzParser(line):
    #xyz parser

    line2 = line.split("\n")[0].split("\r")[0].split(" ")
    line2.append(line2[0])
    line2.pop(0)
    line2 = filter(str.strip,line2)

    return line2

#####################################################################
def parseCoord(File):
    #given coord file, parses out distance and midpoint data 
    #and returns dictionary of data

    #create dictionary for holding data
    data = {
            
            "midpoint":[0.0,0.0,0.0],
            "atomNumber": 0,
            "file":File,
            "lineCount":0

            }

    #iterate over each line in the file that contains atom data
    for line in File:

        #check file format to parse
        if(args.fileType.lower() == "tm"):
            line2 = tmParser(line)
        elif(data["lineCount"] >= 2):
            line2 = xyzParser(line)
        else:
            data["lineCount"] += 1
            continue

        if(line2 == "NAN"):
            continue

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
   
    print("newlines")
    print(newLines)
    print("$$$$$$$$$$$$$$$$4")

    return newLines

############################################
def newPosition(data, newMidpoint):

    newLines = ""
    data["file"].seek(0)

    lineCount = 0

    #calculate delta for each atom in molecule
    delta = [ newMidpoint[dim] - data["midpoint"][dim] for dim in range(3) ]
    print(0)
    #iterate overl all lines in coord file
    for line in data["file"]:
            
        #check file format to parse
        if(args.fileType.lower() == "tm"):
            line2 = tmParser(line)
        elif(lineCount >= 2):
            line2 = xyzParser(line)
        else:
            lineCount += 1
            continue

        #calculate new coord for each atom using delta
        newCoord = [ str(float(line2[dim]) + delta[dim]) for dim in range(3) ]
        
        print(newCoord)
        print("newCoord")

        #convert newCoord to TM coord friendly data
        if(args.fileType.lower() == "tm"):
            newLines += "\n" + space + newCoord[0] + space + newCoord[1] + space + newCoord[2] + space + line2[3]
        else:
            newLines += "\n" + line2[3] + space + newCoord[0] + space + newCoord[1] + space + newCoord[1]
    print("testtestmnewlines")
    print(newLines[:1])
    print("!!!!!!!!!!!!!!!!")
    return newLines

############################################
#creates new coord file in either xyz or TM format
def createNewCoord(linesToAppend):

    if(args.fileType.lower() == "tm"):
        print("creating tm style new coord file")

    else:
        #create xyz style coord file
        
        #get number of atoms in file
        atomNumber = int(os.popen("head -n 1 " + args.coord).read())

        #increment atom number by number of atoms to append to main molecule file
        header = str(atomNumber + len(linesToAppend.split("\n")) - 1) + "\n\n" 

        #get baseAtoms that will be added to new file from original coord file
        baseAtoms = os.popen("tail -n +3 " + args.coord).read()

        newCoord = header + baseAtoms + linesToAppend[1:]
    
        #create new coord 
        os.popen("echo '" + newCoord + "' > new" + args.coord)
        

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

#append new lines to new coord file
#delete last line in coord file
#os.popen("head -n-1 " + args.coord + " > " + "new" + args.coord)

print(linesToAppend)
print("LINESTOAPPEND")

#create new coord file with two molecules "mixed" together
createNewCoord(linesToAppend)

