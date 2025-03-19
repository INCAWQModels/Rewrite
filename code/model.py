from concurrent.futures import ProcessPoolExecutor

from catchment import Catchment
from timeSeries import TimeSeries
from parameterSet import ParameterSet
from chemical import Chemical

class Model:
    """A first attempt at writing the code to run an INCA/PERSiST model"""

    def run(self):
        """Code stub to run a model"""
         #there has to be a more elegant way to do this!
        subcatchmentIDs = []
        for k in range(self.catchment.subcatchments.__len__()):
            subcatchmentIDs.append(k)
        
        with ProcessPoolExecutor() as executor:
            executor.map(self.catchment.solveSubcatchments,subcatchmentIDs)

    def __init__(self,jsonFile):
        self.parameterSet=ParameterSet(jsonFile)
        self.parameterSet.printPars()
        
        self.catchment = Catchment(self.parameterSet)
        self.drivingData=TimeSeries()

        self.hasChemicals=False #flag variable to simplify decision making
        Chemical.addChemicals(self,self.parameterSet) #not the most elegant but it reuses code