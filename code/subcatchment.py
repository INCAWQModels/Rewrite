from landCoverType import LandCoverType
from chemical import Chemical
from timeSeries import TimeSeries
from fib0 import fib

class Subcatchment:
    """First try at writing code for subcatchment / reach pools and processes in INCA / PERSiST"""

    #code to put the system under load, diagnostics only
    x=fib(40)

    def solve(self):
        """Code stub to solve hydrochemical transformation and fluxes in a subcatchment"""
        results = TimeSeries 

        #do something to put some load on the system
        

        return results

    
    def __init__(self, pars,subCatchmentIndex):

        landCoverCount=pars.parameters['landCoverTypes'].__len__()
        
        self.name = pars.parameters['subCatchments'][subCatchmentIndex]['name']

        self.description="The terrestrial and aquatic parts of a subcatchment / reach system"

        self.area=pars.parameters['subCatchments'][subCatchmentIndex]['area']    #total subcatchment area
        
        self.landCoverTypes = []
        for i in range(landCoverCount):
            self.landCoverTypes.append(LandCoverType(pars,subCatchmentIndex,i))

        self.hasChemicals=False #flag variable to simplify decision making
        Chemical.addChemicals(self,pars)