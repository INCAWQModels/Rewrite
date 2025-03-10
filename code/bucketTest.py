
from model import *



M=model()
M.externalTimeStep.value=86400

print("Number of subcatchments    :", M.catchment.subcatchments.__len__())
print("Number of land cover types :",M.catchment.subcatchments[0].landCoverTypes.__len__())
print("Number of buckets          :",M.catchment.subcatchments[0].landCoverTypes[0].buckets.__len__())

print("Number of data rows        :",M.drivingData.dataTable.__len__)