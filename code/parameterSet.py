from json import load,dump
from parameter import *

class ParameterSet:
    """Class to store a parameter set, currently the initializer reads from a JSON file 
    but this might requre a bit or thought down the road. The parameters are stored as a dictionary"""

    def printPars(self): #troubleshooting routine to print contents of self.parameters
        print(self.parameters)

    def saveToJSON(self,jsonfile):
        with open(jsonfile, "w") as outfile:
            dump(self.parameters,outfile)

    def __init__(self,fileName):
        with open(fileName,'r') as parFile:
            self.parameters = load(parFile)
    