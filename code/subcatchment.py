from concurrent.futures import ProcessPoolExecutor

from landCoverType import LandCoverType
from chemical import Chemical
from timeSeries import TimeSeries

class Subcatchment:
    """First try at writing code for subcatchment / reach pools and processes in INCA / PERSiST"""

    def solve(self):
        """Code stub to solve hydrochemical transformation and fluxes in a subcatchment"""
        results = TimeSeries 

        #put the system under load
        print("Loading subcatchment ", self.name)        
        return results
    
    def solveLandCoverTypes(self,landCoverIndex):
         with ProcessPoolExecutor() as executor:
            executor.map(self.catchment.sub)

    
    def __init__(self, pars,subCatchmentIndex):#geographical coordinates of the outflow
        self.latitude=pars.parameters["subcatchment"]["general"]["latitudeAtOutflow"][subCatchmentIndex]
        self.longitude=pars.parameters["subcatchment"]["general"]["longitudeAtOutflow"][subCatchmentIndex]

        landCoverCount=pars.parameters['landCover'].__len__()
        
        self.name = pars.parameters['subcatchment']['general']['name'][subCatchmentIndex]

        self.description="The terrestrial and aquatic parts of a subcatchment / reach system"

        self.area=pars.parameters['subcatchment']['general']['area'][subCatchmentIndex]    #total subcatchment area
        
        self.landCoverTypes = []
        for i in range(landCoverCount):
            self.landCoverTypes.append(LandCoverType(pars,subCatchmentIndex,i))

        self.hasChemicals=False #flag variable to simplify decision making
        Chemical.addChemicals(self,pars)