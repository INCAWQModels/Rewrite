from subcatchment import Subcatchment
from parameter import Parameter

class Catchment:
    """First attempt at creating a catchmnet representation in INCA"""

    externalTimeStep=Parameter(86400,"seconds") #static variable for dealing with non-daily time steps
    daysPerStep=1.0 #static variable for scaling daily rates to external time step
    
    def __init__(self,bucketCount, landCoverCount, subcatchmentCount):
        
         self.subcatchments = [Subcatchment(bucketCount,landCoverCount)]*subcatchmentCount