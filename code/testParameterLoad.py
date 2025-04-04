import os

from parameterSet import ParameterSet

def testBed():

    fileName = 'INCAFormatParSet.json'

    if (os.path.isfile(fileName) == True):
        p=ParameterSet(fileName)
        
if __name__ == '__main__':
    testBed()