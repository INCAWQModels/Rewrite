from parameter import *

class model:
    """A first attempt at writing the code to run an INCA/PERSiST model"""

    def __init__(self):
        self.externalTimeStep=Parameter(86400,"seconds") 
        self.internalStepsPerTimeStep=1.0