from parameter import Parameter, ScaledParameter
from chemical import Chemical

class Reach:
    """First try at implementing the in-stream component of a subcatchment"""

    def __init__(self,pars):
        self.name="Reach"
        self.description="A stream reach"

        self.length=Parameter(1000.0, "m")
        self.widthAtBottom=Parameter(1,"m")
        self.slope=Parameter(1e-06,"m/m")

        #geographical coordinates of the outflow
        self.latitude=Parameter(45.0, "decimal latitude, north positive")
        self.longitude=Parameter(0.0, "decimal longitude, east positive")

        self.hasChemicals=False #flag variable to simplify decision making
        Chemical.addChemicals(self,pars)
        
        self.Manning = {
            #a, b, c and f From Allen, P. M., Arnold, J. G., and Byars, B. W.
            # : Downstream channel geometry for use in planning-level models, Water Resources
            # Bulletin, 30(4), 663–671, 1994.
            "a": 2.71,
            "b": 0.557,
            "c": 0.349,
            "f": 0.341,
            "n": 0.1
        }

        #initial conditions
        self.initialFlow=Parameter(100,"m/s")
        
        self.hasAbstraction=False
        self.hasEffluent=False


