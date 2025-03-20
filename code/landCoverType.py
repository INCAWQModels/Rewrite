from squareMatrix import SquareMatrix
from bucket import Bucket
from chemical import Chemical

class LandCoverType:
    """A first attempt at writing land cover type code suitable for use in INCA or PERSiST"""

    def solve():
        pass

    def updateSnowpack(self, P, T):
        if(T<=self.snowfallTemperature):
            self.snowDepth += self.snowfallMultiplier*P
        if(T>self.snowmeltTemperature):
            melt=min(self.snowmeltRate*(T-self.snowmeltTemperature), self.snowDepth)
            self.snowDepth -= melt

    def __init__(self,pars,subCatchmentIndex,landCoverIndex):

        bucketCount=pars.parameters['landCover']['bucket'].__len__()
        
        externalTimeStep=pars.parameters['general']['timeStep']
        daysPerStep=externalTimeStep/86400.0

        self.name=pars.parameters['landCover']['general']['name'][landCoverIndex]

        self.percentCover=pars.parameters['subcatchment']['general']['landCoverPercent'][subCatchmentIndex][landCoverIndex]
        
        self.flowRouting = SquareMatrix(bucketCount)

        #create the buckets
        self.buckets = []
        for i in range(bucketCount):
            self.buckets.append(Bucket(pars,landCoverIndex,i))

        self.snowmeltRate = pars.parameters['landCover']['hydrology']['snowmeltRate'][landCoverIndex] / daysPerStep
        self.snowmeltDepth=0.0
        self.snowDepth=pars.parameters['landCover']['hydrology']['snowDepth'][landCoverIndex]

        #snowmelt temperature is the sum of the landscape type and subcatchment snowmelt temperatures
        self.snowmeltTemperature = pars.parameters['landCover']['hydrology']['snowmeltTemperature'][landCoverIndex]
        self.snowmeltTemperature += pars.parameters['subcatchment']['hydrology']['snowmeltTemperature'][subCatchmentIndex]

        #snowmelt temperature is the sum of the landscape type and subcatchment snowfall temperatures
        self.snowfallTemperature = pars.parameters['landCover']['hydrology']['snowfallTemperature'][landCoverIndex] 
        self.snowfallTemperature += pars.parameters['subcatchment']['hydrology']['snowfallTemperature'][subCatchmentIndex]
  
        #snowfall multiplier is the product of the landscape type and subcatchment snowfall multiplier
        self.snowfallMultiplier = pars.parameters['landCover']['hydrology']['snowfallMultiplier'][landCoverIndex] 
        self.snowfallMultiplier *= pars.parameters['subcatchment']['hydrology']['snowfallMultiplier'][subCatchmentIndex] 
        
        #rainfall multiplier is the product of the landscape type and subcatchment rainfall multiplier      
        self.rainfallMultiplier=pars.parameters['landCover']['hydrology']['rainfallMultiplier'][landCoverIndex] 
        self.rainfallMultiplier *= pars.parameters['subcatchment']['hydrology']['rainfallMultiplier'][subCatchmentIndex] 
              
        self.hasChemicals=False #flag variable to simplify decision making
        Chemical.addChemicals(self,pars)

