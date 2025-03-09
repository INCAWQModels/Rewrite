from bucket import *
from landCoverType import *
from model import *

x=Bucket()
x.currentWaterDepth.value=9
x.evapotranspirationAdjustmentFactor=0


print(x.name)
print(x.currentWaterDepth())
x.calculatePotentialEvapotranspiration()
x.calculateActualEvapotranspiration()
print(x.currentWaterDepth())

Ag = LandCoverType(3)

M=model()
M.externalTimeStep.value=86400

Bucket.externalTimeStep.value=M.externalTimeStep.value
Bucket.stepsPerDay=1.0