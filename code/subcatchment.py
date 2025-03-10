from landCoverType import LandCoverType
from parameter import Parameter, ScaledParameter

class Subcatchment:
    """First try at writing code for subcatchment / reach pools and processes in INCA / PERSiST"""

    externalTimeStep=Parameter(86400,"seconds") #static variable for dealing with non-daily time steps
    daysPerStep=1.0 #static variable for scaling daily rates to external time step

    def __init__(self, bucketCount, landCoverCount):
        self.name = "Subcatchment"
        self.description="The terrestrial and aquqtuc parts of a subcatchment / reach system"

        self.area=Parameter(1,"km2")    #total subcatchment area
        self.snowmeltOffest=Parameter(0,"degrees C")
        self.snowfallOffset=Parameter(0,"degrees C")
        self.rainfallMultiplier=1.0
        self.snowfallMultiplier=1.0

        self.landCoverTypes = [LandCoverType(bucketCount)]*landCoverCount