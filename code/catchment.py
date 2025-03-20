from subcatchment import Subcatchment
from reach import Reach
from chemical import Chemical

class Catchment:
    """First attempt at creating a catchment representation in INCA/PERSiST"""
  
    def solveSubcatchments(self, subcatchmentIndex):
        """stub to solve inputs and outputs from subcatchments"""

        self.subcatchments[subcatchmentIndex].solve()
        subcatchmentExportsToReach = []
        
        return subcatchmentExportsToReach

    def __init__(self,pars):

        subcatchmentCount=pars.parameters["subcatchment"]["general"]["name"].__len__()
        
        self.name=pars.parameters["general"]["name"]

        self.subcatchments = []
        self.reaches = []
        for i in range(subcatchmentCount):
            self.subcatchments.append(Subcatchment(pars,i))
            self.reaches.append(Reach(pars,i))
        
        self.hasChemicals=False #flag variable to simplify decision making
        Chemical.addChemicals(self,pars)