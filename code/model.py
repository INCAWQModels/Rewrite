from parameter import *
from catchment import Catchment

class model:
    """A first attempt at writing the code to run an INCA/PERSiST model"""

    externalTimeStep=Parameter(86400,"seconds") 
    internalStepsPerTimeStep=1.0
    
    def __init__(self):
        catchment = Catchment(1,2,3)