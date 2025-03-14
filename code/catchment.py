from subcatchment import Subcatchment
from reach import Reach
from parameterSet import ParameterSet
from chemical import Chemical

class Catchment:
    """First attempt at creating a catchment representation in INCA/PERSiST"""
  
    def __init__(self,pars):

        subcatchmentCount=pars.parameters['subCatchments']['subCatchment'].__len__()
        
        self.name=pars.parameters['catchment']['name']

        self.subcatchments = []
        for i in range(subcatchmentCount):
            self.subcatchments.append(Subcatchment(pars,i))
        
        self.hasChemicals=False #flag variable to simplify decision making
        Chemical.addChemicals(self,pars)