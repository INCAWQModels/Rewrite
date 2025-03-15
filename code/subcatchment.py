from landCoverType import LandCoverType
from reach import Reach
from chemical import Chemical

class Subcatchment:
    """First try at writing code for subcatchment / reach pools and processes in INCA / PERSiST"""
    
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