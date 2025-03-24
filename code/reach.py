#from parameter import Parameter, ScaledParameter
from chemical import Chemical

class Reach:
    """First try at implementing the in-stream component of a subcatchment"""

    def __init__(self,pars,reachIndex):
        self.name=pars.parameters["reach"]["general"]["name"][reachIndex]
        self.description="A stream reach"

        self.length=pars.parameters["reach"]["general"]["length"][reachIndex]
        self.widthAtBottom=pars.parameters["reach"]["general"]["widthAtBottom"][reachIndex]
        self.slope=pars.parameters["reach"]["general"]["slope"][reachIndex]

        self.outflow = pars.parameters["reach"]["general"]["outflow"][reachIndex]

        self.inflows = []   #fix later

        self.hasChemicals=False #flag variable to simplify decision making
        Chemical.addChemicals(self,pars)

        self.Manning = {
            "a" : pars.parameters["reach"]["hydrology"]["Manning"]["a"][reachIndex], 
            "b" : pars.parameters["reach"]["hydrology"]["Manning"]["b"][reachIndex], 
            "c" : pars.parameters["reach"]["hydrology"]["Manning"]["c"][reachIndex], 
            "f" : pars.parameters["reach"]["hydrology"]["Manning"]["f"][reachIndex], 
            "n" : pars.parameters["reach"]["hydrology"]["Manning"]["n"][reachIndex] 
        }

        #set flow to initial conditions
        self.Flow=pars.parameters["reach"]["hydrology"]["initialFlow"][reachIndex]
        
        self.hasAbstraction=pars.parameters["reach"]["hydrology"]["hasAbstraction"][reachIndex]
        self.hasEffluent=pars.parameters["reach"]["hydrology"]["hasEffluent"][reachIndex]


