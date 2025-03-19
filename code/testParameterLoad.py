import os

from parameterSet import ParameterSet

def testBed():

    fileName = 'pars.json'

    if (os.path.isfile(fileName) == True):
        p=ParameterSet('INCAFormatParSet.json')
        p.printPars()

        print(p.parameters["general"]["name"] )

if __name__ == '__main__':
    testBed()