from parameter import *

class Chemical:
    """A first try at writing a class to model chemical transformations and transport in INCA"""

    def addChemicals(target,pars):
        """add chemicals if listed in the parameter set, target is the object (bucket, reach, etc.)"
        to whihc chemicals are added"""
        if(pars.parameters['chemicals']):
            target.hasChemicals=True
            chemicalCount=pars.parameters['chemicals'].__len__()
            target.chemicals = []
            for i in range (chemicalCount):
                target.chemicals.append(Chemical(pars,i))

    def __init__(self,pars,chemicalIndex):
        self.name = pars.parameters['chemicals']['chemical'][chemicalIndex]['name']
        self.abbreviation = pars.parameters['chemicals']['chemical'][chemicalIndex]['abbreviation']
        self.mass = pars.parameters['chemicals']['chemical'][chemicalIndex]['mass']