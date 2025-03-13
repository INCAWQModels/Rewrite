from landCoverType import LandCoverType
from parameter import Parameter
from reach import Reach
from chemical import Chemical

class Subcatchment:
    """First try at writing code for subcatchment / reach pools and processes in INCA / PERSiST"""

    externalTimeStep=Parameter(86400,"seconds") #static variable for dealing with non-daily time steps
    daysPerStep=1.0 #static variable for scaling daily rates to external time step

    def __init__(self, pars,subcatchmentIndex):

        landCoverCount=pars.parameters['landCoverTypes']['landCoverType'].__len__()
        
        self.name = pars.parameters['subCatchments']['subCatchment'][subcatchmentIndex]['name']

        self.description="The terrestrial and aquatic parts of a subcatchment / reach system"

        self.area=Parameter(1.0,"km2")    #total subcatchment area
        self.snowmeltOffest=Parameter(0.0,"degrees C")
        self.snowfallOffset=Parameter(0.0,"degrees C")
        self.rainfallMultiplier=1.0
        self.snowfallMultiplier=1.0

        self.reach = Reach(pars)
        
        self.landCoverTypes = []
        for i in range(landCoverCount):
            self.landCoverTypes.append(LandCoverType(pars,i))

        self.hasChemicals=False #flag variable to simplify decision making
        Chemical.addChemicals(self,pars)