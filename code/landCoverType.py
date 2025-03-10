from squareMatrix import SquareMatrix
from bucket import Bucket
from parameter import *

class LandCoverType:
    """A first attempt at writing land cover type code suitable for use in INCA or PERSiST"""

    externalTimeStep=Parameter(86400,"seconds") #static variable for dealing with non-daily time steps
    daysPerStep=1.0 #static variable for scaling daily rates to external time step

    def updateSnowpack(self, P, T):
        if(T<=self.snowfallTemperature):
            self.snowDepth += self.snowfallMultiplier*P
        if(T>self.snowmeltTemperature):
            melt=min(self.snowmeltRate*(T-self.snowmeltTemperature), self.snowDepth)
            self.snowDepth -= melt

    def __init__(self,bucketCount):
        self.name='LandCoverType'
        self.description='A land cover type'

        self.areaProportion=0.1

        self.flowRouting = SquareMatrix(bucketCount)

        self.buckets = [Bucket()]*bucketCount

        self.snowmeltRate = ScaledParameter(3.0,"mm/degree C/day",self.daysPerStep)
        self.snowmeltTemperature = Parameter(0.0, "degrees C")
        self.snowfallTemperature=Parameter(0.0,"degreec C")

        self.initialSnowDepth=Parameter(0.0,"mm")
        self.snowmeltDepth=Parameter(0.0,"mm")

        self.snowDepth=self.initialSnowDepth

        self.snowfallMultiplier=1.0
        self.rainfallMultiplier=1.0

        

