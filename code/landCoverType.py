from squareMatrix import SquareMatrix
from bucket import Bucket
from chemical import Chemical

class LandCoverType:
    """A first attempt at writing land cover type code suitable for use in INCA or PERSiST"""

    def updateSnowpack(self, P, T):
        if(T<=self.snowfallTemperature):
            self.snowDepth += self.snowfallMultiplier*P
        if(T>self.snowmeltTemperature):
            melt=min(self.snowmeltRate*(T-self.snowmeltTemperature), self.snowDepth)
            self.snowDepth -= melt

    def __init__(self,pars,subCatchmentIndex,landCoverIndex):

        bucketCount=pars.parameters['buckets']['bucket'].__len__()
        
        externalTimeStep=pars.parameters['timeStep']
        daysPerStep=externalTimeStep/86400.0

        self.name=pars.parameters['landCoverTypes']['landCoverType'][landCoverIndex]['name']
        self.description='A land cover type'

        self.percentCover=pars.parameters['subCatchments']['subCatchment'][subCatchmentIndex]['landCoverTypes'][landCoverIndex]['percentCover']
        self.waterDepth=pars.parameters['landCoverTypes']['landCoverType'][landCoverIndex]['waterDepth']

        self.flowRouting = SquareMatrix(bucketCount)

        #create the buckets
        self.buckets = []
        for i in range(bucketCount):
            self.buckets.append(Bucket(pars,i))

        self.snowmeltRate = pars.parameters['landCoverTypes']['landCoverType'][landCoverIndex]['snowmeltRate'] / daysPerStep
        self.snowmeltDepth=0.0
        self.snowDepth=pars.parameters['landCoverTypes']['landCoverType'][landCoverIndex]['snowDepth'] 

        #snowmelt temperature is the sum of the landscape type and subcatchment snowmelt temperatures
        self.snowmeltTemperature = pars.parameters['landCoverTypes']['landCoverType'][landCoverIndex]['snowmeltTemperature'] 
        self.snowmeltTemperature += pars.parameters['subCatchments']['subCatchment'][subCatchmentIndex]['snowmeltTemperature']

        #snowmelt temperature is the sum of the landscape type and subcatchment snowfall temperatures
        self.snowfallTemperature = pars.parameters['landCoverTypes']['landCoverType'][landCoverIndex]['snowfallTemperature'] 
        self.snowfallTemperature += pars.parameters['subCatchments']['subCatchment'][subCatchmentIndex]['snowfallTemperature']
  
        #snowfall multiplier is the prodict of the landscape type and subcatchment snowfall multiplier
        self.snowfallMultiplier = pars.parameters['landCoverTypes']['landCoverType'][landCoverIndex]['snowfallMultiplier'] 
        self.snowfallMultiplier *= pars.parameters['subCatchments']['subCatchment'][subCatchmentIndex]['snowfallMultiplier'] 
        
        #rainfall multiplier is the prodict of the landscape type and subcatchment rainfall multiplier      
        self.rainfallMultiplier=pars.parameters['landCoverTypes']['landCoverType'][landCoverIndex]['rainfallMultiplier'] 
        self.rainfallMultiplier *= pars.parameters['subCatchments']['subCatchment'][subCatchmentIndex]['rainfallMultiplier'] 
              
        self.hasChemicals=False #flag variable to simplify decision making
        Chemical.addChemicals(self,pars)

