from subcatchment import Subcatchment
from reach import Reach
from parameter import Parameter
from parameterSet import ParameterSet

class Catchment:
    """First attempt at creating a catchment representation in INCA/PERSiST"""

    externalTimeStep=Parameter(86400,"seconds") #static variable for dealing with non-daily time steps
    daysPerStep=1.0 #static variable for scaling daily rates to external time step
    
    def __init__(self,pars):

        subcatchmentCount=pars.parameters['subCatchments']['subCatchment'].__len__()
        
        self.name=pars.parameters['catchment']['name']

        self.subcatchments = []
        for i in range(subcatchmentCount):
            self.subcatchments.append(Subcatchment(pars,i))
        
        self.reach = Reach()