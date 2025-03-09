from parameter import *

class Bucket:
    """first try at some code to generate a PERSiST bucket"""

    externalTimeStep=Parameter(86400,"seconds") #static variable for dealing with non-daily time steps
    daysPerStep=1.0 #static variable for scaling daily rates to external time step

    def calculatePotentialEvapotranspiration(self):
            """boiler plate code to calculate PET"""
            self.potentialEvapotranspiration.value=1.1
    
    def calculateActualEvapotranspiration(self):
        """boiler plate code to calculate actual evapotranspiration (AET)
        depending on soil moisture limitation, currently AET equals PET when there is freely draining water
        when there is loosley bond water, AET is a fraction of PET dependnt on water in the soil and the 
        evapotranspiration adjustment factor. When ther in only tightly bound water, no ET is simulated"""

        boundWaterDepth=self.tightlyBoundStorage() + self.freelyDrainingStorage()

        if(self.currentWaterDepth() > boundWaterDepth):
            #there is water in the bucket that can contribute to runoff 
            self.actualEvapotranspiration.value = min(
                 self.potentialEvapotranspiration(), self.currentWaterDepth()-boundWaterDepth)
            print(self.currentWaterDepth(), boundWaterDepth)
        else: #no freely draining water, check for plant available water
             if(self.currentWaterDepth() > (self.tightlyBoundStorage())):
                  #calculate the rate modifier, which is dependent on how much water is in the loosely bound fraction
                  rateModifier=(self.currentWaterDepth()-self.tightlyBoundStorage())/(self.looselyBoundStorage())
                  rateModifier= rateModifier ** self.evapotranspirationAdjustmentFactor
                  self.actualEvapotranspiration.value = rateModifier * self.potentialEvapotranspiration()
             else: #only tightly bound water ,no ET possible
                  self.actualEvapotranspiration.value=0
        self.currentWaterDepth.value -= self.actualEvapotranspiration.value

    def __init__(self):
        self.name='Bucket'
        self.Description="A conceptual water store"

        self.hasPrecipitationInputs = False

        self.characteristicTimeConstant=ScaledParameter(100, "days",self.daysPerStep)
        self.maximumDepth=Parameter(100,"mm")
        self.freelyDrainingStorage=Parameter(10,"mm")
        self.looselyBoundStorage=Parameter(10,"mm")
        self.tightlyBoundStorage=Parameter(10,"mm")

        self.evapotranspirationAdjustmentFactor=0.0
        self.relativeAreaIndex=1.0

        self.initialWaterDepth=Parameter(50,"mm")
        self.currentWaterDepth=self.initialWaterDepth

        self.potentialEvapotranspiration=ScaledParameter(0,"mm/day",self.daysPerStep)
        self.actualEvapotranspiration=ScaledParameter(0,"mm/day",self.daysPerStep)
        