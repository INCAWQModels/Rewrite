#from parameter import Parameter, ScaledParameter
from chemical import Chemical

class Reach:
    """First try at implementing the in-stream component of a subcatchment"""

    def __init__(self,pars,reachIndex):
        self.name=pars.parameters["reaches"][reachIndex]["name"]
        self.description="A stream reach"

        self.length=pars.parameters["reaches"][reachIndex]["length"]
        self.widthAtBottom=pars.parameters["reaches"][reachIndex]["widthAtBottom"]
        self.slope=pars.parameters["reaches"][reachIndex]["slope"]

        #geographical coordinates of the outflow
        self.latitude=pars.parameters["reaches"][reachIndex]["latitude"]
        self.longitude=pars.parameters["reaches"][reachIndex]["longitude"]

        self.hasChemicals=False #flag variable to simplify decision making
        Chemical.addChemicals(self,pars)

        self.Manning = {
            "a" : pars.parameters["reaches"][reachIndex]["Manning"]["a"], 
            "b" : pars.parameters["reaches"][reachIndex]["Manning"]["b"], 
            "c" : pars.parameters["reaches"][reachIndex]["Manning"]["c"], 
            "f" : pars.parameters["reaches"][reachIndex]["Manning"]["f"], 
            "n" : pars.parameters["reaches"][reachIndex]["Manning"]["n"] 
        }

        #set flow to initial conditions
        self.Flow=pars.parameters["reaches"][reachIndex]["initialFlow"]
        
        self.hasAbstraction=pars.parameters["reaches"][reachIndex]["hasAbstraction"]
        self.hasEffluent=pars.parameters["reaches"][reachIndex]["hasEffluent"]


