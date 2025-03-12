from parameter import *
from catchment import Catchment
from timeSeries import TimeSeries
from parameterSet import ParameterSet

class Model:
    """A first attempt at writing the code to run an INCA/PERSiST model"""

    externalTimeStep=Parameter(86400,"seconds") 
    internalStepsPerTimeStep=1.0
    
    def __init__(self,jsonFile):
        self.parameterSet=ParameterSet(jsonFile)
        
        self.catchment = Catchment(self.parameterSet)
        self.drivingData=TimeSeries()