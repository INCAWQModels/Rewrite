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

        self.name=pars.parameters['landCover']['name'][landCoverIndex]

        self.percentCover=pars.parameters['subCatchments'][subCatchmentIndex]['landCoverTypes'][landCoverIndex]['percentCover']
        
        self.flowRouting = SquareMatrix(bucketCount)

        #create the buckets
        self.buckets = []
        for i in range(bucketCount):
            self.buckets.append(Bucket(pars,landCoverIndex,i))

        self.snowmeltRate = pars.parameters['landCoverTypes'][landCoverIndex]['snowmeltRate'] / daysPerStep
        self.snowmeltDepth=0.0
        self.snowDepth=pars.parameters['landCoverTypes'][landCoverIndex]['snowDepth'] 

        #snowmelt temperature is the sum of the landscape type and subcatchment snowmelt temperatures
        self.snowmeltTemperature = pars.parameters['landCoverTypes'][landCoverIndex]['snowmeltTemperature'] 
        self.snowmeltTemperature += pars.parameters['subCatchments'][subCatchmentIndex]['snowmeltTemperature']

        #snowmelt temperature is the sum of the landscape type and subcatchment snowfall temperatures
        self.snowfallTemperature = pars.parameters['landCoverTypes'][landCoverIndex]['snowfallTemperature'] 
        self.snowfallTemperature += pars.parameters['subCatchments'][subCatchmentIndex]['snowfallTemperature']
  
        #snowfall multiplier is the product of the landscape type and subcatchment snowfall multiplier
        self.snowfallMultiplier = pars.parameters['landCoverTypes'][landCoverIndex]['snowfallMultiplier'] 
        self.snowfallMultiplier *= pars.parameters['subCatchments'][subCatchmentIndex]['snowfallMultiplier'] 
        
        #rainfall multiplier is the product of the landscape type and subcatchment rainfall multiplier      
        self.rainfallMultiplier=pars.parameters['landCoverTypes'][landCoverIndex]['rainfallMultiplier'] 
        self.rainfallMultiplier *= pars.parameters['subCatchments'][subCatchmentIndex]['rainfallMultiplier'] 
              
        self.hasChemicals=False #flag variable to simplify decision making
        Chemical.addChemicals(self,pars)

