from landCoverType import LandCoverType
from chemical import Chemical
from timeSeries import TimeSeries

class Subcatchment:
    """First try at writing code for subcatchment / reach pools and processes in INCA / PERSiST"""

    def solve(self):
        """Code stub to solve hydrochemical transformation and fluxes in a subcatchment"""
        results = TimeSeries 
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