from chemical import Chemical

class Bucket:
    """first try at some code to generate an INCA/PERSiST bucket. Water properties are enforced in all cases
    but chemcial properties are optional, depending on the contents of the JSON parameter file"""

    def calculatePotentialEvapotranspiration(self):
            """boiler plate code to calculate PET"""
            self.potentialEvapotranspiration.value=1.1
    
    def calculateActualEvapotranspiration(self):
        """boiler plate code to calculate actual evapotranspiration (AET)
        depending on soil moisture limitation, currently AET equals PET when there is freely draining water
        when there is loosley bond water, AET is a fraction of PET dependent on water in the soil and the 
        evapotranspiration adjustment factor. When there in only tightly bound water, no ET is simulated.
        Note that this code also lowers the depth of water in the bucket, might want to rethink this"""

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

    def __init__(self,pars,landCoverIndex, bucketIndex):
        self.name=pars.parameters['landCover']['bucket'][bucketIndex]['general']['name']
        self.surficial=pars.parameters['landCover']['bucket'][bucketIndex]['general']['surficial']

        self.Description="A conceptual water store"

        externalTimeStep=pars.parameters['general']['timeStep']
        daysPerStep=externalTimeStep/86400.0

        #characteristic time constant has units of days in the parameter set, needs to be scaled to the model time step
        self.characteristicTimeConstant=pars.parameters['landCover']['bucket'][bucketIndex]['hydrology']['characteristicTimeConstant'][landCoverIndex]
        self.characteristicTimeConstant /= daysPerStep

        self.freelyDrainingWaterDepth=pars.parameters['landCover']['bucket'][bucketIndex]['hydrology']['freelyDrainingWaterDepth'][landCoverIndex]
        self.looselyBoundWaterDepth=pars.parameters['landCover']['bucket'][bucketIndex]['hydrology']['looselyBoundWaterDepth'][landCoverIndex]
        self.tightlyBoundWaterDepth=pars.parameters['landCover']['bucket'][bucketIndex]['hydrology']['tightlyBoundWaterDepth'][landCoverIndex]

        self.maximumWaterDepth=self.freelyDrainingWaterDepth+self.tightlyBoundWaterDepth+self.looselyBoundWaterDepth
        self.waterDepth=pars.parameters['landCover']['bucket'][bucketIndex]['hydrology']['initialWaterDepth'][landCoverIndex]

        self.relativeAreaIndex=pars.parameters['landCover']['bucket'][bucketIndex]['general']['relativeAreaIndex'][landCoverIndex]
        self.relativeETIndex=pars.parameters['landCover']['bucket'][bucketIndex]['hydrology']['relativeETIndex'][landCoverIndex]
        self.ETScalingExponent=pars.parameters['landCover']['bucket'][bucketIndex]['hydrology']['ETScalingExponent'][landCoverIndex]
        
        #set the parameters for performing soil temperature calculations, starting with the temperature
        self.soilTemperature = pars.parameters['landCover']['bucket'][bucketIndex]['general']['initialSoilTemperature']
        self.soilTemperatureEffectiveDepth=pars.parameters['landCover']['bucket'][bucketIndex]['general']['soilTemperatureEffectiveDepth'][landCoverIndex]

        #iniitialize actual and potential evapotranspiration to 0.0
        self.potentialEvapotranspiration=0.0
        self.actualEvapotranspiration=0.0

        self.hasChemicals=False #flag variable to simplify decision making
        Chemical.addChemicals(self,pars)

        self.hasSolidPhase=False #flag variable to indicate if solids are to be modelled

        