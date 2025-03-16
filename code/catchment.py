from subcatchment import Subcatchment
from reach import Reach
from chemical import Chemical

class Catchment:
    """First attempt at creating a catchment representation in INCA/PERSiST"""
  
    def solveCatchments(self):
        """stub to solve inputs and outputs from subcatchments"""
        subcatchmentExportsToReach = []
        
        return subcatchmentExportsToReach

    def __init__(self,pars):

        subcatchmentCount=pars.parameters['subCatchments'].__len__()
        
        self.name=pars.parameters['catchment']['name']

        self.subcatchments = []
        self.reaches = []
        for i in range(subcatchmentCount):
            self.subcatchments.append(Subcatchment(pars,i))
            self.reaches.append(Reach(pars,i))
        
        self.hasChemicals=False #flag variable to simplify decision making
        Chemical.addChemicals(self,pars)