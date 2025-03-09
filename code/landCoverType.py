from squareMatrix import SquareMatrix
from bucket import Bucket
from parameter import *

class LandCoverType:
    """A first attempt at writing land cover type code"""

    def updateSnowpack(self, P, T):
        if(T<=self.snowfallTemperature):
            self.snowDepth += self.snowfallMultiplier*P
        if(T>self.snowmeltTemperature):
            melt=min(self.snowmeltRate*(T-self.snowmeltTemperature), self.snowDepth)
            self.snowDepth -= melt
              
    def __init__(self,bucketCount):
        self.name='LandCoverType'
        self.description='A land cover type'

        self.flowRouting = SquareMatrix(bucketCount)

        self.buckets = [Bucket()]*bucketCount

        self.snowmeltRate = Parameter(3.0,"mm/degree C/day")
        self.snowmeltTemperature = Parameter(0.0, "degrees C")
        self.snowfallTemperature=Parameter(0.0,"degreec C")

        self.initialSnowDepth=Parameter(0.0,"mm")
        self.snowmeltDepth=Parameter(0.0,"mm")

        self.snowDepth=self.initialSnowDepth

        self.snowfallMultiplier=1.0
        self.rainfallMultiplier=1.0

        

