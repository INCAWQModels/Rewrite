class Parameter:
    """Code to manage parameter values. Much of this could be accomplished 
    using floats but units and dimensions facilitate reality checks in equations"""
    def __call__(self, *args, **kwds):
        return self.value
    
    def __init__(self, v,u):
         self.value=v
         self.units=u
         self.dimensions=dict([('L',0),('M',0),('T',0),('X',0)])

class ScaledParameter(Parameter):
    """Code to create a scaled parameter value operating on the same time step as the model"""

    #override call to return a scaled rate parameter
    def __call__(self, *args, **kwds):
        return self.value*self.daysPerTimestep
    
    def __init__(self, v, u, t):
        self.daysPerTimestep = t

        super().__init__(v, u)